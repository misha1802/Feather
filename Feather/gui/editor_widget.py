from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtGui import QFont, QTextOption

class EditorWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Ubuntu Mono", 11))
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(" ") * 4)
        self.setWordWrapMode(QTextOption.NoWrap)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                padding: 12px;
            }
        """)

    def set_text(self, text):
        self.setPlainText(text)

    def get_text(self):
        return self.toPlainText()
