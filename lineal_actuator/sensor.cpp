#include "Sensor.h"
#include "Config.h"

/**
 * @file sensor.cpp
 * @brief Implements sensor functions for the linear actuator system.
 */

/**
 * @brief Constructs a Sensor object with specified trigger and echo pins.
 *
 * @param trigPin Pin used to send trigger pulses.
 * @param echoPin Pin used to receive echo signals.
 */
Sensor::Sensor(uint8_t trigPin, uint8_t echoPin)
  : trigPin_(trigPin), echoPin_(echoPin)
{
}

/**
 * @brief Initializes the sensor by setting the proper pin modes.
 */
void Sensor::initialize() {
  pinMode(trigPin_, OUTPUT);
  pinMode(echoPin_, INPUT);
  LOG_INFO("Ultrasonic sensor initialized.");
}

/**
 * @brief Reads the distance from the ultrasonic sensor.
 *
 * Sends a 10 µs pulse and measures the echo time to calculate the distance.
 *
 * @return float The distance in centimeters, or -1.0 if a timeout occurs.
 */
float Sensor::readDistance() {
  digitalWrite(trigPin_, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin_, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin_, LOW);

  long duration = pulseIn(echoPin_, HIGH, ULTRASONIC_TIMEOUT_US);
  if (duration == 0) {
    LOG_ERROR("Ultrasonic sensor timeout.");
    return -1.0;
  }
  float distance = (duration * 0.0343) / 2.0;
  LOG_DEBUG(("Distance read: " + String(distance) + " cm").c_str());
  return distance;
}
