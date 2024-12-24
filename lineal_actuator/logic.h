// Logic.h

#ifndef LOGIC_H
#define LOGIC_H

#include <Arduino.h>
#include "Motor.h"
#include "Sensor.h"

class Logic {
public:
  Logic(Motor& motor, Sensor& sensor);
  void initialize();
  void update();
  void handleSerialCommands();

private:
  Motor& motor_;
  Sensor& sensor_;
  MotorState currentState_;
  MotorState previousState_;
  bool autoMode_;
  unsigned long previousDistanceMillis_;
  float currentDistance_;

  void transitionState();
  void processState();
  void setAutoMode(bool mode);
  void adjustSpeed(unsigned long newInterval);
};

#endif // LOGIC_H
