#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// Pin definitions
const uint8_t MOTOR_STEP_PIN     = 3;    // STEP pin for the motor
const uint8_t MOTOR_DIR_PIN      = 4;    // DIR pin for the motor
const uint8_t SENSOR_TRIG_PIN    = 9;    // Trigger pin for the ultrasonic sensor
const uint8_t SENSOR_ECHO_PIN    = 10;   // Echo pin for the ultrasonic sensor
const uint8_t RELAY_PUMP_PIN     = 12;   // Relay pin for the vacuum pump (active-high)

// System parameters (units in cm, steps, etc.)
const float DIST_LOWER_TARGET    = 7.0;  // Lower distance target
const float DIST_UPPER_TARGET    = 30.0; // Upper distance target
const float DIST_MARGIN          = 0.1;  // Margin for distance measurement

// Motor parameters (for AccelStepper)
const float MOTOR_ACCELERATION   = 2000.0;  // Acceleration in steps/s^2
const float MOTOR_MAX_SPEED      = 1000.0;  // Maximum speed in steps/s

// Sensor parameters
const unsigned long SENSOR_READ_INTERVAL_MS = 100;      // Sensor read interval (ms)
const unsigned long ULTRASONIC_TIMEOUT_US     = 30000;    // Sensor timeout (us)

// Motor state enumeration
enum class MotorState {
  MOVING_DOWN,
  MOVING_UP,
  IDLE
};

// Logging configuration
#define LOG_VERBOSITY 2  // 0: Off, 1: Error, 2: Info, 3: Debug

#if LOG_VERBOSITY >= 1
  #define LOG_ERROR(msg) Serial.println(F(msg))
#else
  #define LOG_ERROR(msg)
#endif

#if LOG_VERBOSITY >= 2
  #define LOG_INFO(msg) Serial.println(F(msg))
#else
  #define LOG_INFO(msg)
#endif

#if LOG_VERBOSITY >= 3
  #define LOG_DEBUG(msg) Serial.println(F(msg))
#else
  #define LOG_DEBUG(msg)
#endif

#endif  // CONFIG_H
