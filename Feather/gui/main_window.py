from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QFileDialog, QPlainTextEdit, QSplitter, QPushButton, 
                             QTreeView, QFileSystemModel)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt, QDir
from gui.editor_widget import EditorWidget
from core.runner import CodeRunner

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Feather")
        self.setGeometry(100, 100, 1000, 650)
        self.current_file = None
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #242424;
            }
            QWidget#header_bar {
                background-color: #303030;
                border-bottom: 1px solid #1c1c1c;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: #ffffff;
                font-family: 'Ubuntu', sans-serif;
                font-size: 10pt;
                font-weight: bold;
                padding: 6px 14px;
                border: 1px solid #1c1c1c;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QTreeView {
                background-color: #1a1a1a;
                color: #e0e0e0;
                border: none;
                font-family: 'Ubuntu', sans-serif;
                font-size: 10pt;
            }
            QTreeView::item {
                padding: 6px;
            }
            QTreeView::item:hover {
                background-color: rgba(255, 255, 255, 0.05);
            }
            QTreeView::item:selected {
                background-color: #3584e4;
                color: #ffffff;
            }
            QSplitter::handle {
                background-color: #1c1c1c;
            }
        """)

        self.runner = CodeRunner()
        self.runner.output_received.connect(self.append_to_terminal)
        self.runner.finished.connect(self.process_finished)
        
        self.editor = EditorWidget()
        
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.file_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.file_model.setNameFilters(["*.py"])
        self.file_model.setNameFilterDisables(False)
        
        self.sidebar = QTreeView()
        self.sidebar.setModel(self.file_model)
        self.sidebar.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.sidebar.clicked.connect(self.sidebar_file_clicked)
        self.sidebar.setHeaderHidden(True)
        for i in range(1, self.file_model.columnCount()):
            self.sidebar.hideColumn(i)
        
        self.terminal = QPlainTextEdit()
        self.terminal.setFont(QFont("Ubuntu Mono", 10))
        self.terminal.setStyleSheet("""
            QPlainTextEdit {
                background-color: #ffffff;
                color: #000000;
                border: none;
                padding: 12px;
            }
        """)
        self.terminal.installEventFilter(self)

        header_bar = QWidget()
        header_bar.setObjectName("header_bar")
        header_bar.setFixedHeight(50)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 0, 12, 0)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignVertical_Mask)
        
        self.open_folder_btn = QPushButton("Open Folder")
        self.open_btn = QPushButton("Open File")
        self.save_btn = QPushButton("Save")
        self.run_btn = QPushButton("Run (F5)")
        
        header_layout.addWidget(self.open_folder_btn)
        header_layout.addWidget(self.open_btn)
        header_layout.addWidget(self.save_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.run_btn)
        header_bar.setLayout(header_layout)

        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.editor)
        right_splitter.addWidget(self.terminal)
        right_splitter.setSizes([300, 300])

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.sidebar)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([200, 800])
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(header_bar)
        main_layout.addWidget(main_splitter)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.open_folder_btn.clicked.connect(self.open_folder)
        self.open_btn.clicked.connect(self.open_file)
        self.save_btn.clicked.connect(self.save_file)
        self.run_btn.clicked.connect(self.run_code)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F5:
            self.run_code()
        else:
            super().keyPressEvent(event)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder", QDir.currentPath())
        if folder_path:
            self.sidebar.setRootIndex(self.file_model.index(folder_path))

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Python Files (*.py);;All Files (*)")
        if file_path:
            self.load_file(file_path)

    def sidebar_file_clicked(self, index):
        file_path = self.file_model.filePath(index)
        if not self.file_model.isDir(index):
            self.load_file(file_path)

    def load_file(self, file_path):
        self.current_file = file_path
        with open(file_path, "r", encoding="utf-8") as f:
            self.editor.set_text(f.read())
        self.setWindowTitle(f"Feather - {file_path}")

    def save_file(self):
        if not self.current_file:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Python Files (*.py);;All Files (*)")
            if file_path:
                self.current_file = file_path
            else:
                return
        
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(self.editor.get_text())
        self.setWindowTitle(f"Feather - {self.current_file}")

    def run_code(self):
        self.runner.cleanup()
        self.terminal.clear()
        code = self.editor.get_text()
        self.runner.run(code)

    def append_to_terminal(self, text):
        self.terminal.moveCursor(QTextCursor.End)
        self.terminal.insertPlainText(text)
        self.terminal.moveCursor(QTextCursor.End)

    def process_finished(self):
        self.append_to_terminal("\n[Process finished]")

    def eventFilter(self, obj, event):
        if obj == self.terminal and event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                cursor = self.terminal.textCursor()
                cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
                line_text = cursor.selectedText() + "\n"
                self.runner.write_input(line_text)
                self.append_to_terminal("\n")
                return True
        return super().eventFilter(obj, event)
        
    def closeEvent(self, event):
        self.runner.cleanup()
        super().closeEvent(event)
