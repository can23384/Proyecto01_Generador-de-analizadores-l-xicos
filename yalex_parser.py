from errors import YalexSpecError


def line_col_from_pos(text: str, pos: int):
    line = text.count("\n", 0, pos) + 1
    last_nl = text.rfind("\n", 0, pos)
    column = pos + 1 if last_nl == -1 else pos - last_nl
    return line, column


def remove_comments_preserve_lines(text: str) -> str:
    out = []
    i = 0
    n = len(text)

    while i < n:
        if i + 1 < n and text[i] == "(" and text[i + 1] == "*":
            start = i
            out.append(" ")
            out.append(" ")
            i += 2

            while i + 1 < n and not (text[i] == "*" and text[i + 1] == ")"):
                out.append("\n" if text[i] == "\n" else " ")
                i += 1

            if i + 1 >= n:
                line, col = line_col_from_pos(text, start)
                raise YalexSpecError(line, col, "comentario sin cerrar.", "Falta '*)'.")

            out.append(" ")
            out.append(" ")
            i += 2
            continue

        out.append(text[i])
        i += 1

    return "".join(out)


def skip_ws(text: str, pos: int) -> int:
    while pos < len(text) and text[pos].isspace():
        pos += 1
    return pos


def startswith_word(text: str, pos: int, word: str) -> bool:
    if not text.startswith(word, pos):
        return False

    before_ok = pos == 0 or not (text[pos - 1].isalnum() or text[pos - 1] == "_")
    after = pos + len(word)
    after_ok = after >= len(text) or not (text[after].isalnum() or text[after] == "_")
    return before_ok and after_ok


def read_line(text: str, pos: int):
    end = text.find("\n", pos)
    if end == -1:
        end = len(text)
    return text[pos:end], end


def is_line_prefix_symbol(text: str, pos: int, symbol: str) -> bool:
    if pos >= len(text) or text[pos] != symbol:
        return False

    j = pos - 1
    while j >= 0 and text[j] != "\n":
        if not text[j].isspace():
            return False
        j -= 1
    return True


def parse_brace_block(text: str, pos: int):
    if pos >= len(text) or text[pos] != "{":
        line, col = line_col_from_pos(text, pos)
        raise YalexSpecError(line, col, "se esperaba '{'.")

    start = pos
    depth = 0
    quote = None

    while pos < len(text):
        ch = text[pos]

        if quote is not None:
            if ch == "\\" and pos + 1 < len(text):
                pos += 2
                continue
            if ch == quote:
                quote = None
            pos += 1
            continue

        if ch in ("'", '"'):
            quote = ch
            pos += 1
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:pos + 1], pos + 1

        pos += 1

    line, col = line_col_from_pos(text, start)
    raise YalexSpecError(line, col, "bloque sin cerrar.", "Falta '}'.")


def parse_header_or_trailer(text: str, pos: int):
    pos = skip_ws(text, pos)
    if pos < len(text) and text[pos] == "{":
        return parse_brace_block(text, pos)
    return None, pos


def parse_let_line(text: str, pos: int):
    line_no, col_no = line_col_from_pos(text, pos)
    raw_line, end = read_line(text, pos)
    stripped = raw_line.strip()

    if "=" not in stripped:
        raise YalexSpecError(line_no, col_no, "definición let inválida.", "Use: let nombre = expresión")

    left, right = stripped.split("=", 1)
    left = left.strip()
    right = right.strip()

    if not left.startswith("let "):
        raise YalexSpecError(line_no, col_no, "definición let inválida.")

    name = left[len("let "):].strip()
    if not name:
        raise YalexSpecError(line_no, col_no, "identificador vacío en definición let.")

    return {
        "name": name,
        "regex": right,
        "line": line_no,
        "next_pos": end + 1 if end < len(text) else end,
    }


