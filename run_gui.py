import argparse
import sys
import tkinter as tk
import ttkbootstrap as ttkb
from gui import MotorControlGUI
from gui.serial_comm import SerialInterface
import logging
import os

def setup_logging():
    """
    Configura el sistema de logging para la aplicación.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    from logging.handlers import RotatingFileHandler
    handler = RotatingFileHandler("logs/app.log", maxBytes=5*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Control de Motor Paso a Paso con GUI")
    parser.add_argument('--port', type=str, default='COM3', help="Puerto serial al que está conectado el Arduino (ej. COM3)")
    args = parser.parse_args()
    serial_comm = SerialInterface(port=args.port)
    logging.info(f"Conectando a puerto serial {serial_comm.port}.")
    if not serial_comm.connect():
        logging.error("No se pudo establecer conexión serial. Saliendo.")
        sys.exit(1)
    root = ttkb.Window(themename="superhero")
    root.title("Control de Motor y Estado de la Máquina")
    app = MotorControlGUI(root, serial_comm)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
    serial_comm.disconnect()
    logging.info("Aplicación cerrada correctamente.")

if __name__ == "__main__":
    main()
