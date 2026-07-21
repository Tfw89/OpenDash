import random
from datetime import datetime

from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    Property,
    QPropertyAnimation,
    QRectF,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from bike import BikeData


# ============================================================
# FONT HELPERS
# ============================================================

def find_font_family(candidates: list[str]) -> str:
    available = {
        family.lower(): family
        for family in QFontDatabase.families()
    }

    for candidate in candidates:
        match = available.get(candidate.lower())

        if match:
            return match

    return QFontDatabase.systemFont(
        QFontDatabase.SystemFont.FixedFont
    ).family()


def create_digital_font(
    pixel_size: int,
    bold: bool = True,
) -> QFont:
    family = find_font_family(
        [
            "DSEG7 Classic",
            "DSEG7 Modern",
            "Digital-7",
            "DS-Digital",
            "Quartz",
            "LCDMono2",
            "OCR A Extended",
            "Consolas",
            "Courier New",
        ]
    )

    font = QFont(family)
    font.setPixelSize(pixel_size)
    font.setBold(bold)
    font.setStyleStrategy(
        QFont.StyleStrategy.PreferAntialias
    )

    return font


def create_condensed_font(
    pixel_size: int,
    bold: bool = False,
    italic: bool = False,
) -> QFont:
    family = find_font_family(
        [
            "Arial Narrow",
            "Roboto Condensed",
            "Bahnschrift Condensed",
            "DIN Condensed",
            "Liberation Sans Narrow",
            "Arial",
        ]
    )

    font = QFont(family)
    font.setPixelSize(pixel_size)
    font.setBold(bold)
    font.setItalic(italic)
    font.setStretch(QFont.Stretch.Condensed)

    return font


# ============================================================
# BOOT LOADING BAR
# ============================================================

