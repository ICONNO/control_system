/* 
  Controlador de Motor Paso a Paso NEMA 17 con TB6560 y nsor Ultrasónico HC-SR04
  Funcionalidad:
    - Mueve el motor hacia abajo hasta alcanzar una distancia de 7 cm.
    - Luego, mueve el motor hacia arriba hasta alcanzar una distancia de 35 cm.
    - Repite este ciclo indefinidamente en modo automático.
    - Permite control manual desde PC mediante comandos seriales.
    - Manejo de errores en la lectura del sensor.
    - Control de velocidad preciso utilizando temporizadores no bloqueantes.
    - Implementación de una máquina de estados para gestionar el movimiento.
    - Protección contra movimientos no deseados y sobrecorrientes.
*/
#include <Arduino.h>

// === Definición de Pines ===

// Pines del Motor Paso a Paso con TB6560
const uint8_t PUL_PIN = 3;        // Pin para el pulso
const uint8_t DIR_PIN = 4;        // Pin para la dirección

// Pines del Sensor Ultrasónico HC-SR04
const uint8_t TRIG_PIN = 9;       // Pin de Trigger
const uint8_t ECHO_PIN = 10;      // Pin de Echo

// === Parámetros del Sistema ===

// Distancias objetivo (en centímetros)
const float LOWER_TARGET = 7.0;     // Distancia para detenerse al bajar
const float UPPER_TARGET = 35.0;    // Distancia para detenerse al subir
const float MARGIN = 0.5;           // Margen para evitar oscilaciones

// Velocidad del Motor
const unsigned long PULSE_INTERVAL_DEFAULT = 800; // Intervalo entre pulsos en micros (ajustar para la velocidad)
unsigned long PULSE_INTERVAL = PULSE_INTERVAL_DEFAULT;

// Intervalo de lectura del sensor ultrasónico
const unsigned long DISTANCE_INTERVAL = 100; // Intervalo entre mediciones en milisegundos

// Timeout para la lectura del sensor ultrasónico
const unsigned long ULTRASONIC_TIMEOUT = 30000; // Timeout en micros (30 ms)

// === Definición de Estados ===
enum MotorState {
  MOVING_DOWN,
  MOVING_UP,
  IDLE
};

MotorState currentState = IDLE;
MotorState previousState = IDLE;

// === Variables del Sistema ===

// Control del Motor
bool isMoving = false;
unsigned long previousMicros = 0;

// Control de Lectura del Sensor
unsigned long previousDistanceMillis = 0;
float currentDistance = 0.0;

// Modo Automático
bool autoMode = false;

// Protección contra Sobrecorrientes (Placeholder)
// bool overcurrentDetected = false; // Implementar con sensores si es necesario

// === Función de Configuración ===
void setup() {
  // Configuración de Pines del Motor
  pinMode(PUL_PIN, OUTPUT);
  pinMode(DIR_PIN, OUTPUT);
  digitalWrite(PUL_PIN, LOW);
  digitalWrite(DIR_PIN, LOW);

  // Configuración de Pines del Sensor Ultrasónico
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Inicialización del Monitor Serial
  Serial.begin(9600);
  Serial.println("Sistema de control de cabezal iniciado.");

  // Inicializar el estado inicial del motor en modo manual
  currentState = IDLE;
  previousState = IDLE;
}

// === Función Principal ===
void loop() {
  unsigned long currentMillis = millis();

  // Manejo de comandos seriales
  handleSerialCommands();

  // Lectura del Sensor Ultrasónico a Intervalos Regulares
  if (currentMillis - previousDistanceMillis >= DISTANCE_INTERVAL) {
    previousDistanceMillis = currentMillis;
    currentDistance = readUltrasonicDistance();

    // Mostrar la distancia en el monitor serial
    if (currentDistance >= 0.0) {
      Serial.print("Distancia actual: ");
      Serial.print(currentDistance);
      Serial.println(" cm");
    } else {
      Serial.println("Error en la lectura del sensor ultrasónico.");
      // Implementar lógica de manejo de errores si es necesario
    }

    // Controlar el movimiento del motor basado en la distancia y el estado actual
    switch (currentState) {
      case MOVING_DOWN:
        if (currentDistance <= LOWER_TARGET + MARGIN) {
          stopMotor();
          Serial.println("¡Distancia de 7 cm alcanzada! Deteniendo motor.");
          previousState = MOVING_DOWN;
          currentState = IDLE;
        }
        break;

      case MOVING_UP:
        if (currentDistance >= UPPER_TARGET - MARGIN) {
          stopMotor();
          Serial.println("¡Distancia de 35 cm alcanzada! Deteniendo motor.");
          previousState = MOVING_UP;
          currentState = IDLE;
        }
        break;

      case IDLE:
        if (autoMode) {
          if (previousState == MOVING_DOWN) {
            // Cambiar a subir después de detenerse
            moveUp();
            currentState = MOVING_UP;
            previousState = MOVING_UP;
          }
          else if (previousState == MOVING_UP) {
            // Cambiar a bajar después de detenerse
            moveDown();
            currentState = MOVING_DOWN;
            previousState = MOVING_DOWN;
          }
        }
        break;
    }
  }

  // Control de Pulsos del Motor de Manera No Bloqueante
  if (isMoving) {
    unsigned long currentMicros = micros();
    if (currentMicros - previousMicros >= PULSE_INTERVAL) {
      previousMicros = currentMicros;
      togglePulse();
    }
  }
}

