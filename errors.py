# Módulo de errores: maneja diagnósticos y excepciones del analizador léxico

from dataclasses import dataclass
from typing import Optional


@dataclass
class Diagnostic:
    # Estructura para representar un error o advertencia con posición en el archivo
    kind: str                              # Tipo de error (ERROR YALex, ERROR LÉXICO)
    line: int                              # Número de línea donde ocorre el error
    column: int                            # Número de columna del error
    message: str                           # Descripción del error
    suggestion: Optional[str] = None       # Recomendación para arreglarlo
    lexeme: Optional[str] = None           # Token problemático (optional)

    def format(self) -> str:
        # Formatea el error en un mensaje legible
        base = f"[{self.kind}] Línea {self.line}, Columna {self.column}: {self.message}"
        if self.lexeme is not None:
            base += f" {repr(self.lexeme)}"
        if self.suggestion:
            base += f"\nSugerencia: {self.suggestion}"
        return base


class YalexSpecError(Exception):
    # Excepción para errores en la especificación YALex
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
    # Crea un diccionario con información de error léxico
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
    # Formatea un mensaje de token encontrado correctamente
    return f"[TOKEN] Línea {line}, Columna {column}: {token_name} -> {repr(lexeme)}"