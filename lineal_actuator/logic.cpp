#include "Logic.h"

/**
 * @file logic.cpp
 * @brief Implements the system control logic for the linear actuator.
 *
 * This file defines the methods for processing serial commands, updating the system state,
 * and transitioning between different motor states (e.g., moving up, moving down, idle).
 */

// Serial command definitions
const String CMD_AUTO      = "AUTO";       ///< Command to activate automatic mode.
const String CMD_UP        = "UP";         ///< Command for manual upward movement.
const String CMD_DOWN      = "DOWN";       ///< Command for manual downward movement.
const String CMD_STOP      = "STOP";       ///< Command to stop movement.
const String CMD_SET_SPEED = "SET_SPEED";  ///< Command to set motor speed.
const String CMD_PUMP_ON   = "PUMP_ON";    ///< Command to activate the vacuum pump.
const String CMD_PUMP_OFF  = "PUMP_OFF";   ///< Command to deactivate the vacuum pump.

Logic::Logic(Motor& motor, Sensor& sensor)
  : motor_(motor), sensor_(sensor),
    currentState_(MotorState::IDLE), previousState_(MotorState::IDLE),
    autoMode_(false), previousDistanceMillis_(0),
    currentDistance_(0.0),
    movingUp(false), movingDown(false), targetPosition(0)
{
    // Set the initial target position to the current motor position.
    targetPosition = motor_.currentPosition();
}

/**
 * @brief Initializes the control logic.
 *
 * Sets the motor state to idle and logs initialization.
 */
void Logic::initialize() {
  currentState_ = MotorState::IDLE;
  previousState_ = MotorState::IDLE;
  LOG_INFO("System logic initialized.");
}

/**
 * @brief Periodically updates the system state.
 *
 * Reads sensor data at defined intervals, processes commands,
 * and updates motor movement accordingly.
 */
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
  
  const int deltaSteps = 10;  // Step increment for manual control.
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

/**
 * @brief Processes incoming serial commands.
 *
 * Reads commands from the serial port and adjusts system behavior
 * (switching modes, moving motor, adjusting speed, etc.) accordingly.
 */
void Logic::handleSerialCommands() {
  while (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    Serial.print(F("Command received: "));
    Serial.println(cmd);

    if (cmd.equalsIgnoreCase(CMD_AUTO)) {
      LOG_INFO("Auto mode activated.");
      setAutoMode(true);
      motor_.moveTo(10000); // Command a long downward move.
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

/**
 * @brief Transitions the motor state based on sensor readings.
 *
 * When certain distance thresholds are reached, stops the motor,
 * triggers remote capture if needed, and commands the motor to change direction.
 */
void Logic::transitionState() {
  switch (currentState_) {
    case MotorState::MOVING_DOWN:
      if (currentDistance_ <= DIST_LOWER_TARGET + DIST_MARGIN) {
        motor_.stop();
        LOG_INFO("Lower limit reached. Stopping for 5 seconds for capture, then moving up.");
        Serial.println("CAPTURE");
        delay(10000);  // Wait for 10 seconds (adjustable as needed)
        motor_.moveTo(-100000000000);
        currentState_ = MotorState::MOVING_UP;
        previousState_ = MotorState::MOVING_UP;
      }
      break;
    case MotorState::MOVING_UP:
      if (currentDistance_ >= DIST_UPPER_TARGET - DIST_MARGIN) {
        motor_.stop();
        LOG_INFO("Upper limit reached. Moving down.");
        motor_.moveTo(100000000000);
        currentState_ = MotorState::MOVING_DOWN;
        previousState_ = MotorState::MOVING_DOWN;
      }
      break;
    case MotorState::IDLE:
      if (autoMode_) {
        if (previousState_ == MotorState::MOVING_DOWN) {
          motor_.moveTo(-100000000000);
          currentState_ = MotorState::MOVING_UP;
          previousState_ = MotorState::MOVING_UP;
        }
        else if (previousState_ == MotorState::MOVING_UP) {
          motor_.moveTo(100000000000);
          currentState_ = MotorState::MOVING_DOWN;
          previousState_ = MotorState::MOVING_DOWN;
        }
      }
      break;
  }
}

/**
 * @brief Processes the current state if auto mode is active.
 */
void Logic::processState() {
  if (autoMode_) {
    transitionState();
  }
}

/**
 * @brief Sets the auto mode for the system.
 *
 * Disables manual movement flags when auto mode is activated.
 *
 * @param mode True to enable auto mode; False to disable.
 */
void Logic::setAutoMode(bool mode) {
  autoMode_ = mode;
  if (mode) {
    movingUp = false;
    movingDown = false;
  }
}

/**
 * @brief Adjusts the motor speed and acceleration.
 *
 * Updates the motor's maximum speed and acceleration settings.
 *
 * @param maxSpeed New maximum speed (steps/s).
 * @param acceleration New acceleration (steps/s²).
 */
void Logic::adjustSpeed(float maxSpeed, float acceleration) {
  motor_.setMaxSpeed(maxSpeed);
  motor_.setAcceleration(acceleration);
}

/**
 * @brief Blocking move command to move the motor to a specific position.
 *
 * @param pos Target position in steps.
 * @return true after completion.
 */
bool Logic::move_to(long pos) {
  motor_.moveToBlocking(pos);
  return true;
}
