#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

// === Definición de Pines ===
const uint8_t MOTOR_PUL_PIN = 3;        // Pin de STEP (para el motor)
const uint8_t MOTOR_DIR_PIN = 4;        // Pin de DIR (para el motor)
const uint8_t SENSOR_TRIG_PIN = 9;      // Pin de Trigger del sensor ultrasónico
const uint8_t SENSOR_ECHO_PIN = 10;     // Pin de Echo del sensor ultrasónico
// No se usa ENABLE_PIN
// Pin para el relé que controla la bomba de vacío
const uint8_t RELAY_PUMP_PIN = 12;

// === Parámetros del Sistema ===
// Distancias objetivo (en centímetros)
const float DISTANCE_LOWER_TARGET = 7.0;     
const float DISTANCE_UPPER_TARGET = 35.0;    
const float DISTANCE_MARGIN = 0.5;           

// Parámetros para aceleración del motor (usados con AccelStepper)
// Aumentamos la aceleración para una rampa más corta
const float MOTOR_ACCELERATION = 2000.0;   // pasos/s² (ajusta según tu hardware)
const float MOTOR_MAX_SPEED = 1000.0;       // pasos/s (ajusta según tu sistema)

// Intervalo de lectura del sensor ultrasónico (ms)
const unsigned long SENSOR_READ_INTERVAL_MS = 100;

// Timeout para la lectura del sensor ultrasónico (us)
const unsigned long ULTRASONIC_TIMEOUT_US = 30000;

// === Definición de Estados ===
enum class MotorState {
  MOVING_DOWN,
  MOVING_UP,
  IDLE
};

// === Configuración de Logging ===
#define LOG_VERBOSITY 2 // 0: Off, 1: Error, 2: Info, 3: Debug

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

#endif // CONFIG_H
