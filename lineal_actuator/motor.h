#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>
#include <AccelStepper.h>

class Motor {
public:
  // Constructor using DRIVER mode (STEP/DIR)
  Motor(uint8_t stepPin, uint8_t dirPin);

  void initialize();                        // Initialize motor hardware
  void moveTo(long absolutePosition);       // Non-blocking move
  void moveToBlocking(long absolutePosition);  // Blocking move
  void moveStepsBlocking(long steps);       // Move relative in blocking mode
  void stop();                              // Stop motor
  void update();                            // Must be called in loop
  void setAcceleration(float acceleration);
  void setMaxSpeed(float speed);
  long currentPosition();

private:
  AccelStepper stepper;
};

#endif  // MOTOR_H
