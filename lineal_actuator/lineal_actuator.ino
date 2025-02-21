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
  
  // Inicializar el pin del relé para la bomba de vacío
  pinMode(RELAY_PUMP_PIN, OUTPUT);
  // Asumimos que el relé es activo por nivel bajo: HIGH => bomba apagada
  digitalWrite(RELAY_PUMP_PIN, HIGH);
  
  // Inicializar módulos
  motor.initialize();
  sensor.initialize();
  logic.initialize();
}

void loop() {
  logic.handleSerialCommands();
  logic.update();
}
