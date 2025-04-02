#include <Arduino.h>
#include "Config.h"
#include "Motor.h"
#include "Sensor.h"
#include "Logic.h"

/**
 * @file lineal_actuator.ino
 * @brief Main firmware entry point for the linear actuator control system.
 *
 * This sketch initializes the hardware components (motor, sensor) and the system logic.
 * It continuously processes serial commands and updates the system state.
 */

Motor motor(MOTOR_STEP_PIN, MOTOR_DIR_PIN);     ///< Instantiate the motor control object.
Sensor sensor(SENSOR_TRIG_PIN, SENSOR_ECHO_PIN);   ///< Instantiate the sensor object.
Logic logic(motor, sensor);                        ///< Instantiate the logic controller.

void setup() {
  Serial.begin(9600);
  LOG_INFO("Head control system started.");

  // Initialize vacuum pump control pin.
  pinMode(RELAY_PUMP_PIN, OUTPUT);
  digitalWrite(RELAY_PUMP_PIN, LOW);

  // Initialize hardware components.
  motor.initialize();
  sensor.initialize();
  logic.initialize();
}

void loop() {
  // Process any available serial commands.
  logic.handleSerialCommands();
  // Update system state based on sensor readings and control logic.
  logic.update();
}
