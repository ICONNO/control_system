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
        """
        Establece la conexión serial.
        """
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
        """
        Cierra la conexión serial.
        """
        self.stop_thread = True
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logging.info(f"Conexión serial {self.port} cerrada.")
        self.is_connected = False

    def register_callback(self, callback):
        """
        Registra una función de callback para manejar datos recibidos.
        """
        self.callback = callback

    def read_from_port(self):
        """
        Lee datos desde el puerto serial y los envía al callback.
        """
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
        """
        Envía un comando al Arduino.
        """
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

class MockSerialComm:
    """
    Clase para simular la comunicación serial (modo mock).
    """
    def __init__(self):
        self.is_connected = False
        self.callback = None
        self.thread = None
        self.stop_thread = False

    def connect(self):
        """
        Simula la conexión serial.
        """
        self.is_connected = True
        self.stop_thread = False
        self.thread = threading.Thread(target=self.mock_read, daemon=True)
        self.thread.start()
        logging.info("Modo simulación: Conexión mock establecida.")
        return True

    def disconnect(self):
        """
        Simula el cierre de la conexión serial.
        """
        self.stop_thread = True
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.is_connected = False
        logging.info("Modo simulación: Conexión mock cerrada.")

    def register_callback(self, callback):
        """
        Registra una función de callback para manejar datos simulados.
        """
        self.callback = callback

    def mock_read(self):
        """
        Simula la lectura de datos desde el Arduino.
        """
        while not self.stop_thread:
            simulated_distance = 25
            simulated_speed = 800
            if self.callback:
                self.callback(f"Distancia actual: {simulated_distance} cm")
                self.callback(f"Velocidad actual: {simulated_speed} μs")
            time.sleep(2)

    def send_command(self, command):
        """
        Simula el envío de un comando al Arduino.
        """
        logging.info(f"Modo simulación: Comando recibido '{command}'")
        if self.callback:
            if command == "AUTO":
                self.callback("Activando modo automático.")
            elif command == "STOP":
                self.callback("Desactivando modo automático.")
                self.callback("Motor detenido.")
            elif command.startswith("SET_SPEED"):
                speed = command.split(" ")[1]
                self.callback(f"Velocidad actual: {speed} μs")
            elif command == "PUMP_ON":
                self.callback("Bomba de vacío encendida.")
            elif command == "PUMP_OFF":
                self.callback("Bomba de vacío apagada.")
            elif command == "UP":
                self.callback("Moviendo hacia arriba.")
            elif command == "DOWN":
                self.callback("Moviendo hacia abajo.")
            else:
                self.callback(f"Comando desconocido: {command}")
        return True
