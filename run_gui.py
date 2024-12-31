# run_gui.py

import argparse
import sys
import tkinter as tk
from gui import MotorControlGUI
from gui.serial_comm import SerialInterface, MockSerialComm
import logging
import os

def setup_logging():
    """
    Configura el sistema de logging para la aplicación.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    # Configurar logging
    setup_logging()

    # Configuración de Argumentos de Línea de Comandos
    parser = argparse.ArgumentParser(description="Control de Motor Paso a Paso con GUI")
    parser.add_argument('--mode', choices=['real', 'mock'], default='real', help="Modo de operación: real o mock (simulación)")
    parser.add_argument('--port', type=str, default='COM3', help="Puerto serial al que está conectado el Arduino (ej. COM3)")
    args = parser.parse_args()

    # Seleccionar el tipo de comunicación serial
    if args.mode == 'real':
        serial_comm = SerialInterface(port=args.port)
        logging.info(f"Seleccionado modo real en puerto {args.port}.")
    else:
        serial_comm = MockSerialComm()
        logging.info("Seleccionado modo simulación.")

    # Intentar conectar en modo real
    if args.mode == 'real' and not serial_comm.connect():
        logging.error("No se pudo establecer conexión serial. Cambiando a modo simulación.")
        serial_comm = MockSerialComm()
        serial_comm.connect()

    # Inicializar la GUI
    root = tk.Tk()
    root.title("Control de Motor y Bomba de Vacío")
    app = MotorControlGUI(root, serial_comm)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Asegurar que on_closing se llama al cerrar
    root.mainloop()

    # Cerrar conexión serial al cerrar la aplicación
    serial_comm.disconnect()
    logging.info("Aplicación cerrada correctamente.")

if __name__ == "__main__":
    main()
