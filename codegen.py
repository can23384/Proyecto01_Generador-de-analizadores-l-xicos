import json
from pathlib import Path
from yalex_converter import SPECIAL_LITERAL_MAP, ANY_SYMBOL, LITERAL_UNDERSCORE


def strip_action_braces(action: str) -> str:
    action = action.strip()

    if action == "{}":
        return ""

    if action.startswith("{") and action.endswith("}"):
        action = action[1:-1].strip()

    return action


def convert_action_to_js(action: str) -> str:
    action = strip_action_braces(action).strip()

    if not action:
        return ""

    if action.startswith("/*") and action.endswith("*/"):
        return ""

    if action.startswith("(*") and action.endswith("*)"):
        return ""

    if action.startswith("print(") and action.endswith(")"):
        return "console.log" + action[len("print"):]

    if action.startswith("return"):
        rest = action[len("return"):].strip()

        if rest.startswith(('"', "'")):
            quote = rest[0]
            end = 1
            while end < len(rest):
                if rest[end] == '\\' and end + 1 < len(rest):
                    end += 2
                    continue
                if rest[end] == quote:
                    literal = rest[1:end]
                    return f'return {json.dumps(literal)};'
                end += 1

        token_chars = []
        for ch in rest:
            if ch.isalnum() or ch == "_":
                token_chars.append(ch)
            else:
                break

        if token_chars:
            token_name = "".join(token_chars)
            return f'return "{token_name}";'

    return action


def make_jsonable(obj):
    if isinstance(obj, set):
        return sorted(list(obj))
    if isinstance(obj, dict):
        return {k: make_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_jsonable(x) for x in obj]
    return obj


