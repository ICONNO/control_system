#ifndef LOGIC_H
#define LOGIC_H

#include <Arduino.h>
#include "Motor.h"
#include "Sensor.h"
#include "Config.h"

/**
 * @class Logic
 * @brief Implements the control logic for the linear actuator system.
 *
 * The Logic class manages the state transitions, serial command processing,
 * and overall control of the motor based on sensor readings.
 */
class Logic {
public:
    /**
     * @brief Constructor for the Logic class.
     *
     * @param motor Reference to the Motor object controlling the actuator.
     * @param sensor Reference to the Sensor object for distance measurement.
     */
    Logic(Motor& motor, Sensor& sensor);
    
    /**
     * @brief Initializes the system logic.
     *
     * Sets initial states and logs initialization.
     */
    void initialize();
    
    /**
     * @brief Updates the system logic periodically.
     *
     * Reads sensor data, processes serial commands, and updates motor state.
     */
    void update();
    
    /**
     * @brief Processes incoming serial commands.
     *
     * Reads commands from the serial port and performs corresponding actions.
     */
    void handleSerialCommands();
    
    /**
     * @brief Sets the auto mode.
     *
     * @param mode True to enable auto mode, false for manual mode.
     */
    void setAutoMode(bool mode);
    
    /**
     * @brief Adjusts the motor speed and acceleration.
     *
     * @param maxSpeed New maximum speed (steps/s).
     * @param acceleration New acceleration (steps/s²).
     */
    void adjustSpeed(float maxSpeed, float acceleration);
    
    /**
     * @brief Moves the motor to a specified position in a blocking manner.
     *
     * @param pos Target position in steps.
     * @return true when the move is completed.
     */
    bool move_to(long pos);
    
private:
    Motor& motor_;         ///< Reference to the motor controller.
    Sensor& sensor_;       ///< Reference to the sensor module.
    
    MotorState currentState_;    ///< Current state of the motor.
    MotorState previousState_;   ///< Previous state of the motor.
    
    bool autoMode_;        ///< Flag indicating if auto mode is enabled.
    bool movingUp;         ///< Flag for manual upward movement.
    bool movingDown;       ///< Flag for manual downward movement.
    long targetPosition;   ///< Target motor position.
    
    unsigned long previousDistanceMillis_;  ///< Timestamp of the last sensor read.
    float currentDistance_;                   ///< Most recent distance measurement.
    
    /**
     * @brief Transitions the motor state based on sensor data.
     */
    void transitionState();
    
    /**
     * @brief Processes state transitions in auto mode.
     */
    void processState();
};

#endif  // LOGIC_H
