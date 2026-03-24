APP_STYLE = """
QMainWindow, QWidget {
    background-color: #181a1f;
    color: #e6edf3;
    font-family: "Segoe UI", "Consolas", "Cascadia Code", sans-serif;
    font-size: 12px;
}

QMenuBar {
    background-color: #20232b;
    color: #e6edf3;
    border-bottom: 1px solid #2f3440;
}

QMenuBar::item {
    background: transparent;
    padding: 6px 10px;
}

QMenuBar::item:selected {
    background: #2b3140;
    border-radius: 6px;
}

QMenu {
    background-color: #20232b;
    color: #e6edf3;
    border: 1px solid #2f3440;
}

QMenu::item:selected {
    background-color: #1f6feb;
    color: white;
}

QToolBar {
    background-color: #20232b;
    border: none;
    spacing: 6px;
    padding: 6px 8px;
}

QToolButton {
    background-color: #252a36;
    color: #e6edf3;
    border: 1px solid #364152;
    border-radius: 10px;
    padding: 8px 14px;
    min-height: 18px;
}

QToolButton:hover {
    background-color: #2d3748;
    border: 1px solid #57c7ff;
    color: #ffffff;
}

QToolButton:pressed {
    background-color: #1f6feb;
    border: 1px solid #79d7ff;
}

QStatusBar {
    background-color: #36c2ff;
    color: #081018;
    border-top: 1px solid #57c7ff;
    font-weight: 600;
}

QTabWidget::pane {
    border: 1px solid #2f3440;
    background: #20232b;
    border-radius: 10px;
    top: -1px;
}

QTabBar::tab {
    background: #252a36;
    color: #b9c4d0;
    padding: 9px 16px;
    margin-right: 3px;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}

QTabBar::tab:selected {
    background: #181a1f;
    color: #ffffff;
    border-bottom: 2px solid #36c2ff;
}

QTabBar::tab:hover {
    background: #2d3748;
    color: #ffffff;
}

QPlainTextEdit, QTextEdit {
    background-color: #11141a;
    color: #e6edf3;
    border: 1px solid #2f3440;
    border-radius: 12px;
    selection-background-color: #1f6feb;
    padding: 10px;
    font-family: "Consolas", "Cascadia Code", monospace;
    font-size: 12px;
}

QTreeWidget, QListWidget, QTableWidget, QComboBox {
    background-color: #20232b;
    color: #e6edf3;
    border: 1px solid #2f3440;
    border-radius: 12px;
    padding: 4px;
}

QTreeWidget::item, QListWidget::item {
    padding: 6px;
    border-radius: 6px;
}

QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #36c2ff;
    color: #081018;
    font-weight: 600;
}

QHeaderView::section {
    background-color: #252a36;
    color: #dbe7f3;
    border: none;
    border-right: 1px solid #2f3440;
    border-bottom: 1px solid #2f3440;
    padding: 8px;
    font-weight: 600;
}

QTableWidget {
    gridline-color: #2f3440;
    alternate-background-color: #1a1e27;
}

QTableWidget::item:selected {
    background-color: #1f6feb;
    color: white;
}

QPushButton {
    background-color: #36c2ff;
    color: #081018;
    border: none;
    border-radius: 10px;
    padding: 8px 14px;
    font-weight: 700;
    min-height: 18px;
}

QPushButton:hover {
    background-color: #57c7ff;
    color: #041018;
}

QPushButton:pressed {
    background-color: #1f6feb;
    color: white;
}

QLabel#TitleLabel {
    font-size: 24px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 4px;
    margin-bottom: 0px;
}

QLabel#MutedLabel {
    color: #8fa3b8;
    font-size: 12px;
    margin-top: 0px;
    margin-bottom: 2px;
}

QLabel#SummaryCard {
    background-color: #20232b;
    border: 1px solid #2f3440;
    border-radius: 14px;
    padding: 14px;
    color: #e6edf3;
    line-height: 1.4;
}

QGroupBox {
    border: 1px solid #2f3440;
    border-radius: 14px;
    margin-top: 10px;
    padding-top: 10px;
    background-color: #20232b;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px 0 6px;
    color: #ffffff;
}

QScrollArea {
    border: 1px solid #2f3440;
    border-radius: 12px;
    background: #20232b;
}

QSplitter::handle {
    background: #2f3440;
}

QSplitter::handle:hover {
    background: #36c2ff;
}
"""