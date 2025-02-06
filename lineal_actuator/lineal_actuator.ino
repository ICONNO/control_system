#include <Arduino.h>
#include "Config.h"
#include "Motor.h"
#include "Sensor.h"
#include "Logic.h"

// Instanciación de módulos
Motor motor(MOTOR_PUL_PIN, MOTOR_DIR_PIN);
Sensor sensor(SENSOR_TRIG_PIN, SENSOR_ECHO_PIN);
Logic logic(motor, sensor);

unsigned long lastSensorUpdate = 0;

void setup() {
  Serial.begin(1);
  LOG_INFO("Sistema de control de cabezal iniciado.");
  motor.initialize();
  sensor.initialize();
  logic.initialize();
}

void loop() {
  // Procesar comandos seriales (no bloqueante)
  logic.handleSerialCommands();

  // Actualizar el motor lo más rápido posible
  logic.update();

  // Leer el sensor y procesar la lógica a intervalos definidos (por ejemplo, cada 100 ms)
  if (millis() - lastSensorUpdate >= SENSOR_READ_INTERVAL_MS) {
    lastSensorUpdate = millis();
    logic.updateSensor();
  }
}
