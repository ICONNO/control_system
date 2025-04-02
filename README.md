# Control System Project

This repository contains the source code and documentation for the Control System project, which controls linear actuators using an Arduino-based firmware, a Python-based GUI, and remote capture utilities.

## Table of Contents

- [Overview](#overview)
- [Usage](#usage)
- [Running the Wiki](#running-the-wiki)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)

## Overview

The Control System is designed to provide precise control over linear actuators. It integrates multiple subsystems, including:
- **Firmware (Arduino):** Manages motor control, sensor readings, and system logic.
- **GUI (Python):** Provides a graphical user interface for manual/auto control and system monitoring.
- **Remote Capture:** Allows remote image capture via SSH.
- **Hardware Components:** Detailed in the documentation.

For more details, see our [Wiki](./typescript-wiki/docs/intro.md).

## Usage

### Firmware

1. **Setup Hardware:**  
   Connect the components as specified in `lineal_actuator/config.h`.
2. **Compile and Upload:**  
   Open `lineal_actuator/lineal_actuator.ino` in the Arduino IDE, install required libraries (e.g., AccelStepper), compile, and upload the firmware to the Arduino UNO R3.

### GUI

1. **Setup Python Environment:**  
   Ensure you have Python 3.11 or later installed.
2. **Install Dependencies:**  
   Navigate to the `gui/` directory and run:
   ```bash
   pip install -r requirements.txt
