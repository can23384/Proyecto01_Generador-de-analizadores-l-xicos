from dataclasses import dataclass
from typing import Optional


@dataclass
class Diagnostic:
    kind: str
    line: int
    column: int
    message: str
    suggestion: Optional[str] = None
    lexeme: Optional[str] = None

    def format(self) -> str:
        base = f"[{self.kind}] Línea {self.line}, Columna {self.column}: {self.message}"
        if self.lexeme is not None:
            base += f" {repr(self.lexeme)}"
        if self.suggestion:
            base += f"\nSugerencia: {self.suggestion}"
        return base


class YalexSpecError(Exception):
    def __init__(self, line: int, column: int, message: str, suggestion: Optional[str] = None):
        self.diagnostic = Diagnostic(
            kind="ERROR YALex",
            line=line,
            column=column,
            message=message,
            suggestion=suggestion,
        )
        super().__init__(self.diagnostic.format())


def lexical_error(line: int, column: int, message: str, lexeme: Optional[str] = None) -> dict:
    diag = Diagnostic(
        kind="ERROR LÉXICO",
        line=line,
        column=column,
        message=message,
        lexeme=lexeme,
    )
    return {
        "line": line,
        "column": column,
        "message": message,
        "lexeme": lexeme,
        "formatted": diag.format(),
    }


def token_message(line: int, column: int, token_name: str, lexeme: str) -> str:
    return f"[TOKEN] Línea {line}, Columna {column}: {token_name} -> {repr(lexeme)}"