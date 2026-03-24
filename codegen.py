# Módulo de generación de código: convierte el lexer a código JavaScript

import json
from pathlib import Path
from yalex_converter import SPECIAL_LITERAL_MAP, ANY_SYMBOL, LITERAL_UNDERSCORE


def strip_action_braces(action: str) -> str:
    # Extrae el contenido de { }
    action = action.strip()

    if action == "{}":
        return ""

    if action.startswith("{") and action.endswith("}"):
        action = action[1:-1].strip()

    return action


def convert_action_to_js(action: str) -> str:
    # Convierte acciones YALex/OCaml a código JavaScript equivalente
    action = strip_action_braces(action).strip()

    if not action:
        return ""

    # Ignora comentarios
    if action.startswith("/*") and action.endswith("*/"):
        return ""

    if action.startswith("(*") and action.endswith("*)"):
        return ""

    # Convierte print(...) a console.log(...)
    if action.startswith("print(") and action.endswith(")"):
        return "console.log" + action[len("print"):]

    # Convierte "return ..." en JavaScript con retorno correcto
    if action.startswith("return"):
        rest = action[len("return"):].strip()

        # Si es una cadena entrecomillada
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

        # Si es un identificador
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
    # Convierte objetos a estructuras JSON-serializables (sets -> listas)
    if isinstance(obj, set):
        return sorted(list(obj))
    if isinstance(obj, dict):
        return {k: make_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [make_jsonable(x) for x in obj]
    return obj


def generate_lexer_code_js(lexer: dict) -> str:
    # Genera el código JavaScript completo del lexer
    serialized_rules = []

    # Serializa cada regla del lexer
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

    # Serializa la regla EOF si existe
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

    # Template JavaScript del lexer generado
    template = r'''const fs = require("fs");

// Mapas de caracteres especiales para normalización
const SPECIAL_LITERAL_MAP = __SPECIAL_LITERAL_MAP__;
const ANY_SYMBOL = __ANY_SYMBOL__;
const LITERAL_UNDERSCORE = __LITERAL_UNDERSCORE__;
const RULES = __RULES__;
const EOF_RULE = __EOF_RULE__;


// Normaliza un carácter de entrada según los mapas especiales
function normalizeInputChar(ch) {
    if (ch === "_") {
        return LITERAL_UNDERSCORE;
    }

    return Object.prototype.hasOwnProperty.call(SPECIAL_LITERAL_MAP, ch)
        ? SPECIAL_LITERAL_MAP[ch]
        : ch;
}


// Avanza un estado en el DFA leyendo un carácter
function stepDfa(dfa, currentState, rawChar) {
    const transitions = dfa.transitions[currentState] || {};
    const normalized = normalizeInputChar(rawChar);

    // Intenta transición exacta
    if (Object.prototype.hasOwnProperty.call(transitions, normalized)) {
        return transitions[normalized];
    }

    // Intenta transición ANY_SYMBOL (comodín)
    if (Object.prototype.hasOwnProperty.call(transitions, ANY_SYMBOL)) {
        return transitions[ANY_SYMBOL];
    }

    return null;
}


// Verifica si un carácter es espaciado
function isWhitespace(ch) {
    return ch === " " || ch === "\t" || ch === "\n" || ch === "\r" || ch === "\f" || ch === "\v";
}


// Normaliza saltos de línea (maneja \r\n, \r, \n como \n)
function normalizeNewlines(text) {
    let out = "";
    let i = 0;

    while (i < text.length) {
        const ch = text[i];

        // Convierte \r\n a \n; \r solo también se convierte a \n
        if (ch === "\r") {
            if (i + 1 < text.length && text[i + 1] === "\n") {
                out += "\n";
                i += 2;  // Salta \r\n
            } else {
                out += "\n";
                i += 1;  // Salta \r solo
            }
            continue;
        }

        out += ch;
        i += 1;
    }

    return out;
}


// Intenta emparejar un DFA contra texto; retorna longitud del match
function matchRule(dfa, text, startPos) {
    let currentState = dfa.start_state;
    let lastAcceptPos = -1;  // Última posición en estado aceptante

    let pos = startPos;

    // Avanza el DFA mientras sea posible
    while (pos < text.length) {
        const nextState = stepDfa(dfa, currentState, text[pos]);

        if (nextState === null) {
            break;  // No hay transición, detén búsqueda
        }

        currentState = nextState;
        pos += 1;

        // Registra si llegamos a estado aceptante
        if (dfa.accepting_states.includes(currentState)) {
            lastAcceptPos = pos;
        }
    }

    // Retorna longitud del match (0 si no hay)
    if (lastAcceptPos === -1) {
        return 0;
    }

    return lastAcceptPos - startPos;
}


// Actualiza línea/columna según caracteres del lexema
function updatePosition(lexeme, line, column) {
    for (const ch of lexeme) {
        if (ch === "\n") {
            line += 1;
            column = 1;  // Reinicia columna
        } else {
            column += 1;
        }
    }

    return { line, column };
}


// Consume un carácter como error léxico
function consumeInvalidLexeme(text, startPos) {
    if (startPos >= text.length) {
        return startPos;
    }

    return startPos + 1;  // Salta un carácter
}


// Ejecuta código de acción en JavaScript
function runAction(actionCode, lexeme, line, column) {
    if (!actionCode || !actionCode.trim()) {
        return null;  // Sin acción
    }

    try {
        // Crea función anónima con las variables del contexto
        const fn = new Function("lexeme", "lxm", "line", "column", actionCode);
        return fn(lexeme, lexeme, line, column);
    } catch (error) {
        console.error("Error ejecutando acción:", actionCode);
        console.error(error.message);
        return null;
    }
}


// Tokeniza texto usando las reglas del lexer
function tokenizeText(text) {
    const tokens = [];
    const errors = [];

    let pos = 0;
    let line = 1;
    let column = 1;

    // Procesa caracteres hasta fin del texto
    while (pos < text.length) {
        let bestRule = null;
        let bestLength = 0;

        // Busca la mejor regla: longest match + menor prioridad
        for (const rule of RULES) {
            const length = matchRule(rule.dfa, text, pos);

            if (length > bestLength) {
                bestLength = length;
                bestRule = rule;
            } else if (length === bestLength && length > 0) {
                // Desempate: prefiere menor prioridad
                if (bestRule === null || rule.priority < bestRule.priority) {
                    bestRule = rule;
                }
            }
        }

        // Sin match: error léxico
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

            // Actualiza posición y continúa
            const updatedError = updatePosition(badLexeme, line, column);
            line = updatedError.line;
            column = updatedError.column;
            pos = invalidEnd;
            continue;
        }

        // Extrae lexema y crea token
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

        // Ejecuta acción y obtiene posible alias de token
        const actionResult = runAction(bestRule.action_code, lexeme, line, column);

        // Si la regla no es SKIP, agrega token
        if (!bestRule.skip) {
            if (typeof actionResult === "string" && actionResult.trim() !== "") {
                tokenInfo.token_name = actionResult;  // Renombra si acción retorna string
            }

            tokens.push(tokenInfo);
        }

        // Actualiza línea/columna y avanza
        const updated = updatePosition(lexeme, line, column);
        line = updated.line;
        column = updated.column;
        pos += bestLength;
    }

    // Agrega token EOF si está definido
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


// Imprime resultados del tokenizado (tokens y errores)
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


// Punto de entrada del lexer generado
function main() {
    if (process.argv.length < 3) {
        console.log("Uso: node lexer_generado.js <archivo_entrada>");
        return;
    }

    const inputPath = process.argv[2];
    const rawText = fs.readFileSync(inputPath, "utf8");
    const text = normalizeNewlines(rawText);  // Normaliza line breaks

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
    # Genera el código JavaScript y lo guarda en un archivo
    code = generate_lexer_code_js(lexer)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)

    return str(path)