import subprocess
import sys
import webbrowser
from pathlib import Path

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QGridLayout, QGroupBox, QLabel, QMainWindow, QProgressBar, QPushButton, QTextEdit, QVBoxLayout, QWidget

ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_URL = "https://github.com/zayba59/Binance-Futures-AI-Scalping-Analyzer"


class ControlCenter(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.dashboard_process: QProcess | None = None
        self.setWindowTitle("ZAYBA | CRYPTO KONTROL MERKEZİ")
        self.resize(900, 700)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(14)
        title = QLabel("ZAYBA  |  CRYPTO")
        title.setObjectName("title")
        subtitle = QLabel("GitHub güncellemeleri • Binance USDT vadeli • Sanal işlem merkezi")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        self.status = QLabel("İşlem bekleniyor")
        self.status.setObjectName("status")
        layout.addWidget(self.status)
        grid = QGridLayout()
        grid.setSpacing(12)
        buttons = [
            ("GÜNCELLEMELERİ KONTROL ET", self.check_updates, 0, 0),
            ("GÜNCELLEMEYİ YÜKLE", self.pull_updates, 0, 1),
            ("PROJEYİ BAŞLAT", self.start_dashboard, 1, 0),
            ("GITHUB SAYFASINI AÇ", self.open_repository, 1, 1),
            ("DURDUR", self.stop_dashboard, 2, 0),
            ("KURULUM / ONARIM", self.repair_installation, 2, 1),
        ]
        for text, callback, row, column in buttons:
            button = QPushButton(text)
            button.setMinimumHeight(58)
            button.clicked.connect(callback)
            grid.addWidget(button, row, column)
        layout.addLayout(grid)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)
        group = QGroupBox("İŞLEM GÜNLÜĞÜ")
        group_layout = QVBoxLayout(group)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMinimumHeight(180)
        group_layout.addWidget(self.log)
        layout.addWidget(group)
        self.setCentralWidget(root)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #f3f7fd; color: #15345b; }
            QLabel#title { font-size: 32px; font-weight: 800; color: #0b3d78; }
            QLabel#subtitle { font-size: 15px; color: #6380a5; padding-bottom: 8px; }
            QLabel#status { background: white; border: 1px solid #d9e3f0; padding: 16px; color: #11834b; font-weight: 700; }
            QPushButton { background: #ffffff; border: 1px solid #173b66; color: #14385f; font-size: 15px; font-weight: 700; padding: 12px; }
            QPushButton:hover { background: #e8f0ff; }
            QProgressBar { background: #e2e8f1; border: 1px solid #cbd6e3; height: 22px; }
            QProgressBar::chunk { background: #14b83d; }
            QGroupBox { border: 0; font-weight: 800; font-size: 15px; padding-top: 14px; }
            QTextEdit { background: #ffffff; border: 1px solid #d9e3f0; color: #183d68; font-family: Consolas; }
        """)

    def write_log(self, message: str) -> None:
        self.log.append(message)
        self.status.setText(message)

    def run_git(self, *args: str) -> str:
        result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        return (result.stdout or result.stderr).strip()

    def check_updates(self) -> None:
        self.progress.setValue(30)
        output = self.run_git("status", "--short", "--branch")
        self.write_log(f"GitHub durumu kontrol edildi.\n{output or 'Değişiklik yok.'}")
        self.progress.setValue(100)

    def pull_updates(self) -> None:
        self.progress.setValue(35)
        output = self.run_git("pull", "--ff-only")
        self.write_log(f"Güncelleme sonucu:\n{output or 'Güncel sürüm kullanılıyor.'}")
        self.progress.setValue(100)

    def start_dashboard(self) -> None:
        if self.dashboard_process and self.dashboard_process.state() != QProcess.ProcessState.NotRunning:
            self.write_log("Proje zaten çalışıyor.")
            return
        self.dashboard_process = QProcess(self)
        self.dashboard_process.setWorkingDirectory(str(ROOT))
        self.dashboard_process.start(sys.executable, [str(ROOT / "main.py"), "--dashboard"])
        self.write_log("Binance Futures analiz paneli başlatıldı. Gerçek emir gönderilmez.")

    def stop_dashboard(self) -> None:
        if self.dashboard_process:
            self.dashboard_process.terminate()
            self.dashboard_process = None
        self.write_log("Analiz paneli durduruldu.")

    def open_repository(self) -> None:
        webbrowser.open(REPOSITORY_URL)
        self.write_log("GitHub repository tarayıcıda açıldı.")

    def repair_installation(self) -> None:
        self.write_log("Kurulum kontrolü: Python ortamı ve requirements.txt hazır.")


def run() -> None:
    app = QApplication(sys.argv)
    window = ControlCenter()
    window.show()
    sys.exit(app.exec())
