#ifndef LOGIC_H
#define LOGIC_H

#include <Arduino.h>
#include "Motor.h"
#include "Sensor.h"
#include "Config.h"

/**
 * Clase que maneja la lógica del sistema.
 * Procesa comandos seriales, actualiza el estado del motor según la lectura del sensor,
 * y administra tanto un modo automático como un modo manual continuo basado en banderas.
 */
class Logic {
public:
    Logic(Motor& motor, Sensor& sensor);
    
    // Inicializa la lógica del sistema
    void initialize();
    
    // Actualiza la lógica (se debe llamar periódicamente en loop)
    void update();
    
    // Procesa los comandos recibidos por Serial
    void handleSerialCommands();
    
    // Cambia entre modo automático y manual
    void setAutoMode(bool mode);
    
    // Ajusta parámetros del motor (velocidad y aceleración)
    void adjustSpeed(float maxSpeed, float acceleration);
    
    // Mueve la cabeza a una posición (bloqueante)
    bool move_to(long pos);
    
private:
    Motor& motor_;
    Sensor& sensor_;
    
    MotorState currentState_;
    MotorState previousState_;
    
    bool autoMode_;
    
    // Variables para control continuo manual
    bool movingUp;
    bool movingDown;
    long targetPosition;
    
    unsigned long previousDistanceMillis_;
    float currentDistance_;
    
    // Realiza la transición de estados (modo automático)
    void transitionState();
    
    // Procesa el estado actual llamando a transitionState()
    void processState();
};

#endif // LOGIC_H
