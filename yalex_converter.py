from errors import YalexSpecError

# Símbolos especiales internos
SPECIAL_LITERAL_MAP = {
    '+': '§',
    '*': '¶',
    '?': '¤',
    '|': '¦',
    '(': '«',
    ')': '»',
    '.': '•',
    '#': '♯',
    '"': '¨',
    "'": '´'
}

# Símbolo interno para "_"
ANY_SYMBOL = '∷'

# Símbolo interno para underscore literal
LITERAL_UNDERSCORE = '⌁'

# Universo práctico para [^ ... ]
NEGATED_CLASS_UNIVERSE = ['\t', '\n', '\r'] + [chr(i) for i in range(32, 127)]


def decode_char(s: str) -> str:
    mapping = {
        r"\n": "\n",
        r"\t": "\t",
        r"\r": "\r",
        r"\b": "\b",
        r"\f": "\f",
        r"\v": "\v",
        r"\0": "\0",
        r"\\": "\\",
        r"\'": "'",
        r'\"': '"'
    }
    if s in mapping:
        return mapping[s]
    if len(s) == 2 and s.startswith('\\'):
        return s[1]
    return s


def escape_engine_symbol(ch: str) -> str:
    if ch == '\\':
        return '\\\\'
    if ch.isalnum():
        return '\\' + ch
    return ch


def engine_literal_char(ch: str) -> str:
    normalized = normalize_literal_char(ch)
    return escape_engine_symbol(normalized)


def engine_literal_sequence(text: str) -> str:
    return ''.join(engine_literal_char(ch) for ch in text)


def normalize_literal_char(ch: str) -> str:
    if ch == "_":
        return LITERAL_UNDERSCORE
    return SPECIAL_LITERAL_MAP.get(ch, ch)


def is_eof_rule(regex: str) -> bool:
    return regex.strip() == "eof"


def _raise_spec_error(line: int, expr: str, fragment: str, message: str, suggestion: str = None):
    idx = expr.find(fragment)
    column = idx + 1 if idx >= 0 else 1
    raise YalexSpecError(line, column, message, suggestion)


def strip_regex_whitespace(regex: str) -> str:
    """
    Elimina espacios insignificantes fuera de:
    - comillas simples
    - comillas dobles
    - clases [ ... ]
    """
    out = []
    i = 0
    quote = None
    bracket_depth = 0

    while i < len(regex):
        ch = regex[i]

        if quote is not None:
            out.append(ch)

            if ch == "\\" and i + 1 < len(regex):
                out.append(regex[i + 1])
                i += 2
                continue

            if ch == quote:
                quote = None

            i += 1
            continue

        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            i += 1
            continue

        if ch == "[":
            bracket_depth += 1
            out.append(ch)
            i += 1
            continue

        if ch == "]":
            if bracket_depth > 0:
                bracket_depth -= 1
            out.append(ch)
            i += 1
            continue

        if ch in (" ", "\t", "\n", "\r") and bracket_depth == 0:
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def _read_quoted(text: str, pos: int, quote: str):
    """
    Lee una constante entre comillas simples o dobles.
    Devuelve: (contenido_decodificado, next_pos, raw_fragment)
    """
    start = pos
    pos += 1
    buf = []

    while pos < len(text):
        ch = text[pos]

        if ch == "\\" and pos + 1 < len(text):
            raw = text[pos:pos + 2]
            buf.append(decode_char(raw))
            pos += 2
            continue

        if ch == quote:
            raw_fragment = text[start:pos + 1]
            return "".join(buf), pos + 1, raw_fragment

        buf.append(ch)
        pos += 1

    return None, pos, text[start:]


def _dedupe(chars):
    out = []
    seen = set()
    for ch in chars:
        if ch not in seen:
            seen.add(ch)
            out.append(ch)
    return out


def _set_to_regex(chars, *, line: int, expr: str, fragment: str) -> str:
    chars = _dedupe(chars)

    if not chars:
        _raise_spec_error(
            line,
            expr,
            fragment,
            "la diferencia de conjuntos produjo un conjunto vacío, y esta versión no lo soporta como regex.",
        )

    if len(chars) == 1:
        return engine_literal_char(chars[0])

    return "(" + "|".join(engine_literal_char(ch) for ch in chars) + ")"


def _find_matching_bracket(text: str, pos: int):
    assert text[pos] == "["
    i = pos + 1
    quote = None

    while i < len(text):
        ch = text[i]

        if quote is not None:
            if ch == "\\" and i + 1 < len(text):
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue

        if ch in ("'", '"'):
            quote = ch
            i += 1
            continue

        if ch == "]":
            return i

        i += 1

    return -1


