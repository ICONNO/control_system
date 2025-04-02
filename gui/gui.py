#!/usr/bin/env python3
"""
Motor and Vacuum Pump Control GUI

Displays mode, current distance, and system status.
Provides buttons for auto/manual operation, pump control, remote image capture,
and discrete pulse interval selection for 100, 200, 300, and 500 µs.
"""

import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import threading
import time
import logging
import queue
import psutil
from typing import Optional
from .serial_comm import SerialInterface
from .styles import set_styles
from remote_capture import capture_images  # Ensure remote_capture.py is in your project root

# Logging configuration
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CreateToolTip:
    """
    A simple tooltip class for displaying contextual information on widget hover.

    Attributes:
        widget (tk.Widget): The widget to attach the tooltip.
        text (str): The text to be displayed in the tooltip.
        waittime (int): Delay (in ms) before the tooltip is shown.
        wraplength (int): Maximum width (in pixels) of the tooltip text.
    """
    def __init__(self, widget: tk.Widget, text: str = 'widget info') -> None:
        """
        Initialize the tooltip with the specified widget and text.

        :param widget: The tkinter widget to attach the tooltip.
        :param text: The text content of the tooltip.
        """
        self.waittime = 500
        self.wraplength = 180
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event: Optional[tk.Event] = None) -> None:
        """Schedules the tooltip to be shown on mouse enter."""
        self.schedule()

    def leave(self, event: Optional[tk.Event] = None) -> None:
        """Cancels the scheduled tooltip and hides it when mouse leaves."""
        self.unschedule()
        self.hidetip()

    def schedule(self) -> None:
        """Schedule tooltip display after waittime."""
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self) -> None:
        """Cancel the scheduled tooltip if it exists."""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self, event: Optional[tk.Event] = None) -> None:
        """
        Create and display the tooltip window near the widget.

        :param event: The triggering event (optional).
        """
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
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
        """Destroy the tooltip window if it exists."""
        if self.tw:
            self.tw.destroy()
            self.tw = None

