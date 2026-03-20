from yalex_parser import parse_yalex_file
from lexer_builder import build_lexer, tokenize_text
from codegen import write_generated_lexer_js


def main():
    yal_path = "tests/Ejemplo_basico.yal"
    input_path = "tests/entrada1.txt"

    spec = parse_yalex_file(yal_path)

    print("=" * 60)
    print("DEFINICIONES LET")
    print("=" * 60)
    for name, expr in spec["lets"].items():
        print(f"{name} = {expr}")

    lexer = build_lexer(spec)

    print("\n" + "=" * 60)
    print("REGLAS DEL LEXER")
    print("=" * 60)

    for rule in lexer["rules"]:
        print(f"\nRegla {rule['index'] + 1}")
        print("Original   :", rule["original_regex"])
        print("Convertida :", repr(rule["converted_regex"]))
        print("Action     :", rule["action"])
        print("Estados    :", len(rule["dfa"]["states"]))
        print("Finales    :", rule["dfa"]["accepting_states"])

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    tokens, errors = tokenize_text(lexer, text)

    print("\n" + "=" * 60)
    print("TOKENS ENCONTRADOS")
    print("=" * 60)

    for token in tokens:
        print(
            f"[L{token['line']}, C{token['column']}] "
            f"lexema={repr(token['lexeme'])} "
            f"regex={token['regex']} "
            f"action={token['action']}"
        )

    print("\n" + "=" * 60)
    print("ERRORES LÉXICOS")
    print("=" * 60)

    if not errors:
        print("No se encontraron errores léxicos.")
    else:
        for err in errors:
            print(
                f"[L{err['line']}, C{err['column']}] "
                f"carácter inesperado: {repr(err['char'])}"
            )

    output_file = write_generated_lexer_js(lexer)
    print("\n" + "=" * 60)
    print("ARCHIVO GENERADO")
    print("=" * 60)
    print("Se generó:", output_file)


if __name__ == "__main__":
    main()