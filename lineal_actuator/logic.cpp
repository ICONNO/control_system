#include "Logic.h"

// Serial command definitions
const String CMD_AUTO      = "AUTO";
const String CMD_UP        = "UP";
const String CMD_DOWN      = "DOWN";
const String CMD_STOP      = "STOP";
const String CMD_SET_SPEED = "SET_SPEED";
const String CMD_PUMP_ON   = "PUMP_ON";
const String CMD_PUMP_OFF  = "PUMP_OFF";

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
  LOG_INFO("System logic initialized.");
}

void Logic::update() {
  unsigned long now = millis();
  if (now - previousDistanceMillis_ >= SENSOR_READ_INTERVAL_MS) {
    previousDistanceMillis_ = now;
    currentDistance_ = sensor_.readDistance();
    if (currentDistance_ < 0.0) {
      Serial.println(F("Ultrasonic sensor error."));
    } else {
      Serial.print(F("Current distance: "));
      Serial.print(currentDistance_);
      Serial.println(F(" cm"));
    }
    if (autoMode_) {
      processState();
    }
  }
  
  const int deltaSteps = 10;  // Step increment for manual control
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
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    Serial.print(F("Command received: "));
    Serial.println(cmd);

    if (cmd.equalsIgnoreCase(CMD_AUTO)) {
      LOG_INFO("Auto mode activated.");
      setAutoMode(true);
      motor_.moveToBlocking(10000);
      currentState_ = MotorState::MOVING_DOWN;
      previousState_ = MotorState::MOVING_DOWN;
      movingUp = false;
      movingDown = false;
      targetPosition = motor_.currentPosition();
    }
    else if (cmd.equalsIgnoreCase(CMD_UP)) {
      LOG_INFO("Manual mode: Continuous up.");
      setAutoMode(false);
      movingUp = true;
      movingDown = false;
      targetPosition = motor_.currentPosition();
    }
    else if (cmd.equalsIgnoreCase(CMD_DOWN)) {
      LOG_INFO("Manual mode: Continuous down.");
      setAutoMode(false);
      movingDown = true;
      movingUp = false;
      targetPosition = motor_.currentPosition();
    }
    else if (cmd.equalsIgnoreCase(CMD_STOP)) {
      LOG_INFO("Stopping manual motion.");
      movingUp = false;
      movingDown = false;
      motor_.stop();
      currentState_ = MotorState::IDLE;
    }
    else if (cmd.startsWith(CMD_SET_SPEED)) {
      int spaceIdx = cmd.indexOf(' ');
      if (spaceIdx != -1) {
        String valStr = cmd.substring(spaceIdx + 1);
        float newSpeed = valStr.toFloat();
        if (newSpeed > 0) {
          adjustSpeed(newSpeed, MOTOR_ACCELERATION);
          Serial.print(F("Max speed set to: "));
          Serial.print(newSpeed);
          Serial.println(F(" steps/s."));
        } else {
          LOG_ERROR("Invalid speed value.");
        }
      }
      else {
        LOG_ERROR("Incorrect SET_SPEED format.");
      }
    }
    else if (cmd.equalsIgnoreCase(CMD_PUMP_ON)) {
      LOG_INFO("Vacuum pump ON.");
      digitalWrite(RELAY_PUMP_PIN, HIGH);
    }
    else if (cmd.equalsIgnoreCase(CMD_PUMP_OFF)) {
      LOG_INFO("Vacuum pump OFF.");
      digitalWrite(RELAY_PUMP_PIN, LOW);
    }
    else {
      LOG_ERROR("Unknown command.");
    }
  }
}

void Logic::transitionState() {
  switch (currentState_) {
    case MotorState::MOVING_DOWN:
      if (currentDistance_ <= DIST_LOWER_TARGET + DIST_MARGIN) {
        motor_.stop();
        LOG_INFO("Lower limit reached. Stopping motor.");
        currentState_ = MotorState::IDLE;
      }
      break;
    case MotorState::MOVING_UP:
      if (currentDistance_ >= DIST_UPPER_TARGET - DIST_MARGIN) {
        motor_.stop();
        LOG_INFO("Upper limit reached. Stopping motor.");
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
