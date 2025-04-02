# Control System Project

Este repositorio contiene el firmware para Arduino, la GUI en Python y la documentación (wiki) del Control System.

## Contenido

- **Firmware (lineal_actuator):** Control del motor, sensores y lógica.
- **GUI (gui):** Interfaz gráfica para control manual/automático y monitoreo.
- **Wiki (typescript-wiki):** Documentación completa con Docusaurus.

## Requisitos

- **Hardware:** Arduino UNO R3, motor paso a paso con driver TB6560, sensor ultrasónico, bomba VN-CE, fuente LRS-350-12, Raspberry Pi 5, cámaras ARDUCAM Hawkeye.
- **Software:** Arduino IDE, Python 3.11+, Node.js y npm.

## Uso

### Firmware
1. Conecta el hardware según `lineal_actuator/config.h`.
2. Abre `lineal_actuator/lineal_actuator.ino` en el Arduino IDE, compila y sube.

### GUI
1. Navega a la carpeta `gui/` y ejecuta:
   ```bash
   pip install -r requirements.txt
   python run_gui.py --port COM3


### Wiki
1. Navega a la carpeta `typescript-wiki/` y ejecuta:
   ```bash
   npm install
   npm start
   ```
2. Abre `http://localhost:3000` en tu navegador web.

