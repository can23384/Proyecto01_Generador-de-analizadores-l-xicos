# Módulo de utilidades para tokens: genera nombres de tokens automáticamente

# Mapeo de símbolos especiales con sus nombres de token
LITERAL_TOKEN_NAMES = {
    "'+'": "PLUS",
    "'-'": "MINUS",
    "'*'": "TIMES",
    "'/'": "DIV",
    "'('": "LPAREN",
    "')'": "RPAREN",
    "'='": "ASSIGN",
    "';'": "SEMICOLON",
    "','": "COMMA",
    "':'": "COLON",
    "'.'": "DOT",
}


def strip_action_braces(action: str) -> str:
    # Extrae el contenido entre llaves { }
    action = action.strip()
    if action.startswith("{") and action.endswith("}"):
        return action[1:-1].strip()
    return action




def sanitize_token_name(text: str):
    # Limpia el nombre del token: mayúsculas, reemplaza caracteres especiales con _
    out = []
    prev_underscore = False

    for ch in text.upper():
        if ch.isalnum():
            out.append(ch)
            prev_underscore = False
        else:
            if out and not prev_underscore:
                out.append("_")
                prev_underscore = True

    token = "".join(out).strip("_")
    if not token:
        return None
    if token[0].isdigit():
        token = f"TOKEN_{token}"  # Si comienza con número lo prefija
    return token


def extract_first_quoted_string(text: str):
    # Extrae la primera cadena entrecomillada (simple o doble)
    quote = None
    buf = []
    i = 0

    while i < len(text):
        ch = text[i]

        if quote is None:
            if ch in ("'", '"'):
                quote = ch
        else:
            if ch == "\\" and i + 1 < len(text):  # Maneja caracteres escapados
                buf.append(text[i + 1])
                i += 2
                continue
            if ch == quote:
                return "".join(buf)
            buf.append(ch)

        i += 1

    return None


def extract_name_from_return(action_code: str):
    # Extrae nombre de token de una acción "return ..."
    code = strip_action_braces(action_code)
    if not code.startswith("return"):
        return None

    rest = code[len("return"):].strip()
    if not rest:
        return None

    # Si es una cadena entrecomillada
    if rest[0] in ("'", '"'):
        quoted = extract_first_quoted_string(rest)
        return sanitize_token_name(quoted) if quoted else None

    # Si es un identificador directo
    token = []
    for ch in rest:
        if ch.isalnum() or ch == "_":
            token.append(ch)
        else:
            break

    name = "".join(token)
    if not name:
        return None

    return sanitize_token_name(name)


def extract_name_from_print(action_code: str):
    # Extrae nombre de token de una acción "print(...)" o "console.log(...)"
    code = strip_action_braces(action_code)

    for prefix in ("print(", "console.log("):
        idx = code.find(prefix)
        if idx != -1:
            inside = code[idx + len(prefix):]
            quoted = extract_first_quoted_string(inside)
            if quoted:
                return sanitize_token_name(quoted)

    return None


def infer_token_name(original_regex: str, action: str, index: int) -> str:
    # Intenta adivinar el nombre del token por varios métodos
    # 1. Del código de acción (return, print)
    action_name = extract_name_from_return(action) or extract_name_from_print(action)
    if action_name:
        return action_name

    # 2. Si es un símbolo literal conocido
    normalized = "".join(original_regex.split())

    if normalized in LITERAL_TOKEN_NAMES:
        return LITERAL_TOKEN_NAMES[normalized]

    # 3. Por patrones en el nombre (identificador, número, etc)
    lowered = normalized.lower()

    if "identificador" in lowered or lowered in ("ident", "id"):
        return "IDENTIFIER"

    if "numero" in lowered or "digito" in lowered or "digit" in lowered:
        return "NUMBER"

    if "blank" in lowered or "space" in lowered or "ws" in lowered:
        return "WHITESPACE"

    if action.strip() == "{}":
        return "SKIP"
    
    if original_regex.strip() == "eof":
        return "EOF"

    # 4. Si nada funciona usa nombre genérico
    return f"TOKEN_{index + 1}"