def parse_rule_signature(text: str, pos: int):
    line_no, col_no = line_col_from_pos(text, pos)
    eq_pos = text.find("=", pos)

    if eq_pos == -1:
        raise YalexSpecError(line_no, col_no, "definición rule inválida.", "Falta '=' en la declaración de rule.")

    signature = text[pos:eq_pos].strip()
    if not signature.startswith("rule "):
        raise YalexSpecError(line_no, col_no, "definición rule inválida.")

    rest = signature[len("rule "):].strip()
    if not rest:
        raise YalexSpecError(line_no, col_no, "nombre de rule vacío.")

    rule_name = rest
    rule_args = []

    lb = rest.find("[")
    rb = rest.rfind("]")
    if lb != -1 and rb != -1 and rb > lb:
        rule_name = rest[:lb].strip()
        args_text = rest[lb + 1:rb].strip()
        rule_args = args_text.split() if args_text else []

    if not rule_name:
        raise YalexSpecError(line_no, col_no, "nombre de rule vacío.")

    return {
        "rule_name": rule_name,
        "rule_args": rule_args,
        "next_pos": eq_pos + 1,
    }


def parse_rule_entries(text: str, pos: int):
    rules = []
    n = len(text)

    while pos < n:
        pos = skip_ws(text, pos)
        if pos >= n:
            break

        if text[pos] == "{" and is_line_prefix_symbol(text, pos, "{"):
            break

        if text[pos] == "|":
            pos += 1
            pos = skip_ws(text, pos)

        if pos >= n:
            break

        if text[pos] == "{" and is_line_prefix_symbol(text, pos, "{"):
            break

        entry_line, _ = line_col_from_pos(text, pos)
        regex_chars = []
        action = "{}"
        quote = None

        while pos < n:
            ch = text[pos]

            if quote is not None:
                regex_chars.append(ch)
                if ch == "\\" and pos + 1 < n:
                    regex_chars.append(text[pos + 1])
                    pos += 2
                    continue
                if ch == quote:
                    quote = None
                pos += 1
                continue

            if ch in ("'", '"'):
                quote = ch
                regex_chars.append(ch)
                pos += 1
                continue

            if ch == "{":
                action, pos = parse_brace_block(text, pos)
                break

            if ch == "|" and is_line_prefix_symbol(text, pos, "|"):
                break

            if ch == "\n":
                pos += 1
                break

            regex_chars.append(ch)
            pos += 1

        regex_text = "".join(regex_chars).strip()
        if not regex_text:
            break

        rules.append({
            "regex": regex_text,
            "action": action.strip() if action else "{}",
            "line": entry_line,
        })

        while pos < n and text[pos] not in "\n":
            pos += 1
        if pos < n and text[pos] == "\n":
            pos += 1

    return rules, pos


def parse_yalex(text: str) -> dict:
    clean = remove_comments_preserve_lines(text)
    pos = 0

    header, pos = parse_header_or_trailer(clean, pos)

    lets = {}
    lets_lines = {}

    while True:
        pos = skip_ws(clean, pos)
        if pos >= len(clean):
            break

        if startswith_word(clean, pos, "let"):
            parsed = parse_let_line(clean, pos)
            lets[parsed["name"]] = parsed["regex"]
            lets_lines[parsed["name"]] = parsed["line"]
            pos = parsed["next_pos"]
            continue

        break

    pos = skip_ws(clean, pos)
    if pos >= len(clean) or not startswith_word(clean, pos, "rule"):
        line, col = line_col_from_pos(clean, pos)
        raise YalexSpecError(
            line,
            col,
            "no se encontró una sección 'rule'.",
            "La especificación debe contener al menos una regla de análisis léxico.",
        )

    signature = parse_rule_signature(clean, pos)
    rule_name = signature["rule_name"]
    rule_args = signature["rule_args"]
    pos = signature["next_pos"]

    rules, pos = parse_rule_entries(clean, pos)
    if not rules:
        line, col = line_col_from_pos(clean, pos)
        raise YalexSpecError(line, col, "la sección rule no contiene reglas válidas.")

    trailer, pos = parse_header_or_trailer(clean, pos)

    return {
        "header": header or "",
        "trailer": trailer or "",
        "lets": lets,
        "lets_lines": lets_lines,
        "rule_name": rule_name,
        "rule_args": rule_args,
        "rules": rules,
    }


def parse_yalex_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return parse_yalex(f.read())