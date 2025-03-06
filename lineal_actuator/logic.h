#ifndef LOGIC_H
#define LOGIC_H

#include <Arduino.h>
#include "Motor.h"
#include "Sensor.h"
#include "Config.h"

class Logic {
public:
    Logic(Motor& motor, Sensor& sensor);
    
    void initialize();      // Initialize logic
    void update();          // Update logic periodically (called in loop)
    void handleSerialCommands();  // Process serial commands
    void setAutoMode(bool mode);
    void adjustSpeed(float maxSpeed, float acceleration);
    bool move_to(long pos); // Blocking move
    
private:
    Motor& motor_;
    Sensor& sensor_;
    
    MotorState currentState_;
    MotorState previousState_;
    
    bool autoMode_;
    bool movingUp;
    bool movingDown;
    long targetPosition;
    
    unsigned long previousDistanceMillis_;
    float currentDistance_;
    
    void transitionState();  // Auto mode state transition
    void processState();     // Process state in auto mode
};

#endif