class SlantedLoadingBar(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._progress = 0.0

        self.setMinimumSize(440, 24)
        self.setMaximumHeight(24)

    def get_progress(self) -> float:
        return self._progress

    def set_progress(self, value: float) -> None:
        self._progress = max(
            0.0,
            min(100.0, float(value)),
        )

        self.update()

    progress = Property(
        float,
        get_progress,
        set_progress,
    )

    def paintEvent(self, event) -> None:
        del event

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        width = float(self.width())
        height = float(self.height())
        slant = 12.0

        track = QPainterPath()
        track.moveTo(slant, 2.0)
        track.lineTo(width, 2.0)
        track.lineTo(width - slant, height - 2.0)
        track.lineTo(0.0, height - 2.0)
        track.closeSubpath()

        painter.fillPath(
            track,
            QColor("#101719"),
        )

        painter.setPen(
            QPen(
                QColor("#445157"),
                1.2,
            )
        )

        painter.drawPath(track)

        fill_width = (
            width - slant
        ) * (
            self._progress / 100.0
        )

        if fill_width <= 1.0:
            return

        fill_end = min(
            width,
            slant + fill_width,
        )

        fill = QPainterPath()
        fill.moveTo(slant, 4.0)
        fill.lineTo(fill_end, 4.0)
        fill.lineTo(
            max(0.0, fill_end - slant),
            height - 4.0,
        )
        fill.lineTo(3.0, height - 4.0)
        fill.closeSubpath()

        painter.fillPath(
            fill,
            QColor("#35E16F"),
        )


# ============================================================
# OPENDASH BOOT LOGO
# ============================================================

class SparkleLogo(QWidget):
    def __init__(
        self,
        text: str,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.text = text
        self._sparkle_position = 0.0

        self.setMinimumSize(600, 150)

    def get_sparkle_position(self) -> float:
        return self._sparkle_position

    def set_sparkle_position(
        self,
        value: float,
    ) -> None:
        self._sparkle_position = value
        self.update()

    sparkle_position = Property(
        float,
        get_sparkle_position,
        set_sparkle_position,
    )

    def paintEvent(self, event) -> None:
        del event

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setRenderHint(
            QPainter.RenderHint.TextAntialiasing
        )

        logo_font = create_condensed_font(
            72,
            bold=True,
            italic=True,
        )

        painter.setFont(logo_font)
        painter.setPen(QColor("#F5F7F7"))

        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            self.text,
        )

        sparkle_x = (
            self.width()
            * self._sparkle_position
        )

        center_y = self.height() / 2.0

        painter.setPen(
            QPen(
                QColor(255, 255, 255, 220),
                3.0,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )

        painter.drawLine(
            QPointF(sparkle_x - 22, center_y),
            QPointF(sparkle_x + 22, center_y),
        )

        painter.drawLine(
            QPointF(sparkle_x, center_y - 22),
            QPointF(sparkle_x, center_y + 22),
        )

        painter.setPen(
            QPen(
                QColor(255, 255, 255, 130),
                1.8,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )

        painter.drawLine(
            QPointF(
                sparkle_x - 13,
                center_y - 13,
            ),
            QPointF(
                sparkle_x + 13,
                center_y + 13,
            ),
        )

        painter.drawLine(
            QPointF(
                sparkle_x + 13,
                center_y - 13,
            ),
            QPointF(
                sparkle_x - 13,
                center_y + 13,
            ),
        )


# ============================================================
# MAIN TFT DASHBOARD
# ============================================================

class EnduroDashboardWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.speed = 0
        self.rpm = 1200
        self.gear = "N"
        self.fuel = 80
        self.coolant = 185
        self.battery = 14.2
        self.ktrc = 1
        self.power_mode = "F"

        self.maximum_rpm = 11000

        self.setMinimumSize(800, 480)

    def set_data(
        self,
        speed: int,
        rpm: int,
        gear: str,
        fuel: int,
        coolant: int,
        battery: float,
        ktrc,
        power_mode,
    ) -> None:
        self.speed = speed
        self.rpm = rpm
        self.gear = gear
        self.fuel = fuel
        self.coolant = coolant
        self.battery = battery
        self.ktrc = ktrc
        self.power_mode = power_mode

        self.update()

    def scaled_point(
        self,
        x: float,
        y: float,
    ) -> QPointF:
        return QPointF(
            x * self.width() / 800.0,
            y * self.height() / 480.0,
        )

    def scaled_rect(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> QRectF:
        return QRectF(
            x * self.width() / 800.0,
            y * self.height() / 480.0,
            width * self.width() / 800.0,
            height * self.height() / 480.0,
        )

    def scale_x(self, value: float) -> float:
        return value * self.width() / 800.0

    def scale_y(self, value: float) -> float:
        return value * self.height() / 480.0

    def draw_background(
        self,
        painter: QPainter,
    ) -> None:
        painter.fillRect(
            self.rect(),
            QColor("#010403"),
        )

        # Green focus glow behind the speed display.
        center_glow = QRadialGradient(
            self.width() * 0.48,
            self.height() * 0.56,
            self.width() * 0.49,
        )

        center_glow.setColorAt(
            0.00,
            QColor(15, 78, 39, 175),
        )

        center_glow.setColorAt(
            0.22,
            QColor(9, 52, 27, 150),
        )

        center_glow.setColorAt(
            0.48,
            QColor(5, 30, 16, 120),
        )

        center_glow.setColorAt(
            0.72,
            QColor(2, 14, 7, 80),
        )

        center_glow.setColorAt(
            1.00,
            QColor(0, 0, 0, 0),
        )

        painter.fillRect(
            self.rect(),
            center_glow,
        )

        # Approximately 50% stronger than the previous border vignette.
        vignette = QRadialGradient(
            self.width() * 0.49,
            self.height() * 0.53,
            max(
                self.width(),
                self.height(),
            ) * 0.63,
        )

        vignette.setColorAt(
            0.00,
            QColor(0, 0, 0, 0),
        )

        vignette.setColorAt(
            0.34,
            QColor(0, 0, 0, 8),
        )

        vignette.setColorAt(
            0.50,
            QColor(0, 0, 0, 55),
        )

        vignette.setColorAt(
            0.64,
            QColor(0, 0, 0, 145),
        )

        vignette.setColorAt(
            0.76,
            QColor(0, 0, 0, 220),
        )

        vignette.setColorAt(
            0.86,
            QColor(0, 0, 0, 248),
        )

        vignette.setColorAt(
            1.00,
            QColor(0, 0, 0, 255),
        )

        painter.fillRect(
            self.rect(),
            vignette,
        )

    def draw_top_status(
        self,
        painter: QPainter,
    ) -> None:
        small_font = create_condensed_font(
            max(10, int(self.scale_y(12))),
            bold=True,
        )

        painter.setFont(small_font)

        painter.setPen(
            QColor(210, 220, 218, 215)
        )

        painter.drawText(
            self.scaled_rect(
                50,
                27,
                110,
                25,
            ),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
            "ROAD",
        )

        signal_x = 132.0

        for index in range(6):
            bar_height = 5.0 + index * 2.2

            rect = self.scaled_rect(
                signal_x + index * 7.0,
                46.0 - bar_height,
                4.0,
                bar_height,
            )

            painter.fillRect(
                rect,
                QColor(205, 216, 216, 220),
            )

        title_font = create_condensed_font(
            max(10, int(self.scale_y(13))),
            bold=True,
            italic=True,
        )

        painter.setFont(title_font)

        painter.setPen(
            QColor(225, 188, 59, 235)
        )

        painter.drawText(
            self.scaled_rect(
                530,
                17,
                155,
                28,
            ),
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter,
            "OPEN DASH",
        )

    def rpm_centerline(
        self,
        fraction: float,
    ) -> QPointF:
        fraction = max(
            0.0,
            min(1.0, fraction),
        )

        start = self.scaled_point(
            115,
            187,
        )

        end = self.scaled_point(
            625,
            71,
        )

        return QPointF(
            start.x()
            + (
                end.x() - start.x()
            ) * fraction,
            start.y()
            + (
                end.y() - start.y()
            ) * fraction,
        )

    def rpm_normal(self) -> QPointF:
        start = self.rpm_centerline(0.0)
        end = self.rpm_centerline(1.0)

        dx = end.x() - start.x()
        dy = end.y() - start.y()

        length = max(
            1.0,
            (
                dx * dx
                + dy * dy
            ) ** 0.5,
        )

        return QPointF(
            -dy / length,
            dx / length,
        )

    def create_rpm_segment(
        self,
        start_fraction: float,
        end_fraction: float,
        lower_width: float,
        upper_width: float,
    ) -> QPolygonF:
        start = self.rpm_centerline(
            start_fraction
        )

        end = self.rpm_centerline(
            end_fraction
        )

        normal = self.rpm_normal()

        return QPolygonF(
            [
                QPointF(
                    start.x()
                    + normal.x() * upper_width,
                    start.y()
                    + normal.y() * upper_width,
                ),
                QPointF(
                    end.x()
                    + normal.x() * upper_width,
                    end.y()
                    + normal.y() * upper_width,
                ),
                QPointF(
                    end.x()
                    - normal.x() * lower_width,
                    end.y()
                    - normal.y() * lower_width,
                ),
                QPointF(
                    start.x()
                    - normal.x() * lower_width,
                    start.y()
                    - normal.y() * lower_width,
                ),
            ]
        )

    def draw_rpm_gauge(
        self,
        painter: QPainter,
    ) -> None:
        normal = self.rpm_normal()

        # Dark full gauge foundation.
        full_track = self.create_rpm_segment(
            0.0,
            1.0,
            self.scale_y(19),
            self.scale_y(8),
        )

        track_gradient = QLinearGradient(
            self.rpm_centerline(0.0),
            self.rpm_centerline(1.0),
        )

        track_gradient.setColorAt(
            0.00,
            QColor(19, 30, 35, 235),
        )

        track_gradient.setColorAt(
            0.62,
            QColor(24, 32, 38, 235),
        )

        track_gradient.setColorAt(
            1.00,
            QColor(44, 13, 18, 240),
        )

        painter.setPen(
            QPen(
                QColor(80, 100, 108, 160),
                self.scale_y(1.0),
            )
        )

        painter.setBrush(track_gradient)
        painter.drawPolygon(full_track)

        # Red warning blocks from 6,000 RPM upward.
        warning_segments = [
            (6, 7, QColor(94, 18, 27, 205)),
            (7, 8, QColor(112, 18, 27, 215)),
            (8, 9, QColor(139, 17, 27, 225)),
            (9, 10, QColor(175, 19, 28, 235)),
            (10, 11, QColor(214, 23, 32, 245)),
        ]

        for start_value, end_value, color in warning_segments:
            segment = self.create_rpm_segment(
                start_value / 11.0,
                end_value / 11.0,
                self.scale_y(18),
                self.scale_y(7),
            )

            painter.setPen(
                QPen(
                    QColor(226, 35, 45, 110),
                    self.scale_y(0.8),
                )
            )

            painter.setBrush(color)
            painter.drawPolygon(segment)

        # Active RPM illumination.
        rpm_fraction = min(
            1.0,
            self.rpm / self.maximum_rpm,
        )

        if rpm_fraction > 0.0:
            active = self.create_rpm_segment(
                0.0,
                rpm_fraction,
                self.scale_y(12),
                self.scale_y(4),
            )

            active_gradient = QLinearGradient(
                self.rpm_centerline(0.0),
                self.rpm_centerline(1.0),
            )

            active_gradient.setColorAt(
                0.00,
                QColor(123, 150, 158, 205),
            )

            active_gradient.setColorAt(
                0.50,
                QColor(195, 210, 210, 220),
            )

            active_gradient.setColorAt(
                0.72,
                QColor(224, 225, 208, 225),
            )

            active_gradient.setColorAt(
                0.82,
                QColor(255, 112, 55, 235),
            )

            active_gradient.setColorAt(
                1.00,
                QColor(255, 30, 38, 250),
            )

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(active_gradient)
            painter.drawPolygon(active)

        tick_font = create_condensed_font(
            max(10, int(self.scale_y(15))),
            bold=True,
        )

        painter.setFont(tick_font)

        for value in range(3, 12):
            fraction = value / 11.0
            point = self.rpm_centerline(fraction)

            tick_start = QPointF(
                point.x()
                + normal.x() * self.scale_y(9),
                point.y()
                + normal.y() * self.scale_y(9),
            )

            tick_end = QPointF(
                point.x()
                + normal.x() * self.scale_y(20),
                point.y()
                + normal.y() * self.scale_y(20),
            )

            if value >= 9:
                color = QColor(
                    255,
                    45,
                    52,
                    245,
                )

            elif value >= 6:
                color = QColor(
                    235,
                    70,
                    70,
                    230,
                )

            else:
                color = QColor(
                    194,
                    205,
                    205,
                    220,
                )

            painter.setPen(
                QPen(
                    color,
                    self.scale_y(1.3),
                )
            )

            painter.drawLine(
                tick_start,
                tick_end,
            )

            label_rect = QRectF(
                tick_end.x() - self.scale_x(16),
                tick_end.y() - self.scale_y(26),
                self.scale_x(32),
                self.scale_y(22),
            )

            painter.setPen(color)

            painter.drawText(
                label_rect,
                Qt.AlignmentFlag.AlignCenter,
                str(value),
            )

        rpm_label_font = create_condensed_font(
            max(8, int(self.scale_y(10))),
            bold=True,
        )

        painter.setFont(rpm_label_font)

        painter.setPen(
            QColor(150, 164, 165, 200)
        )

        painter.drawText(
            self.scaled_rect(
                116,
                195,
                110,
                20,
            ),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
            "x1000 r/min",
        )

    def draw_speed(
        self,
        painter: QPainter,
    ) -> None:
        speed_font = create_digital_font(
            max(
                92,
                int(self.scale_y(132)),
            ),
            bold=True,
        )

        painter.setFont(speed_font)

        speed_text = str(
            max(0, int(self.speed))
        )

        speed_rect = self.scaled_rect(
            250,
            188,
            270,
            170,
        )

        # Subtle dark shadow beneath the digital number.
        painter.setPen(
            QColor(0, 0, 0, 210)
        )

        shadow_rect = QRectF(
            speed_rect.x()
            + self.scale_x(4),
            speed_rect.y()
            + self.scale_y(5),
            speed_rect.width(),
            speed_rect.height(),
        )

        painter.drawText(
            shadow_rect,
            Qt.AlignmentFlag.AlignCenter,
            speed_text,
        )

        speed_gradient = QLinearGradient(
            speed_rect.topLeft(),
            speed_rect.bottomLeft(),
        )

        speed_gradient.setColorAt(
            0.00,
            QColor("#F5FAF9"),
        )

        speed_gradient.setColorAt(
            0.48,
            QColor("#DCE8E6"),
        )

        speed_gradient.setColorAt(
            1.00,
            QColor("#A7B6B5"),
        )

        painter.setPen(
            QPen(
                speed_gradient,
                self.scale_y(1.0),
            )
        )

        painter.drawText(
            speed_rect,
            Qt.AlignmentFlag.AlignCenter,
            speed_text,
        )

        unit_font = create_condensed_font(
            max(10, int(self.scale_y(17))),
            bold=True,
        )

        painter.setFont(unit_font)

        painter.setPen(
            QColor(185, 198, 197, 220)
        )

        painter.drawText(
            self.scaled_rect(
                497,
                294,
                74,
                25,
            ),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
            "mph",
        )

    def draw_gear_and_warnings(
        self,
        painter: QPainter,
    ) -> None:
        gear_font = create_condensed_font(
            max(34, int(self.scale_y(49))),
            bold=True,
            italic=True,
        )

        painter.setFont(gear_font)

        gear_color = (
            QColor("#39E96E")
            if self.gear == "N"
            else QColor("#EAF2F0")
        )

        painter.setPen(gear_color)

        painter.drawText(
            self.scaled_rect(
                640,
                163,
                75,
                72,
            ),
            Qt.AlignmentFlag.AlignCenter,
            self.gear,
        )

        warning_font = create_condensed_font(
            max(14, int(self.scale_y(20))),
            bold=True,
        )

        painter.setFont(warning_font)

        painter.setPen(
            QColor(235, 149, 33, 245)
        )

        painter.drawText(
            self.scaled_rect(
                716,
                180,
                45,
                28,
            ),
            Qt.AlignmentFlag.AlignCenter,
            "⚠",
        )

        painter.drawText(
            self.scaled_rect(
                716,
                216,
                45,
                28,
            ),
            Qt.AlignmentFlag.AlignCenter,
            "Ⓐ",
        )

    def draw_lower_information(
        self,
        painter: QPainter,
    ) -> None:
        label_font = create_condensed_font(
            max(9, int(self.scale_y(12))),
            bold=True,
        )

        painter.setFont(label_font)

        painter.setPen(
            QColor(180, 194, 193, 220)
        )

        painter.drawText(
            self.scaled_rect(
                48,
                362,
                95,
                25,
            ),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
            f"{self.coolant}°F",
        )

        painter.drawText(
            self.scaled_rect(
                50,
                402,
                110,
                22,
            ),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
            "FUEL",
        )

        # Fuel gauge.
        fuel_x = 111.0
        fuel_y = 408.0
        fuel_width = 105.0
        segment_count = 7

        active_segments = round(
            max(
                0,
                min(100, self.fuel),
            )
            / 100.0
            * segment_count
        )

        for index in range(segment_count):
            segment_rect = self.scaled_rect(
                fuel_x + index * 15.0,
                fuel_y,
                11.0,
                8.0,
            )

            if index < active_segments:
                color = QColor(
                    215,
                    226,
                    223,
                    225,
                )
            else:
                color = QColor(
                    60,
                    72,
                    72,
                    175,
                )

            painter.fillRect(
                segment_rect,
                color,
            )

        painter.setPen(
            QColor(146, 159, 159, 215)
        )

        painter.drawText(
            self.scaled_rect(
                300,
                392,
                150,
                25,
            ),
            Qt.AlignmentFlag.AlignCenter,
            f"{self.battery:.1f}V",
        )

        painter.drawText(
            self.scaled_rect(
                455,
                392,
                120,
                25,
            ),
            Qt.AlignmentFlag.AlignCenter,
            f"KTRC {self.ktrc}",
        )

        painter.drawText(
            self.scaled_rect(
                550,
                392,
                110,
                25,
            ),
            Qt.AlignmentFlag.AlignCenter,
            f"PWR {self.power_mode}",
        )

        clock_font = create_digital_font(
            max(11, int(self.scale_y(16))),
            bold=False,
        )

        painter.setFont(clock_font)

        painter.setPen(
            QColor(176, 191, 190, 225)
        )

        time_text = datetime.now().strftime(
            "%H:%M"
        )

        painter.drawText(
            self.scaled_rect(
                650,
                392,
                105,
                30,
            ),
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter,
            time_text,
        )

        # Small decorative line under the speed.
        pulse_path = QPainterPath()

        pulse_path.moveTo(
            self.scaled_point(342, 382)
        )

        pulse_path.lineTo(
            self.scaled_point(368, 382)
        )

        pulse_path.lineTo(
            self.scaled_point(379, 374)
        )

        pulse_path.lineTo(
            self.scaled_point(387, 388)
        )

        pulse_path.lineTo(
            self.scaled_point(399, 379)
        )

        pulse_path.lineTo(
            self.scaled_point(426, 379)
        )

        painter.setPen(
            QPen(
                QColor(221, 180, 43, 215),
                self.scale_y(1.2),
            )
        )

        painter.drawPath(pulse_path)

    def paintEvent(self, event) -> None:
        del event

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setRenderHint(
            QPainter.RenderHint.TextAntialiasing
        )

        self.draw_background(painter)
        self.draw_top_status(painter)
        self.draw_rpm_gauge(painter)
        self.draw_speed(painter)
        self.draw_gear_and_warnings(painter)
        self.draw_lower_information(painter)


# ============================================================
# MAIN WINDOW
# ============================================================

class DashboardWindow(QMainWindow):
    def __init__(
        self,
        bike: BikeData,
    ) -> None:
        super().__init__()

        self.bike = bike

        self.target_speed = 0
        self.target_rpm = 1200

        self.setWindowTitle("OpenDash")
        self.resize(800, 480)
        self.setMinimumSize(800, 480)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #020403;
            }

            QWidget {
                background-color: transparent;
            }

            QLabel {
                background-color: transparent;
                color: #F4F7F7;
            }
            """
        )

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)

        self.loading_page = (
            self.create_loading_page()
        )

        self.opendash_page = (
            self.create_opendash_page()
        )

        self.kawasaki_page = (
            self.create_kawasaki_page()
        )

        self.dashboard_page = (
            EnduroDashboardWidget()
        )

        self.pages.addWidget(
            self.loading_page
        )

        self.pages.addWidget(
            self.opendash_page
        )

        self.pages.addWidget(
            self.kawasaki_page
        )

        self.pages.addWidget(
            self.dashboard_page
        )

        self.pages.setCurrentWidget(
            self.loading_page
        )

        self.animation_timer = QTimer(self)

        self.animation_timer.timeout.connect(
            self.animate_dashboard
        )

        self.simulation_timer = QTimer(self)

        self.simulation_timer.timeout.connect(
            self.update_simulation_targets
        )

        self.start_boot_sequence()

    def create_loading_page(
        self,
    ) -> QWidget:
        page = QWidget()

        page.setStyleSheet(
            """
            QWidget {
                background-color: #020403;
            }
            """
        )

        title = QLabel("SYSTEM START")

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        title.setStyleSheet(
            """
            font-size: 15px;
            font-weight: bold;
            font-style: italic;
            letter-spacing: 5px;
            color: #AAB4B8;
            """
        )

        self.loading_bar = SlantedLoadingBar()

        self.loading_percent = QLabel("0%")

        self.loading_percent.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.loading_percent.setStyleSheet(
            """
            font-size: 13px;
            font-weight: bold;
            font-style: italic;
            letter-spacing: 2px;
            color: #748188;
            """
        )

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            60,
            60,
            60,
            60,
        )

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(18)

        layout.addWidget(
            self.loading_bar,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        layout.addSpacing(10)
        layout.addWidget(self.loading_percent)
        layout.addStretch()

        return page

    def create_opendash_page(
        self,
    ) -> QWidget:
        page = QWidget()

        page.setStyleSheet(
            """
            QWidget {
                background-color: #020403;
            }
            """
        )

        self.opendash_logo = SparkleLogo(
            "OpenDash"
        )

        subtitle = QLabel(
            "MOTORCYCLE DISPLAY SYSTEM"
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        subtitle.setStyleSheet(
            """
            font-size: 13px;
            font-style: italic;
            letter-spacing: 5px;
            color: #68757B;
            """
        )

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            40,
            40,
            40,
            40,
        )

        layout.addStretch()

        layout.addWidget(
            self.opendash_logo,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        layout.addWidget(subtitle)
        layout.addStretch()

        return page

    def create_kawasaki_page(
        self,
    ) -> QWidget:
        page = QWidget()

        page.setStyleSheet(
            """
            QWidget {
                background-color: #020403;
            }
            """
        )

        logo = QLabel("Kawasaki")

        logo.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        logo.setStyleSheet(
            """
            font-family: Arial;
            font-size: 68px;
            font-weight: bold;
            font-style: italic;
            color: #F5F5F5;
            """
        )

        subtitle = QLabel(
            "LET THE GOOD TIMES ROLL"
        )

        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        subtitle.setStyleSheet(
            """
            font-size: 13px;
            font-weight: bold;
            font-style: italic;
            letter-spacing: 4px;
            color: #39E86F;
            """
        )

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            40,
            40,
            40,
            40,
        )

        layout.addStretch()
        layout.addWidget(logo)
        layout.addSpacing(8)
        layout.addWidget(subtitle)
        layout.addStretch()

        return page

    def start_boot_sequence(
        self,
    ) -> None:
        self.loading_animation = QPropertyAnimation(
            self.loading_bar,
            b"progress",
            self,
        )

        self.loading_animation.setDuration(2400)
        self.loading_animation.setStartValue(0.0)
        self.loading_animation.setEndValue(100.0)

        self.loading_animation.setEasingCurve(
            QEasingCurve.Type.InOutCubic
        )

        self.loading_animation.valueChanged.connect(
            self.update_loading_percent
        )

        self.loading_animation.finished.connect(
            self.show_opendash_logo
        )

        self.loading_animation.start()

    def update_loading_percent(
        self,
        value,
    ) -> None:
        self.loading_percent.setText(
            f"{int(float(value))}%"
        )

    def show_opendash_logo(
        self,
    ) -> None:
        self.pages.setCurrentWidget(
            self.opendash_page
        )

        self.opendash_opacity = (
            QGraphicsOpacityEffect(
                self.opendash_page
            )
        )

        self.opendash_page.setGraphicsEffect(
            self.opendash_opacity
        )

        self.opendash_opacity.setOpacity(0.0)

        self.opendash_fade = QPropertyAnimation(
            self.opendash_opacity,
            b"opacity",
            self,
        )

        self.opendash_fade.setDuration(700)
        self.opendash_fade.setStartValue(0.0)
        self.opendash_fade.setEndValue(1.0)

        self.opendash_fade.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self.sparkle_animation = (
            QPropertyAnimation(
                self.opendash_logo,
                b"sparkle_position",
                self,
            )
        )

        self.sparkle_animation.setDuration(1000)
        self.sparkle_animation.setStartValue(0.16)
        self.sparkle_animation.setEndValue(0.84)

        self.sparkle_animation.setEasingCurve(
            QEasingCurve.Type.InOutQuad
        )

        self.opendash_fade.start()
        self.sparkle_animation.start()

        QTimer.singleShot(
            1600,
            self.fade_out_opendash,
        )

    def fade_out_opendash(
        self,
    ) -> None:
        self.opendash_fade_out = (
            QPropertyAnimation(
                self.opendash_opacity,
                b"opacity",
                self,
            )
        )

        self.opendash_fade_out.setDuration(500)
        self.opendash_fade_out.setStartValue(1.0)
        self.opendash_fade_out.setEndValue(0.0)

        self.opendash_fade_out.setEasingCurve(
            QEasingCurve.Type.InCubic
        )

        self.opendash_fade_out.finished.connect(
            self.show_kawasaki_logo
        )

        self.opendash_fade_out.start()

    def show_kawasaki_logo(
        self,
    ) -> None:
        self.pages.setCurrentWidget(
            self.kawasaki_page
        )

        self.kawasaki_opacity = (
            QGraphicsOpacityEffect(
                self.kawasaki_page
            )
        )

        self.kawasaki_page.setGraphicsEffect(
            self.kawasaki_opacity
        )

        self.kawasaki_opacity.setOpacity(1.0)

        QTimer.singleShot(
            1500,
            self.fade_out_kawasaki,
        )

    def fade_out_kawasaki(
        self,
    ) -> None:
        self.kawasaki_fade_out = (
            QPropertyAnimation(
                self.kawasaki_opacity,
                b"opacity",
                self,
            )
        )

        self.kawasaki_fade_out.setDuration(400)
        self.kawasaki_fade_out.setStartValue(1.0)
        self.kawasaki_fade_out.setEndValue(0.0)

        self.kawasaki_fade_out.setEasingCurve(
            QEasingCurve.Type.InQuad
        )

        self.kawasaki_fade_out.finished.connect(
            self.show_dashboard
        )

        self.kawasaki_fade_out.start()

    def show_dashboard(
        self,
    ) -> None:
        self.pages.setCurrentWidget(
            self.dashboard_page
        )

        self.refresh_display()

        self.animation_timer.start(40)
        self.simulation_timer.start(1000)

    def update_simulation_targets(
        self,
    ) -> None:
        self.target_speed += random.randint(
            -15,
            25,
        )

        self.target_speed = max(
            0,
            min(186, self.target_speed),
        )

        self.bike.coolant += random.choice(
            [-1, 0, 0, 0, 1]
        )

        self.bike.coolant = max(
            160,
            min(220, self.bike.coolant),
        )

        self.bike.battery += random.choice(
            [-0.1, 0.0, 0.0, 0.1]
        )

        self.bike.battery = max(
            12.0,
            min(14.7, self.bike.battery),
        )

        self.calculate_target_rpm()

    def animate_dashboard(
        self,
    ) -> None:
        if self.bike.speed < self.target_speed:
            self.bike.speed += 1

        elif self.bike.speed > self.target_speed:
            self.bike.speed -= 1

        self.update_gear()
        self.calculate_target_rpm()

        rpm_step = 100

        if self.bike.rpm < self.target_rpm:
            self.bike.rpm = min(
                self.bike.rpm + rpm_step,
                self.target_rpm,
            )

        elif self.bike.rpm > self.target_rpm:
            self.bike.rpm = max(
                self.bike.rpm - rpm_step,
                self.target_rpm,
            )

        self.refresh_display()

    def update_gear(
        self,
    ) -> None:
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

    def calculate_target_rpm(
        self,
    ) -> None:
        if self.bike.gear == "N":
            self.target_rpm = 1200
            return

        gear_number = int(
            self.bike.gear
        )

        gear_multiplier = {
            1: 310,
            2: 205,
            3: 150,
            4: 115,
            5: 92,
            6: 78,
        }

        calculated_rpm = (
            self.bike.speed
            * gear_multiplier[gear_number]
        )

        calculated_rpm += random.randint(
            -100,
            100,
        )

        self.target_rpm = max(
            1200,
            min(11000, calculated_rpm),
        )

    def refresh_display(
        self,
    ) -> None:
        self.dashboard_page.set_data(
            speed=self.bike.speed,
            rpm=self.bike.rpm,
            gear=self.bike.gear,
            fuel=self.bike.fuel,
            coolant=self.bike.coolant,
            battery=self.bike.battery,
            ktrc=self.bike.ktrc,
            power_mode=self.bike.power_mode,
        )