# Módulo de construcción del lexer: convierte especificación YALex en un AFD funcional

from yalex_converter import (
    yalex_regex_to_engine_regex,
    SPECIAL_LITERAL_MAP,
    ANY_SYMBOL,
    LITERAL_UNDERSCORE,
    is_eof_rule,
)
from regex_engine import regex_to_dfa
from errors import lexical_error
from token_utils import infer_token_name as infer_token_name_from_rule


def normalize_input_char(ch: str) -> str:
    # Normaliza un carácter de entrada usando el mapa especial
    if ch == "_":
        return LITERAL_UNDERSCORE
    return SPECIAL_LITERAL_MAP.get(ch, ch)


def step_dfa(dfa: dict, current_state: str, raw_char: str):
    # Avanza un estado en el DFA leyendo un carácter
    # Intenta 1) transición exacta 2) transición ANY_SYMBOL (comodín)
    transitions = dfa["transitions"].get(current_state, {})
    normalized = normalize_input_char(raw_char)

    if normalized in transitions:
        return transitions[normalized]

    if ANY_SYMBOL in transitions:
        return transitions[ANY_SYMBOL]

    return None


def strip_action_braces(action: str) -> str:
    # Extrae el contenido de { }
    action = action.strip()
    if action.startswith("{") and action.endswith("}"):
        action = action[1:-1].strip()
    return action


def is_skip_action(action: str) -> bool:
    # Detecta si una acción debe ser ignorada (comentario vacío)
    code = strip_action_braces(action).strip()

    if not code:
        return True

    # Comentario estilo OCaml (* ... *)
    if code.startswith("(*") and code.endswith("*)"):
        return True

    # Comentario estilo C /* ... */
    if code.startswith("/*") and code.endswith("*/"):
        return True

    return False


def build_lexer(spec: dict) -> dict:
    # Construye el lexer a partir de la especificación YALex
    rules = []
    eof_rule = None

    for idx, rule in enumerate(spec["rules"]):
        original_regex = rule["regex"].strip()

        # Maneja la regla especial EOF
        if is_eof_rule(original_regex):
            eof_rule = {
                "index": idx,
                "priority": idx,
                "token_name": infer_token_name_from_rule(original_regex, rule["action"], idx) if rule["action"].strip() != "{}" else "EOF",
                "skip": is_skip_action(rule["action"]),
                "original_regex": "eof",
                "converted_regex": "eof",
                "action": rule["action"],
                "line": rule.get("line", 1),
            }
            continue

        # Convierte la regex YALex a formato compatible con el motor
        converted_regex = yalex_regex_to_engine_regex(
            original_regex,
            spec["lets"],
            line=rule.get("line", 1),
            lets_lines=spec.get("lets_lines", {}),
        )

        # Construye el AFD para esta regla
        result = build_automaton_from_regex(converted_regex)
        minimized_dfa = result["minimized_dfa"]

        token_name = infer_token_name_from_rule(original_regex, rule["action"], idx)
        skip = is_skip_action(rule["action"])

        rules.append({
            "index": idx,
            "priority": idx,  # Prioridad en caso de conflicto
            "token_name": token_name,
            "skip": skip,
            "original_regex": original_regex,
            "converted_regex": converted_regex,
            "action": rule["action"],
            "line": rule.get("line", 1),
            "dfa": minimized_dfa,
        })

    return {
        "rule_name": spec["rule_name"],
        "rules": rules,
        "eof_rule": eof_rule,
    }


def match_rule(dfa: dict, text: str, start_pos: int):
    # Intenta hacer coincidir una regla desde una posición en el texto
    current_state = dfa["start_state"]
    last_accept_pos = -1

    pos = start_pos
    while pos < len(text):
        next_state = step_dfa(dfa, current_state, text[pos])
        if next_state is None:
            break

        current_state = next_state
        pos += 1

        # Registra la última posición de aceptación
        if current_state in dfa["accepting_states"]:
            last_accept_pos = pos

    if last_accept_pos == -1:
        return 0

    return last_accept_pos - start_pos


def update_position(lexeme: str, line: int, col: int):
    # Actualiza línea y columna después de leer un lexema
    for ch in lexeme:
        if ch == "\n":
            line += 1
            col = 1
        else:
            col += 1
    return line, col


def consume_invalid_lexeme(text: str, start_pos: int) -> int:
    # Lee un carácter inválido
    if start_pos >= len(text):
        return start_pos
    return start_pos + 1


def tokenize_text(lexer: dict, text: str):
    # Tokeniza el texto completo usando las reglas del lexer
    tokens = []
    errors = []

    pos = 0
    line = 1
    col = 1

    while pos < len(text):
        # Busca la mejor regla que coincida
        best_rule = None
        best_length = 0

        for rule in lexer["rules"]:
            length = match_rule(rule["dfa"], text, pos)

            # Elige la coincidencia más larga
            if length > best_length:
                best_length = length
                best_rule = rule
            # En caso de empate, elige por prioridad
            elif length == best_length and length > 0:
                if best_rule is None or rule["priority"] < best_rule["priority"]:
                    best_rule = rule

        # Si no hay coincidencia, es un error
        if best_rule is None or best_length == 0:
            invalid_end = consume_invalid_lexeme(text, pos)
            bad_lexeme = text[pos:invalid_end]

            errors.append(
                lexical_error(
                    line,
                    col,
                    "token no reconocido" if len(bad_lexeme) > 1 else "carácter no reconocido",
                    bad_lexeme,
                )
            )

            line, col = update_position(bad_lexeme, line, col)
            pos = invalid_end
            continue

        # Se encontró una coincidencia
        lexeme = text[pos:pos + best_length]

        token_info = {
            "rule_index": best_rule["index"],
            "token_name": best_rule["token_name"],
            "lexeme": lexeme,
            "line": line,
            "column": col,
            "action": best_rule["action"],
            "regex": best_rule["original_regex"],
        }

        # Añade el token si no debe saltarse
        if not best_rule.get("skip", False):
            tokens.append(token_info)

        line, col = update_position(lexeme, line, col)
        pos += best_length

    # Añade token EOF si está definido
    eof_rule = lexer.get("eof_rule")
    if eof_rule is not None and not eof_rule.get("skip", False):
        tokens.append({
            "rule_index": eof_rule["index"],
            "token_name": eof_rule["token_name"],
            "lexeme": "",
            "line": line,
            "column": col,
            "action": eof_rule["action"],
            "regex": "eof",
        })

    return tokens, errors


def build_automaton_from_regex(regex: str):
    # Construye un AFD a partir de una expresión regular
    return regex_to_dfa(regex)