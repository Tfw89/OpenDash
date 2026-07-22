#include <Arduino.h>
#include <Wire.h>
#include <MPU6050.h>
#include <FastLED.h>
#include <math.h>

// -----------------------------------------------------------------------------
// OpenDash — Phase 1 bench prototype
//
// Hardware:
//   ESP32 WROOM-32 DevKit
//   MPU-6050 GY-521:
//     SDA = GPIO21
//     SCL = GPIO22
//   WS2812B-compatible FCOB strip:
//     DATA = GPIO13 through a 74AHCT125 level shifter
//
// Sensor-axis assumption:
//   MPU6050 X axis = motorcycle forward direction
//   MPU6050 Y axis = motorcycle left/right direction
//   MPU6050 Z axis = motorcycle vertical direction
//
// With that mounting orientation:
//   Gyroscope X = roll rate
//   atan2(accel Y, accel Z) = accelerometer roll angle
//
// If your sensor is mounted differently, change ROLL_GYRO_AXIS and the
// accelerometer roll calculation in readSensor().
// -----------------------------------------------------------------------------

// User-requested tuning constants.
constexpr int LED_COUNT = 30;                  // Placeholder; set from dash-arc measurement later
constexpr int LED_PIN = 13;
constexpr float ALPHA = 0.98f;                 // Gyro weight when stable
constexpr float MAX_LEAN_DEG = 55.0f;          // Lean-angle clamp
constexpr float STABLE_RATE_DPS = 5.0f;        // Gyro below this = candidate stable
constexpr float G_TOLERANCE = 0.15f;           // Accel magnitude must be within this of 1g
constexpr float LOWPASS_ALPHA = 0.20f;         // Output smoothing
constexpr uint8_t MAX_BRIGHTNESS = 100;        // Caps current draw

// ESP32 I2C pins.
constexpr int I2C_SDA_PIN = 21;
constexpr int I2C_SCL_PIN = 22;

// ElectronicCats MPU6050 initialize() defaults to:
//   Accelerometer: +/-2g
//   Gyroscope:     +/-250 degrees/second
//
// The raw conversion factors for those ranges are:
constexpr float ACCEL_LSB_PER_G = 16384.0f;
constexpr float GYRO_LSB_PER_DPS = 131.0f;

// Boot calibration settings.
constexpr uint16_t CALIBRATION_SAMPLES = 1000;
constexpr uint16_t CALIBRATION_DELAY_MS = 2;

// Serial output rate.
constexpr uint32_t SERIAL_INTERVAL_MS = 100;

// Reject unusually large loop intervals so a pause, USB event, or debugger
// interruption cannot create a huge false gyro integration step.
constexpr float MAX_VALID_DT_SECONDS = 0.100f;

// Dim Kawasaki-green base color.
//
// MAX_BRIGHTNESS provides the global current cap. These RGB values keep the
// always-on base substantially dimmer than future comet effects.
constexpr uint8_t BASE_GREEN_R = 2;
constexpr uint8_t BASE_GREEN_G = 24;
constexpr uint8_t BASE_GREEN_B = 0;

CRGB leds[LED_COUNT];
MPU6050 mpu;

// Raw sensor storage required by MPU6050::getMotion6().
int16_t rawAccelX = 0;
int16_t rawAccelY = 0;
int16_t rawAccelZ = 0;
int16_t rawGyroX = 0;
int16_t rawGyroY = 0;
int16_t rawGyroZ = 0;

// Calibration results.
float gyroRollBiasDps = 0.0f;
float uprightAccelRollDeg = 0.0f;

// Estimator state.
float gyroLeanDeg = 0.0f;
float filteredLeanDeg = 0.0f;

uint32_t previousLoopMicros = 0;
uint32_t previousSerialMillis = 0;

struct SensorReading
{
    float accelXG;
    float accelYG;
    float accelZG;

    float gyroRollRateDps;
    float accelRollDeg;
    float accelMagnitudeG;
};

float clampFloat(float value, float minimum, float maximum)
{
    if (value < minimum)
    {
        return minimum;
    }

    if (value > maximum)
    {
        return maximum;
    }

    return value;
}

float radiansToDegrees(float radians)
{
    return radians * (180.0f / PI);
}

