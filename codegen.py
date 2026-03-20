import json
import re
from pathlib import Path
from yalex_converter import SPECIAL_LITERAL_MAP


def strip_action_braces(action: str) -> str:
    action = action.strip()
    if action == "{}":
        return ""

    if action.startswith("{") and action.endswith("}"):
        action = action[1:-1].strip()

    return action


def convert_action_to_js(action: str) -> str:
    """
    Convierte acciones simples estilo Python a JS.
    Ejemplo:
        print("Hola")
    ->  console.log("Hola")
    Si ya viene en JS, la deja igual.
    """
    action = strip_action_braces(action)

    if not action:
        return ""

    # Caso simple: print(...) de Python -> console.log(...)
    if action.startswith("print(") and action.endswith(")"):
        return "console.log" + action[len("print"):]

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
            "original_regex": rule["original_regex"],
            "converted_regex": rule["converted_regex"],
            "action_code": convert_action_to_js(rule["action"]),
            "dfa": make_jsonable(rule["dfa"])
        })

    template = r'''const fs = require("fs");

const SPECIAL_LITERAL_MAP = __SPECIAL_LITERAL_MAP__;
const RULES = __RULES__;


function normalizeInputChar(ch) {
    return Object.prototype.hasOwnProperty.call(SPECIAL_LITERAL_MAP, ch)
        ? SPECIAL_LITERAL_MAP[ch]
        : ch;
}


function matchRule(dfa, text, startPos) {
    let currentState = dfa.start_state;
    let lastAcceptPos = -1;

    let pos = startPos;
    while (pos < text.length) {
        const ch = normalizeInputChar(text[pos]);

        if (!dfa.alphabet.includes(ch)) {
            break;
        }

        const stateTransitions = dfa.transitions[currentState] || {};
        if (!(ch in stateTransitions)) {
            break;
        }

        currentState = stateTransitions[ch];
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


function runAction(actionCode, lexeme, line, column) {
    if (!actionCode || !actionCode.trim()) {
        return;
    }

    try {
        const fn = new Function("lexeme", "lxm", "line", "column", actionCode);
        fn(lexeme, lexeme, line, column);
    } catch (error) {
        console.error("Error ejecutando acción:", actionCode);
        console.error(error.message);
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
            const badChar = text[pos];
            errors.push({
                line,
                column,
                char: badChar
            });

            if (badChar === "\n") {
                line += 1;
                column = 1;
            } else {
                column += 1;
            }

            pos += 1;
            continue;
        }

        const lexeme = text.slice(pos, pos + bestLength);

        const tokenInfo = {
            rule_index: bestRule.index,
            lexeme,
            line,
            column,
            regex: bestRule.original_regex,
            action_code: bestRule.action_code
        };

        if (bestRule.action_code && bestRule.action_code.trim() !== "") {
            runAction(bestRule.action_code, lexeme, line, column);
            tokens.push(tokenInfo);
        }

        const updated = updatePosition(lexeme, line, column);
        line = updated.line;
        column = updated.column;
        pos += bestLength;
    }

    return { tokens, errors };
}


function printResults(result) {
    console.log("\n============================================================");
    console.log("TOKENS ENCONTRADOS");
    console.log("============================================================");

    for (const token of result.tokens) {
        console.log(
            `[L${token.line}, C${token.column}] ` +
            `lexema=${JSON.stringify(token.lexeme)} ` +
            `regex=${token.regex}`
        );
    }

    console.log("\n============================================================");
    console.log("ERRORES LÉXICOS");
    console.log("============================================================");

    if (result.errors.length === 0) {
        console.log("No se encontraron errores léxicos.");
    } else {
        for (const err of result.errors) {
            console.log(
                `[L${err.line}, C${err.column}] ` +
                `carácter inesperado: ${JSON.stringify(err.char)}`
            );
        }
    }
}


function main() {
    if (process.argv.length < 3) {
        console.log("Uso: node lexer_generado.js <archivo_entrada>");
        return;
    }

    const inputPath = process.argv[2];
    const text = fs.readFileSync(inputPath, "utf8").replace(/\r\n/g, "\n").replace(/\r/g, "\n");

    const result = tokenizeText(text);
    printResults(result);
}


if (require.main === module) {
    main();
}
'''

    code = template.replace(
        "__SPECIAL_LITERAL_MAP__",
        json.dumps(SPECIAL_LITERAL_MAP, ensure_ascii=False, indent=2)
    ).replace(
        "__RULES__",
        json.dumps(serialized_rules, ensure_ascii=False, indent=2)
    )

    return code


def write_generated_lexer_js(lexer: dict, output_path: str = "generated/lexer_generado.js"):
    code = generate_lexer_code_js(lexer)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return str(path)