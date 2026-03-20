from yalex_converter import yalex_regex_to_engine_regex, SPECIAL_LITERAL_MAP
from regex_engine import build_automaton_from_regex


def normalize_input_char(ch: str) -> str:
    """
    Convierte caracteres de entrada a los símbolos internos usados
    por el motor de regex para literales especiales.
    Ejemplo: '+' -> '§', '*' -> '¶'
    """
    return SPECIAL_LITERAL_MAP.get(ch, ch)


def build_lexer(spec: dict) -> dict:
    """
    Construye una especificación interna del lexer:
    - una lista de reglas
    - cada regla con su regex original
    - regex convertida
    - acción
    - prioridad
    - AFD minimizado
    """
    rules = []

    for idx, rule in enumerate(spec["rules"]):
        original_regex = rule["regex"]
        converted_regex = yalex_regex_to_engine_regex(original_regex, spec["lets"])

        result = build_automaton_from_regex(converted_regex)
        minimized_dfa = result["minimized_dfa"]

        rules.append({
            "index": idx,
            "priority": idx,   # menor = mayor prioridad
            "original_regex": original_regex,
            "converted_regex": converted_regex,
            "action": rule["action"],
            "dfa": minimized_dfa
        })

    return {
        "rule_name": spec["rule_name"],
        "rules": rules
    }


def match_rule(dfa: dict, text: str, start_pos: int):
    """
    Intenta hacer match con UNA regla desde start_pos.
    Devuelve la longitud del match más largo aceptado.
    Si no acepta nada, devuelve 0.
    """
    current_state = dfa["start_state"]
    last_accept_pos = -1

    pos = start_pos
    while pos < len(text):
        ch = normalize_input_char(text[pos])

        if ch not in dfa["alphabet"]:
            break

        state_transitions = dfa["transitions"].get(current_state, {})
        if ch not in state_transitions:
            break

        current_state = state_transitions[ch]
        pos += 1

        if current_state in dfa["accepting_states"]:
            last_accept_pos = pos

    if last_accept_pos == -1:
        return 0

    return last_accept_pos - start_pos


def update_position(lexeme: str, line: int, col: int):
    """
    Actualiza línea y columna según el lexema consumido.
    """
    for ch in lexeme:
        if ch == "\n":
            line += 1
            col = 1
        else:
            col += 1
    return line, col


def tokenize_text(lexer: dict, text: str):
    """
    Tokeniza el texto completo.
    Aplica:
    - longest match
    - prioridad por orden de regla
    - error léxico si ninguna regla acepta
    """
    tokens = []
    errors = []

    pos = 0
    line = 1
    col = 1

    while pos < len(text):
        best_rule = None
        best_length = 0

        for rule in lexer["rules"]:
            length = match_rule(rule["dfa"], text, pos)

            if length > best_length:
                best_length = length
                best_rule = rule
            elif length == best_length and length > 0:
                if rule["priority"] < best_rule["priority"]:
                    best_rule = rule

        if best_rule is None or best_length == 0:
            bad_char = text[pos]
            errors.append({
                "line": line,
                "column": col,
                "char": bad_char
            })

            # avanzar un carácter para no quedar en loop
            if bad_char == "\n":
                line += 1
                col = 1
            else:
                col += 1
            pos += 1
            continue

        lexeme = text[pos:pos + best_length]

        token_info = {
            "rule_index": best_rule["index"],
            "lexeme": lexeme,
            "line": line,
            "column": col,
            "action": best_rule["action"],
            "regex": best_rule["original_regex"]
        }

        # Si la acción es {} lo tratamos como skip
        if best_rule["action"].strip() != "{}":
            tokens.append(token_info)

        line, col = update_position(lexeme, line, col)
        pos += best_length

    return tokens, errors