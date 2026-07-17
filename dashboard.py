from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class DashboardWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("OpenDash")
        self.resize(800, 480)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #050708;
            }

            QLabel {
                color: white;
                font-family: Arial;
            }

            QProgressBar {
                border: 1px solid #53616a;
                border-radius: 6px;
                background-color: #14191c;
                color: white;
                text-align: center;
                height: 28px;
            }

            QProgressBar::chunk {
                background-color: #3fd06f;
                border-radius: 5px;
            }
            """
        )

        self.ktrc_label = QLabel("KTRC 1")
        self.ktrc_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.power_label = QLabel("POWER F")
        self.power_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.power_label.setStyleSheet("font-size: 20px; font-weight: bold;")

        top_row = QHBoxLayout()
        top_row.addWidget(self.ktrc_label)
        top_row.addStretch()
        top_row.addWidget(self.power_label)

        self.speed_label = QLabel("000")
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_label.setStyleSheet(
            "font-size: 110px; font-weight: bold;"
        )

        self.mph_label = QLabel("MPH")
        self.mph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mph_label.setStyleSheet(
            "font-size: 24px; color: #9aa7ad;"
        )

        self.gear_label = QLabel("GEAR N")
        self.gear_label.setStyleSheet(
            "font-size: 30px; font-weight: bold;"
        )

        self.coolant_label = QLabel("COOLANT 172°F")
        self.coolant_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.coolant_label.setStyleSheet("font-size: 20px;")

        middle_row = QHBoxLayout()
        middle_row.addWidget(self.gear_label)
        middle_row.addStretch()
        middle_row.addWidget(self.coolant_label)

        self.fuel_bar = QProgressBar()
        self.fuel_bar.setRange(0, 100)
        self.fuel_bar.setValue(78)
        self.fuel_bar.setFormat("FUEL %p%")

        self.battery_label = QLabel("BATTERY 14.2V")
        self.battery_label.setStyleSheet("font-size: 18px;")

        self.clock_label = QLabel("10:42 PM")
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock_label.setStyleSheet("font-size: 18px;")

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.battery_label)
        bottom_row.addStretch()
        bottom_row.addWidget(self.clock_label)

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 22, 28, 22)
        layout.addLayout(top_row)
        layout.addStretch()
        layout.addWidget(self.speed_label)
        layout.addWidget(self.mph_label)
        layout.addStretch()
        layout.addLayout(middle_row)
        layout.addSpacing(18)
        layout.addWidget(self.fuel_bar)
        layout.addSpacing(12)
        layout.addLayout(bottom_row)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