def _find_matching_paren(text: str, pos: int):
    assert text[pos] == "("
    depth = 0
    i = pos
    quote = None
    bracket_depth = 0

    while i < len(text):
        ch = text[i]

        if quote is not None:
            if ch == "\\" and i + 1 < len(text):
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue

        if ch in ("'", '"'):
            quote = ch
            i += 1
            continue

        if ch == "[":
            bracket_depth += 1
            i += 1
            continue

        if ch == "]":
            if bracket_depth > 0:
                bracket_depth -= 1
            i += 1
            continue

        if bracket_depth > 0:
            i += 1
            continue

        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return i

        i += 1

    return -1


def _strip_outer_parens(expr: str) -> str:
    expr = expr.strip()

    while expr.startswith("(") and expr.endswith(")"):
        end = _find_matching_paren(expr, 0)
        if end != len(expr) - 1:
            break
        expr = expr[1:-1].strip()

    return expr


def _find_top_level_hash(expr: str) -> int:
    depth_paren = 0
    depth_bracket = 0
    quote = None

    i = 0
    while i < len(expr):
        ch = expr[i]

        if quote is not None:
            if ch == "\\" and i + 1 < len(expr):
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue

        if ch in ("'", '"'):
            quote = ch
            i += 1
            continue

        if ch == "[":
            depth_bracket += 1
            i += 1
            continue

        if ch == "]":
            if depth_bracket > 0:
                depth_bracket -= 1
            i += 1
            continue

        if depth_bracket > 0:
            i += 1
            continue

        if ch == "(":
            depth_paren += 1
            i += 1
            continue

        if ch == ")":
            if depth_paren > 0:
                depth_paren -= 1
            i += 1
            continue

        if ch == "#" and depth_paren == 0 and depth_bracket == 0:
            return i

        i += 1

    return -1


def _parse_class_body_chars(content: str, *, line: int, full_expr: str):
    """
    Soporta dentro de [ ... ]:
    - 'a'
    - 'a'-'z'
    - "abc" -> {a, b, c}
    """
    chars = []
    i = 0

    while i < len(content):
        while i < len(content) and content[i].isspace():
            i += 1

        if i >= len(content):
            break

        if content[i] not in ("'", '"'):
            fragment = content[i:min(i + 12, len(content))]
            _raise_spec_error(
                line,
                full_expr,
                fragment,
                "elemento inválido dentro de clase de caracteres.",
            )

        quote = content[i]
        value, j, raw_fragment = _read_quoted(content, i, quote)
        if value is None:
            _raise_spec_error(line, full_expr, content[i:], "constante sin cerrar dentro de clase de caracteres.")

        if quote == '"':
            for ch in value:
                chars.append(ch)
            i = j
            continue

        k = j
        while k < len(content) and content[k].isspace():
            k += 1

        if k < len(content) and content[k] == "-":
            k += 1
            while k < len(content) and content[k].isspace():
                k += 1

            if k >= len(content) or content[k] != "'":
                _raise_spec_error(
                    line,
                    full_expr,
                    content[i:k],
                    "rango inválido en clase de caracteres.",
                )

            end_value, end_pos, _ = _read_quoted(content, k, "'")
            if end_value is None:
                _raise_spec_error(line, full_expr, content[k:], "constante sin cerrar dentro de rango.")

            if len(value) != 1 or len(end_value) != 1:
                _raise_spec_error(
                    line,
                    full_expr,
                    content[i:end_pos],
                    f"rango inválido en clase de caracteres: {content[i:end_pos]}",
                )

            start = value
            end = end_value

            if ord(start) > ord(end):
                suggestion = None
                if start == "a" and end == "Z":
                    suggestion = "Quizá quiso escribir 'a'-'z'."
                _raise_spec_error(
                    line,
                    full_expr,
                    content[i:end_pos],
                    f"rango inválido en clase de caracteres: {content[i:end_pos]}",
                    suggestion,
                )

            for code in range(ord(start), ord(end) + 1):
                chars.append(chr(code))

            i = end_pos
            continue

        if len(value) != 1:
            _raise_spec_error(
                line,
                full_expr,
                raw_fragment,
                f"literal inválido en clase de caracteres: {raw_fragment}",
            )

        chars.append(value)
        i = j

    return _dedupe(chars)


