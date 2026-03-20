import re

# Símbolos especiales de tu motor que no pueden aparecer como literales directos
# porque Lab2.py los interpreta como operadores.
SPECIAL_LITERAL_MAP = {
    '+': '§',
    '*': '¶',
    '?': '¤',
    '|': '¦',
    '(': '«',
    ')': '»',
    '.': '•',
    '#': '♯'
}


def decode_char(s: str) -> str:
    mapping = {
        r"\n": "\n",
        r"\t": "\t",
        r"\r": "\r",
        r"\\": "\\",
        r"\'": "'",
        r"\"": '"'
    }
    return mapping.get(s, s)


def normalize_literal_char(ch: str) -> str:
    return SPECIAL_LITERAL_MAP.get(ch, ch)


def expand_char_class(content: str) -> str:
    """
    Convierte contenido dentro de [ ... ] a una unión explícita.
    Ejemplo:
        '0'-'9'        -> (0|1|2|3|4|5|6|7|8|9)
        'a'-'z''A'-'Z' -> (a|b|...|z|A|B|...|Z)
    """
    pattern = r"'(?:\\.|[^'])*'(?:\s*-\s*'(?:\\.|[^'])*')?"
    tokens = re.findall(pattern, content)

    chars = []

    for token in tokens:
        parts = re.findall(r"'((?:\\.|[^'])*)'", token)

        if "-" in token and len(parts) == 2:
            start = decode_char(parts[0])
            end = decode_char(parts[1])

            if len(start) != 1 or len(end) != 1:
                raise ValueError(f"Rango inválido en clase: {token}")

            if ord(start) > ord(end):
                raise ValueError(f"Rango invertido en clase: {token}")

            for code in range(ord(start), ord(end) + 1):
                chars.append(normalize_literal_char(chr(code)))
        else:
            for p in parts:
                ch = decode_char(p)
                if len(ch) != 1:
                    raise ValueError(f"Literal inválido en clase: '{p}'")
                chars.append(normalize_literal_char(ch))

    # quitar duplicados preservando orden
    unique = []
    for ch in chars:
        if ch not in unique:
            unique.append(ch)

    return "(" + "|".join(unique) + ")"


def replace_char_classes(regex: str) -> str:
    """
    Reemplaza [ ... ] por una unión explícita.
    """
    pattern = r"\[(.*?)\]"

    while re.search(pattern, regex):
        match = re.search(pattern, regex)
        content = match.group(1)
        expanded = expand_char_class(content)
        regex = regex[:match.start()] + expanded + regex[match.end():]

    return regex


def replace_quoted_literals(regex: str) -> str:
    """
    Reemplaza literales de YALex tipo:
        '+'   '*'   '='   '-'
    por el carácter interno que entiende el motor.
    """

    def repl(match):
        raw = match.group(1)
        ch = decode_char(raw)
        if len(ch) != 1:
            raise ValueError(f"Literal inválido: '{raw}'")
        return normalize_literal_char(ch)

    return re.sub(r"'((?:\\.|[^'])*)'", repl, regex)


def expand_definitions(expr: str, definitions: dict) -> str:
    """
    Sustituye nombres let por su definición expandida.
    """
    changed = True

    while changed:
        changed = False
        for name, value in definitions.items():
            pattern = rf"\b{name}\b"
            new_expr = re.sub(pattern, f"({value})", expr)
            if new_expr != expr:
                expr = new_expr
                changed = True

    return expr


def yalex_regex_to_engine_regex(regex: str, definitions: dict) -> str:
    """
    Convierte una regex YALex a una regex compatible con tu motor.
    """
    expanded_defs = {}

    # primero normalizamos las definiciones let
    for name, value in definitions.items():
        value = replace_char_classes(value)
        value = replace_quoted_literals(value)
        expanded_defs[name] = value

    # luego normalizamos la regla
    regex = replace_char_classes(regex)
    regex = replace_quoted_literals(regex)

    # finalmente expandimos referencias
    regex = expand_definitions(regex, expanded_defs)

    return regex