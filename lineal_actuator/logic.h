#ifndef LOGIC_H
#define LOGIC_H

#include <Arduino.h>
#include "Motor.h"
#include "Sensor.h"

// Declaración de estados (ya definidos en Config.h, pero se pueden incluir aquí para la lógica)
enum class MotorState {
  MOVING_DOWN,
  MOVING_UP,
  IDLE
};

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
    // Ahora update() solo se encargará de actualizar el motor
    void update();
    // Nueva función para leer el sensor y procesar el estado
    void updateSensor();
    void handleSerialCommands();
    
    // Métodos de seguridad (stubs)
    void emergencyStop();
    void resetSystem();
    bool isSafe() const;
    SystemStatus getStatus() const;
    
    // Métodos de control mejorados (stubs)
    void calibrate();
    void setMaintenanceMode(bool enabled);
    float getSystemHealth() const;
    
    // Métodos básicos
    void setAutoMode(bool mode);
    void adjustSpeed(unsigned long newInterval);

private:
    Motor& motor_;
    Sensor& sensor_;
    MotorState currentState_;
    MotorState previousState_;
    bool autoMode_;
    unsigned long previousDistanceMillis_;
    float currentDistance_;
};

#endif // LOGIC_H
