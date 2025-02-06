/*
  lineal_actuator.ino
  Firmware para un NEMA 17 controlado mediante un TB6560,
  implementando un protocolo binario simple.
  
  Protocolo: se reciben dos bytes:
    - Primer byte: código de comando.
    - Segundo byte: payload (para movimiento, 1 = subir, 0 = bajar; para SET_SPEED, el nuevo delay en µs).
  
  Comandos definidos:
    CMD_AUTO      = 0xA0   // Modo automático: baja hasta límite (usando sensor de distancia)
    CMD_UP        = 0xA1   // Mover hacia arriba (modo manual)
    CMD_DOWN      = 0xA2   // Mover hacia abajo (modo manual)
    CMD_STOP      = 0xA3   // Detener motor
    CMD_SET_SPEED = 0xA4   // Ajustar velocidad (payload = nuevo delay en µs)
  
  NOTA: Este ejemplo usa delays (delayMicroseconds) para generar los pulsos, lo que puede bloquear el loop.  
  Se recomienda en el futuro usar una máquina de estados o interrupciones para evitar saturar el Arduino.
*/

#include <Arduino.h>
#include <SPI.h>

// ==================== CONFIGURACIÓN ====================
#define MOTOR_PUL_PIN 3        // Pin para el pulso (STEP)
#define MOTOR_DIR_PIN 4        // Pin para la dirección (DIR)

#define SENSOR_TRIG_PIN 9      // Pin de Trigger (sensor ultrasónico)
#define SENSOR_ECHO_PIN 10     // Pin de Echo

const float DISTANCE_LOWER_TARGET = 7.0;  // cm (para detener al bajar en modo automático)
const float DISTANCE_UPPER_TARGET = 35.0;   // cm (para detener al subir en modo automático)
const float DISTANCE_MARGIN = 0.5;

const unsigned long PULSE_INTERVAL_DEFAULT_US = 100;  // Delay entre pasos (µs)
unsigned long pulseInterval = PULSE_INTERVAL_DEFAULT_US;

const unsigned long SENSOR_READ_INTERVAL_MS = 100;    // Intervalo para leer el sensor
const unsigned long ULTRASONIC_TIMEOUT_US = 30000;

// Definición de estados para la lógica
enum class MotorState {
  MOVING_DOWN,
  MOVING_UP,
  IDLE
};

// Configuración de logging (para debug; en producción, usar LOG_VERBOSITY = 0)
#define LOG_VERBOSITY 0

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

// ==================== PROTOCOLO BINARIO ====================
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
    setDirection(LOW);  // Asumimos: LOW para subir
    isMoving_ = true;
    previousMicros_ = micros();
    togglePulse();
    LOG_INFO("Moviendo hacia arriba.");
  }

  void moveDown() {
    setDirection(HIGH); // Asumimos: HIGH para bajar
    isMoving_ = true;
    previousMicros_ = micros();
    togglePulse();
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
    // Para evitar saturar Serial, se comenta el LOG_DEBUG
    // LOG_DEBUG("Pulso alternado.");
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

  // Actualiza el motor sin bloqueos (lo más rápido posible)
  void update() {
    motor_.update();
  }

  // Lee el sensor y procesa la transición de estado en modo automático
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

  // Maneja comandos recibidos vía Serial usando el protocolo binario
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
            adjustSpeed(payload); // El payload es el nuevo delay en µs
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

  // En modo automático, se verifica la distancia para detener el movimiento
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
          // En modo automático, podrías alternar la dirección basándote en el estado previo (opcional)
          break;
      }
    }
  }

  void setAutoMode(bool mode) { autoMode_ = mode; }
  void adjustSpeed(unsigned long newInterval) {
    pulseInterval = newInterval;
    motor_.setPulseInterval(newInterval);
  }

  // Stubs de seguridad y control
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
  // Inicia Serial a 115200 baudios (asegúrate de que tu monitor y tu aplicación lo usen)
  Serial.begin(115200);
  LOG_INFO("Sistema de control de cabezal iniciado.");

  motor.initialize();
  sensor.initialize();
  logic.initialize();
}

void loop() {
  // Procesar comandos binarios (dos bytes por comando)
  logic.handleSerialCommands();

  // Actualizar el motor continuamente
  logic.update();

  // Cada SENSOR_READ_INTERVAL_MS se lee el sensor y se procesa la lógica
  if (millis() - lastSensorUpdate >= SENSOR_READ_INTERVAL_MS) {
    lastSensorUpdate = millis();
    logic.updateSensor();
  }
}
