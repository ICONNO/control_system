#include "Sensor.h"
#include "Config.h"

Sensor::Sensor(uint8_t trigPin, uint8_t echoPin)
  : trigPin_(trigPin), echoPin_(echoPin)
{
}

void Sensor::initialize() {
  pinMode(trigPin_, OUTPUT);
  pinMode(echoPin_, INPUT);
  LOG_INFO("Sensor ultrasónico inicializado.");
}

float Sensor::readDistance() {
  digitalWrite(trigPin_, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin_, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin_, LOW);

  long duration = pulseIn(echoPin_, HIGH, ULTRASONIC_TIMEOUT_US);
  if (duration == 0) {
    LOG_ERROR("Timeout en la lectura del sensor ultrasónico.");
    return -1.0;
  }
  float distance = (duration * 0.0343) / 2.0;
  LOG_DEBUG(("Distancia leída: " + String(distance) + " cm").c_str());
  return distance;
}
