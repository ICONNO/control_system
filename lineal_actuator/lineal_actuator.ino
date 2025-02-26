#include <Arduino.h>
#include "Config.h"
#include "Motor.h"
#include "Sensor.h"
#include "Logic.h"

// Instanciación de módulos
Motor motor(MOTOR_PUL_PIN, MOTOR_DIR_PIN);
Sensor sensor(SENSOR_TRIG_PIN, SENSOR_ECHO_PIN);
Logic logic(motor, sensor);

void setup() {
  Serial.begin(9600);
  LOG_INFO("Sistema de control de cabezal iniciado.");
  
  // Configurar el relé para la bomba: Bomba apagada por defecto (según la lógica de tu sistema)
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