def generate_lexer_code_js(lexer: dict) -> str:
    serialized_rules = []

    for rule in lexer["rules"]:
        serialized_rules.append({
            "index": rule["index"],
            "priority": rule["priority"],
            "token_name": rule.get("token_name", f"TOKEN_{rule['index'] + 1}"),
            "original_regex": rule["original_regex"],
            "converted_regex": rule["converted_regex"],
            "action_code": convert_action_to_js(rule["action"]),
            "skip": rule.get("skip", False),
            "dfa": make_jsonable(rule["dfa"]),
        })

    eof_rule = lexer.get("eof_rule")
    serialized_eof_rule = None

    if eof_rule is not None:
        serialized_eof_rule = {
            "index": eof_rule["index"],
            "priority": eof_rule["priority"],
            "token_name": eof_rule.get("token_name", "EOF"),
            "original_regex": "eof",
            "action_code": convert_action_to_js(eof_rule["action"]),
            "skip": eof_rule.get("skip", False),
        }

    template = r'''const fs = require("fs");

const SPECIAL_LITERAL_MAP = __SPECIAL_LITERAL_MAP__;
const ANY_SYMBOL = __ANY_SYMBOL__;
const LITERAL_UNDERSCORE = __LITERAL_UNDERSCORE__;
const RULES = __RULES__;
const EOF_RULE = __EOF_RULE__;


function normalizeInputChar(ch) {
    if (ch === "_") {
        return LITERAL_UNDERSCORE;
    }

    return Object.prototype.hasOwnProperty.call(SPECIAL_LITERAL_MAP, ch)
        ? SPECIAL_LITERAL_MAP[ch]
        : ch;
}


function stepDfa(dfa, currentState, rawChar) {
    const transitions = dfa.transitions[currentState] || {};
    const normalized = normalizeInputChar(rawChar);

    if (Object.prototype.hasOwnProperty.call(transitions, normalized)) {
        return transitions[normalized];
    }

    if (Object.prototype.hasOwnProperty.call(transitions, ANY_SYMBOL)) {
        return transitions[ANY_SYMBOL];
    }

    return null;
}


function isWhitespace(ch) {
    return ch === " " || ch === "\t" || ch === "\n" || ch === "\r" || ch === "\f" || ch === "\v";
}


function normalizeNewlines(text) {
    let out = "";
    let i = 0;

    while (i < text.length) {
        const ch = text[i];

        if (ch === "\r") {
            if (i + 1 < text.length && text[i + 1] === "\n") {
                out += "\n";
                i += 2;
            } else {
                out += "\n";
                i += 1;
            }
            continue;
        }

        out += ch;
        i += 1;
    }

    return out;
}


function matchRule(dfa, text, startPos) {
    let currentState = dfa.start_state;
    let lastAcceptPos = -1;

    let pos = startPos;

    while (pos < text.length) {
        const nextState = stepDfa(dfa, currentState, text[pos]);

        if (nextState === null) {
            break;
        }

        currentState = nextState;
        pos += 1;

        if (dfa.accepting_states.includes(currentState)) {
            lastAcceptPos = pos;
        }
    }

    if (lastAcceptPos === -1) {
        return 0;
    }

    return lastAcceptPos - startPos;
}


function updatePosition(lexeme, line, column) {
    for (const ch of lexeme) {
        if (ch === "\n") {
            line += 1;
            column = 1;
        } else {
            column += 1;
        }
    }

    return { line, column };
}


function consumeInvalidLexeme(text, startPos) {
    let pos = startPos;

    if (pos >= text.length) {
        return pos;
    }

    if (isWhitespace(text[pos])) {
        return pos + 1;
    }

    while (pos < text.length && !isWhitespace(text[pos])) {
        pos += 1;
    }

    return pos;
}


function runAction(actionCode, lexeme, line, column) {
    if (!actionCode || !actionCode.trim()) {
        return null;
    }

    try {
        const fn = new Function("lexeme", "lxm", "line", "column", actionCode);
        return fn(lexeme, lexeme, line, column);
    } catch (error) {
        console.error("Error ejecutando acción:", actionCode);
        console.error(error.message);
        return null;
    }
}


function tokenizeText(text) {
    const tokens = [];
    const errors = [];

    let pos = 0;
    let line = 1;
    let column = 1;

    while (pos < text.length) {
        let bestRule = null;
        let bestLength = 0;

        for (const rule of RULES) {
            const length = matchRule(rule.dfa, text, pos);

            if (length > bestLength) {
                bestLength = length;
                bestRule = rule;
            } else if (length === bestLength && length > 0) {
                if (bestRule === null || rule.priority < bestRule.priority) {
                    bestRule = rule;
                }
            }
        }

        if (bestRule === null || bestLength === 0) {
            const invalidEnd = consumeInvalidLexeme(text, pos);
            const badLexeme = text.slice(pos, invalidEnd);

            errors.push({
                line,
                column,
                lexeme: badLexeme,
                formatted:
                    `[ERROR LÉXICO] Línea ${line}, Columna ${column}: ` +
                    `${badLexeme.length > 1 ? "token no reconocido" : "carácter no reconocido"} ` +
                    `${JSON.stringify(badLexeme)}`
            });

            const updatedError = updatePosition(badLexeme, line, column);
            line = updatedError.line;
            column = updatedError.column;
            pos = invalidEnd;
            continue;
        }

        const lexeme = text.slice(pos, pos + bestLength);

        const tokenInfo = {
            rule_index: bestRule.index,
            token_name: bestRule.token_name,
            lexeme,
            line,
            column,
            regex: bestRule.original_regex,
            action_code: bestRule.action_code
        };

        const actionResult = runAction(bestRule.action_code, lexeme, line, column);

        if (!bestRule.skip) {
            if (typeof actionResult === "string" && actionResult.trim() !== "") {
                tokenInfo.token_name = actionResult;
            }

            tokens.push(tokenInfo);
        }

        const updated = updatePosition(lexeme, line, column);
        line = updated.line;
        column = updated.column;
        pos += bestLength;
    }

    if (EOF_RULE && !EOF_RULE.skip) {
        const eofResult = runAction(EOF_RULE.action_code, "", line, column);

        const eofToken = {
            rule_index: EOF_RULE.index,
            token_name:
                (typeof eofResult === "string" && eofResult.trim() !== "")
                    ? eofResult
                    : EOF_RULE.token_name,
            lexeme: "",
            line,
            column,
            regex: "eof",
            action_code: EOF_RULE.action_code
        };

        tokens.push(eofToken);
    }

    return { tokens, errors };
}


function printResults(result) {
    console.log("\n============================================================");
    console.log("TOKENS ENCONTRADOS");
    console.log("============================================================");

    for (const token of result.tokens) {
        console.log(
            `[TOKEN] Línea ${token.line}, Columna ${token.column}: ` +
            `${token.token_name} -> ${JSON.stringify(token.lexeme)}`
        );
    }

    console.log("\n============================================================");
    console.log("ERRORES LÉXICOS");
    console.log("============================================================");

    if (result.errors.length === 0) {
        console.log("No se encontraron errores léxicos.");
    } else {
        for (const err of result.errors) {
            console.log(err.formatted);
        }
    }
}


function main() {
    if (process.argv.length < 3) {
        console.log("Uso: node lexer_generado.js <archivo_entrada>");
        return;
    }

    const inputPath = process.argv[2];
    const rawText = fs.readFileSync(inputPath, "utf8");
    const text = normalizeNewlines(rawText);

    const result = tokenizeText(text);
    printResults(result);
}


module.exports = {
    tokenizeText,
    normalizeNewlines,
    printResults,
    RULES,
    EOF_RULE
};


if (require.main === module) {
    main();
}
'''

    code = (
        template.replace(
            "__SPECIAL_LITERAL_MAP__",
            json.dumps(SPECIAL_LITERAL_MAP, ensure_ascii=False, indent=2)
        )
        .replace(
            "__ANY_SYMBOL__",
            json.dumps(ANY_SYMBOL, ensure_ascii=False)
        )
        .replace(
            "__LITERAL_UNDERSCORE__",
            json.dumps(LITERAL_UNDERSCORE, ensure_ascii=False)
        )
        .replace(
            "__RULES__",
            json.dumps(serialized_rules, ensure_ascii=False, indent=2)
        )
        .replace(
            "__EOF_RULE__",
            json.dumps(serialized_eof_rule, ensure_ascii=False, indent=2)
        )
    )

    return code


def write_generated_lexer_js(lexer: dict, output_path: str = "generated/lexer_generado.js"):
    code = generate_lexer_code_js(lexer)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return str(path)