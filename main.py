import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow


class OpenDashWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("OpenDash")
        self.resize(800, 480)

        title = QLabel("OpenDash")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            """
            background-color: black;
            color: white;
            font-size: 48px;
            font-weight: bold;
            """
        )

        self.setCentralWidget(title)


def main() -> int:
    app = QApplication(sys.argv)
    window = OpenDashWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())