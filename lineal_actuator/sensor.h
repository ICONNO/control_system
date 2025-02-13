#ifndef SENSOR_H
#define SENSOR_H

#include <Arduino.h>

class Sensor {
public:
  Sensor(uint8_t trigPin, uint8_t echoPin);
  void initialize();
  float readDistance();
private:
  uint8_t trigPin_;
  uint8_t echoPin_;
};

#endif // SENSOR_H
