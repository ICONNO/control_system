import serial
import serial.tools.list_ports
import threading
import time
import logging

class SerialInterface:
    """
    Maneja la comunicación serial con el Arduino utilizando el protocolo binario.
    """
    def __init__(self, port='COM3', baudrate=115200):
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
            logging.info(f"Conectado al puerto {self.port} a {self.baudrate} bps.")
            return True
        except serial.SerialException as e:
            logging.error(f"Error al conectar al puerto {self.port}: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        self.stop_thread = True
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logging.info(f"Puerto {self.port} cerrado.")
        self.is_connected = False

    def register_callback(self, callback):
        self.callback = callback

    def read_from_port(self):
        while not self.stop_thread:
            try:
                # Para el protocolo binario leemos 2 bytes a la vez
                if self.serial_conn.in_waiting >= 2:
                    packet = self.serial_conn.read(2)
                    if self.callback:
                        # La callback recibe el paquete en formato bytes
                        self.callback(packet)
                time.sleep(0.05)
            except Exception as e:
                logging.error(f"Error al leer puerto serial: {e}")
                self.is_connected = False
                break

    def send_command(self, cmd_byte, payload_byte):
        if self.is_connected and self.serial_conn:
            try:
                packet = bytes([cmd_byte, payload_byte])
                self.serial_conn.write(packet)
                logging.debug(f"Enviado: {packet}")
                return True
            except Exception as e:
                logging.error(f"Error al enviar {packet}: {e}")
                self.is_connected = False
                return False
        else:
            logging.error("No hay conexión serial para enviar comando.")
            return False

class MockSerialComm:
    """
    Simula la comunicación serial (modo mock).
    """
    def __init__(self):
        self.is_connected = False
        self.callback = None
        self.thread = None
        self.stop_thread = False

    def connect(self):
        self.is_connected = True
        self.stop_thread = False
        self.thread = threading.Thread(target=self.mock_read, daemon=True)
        self.thread.start()
        logging.info("Modo mock: Conexión establecida.")
        return True

    def disconnect(self):
        self.stop_thread = True
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.is_connected = False
        logging.info("Modo mock: Conexión cerrada.")

    def register_callback(self, callback):
        self.callback = callback

    def mock_read(self):
        while not self.stop_thread:
            if self.callback:
                # Simula un mensaje (en este caso, simplemente enviamos 2 bytes de ejemplo)
                self.callback(bytes([0x00, 0x00]))
            time.sleep(2)

    def send_command(self, cmd_byte, payload_byte):
        logging.info(f"(Mock) Enviado: {[hex(cmd_byte), hex(payload_byte)]}")
        if self.callback:
            self.callback(bytes([cmd_byte, payload_byte]))
        return True
