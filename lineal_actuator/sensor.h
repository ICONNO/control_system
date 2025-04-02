#ifndef SENSOR_H
#define SENSOR_H

#include <Arduino.h>

/**
 * @class Sensor
 * @brief Handles ultrasonic sensor operations.
 *
 * Provides methods to initialize the sensor and read distance measurements.
 */
class Sensor {
public:
  /**
   * @brief Constructs a Sensor object.
   *
   * @param trigPin Pin for triggering the ultrasonic pulse.
   * @param echoPin Pin for receiving the echo signal.
   */
  Sensor(uint8_t trigPin, uint8_t echoPin);

  /**
   * @brief Initializes the sensor.
   *
   * Sets the trigger pin as OUTPUT and the echo pin as INPUT.
   */
  void initialize();

  /**
   * @brief Reads the distance using the ultrasonic sensor.
   *
   * @return float The distance in centimeters, or -1.0 if an error occurs.
   */
  float readDistance();

private:
  uint8_t trigPin_;  ///< Trigger pin for the ultrasonic sensor.
  uint8_t echoPin_;  ///< Echo pin for the ultrasonic sensor.
};

#endif  // SENSOR_H
