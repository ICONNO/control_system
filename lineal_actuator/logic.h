#ifndef LOGIC_H
#define LOGIC_H

#include <Arduino.h>
#include "Motor.h"
#include "Sensor.h"
#include "Config.h"

/**
 * @brief Clase que maneja la lógica del sistema.
 *
 * Se encarga de procesar los comandos seriales, actualizar el estado del motor según
 * la lectura del sensor ultrasónico y gestionar el modo automático.
 */
class Logic {
public:
    /**
     * @brief Constructor de la clase Logic.
     * 
     * @param motor Referencia al objeto Motor.
     * @param sensor Referencia al objeto Sensor.
     */
    Logic(Motor& motor, Sensor& sensor);
    
    /**
     * @brief Inicializa la lógica del sistema.
     */
    void initialize();
    
    /**
     * @brief Actualiza la lógica del sistema y el estado del motor.
     * 
     * Realiza la lectura del sensor, imprime la distancia y llama a la función de
     * procesamiento de estados.
     */
    void update();
    
    /**
     * @brief Maneja los comandos recibidos por el puerto serial.
     */
    void handleSerialCommands();
    
    /**
     * @brief Procesa el estado actual del sistema.
     * 
     * Llama a la función de transición de estado.
     */
    void processState();
    
    /**
     * @brief Activa o desactiva el modo automático.
     * 
     * @param mode True para activar el modo automático, false para desactivarlo.
     */
    void setAutoMode(bool mode);
    
    /**
     * @brief Ajusta la velocidad del motor.
     * 
     * @param newInterval Nuevo intervalo de pulsos (en micros).
     */
    void adjustSpeed(unsigned long newInterval);
    
private:
    // Referencias a los módulos del sistema
    Motor& motor_;
    Sensor& sensor_;
    
    // Estados actuales y previos del motor (MotorState está definido en Config.h)
    MotorState currentState_;
    MotorState previousState_;
    
    // Indicador del modo automático
    bool autoMode_;
    
    // Tiempo de la última medición de distancia
    unsigned long previousDistanceMillis_;
    
    // Última distancia leída por el sensor
    float currentDistance_;
    
    /**
     * @brief Realiza la transición entre estados en función de la distancia medida.
     *
     * Evalúa la distancia actual y detiene o invierte el movimiento del motor según
     * los umbrales definidos.
     */
    void transitionState();
};

#endif // LOGIC_H
