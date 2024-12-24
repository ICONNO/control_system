// Motor.h

#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>

class Motor {
public:
  Motor(uint8_t pulPin, uint8_t dirPin);
  void initialize();
  void moveUp();
  void moveDown();
  void stop();
  void update();
  void setPulseInterval(unsigned long interval);

private:
  uint8_t pulPin_;
  uint8_t dirPin_;
  bool isMoving_;
  bool pulseState_;
  unsigned long previousMicros_;
  unsigned long pulseInterval_;

  void togglePulse();
};

#endif // MOTOR_H
