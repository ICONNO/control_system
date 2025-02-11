// lineal_actuator.ino

#include <Arduino.h>
#include "Config.h"
#include "Motor.h"
#include "Sensor.h"
#include "Logic.h"

// Instanciación de módulos
Motor motor(MOTOR_PUL_PIN, MOTOR_DIR_PIN);
Sensor sensor(SENSOR_TRIG_PIN, SENSOR_ECHO_PIN);
Logic logic(motor, sensor);

// === Función de Configuración ===
void setup() {
  // Inicializar Monitor Serial
  Serial.begin(9600);
  LOG_INFO("Sistema de control de cabezal iniciado.");


  pinMode(ENABLE_PIN, OUTPUT);      // Configurar pin 5 como salida
  digitalWrite(ENABLE_PIN, HIGH);   // Ponerlo en alto para habilitar el driver

  // Inicializar módulos
  motor.initialize();
  sensor.initialize();
  logic.initialize();
}

// === Función Principal ===
void loop() {
  // Manejo de comandos seriales
  logic.handleSerialCommands();

  // Actualizar lógica del sistema
  logic.update();
}
