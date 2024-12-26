<<<<<<< HEAD
# Advanced Automated Control System for NEMA 17 Stepper Motor with Ultrasonic Feedback and Python GUI

![Project Logo](https://example.com/logo.png) <!-- Replace with your project logo -->

## Table of Contents

1. [Introduction](#introduction)
2. [Project Background](#project-background)
3. [Features](#features)
4. [System Architecture](#system-architecture)
5. [Hardware Components](#hardware-components)
6. [Software Components](#software-components)
7. [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Hardware Setup](#hardware-setup)
    - [Arduino Firmware Setup](#arduino-firmware-setup)
    - [Python Environment Setup](#python-environment-setup)
8. [Configuration](#configuration)
    - [Arduino Configuration](#arduino-configuration)
    - [Python Configuration](#python-configuration)
9. [Usage](#usage)
    - [Uploading Firmware to Arduino](#uploading-firmware-to-arduino)
    - [Launching the Python GUI](#launching-the-python-gui)
    - [Interacting with the System](#interacting-with-the-system)
10. [Logging and Monitoring](#logging-and-monitoring)
11. [Troubleshooting](#troubleshooting)
12. [Contributing](#contributing)
13. [License](#license)
14. [Acknowledgments](#acknowledgments)
15. [Contact](#contact)

=======
# Control System for NEMA 17 Stepper Motor with TB6560 Driver and HC-SR04 Ultrasonic Sensor
## Table of Contents

>>>>>>> e32da3fb947edebd4f0b71f4c34437d189456b79
---

## Introduction

Welcome to the **Advanced Automated Control System for NEMA 17 Stepper Motor** project. This system integrates a **NEMA 17 Stepper Motor** with a **TB6560 Driver** and an **HC-SR04 Ultrasonic Sensor** to provide precise, automated control based on real-time distance measurements. A **Python-based Graphical User Interface (GUI)** offers an intuitive platform for monitoring and commanding the motor, making the system suitable for applications in robotics, automation, and educational environments.

## Project Background

In the realm of automation and robotics, precise control over actuators is paramount. Traditional systems often lack real-time feedback mechanisms, leading to inefficiencies and inaccuracies. This project aims to bridge that gap by combining robust hardware with an intelligent software interface. By leveraging the capabilities of Arduino for hardware control and Python for software interfacing, we create a versatile system that can adapt to various use cases, from simple motor control to complex automated tasks.

## Features

- **Dual Operation Modes**: Seamlessly switch between automatic and manual control of the stepper motor.
- **Real-Time Ultrasonic Feedback**: Utilize the HC-SR04 sensor to monitor distances and adjust motor actions accordingly.
- **Dynamic Speed Adjustment**: Modify the motor's speed in real-time through the GUI.
- **Comprehensive Logging**: Maintain detailed logs for system operations and debugging purposes.
- **Modular Codebase**: Structured with separate modules for motor control, sensor management, system logic, and GUI operations.
- **Robust Error Handling**: Gracefully manage sensor failures, communication issues, and hardware anomalies.
- **Extensible Design**: Easily integrate additional sensors, actuators, or features in future iterations.

## System Architecture

![System Architecture](https://example.com/architecture.png) <!-- Replace with an actual architecture diagram -->

The system is divided into two main components:

1. **Hardware Component (Arduino-based)**
    - **Motor Control Module**: Manages the NEMA 17 stepper motor via the TB6560 driver.
    - **Sensor Module**: Interfaces with the HC-SR04 ultrasonic sensor to measure distances.
    - **Logic Module**: Implements the state machine controlling motor movements based on sensor input and user commands.
    - **Communication Module**: Handles serial communication with the Python GUI.

2. **Software Component (Python-based GUI)**
    - **User Interface**: Provides an intuitive GUI for monitoring sensor data and controlling motor operations.
    - **Serial Communication**: Facilitates command transmission and data reception between the GUI and Arduino.
    - **Data Visualization**: Utilizes gauges and plots to represent real-time sensor data.
    - **Logging System**: Records events, errors, and system statuses for analysis and debugging.

<<<<<<< HEAD
## Hardware Components

1. **Arduino Uno**: The microcontroller board acts as the central hub for interfacing with sensors and actuators.
2. **NEMA 17 Stepper Motor**: Provides precise rotational control for various applications.
3. **TB6560 Stepper Motor Driver**: Interfaces between the Arduino and the stepper motor, handling high current requirements.
4. **HC-SR04 Ultrasonic Sensor**: Measures distances by emitting ultrasonic waves and calculating the time taken for echoes to return.
5. **Power Supply**: A stable 12V DC power source to drive the stepper motor via the TB6560 driver.
6. **Connecting Wires and Breadboard**: For establishing connections between components.
7. **Optional Components**:
    - **ACS712 Current Sensor**: For monitoring and protecting against overcurrent situations.
    - **Resistors, Capacitors**: As required for sensor stabilization and noise reduction.

## Software Components

1. **Arduino IDE**: For writing, compiling, and uploading firmware to the Arduino Uno.
2. **Visual Studio Code (VSCode)**: Enhanced code editing with extensions for Arduino and Python development.
3. **Python 3.6+**: Programming language for developing the GUI and handling serial communication.
4. **Python Libraries**:
    - `pyserial`: Enables serial communication between Python and Arduino.
    - `matplotlib`: Facilitates data visualization within the GUI.
    - `Tkinter` or `PyQt`: Frameworks for building the graphical user interface.
    - `logging`: Implements logging mechanisms for monitoring and debugging.

## Installation

### Prerequisites

- **Arduino IDE**: [Download Here](https://www.arduino.cc/en/software)
- **Visual Studio Code (VSCode)**: [Download Here](https://code.visualstudio.com/)
- **Python 3.6+**: [Download Here](https://www.python.org/downloads/)
- **Python Libraries**: Install via `pip`
    ```bash
    pip install -r requirements.txt
    ```
- **VSCode Extensions**:
    - **Arduino for VSCode**
    - **Python**
    - **C/C++**

### Hardware Setup

1. **Connect the Stepper Motor to TB6560 Driver**:
    - **Motor Wires**: Connect according to the motor's datasheet.
    - **Power Supply**: Ensure the TB6560 is connected to a stable 12V DC power source.
    - **Control Pins**: Connect the TB6560's Pulse and Direction pins to Arduino Digital Pins 3 and 4, respectively.

2. **Connect HC-SR04 Ultrasonic Sensor to Arduino**:
    - **VCC**: Connect to 5V on Arduino.
    - **GND**: Connect to GND on Arduino.
    - **Trig**: Connect to Digital Pin 9 on Arduino.
    - **Echo**: Connect to Digital Pin 10 on Arduino.

3. **Optional: Connect ACS712 Current Sensor**:
    - **VCC**: Connect to 5V on Arduino.
    - **GND**: Connect to GND on Arduino.
    - **OUT**: Connect to Analog Pin A0 on Arduino.

4. **Finalize Connections**:
    - Double-check all wiring against the `Config.h` pin definitions.
    - Ensure all connections are secure to prevent short circuits.

### Arduino Firmware Setup

1. **Open the Project in VSCode**:
    - Launch VSCode and open the `control_system/` directory.

2. **Configure VSCode for Arduino**:
    - Ensure the Arduino extension is installed and properly configured.
    - Open `.vscode/arduino.json` and verify:
        - `"sketch"` points to `lineal_actuator/lineal_actuator.ino`.
        - `"board"` is set to your Arduino model (e.g., `"arduino:avr:uno"`).
        - `"port"` matches your Arduino's serial port (e.g., `"COM3"` on Windows or `"/dev/ttyACM0"` on Linux).

3. **Configure `c_cpp_properties.json`**:
    - Ensure the `includePath` includes `"${workspaceFolder}/**"` to allow VSCode to find all header files.
    - Example configuration:
        ```json
        {
            "configurations": [
                {
                    "name": "Arduino",
                    "includePath": [
                        "${workspaceFolder}/**",
                        "${env:ARDUINO_HOME}/libraries/**"
                    ],
                    "defines": [
                        "USBCON"
                    ],
                    "compilerPath": "/usr/bin/avr-gcc",
                    "cStandard": "c11",
                    "cppStandard": "c++17",
                    "intelliSenseMode": "gcc-x64"
                }
            ],
            "version": 4
        }
        ```

4. **Verify and Upload Firmware**:
    - Click the `Verify` (✓) button in the Arduino toolbar within VSCode.
    - Ensure there are no compilation errors.
    - Click the `Upload` (→) button to upload the firmware to the Arduino Uno.
    - Monitor the output for any compilation or upload errors.

### Python Environment Setup

1. **Navigate to the Project Directory**:
    ```bash
    cd path/to/control_system/
    ```

2. **Create and Activate a Virtual Environment (Optional but Recommended)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Required Python Libraries**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure all dependencies are listed in `requirements.txt`)*

4. **Configure `serial_comm.py`**:
    - Open `gui/serial_comm.py`.
    - Set the correct serial port matching your Arduino's connection.
    ```python
    # serial_comm.py

    serial_port = 'COM3'  # Replace with your Arduino's serial port (e.g., '/dev/ttyACM0' on Linux)
    baudrate = 9600
    timeout = 1
    ```

## Configuration

=======
>>>>>>> e32da3fb947edebd4f0b71f4c34437d189456b79
### Arduino Configuration

All configurable parameters are centralized in the `Config.h` file located in the `lineal_actuator/` directory. Adjust these parameters as needed to match your hardware setup and operational requirements.

#### Key Configuration Parameters

- **Pin Definitions**:
    ```cpp
    // Config.h

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

#### Serial Communication Configuration

- **Serial Port**: Ensure `serial_port` in `serial_comm.py` matches your Arduino's connection.
    ```python
    # serial_comm.py

    serial_port = 'COM3'  # Replace with your Arduino's serial port (e.g., '/dev/ttyACM0' on Linux)
    baudrate = 9600
    timeout = 1
    ```

#### Logging Configuration

- **Logging Levels**: Adjust logging levels in `logging_config.py` to control the verbosity of logs.
    ```python
    # logging_config.py

    import logging

    logging.basicConfig(
        filename='logs/app.log',
        level=logging.DEBUG,  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    ```

<<<<<<< HEAD
#### GUI Customization

- **Styles**: Modify `styles.py` to change the appearance of the GUI elements.
- **Visualization**: Adjust `matplotlib_gauge.py` to alter gauge styles or add new visual components.

## Usage

### Uploading Firmware to Arduino

1. **Connect Arduino to PC**:
    - Use a USB cable to connect your Arduino Uno to your computer.

2. **Open VSCode and Project**:
    - Launch VSCode.
    - Open the `control_system/` directory.

3. **Verify and Upload**:
    - Click the `Verify` (✓) button in the Arduino toolbar to compile the firmware.
    - Ensure there are no compilation errors.
    - Click the `Upload` (→) button to upload the firmware to the Arduino Uno.
    - Monitor the output for any compilation or upload errors.

4. **Monitor Serial Output (Optional)**:
    - Open the Serial Monitor in VSCode or use an external tool like `PuTTY` or `minicom`.
    - Ensure the baud rate is set to `9600` to view real-time logs from Arduino.

### Launching the Python GUI

1. **Ensure Arduino is Running**:
    - Confirm that the Arduino is powered on and the firmware is uploaded.

2. **Open Terminal in VSCode**:
    - Navigate to the `control_system/` directory.

3. **Activate Virtual Environment (If Created)**:
    ```bash
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4. **Run the GUI Application**:
    ```bash
    python run_gui.py
    ```
    - Alternatively, if `motor_control_gui.py` is the main GUI script, execute:
    ```bash
    python motor_control_gui.py
    ```

5. **Interact with the GUI**:
    - **Automatic Mode**: Click the `AUTO` button to start automatic motor movements based on sensor input.
    - **Manual Control**: Use the `UP`, `DOWN`, and `STOP` buttons to control motor direction manually.
    - **Adjust Speed**: Input a value in the `SET_SPEED` field and apply to modify motor speed dynamically.
    - **Monitor Distance**: View real-time distance measurements displayed on visual gauges within the GUI.

### Interacting with the System

- **Sending Commands via GUI**:
    - Use the GUI buttons and input fields to send commands directly to the Arduino.
    - Commands include `AUTO`, `UP`, `DOWN`, `STOP`, and `SET_SPEED <value>`.

- **Sending Commands via Serial**:
    - Use the Serial Monitor or other serial communication tools to send text-based commands.
    - Ensure commands are terminated with a newline character (`\n`).

- **Receiving Feedback**:
    - The system provides real-time feedback through logs displayed in the GUI and recorded in log files.
    - Monitor logs to verify system behavior and debug issues.

## Logging and Monitoring

### Arduino Logging

- **Log Messages**: Arduino sends log messages via Serial at a baud rate of `9600`.
- **Log Levels**:
    - **ERROR**: Critical issues requiring immediate attention.
    - **INFO**: General system information and status updates.
    - **DEBUG**: Detailed information useful for debugging.
- **Adjusting Verbosity**: Set `LOG_VERBOSITY` in `Config.h` to control the level of log messages.
    ```cpp
    #define LOG_VERBOSITY 2 // 0: Off, 1: Error, 2: Info, 3: Debug
    ```

### Python Logging

- **Log Files**: All Python logs are stored in `logs/app.log`.
- **Log Levels**:
    - **DEBUG**: Detailed information for debugging.
    - **INFO**: Confirmation that things are working as expected.
    - **WARNING**: Indications of potential issues.
    - **ERROR**: Serious problems preventing some functionality.
    - **CRITICAL**: Severe errors causing program termination.
- **Viewing Logs**:
    - Open `logs/app.log` with any text editor to review historical logs.
    - Logs are also output to the console during runtime for real-time monitoring.

## Troubleshooting

### Common Issues and Solutions

1. **Arduino Compilation Errors**:
    - **Cause**: Missing or incorrectly placed header/source files.
    - **Solution**: Ensure all modules (`Motor.h`, `Motor.cpp`, `Sensor.h`, `Sensor.cpp`, `Logic.h`, `Logic.cpp`) are correctly placed in the `lineal_actuator/` directory and properly included in `lineal_actuator.ino`.

2. **Serial Communication Issues**:
    - **Cause**: Incorrect serial port or baud rate settings.
    - **Solution**:
        - Verify that `serial_comm.py` points to the correct serial port.
        - Ensure the baud rate in `serial_comm.py` matches the Arduino's baud rate (`9600`).
        - Check that no other application is using the serial port.

3. **GUI Not Responding or Crashing**:
    - **Cause**: Unhandled exceptions or incorrect GUI configurations.
    - **Solution**:
        - Check `logs/app.log` for error messages.
        - Ensure all required Python libraries are installed and up-to-date.
        - Verify that the Python scripts are free of syntax errors.

4. **Motor Not Moving**:
    - **Cause**: Incorrect wiring, insufficient power, or code issues.
    - **Solution**:
        - Double-check all motor and driver connections.
        - Ensure the power supply provides adequate current.
        - Review motor control logic in the Arduino code.

5. **Ultrasonic Sensor Not Reading Correctly**:
    - **Cause**: Incorrect sensor placement, wiring issues, or environmental factors.
    - **Solution**:
        - Ensure the sensor is properly connected and mounted.
        - Test the sensor independently using a simple Arduino sketch to verify functionality.
        - Check for obstacles or interference in the sensor's environment.

6. **Overcurrent Protection Not Triggering**:
    - **Cause**: Faulty current sensor or incorrect integration.
    - **Solution**:
        - Verify the current sensor connections.
        - Ensure the current thresholds are correctly set in the Arduino code.
        - Test the current sensor separately to confirm functionality.

### Debugging Steps

1. **Isolate Components**:
    - Test each component (motor, sensor, GUI) individually to identify the source of the problem.

2. **Use Serial Logs**:
    - Utilize Arduino's Serial Monitor to view real-time logs and identify issues.

3. **Check Power Supply**:
    - Ensure the power supply is stable and meets the current requirements of the motor and driver.

4. **Review Wiring**:
    - Double-check all physical connections against the pin definitions in `Config.h`.

5. **Update Firmware and Libraries**:
    - Ensure both Arduino firmware and Python libraries are up-to-date to avoid compatibility issues.

6. **Monitor Log Files**:
    - Review `logs/app.log` for detailed error messages and system statuses.


---

*This project is a work in progress. Contributions and feedback are highly appreciated to improve its functionality and robustness.*
=======
- **GUI Customization**:
    - Modify `styles.py` to change the appearance of the GUI.
    - Update `matplotlib_gauge.py` for different gauge styles or additional visualizations.
>>>>>>> e32da3fb947edebd4f0b71f4c34437d189456b79
