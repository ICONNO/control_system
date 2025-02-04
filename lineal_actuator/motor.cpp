#include "Motor.h"
#include "Config.h"

Motor::Motor(uint8_t pulPin, uint8_t dirPin)
  : pulPin_(pulPin), dirPin_(dirPin), isMoving_(false),
    pulseState_(LOW), previousMicros_(0),
    pulseInterval_(PULSE_INTERVAL_DEFAULT_US) {}

void Motor::initialize() {
  pinMode(pulPin_, OUTPUT);
  pinMode(dirPin_, OUTPUT);
  digitalWrite(pulPin_, LOW);
  digitalWrite(dirPin_, LOW);
  LOG_INFO("Motor inicializado.");
}

void Motor::moveUp() {
  digitalWrite(dirPin_, LOW); // LOW para subir
  isMoving_ = true;
  previousMicros_ = micros();
  togglePulse();
  LOG_INFO("Moviendo hacia arriba.");
}

void Motor::moveDown() {
  digitalWrite(dirPin_, HIGH); // HIGH para bajar
  isMoving_ = true;
  previousMicros_ = micros();
  togglePulse();
  LOG_INFO("Moviendo hacia abajo.");
}

void Motor::stop() {
  if (isMoving_) {
    isMoving_ = false;
    digitalWrite(pulPin_, LOW);
    LOG_INFO("Motor detenido.");
  }
}

void Motor::update() {
  if (isMoving_) {
    unsigned long currentMicros = micros();
    if (currentMicros - previousMicros_ >= pulseInterval_) {
      previousMicros_ = currentMicros;
      togglePulse();
    }
  }
}

void Motor::setPulseInterval(unsigned long interval) {
  pulseInterval_ = interval;
  LOG_INFO("Intervalo de pulsos ajustado.");
}

void Motor::togglePulse() {
  pulseState_ = !pulseState_;
  digitalWrite(pulPin_, pulseState_);
  LOG_DEBUG("Pulso alternado.");
}
