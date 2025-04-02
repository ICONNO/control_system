#include "Motor.h"
#include "Config.h"

/**
 * @file motor.cpp
 * @brief Implements motor control functions using the AccelStepper library.
 */

/**
 * @brief Constructs a Motor object with the given step and direction pins.
 *
 * @param stepPin Pin used for step signals.
 * @param dirPin Pin used for direction signals.
 */
Motor::Motor(uint8_t stepPin, uint8_t dirPin)
  : stepper(AccelStepper::DRIVER, stepPin, dirPin)
{
}

/**
 * @brief Initializes the motor hardware.
 *
 * Sets the acceleration and maximum speed parameters and resets the position.
 */
void Motor::initialize() {
  stepper.setAcceleration(MOTOR_ACCELERATION);
  stepper.setMaxSpeed(MOTOR_MAX_SPEED);
  stepper.setCurrentPosition(0);
  LOG_INFO("Motor initialized with set acceleration and max speed.");
}

/**
 * @brief Commands a non-blocking move to an absolute position.
 *
 * @param absolutePosition The target position in steps.
 */
void Motor::moveTo(long absolutePosition) {
  stepper.moveTo(absolutePosition);
}

/**
 * @brief Commands a blocking move to an absolute position.
 *
 * Waits until the motor reaches the target position.
 *
 * @param absolutePosition The target position in steps.
 */
void Motor::moveToBlocking(long absolutePosition) {
  moveTo(absolutePosition);
  while (stepper.distanceToGo() != 0) {
    update();
  }
}

/**
 * @brief Moves the motor a specified number of steps in blocking mode.
 *
 * @param steps Number of steps to move relative to the current position.
 */
void Motor::moveStepsBlocking(long steps) {
  long target = stepper.currentPosition() + steps;
  moveToBlocking(target);
}

/**
 * @brief Stops the motor movement immediately.
 */
void Motor::stop() {
  stepper.stop();
}

/**
 * @brief Updates the motor state; must be called in the main loop.
 */
void Motor::update() {
  stepper.run();
}

/**
 * @brief Sets the acceleration for the motor.
 *
 * @param acceleration Acceleration in steps per second squared.
 */
void Motor::setAcceleration(float acceleration) {
  stepper.setAcceleration(acceleration);
}

/**
 * @brief Sets the maximum speed for the motor.
 *
 * @param speed Maximum speed in steps per second.
 */
void Motor::setMaxSpeed(float speed) {
  stepper.setMaxSpeed(speed);
}

/**
 * @brief Retrieves the current motor position.
 *
 * @return Current position in steps.
 */
long Motor::currentPosition() {
  return stepper.currentPosition();
}