def _parse_set_expr(expr: str, definitions: dict, *, line: int, lets_lines=None, stack=None):
    """
    Parsea una expresión de conjunto para:
    - [ ... ]
    - [^ ... ]
    - 'c'
    - ident   (si ident define un character-set)
    - expr1 # expr2
    - (expr)
    """
    if stack is None:
        stack = set()

    original = expr
    expr = strip_regex_whitespace(expr)
    expr = _strip_outer_parens(expr)

    idx = _find_top_level_hash(expr)
    if idx != -1:
        left = _parse_set_expr(expr[:idx], definitions, line=line, lets_lines=lets_lines, stack=stack)
        right = _parse_set_expr(expr[idx + 1:], definitions, line=line, lets_lines=lets_lines, stack=stack)
        right_set = set(right)
        return [ch for ch in left if ch not in right_set]

    if expr.startswith("[") and expr.endswith("]"):
        end = _find_matching_bracket(expr, 0)
        if end != len(expr) - 1:
            raise ValueError("No es un character-set puro.")

        negated = len(expr) >= 2 and expr[1] == "^"
        inner = expr[2:-1] if negated else expr[1:-1]
        chars = _parse_class_body_chars(inner, line=line, full_expr=original)

        if negated:
            inner_set = set(chars)
            return [ch for ch in NEGATED_CLASS_UNIVERSE if ch not in inner_set]

        return chars

    if expr.startswith("'") and expr.endswith("'"):
        value, end, raw = _read_quoted(expr, 0, "'")
        if value is None or end != len(expr):
            _raise_spec_error(line, original, expr, "literal sin cerrar.")
        if len(value) != 1:
            _raise_spec_error(line, original, raw, f"literal inválido: {raw}")
        return [value]

    if expr.startswith('"') and expr.endswith('"'):
        value, end, _ = _read_quoted(expr, 0, '"')
        if value is None or end != len(expr):
            _raise_spec_error(line, original, expr, "cadena sin cerrar.")
        return _dedupe(list(value))

    if expr and (expr[0].isalpha() or expr[0] == "_"):
        j = 1
        while j < len(expr) and (expr[j].isalnum() or expr[j] == "_"):
            j += 1

        if j == len(expr):
            name = expr
            if name not in definitions:
                raise ValueError("Identificador no es un character-set conocido.")

            if name in stack:
                def_line = lets_lines.get(name, line) if lets_lines else line
                raise YalexSpecError(def_line, 1, f"definición recursiva detectada en '{name}'.")

            def_line = lets_lines.get(name, line) if lets_lines else line
            return _parse_set_expr(
                definitions[name],
                definitions,
                line=def_line,
                lets_lines=lets_lines,
                stack=stack | {name},
            )

    raise ValueError("No es una expresión de conjunto pura.")


def _parse_set_atom_at(text: str, pos: int, definitions: dict, *, line: int, lets_lines=None):
    if pos >= len(text):
        return None

    ch = text[pos]

    try:
        if ch == "[":
            end = _find_matching_bracket(text, pos)
            if end == -1:
                _raise_spec_error(line, text, text[pos:], "clase de caracteres sin cerrar.", "Falta ']'.")
            fragment = text[pos:end + 1]
            chars = _parse_set_expr(fragment, definitions, line=line, lets_lines=lets_lines)
            return chars, end + 1

        if ch in ("'", '"'):
            value, end, _ = _read_quoted(text, pos, ch)
            if value is None:
                if ch == "'":
                    _raise_spec_error(line, text, text[pos:], "literal sin cerrar.")
                _raise_spec_error(line, text, text[pos:], "cadena sin cerrar.")
            fragment = text[pos:end]
            chars = _parse_set_expr(fragment, definitions, line=line, lets_lines=lets_lines)
            return chars, end

        if ch == "(":
            end = _find_matching_paren(text, pos)
            if end == -1:
                _raise_spec_error(line, text, text[pos:], "paréntesis sin cerrar.", "Falta ')'.")
            fragment = text[pos:end + 1]
            chars = _parse_set_expr(fragment, definitions, line=line, lets_lines=lets_lines)
            return chars, end + 1

        if ch.isalpha() or ch == "_":
            j = pos + 1
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1

            name = text[pos:j]
            chars = _parse_set_expr(name, definitions, line=line, lets_lines=lets_lines)
            return chars, j

    except ValueError:
        return None

    return None


