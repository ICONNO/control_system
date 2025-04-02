"""
Run GUI Application Script

This script sets up logging, parses command-line arguments, establishes
a serial connection with the Arduino, and launches the MotorControlGUI.
"""

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
    Set up logging for the application.

    Creates a 'logs' directory if it doesn't exist, and configures both a RotatingFileHandler
    for file logging and a StreamHandler for console output.
    
    :return: None
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
    """
    Main function to start the GUI application.

    Parses command-line arguments, sets up logging, connects to the serial port,
    initializes the GUI, and enters the main loop.
    
    :return: None
    """
    setup_logging()
    parser = argparse.ArgumentParser(description="Stepper Motor Control GUI")
    parser.add_argument('--port', type=str, default='COM3', help="Serial port for Arduino (e.g., COM3)")
    args = parser.parse_args()
    
    serial_comm = SerialInterface(port=args.port)
    logging.info(f"Connecting to serial port {serial_comm.port}.")
    if not serial_comm.connect():
        logging.error("Failed to connect to serial. Exiting.")
        sys.exit(1)
    
    # Create the main window using ttkbootstrap for theming.
    root = ttkb.Window(themename="superhero")
    root.title("Motor and Vacuum Pump Control")
    app = MotorControlGUI(root, serial_comm)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
    
    serial_comm.disconnect()
    logging.info("Application closed successfully.")

if __name__ == "__main__":
    main()
