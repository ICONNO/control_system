#include "Logic.h"

// Comandos Seriales
const String CMD_AUTO = "AUTO";
const String CMD_UP = "UP";
const String CMD_DOWN = "DOWN";
const String CMD_STOP = "STOP";
const String CMD_SET_SPEED = "SET_SPEED";
const String CMD_PUMP_ON = "PUMP_ON";
const String CMD_PUMP_OFF = "PUMP_OFF";

Logic::Logic(Motor& motor, Sensor& sensor)
  : motor_(motor), sensor_(sensor),
    currentState_(MotorState::IDLE), previousState_(MotorState::IDLE),
    autoMode_(false), previousDistanceMillis_(0),
    currentDistance_(0.0),
    movingUp(false), movingDown(false), targetPosition(0)
{
    targetPosition = motor_.currentPosition();
}

void Logic::initialize() {
  currentState_ = MotorState::IDLE;
  previousState_ = MotorState::IDLE;
  LOG_INFO("Lógica del sistema inicializada.");
}

void Logic::update() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousDistanceMillis_ >= SENSOR_READ_INTERVAL_MS) {
    previousDistanceMillis_ = currentMillis;
    currentDistance_ = sensor_.readDistance();
    if (currentDistance_ >= 0.0) {
      Serial.print(F("Distancia actual: "));
      Serial.print(currentDistance_);
      Serial.println(F(" cm"));
    } else {
      Serial.println(F("Error en la lectura del sensor ultrasónico."));
    }
    if (autoMode_) {
      processState();
    }
  }
  
  const int deltaSteps = 10;  // Ajusta este valor para modificar la sensibilidad del movimiento manual
  if (!autoMode_) {
    if (movingUp) {
      targetPosition += deltaSteps;
      motor_.moveTo(targetPosition);
    }
    else if (movingDown) {
      targetPosition -= deltaSteps;
      motor_.moveTo(targetPosition);
    }
  }
  
  motor_.update();
}

void Logic::handleSerialCommands() {
  while (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    Serial.print(F("Comando recibido: "));
    Serial.println(command);

    if (command.equalsIgnoreCase(CMD_AUTO)) {
      LOG_INFO("Activando modo automático.");
      setAutoMode(true);
      motor_.moveToBlocking(10000);
      currentState_ = MotorState::MOVING_DOWN;
      previousState_ = MotorState::MOVING_DOWN;
      movingUp = false;
      movingDown = false;
      targetPosition = motor_.currentPosition();
    }
    else if (command.equalsIgnoreCase(CMD_UP)) {
      LOG_INFO("Modo manual: Activando subida continua.");
      setAutoMode(false);
      movingUp = true;
      movingDown = false;
      targetPosition = motor_.currentPosition();
    }
    else if (command.equalsIgnoreCase(CMD_DOWN)) {
      LOG_INFO("Modo manual: Activando bajada continua.");
      setAutoMode(false);
      movingDown = true;
      movingUp = false;
      targetPosition = motor_.currentPosition();
    }
    else if (command.equalsIgnoreCase(CMD_STOP)) {
      LOG_INFO("Deteniendo movimiento manual.");
      movingUp = false;
      movingDown = false;
      motor_.stop();
      currentState_ = MotorState::IDLE;
    }
    else if (command.startsWith(CMD_SET_SPEED)) {
      int spaceIndex = command.indexOf(' ');
      if (spaceIndex != -1) {
        String valueStr = command.substring(spaceIndex + 1);
        float newMaxSpeed = valueStr.toFloat();
        if (newMaxSpeed > 0) {
          // Ajustamos la velocidad máxima y usamos la aceleración definida en Config.h
          adjustSpeed(newMaxSpeed, MOTOR_ACCELERATION);
          Serial.print(F("Velocidad máxima ajustada a: "));
          Serial.print(newMaxSpeed);
          Serial.println(F(" pasos/s."));
        } else {
          LOG_ERROR("Valor de velocidad inválido.");
        }
      }
      else {
        LOG_ERROR("Formato de comando incorrecto para SET_SPEED.");
      }
    }
    else if (command.equalsIgnoreCase(CMD_PUMP_ON)) {
      LOG_INFO("Encendiendo bomba de vacío.");
      // Suponiendo que el relé es activo por nivel bajo:
      digitalWrite(RELAY_PUMP_PIN, LOW);
    }
    else if (command.equalsIgnoreCase(CMD_PUMP_OFF)) {
      LOG_INFO("Apagando bomba de vacío.");
      digitalWrite(RELAY_PUMP_PIN, HIGH);
    }
    else {
      LOG_ERROR("Comando no reconocido.");
    }
  }
}

void Logic::transitionState() {
  // Modo automático: se mueve en función de la lectura del sensor
  switch (currentState_) {
    case MotorState::MOVING_DOWN:
      if (currentDistance_ <= DISTANCE_LOWER_TARGET + DISTANCE_MARGIN) {
        motor_.stop();
        LOG_INFO("¡Distancia inferior alcanzada! Deteniendo motor.");
        currentState_ = MotorState::IDLE;
      }
      break;
    case MotorState::MOVING_UP:
      if (currentDistance_ >= DISTANCE_UPPER_TARGET - DISTANCE_MARGIN) {
        motor_.stop();
        LOG_INFO("¡Distancia superior alcanzada! Deteniendo motor.");
        currentState_ = MotorState::IDLE;
      }
      break;
    case MotorState::IDLE:
      if (autoMode_) {
        if (previousState_ == MotorState::MOVING_DOWN) {
          motor_.moveToBlocking(motor_.currentPosition() + 200);
          currentState_ = MotorState::MOVING_UP;
          previousState_ = MotorState::MOVING_UP;
        }
        else if (previousState_ == MotorState::MOVING_UP) {
          motor_.moveToBlocking(motor_.currentPosition() - 200);
          currentState_ = MotorState::MOVING_DOWN;
          previousState_ = MotorState::MOVING_DOWN;
        }
      }
      break;
  }
}

void Logic::processState() {
  if (autoMode_) {
    transitionState();
  }
}

void Logic::setAutoMode(bool mode) {
  autoMode_ = mode;
  if (mode) {
    movingUp = false;
    movingDown = false;
  }
}

void Logic::adjustSpeed(float maxSpeed, float acceleration) {
  motor_.setMaxSpeed(maxSpeed);
  motor_.setAcceleration(acceleration);
}

bool Logic::move_to(long pos) {
  motor_.moveToBlocking(pos);
  return true;
}
