from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from .main_window import MainWindow
from .styles import APP_STYLE


def main():
    try:
        app = QApplication(sys.argv)
    except Exception as exc:
        print("No se pudo iniciar la aplicación:", exc)
        return

    app.setApplicationName("Los Tres Furiosos - YALex Studio")
    app.setOrganizationName("UVG")

    base_font = QFont("Segoe UI", 10)
    app.setFont(base_font)
    app.setStyleSheet(APP_STYLE)

    window = MainWindow()
    window.show()

    try:
        sys.exit(app.exec())
    except Exception as exc:
        QMessageBox.critical(
            None,
            "Error",
            f"La aplicación terminó con un error inesperado:\n\n{exc}",
        )


if __name__ == "__main__":
    main()