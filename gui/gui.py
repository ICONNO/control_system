# gui/gui.py

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import threading
import time
import logging
import queue
import psutil
from typing import Callable, Optional
from .serial_comm import SerialInterface, MockSerialComm  # Ensure these modules are implemented
from .styles import set_styles  # Import the styles function if available


# ------------------- Logging Configuration -------------------
# Configure logging once to prevent multiple handlers if multiple instances are created
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Create a logger for the application
logger = logging.getLogger(__name__)
# -------------------------------------------------------------


class CreateToolTip:
    """
    A class to create a tooltip for a given widget.

    Attributes
    ----------
    widget : tk.Widget
        The widget to attach the tooltip to.
    text : str
        The text to display in the tooltip.
    waittime : int
        Time in milliseconds before the tooltip appears.
    wraplength : int
        The maximum line length for the tooltip text.
    tw : Optional[tk.Toplevel]
        The tooltip window, if currently displayed.
    id : Optional[str]
        The identifier for the scheduled tooltip display.
    """

    def __init__(self, widget: tk.Widget, text: str = 'widget info') -> None:
        """
        Initializes the CreateToolTip instance.

        Parameters
        ----------
        widget : tk.Widget
            The widget to attach the tooltip to.
        text : str, optional
            The text to display in the tooltip (default is 'widget info').
        """
        self.waittime = 500  # milliseconds
        self.wraplength = 180  # text wrap length in pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event: Optional[tk.Event] = None) -> None:
        """Schedules the tooltip to be displayed after waittime."""
        self.schedule()

    def leave(self, event: Optional[tk.Event] = None) -> None:
        """Unschedules and hides the tooltip."""
        self.unschedule()
        self.hidetip()

    def schedule(self) -> None:
        """Schedules the tooltip to be shown after waittime."""
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self) -> None:
        """Cancels the scheduled tooltip display."""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self, event: Optional[tk.Event] = None) -> None:
        """
        Displays the tooltip near the widget.

        Parameters
        ----------
        event : Optional[tk.Event], optional
            The event that triggered the tooltip (default is None).
        """
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # Create a Toplevel window for the tooltip
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)  # Remove window decorations
        self.tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.tw,
            text=self.text,
            justify='left',
            background="#2e2e2e",
            foreground="#ffffff",
            relief='solid',
            borderwidth=1,
            wraplength=self.wraplength
        )
        label.pack(ipadx=1)

    def hidetip(self) -> None:
        """Destroys the tooltip window if it exists."""
        if self.tw:
            self.tw.destroy()
            self.tw = None