void showDimGreenBase()
{
    fill_solid(
        leds,
        LED_COUNT,
        CRGB(BASE_GREEN_R, BASE_GREEN_G, BASE_GREEN_B));

    FastLED.show();
}

SensorReading readSensor()
{
    mpu.getMotion6(
        &rawAccelX,
        &rawAccelY,
        &rawAccelZ,
        &rawGyroX,
        &rawGyroY,
        &rawGyroZ);

    SensorReading reading{};

    reading.accelXG =
        static_cast<float>(rawAccelX) / ACCEL_LSB_PER_G;

    reading.accelYG =
        static_cast<float>(rawAccelY) / ACCEL_LSB_PER_G;

    reading.accelZG =
        static_cast<float>(rawAccelZ) / ACCEL_LSB_PER_G;

    // The X gyro is used as roll rate because this code assumes the sensor's
    // X axis points forward along the motorcycle.
    reading.gyroRollRateDps =
        static_cast<float>(rawGyroX) / GYRO_LSB_PER_DPS;

    reading.accelMagnitudeG = sqrtf(
        reading.accelXG * reading.accelXG +
        reading.accelYG * reading.accelYG +
        reading.accelZG * reading.accelZG);

    // This assumes:
    //   X = forward
    //   Y = left/right
    //   Z = vertical
    reading.accelRollDeg =
        radiansToDegrees(atan2f(reading.accelYG, reading.accelZG));

    return reading;
}

void haltWithLedError()
{
    Serial.println();
    Serial.println("FATAL: MPU-6050 connection failed.");
    Serial.println("Check:");
    Serial.println("  GY-521 VCC -> ESP32 3.3V");
    Serial.println("  GY-521 GND -> ESP32 GND");
    Serial.println("  GY-521 SDA -> GPIO21");
    Serial.println("  GY-521 SCL -> GPIO22");
    Serial.println("  GY-521 AD0 -> GND or left low");
    Serial.println();

    fill_solid(leds, LED_COUNT, CRGB(24, 0, 0));
    FastLED.show();

    while (true)
    {
        delay(1000);
    }
}

void calibrateUprightPosition()
{
    Serial.println();
    Serial.println("Starting upright calibration.");
    Serial.println("Keep the MPU-6050 completely still and upright...");

    double gyroBiasAccumulator = 0.0;
    double accelRollAccumulator = 0.0;

    // Allow the sensor to settle after initialization.
    delay(500);

    for (uint16_t sample = 0; sample < CALIBRATION_SAMPLES; ++sample)
    {
        SensorReading reading = readSensor();

        gyroBiasAccumulator += reading.gyroRollRateDps;
        accelRollAccumulator += reading.accelRollDeg;

        if ((sample + 1) % 100 == 0)
        {
            Serial.print(".");
        }

        delay(CALIBRATION_DELAY_MS);
    }

    gyroRollBiasDps =
        static_cast<float>(
            gyroBiasAccumulator / CALIBRATION_SAMPLES);

    uprightAccelRollDeg =
        static_cast<float>(
            accelRollAccumulator / CALIBRATION_SAMPLES);

    gyroLeanDeg = 0.0f;
    filteredLeanDeg = 0.0f;

    Serial.println();
    Serial.println("Calibration complete.");

    Serial.print("Gyro roll bias: ");
    Serial.print(gyroRollBiasDps, 4);
    Serial.println(" deg/s");

    Serial.print("Upright accel roll: ");
    Serial.print(uprightAccelRollDeg, 3);
    Serial.println(" deg");

    Serial.println();
}

void setup()
{
    Serial.begin(115200);
    delay(500);

    Serial.println();
    Serial.println("========================================");
    Serial.println(" OpenDash");
    Serial.println(" Phase 1: IMU estimator + green LED base");
    Serial.println("========================================");

    FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, LED_COUNT);
    FastLED.setBrightness(MAX_BRIGHTNESS);
    FastLED.setCorrection(TypicalLEDStrip);
    FastLED.clear(true);

    showDimGreenBase();

    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
    Wire.setClock(400000);

    mpu.initialize();

    if (!mpu.testConnection())
    {
        haltWithLedError();
    }

    Serial.println("MPU-6050 connection successful.");

    calibrateUprightPosition();

    previousLoopMicros = micros();
    previousSerialMillis = millis();

    Serial.println("Estimator running.");
    Serial.println("lean_deg,gyro_rate_dps,accel_roll_deg,accel_mag_g,stable");
}

