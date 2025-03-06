#include <Arduino.h>
#include "Config.h"
#include "Motor.h"
#include "Sensor.h"
#include "Logic.h"

Motor motor(MOTOR_STEP_PIN, MOTOR_DIR_PIN);
Sensor sensor(SENSOR_TRIG_PIN, SENSOR_ECHO_PIN);
Logic logic(motor, sensor);

void setup() {
  Serial.begin(9600);
  LOG_INFO("Head control system started.");
  
  pinMode(RELAY_PUMP_PIN, OUTPUT);
  digitalWrite(RELAY_PUMP_PIN, LOW);
  
  motor.initialize();
  sensor.initialize();
  logic.initialize();
}

void loop() {
  logic.handleSerialCommands();
  logic.update();
}
