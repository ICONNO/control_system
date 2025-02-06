/*
  lineal_actuator.ino
  Firmware para un NEMA 17 en guía lineal controlado por un TB6560,
  utilizando un protocolo binario (2 bytes por comando) y comunicación a 115200 baudios.
  
  Protocolo:
    - Byte 1: Código de comando
    - Byte 2: Payload (por ejemplo, 0x00 para comandos UP/DOWN/STOP o el nuevo retardo para SET_SPEED)
  
  Comandos definidos:
    0xA0: CMD_AUTO      - Modo automático (baja hasta el límite medido)
    0xA1: CMD_UP        - Mueve el motor hacia arriba
    0xA2: CMD_DOWN      - Mueve el motor hacia abajo
    0xA3: CMD_STOP      - Detiene el motor
    0xA4: CMD_SET_SPEED - Ajusta la velocidad (payload = nuevo delay en µs)
  
  NOTA: Se utiliza delayMicroseconds() para generar los pulsos. Para evitar bloqueos,
        se recomienda en el futuro migrar a una máquina de estados o usar interrupciones.
*/

#include <Arduino.h>
#include "Config.h"

// Agregamos el pin de Sleep/Enable para el TB6560
#define SLEEP_PIN 8

// ==================== VARIABLES Y CONSTANTES ====================
const unsigned long BAUD_RATE = 115200;

// Estados del motor (para la lógica interna)
enum class MotorState {
  MOVING_DOWN,
  MOVING_UP,
  IDLE
};

// ==================== Protocolo Binario ====================
const uint8_t CMD_AUTO      = 0xA0;
const uint8_t CMD_UP        = 0xA1;
const uint8_t CMD_DOWN      = 0xA2;
const uint8_t CMD_STOP      = 0xA3;
const uint8_t CMD_SET_SPEED = 0xA4;

// ==================== CLASE MOTOR ====================
class Motor {
public:
  Motor(uint8_t pulPin, uint8_t dirPin)
    : pulPin_(pulPin), dirPin_(dirPin), isMoving_(false),
      pulseState_(LOW), previousMicros_(0),
      pulseInterval_(PULSE_INTERVAL_DEFAULT_US) {}

  void initialize() {
    pinMode(pulPin_, OUTPUT);
    pinMode(dirPin_, OUTPUT);
    digitalWrite(pulPin_, LOW);
    digitalWrite(dirPin_, LOW);
    LOG_INFO("Motor inicializado.");
  }

  void setDirection(uint8_t dir) {
    digitalWrite(dirPin_, dir);
  }

  void moveUp() {
    setDirection(LOW);  // LOW para subir (verifica si esto coincide con tu TB6560)
    isMoving_ = true;
    previousMicros_ = micros();
    togglePulse();  // Envía el primer pulso
    LOG_INFO("Moviendo hacia arriba.");
  }

  void moveDown() {
    setDirection(HIGH); // HIGH para bajar
    isMoving_ = true;
    previousMicros_ = micros();
    togglePulse();  // Envía el primer pulso
    LOG_INFO("Moviendo hacia abajo.");
  }

  void stop() {
    if (isMoving_) {
      isMoving_ = false;
      digitalWrite(pulPin_, LOW);
      LOG_INFO("Motor detenido.");
    }
  }

  void update() {
    if (isMoving_) {
      unsigned long currentMicros = micros();
      if (currentMicros - previousMicros_ >= pulseInterval_) {
        previousMicros_ = currentMicros;
        togglePulse();
      }
    }
  }

  void setPulseInterval(unsigned long interval) {
    pulseInterval_ = interval;
    LOG_INFO("Intervalo de pulsos ajustado.");
  }

  void step() {
    togglePulse();
  }

private:
  uint8_t pulPin_;
  uint8_t dirPin_;
  bool isMoving_;
  bool pulseState_;
  unsigned long previousMicros_;
  unsigned long pulseInterval_;

  void togglePulse() {
    pulseState_ = !pulseState_;
    digitalWrite(pulPin_, pulseState_);
  }
};

// ==================== CLASE SENSOR ====================
class Sensor {
public:
  Sensor(uint8_t trigPin, uint8_t echoPin)
    : trigPin_(trigPin), echoPin_(echoPin) {}

  void initialize() {
    pinMode(trigPin_, OUTPUT);
    pinMode(echoPin_, INPUT);
    LOG_INFO("Sensor ultrasónico inicializado.");
  }

  float readDistance() {
    digitalWrite(trigPin_, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin_, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin_, LOW);

    long duration = pulseIn(echoPin_, HIGH, ULTRASONIC_TIMEOUT_US);
    if (duration == 0) {
      LOG_ERROR("Timeout en sensor ultrasónico.");
      return -1.0;
    }
    float distance = (duration * 0.0343) / 2.0;
    return distance;
  }

private:
  uint8_t trigPin_;
  uint8_t echoPin_;
};

// ==================== CLASE LOGIC ====================
enum class SystemStatus {
    OK,
    ERROR,
    EMERGENCY_STOP,
    CALIBRATING,
    MAINTENANCE
};

