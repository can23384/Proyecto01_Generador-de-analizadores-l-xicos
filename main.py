from pathlib import Path
import subprocess

from yalex_parser import parse_yalex_file
from lexer_builder import build_lexer, tokenize_text
from codegen import write_generated_lexer_js
from errors import YalexSpecError, token_message


def escape_label(label: str) -> str:
    replacements = {
        "\\": "\\\\",
        '"': '\\"',
        "\n": "\\n",
        "\t": "\\t",
    }
    for old, new in replacements.items():
        label = label.replace(old, new)
    return label


def dfa_to_dot(dfa: dict, title: str = "DFA") -> str:
    states = dfa["states"]
    start_state = dfa["start_state"]
    accepting = set(dfa["accepting_states"])
    transitions = dfa["transitions"]

    lines = []
    lines.append("digraph DFA {")
    lines.append("  rankdir=LR;")
    lines.append(f'  label="{escape_label(title)}";')
    lines.append('  labelloc="t";')
    lines.append("  fontsize=20;")
    lines.append("  node [shape=circle];")
    lines.append("  start [shape=point];")
    lines.append(f'  start -> "{start_state}";')

    for state in states:
        if state in accepting:
            lines.append(f'  "{state}" [shape=doublecircle];')
        else:
            lines.append(f'  "{state}" [shape=circle];')

    for src, trans in transitions.items():
        for symbol, dst in trans.items():
            label = escape_label(str(symbol))
            lines.append(f'  "{src}" -> "{dst}" [label="{label}"];')

    lines.append("}")
    return "\n".join(lines)


def write_rule_diagrams(lexer: dict, output_dir: str = "generated/diagrams"):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    written = []

    for rule in lexer["rules"]:
        token_name = rule.get("token_name", f"TOKEN_{rule['index'] + 1}")
        safe_name = "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in token_name)

        dot = dfa_to_dot(
            rule["dfa"],
            title=f"Regla {rule['index'] + 1} - {token_name}"
        )

        path = out / f"dfa_{rule['index'] + 1:02d}_{safe_name}.dot"
        path.write_text(dot, encoding="utf-8")
        written.append(str(path))

    return written


def render_dot_files(output_dir: str = "generated/diagrams", fmt: str = "png"):
    out = Path(output_dir)
    rendered = []

    for dot_file in out.glob("*.dot"):
        image_file = dot_file.with_suffix(f".{fmt}")
        subprocess.run(
            ["dot", f"-T{fmt}", str(dot_file), "-o", str(image_file)],
            check=True
        )
        rendered.append(str(image_file))

    return rendered


def main():
    yal_path = "tests/Ejemplo_basico.yal"
    input_path = "tests/entrada1.txt"

    try:
        spec = parse_yalex_file(yal_path)
        lexer = build_lexer(spec)
    except YalexSpecError as e:
        print("=" * 60)
        print("ERRORES DE ESPECIFICACIÓN YALex")
        print("=" * 60)
        print(e)
        return

    print("=" * 60)
    print("DEFINICIONES LET")
    print("=" * 60)
    for name, expr in spec["lets"].items():
        print(f"{name} = {expr}")

    print("\n" + "=" * 60)
    print("REGLAS DEL LEXER")
    print("=" * 60)

    for rule in lexer["rules"]:
        print(f"\nRegla {rule['index'] + 1}")
        print("Token      :", rule["token_name"])
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
        print(token_message(
            token["line"],
            token["column"],
            token["token_name"],
            token["lexeme"],
        ))

    print("\n" + "=" * 60)
    print("ERRORES LÉXICOS")
    print("=" * 60)

    if not errors:
        print("No se encontraron errores léxicos.")
    else:
        for err in errors:
            print(err["formatted"])

    output_file = write_generated_lexer_js(lexer)
    print("\n" + "=" * 60)
    print("ARCHIVO GENERADO")
    print("=" * 60)
    print("Se generó:", output_file)

    diagram_files = write_rule_diagrams(lexer)
    print("\n" + "=" * 60)
    print("DIAGRAMAS DE ESTADOS")
    print("=" * 60)
    for f in diagram_files:
        print("Se generó:", f)

    try:
        image_files = render_dot_files(fmt="png")
        print("\n" + "=" * 60)
        print("IMÁGENES DE DIAGRAMAS")
        print("=" * 60)
        for f in image_files:
            print("Se generó:", f)
    except Exception as e:
        print("\n" + "=" * 60)
        print("IMÁGENES DE DIAGRAMAS")
        print("=" * 60)
        print("No se pudieron generar imágenes automáticamente.")
        print("Asegúrate de tener Graphviz instalado y el comando 'dot' disponible.")
        print("Detalle:", e)


if __name__ == "__main__":
    main()