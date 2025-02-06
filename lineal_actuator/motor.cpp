#include "Logic.h"
#include "Config.h"

const String CMD_AUTO = "AUTO";
const String CMD_UP = "UP";
const String CMD_DOWN = "DOWN";
const String CMD_STOP = "STOP";
const String CMD_SET_SPEED = "SET_SPEED";

Logic::Logic(Motor& motor, Sensor& sensor)
  : motor_(motor), sensor_(sensor),
    currentState_(MotorState::IDLE), previousState_(MotorState::IDLE),
    autoMode_(false), previousDistanceMillis_(0),
    currentDistance_(0.0) {}

void Logic::initialize() {
  currentState_ = MotorState::IDLE;
  previousState_ = MotorState::IDLE;
  LOG_INFO("Lógica del sistema inicializada.");
}

// Ahora update() solo llama a la actualización del motor
void Logic::update() {
  motor_.update();
}

// Nueva función para actualizar el sensor y procesar el estado
void Logic::updateSensor() {
  currentDistance_ = sensor_.readDistance();
  if (currentDistance_ >= 0.0) {
    Serial.print("Distancia actual: ");
    Serial.print(currentDistance_);
    Serial.println(" cm");
  } else {
    Serial.println("Error en la lectura del sensor ultrasónico.");
  }
  // Procesar el estado en función de la lectura y del modo
  // La transición automática solo se realiza en modo AUTO
  if (autoMode_) {
    switch (currentState_) {
      case MotorState::MOVING_DOWN:
        if (currentDistance_ <= DISTANCE_LOWER_TARGET + DISTANCE_MARGIN) {
          motor_.stop();
          LOG_INFO("¡Distancia de 7 cm alcanzada en modo automático! Deteniendo motor.");
          currentState_ = MotorState::IDLE;
        }
        break;
      case MotorState::MOVING_UP:
        if (currentDistance_ >= DISTANCE_UPPER_TARGET - DISTANCE_MARGIN) {
          motor_.stop();
          LOG_INFO("¡Distancia de 35 cm alcanzada en modo automático! Deteniendo motor.");
          currentState_ = MotorState::IDLE;
        }
        break;
      case MotorState::IDLE:
        if (previousState_ == MotorState::MOVING_DOWN) {
          motor_.moveUp();
          currentState_ = MotorState::MOVING_UP;
          previousState_ = MotorState::MOVING_UP;
        }
        else if (previousState_ == MotorState::MOVING_UP) {
          motor_.moveDown();
          currentState_ = MotorState::MOVING_DOWN;
          previousState_ = MotorState::MOVING_DOWN;
        }
        break;
    }
  }
  // En modo manual, se deja que el operador controle cuándo detener el motor.
}

void Logic::handleSerialCommands() {
  while (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    LOG_INFO(("Comando recibido: " + command).c_str());

    if (command.equalsIgnoreCase(CMD_AUTO)) {
      LOG_INFO("Activando modo automático.");
      setAutoMode(true);
      motor_.moveDown();
      currentState_ = MotorState::MOVING_DOWN;
      previousState_ = MotorState::MOVING_DOWN;
    }
    else if (command.equalsIgnoreCase(CMD_UP)) {
      LOG_INFO("Modo manual: Moviendo hacia arriba.");
      setAutoMode(false);
      motor_.moveUp();
      currentState_ = MotorState::MOVING_UP;
      previousState_ = MotorState::MOVING_UP;
    }
    else if (command.equalsIgnoreCase(CMD_DOWN)) {
      LOG_INFO("Modo manual: Moviendo hacia abajo.");
      setAutoMode(false);
      motor_.moveDown();
      currentState_ = MotorState::MOVING_DOWN;
      previousState_ = MotorState::MOVING_DOWN;
    }
    else if (command.equalsIgnoreCase(CMD_STOP)) {
      LOG_INFO("Deteniendo motor y desactivando modo automático.");
      setAutoMode(false);
      motor_.stop();
      currentState_ = MotorState::IDLE;
    }
    else if (command.startsWith(CMD_SET_SPEED)) {
      int spaceIndex = command.indexOf(' ');
      if (spaceIndex != -1) {
        String valueStr = command.substring(spaceIndex + 1);
        unsigned long newInterval = valueStr.toInt();
        if (newInterval > 0 && newInterval < 1000000) {
          adjustSpeed(newInterval);
          Serial.print("Intervalo de pulsos ajustado a: ");
          Serial.print(pulseInterval);
          Serial.println(" micros.");
        }
        else {
          LOG_ERROR("Valor de velocidad inválido.");
        }
      }
      else {
        LOG_ERROR("Formato de comando incorrecto para SET_SPEED.");
      }
    }
    else {
      LOG_ERROR("Comando no reconocido.");
    }
  }
}

void Logic::setAutoMode(bool mode) {
  autoMode_ = mode;
}

void Logic::adjustSpeed(unsigned long newInterval) {
  pulseInterval = newInterval;
  motor_.setPulseInterval(newInterval);
}

// Métodos de seguridad y control mejorado (stubs)
void Logic::emergencyStop() {
    motor_.stop();
}

void Logic::resetSystem() {
    // Implementar reinicio del sistema si es necesario
}

bool Logic::isSafe() const {
    return true;
}

SystemStatus Logic::getStatus() const {
    return SystemStatus::OK;
}

void Logic::calibrate() {
    // Implementar calibración si es necesario
}

void Logic::setMaintenanceMode(bool enabled) {
    // Implementar modo de mantenimiento si es necesario
}

float Logic::getSystemHealth() const {
    return 100.0;
}