class Logic {
public:
  Logic(Motor& motor, Sensor& sensor)
    : motor_(motor), sensor_(sensor),
      currentState_(MotorState::IDLE), previousState_(MotorState::IDLE),
      autoMode_(false), previousDistanceMillis_(0),
      currentDistance_(0.0) {}

  void initialize() {
    currentState_ = MotorState::IDLE;
    previousState_ = MotorState::IDLE;
    LOG_INFO("Lógica del sistema inicializada.");
  }

  // Actualiza el motor (se llama cada ciclo)
  void update() {
    motor_.update();
  }

  // Lee el sensor ultrasónico y procesa el estado
  void updateSensor() {
    currentDistance_ = sensor_.readDistance();
    if (currentDistance_ >= 0.0) {
      Serial.print("Distancia actual: ");
      Serial.print(currentDistance_);
      Serial.println(" cm");
    } else {
      Serial.println("Error en sensor ultrasónico.");
    }
    processState();
  }

  // Procesa los comandos recibidos (se esperan 2 bytes por comando)
  void handleSerialCommands() {
    while (Serial.available() >= 2) {
      uint8_t cmd = Serial.read();
      uint8_t payload = Serial.read();
      switch (cmd) {
        case CMD_AUTO:
          LOG_INFO("CMD_AUTO recibido.");
          setAutoMode(true);
          motor_.moveDown();
          currentState_ = MotorState::MOVING_DOWN;
          previousState_ = MotorState::MOVING_DOWN;
          break;
        case CMD_UP:
          LOG_INFO("CMD_UP recibido.");
          setAutoMode(false);
          motor_.moveUp();
          currentState_ = MotorState::MOVING_UP;
          previousState_ = MotorState::MOVING_UP;
          break;
        case CMD_DOWN:
          LOG_INFO("CMD_DOWN recibido.");
          setAutoMode(false);
          motor_.moveDown();
          currentState_ = MotorState::MOVING_DOWN;
          previousState_ = MotorState::MOVING_DOWN;
          break;
        case CMD_STOP:
          LOG_INFO("CMD_STOP recibido.");
          setAutoMode(false);
          motor_.stop();
          currentState_ = MotorState::IDLE;
          break;
        case CMD_SET_SPEED:
          LOG_INFO("CMD_SET_SPEED recibido.");
          if (payload > 0) {
            adjustSpeed(payload);
            Serial.print("Nuevo intervalo: ");
            Serial.print(pulseInterval);
            Serial.println(" µs");
          } else {
            LOG_ERROR("Payload inválido en SET_SPEED.");
          }
          break;
        default:
          LOG_ERROR("Comando desconocido.");
          break;
      }
    }
  }

  // En modo automático, detiene el motor cuando se alcanza el límite de distancia
  void processState() {
    if (autoMode_) {
      switch (currentState_) {
        case MotorState::MOVING_DOWN:
          if (currentDistance_ <= DISTANCE_LOWER_TARGET + DISTANCE_MARGIN) {
            motor_.stop();
            LOG_INFO("Límite inferior alcanzado en modo automático.");
            currentState_ = MotorState::IDLE;
          }
          break;
        case MotorState::MOVING_UP:
          if (currentDistance_ >= DISTANCE_UPPER_TARGET - DISTANCE_MARGIN) {
            motor_.stop();
            LOG_INFO("Límite superior alcanzado en modo automático.");
            currentState_ = MotorState::IDLE;
          }
          break;
        case MotorState::IDLE:
          break;
      }
    }
  }

  void setAutoMode(bool mode) { autoMode_ = mode; }
  void adjustSpeed(unsigned long newInterval) {
    pulseInterval = newInterval;
    motor_.setPulseInterval(newInterval);
  }
  
  // Funciones stub de seguridad y control
  void emergencyStop() { motor_.stop(); }
  void resetSystem() { }
  bool isSafe() const { return true; }
  SystemStatus getStatus() const { return SystemStatus::OK; }
  void calibrate() { }
  void setMaintenanceMode(bool enabled) { }
  float getSystemHealth() const { return 100.0; }

private:
  Motor& motor_;
  Sensor& sensor_;
  MotorState currentState_;
  MotorState previousState_;
  bool autoMode_;
  unsigned long previousDistanceMillis_;
  float currentDistance_;
};

// ==================== OBJETOS GLOBALES Y LOOP PRINCIPAL ====================

Motor motor(MOTOR_PUL_PIN, MOTOR_DIR_PIN);
Sensor sensor(SENSOR_TRIG_PIN, SENSOR_ECHO_PIN);
Logic logic(motor, sensor);

unsigned long lastSensorUpdate = 0;

void setup() {
  // Configuración del pin de Sleep para habilitar el TB6560
  pinMode(SLEEP_PIN, OUTPUT);
  digitalWrite(SLEEP_PIN, HIGH);  // Habilita el driver

  Serial.begin(BAUD_RATE);
  LOG_INFO("Sistema de control de cabezal iniciado.");
  
  motor.initialize();
  sensor.initialize();
  logic.initialize();
}

void loop() {
  logic.handleSerialCommands();
  logic.update();
  if (millis() - lastSensorUpdate >= SENSOR_READ_INTERVAL_MS) {
    lastSensorUpdate = millis();
    logic.updateSensor();
  }
}