class MotorControlGUI:
    """
    The main class for the motor control graphical user interface.

    This class creates the GUI, handles user interactions, communicates with the serial device,
    manages command queues, and monitors system health.

    Attributes
    ----------
    master : tk.Tk
        The root window of the Tkinter application.
    serial : SerialInterface
        The serial communication interface with the Arduino.
    mode : tk.StringVar
        The current mode of operation ('Manual' or 'Automático').
    current_distance : tk.StringVar
        The current distance reading from the Arduino.
    pulse_interval : tk.IntVar
        The current pulse interval value.
    system_status : tk.StringVar
        The current system status.
    up_pressed : bool
        Indicates if the 'Up' button is pressed.
    down_pressed : bool
        Indicates if the 'Down' button is pressed.
    queue : queue.Queue
        Queue for handling serial data.
    command_queue : queue.Queue
        Queue for handling commands to send to the serial device.
    command_lock : threading.Lock
        Lock for thread-safe access to the command queue.
    last_command_time : float
        Timestamp of the last command sent.
    command_throttle : float
        Minimum interval between sending commands (in seconds).
    system_health : float
        Represents the overall health of the system.
    error_count : int
        Counts consecutive command errors.
    last_error_time : float
        Timestamp of the last error occurrence.
    reconnect_attempts : int
        Number of attempts made to reconnect to the serial device.
    command_thread : threading.Thread
        Thread responsible for processing the command queue.
    """

    def __init__(self, master: tk.Tk, serial_comm: SerialInterface) -> None:
        """
        Initializes the MotorControlGUI instance.

        Parameters
        ----------
        master : tk.Tk
            The root window of the Tkinter application.
        serial_comm : SerialInterface
            The serial communication interface with the Arduino.
        """
        self.master = master
        self.serial = serial_comm
        self.serial.register_callback(self.enqueue_serial_data)

        # Apply ttkbootstrap theme
        self.style = ttkb.Style(theme='superhero')  # Other themes: 'darkly', 'cyborg', etc.

        # Log initialization
        logger.info("Initializing the GUI interface.")

        # State variables
        self.mode = tk.StringVar(value="Manual")
        self.current_distance = tk.StringVar(value="Desconocida")
        self.pulse_interval = tk.IntVar(value=800)  # Initial value consistent with label
        self.system_status = tk.StringVar(
            value="Operando en Modo Real" if self.serial.is_connected else "Modo Simulación"
        )

        # Button state tracking
        self.up_pressed = False
        self.down_pressed = False

        # Queue for inter-thread communication
        self.queue = queue.Queue()

        # Apply custom styles if available
        set_styles()

        # Create GUI widgets
        self.create_widgets()

        # Start processing the serial data queue
        self.master.after(100, self.process_queue)

        logger.info("GUI interface initialized successfully.")

        # Command queue and thread safety
        self.command_queue = queue.Queue()
        self.command_lock = threading.Lock()
        self.last_command_time = 0.0
        self.command_throttle = 0.1  # seconds

        # System monitoring variables
        self.system_health = 100.0
        self.error_count = 0
        self.last_error_time = 0.0
        self.reconnect_attempts = 0

        # Event to signal the command thread to stop
        self.stop_event = threading.Event()

        # Start command processor thread
        self.command_thread = threading.Thread(target=self.process_command_queue, daemon=True)
        self.command_thread.start()

        # Start periodic health check
        self.master.after(5000, self.check_system_health)

        # Handle window closing
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self) -> None:
        """
        Creates and organizes all the widgets in the GUI.
        """
        # Main frame divided into left and right
        main_frame = ttkb.Frame(self.master, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Left frame for controls
        left_frame = ttkb.Frame(main_frame, padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Right frame for logs
        right_frame = ttkb.Frame(main_frame, width=400, padding=10)
        right_frame.pack(side="right", fill="both", expand=False)

        # ------------------ Left Frame ------------------ #

        # Control Frame
        control_frame = ttkb.LabelFrame(left_frame, text="Controles del Motor", padding=20)
        control_frame.pack(padx=10, pady=10, fill="x")

        # Automatic Mode Button
        btn_auto = ttkb.Button(control_frame, text="Modo Automático", command=self.activate_auto)
        btn_auto.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_auto, "Activa el modo automático del motor.")

        # Manual Mode Button
        btn_manual = ttkb.Button(control_frame, text="Modo Manual", command=self.activate_manual)
        btn_manual.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_manual, "Activa el modo manual del motor.")

        # Move Up Button
        btn_up = ttkb.Button(control_frame, text="Subir")
        btn_up.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        btn_up.bind('<ButtonPress>', self.on_up_press)
        btn_up.bind('<ButtonRelease>', self.on_up_release)
        CreateToolTip(btn_up, "Mueve el motor hacia arriba mientras se mantenga presionado.")

        # Move Down Button
        btn_down = ttkb.Button(control_frame, text="Bajar")
        btn_down.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        btn_down.bind('<ButtonPress>', self.on_down_press)
        btn_down.bind('<ButtonRelease>', self.on_down_release)
        CreateToolTip(btn_down, "Mueve el motor hacia abajo mientras se mantenga presionado.")

        # Stop Motor Button
        btn_stop = ttkb.Button(control_frame, text="Detener", command=self.stop_motor)
        btn_stop.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_stop, "Detiene el motor inmediatamente.")

        # Vacuum Pump On Button
        btn_pump_on = ttkb.Button(control_frame, text="Encender Bomba", command=self.pump_on)
        btn_pump_on.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_pump_on, "Enciende la bomba de vacío.")

        # Vacuum Pump Off Button
        btn_pump_off = ttkb.Button(control_frame, text="Apagar Bomba", command=self.pump_off)
        btn_pump_off.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_pump_off, "Apaga la bomba de vacío.")

        # Configure grid columns for equal expansion
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        # Speed Adjustment Frame
        speed_frame = ttkb.LabelFrame(left_frame, text="Ajuste de Velocidad", padding=20)
        speed_frame.pack(padx=10, pady=10, fill="x")

        # Speed Slider Label
        speed_label = ttkb.Label(speed_frame, text="Intervalo de Pulsos (μs):")
        speed_label.pack(side="left", padx=10, pady=10)

        # Speed Slider
        self.speed_slider = ttkb.Scale(
            speed_frame,
            from_=20,    # Updated minimum
            to=2000,
            orient="horizontal",
            variable=self.pulse_interval,
            command=self.update_speed
        )
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        # Speed Display Label
        self.speed_display = ttkb.Label(speed_frame, text=f"{self.pulse_interval.get()} μs")
        self.speed_display.pack(side="left", padx=10, pady=10)

        # System Information Frame
        info_frame = ttkb.LabelFrame(left_frame, text="Información del Sistema", padding=20)
        info_frame.pack(padx=10, pady=10, fill="x")

        # Status Indicators Frame
        status_frame = ttkb.Frame(info_frame)
        status_frame.pack(pady=10, fill="x")

        # Current Mode Label and Value
        mode_label = ttkb.Label(status_frame, text="Modo Actual:")
        mode_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        mode_value = ttkb.Label(
            status_frame,
            textvariable=self.mode,
            foreground="#a020f0",
            font=("Consolas", 12, "bold")
        )
        mode_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Current Distance Label and Value
        distance_label = ttkb.Label(status_frame, text="Distancia Actual:")
        distance_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        distance_value = ttkb.Label(
            status_frame,
            textvariable=self.current_distance,
            foreground="#00ff00",
            font=("Consolas", 12, "bold")
        )
        distance_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # System Status Frame
        system_status_frame = ttkb.Frame(info_frame)
        system_status_frame.pack(pady=10, fill="x")

        status_label = ttkb.Label(
            system_status_frame,
            text="Estado del Sistema:",
            font=("Consolas", 12, "bold")
        )
        status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.system_status_label = ttkb.Label(
            system_status_frame,
            textvariable=self.system_status,
            foreground="#ff00ff",
            font=("Consolas", 12, "bold")
        )
        self.system_status_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # ------------------ Right Frame ------------------ #

        # Logs Frame
        log_frame = ttkb.LabelFrame(right_frame, text="Logs del Sistema", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Logs Text Widget
        self.text_log = tk.Text(
            log_frame,
            state='disabled',
            wrap='word',
            height=30,
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Consolas", 10, "bold")  # Monospaced and bold font
        )
        self.text_log.pack(side="left", fill="both", expand=True)

        # Logs Scrollbar
        scrollbar = ttkb.Scrollbar(log_frame, orient="vertical", command=self.text_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_log.configure(yscrollcommand=scrollbar.set)

        # ------------------ Keyboard Events ------------------ #

        # Bind key press and release events for Up and Down arrows
        self.master.bind("<KeyPress-Up>", self.on_up_press)
        self.master.bind("<KeyRelease-Up>", self.on_up_release)
        self.master.bind("<KeyPress-Down>", self.on_down_press)
        self.master.bind("<KeyRelease-Down>", self.on_down_release)

        # Ensure the window has focus to receive keyboard events
        self.master.focus_set()

        logger.info("GUI widgets created and organized.")

    def enqueue_serial_data(self, data: str) -> None:
        """
        Enqueues data received from the serial interface for processing.

        Parameters
        ----------
        data : str
            The data received from the serial device.
        """
        self.queue.put(data)

    def process_queue(self) -> None:
        """
        Processes data in the queue and handles it appropriately.
        This method is called periodically via the Tkinter `after` method.
        """
        try:
            while not self.queue.empty():
                data = self.queue.get_nowait()
                self.handle_serial_data(data)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error processing queue: {e}")
            self.log_message(f"Error al procesar la cola: {e}", level="ERROR")
        finally:
            self.master.after(100, self.process_queue)

    def on_up_press(self, event: Optional[tk.Event] = None) -> None:
        """
        Handles the pressing of the 'Up' button.

        Parameters
        ----------
        event : Optional[tk.Event], optional
            The event that triggered the method (default is None).
        """
        if not self.up_pressed:
            self.up_pressed = True
            logger.debug("Up button pressed.")
            self.move_up()

    def on_up_release(self, event: Optional[tk.Event] = None) -> None:
        """
        Handles the releasing of the 'Up' button.

        Parameters
        ----------
        event : Optional[tk.Event], optional
            The event that triggered the method (default is None).
        """
        if self.up_pressed:
            self.up_pressed = False
            logger.debug("Up button released.")
            self.stop_motor()

    def on_down_press(self, event: Optional[tk.Event] = None) -> None:
        """
        Handles the pressing of the 'Down' button.

        Parameters
        ----------
        event : Optional[tk.Event], optional
            The event that triggered the method (default is None).
        """
        if not self.down_pressed:
            self.down_pressed = True
            logger.debug("Down button pressed.")
            self.move_down()

    def on_down_release(self, event: Optional[tk.Event] = None) -> None:
        """
        Handles the releasing of the 'Down' button.

        Parameters
        ----------
        event : Optional[tk.Event], optional
            The event that triggered the method (default is None).
        """
        if self.down_pressed:
            self.down_pressed = False
            logger.debug("Down button released.")
            self.stop_motor()

    def activate_auto(self) -> None:
        """
        Activates automatic mode by sending the corresponding command to the Arduino.
        """
        success = self.send_command("AUTO")
        if success:
            self.mode.set("Automático")
            self.system_status.set("Modo Automático Activado")
            self.system_status_label.config(foreground="#a020f0")  # Dark purple
            self.log_message("Activando modo automático.", level="INFO")
            logger.info("Automatic mode activated.")

    def activate_manual(self) -> None:
        """
        Activates manual mode by sending the corresponding command to the Arduino.
        """
        success = self.send_command("STOP")
        if success:
            self.mode.set("Manual")
            self.system_status.set("Modo Manual Activado")
            self.system_status_label.config(foreground="#00ffff")  # Cyan
            self.log_message("Modo manual activado. Motor detenido.", level="INFO")
            logger.info("Manual mode activated.")

    def move_up(self) -> None:
        """
        Sends the command to move the motor upwards.
        """
        success = self.send_command("UP")
        if success:
            self.mode.set("Manual")
            self.log_message("Moviendo hacia arriba.", level="INFO")
            logger.info("Command 'UP' sent.")

    def move_down(self) -> None:
        """
        Sends the command to move the motor downwards.
        """
        success = self.send_command("DOWN")
        if success:
            self.mode.set("Manual")
            self.log_message("Moviendo hacia abajo.", level="INFO")
            logger.info("Command 'DOWN' sent.")

    def stop_motor(self) -> None:
        """
        Sends the command to stop the motor.
        """
        success = self.send_command("STOP")
        if success:
            self.mode.set("Manual")
            self.log_message("Motor detenido.", level="INFO")
            logger.info("Command 'STOP' sent.")

    def update_speed(self, event: Optional[tk.Event] = None) -> None:
        """
        Updates the motor speed based on the slider's value and sends the corresponding command.

        Parameters
        ----------
        event : Optional[tk.Event], optional
            The event that triggered the method (default is None).
        """
        speed = self.pulse_interval.get()
        self.speed_display.config(text=f"{int(speed)} μs")
        success = self.send_command(f"SET_SPEED {int(speed)}")
        if success:
            self.log_message(f"Ajustando velocidad a {int(speed)} μs.", level="INFO")
            logger.info(f"Command 'SET_SPEED {int(speed)}' sent.")

    def handle_serial_data(self, data: str) -> None:
        """
        Handles data received from the serial interface and updates the GUI accordingly.

        Parameters
        ----------
        data : str
            The data received from the serial device.
        """
        logger.debug(f"Received data for handling: {data}")
        if "Distancia actual" in data:
            try:
                distance_str = data.split(":")[-1].strip().replace(" cm", "")
                distance = float(distance_str)
                self.current_distance.set(f"{distance} cm")
                self.log_message(f"Distancia: {distance} cm", level="INFO")
                logger.info(f"Distance updated to {distance} cm.")
            except ValueError:
                self.log_message(f"Error al parsear distancia: {data}", level="ERROR")
                logger.error(f"Error parsing distance: {data}")
        elif "Velocidad actual" in data:
            try:
                speed_str = data.split(":")[-1].strip().replace(" μs", "")
                speed = int(speed_str)
                self.pulse_interval.set(speed)  # Sync the slider
                self.speed_display.config(text=f"{speed} μs")
                self.log_message(f"Velocidad: {speed} μs", level="INFO")
                logger.info(f"Speed updated to {speed} μs.")
            except ValueError:
                self.log_message(f"Error al parsear velocidad: {data}", level="ERROR")
                logger.error(f"Error parsing speed: {data}")
        elif "Motor detenido" in data:
            self.mode.set("Manual")
            self.log_message("Motor detenido por Arduino.", level="INFO")
            logger.info("Motor stopped by Arduino.")
        elif "Activando modo automático" in data:
            self.mode.set("Automático")
            self.system_status.set("Modo Automático Activado")
            self.system_status_label.config(foreground="#a020f0")  # Dark purple
            self.log_message("Modo automático activado por Arduino.", level="INFO")
            logger.info("Automatic mode activated by Arduino.")
        elif "Desactivando modo automático" in data:
            self.mode.set("Manual")
            self.system_status.set("Modo Manual Activado")
            self.system_status_label.config(foreground="#00ffff")  # Cyan
            self.log_message("Modo automático desactivado por Arduino.", level="INFO")
            logger.info("Automatic mode deactivated by Arduino.")
        elif "Bomba de vacío encendida." in data:
            self.log_message("Bomba de vacío encendida.", level="INFO")
            logger.info("Vacuum pump turned on.")
        elif "Bomba de vacío apagada." in data:
            self.log_message("Bomba de vacío apagada.", level="INFO")
            logger.info("Vacuum pump turned off.")
        else:
            self.log_message(data, level="DEBUG")
            logger.info(f"Received message: {data}")

    def log_message(self, message: str, level: str = "INFO") -> None:
        """
        Adds a message to the log area with a specific color based on the level.

        Parameters
        ----------
        message : str
            The message to display.
        level : str, optional
            The level of the message ('INFO', 'DEBUG', 'WARNING', 'ERROR').
            Default is 'INFO'.
        """
        color_map = {
            "INFO": "#ffffff",     # White
            "DEBUG": "#a9a9a9",    # Gray
            "WARNING": "#ffa500",  # Orange
            "ERROR": "#ff0000"     # Red
        }
        color = color_map.get(level, "#ffffff")  # Default to white if level not defined

        self.text_log.configure(state='normal')
        self.text_log.insert(tk.END, f"{message}\n")

        # Limit the number of lines in the log to optimize performance
        max_lines = 1000
        current_lines = int(self.text_log.index('end-1c').split('.')[0])
        if current_lines > max_lines:
            # Remove the first 100 lines to prevent indefinite growth
            self.text_log.delete('1.0', f"{100}.0")

        # Apply color to the last inserted line
        last_line = int(self.text_log.index("end-1c").split('.')[0])
        tag_name = f"log_{last_line}"
        self.text_log.tag_add(tag_name, f"{last_line}.0", f"{last_line}.end")
        self.text_log.tag_config(tag_name, foreground=color)
        self.text_log.configure(state='disabled')
        self.text_log.see(tk.END)

        logger.debug(f"Logged message: {message}")

    def pump_on(self) -> None:
        """
        Sends the command to turn on the vacuum pump.
        """
        success = self.send_command("PUMP_ON")
        if success:
            self.log_message("Encendiendo bomba de vacío.", level="INFO")
            logger.info("Command 'PUMP_ON' sent.")

    def pump_off(self) -> None:
        """
        Sends the command to turn off the vacuum pump.
        """
        success = self.send_command("PUMP_OFF")
        if success:
            self.log_message("Apagando bomba de vacío.", level="INFO")
            logger.info("Command 'PUMP_OFF' sent.")

    def on_closing(self) -> None:
        """
        Handles the safe closure of the application.
        Sends the 'STOP' command and disconnects the serial communication.
        """
        if messagebox.askokcancel("Salir", "¿Quieres salir de la aplicación?"):
            self.send_command("STOP")
            self.serial.disconnect()
            logger.info("Application closed by user.")
            # Signal the command thread to stop
            self.stop_event.set()
            self.command_thread.join(timeout=1)
            self.master.destroy()

    def send_command(self, command: str, priority: int = 1) -> bool:
        """
        Enqueues a command with a given priority.

        Parameters
        ----------
        command : str
            The command string to send.
        priority : int, optional
            The priority of the command (1-5, lower number = higher priority).
            Default is 1.

        Returns
        -------
        bool
            True if the command was enqueued successfully, False otherwise.
        """
        current_time = time.time()
        if current_time - self.last_command_time < self.command_throttle:
            logger.warning(f"Command '{command}' discarded due to throttle.")
            self.log_message(f"Comando '{command}' descartado por throttle.", level="WARNING")
            return False

        with self.command_lock:
            self.command_queue.put((priority, current_time, command))
            self.last_command_time = current_time
        return True

    def process_command_queue(self) -> None:
        """
        Continuously processes the command queue and sends commands to the serial device.
        Handles errors and retries as necessary.
        """
        while not self.stop_event.is_set():
            try:
                priority, timestamp, command = self.command_queue.get_nowait()
                if time.time() - timestamp > 5.0:
                    logger.warning(f"Command '{command}' discarded due to age.")
                    self.log_message(f"Comando '{command}' descartado por antigüedad.", level="WARNING")
                    continue

                success = self.serial.send_command(command)
                if not success:
                    self.handle_command_error(command)
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                self.log_message(f"Error processing command: {e}", level="ERROR")
            time.sleep(0.05)  # Short sleep to prevent CPU overuse

    def check_system_health(self) -> None:
        """
        Monitors system health and attempts recovery if needed.
        """
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()

        if cpu_usage > 80 or memory_info.percent > 80:
            self.system_health = max(0, self.system_health - 10)
            self.log_message(
                f"High resource usage detected: CPU {cpu_usage}%, Memory {memory_info.percent}%",
                level="WARNING"
            )
            logger.warning(f"High resource usage: CPU {cpu_usage}%, Memory {memory_info.percent}%")

        if self.error_count > 5:
            self.system_health = max(0, self.system_health - 10)
            self.attempt_system_recovery()

        if not self.serial.is_connected:
            self.attempt_reconnect()

        # Schedule the next health check
        self.master.after(5000, self.check_system_health)

    def attempt_system_recovery(self) -> None:
        """
        Attempts to recover the system from errors by stopping the motor and resetting error counts.
        """
        self.log_message("Intentando recuperar el sistema...", level="WARNING")
        logger.info("Attempting system recovery.")
        self.stop_motor()
        self.error_count = 0
        self.system_health = min(100, self.system_health + 20)
        self.log_message("Recuperación exitosa.", level="INFO")
        logger.info("System recovery successful.")

    def attempt_reconnect(self) -> None:
        """
        Attempts to reconnect to the serial device if disconnected.
        """
        if self.reconnect_attempts < 3:
            self.log_message("Intentando reconectar...", level="WARNING")
            logger.info("Attempting to reconnect to the serial device.")
            success = self.serial.connect()
            if success:
                self.reconnect_attempts = 0
                self.log_message("¡Reconexión exitosa!", level="INFO")
                logger.info("Reconnection to the serial device successful.")
                # Update system status
                self.system_status.set("Operando en Modo Real")
                self.system_status_label.config(foreground="#ff00ff")  # Magenta
            else:
                self.reconnect_attempts += 1
                self.log_message(
                    f"Reconexión fallida. Intento {self.reconnect_attempts}/3.",
                    level="ERROR"
                )
                logger.warning(f"Reconnection failed. Attempt {self.reconnect_attempts}/3.")
        else:
            self.log_message("Máximo de intentos de reconexión alcanzado.", level="ERROR")
            logger.error("Maximum reconnection attempts reached.")

    def handle_command_error(self, command: str) -> None:
        """
        Handles failed commands by incrementing the error count and retrying if applicable.

        Parameters
        ----------
        command : str
            The command that failed to send successfully.
        """
        self.error_count += 1
        self.last_error_time = time.time()
        self.log_message(f"Comando fallido: {command}", level="ERROR")
        logger.error(f"Failed command: {command}")

        if self.error_count <= 3:
            retry_priority = 5  # Lower priority for retries
            self.send_command(command, priority=retry_priority)
            self.log_message(f"Reintentando comando: {command}", level="WARNING")
            logger.info(f"Retrying command: {command}")
        else:
            self.log_message("Se alcanzó el límite de reintentos para comandos.", level="ERROR")
            logger.error("Command retry limit reached.")

    def on_closing(self) -> None:
        """
        Handles the closing of the application safely by stopping the motor,
        disconnecting the serial interface, and terminating threads.
        """
        if messagebox.askokcancel("Salir", "¿Quieres salir de la aplicación?"):
            self.send_command("STOP")
            self.serial.disconnect()
            logger.info("Application closed by the user.")
            # Signal the command thread to stop and wait for it to finish
            self.stop_event.set()
            self.command_thread.join(timeout=1)
            self.master.destroy()

#hello