def replace_set_expressions(regex: str, definitions: dict, *, line: int, lets_lines=None) -> str:
    """
    Reemplaza:
    - [ ... ]
    - [^ ... ]
    - 'c'
    - ident  (solo si ident es character-set)
    - expr1 # expr2
    por una unión explícita.
    """
    out = []
    i = 0

    while i < len(regex):
        ch = regex[i]

        if ch == '"':
            value, j, raw_fragment = _read_quoted(regex, i, '"')
            if value is None:
                _raise_spec_error(line, regex, regex[i:], "cadena sin cerrar.")
            out.append(raw_fragment)
            i = j
            continue

        parsed = _parse_set_atom_at(regex, i, definitions, line=line, lets_lines=lets_lines)
        if parsed is not None:
            chars, j = parsed
            end = j
            current_chars = chars

            while end < len(regex) and regex[end] == "#":
                rhs = _parse_set_atom_at(regex, end + 1, definitions, line=line, lets_lines=lets_lines)
                if rhs is None:
                    _raise_spec_error(
                        line,
                        regex,
                        regex[i:end + 1],
                        "operador '#' inválido; ambos lados deben ser character-set.",
                    )
                rhs_chars, rhs_end = rhs
                rhs_set = set(rhs_chars)
                current_chars = [c for c in current_chars if c not in rhs_set]
                end = rhs_end

            out.append(_set_to_regex(current_chars, line=line, expr=regex, fragment=regex[i:end]))
            i = end
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def replace_double_quoted_strings(regex: str, *, line: int) -> str:
    """
    Convierte "if" -> if
    Luego regex_engine insertará la concatenación explícita.
    """
    out = []
    i = 0

    while i < len(regex):
        ch = regex[i]

        if ch == '"':
            value, j, raw_fragment = _read_quoted(regex, i, '"')
            if value is None:
                _raise_spec_error(line, regex, regex[i:], "cadena sin cerrar.")

            if value == "":
                _raise_spec_error(
                    line,
                    regex,
                    raw_fragment,
                    "la cadena vacía no está soportada en esta versión del proyecto.",
                )

            out.append(engine_literal_sequence(value))
            i = j
            continue

        out.append(ch)
        i += 1

    return "".join(out)

def replace_wildcard_underscore(regex: str) -> str:
    """
    Reemplaza _ por ANY_SYMBOL, respetando comillas
    y preservando underscores literales ya normalizados.
    """
    out = []
    i = 0
    quote = None

    while i < len(regex):
        ch = regex[i]

        if quote is not None:
            out.append(ch)

            if ch == "\\" and i + 1 < len(regex):
                out.append(regex[i + 1])
                i += 2
                continue

            if ch == quote:
                quote = None

            i += 1
            continue

        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            i += 1
            continue

        if ch == LITERAL_UNDERSCORE:
            out.append(ch)
            i += 1
            continue

        if ch == "_":
            out.append(ANY_SYMBOL)
            i += 1
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def expand_remaining_definitions(regex: str, definitions: dict, *, lets_lines=None, cache=None, stack=None) -> str:
    """
    Expande identificadores let que sigan presentes.
    """
    if cache is None:
        cache = {}
    if stack is None:
        stack = set()

    out = []
    i = 0
    quote = None

    while i < len(regex):
        ch = regex[i]

        if quote is not None:
            out.append(ch)

            if ch == "\\" and i + 1 < len(regex):
                out.append(regex[i + 1])
                i += 2
                continue

            if ch == quote:
                quote = None

            i += 1
            continue

        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            i += 1
            continue

        if ch.isalpha() or ch == "_":
            j = i + 1
            while j < len(regex) and (regex[j].isalnum() or regex[j] == "_"):
                j += 1

            name = regex[i:j]

            if name == "eof":
                out.append(name)
                i = j
                continue

            if name in definitions:
                normalized = normalize_definition(
                    name,
                    definitions,
                    lets_lines=lets_lines,
                    cache=cache,
                    stack=stack,
                )
                out.append(f"({normalized})")
            else:
                out.append(name)

            i = j
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def normalize_definition(name: str, definitions: dict, *, lets_lines=None, cache=None, stack=None) -> str:
    if cache is None:
        cache = {}
    if stack is None:
        stack = set()

    if name in cache:
        return cache[name]

    if name in stack:
        def_line = lets_lines.get(name, 1) if lets_lines else 1
        raise YalexSpecError(def_line, 1, f"definición recursiva detectada en '{name}'.")

    if name not in definitions:
        raise KeyError(name)

    def_line = lets_lines.get(name, 1) if lets_lines else 1
    raw = definitions[name]

    normalized = yalex_regex_to_engine_regex(
        raw,
        definitions,
        line=def_line,
        lets_lines=lets_lines,
        cache=cache,
        stack=stack | {name},
    )

    cache[name] = normalized
    return normalized


def yalex_regex_to_engine_regex(regex: str, definitions: dict, *, line: int = 1, lets_lines: dict = None, cache=None, stack=None) -> str:
    """
    Convierte una regex YALex a una regex compatible con tu motor.
    Soporta:
    - _
    - "string"
    - [ ... ]
    - [^ ... ]
    - expr1 # expr2   (sobre character-set)
    - ident
    - eof
    """
    if cache is None:
        cache = {}
    if stack is None:
        stack = set()

    if is_eof_rule(regex):
        return "eof"

    regex = strip_regex_whitespace(regex)
    regex = replace_set_expressions(regex, definitions, line=line, lets_lines=lets_lines)
    regex = replace_wildcard_underscore(regex)
    regex = replace_double_quoted_strings(regex, line=line)
    regex = expand_remaining_definitions(
        regex,
        definitions,
        lets_lines=lets_lines,
        cache=cache,
        stack=stack,
    )

    return regex