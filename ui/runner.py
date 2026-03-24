from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from codegen import write_generated_lexer_js
from errors import YalexSpecError, token_message
from lexer_builder import build_lexer, tokenize_text
from yalex_converter import ANY_SYMBOL, LITERAL_UNDERSCORE, SPECIAL_LITERAL_MAP
from yalex_parser import parse_yalex_file


REVERSE_SPECIAL_LITERAL_MAP = {v: k for k, v in SPECIAL_LITERAL_MAP.items()}


@dataclass
class RunnerResult:
    success: bool
    spec_error: Optional[str] = None
    tokens: list[dict] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    output_file: Optional[str] = None
    generated_code: str = ""
    diagram_files: list[str] = field(default_factory=list)
    image_files: list[str] = field(default_factory=list)
    logs: list[str] = field(default_factory=list)
    yal_path: Optional[str] = None
    input_path: Optional[str] = None
    rule_count: int = 0
    definitions_count: int = 0


def _safe_name(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "_-" else "_" for ch in text)


def _escape_label(label: str) -> str:
    replacements = {
        "\\": "\\\\",
        '"': '\\"',
        "\n": "\\n",
        "\t": "\\t",
    }
    for old, new in replacements.items():
        label = label.replace(old, new)
    return label


def _pretty_symbol(symbol: str) -> str:
    if symbol == ANY_SYMBOL:
        return "ANY"
    if symbol == LITERAL_UNDERSCORE:
        return "_"
    return REVERSE_SPECIAL_LITERAL_MAP.get(symbol, symbol)


def _chunk_labels(labels: list[str], size: int = 8) -> str:
    chunks = [labels[i:i + size] for i in range(0, len(labels), size)]
    return "\\n".join(", ".join(chunk) for chunk in chunks)


def dfa_to_dot_grouped(dfa: dict, title: str = "DFA") -> str:
    states = dfa["states"]
    start_state = dfa["start_state"]
    accepting = set(dfa["accepting_states"])
    transitions = dfa["transitions"]

    grouped_edges: dict[tuple[str, str], list[str]] = {}
    for src, trans in transitions.items():
        for symbol, dst in trans.items():
            grouped_edges.setdefault((src, dst), []).append(_pretty_symbol(str(symbol)))

    lines = []
    lines.append("digraph DFA {")
    lines.append("  rankdir=LR;")
    lines.append("  splines=true;")
    lines.append('  bgcolor="white";')
    lines.append('  fontname="Segoe UI";')
    lines.append('  label="%s";' % _escape_label(title))
    lines.append('  labelloc="t";')
    lines.append("  fontsize=20;")
    lines.append('  node [shape=circle, fontname="Segoe UI", fontsize=12];')
    lines.append('  edge [fontname="Consolas", fontsize=10];')
    lines.append("  start [shape=point];")
    lines.append(f'  start -> "{start_state}";')

    for state in states:
        if state in accepting:
            lines.append(f'  "{state}" [shape=doublecircle];')
        else:
            lines.append(f'  "{state}" [shape=circle];')

    for (src, dst), labels in grouped_edges.items():
        pretty = sorted(labels, key=lambda x: (len(x), x))
        label_text = _chunk_labels(pretty)
        lines.append(f'  "{src}" -> "{dst}" [label="{_escape_label(label_text)}"];')

    lines.append("}")
    return "\n".join(lines)