void loop()
{
    const uint32_t currentMicros = micros();
    float deltaTimeSeconds =
        static_cast<float>(currentMicros - previousLoopMicros) /
        1000000.0f;

    previousLoopMicros = currentMicros;

    // Skip an invalid integration interval. This protects the estimate after
    // startup delays, debugger pauses, or other unusually long interruptions.
    if (deltaTimeSeconds <= 0.0f ||
        deltaTimeSeconds > MAX_VALID_DT_SECONDS)
    {
        deltaTimeSeconds = 0.0f;
    }

    const SensorReading reading = readSensor();

    // Remove the resting gyro offset measured during boot calibration.
    const float correctedRollRateDps =
        reading.gyroRollRateDps - gyroRollBiasDps;

    // Convert the accelerometer roll angle to a zero-centered value using the
    // upright position measured during startup.
    float accelLeanDeg =
        reading.accelRollDeg - uprightAccelRollDeg;

    accelLeanDeg = clampFloat(
        accelLeanDeg,
        -MAX_LEAN_DEG,
        MAX_LEAN_DEG);

    // The gyroscope is the primary lean source. It responds quickly and is not
    // incorrectly pulled toward upright by lateral cornering acceleration.
    gyroLeanDeg += correctedRollRateDps * deltaTimeSeconds;

    gyroLeanDeg = clampFloat(
        gyroLeanDeg,
        -MAX_LEAN_DEG,
        MAX_LEAN_DEG);

    const bool rollRateIsStable =
        fabsf(correctedRollRateDps) < STABLE_RATE_DPS;

    const bool gravityMagnitudeIsStable =
        fabsf(reading.accelMagnitudeG - 1.0f) < G_TOLERANCE;

    // Phase 1 placeholder. This must eventually be replaced by a real turning
    // or lateral-acceleration confidence signal.
    //
    // The complete stability gate is retained now so the estimator structure
    // does not need to change later.
    const bool lowTurningSignal = true;

    const bool bikeIsStable =
        rollRateIsStable &&
        gravityMagnitudeIsStable &&
        lowTurningSignal;

    // IMPORTANT:
    // Accelerometer correction is allowed only while stable.
    //
    // During a steady motorcycle corner, gravity and cornering acceleration
    // combine along the motorcycle's apparent vertical axis. An accelerometer
    // can therefore appear close to upright even while the motorcycle is
    // leaned. Continuously correcting the gyro with that reading would pull
    // the displayed lean angle back toward zero in the middle of a corner.
    if (bikeIsStable)
    {
        gyroLeanDeg =
            ALPHA * gyroLeanDeg +
            (1.0f - ALPHA) * accelLeanDeg;
    }

    // When the stability conditions are false, gyroLeanDeg remains gyro-only.
    // No accelerometer correction is applied.

    gyroLeanDeg = clampFloat(
        gyroLeanDeg,
        -MAX_LEAN_DEG,
        MAX_LEAN_DEG);

    // Low-pass the displayed output to reduce vibration-induced jitter.
    filteredLeanDeg +=
        LOWPASS_ALPHA * (gyroLeanDeg - filteredLeanDeg);

    filteredLeanDeg = clampFloat(
        filteredLeanDeg,
        -MAX_LEAN_DEG,
        MAX_LEAN_DEG);

    // Keep the entire strip visibly on with a dim Kawasaki-green base.
    // It is rewritten periodically here so later code cannot accidentally
    // leave stale LED data in the buffer.
    showDimGreenBase();

    const uint32_t currentMillis = millis();

    if (currentMillis - previousSerialMillis >= SERIAL_INTERVAL_MS)
    {
        previousSerialMillis = currentMillis;

        Serial.print(filteredLeanDeg, 2);
        Serial.print(",");
        Serial.print(correctedRollRateDps, 2);
        Serial.print(",");
        Serial.print(accelLeanDeg, 2);
        Serial.print(",");
        Serial.print(reading.accelMagnitudeG, 3);
        Serial.print(",");
        Serial.println(bikeIsStable ? 1 : 0);
    }

    delay(2);
}