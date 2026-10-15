import os
from PySide6.QtCore import QProcess, QObject, Signal

class CodeRunner(QObject):
    output_received = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.process = None
        self.temp_file = "temp_feather_run.py"

    def run(self, code):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.process.waitForFinished()

        with open(self.temp_file, "w", encoding="utf-8") as f:
            f.write(code)
            f.flush()
            os.fsync(f.fileno())

        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.handle_finish)
        self.process.start("python3", [self.temp_file])

    def write_input(self, text):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.write(text.encode("utf-8"))

    def handle_output(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8")
        self.output_received.emit(data)

    def handle_finish(self):
        self.finished.emit()

    def cleanup(self):
        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except:
                pass
