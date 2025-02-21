import serial
import serial.tools.list_ports
import threading
import time
import logging

class SerialInterface:
    """
    Clase para manejar la comunicación serial con el Arduino.
    """
    def __init__(self, port='COM3', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_connected = False
        self.callback = None
        self.read_thread = None
        self.stop_thread = False

    def connect(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_connected = True
            self.stop_thread = False
            self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
            self.read_thread.start()
            logging.info(f"Conectado al puerto serial {self.port} a {self.baudrate} bps.")
            return True
        except serial.SerialException as e:
            logging.error(f"Error al conectar al puerto serial {self.port}: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        self.stop_thread = True
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logging.info(f"Conexión serial {self.port} cerrada.")
        self.is_connected = False

    def register_callback(self, callback):
        self.callback = callback

    def read_from_port(self):
        while not self.stop_thread:
            try:
                if self.serial_conn.in_waiting:
                    data = self.serial_conn.readline().decode('utf-8').strip()
                    if self.callback:
                        self.callback(data)
                time.sleep(0.1)
            except Exception as e:
                logging.error(f"Error al leer desde el puerto serial: {e}")
                self.is_connected = False
                break

    def send_command(self, command):
        if self.is_connected and self.serial_conn:
            try:
                self.serial_conn.write(f"{command}\n".encode('utf-8'))
                logging.debug(f"Comando enviado: {command}")
                return True
            except Exception as e:
                logging.error(f"Error al enviar comando '{command}': {e}")
                self.is_connected = False
                return False
        else:
            logging.error("Intento de enviar comando sin conexión serial.")
            return False
