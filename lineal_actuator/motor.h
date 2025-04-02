#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>
#include <AccelStepper.h>

/**
 * @class Motor
 * @brief Controls the motor using AccelStepper in DRIVER mode.
 *
 * Provides methods to initialize the motor, command movements (blocking and non-blocking),
 * and update motor status.
 */
class Motor {
public:
  /**
   * @brief Constructs a Motor object with specified pins.
   *
   * @param stepPin Pin for STEP signals.
   * @param dirPin Pin for DIR signals.
   */
  Motor(uint8_t stepPin, uint8_t dirPin);

  /**
   * @brief Initializes the motor hardware.
   */
  void initialize();

  /**
   * @brief Commands a non-blocking move to an absolute position.
   *
   * @param absolutePosition Target position in steps.
   */
  void moveTo(long absolutePosition);

  /**
   * @brief Commands a blocking move to an absolute position.
   *
   * Waits until the motor reaches the target.
   *
   * @param absolutePosition Target position in steps.
   */
  void moveToBlocking(long absolutePosition);

  /**
   * @brief Moves the motor a relative number of steps in a blocking manner.
   *
   * @param steps Number of steps to move.
   */
  void moveStepsBlocking(long steps);

  /**
   * @brief Stops the motor immediately.
   */
  void stop();

  /**
   * @brief Updates the motor control; must be called repeatedly in loop.
   */
  void update();

  /**
   * @brief Sets the motor acceleration.
   *
   * @param acceleration Acceleration in steps/s².
   */
  void setAcceleration(float acceleration);

  /**
   * @brief Sets the maximum motor speed.
   *
   * @param speed Maximum speed in steps/s.
   */
  void setMaxSpeed(float speed);

  /**
   * @brief Gets the current motor position.
   *
   * @return Current position in steps.
   */
  long currentPosition();

private:
  AccelStepper stepper;  ///< Instance of the AccelStepper library for motor control.
};

#endif  // MOTOR_H
