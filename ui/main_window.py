from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QPixmap, QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QComboBox,
)

from .runner import ROOT_DIR, RunnerResult, run_pipeline


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.current_yal_path: str | None = None
        self.current_input_path: str | None = None
        self.current_generated_path: str | None = None
        self.current_image_path: str | None = None
        self.current_original_pixmap: QPixmap | None = None

        self.setWindowTitle("Los Tres Furiosos - YALex Studio")
        self.resize(1600, 950)
        self.setMinimumSize(1200, 760)

        self._build_actions()
        self._build_ui()
        self._build_toolbar()
        self._build_menubar()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo. Carga un .yal y un .txt para comenzar.")

        self._load_default_example()

    def _build_actions(self):
        self.open_yal_action = QAction("Abrir YAL", self)
        self.open_yal_action.triggered.connect(self.open_yal_file)

        self.open_input_action = QAction("Abrir TXT", self)
        self.open_input_action.triggered.connect(self.open_input_file)

        self.save_yal_action = QAction("Guardar YAL", self)
        self.save_yal_action.triggered.connect(self.save_yal_file)

        self.save_input_action = QAction("Guardar TXT", self)
        self.save_input_action.triggered.connect(self.save_input_file)

        self.generate_action = QAction("Generar lexer", self)
        self.generate_action.triggered.connect(self.generate_project)

        self.refresh_diagrams_action = QAction("Actualizar diagramas", self)
        self.refresh_diagrams_action.triggered.connect(self.show_selected_diagram)

        self.load_examples_action = QAction("Cargar ejemplo", self)
        self.load_examples_action.triggered.connect(self._load_default_example)

    def _build_toolbar(self):
        toolbar = QToolBar("Principal", self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.addAction(self.open_yal_action)
        toolbar.addAction(self.open_input_action)
        toolbar.addSeparator()
        toolbar.addAction(self.save_yal_action)
        toolbar.addAction(self.save_input_action)
        toolbar.addSeparator()
        toolbar.addAction(self.generate_action)
        toolbar.addAction(self.refresh_diagrams_action)
        toolbar.addSeparator()
        toolbar.addAction(self.load_examples_action)
        self.addToolBar(toolbar)

    def _build_menubar(self):
        menu = self.menuBar()

        archivo = menu.addMenu("Archivo")
        archivo.addAction(self.open_yal_action)
        archivo.addAction(self.open_input_action)
        archivo.addSeparator()
        archivo.addAction(self.save_yal_action)
        archivo.addAction(self.save_input_action)

        ejecutar = menu.addMenu("Ejecutar")
        ejecutar.addAction(self.generate_action)
        ejecutar.addAction(self.refresh_diagrams_action)

        ayuda = menu.addMenu("Ayuda")
        ayuda.addAction(self.load_examples_action)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(10, 8, 10, 10)
        root_layout.setSpacing(8)

        title = QLabel("Los Tres Furiosos - YALex Studio")
        title.setObjectName("TitleLabel")

        subtitle = QLabel("Generador y visualizador de analizadores léxicos")
        subtitle.setObjectName("MutedLabel")

        root_layout.addWidget(title)
        root_layout.addWidget(subtitle)

        main_splitter = QSplitter(Qt.Horizontal)

        self.sidebar_panel = self._build_sidebar_panel()
        center_panel = self._build_center_panel()
        self.diagram_panel = self._build_diagram_panel()

        main_splitter.addWidget(self.sidebar_panel)
        main_splitter.addWidget(center_panel)
        main_splitter.addWidget(self.diagram_panel)
        main_splitter.setSizes([240, 980, 420])

        root_layout.addWidget(main_splitter, 1)

    def _build_sidebar_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        files_group = QGroupBox("Explorador")
        files_layout = QVBoxLayout(files_group)
        files_layout.setContentsMargins(10, 12, 10, 10)
        files_layout.setSpacing(8)

        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderHidden(True)
        self.project_tree.itemClicked.connect(self._handle_tree_click)
        files_layout.addWidget(self.project_tree)

        quick_actions = QHBoxLayout()
        quick_actions.setSpacing(8)

        btn_example = QPushButton("Cargar ejemplo")
        btn_example.clicked.connect(self._load_default_example)

        btn_generate = QPushButton("Generar")
        btn_generate.clicked.connect(self.generate_project)

        quick_actions.addWidget(btn_example)
        quick_actions.addWidget(btn_generate)
        files_layout.addLayout(quick_actions)

        info_group = QGroupBox("Resumen")
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(10, 12, 10, 10)

        self.summary_label = QLabel(
            "Aún no se ha generado ningún lexer.\n\n"
            "Pasos sugeridos:\n"
            "• Carga un archivo .yal\n"
            "• Carga un archivo .txt\n"
            "• Presiona Generar lexer"
        )
        self.summary_label.setObjectName("SummaryCard")
        self.summary_label.setWordWrap(True)
        self.summary_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        info_layout.addWidget(self.summary_label)

        layout.addWidget(files_group, 3)
        layout.addWidget(info_group, 2)

        return panel
    
    def _build_center_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        vertical_splitter = QSplitter(Qt.Vertical)

        self.editor_tabs = QTabWidget()
        self.yal_editor = self._make_editor(
            "Escribe o carga aquí la especificación YALex..."
        )
        self.input_editor = self._make_editor(
            "Escribe o carga aquí el archivo de entrada..."
        )
        self.generated_editor = self._make_editor(
            "Aquí aparecerá el lexer generado en JavaScript...",
            read_only=True,
        )

        self.editor_tabs.addTab(self.yal_editor, "Especificación .yal")
        self.editor_tabs.addTab(self.input_editor, "Entrada .txt")
        self.editor_tabs.addTab(self.generated_editor, "lexer_generado.js")

        self.output_tabs = QTabWidget()

        self.tokens_table = QTableWidget(0, 4)
        self.tokens_table.setHorizontalHeaderLabels(["Token", "Lexema", "Línea", "Columna"])
        self.tokens_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tokens_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tokens_table.verticalHeader().setVisible(False)
        self.tokens_table.setAlternatingRowColors(True)

        self.errors_table = QTableWidget(0, 4)
        self.errors_table.setHorizontalHeaderLabels(["Mensaje", "Lexema", "Línea", "Columna"])
        self.errors_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.errors_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.errors_table.verticalHeader().setVisible(False)
        self.errors_table.setAlternatingRowColors(True)

        self.log_console = self._make_editor(
            "Aquí verás el log completo de la ejecución...",
            read_only=True,
        )

        self.output_tabs.addTab(self.tokens_table, "Tokens")
        self.output_tabs.addTab(self.errors_table, "Errores")
        self.output_tabs.addTab(self.log_console, "Salida")

        vertical_splitter.addWidget(self.editor_tabs)
        vertical_splitter.addWidget(self.output_tabs)
        vertical_splitter.setSizes([590, 270])

        layout.addWidget(vertical_splitter)
        return panel

    def _build_diagram_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        group = QGroupBox("Diagramas")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(10, 12, 10, 10)
        group_layout.setSpacing(8)

        row = QHBoxLayout()
        self.diagram_combo = QComboBox()
        self.diagram_combo.currentIndexChanged.connect(self.show_selected_diagram)

        refresh_button = QPushButton("Ver")
        refresh_button.clicked.connect(self.show_selected_diagram)
        refresh_button.setFixedWidth(60)

        row.addWidget(self.diagram_combo, 1)
        row.addWidget(refresh_button)

        self.diagram_info = QLabel("Aquí aparecerán los AFD generados.")
        self.diagram_info.setObjectName("MutedLabel")
        self.diagram_info.setWordWrap(True)

        self.diagram_label = QLabel("Sin diagrama seleccionado")
        self.diagram_label.setAlignment(Qt.AlignCenter)
        self.diagram_label.setMinimumHeight(520)
        self.diagram_label.setStyleSheet(
            "border: 1px dashed #3c3c3c; border-radius: 12px; padding: 10px; background-color: #1e1e1e;"
        )

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.diagram_container = QWidget()
        container_layout = QVBoxLayout(self.diagram_container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.addWidget(self.diagram_label, alignment=Qt.AlignCenter)
        container_layout.addStretch()

        scroll.setWidget(self.diagram_container)
        self.diagram_scroll = scroll

        group_layout.addLayout(row)
        group_layout.addWidget(self.diagram_info)
        group_layout.addWidget(scroll)

        layout.addWidget(group)
        return panel

    def _make_editor(self, placeholder: str, read_only: bool = False) -> QPlainTextEdit:
        editor = QPlainTextEdit()
        editor.setPlaceholderText(placeholder)
        editor.setReadOnly(read_only)
        editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        editor.setFont(QFont("Consolas", 11))
        return editor

    def _handle_tree_click(self, item: QTreeWidgetItem):
        kind = item.data(0, Qt.UserRole)
        if kind == "yal":
            self.editor_tabs.setCurrentIndex(0)
        elif kind == "txt":
            self.editor_tabs.setCurrentIndex(1)
        elif kind == "js":
            self.editor_tabs.setCurrentIndex(2)
        elif kind == "diagram":
            self.show_selected_diagram()

    def _refresh_tree(self):
        self.project_tree.clear()

        entrada = QTreeWidgetItem(["Entrada"])
        salida = QTreeWidgetItem(["Salida"])

        yal_name = Path(self.current_yal_path).name if self.current_yal_path else "Sin archivo .yal"
        txt_name = Path(self.current_input_path).name if self.current_input_path else "Sin archivo .txt"
        js_name = Path(self.current_generated_path).name if self.current_generated_path else "lexer_generado.js"

        yal_item = QTreeWidgetItem([yal_name])
        yal_item.setData(0, Qt.UserRole, "yal")

        txt_item = QTreeWidgetItem([txt_name])
        txt_item.setData(0, Qt.UserRole, "txt")

        js_item = QTreeWidgetItem([js_name])
        js_item.setData(0, Qt.UserRole, "js")

        diagram_item = QTreeWidgetItem(["Diagramas generados"])
        diagram_item.setData(0, Qt.UserRole, "diagram")

        entrada.addChild(yal_item)
        entrada.addChild(txt_item)
        salida.addChild(js_item)
        salida.addChild(diagram_item)

        self.project_tree.addTopLevelItem(entrada)
        self.project_tree.addTopLevelItem(salida)
        self.project_tree.expandAll()

    def _load_default_example(self):
        tests_dir = ROOT_DIR / "tests"
        default_yal = tests_dir / "alto.yal"
        default_txt = tests_dir / "alto.txt"

        if default_yal.exists():
            self.current_yal_path = str(default_yal)
            self.yal_editor.setPlainText(default_yal.read_text(encoding="utf-8"))

        if default_txt.exists():
            self.current_input_path = str(default_txt)
            self.input_editor.setPlainText(default_txt.read_text(encoding="utf-8"))

        self.editor_tabs.setCurrentIndex(0)
        self.output_tabs.setCurrentIndex(0)
        self._refresh_tree()
        self.status_bar.showMessage("Ejemplo cargado. Ya puedes generar el lexer.")

    def open_yal_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir especificación YALex",
            str(ROOT_DIR / "tests"),
            "Archivos YAL (*.yal);;Todos los archivos (*)",
        )
        if not file_path:
            return

        self.current_yal_path = file_path
        self.yal_editor.setPlainText(Path(file_path).read_text(encoding="utf-8"))
        self.editor_tabs.setCurrentIndex(0)
        self._refresh_tree()
        self.status_bar.showMessage(f"Se cargó {Path(file_path).name}")

    def open_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo de entrada",
            str(ROOT_DIR / "tests"),
            "Archivos de texto (*.txt);;Todos los archivos (*)",
        )
        if not file_path:
            return

        self.current_input_path = file_path
        self.input_editor.setPlainText(Path(file_path).read_text(encoding="utf-8"))
        self.editor_tabs.setCurrentIndex(1)
        self._refresh_tree()
        self.status_bar.showMessage(f"Se cargó {Path(file_path).name}")

    def save_yal_file(self):
        self.current_yal_path = self._save_editor_to_path(
            self.yal_editor,
            self.current_yal_path,
            "Guardar especificación YALex",
            "Archivos YAL (*.yal)",
        )
        self._refresh_tree()

    def save_input_file(self):
        self.current_input_path = self._save_editor_to_path(
            self.input_editor,
            self.current_input_path,
            "Guardar archivo de entrada",
            "Archivos de texto (*.txt)",
        )
        self._refresh_tree()

    def _save_editor_to_path(
        self,
        editor: QPlainTextEdit,
        current_path: str | None,
        dialog_title: str,
        file_filter: str,
    ) -> str | None:
        path = current_path
        if not path:
            path, _ = QFileDialog.getSaveFileName(
                self,
                dialog_title,
                str(ROOT_DIR / "tests"),
                file_filter,
            )
            if not path:
                return current_path

        Path(path).write_text(editor.toPlainText(), encoding="utf-8")
        self.status_bar.showMessage(f"Guardado: {Path(path).name}")
        return path

    def generate_project(self):
        result = run_pipeline(
            self.yal_editor.toPlainText(),
            self.input_editor.toPlainText(),
            yal_path=self.current_yal_path,
            input_path=self.current_input_path,
        )

        self.current_yal_path = result.yal_path
        self.current_input_path = result.input_path

        if not result.success:
            self._show_spec_error(result)
            return

        self.current_generated_path = result.output_file
        self.generated_editor.setPlainText(result.generated_code)
        self.log_console.setPlainText("\n".join(result.logs))

        self._fill_tokens_table(result)
        self._fill_errors_table(result)
        self._load_diagrams(result)
        self._update_summary(result)
        self._refresh_tree()

        if result.errors:
            self.output_tabs.setCurrentIndex(1)
        else:
            self.output_tabs.setCurrentIndex(0)

        self.editor_tabs.setCurrentIndex(2)
        self.status_bar.showMessage("Lexer generado correctamente.")

    def _show_spec_error(self, result: RunnerResult):
        self.log_console.setPlainText("\n".join(result.logs) if result.logs else "")
        self.tokens_table.setRowCount(0)
        self.errors_table.setRowCount(0)
        self.generated_editor.clear()
        self.diagram_combo.clear()
        self.diagram_label.setText("No se pudo generar el lexer.")
        self.diagram_info.setText("Corrige el archivo .yal y vuelve a intentarlo.")
        self.summary_label.setText(
            "Se encontró un error de especificación.\n\n"
            "No se pudo construir el lexer.\n"
            "Revisa la pestaña 'Salida' para ver el detalle y corregir el archivo .yal."
        )
        self.output_tabs.setCurrentIndex(2)
        QMessageBox.warning(self, "Error de especificación YALex", result.spec_error or "Error desconocido")
        self.status_bar.showMessage("Se encontró un error de especificación.")

    def _fill_tokens_table(self, result: RunnerResult):
        self.tokens_table.setRowCount(len(result.tokens))

        for row, token in enumerate(result.tokens):
            values = [
                token["token_name"],
                repr(token["lexeme"]),
                str(token["line"]),
                str(token["column"]),
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 0:
                    item.setForeground(QColor("#4FC1FF"))
                self.tokens_table.setItem(row, col, item)

        self.tokens_table.resizeColumnsToContents()

    def _fill_errors_table(self, result: RunnerResult):
        self.errors_table.setRowCount(len(result.errors))

        for row, error in enumerate(result.errors):
            values = [
                error["message"],
                repr(error["lexeme"]),
                str(error["line"]),
                str(error["column"]),
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setForeground(QColor("#F48771"))
                self.errors_table.setItem(row, col, item)

        self.errors_table.resizeColumnsToContents()

    def _load_diagrams(self, result: RunnerResult):
        self.diagram_combo.blockSignals(True)
        self.diagram_combo.clear()

        for image_path in result.image_files:
            image_name = Path(image_path).name
            self.diagram_combo.addItem(image_name, image_path)

        self.diagram_combo.blockSignals(False)

        if result.image_files:
            self.diagram_combo.setCurrentIndex(0)
            self.show_selected_diagram()
        else:
            self.current_image_path = None
            self.current_original_pixmap = None
            self.diagram_label.setPixmap(QPixmap())
            self.diagram_label.setText("No se generaron imágenes.\nRevisa si Graphviz está instalado.")
            self.diagram_info.setText("Puedes seguir usando el proyecto; solo faltó la renderización PNG.")

    def _update_summary(self, result: RunnerResult):
        token_count = len(result.tokens)
        error_count = len(result.errors)
        rules_count = result.rule_count
        defs_count = result.definitions_count
        diagrams_count = len(result.image_files) if result.image_files else len(result.diagram_files)

        status_text = "Sin errores léxicos" if error_count == 0 else f"Con {error_count} error(es) léxicos"

        self.summary_label.setText(
            f"Resumen de la ejecución\n\n"
            f"• Definiciones let: {defs_count}\n"
            f"• Reglas generadas: {rules_count}\n"
            f"• Tokens encontrados: {token_count}\n"
            f"• Estado: {status_text}\n"
            f"• Diagramas: {diagrams_count}\n\n"
            f"Salida principal:\n"
            f"{Path(result.output_file).name if result.output_file else 'No generada'}"
        )

    def show_selected_diagram(self):
        if self.diagram_combo.count() == 0:
            return

        image_path = self.diagram_combo.currentData()
        if not image_path:
            return

        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            self.diagram_label.setText("No se pudo cargar la imagen del diagrama.")
            return

        self.current_image_path = image_path
        self.current_original_pixmap = pixmap
        self.diagram_info.setText(f"Vista previa: {Path(image_path).name}")
        self._update_diagram_preview()

    def _update_diagram_preview(self):
        if self.current_original_pixmap is None:
            return

        viewport = self.diagram_scroll.viewport()
        available_width = max(280, viewport.width() - 30)
        available_height = max(300, viewport.height() - 30)

        scaled = self.current_original_pixmap.scaled(
            available_width,
            available_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        self.diagram_label.setPixmap(scaled)
        self.diagram_label.setMinimumSize(scaled.width() + 20, scaled.height() + 20)
        self.diagram_label.adjustSize()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_diagram_preview()