# Control System for NEMA 17 Stepper Motor with TB6560 Driver and HC-SR04 Ultrasonic Sensor
## Table of Contents

---

## Project Overview

This project implements a comprehensive control system for a **NEMA 17 Stepper Motor** using an **TB6560 Driver** and an **HC-SR04 Ultrasonic Sensor**. The system facilitates both automatic and manual control modes, allowing precise motor movements based on real-time distance measurements. A **Python-based Graphical User Interface (GUI)** provides an intuitive platform for users to interact with the system, monitor sensor data, and issue control commands seamlessly.

**Key Objectives:**

- Automate motor movements between predefined positions using sensor feedback.
- Enable manual control of motor direction and speed via a user-friendly GUI.
- Implement robust error handling and logging mechanisms for reliable operation.
- Maintain a modular and scalable codebase for easy maintenance and future enhancements.

## Features

- **Automatic Mode**: Motor moves downward until a distance of 7 cm is detected, then moves upward until a distance of 35 cm is reached, repeating this cycle indefinitely.
- **Manual Mode**: Users can manually command the motor to move up, down, or stop via the Python GUI or serial commands.
- **Real-Time Monitoring**: Live distance measurements are displayed on the GUI using visual gauges.
- **Adjustable Motor Speed**: Users can modify the motor's speed dynamically through the GUI.
- **Error Handling**: The system gracefully handles sensor read failures and communication issues.
- **Logging System**: Comprehensive logging for both Arduino and Python components to facilitate debugging and monitoring.
- **Modular Architecture**: Well-organized codebase with separate modules for motor control, sensor management, system logic, and GUI operations.
- **Extensible Design**: Easy integration of additional sensors, actuators, or features in the future.

### Arduino Configuration

All configurable parameters are centralized in the `Config.h` file within the `lineal_actuator/` directory. Adjust the following as needed:

- **Pin Definitions**:
    ```cpp
    // Pines del Motor Paso a Paso con TB6560
    const uint8_t MOTOR_PUL_PIN = 3;        // Pin para el pulso
    const uint8_t MOTOR_DIR_PIN = 4;        // Pin para la dirección

    // Pines del Sensor Ultrasónico HC-SR04
    const uint8_t SENSOR_TRIG_PIN = 9;      // Pin de Trigger
    const uint8_t SENSOR_ECHO_PIN = 10;     // Pin de Echo
    ```

- **System Parameters**:
    ```cpp
    // Distancias objetivo (en centímetros)
    const float DISTANCE_LOWER_TARGET = 7.0;     // Distancia para detenerse al bajar
    const float DISTANCE_UPPER_TARGET = 35.0;    // Distancia para detenerse al subir
    const float DISTANCE_MARGIN = 0.5;           // Margen para evitar oscilaciones

    // Velocidad del Motor
    const unsigned long PULSE_INTERVAL_DEFAULT_US = 800; // Intervalo entre pulsos en micros (ajustar para la velocidad)
    unsigned long pulseInterval = PULSE_INTERVAL_DEFAULT_US;

    // Intervalo de lectura del sensor ultrasónico
    const unsigned long SENSOR_READ_INTERVAL_MS = 100; // Intervalo entre mediciones en milisegundos

    // Timeout para la lectura del sensor ultrasónico
    const unsigned long ULTRASONIC_TIMEOUT_US = 30000; // Timeout en micros (30 ms)
    ```

- **Logging Configuration**:
    ```cpp
    #define LOG_VERBOSITY 2 // 0: Off, 1: Error, 2: Info, 3: Debug

    #if LOG_VERBOSITY >= 1
      #define LOG_ERROR(msg) Serial.println(F(msg))
    #else
      #define LOG_ERROR(msg)
    #endif

    #if LOG_VERBOSITY >= 2
      #define LOG_INFO(msg) Serial.println(F(msg))
    #else
      #define LOG_INFO(msg)
    #endif

    #if LOG_VERBOSITY >= 3
      #define LOG_DEBUG(msg) Serial.println(F(msg))
    #else
      #define LOG_DEBUG(msg)
    #endif
    ```

### Python Configuration

Configuration settings for the Python GUI and serial communication are managed within the Python scripts, primarily in `serial_comm.py` and `run_gui.py`.

- **Serial Port Configuration**:
    - Edit `serial_comm.py` to specify the correct serial port.
    ```python
    # serial_comm.py

    serial_port = 'COM3'  # Replace with your Arduino's serial port (e.g., 'COM3' on Windows or '/dev/ttyACM0' on Linux)
    baudrate = 9600
    timeout = 1
    ```

- **Logging Configuration**:
    - Adjust logging levels and log file paths in `logging_config.py`.
    ```python
    # logging_config.py

    import logging

    logging.basicConfig(
        filename='logs/app.log',
        level=logging.DEBUG,  # Adjust as needed: DEBUG, INFO, WARNING, ERROR, CRITICAL
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    ```

- **GUI Customization**:
    - Modify `styles.py` to change the appearance of the GUI.
    - Update `matplotlib_gauge.py` for different gauge styles or additional visualizations.