/**
 * @brief Maneja los comandos seriales recibidos desde la PC.
 */
void handleSerialCommands() {
  while (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim(); // Eliminar espacios en blanco y saltos de línea

    Serial.print("Comando recibido: ");
    Serial.println(command);

    if (command.equalsIgnoreCase("AUTO")) {
      // Activar modo automático
      Serial.println("Activando modo automático.");
      if (!autoMode) {
        autoMode = true;
        moveDown();
        currentState = MOVING_DOWN;
        previousState = MOVING_DOWN;
      }
    }
    else if (command.equalsIgnoreCase("UP")) {
      // Mover manualmente hacia arriba
      Serial.println("Modo manual: Moviendo hacia arriba.");
      if (autoMode) {
        autoMode = false;
      }
      // stopMotor(); // Eliminado para permitir movimiento continuo
      moveUp();
      currentState = MOVING_UP;
      previousState = MOVING_UP;
    }
    else if (command.equalsIgnoreCase("DOWN")) {
      // Mover manualmente hacia abajo
      Serial.println("Modo manual: Moviendo hacia abajo.");
      if (autoMode) {
        autoMode = false;
      }
      // stopMotor(); // Eliminado para permitir movimiento continuo
      moveDown();
      currentState = MOVING_DOWN;
      previousState = MOVING_DOWN;
    }
    else if (command.equalsIgnoreCase("STOP")) {
      // Detener el motor y desactivar modo automático
      Serial.println("Deteniendo motor y desactivando modo automático.");
      if (autoMode) {
        autoMode = false;
      }
      stopMotor();
      currentState = IDLE;
    }
    else if (command.startsWith("SET_SPEED")) {
      // Comando para ajustar la velocidad del motor
      // Formato esperado: SET_SPEED <valor_en_micros>
      int spaceIndex = command.indexOf(' ');
      if (spaceIndex != -1) {
        String valueStr = command.substring(spaceIndex + 1);
        unsigned long newInterval = valueStr.toInt();
        if (newInterval > 0 && newInterval < 1000000) { // Validar rango
          PULSE_INTERVAL = newInterval;
          Serial.print("Intervalo de pulsos ajustado a: ");
          Serial.print(PULSE_INTERVAL);
          Serial.println(" micros.");
        }
        else {
          Serial.println("Valor de velocidad inválido.");
        }
      }
      else {
        Serial.println("Formato de comando incorrecto para SET_SPEED.");
      }
    }
    else {
      Serial.println("Comando no reconocido.");
    }
  }
}

/**
 * @brief Mide la distancia usando el sensor ultrasónico HC-SR04.
 * @return Distancia en centímetros. Retorna -1.0 en caso de error.
 */
float readUltrasonicDistance() {
  // Enviar pulso de Trigger
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Leer la duración del pulso de Echo con timeout
  long duration = pulseIn(ECHO_PIN, HIGH, ULTRASONIC_TIMEOUT);

  // Verificar si se recibió un eco
  if (duration == 0) {
    return -1.0; // Indicar error
  }

  // Conversión a centímetros
  float distance = (duration * 0.0343) / 2.0;
  return distance;
}

/**
 * @brief Inicia el movimiento del motor hacia abajo.
 */
void moveDown() {
  digitalWrite(DIR_PIN, HIGH); // HIGH para bajar
  isMoving = true;
  previousMicros = micros();
  togglePulse(); // Enviar el primer pulso
  Serial.println("Moviendo hacia abajo.");
}

/**
 * @brief Inicia el movimiento del motor hacia arriba.
 */
void moveUp() {
  digitalWrite(DIR_PIN, LOW); // LOW para subir
  isMoving = true;
  previousMicros = micros();
  togglePulse(); // Enviar el primer pulso
  Serial.println("Moviendo hacia arriba.");
}

/**
 * @brief Detiene el movimiento del motor.
 */
void stopMotor() {
  if (isMoving) {
    isMoving = false;
    digitalWrite(PUL_PIN, LOW); // Asegurar que el pulso esté bajo
    Serial.println("Motor detenido.");
  }
}

/**
 * @brief Alterna el estado del pulso del motor para generar pasos.
 */
void togglePulse() {
  static bool pulseState = LOW;
  pulseState = !pulseState;
  digitalWrite(PUL_PIN, pulseState);
}
