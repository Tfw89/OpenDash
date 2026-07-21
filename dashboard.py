import random
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from bike import BikeData


class DashboardWindow(QMainWindow):
    def __init__(self, bike: BikeData) -> None:
        super().__init__()

        self.bike = bike
        self.target_speed = 0

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

        self.ktrc_label = QLabel()
        self.ktrc_label.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        self.power_label = QLabel()
        self.power_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.power_label.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        top_row = QHBoxLayout()
        top_row.addWidget(self.ktrc_label)
        top_row.addStretch()
        top_row.addWidget(self.power_label)

        self.speed_label = QLabel()
        self.speed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speed_label.setStyleSheet(
            "font-size: 110px; font-weight: bold;"
        )

        self.mph_label = QLabel("MPH")
        self.mph_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mph_label.setStyleSheet(
            "font-size: 24px; color: #9aa7ad;"
        )

        self.gear_label = QLabel()
        self.gear_label.setStyleSheet(
            "font-size: 30px; font-weight: bold;"
        )

        self.coolant_label = QLabel()
        self.coolant_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.coolant_label.setStyleSheet("font-size: 20px;")

        middle_row = QHBoxLayout()
        middle_row.addWidget(self.gear_label)
        middle_row.addStretch()
        middle_row.addWidget(self.coolant_label)

        self.fuel_bar = QProgressBar()
        self.fuel_bar.setRange(0, 100)

        self.battery_label = QLabel()
        self.battery_label.setStyleSheet("font-size: 18px;")

        self.clock_label = QLabel()
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

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_speed)
        self.animation_timer.start(40)

        self.simulation_timer = QTimer(self)
        self.simulation_timer.timeout.connect(
            self.update_simulation_target
        )
        self.simulation_timer.start(1000)

        self.refresh_display()

    def update_simulation_target(self) -> None:
        speed_change = random.randint(-15, 25)

        self.target_speed += speed_change
        self.target_speed = max(0, min(186, self.target_speed))

        self.bike.coolant += random.choice([-1, 0, 0, 0, 1])
        self.bike.coolant = max(160, min(220, self.bike.coolant))

        self.bike.battery += random.choice(
            [-0.1, 0.0, 0.0, 0.1]
        )
        self.bike.battery = max(
            12.0,
            min(14.7, self.bike.battery),
        )

    def animate_speed(self) -> None:
        if self.bike.speed < self.target_speed:
            self.bike.speed += 1
        elif self.bike.speed > self.target_speed:
            self.bike.speed -= 1

        if self.bike.speed == 0:
            self.bike.gear = "N"
        elif self.bike.speed < 20:
            self.bike.gear = "1"
        elif self.bike.speed < 40:
            self.bike.gear = "2"
        elif self.bike.speed < 65:
            self.bike.gear = "3"
        elif self.bike.speed < 95:
            self.bike.gear = "4"
        elif self.bike.speed < 130:
            self.bike.gear = "5"
        else:
            self.bike.gear = "6"

        self.refresh_display()

    def refresh_display(self) -> None:
        self.speed_label.setText(f"{self.bike.speed:03}")
        self.gear_label.setText(f"GEAR {self.bike.gear}")
        self.coolant_label.setText(
            f"COOLANT {self.bike.coolant}°F"
        )
        self.battery_label.setText(
            f"BATTERY {self.bike.battery:.1f}V"
        )
        self.ktrc_label.setText(f"KTRC {self.bike.ktrc}")
        self.power_label.setText(
            f"POWER {self.bike.power_mode}"
        )

        self.fuel_bar.setValue(self.bike.fuel)
        self.fuel_bar.setFormat(
            f"FUEL {self.bike.fuel}%"
        )

        current_time = datetime.now().strftime("%I:%M:%S %p")
        self.clock_label.setText(
            current_time.lstrip("0")
        )