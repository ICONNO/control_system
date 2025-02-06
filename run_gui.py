import argparse
import sys
import tkinter as tk
import ttkbootstrap as ttkb
from gui import MotorControlGUI
from gui.serial_comm import SerialInterface
import logging
import os

def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    from logging.handlers import RotatingFileHandler
    handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=5*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Control de Motor y Bomba de Vacío con GUI")
    parser.add_argument('--mode', choices=['real', 'mock'], default='real', help="Modo de operación (solo real se usará)")
    parser.add_argument('--port', type=str, default='COM3', help="Puerto serial (ej. COM3)")
    args = parser.parse_args()

    # En modo real, siempre usamos SerialInterface con 115200 baudios
    serial_comm = SerialInterface(port=args.port, baudrate=115200)
    logging.info(f"Modo real en puerto {serial_comm.port}.")
    
    if not serial_comm.connect():
        logging.error("No se pudo establecer conexión serial. Finalizando.")
        sys.exit(1)
    
    root = ttkb.Window(themename="superhero")
    root.title("Control de Motor y Bomba de Vacío")
    app = MotorControlGUI(root, serial_comm)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
    serial_comm.disconnect()
    logging.info("Aplicación cerrada correctamente.")

if __name__ == "__main__":
    main()
