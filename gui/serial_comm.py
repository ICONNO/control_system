"""
Serial Communication Module

Handles the serial communication between the GUI and the Arduino.
Provides functions for connecting, disconnecting, reading, and sending commands.

Classes:
    SerialInterface: Manages the serial connection and communication.
"""

import serial
import serial.tools.list_ports
import threading
import time
import logging

class SerialInterface:
    """
    Handles serial communication with the Arduino.

    Attributes:
        port (str): The serial port identifier (e.g., "COM3").
        baudrate (int): The communication speed in baud.
        serial_conn: The serial connection object.
        is_connected (bool): Connection status.
        callback: Function to call when new data is received.
        read_thread: Thread for continuously reading data.
        stop_thread (bool): Flag to stop the reading thread.
    """
    def __init__(self, port='COM3', baudrate=9600):
        """
        Initializes the SerialInterface with the given port and baudrate.

        :param port: Serial port identifier.
        :param baudrate: Communication baud rate.
        """
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        self.is_connected = False
        self.callback = None
        self.read_thread = None
        self.stop_thread = False

    def connect(self):
        """
        Establishes a serial connection to the specified port.

        :return: True if connected successfully, False otherwise.
        """
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.is_connected = True
            self.stop_thread = False
            self.read_thread = threading.Thread(target=self.read_from_port, daemon=True)
            self.read_thread.start()
            logging.info(f"Connected to serial port {self.port} at {self.baudrate} bps.")
            return True
        except serial.SerialException as e:
            logging.error(f"Serial connection error on {self.port}: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """
        Closes the serial connection and stops the reading thread.
        """
        self.stop_thread = True
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            logging.info(f"Serial port {self.port} closed.")
        self.is_connected = False

    def register_callback(self, callback):
        """
        Registers a callback function to be called upon receiving serial data.

        :param callback: Function that takes a string argument.
        """
        self.callback = callback

    def read_from_port(self):
        """
        Continuously reads data from the serial port and invokes the callback.
        """
        while not self.stop_thread:
            try:
                if self.serial_conn.in_waiting:
                    data = self.serial_conn.readline().decode('utf-8').strip()
                    if self.callback:
                        self.callback(data)
                time.sleep(0.1)
            except Exception as e:
                logging.error(f"Serial read error: {e}")
                self.is_connected = False
                break

    def send_command(self, command):
        """
        Sends a command string to the Arduino via the serial port.

        :param command: Command string to send.
        :return: True if the command is sent successfully, False otherwise.
        """
        if self.is_connected and self.serial_conn:
            try:
                self.serial_conn.write(f"{command}\n".encode('utf-8'))
                logging.debug(f"Command sent: {command}")
                return True
            except Exception as e:
                logging.error(f"Error sending command '{command}': {e}")
                self.is_connected = False
                return False
        else:
            logging.error("Attempt to send command without serial connection.")
            return False
