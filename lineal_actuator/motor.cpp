#include "Motor.h"
#include "Config.h"

Motor::Motor(uint8_t stepPin, uint8_t dirPin)
  : stepper(AccelStepper::DRIVER, stepPin, dirPin)
{
}

void Motor::initialize() {
  stepper.setAcceleration(MOTOR_ACCELERATION);
  stepper.setMaxSpeed(MOTOR_MAX_SPEED);
  stepper.setCurrentPosition(0);
  LOG_INFO("Motor initialized with set acceleration and max speed.");
}

void Motor::moveTo(long absolutePosition) {
  stepper.moveTo(absolutePosition);
}

void Motor::moveToBlocking(long absolutePosition) {
  moveTo(absolutePosition);
  while (stepper.distanceToGo() != 0) {
    update();
  }
}

void Motor::moveStepsBlocking(long steps) {
  long target = stepper.currentPosition() + steps;
  moveToBlocking(target);
}

void Motor::stop() {
  stepper.stop();
}

void Motor::update() {
  stepper.run();
}

void Motor::setAcceleration(float acceleration) {
  stepper.setAcceleration(acceleration);
}

void Motor::setMaxSpeed(float speed) {
  stepper.setMaxSpeed(speed);
}

long Motor::currentPosition() {
  return stepper.currentPosition();
}
