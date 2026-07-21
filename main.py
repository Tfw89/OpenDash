import sys

from PySide6.QtWidgets import QApplication

from bike import BikeData
from dashboard import DashboardWindow


def main() -> int:
    app = QApplication(sys.argv)

    bike = BikeData()
    window = DashboardWindow(bike)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())