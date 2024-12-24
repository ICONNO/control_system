# serial_comm.py

import serial
import threading
import time
import logging
from serial import SerialException
import math

class SerialInterface:
    """
    Clase para manejar la comunicación serial real con el Arduino.
    """
    def __init__(self, port='COM3', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.thread = None
        self.running = False
        self.callback = None
        self.lock = threading.Lock()
        self.is_connected = False

    def connect(self):
        """
        Intenta establecer una conexión serial.
        """
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            self.thread = threading.Thread(target=self.read_from_port, daemon=True)
            self.thread.start()
            logging.info(f"Conectado al puerto {self.port} a {self.baudrate} baud.")
            self.is_connected = True
            return True
        except SerialException as e:
            logging.error(f"No se pudo conectar al puerto {self.port}: {e}")
            self.is_connected = False
            return False

    def read_from_port(self):
        """
        Lee continuamente datos del puerto serial en un hilo separado.
        """
        while self.running:
            try:
                if self.serial.in_waiting:
                    line = self.serial.readline().decode('utf-8').strip()
                    if self.callback:
                        self.callback(line)
                time.sleep(0.1)
            except SerialException as e:
                logging.error(f"Error al leer del puerto serial: {e}")
                self.running = False
                if self.callback:
                    self.callback(f"Error en la comunicación serial: {e}")
            except Exception as e:
                logging.error(f"Error inesperado en el hilo serial: {e}")
                self.running = False
                if self.callback:
                    self.callback(f"Error inesperado en el hilo serial: {e}")

    def send_command(self, command):
        """
        Envía un comando al Arduino de manera segura.
        """
        with self.lock:
            try:
                if self.serial and self.serial.is_open:
                    self.serial.write(f"{command}\n".encode())
                    logging.info(f"Comando '{command}' enviado.")
                    return True
                else:
                    logging.warning("Intento de enviar comando cuando la conexión serial está cerrada.")
                    return False
            except SerialException as e:
                logging.error(f"Error al enviar comando '{command}': {e}")
                return False

    def register_callback(self, callback):
        """
        Registra una función de callback para manejar datos recibidos.
        """
        self.callback = callback
        logging.info("Callback para datos recibidos registrado.")

    def disconnect(self):
        """
        Cierra la conexión serial de manera segura.
        """
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        if self.serial and self.serial.is_open:
            self.serial.close()
            logging.info(f"Desconectado del puerto {self.port}.")
            self.is_connected = False


class MockSerialComm:
    """
    Clase de simulación de comunicación serial para pruebas sin hardware.
    """
    def __init__(self):
        self.callback = None
        self.running = False
        self.thread = None

    def connect(self):
        """
        Inicia la simulación de datos seriales.
        """
        self.running = True
        self.thread = threading.Thread(target=self.simulate_data, daemon=True)
        self.thread.start()
        logging.info("Modo simulación activado.")
        return True

    def simulate_data(self):
        """
        Simula el envío de datos seriales.
        """
        while self.running:
            # Simular distancia fluctuante
            distance = 7 + 23 * (1 + math.sin(time.time())) / 2  # Oscila entre 7 y 30 cm
            if self.callback:
                self.callback(f"Distancia actual: {distance:.2f} cm")
            # Simular velocidad fluctuante
            speed = 200 + 1800 * (1 + math.cos(time.time())) / 2  # Oscila entre 200 y 2000 μs
            if self.callback:
                self.callback(f"Velocidad actual: {int(speed)} μs")
            time.sleep(1)  # Simular lectura cada segundo

    def send_command(self, command):
        """
        Simula la recepción y respuesta a comandos.
        """
        logging.info(f"Comando simulado recibido: {command}")
        if self.callback:
            if command.upper() == "AUTO":
                self.callback("Activando modo automático.")
            elif command.upper() == "STOP":
                self.callback("Motor detenido.")
            elif command.upper().startswith("SET_SPEED"):
                partes = command.split()
                if len(partes) == 2 and partes[1].isdigit():
                    velocidad = partes[1]
                    self.callback(f"Intervalo de pulsos ajustado a: {velocidad} μs.")
                else:
                    self.callback("Formato de comando SET_SPEED inválido.")
            elif command.upper() == "PUMP_ON":
                self.callback("Bomba de vacío encendida.")
            elif command.upper() == "PUMP_OFF":
                self.callback("Bomba de vacío apagada.")
            elif command.upper() == "UP":
                self.callback("Moviendo hacia arriba.")
            elif command.upper() == "DOWN":
                self.callback("Moviendo hacia abajo.")
            else:
                self.callback("Comando no reconocido.")

    def register_callback(self, callback):
        """
        Registra una función de callback para manejar datos simulados.
        """
        self.callback = callback
        logging.info("Callback para datos simulados registrado.")

    def disconnect(self):
        """
        Detiene la simulación de datos seriales.
        """
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        logging.info("Modo simulación desactivado.")