def write_rule_diagrams(lexer: dict, output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    for old_file in output_dir.glob("*"):
        if old_file.is_file():
            old_file.unlink()

    written = []
    for rule in lexer["rules"]:
        token_name = rule.get("token_name", f"TOKEN_{rule['index'] + 1}")
        dot = dfa_to_dot_grouped(
            rule["dfa"],
            title=f"Regla {rule['index'] + 1} - {token_name}",
        )
        path = output_dir / f"dfa_{rule['index'] + 1:02d}_{_safe_name(token_name)}.dot"
        path.write_text(dot, encoding="utf-8")
        written.append(str(path))

    return written


def render_dot_files(output_dir: Path, fmt: str = "png") -> list[str]:
    rendered = []

    if shutil.which("dot") is None:
        raise RuntimeError(
            "No se encontró Graphviz. Instálalo y asegúrate de que el comando 'dot' esté disponible."
        )

    for dot_file in sorted(output_dir.glob("*.dot")):
        image_file = dot_file.with_suffix(f".{fmt}")
        subprocess.run(
            ["dot", f"-T{fmt}", str(dot_file), "-o", str(image_file)],
            check=True,
            capture_output=True,
            text=True,
        )
        rendered.append(str(image_file))

    return rendered


def _save_editor_content(
    yal_text: str,
    input_text: str,
    yal_path: Optional[str],
    input_path: Optional[str],
) -> tuple[Path, Path]:
    cache_dir = ROOT_DIR / "generated" / ".ui_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    used_yal = Path(yal_path) if yal_path else cache_dir / "ui_current.yal"
    used_input = Path(input_path) if input_path else cache_dir / "ui_current.txt"

    used_yal.parent.mkdir(parents=True, exist_ok=True)
    used_input.parent.mkdir(parents=True, exist_ok=True)

    used_yal.write_text(yal_text, encoding="utf-8")
    used_input.write_text(input_text, encoding="utf-8")

    return used_yal, used_input


def run_pipeline(
    yal_text: str,
    input_text: str,
    yal_path: Optional[str] = None,
    input_path: Optional[str] = None,
) -> RunnerResult:
    logs: list[str] = []
    generated_dir = ROOT_DIR / "generated"
    diagrams_dir = generated_dir / "diagrams"
    generated_dir.mkdir(parents=True, exist_ok=True)

    used_yal, used_input = _save_editor_content(yal_text, input_text, yal_path, input_path)

    try:
        spec = parse_yalex_file(str(used_yal))
        lexer = build_lexer(spec)
    except YalexSpecError as exc:
        return RunnerResult(
            success=False,
            spec_error=str(exc),
            logs=[str(exc)],
            yal_path=str(used_yal),
            input_path=str(used_input),
        )

    logs.append("=" * 60)
    logs.append("DEFINICIONES LET")
    logs.append("=" * 60)
    if spec["lets"]:
        for name, expr in spec["lets"].items():
            logs.append(f"{name} = {expr}")
    else:
        logs.append("No hay definiciones let.")

    logs.append("")
    logs.append("=" * 60)
    logs.append("REGLAS DEL LEXER")
    logs.append("=" * 60)

    for rule in lexer["rules"]:
        logs.append("")
        logs.append(f"Regla {rule['index'] + 1}")
        logs.append(f"Token      : {rule['token_name']}")
        logs.append(f"Original   : {rule['original_regex']}")
        logs.append(f"Convertida : {repr(rule['converted_regex'])}")
        logs.append(f"Action     : {rule['action']}")
        logs.append(f"Estados    : {len(rule['dfa']['states'])}")
        logs.append(f"Finales    : {rule['dfa']['accepting_states']}")

    tokens, errors = tokenize_text(lexer, input_text)

    logs.append("")
    logs.append("=" * 60)
    logs.append("TOKENS ENCONTRADOS")
    logs.append("=" * 60)
    if tokens:
        for token in tokens:
            logs.append(
                token_message(
                    token["line"],
                    token["column"],
                    token["token_name"],
                    token["lexeme"],
                )
            )
    else:
        logs.append("No se encontraron tokens.")

    logs.append("")
    logs.append("=" * 60)
    logs.append("ERRORES LÉXICOS")
    logs.append("=" * 60)
    if errors:
        for err in errors:
            logs.append(err["formatted"])
    else:
        logs.append("No se encontraron errores léxicos.")

    output_file = write_generated_lexer_js(
        lexer,
        output_path=str(generated_dir / "lexer_generado.js"),
    )
    generated_code = Path(output_file).read_text(encoding="utf-8")

    logs.append("")
    logs.append("=" * 60)
    logs.append("ARCHIVO GENERADO")
    logs.append("=" * 60)
    logs.append(f"Se generó: {output_file}")

    diagram_files = write_rule_diagrams(lexer, diagrams_dir)
    logs.append("")
    logs.append("=" * 60)
    logs.append("DIAGRAMAS DE ESTADOS")
    logs.append("=" * 60)
    for file_path in diagram_files:
        logs.append(f"Se generó: {file_path}")

    image_files: list[str] = []
    try:
        image_files = render_dot_files(diagrams_dir, fmt="png")
        logs.append("")
        logs.append("=" * 60)
        logs.append("IMÁGENES DE DIAGRAMAS")
        logs.append("=" * 60)
        for file_path in image_files:
            logs.append(f"Se generó: {file_path}")
    except Exception as exc:
        logs.append("")
        logs.append("=" * 60)
        logs.append("IMÁGENES DE DIAGRAMAS")
        logs.append("=" * 60)
        logs.append("No se pudieron generar imágenes automáticamente.")
        logs.append(str(exc))

    return RunnerResult(
        success=True,
        tokens=tokens,
        errors=errors,
        output_file=output_file,
        generated_code=generated_code,
        diagram_files=diagram_files,
        image_files=image_files,
        logs=logs,
        yal_path=str(used_yal),
        input_path=str(used_input),
        rule_count=len(lexer["rules"]),
        definitions_count=len(spec["lets"]),
    )