class MotorControlGUI:
    """
    GUI for controlling the motor and vacuum pump.

    This class creates the main window, sets up all the widgets,
    manages user interactions, and communicates with the Arduino via serial.

    Attributes:
        master (tk.Tk): The main application window.
        serial (SerialInterface): Serial interface for communication.
        mode (tk.StringVar): Current operating mode (Manual or Auto).
        current_distance (tk.StringVar): Current distance value displayed.
        system_status (tk.StringVar): Current status of the system.
        pulse_interval_choice (tk.StringVar): Selected discrete pulse interval.
        queue (queue.Queue): Queue for incoming serial data.
        command_queue (queue.Queue): Queue for outgoing commands.
    """
    def __init__(self, master: tk.Tk, serial_comm: SerialInterface) -> None:
        """
        Initialize the MotorControlGUI instance.

        :param master: The main tkinter window.
        :param serial_comm: Instance of SerialInterface to handle serial comm.
        """
        self.master = master
        self.serial = serial_comm
        self.serial.register_callback(self.enqueue_serial_data)

        # Apply custom styles using ttkbootstrap
        self.style = ttkb.Style(theme='superhero')
        logger.info("Initializing GUI.")

        # GUI state variables
        self.mode = tk.StringVar(value="Manual")
        self.current_distance = tk.StringVar(value="Unknown")
        self.system_status = tk.StringVar(
            value="Real Mode" if self.serial.is_connected else "Disconnected"
        )

        # Discrete pulse interval selection (values: "100", "200", "300", "500")
        self.pulse_interval_choice = tk.StringVar(value="100")

        # Flags for manual control
        self.up_pressed = False
        self.down_pressed = False
        self.queue = queue.Queue()

        set_styles()
        self.create_widgets()
        self.master.after(100, self.process_queue)
        logger.info("GUI initialized.")

        # Command queue and system monitoring
        self.command_queue = queue.Queue()
        self.command_lock = threading.Lock()
        self.last_command_time = 0.0
        self.command_throttle = 0.1

        self.system_health = 100.0
        self.error_count = 0
        self.reconnect_attempts = 0

        self.stop_event = threading.Event()
        self.command_thread = threading.Thread(target=self.process_command_queue, daemon=True)
        self.command_thread.start()

        self.master.after(5000, self.check_system_health)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self) -> None:
        """
        Create and layout all GUI widgets including info panel, button panel,
        speed selection, and log area.
        """
        main_frame = ttkb.Frame(self.master, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Info Panel: Displays current mode, distance, and system status.
        info_frame = ttkb.Frame(main_frame)
        info_frame.pack(fill="x", pady=5)
        ttkb.Label(info_frame, text="Mode:").pack(side="left", padx=5)
        ttkb.Label(info_frame, textvariable=self.mode, foreground="#a020f0", font=("Consolas", 12, "bold")).pack(side="left", padx=5)
        ttkb.Label(info_frame, text="Distance:").pack(side="left", padx=5)
        ttkb.Label(info_frame, textvariable=self.current_distance, foreground="#00ff00", font=("Consolas", 12, "bold")).pack(side="left", padx=5)
        ttkb.Label(info_frame, text="Status:").pack(side="left", padx=5)
        ttkb.Label(info_frame, textvariable=self.system_status, foreground="#ff00ff", font=("Consolas", 12, "bold")).pack(side="left", padx=5)

        # Button Panel: Contains operational buttons and controls.
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill="x", pady=5)
        btn_auto = ttkb.Button(button_frame, text="Auto Mode", command=self.activate_auto)
        btn_auto.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_auto, "Activate auto mode.")
        btn_manual = ttkb.Button(button_frame, text="Manual Mode", command=self.activate_manual)
        btn_manual.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_manual, "Activate manual mode.")
        btn_up = ttkb.Button(button_frame, text="Up")
        btn_up.pack(side="left", padx=5, pady=5)
        # Inverted behavior: "Up" button triggers move_down.
        btn_up.bind('<ButtonPress>', self.on_down_press)
        btn_up.bind('<ButtonRelease>', self.on_down_release)
        CreateToolTip(btn_up, "Move motor down while pressed.")
        btn_down = ttkb.Button(button_frame, text="Down")
        btn_down.pack(side="left", padx=5, pady=5)
        # Inverted behavior: "Down" button triggers move_up.
        btn_down.bind('<ButtonPress>', self.on_up_press)
        btn_down.bind('<ButtonRelease>', self.on_up_release)
        CreateToolTip(btn_down, "Move motor up while pressed.")
        btn_stop = ttkb.Button(button_frame, text="Stop", command=self.stop_motor)
        btn_stop.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_stop, "Stop motor immediately.")
        btn_pump_on = ttkb.Button(button_frame, text="Pump On", command=self.pump_on)
        btn_pump_on.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_pump_on, "Turn vacuum pump on.")
        btn_pump_off = ttkb.Button(button_frame, text="Pump Off", command=self.pump_off)
        btn_pump_off.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_pump_off, "Turn vacuum pump off.")
        btn_capture = ttkb.Button(button_frame, text="Capture Image", command=self.trigger_capture)
        btn_capture.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_capture, "Trigger remote image capture.")

        # Speed Selection Panel: Allows selection of pulse interval.
        speed_frame = ttkb.Frame(main_frame)
        speed_frame.pack(fill="x", pady=5)
        ttkb.Label(speed_frame, text="Pulse Interval (μs):").pack(side="left", padx=5)
        for interval in ["100", "200", "300", "500"]:
            r = ttkb.Radiobutton(
                speed_frame,
                text=f"{interval} μs",
                value=interval,
                variable=self.pulse_interval_choice,
                command=self.update_discrete_speed
            )
            r.pack(side="left", padx=5)

        # Log Area: Displays system logs.
        log_frame = ttkb.LabelFrame(main_frame, text="Logs", padding=10)
        log_frame.pack(fill="both", expand=True, pady=5)
        self.text_log = tk.Text(log_frame, state='disabled', wrap='word', height=10,
                                 bg="#1e1e1e", fg="#ffffff", font=("Consolas", 10))
        self.text_log.pack(side="left", fill="both", expand=True)
        scrollbar = ttkb.Scrollbar(log_frame, orient="vertical", command=self.text_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_log.configure(yscrollcommand=scrollbar.set)

        # Bind keys for movement control (inverted mapping)
        self.master.bind("<KeyPress-Up>", self.on_down_press)
        self.master.bind("<KeyRelease-Up>", self.on_down_release)
        self.master.bind("<KeyPress-Down>", self.on_up_press)
        self.master.bind("<KeyRelease-Down>", self.on_up_release)
        self.master.focus_set()
        logger.info("Widgets created and arranged.")

    def update_discrete_speed(self) -> None:
        """
        Update motor speed based on selected pulse interval.

        Reads the pulse_interval_choice, calculates steps per second as:
            steps_per_second = 1,000,000 / pulse_interval
        and sends the "SET_SPEED" command to the controller.
        """
        pulse_interval = int(self.pulse_interval_choice.get())
        steps_per_second = int(1_000_000 / pulse_interval)
        success = self.send_command(f"SET_SPEED {steps_per_second}")
        if success:
            self.log_message(f"Speed set to: {steps_per_second} steps/s (Pulse interval: {pulse_interval} μs).", level="INFO")
            logger.info(f"Command 'SET_SPEED {steps_per_second}' sent.")

    def trigger_capture(self) -> None:
        """
        Trigger remote image capture via SSH.

        Connects to the Raspberry Pi at the specified IP address and
        executes the remote capture script.
        """
        raspberry_ip = "192.168.1.96"
        if capture_images(raspberry_ip):
            self.log_message("Remote capture succeeded.", level="INFO")
        else:
            self.log_message("Remote capture failed.", level="ERROR")

    def enqueue_serial_data(self, data: str) -> None:
        """
        Enqueue data received from the serial interface.

        :param data: Data string received from Arduino.
        """
        self.queue.put(data)

    def process_queue(self) -> None:
        """
        Process the serial data queue by handling each item.

        Continuously schedules itself to run every 100 ms.
        """
        try:
            while not self.queue.empty():
                data = self.queue.get_nowait()
                self.handle_serial_data(data)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Queue error: {e}")
            self.log_message(f"Queue error: {e}", level="ERROR")
        finally:
            self.master.after(100, self.process_queue)

    def on_down_press(self, event: Optional[tk.Event] = None) -> None:
        """
        Handles the key press event for the "Up" key (mapped to move_down).

        :param event: The key press event.
        """
        if not self.down_pressed:
            self.down_pressed = True
            logger.debug("Up key pressed (action: move down).")
            self.move_down()

    def on_down_release(self, event: Optional[tk.Event] = None) -> None:
        """
        Handles the key release event for the "Up" key to stop the motor.

        :param event: The key release event.
        """
        if self.down_pressed:
            self.down_pressed = False
            logger.debug("Up key released (action: stop).")
            self.stop_motor()

    def on_up_press(self, event: Optional[tk.Event] = None) -> None:
        """
        Handles the key press event for the "Down" key (mapped to move_up).

        :param event: The key press event.
        """
        if not self.up_pressed:
            self.up_pressed = True
            logger.debug("Down key pressed (action: move up).")
            self.move_up()

    def on_up_release(self, event: Optional[tk.Event] = None) -> None:
        """
        Handles the key release event for the "Down" key to stop the motor.

        :param event: The key release event.
        """
        if self.up_pressed:
            self.up_pressed = False
            logger.debug("Down key released (action: stop).")
            self.stop_motor()

    def activate_auto(self) -> None:
        """
        Activates auto mode by sending the "AUTO" command.

        Sets the system mode to Auto and updates the GUI.
        """
        success = self.send_command("AUTO")
        if success:
            self.mode.set("Auto")
            self.system_status.set("Auto Mode Active")
            self.log_message("Auto mode activated.", level="INFO")
            logger.info("Auto mode activated.")

    def activate_manual(self) -> None:
        """
        Activates manual mode by sending the "STOP" command.

        Sets the system mode to Manual and stops the motor.
        """
        success = self.send_command("STOP")
        if success:
            self.mode.set("Manual")
            self.system_status.set("Manual Mode Active")
            self.log_message("Manual mode activated; motor stopped.", level="INFO")
            logger.info("Manual mode activated.")

    def move_up(self) -> None:
        """
        Sends the "UP" command to move the motor upward.

        Updates the GUI to reflect manual mode.
        """
        success = self.send_command("UP")
        if success:
            self.mode.set("Manual")
            self.log_message("Moving up.", level="INFO")
            logger.info("Command 'UP' sent.")

    def move_down(self) -> None:
        """
        Sends the "DOWN" command to move the motor downward.

        Updates the GUI to reflect manual mode.
        """
        success = self.send_command("DOWN")
        if success:
            self.mode.set("Manual")
            self.log_message("Moving down.", level="INFO")
            logger.info("Command 'DOWN' sent.")

    def stop_motor(self) -> None:
        """
        Sends the "STOP" command to halt the motor immediately.

        Updates the system mode to Manual.
        """
        success = self.send_command("STOP")
        if success:
            self.mode.set("Manual")
            self.log_message("Motor stopped.", level="INFO")
            logger.info("Command 'STOP' sent.")

    def update_speed(self, event: Optional[tk.Event] = None) -> None:
        """
        Placeholder method for speed updates from a slider (unused).
        """
        pass

    def handle_serial_data(self, data: str) -> None:
        """
        Processes data received from the serial interface and updates the GUI.

        :param data: The data string received from the serial port.
        """
        logger.debug(f"Received: {data}")
        if "Current distance" in data:
            try:
                d_str = data.split(":")[-1].strip().replace(" cm", "")
                d_val = float(d_str)
                self.current_distance.set(f"{d_val} cm")
            except ValueError:
                self.log_message(f"Distance parse error: {data}", level="ERROR")
        elif "Motor stopped" in data:
            self.mode.set("Manual")
            self.log_message("Motor stopped (from Arduino).", level="INFO")
        elif "Auto mode" in data:
            self.mode.set("Auto")
            self.system_status.set("Auto Mode Active")
            self.log_message("Auto mode activated (from Arduino).", level="INFO")
        elif "Manual mode" in data:
            self.mode.set("Manual")
            self.system_status.set("Manual Mode Active")
            self.log_message("Manual mode activated (from Arduino).", level="INFO")
        elif "Vacuum pump on" in data:
            self.log_message("Vacuum pump turned on.", level="INFO")
        elif "Vacuum pump off" in data:
            self.log_message("Vacuum pump turned off.", level="INFO")
        elif "CAPTURE" in data:
            self.log_message("Capture command received from Arduino.", level="INFO")
            self.trigger_capture()
        else:
            logger.debug(f"Unclassified: {data}")

    def log_message(self, message: str, level: str = "INFO") -> None:
        """
        Logs a message in the text log area of the GUI.

        :param message: The message to log.
        :param level: The log level (INFO, WARNING, ERROR).
        """
        if level == "DEBUG":
            return
        color_map = {"INFO": "#ffffff", "WARNING": "#ffa500", "ERROR": "#ff0000"}
        color = color_map.get(level, "#ffffff")
        self.text_log.configure(state='normal')
        self.text_log.insert(tk.END, f"{message}\n")
        max_lines = 1000
        current_lines = int(self.text_log.index('end-1c').split('.')[0])
        if current_lines > max_lines:
            self.text_log.delete('1.0', f"{100}.0")
        last_line = int(self.text_log.index("end-1c").split('.')[0])
        tag_name = f"log_{last_line}"
        self.text_log.tag_add(tag_name, f"{last_line}.0", f"{last_line}.end")
        self.text_log.tag_config(tag_name, foreground=color)
        self.text_log.configure(state='disabled')
        self.text_log.see(tk.END)
        logger.info(f"Log: {message}")

    def pump_on(self) -> None:
        """
        Sends the "PUMP_ON" command to activate the vacuum pump.
        """
        success = self.send_command("PUMP_ON")
        if success:
            self.log_message("Vacuum pump turned on.", level="INFO")
            logger.info("Command 'PUMP_ON' sent.")

    def pump_off(self) -> None:
        """
        Sends the "PUMP_OFF" command to deactivate the vacuum pump.
        """
        success = self.send_command("PUMP_OFF")
        if success:
            self.log_message("Vacuum pump turned off.", level="INFO")
            logger.info("Command 'PUMP_OFF' sent.")

    def on_closing(self) -> None:
        """
        Handles the GUI window closing event.

        Prompts the user for confirmation, sends a STOP command,
        disconnects the serial interface, and cleans up the thread.
        """
        if messagebox.askokcancel("Exit", "Do you want to exit?"):
            self.send_command("STOP")
            self.serial.disconnect()
            logger.info("Application closed by user.")
            self.stop_event.set()
            self.command_thread.join(timeout=1)
            self.master.destroy()

    def send_command(self, command: str, priority: int = 1) -> bool:
        """
        Sends a command to the Arduino via the serial interface.

        :param command: The command string to send (e.g., "AUTO", "UP").
        :param priority: Priority level for the command queue.
        :return: True if the command was enqueued successfully, False otherwise.
        """
        current_time = time.time()
        if current_time - self.last_command_time < self.command_throttle:
            logger.warning(f"Command '{command}' throttled.")
            self.log_message(f"Command '{command}' throttled.", level="WARNING")
            return False
        with self.command_lock:
            self.command_queue.put((priority, current_time, command))
            self.last_command_time = current_time
        return True

    def process_command_queue(self) -> None:
        """
        Processes the command queue by sending commands to the Arduino.

        Commands older than 5 seconds are discarded. This function runs continuously in a separate thread.
        """
        while not self.stop_event.is_set():
            try:
                priority, timestamp, command = self.command_queue.get_nowait()
                if (time.time() - timestamp) > 5.0:
                    logger.warning(f"Command '{command}' discarded (old).")
                    self.log_message(f"Command '{command}' discarded (old).", level="WARNING")
                    continue
                success = self.serial.send_command(command)
                if not success:
                    self.log_message(f"Error sending '{command}'", level="ERROR")
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                self.log_message(f"Error processing command: {e}", level="ERROR")
            time.sleep(0.05)

    def check_system_health(self) -> None:
        """
        Checks system health by monitoring CPU and memory usage and attempts reconnection if necessary.

        :return: None
        """
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        if cpu > 80 or mem > 80:
            self.system_health = max(0, self.system_health - 10)
            self.log_message(f"High usage: CPU {cpu}%, Memory {mem}%", level="WARNING")
            logger.warning(f"High usage: CPU {cpu}%, Memory {mem}%")
        if self.error_count > 5:
            self.system_health = max(0, self.system_health - 10)
            self.log_message("System recovering...", level="WARNING")
            self.stop_motor()
            self.error_count = 0
            self.system_health = min(100, self.system_health + 20)
            self.log_message("Recovery successful.", level="INFO")
            logger.info("Recovery successful.")
        if not self.serial.is_connected:
            self.attempt_reconnect()
        self.master.after(5000, self.check_system_health)

    def attempt_reconnect(self) -> None:
        """
        Attempts to reconnect the serial interface if the connection is lost.

        Retries up to 3 times and logs the outcome.
        """
        if self.reconnect_attempts < 3:
            self.log_message("Attempting reconnect...", level="WARNING")
            logger.info("Attempting reconnect to serial.")
            success = self.serial.connect()
            if success:
                self.reconnect_attempts = 0
                self.log_message("Reconnect successful.", level="INFO")
                logger.info("Reconnect successful.")
                self.system_status.set("Real Mode")
            else:
                self.reconnect_attempts += 1
                self.log_message(f"Reconnect failed, attempt {self.reconnect_attempts}/3.", level="ERROR")
                logger.warning(f"Reconnect failed, attempt {self.reconnect_attempts}/3.")
        else:
            self.log_message("Max reconnection attempts reached.", level="ERROR")
            logger.error("Max reconnection attempts reached.")

    def handle_command_error(self, command: str) -> None:
        """
        Handles errors encountered during command processing.

        Increments the error counter and attempts to retry sending the command if within retry limits.

        :param command: The command that failed.
        """
        self.error_count += 1
        self.last_error_time = time.time()
        self.log_message(f"Command failed: {command}", level="ERROR")
        logger.error(f"Command failed: {command}")
        if self.error_count <= 3:
            self.send_command(command, priority=5)
            self.log_message(f"Retrying: {command}", level="WARNING")
            logger.info(f"Retrying command: {command}")
        else:
            self.log_message("Command retry limit reached.", level="ERROR")
            logger.error("Command retry limit reached.")
