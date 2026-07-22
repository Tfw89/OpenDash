# OpenDash

**An ESP32-based open-source motorcycle instrumentation platform.**
The first module is a curved, real-time lean-angle indicator using an onboard
IMU and an addressable FCOB LED strip — a "comet" of light that sweeps across
the dash arc as the bike leans, over a dim Kawasaki-green base.

Built for a 2016 Kawasaki ZX-14R, but the approach is bike-agnostic. Fully
independent of the motorcycle's ECU and CAN bus — it reads its own sensor and
drives its own display, so there's nothing to reverse-engineer and no risk to
the bike's electronics.

---

## Status

**Phase 1 — bench prototype.** Getting the IMU read and the strip lit on the
bench, USB-powered. No vehicle integration yet.

---

## How it works

A 6-axis IMU (accelerometer + gyroscope) measures the bike's motion. Firmware
on an ESP32 runs a lean-angle estimator, then maps the estimated angle to a
position along an addressable LED strip:

- The whole strip glows a dim **Kawasaki green** so the arc always reads as "on."
- A brighter **comet** rides on top, moving toward the direction of lean.
- Comet color sweeps **green → yellow → red** as lean increases.
- A faint **peak marker** lingers briefly so you can check your max lean *after*
  the corner, not during it.

### The estimator (the important part)

A motorcycle in a steady corner leans so that gravity plus cornering force align
with the bike's vertical axis. This means a plain accelerometer reads
near-upright *mid-corner* and will lie about your lean angle if trusted during
cornering.

OpenDash uses a **conditional complementary filter**:

- Gyroscope integration provides the live lean angle (trusted while cornering).
- Accelerometer correction is applied **only when the bike is stable** — low
  roll rate, accelerometer magnitude near 1g, and low turning signal — so the
  correction never fires mid-corner.

Phase 1 is a convincing *approximate* indicator. A later phase adds speed/GPS
aiding to make it precise.

---

## Hardware (Phase 1 bench)

| Part | Detail |
|------|--------|
| MCU | ESP32 WROOM-32 DevKit |
| IMU | MPU-6050 (GY-521 board), I²C |
| Display | BTF-LIGHTING FCOB WS2812B, 5V, 160 LED/m, addressable |
| Level shifter | 74AHCT125 (3.3V → 5V data) |
| Bench power | MP1584 buck converter (5V out) |
| Passives | 1000µF cap across strip 5V/GND, 330–470Ω on data line |

### Wiring (bench)

- MP1584 → clean 5V. Feeds both the ESP32 and the LED strip directly.
- LED strip 5V comes from the buck, **not** through the ESP32.
- ESP32 GPIO13 → 74AHCT125 → strip DATA (through 330–470Ω resistor).
- 1000µF cap across the strip's 5V and GND, near the first LED.
- MPU-6050 on I²C: SDA=GPIO21, SCL=GPIO22, powered from ESP32 3.3V.

---

## Roadmap

- **Phase 1** — Bench prototype: IMU read, green base, comet animation, on USB.
- **Phase 2** — Calibration (startup zero to NVS), smoothing, peak-hold, tuning.
- **Phase 3** — On-bike: protected 12V→5V supply, weatherproofing, mounting.
- **Phase 4** — Optional: GPS/speed-aided estimator, ride logging, Bluetooth config.

---

## Config

Tunable constants live at the top of the firmware:

```cpp
constexpr int   LED_COUNT      = 0;      // set from dash-arc measurement (arc_mm / 6.25)
constexpr float MAX_LEAN_DEG   = 55.0f;  // lean at full-red, comet at strip end
constexpr float YELLOW_ANGLE   = 25.0f;
constexpr float RED_ANGLE      = 40.0f;
constexpr int   COMET_LENGTH   = 6;
constexpr uint8_t MAX_BRIGHTNESS = 100;  // caps current draw
```

At 160 LED/m the strip has one addressable pixel every 6.25 mm.
`LED_COUNT` = (dash-arc length in mm) ÷ 6.25.

---

## License

MIT (see LICENSE).

---

*OpenDash is a personal build project. It is not affiliated with Kawasaki.*