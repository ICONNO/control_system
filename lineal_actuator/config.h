#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

/**
 * @file config.h
 * @brief Defines hardware pin assignments, system parameters, motor parameters, sensor parameters, and logging configuration.
 *
 * This file contains the definitions of all constants and parameters used throughout
 * the firmware for controlling the linear actuator system.
 */

// Pin definitions
const uint8_t MOTOR_STEP_PIN     = 3;    ///< STEP pin for the motor driver.
const uint8_t MOTOR_DIR_PIN      = 4;    ///< DIR pin for the motor driver.
const uint8_t SENSOR_TRIG_PIN    = 9;    ///< Trigger pin for the ultrasonic sensor.
const uint8_t SENSOR_ECHO_PIN    = 10;   ///< Echo pin for the ultrasonic sensor.
const uint8_t RELAY_PUMP_PIN     = 12;   ///< Relay pin for the vacuum pump (active-high).

// System parameters (units in cm, steps, etc.)
const float DIST_LOWER_TARGET    = 10.0;  ///< Lower distance target (in cm).
const float DIST_UPPER_TARGET    = 20.0;  ///< Upper distance target (in cm).
const float DIST_MARGIN          = 0.1;   ///< Acceptable margin for distance measurement (in cm).

// Motor parameters (for AccelStepper)
const float MOTOR_ACCELERATION   = 2000.0;  ///< Motor acceleration (in steps/s²).
const float MOTOR_MAX_SPEED      = 1000.0;  ///< Maximum motor speed (in steps/s).

// Sensor parameters
const unsigned long SENSOR_READ_INTERVAL_MS = 100;      ///< Interval between sensor readings (in ms).
const unsigned long ULTRASONIC_TIMEOUT_US     = 30000;    ///< Timeout for ultrasonic sensor response (in µs).

// Motor state enumeration
/**
 * @enum MotorState
 * @brief Enumerates the possible states of the motor.
 */
enum class MotorState {
  MOVING_DOWN,  ///< The motor is moving downward.
  MOVING_UP,    ///< The motor is moving upward.
  IDLE          ///< The motor is idle.
};

// Logging configuration
#define LOG_VERBOSITY 2  ///< Logging level: 0-Off, 1-Error, 2-Info, 3-Debug.

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
