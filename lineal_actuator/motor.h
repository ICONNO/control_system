#ifndef MOTOR_H
#define MOTOR_H

#include <Arduino.h>
#include <AccelStepper.h>

class Motor {
public:
  // Constructor: usa el modo DRIVER (STEP/DIR)
  Motor(uint8_t stepPin, uint8_t dirPin);

  // Inicializa el hardware y configura aceleración y velocidad máxima
  void initialize();

  // Mueve el motor a una posición absoluta (no bloqueante)
  void moveTo(long absolutePosition);

  // Movimiento bloqueante hacia una posición
  void moveToBlocking(long absolutePosition);

  // Movimiento relativo bloqueante (en pasos)
  void moveStepsBlocking(long steps);

  // Detiene el movimiento
  void stop();

  // Actualiza el motor (llamar periódicamente desde loop)
  void update();

  // Configura aceleración y velocidad máxima
  void setAcceleration(float acceleration);
  void setMaxSpeed(float speed);

  // Devuelve la posición actual (en pasos)
  long currentPosition();

private:
  AccelStepper stepper;
};

#endif // MOTOR_H
