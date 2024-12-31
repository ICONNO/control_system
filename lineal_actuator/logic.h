// Logic.h

#ifndef LOGIC_H
#define LOGIC_H

#include <Arduino.h>
#include "Motor.h"
#include "Sensor.h"

enum class SystemStatus {
    OK,
    ERROR,
    EMERGENCY_STOP,
    CALIBRATING,
    MAINTENANCE
};

class Logic {
public:
    Logic(Motor& motor, Sensor& sensor);
    void initialize();
    void update();
    void handleSerialCommands();
    
    // Métodos de seguridad
    void emergencyStop();
    void resetSystem();
    bool isSafe() const;
    SystemStatus getStatus() const;
    
    // Métodos de control mejorados
    void calibrate();
    void setMaintenanceMode(bool enabled);
    float getSystemHealth() const;

private:
    Motor& motor_;
    Sensor& sensor_;
    MotorState currentState_;
    MotorState previousState_;
    SystemStatus status_;
    
    // Parámetros de seguridad
    bool autoMode_;
    bool emergencyStopActive_;
    bool maintenanceMode_;
    unsigned long lastWatchdogReset_;
    unsigned long previousDistanceMillis_;
    float currentDistance_;
    float maxSpeed_;
    float minSpeed_;
    
    // Seguimiento de errores
    uint8_t errorCount_;
    unsigned long lastErrorTime_;
    
    // Métodos privados
    void transitionState();
    void processState();
    void updateWatchdog();
    void validateParameters();
    void logSystemStatus();
    bool checkSafetyLimits();
    void handleError(const char* errorMsg);
};

#endif // LOGIC_H
