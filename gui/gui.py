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
from .serial_comm import SerialInterface, MockSerialComm  # Asegúrate de que estos módulos estén implementados
from .styles import set_styles  # Función para aplicar estilos

# ------------------- Configuración de Logging -------------------
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------

class CreateToolTip:
    """
    Clase para crear un tooltip para un widget dado.
    """
    def __init__(self, widget: tk.Widget, text: str = 'widget info') -> None:
        self.waittime = 500  # milisegundos
        self.wraplength = 180  # ancho máximo de texto
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event: Optional[tk.Event] = None) -> None:
        self.schedule()

    def leave(self, event: Optional[tk.Event] = None) -> None:
        self.unschedule()
        self.hidetip()

    def schedule(self) -> None:
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self) -> None:
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def showtip(self, event: Optional[tk.Event] = None) -> None:
        x, y, cx, cy = self.widget.bbox("insert")
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
        if self.tw:
            self.tw.destroy()
            self.tw = None

class MotorControlGUI:
    """
    Clase principal para la interfaz gráfica de control del motor.
    """
    def __init__(self, master: tk.Tk, serial_comm: SerialInterface) -> None:
        self.master = master
        self.serial = serial_comm
        self.serial.register_callback(self.enqueue_serial_data)

        # Aplicar tema de ttkbootstrap
        self.style = ttkb.Style(theme='superhero')
        logger.info("Inicializando la interfaz gráfica.")

        # Variables de estado
        self.mode = tk.StringVar(value="Manual")
        self.current_distance = tk.StringVar(value="Desconocida")
        self.pulse_interval = tk.IntVar(value=800)
        self.system_status = tk.StringVar(
            value="Operando en Modo Real" if self.serial.is_connected else "Modo Simulación"
        )

        # Variables para control continuo de teclas
        self.up_pressed = False
        self.down_pressed = False
        self.up_repeat_job = None
        self.down_repeat_job = None

        # Cola para comunicación entre hilos
        self.queue = queue.Queue()

        # Aplicar estilos personalizados
        set_styles()

        # Crear widgets de la GUI
        self.create_widgets()

        # Iniciar procesamiento de datos seriales
        self.master.after(100, self.process_queue)

        logger.info("Interfaz gráfica inicializada correctamente.")

        # Cola de comandos y sincronización
        self.command_queue = queue.Queue()
        self.command_lock = threading.Lock()
        self.last_command_time = 0.0
        self.command_throttle = 0.1  # segundos

        # Variables de monitoreo del sistema
        self.system_health = 100.0
        self.error_count = 0
        self.last_error_time = 0.0
        self.reconnect_attempts = 0

        # Evento para detener el hilo de comandos
        self.stop_event = threading.Event()
        self.command_thread = threading.Thread(target=self.process_command_queue, daemon=True)
        self.command_thread.start()

        self.master.after(5000, self.check_system_health)

        # Configurar cierre seguro de la ventana
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Bind para eventos de teclado (para control continuo)
        self.master.bind("<KeyPress-Up>", self.on_up_press)
        self.master.bind("<KeyRelease-Up>", self.on_up_release)
        self.master.bind("<KeyPress-Down>", self.on_down_press)
        self.master.bind("<KeyRelease-Down>", self.on_down_release)
        self.master.focus_set()

    def create_widgets(self) -> None:
        main_frame = ttkb.Frame(self.master, padding=10)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttkb.Frame(main_frame, padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_frame = ttkb.Frame(main_frame, width=400, padding=10)
        right_frame.pack(side="right", fill="both", expand=False)

        # --- Controles del Motor ---
        control_frame = ttkb.LabelFrame(left_frame, text="Controles del Motor", padding=20)
        control_frame.pack(padx=10, pady=10, fill="x")

        btn_auto = ttkb.Button(control_frame, text="Modo Automático", command=self.activate_auto)
        btn_auto.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_auto, "Activa el modo automático del motor.")

        btn_manual = ttkb.Button(control_frame, text="Modo Manual", command=self.activate_manual)
        btn_manual.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_manual, "Activa el modo manual del motor.")

        btn_up = ttkb.Button(control_frame, text="Subir")
        btn_up.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        btn_up.bind('<ButtonPress>', self.on_up_press)
        btn_up.bind('<ButtonRelease>', self.on_up_release)
        CreateToolTip(btn_up, "Mueve el motor hacia arriba mientras se mantenga presionado.")

        btn_down = ttkb.Button(control_frame, text="Bajar")
        btn_down.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        btn_down.bind('<ButtonPress>', self.on_down_press)
        btn_down.bind('<ButtonRelease>', self.on_down_release)
        CreateToolTip(btn_down, "Mueve el motor hacia abajo mientras se mantenga presionado.")

        btn_stop = ttkb.Button(control_frame, text="Detener", command=self.stop_motor)
        btn_stop.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_stop, "Detiene el motor inmediatamente.")

        btn_pump_on = ttkb.Button(control_frame, text="Encender Bomba", command=self.pump_on)
        btn_pump_on.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_pump_on, "Enciende la bomba de vacío.")

        btn_pump_off = ttkb.Button(control_frame, text="Apagar Bomba", command=self.pump_off)
        btn_pump_off.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_pump_off, "Apaga la bomba de vacío.")

        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        # --- Ajuste de Velocidad ---
        speed_frame = ttkb.LabelFrame(left_frame, text="Ajuste de Velocidad", padding=20)
        speed_frame.pack(padx=10, pady=10, fill="x")

        speed_label = ttkb.Label(speed_frame, text="Intervalo de Pulsos (μs):")
        speed_label.pack(side="left", padx=10, pady=10)

        self.speed_slider = ttkb.Scale(
            speed_frame,
            from_=20,
            to=2000,
            orient="horizontal",
            variable=self.pulse_interval,
            command=self.update_speed
        )
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        self.speed_display = ttkb.Label(speed_frame, text=f"{self.pulse_interval.get()} μs")
        self.speed_display.pack(side="left", padx=10, pady=10)

        # --- Información del Sistema ---
        info_frame = ttkb.LabelFrame(left_frame, text="Información del Sistema", padding=20)
        info_frame.pack(padx=10, pady=10, fill="x")

        status_frame = ttkb.Frame(info_frame)
        status_frame.pack(pady=10, fill="x")

        mode_label = ttkb.Label(status_frame, text="Modo Actual:")
        mode_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        mode_value = ttkb.Label(
            status_frame,
            textvariable=self.mode,
            foreground="#a020f0",
            font=("Consolas", 12, "bold")
        )
        mode_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        distance_label = ttkb.Label(status_frame, text="Distancia Actual:")
        distance_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        distance_value = ttkb.Label(
            status_frame,
            textvariable=self.current_distance,
            foreground="#00ff00",
            font=("Consolas", 12, "bold")
        )
        distance_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")

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

        # --- Logs del Sistema ---
        log_frame = ttkb.LabelFrame(right_frame, text="Logs del Sistema", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.text_log = tk.Text(
            log_frame,
            state='disabled',
            wrap='word',
            height=30,
            bg="#1e1e1e",
            fg="#ffffff",
            font=("Consolas", 10, "bold")
        )
        self.text_log.pack(side="left", fill="both", expand=True)

        scrollbar = ttkb.Scrollbar(log_frame, orient="vertical", command=self.text_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_log.configure(yscrollcommand=scrollbar.set)

        logger.info("Widgets creados y organizados.")

    def enqueue_serial_data(self, data: str) -> None:
        self.queue.put(data)

    def process_queue(self) -> None:
        try:
            while not self.queue.empty():
                data = self.queue.get_nowait()
                self.handle_serial_data(data)
        except queue.Empty:
            pass
        except Exception as e:
            logger.error(f"Error al procesar la cola: {e}")
            self.log_message(f"Error al procesar la cola: {e}", level="ERROR")
        finally:
            self.master.after(100, self.process_queue)

    # --- Manejo de eventos de teclas con repetición ---
    def on_up_press(self, event: Optional[tk.Event] = None) -> None:
        if not self.up_pressed:
            self.up_pressed = True
            logger.debug("Tecla 'Subir' presionada.")
            self.start_up_repeat()

    def start_up_repeat(self) -> None:
        if self.up_pressed:
            self.move_up()  # Enviar comando "UP"
            self.up_repeat_job = self.master.after(100, self.start_up_repeat)

    def on_up_release(self, event: Optional[tk.Event] = None) -> None:
        if self.up_pressed:
            self.up_pressed = False
            if self.up_repeat_job:
                self.master.after_cancel(self.up_repeat_job)
                self.up_repeat_job = None
            logger.debug("Tecla 'Subir' liberada.")
            self.stop_motor()

    def on_down_press(self, event: Optional[tk.Event] = None) -> None:
        if not self.down_pressed:
            self.down_pressed = True
            logger.debug("Tecla 'Bajar' presionada.")
            self.start_down_repeat()

    def start_down_repeat(self) -> None:
        if self.down_pressed:
            self.move_down()  # Enviar comando "DOWN"
            self.down_repeat_job = self.master.after(100, self.start_down_repeat)

    def on_down_release(self, event: Optional[tk.Event] = None) -> None:
        if self.down_pressed:
            self.down_pressed = False
            if self.down_repeat_job:
                self.master.after_cancel(self.down_repeat_job)
                self.down_repeat_job = None
            logger.debug("Tecla 'Bajar' liberada.")
            self.stop_motor()

    # --- Funciones de comandos ---
    def activate_auto(self) -> None:
        success = self.send_command("AUTO")
        if success:
            self.mode.set("Automático")
            self.system_status.set("Modo Automático Activado")
            self.system_status_label.config(foreground="#a020f0")
            self.log_message("Activando modo automático.", level="INFO")
            logger.info("Modo automático activado.")

    def activate_manual(self) -> None:
        success = self.send_command("STOP")
        if success:
            self.mode.set("Manual")
            self.system_status.set("Modo Manual Activado")
            self.system_status_label.config(foreground="#00ffff")
            self.log_message("Modo manual activado. Motor detenido.", level="INFO")
            logger.info("Modo manual activado.")

    def move_up(self) -> None:
        success = self.send_command("UP")
        if success:
            self.mode.set("Manual")
            self.log_message("Moviendo hacia arriba.", level="INFO")
            logger.info("Comando 'UP' enviado.")

    def move_down(self) -> None:
        success = self.send_command("DOWN")
        if success:
            self.mode.set("Manual")
            self.log_message("Moviendo hacia abajo.", level="INFO")
            logger.info("Comando 'DOWN' enviado.")

    def stop_motor(self) -> None:
        success = self.send_command("STOP")
        if success:
            self.mode.set("Manual")
            self.log_message("Motor detenido.", level="INFO")
            logger.info("Comando 'STOP' enviado.")

    def update_speed(self, event: Optional[tk.Event] = None) -> None:
        speed = self.pulse_interval.get()
        self.speed_display.config(text=f"{int(speed)} μs")
        success = self.send_command(f"SET_SPEED {int(speed)}")
        if success:
            self.log_message(f"Ajustando velocidad a {int(speed)} μs.", level="INFO")
            logger.info(f"Comando 'SET_SPEED {int(speed)}' enviado.")

    def handle_serial_data(self, data: str) -> None:
        logger.debug(f"Datos recibidos: {data}")
        if "Distancia actual" in data:
            try:
                distance_str = data.split(":")[-1].strip().replace(" cm", "")
                distance = float(distance_str)
                self.current_distance.set(f"{distance} cm")
                self.log_message(f"Distancia: {distance} cm", level="INFO")
                logger.info(f"Distancia actualizada a {distance} cm.")
            except ValueError:
                self.log_message(f"Error al parsear distancia: {data}", level="ERROR")
                logger.error(f"Error al parsear distancia: {data}")
        elif "Velocidad actual" in data:
            try:
                speed_str = data.split(":")[-1].strip().replace(" μs", "")
                speed = int(speed_str)
                self.pulse_interval.set(speed)
                self.speed_display.config(text=f"{speed} μs")
                self.log_message(f"Velocidad: {speed} μs", level="INFO")
                logger.info(f"Velocidad actualizada a {speed} μs.")
            except ValueError:
                self.log_message(f"Error al parsear velocidad: {data}", level="ERROR")
                logger.error(f"Error al parsear velocidad: {data}")
        elif "Motor detenido" in data:
            self.mode.set("Manual")
            self.log_message("Motor detenido por Arduino.", level="INFO")
            logger.info("Motor detenido por Arduino.")
        elif "Activando modo automático" in data:
            self.mode.set("Automático")
            self.system_status.set("Modo Automático Activado")
            self.system_status_label.config(foreground="#a020f0")
            self.log_message("Modo automático activado por Arduino.", level="INFO")
            logger.info("Modo automático activado por Arduino.")
        elif "Desactivando modo automático" in data:
            self.mode.set("Manual")
            self.system_status.set("Modo Manual Activado")
            self.system_status_label.config(foreground="#00ffff")
            self.log_message("Modo automático desactivado por Arduino.", level="INFO")
            logger.info("Modo automático desactivado por Arduino.")
        elif "Bomba de vacío encendida." in data:
            self.log_message("Bomba de vacío encendida.", level="INFO")
            logger.info("Bomba de vacío encendida.")
        elif "Bomba de vacío apagada." in data:
            self.log_message("Bomba de vacío apagada.", level="INFO")
            logger.info("Bomba de vacío apagada.")
        else:
            self.log_message(data, level="DEBUG")
            logger.info(f"Mensaje recibido: {data}")

    def log_message(self, message: str, level: str = "INFO") -> None:
        color_map = {
            "INFO": "#ffffff",
            "DEBUG": "#a9a9a9",
            "WARNING": "#ffa500",
            "ERROR": "#ff0000"
        }
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
        logger.debug(f"Mensaje logueado: {message}")

    def pump_on(self) -> None:
        success = self.send_command("PUMP_ON")
        if success:
            self.log_message("Encendiendo bomba de vacío.", level="INFO")
            logger.info("Comando 'PUMP_ON' enviado.")

    def pump_off(self) -> None:
        success = self.send_command("PUMP_OFF")
        if success:
            self.log_message("Apagando bomba de vacío.", level="INFO")
            logger.info("Comando 'PUMP_OFF' enviado.")

    def on_closing(self) -> None:
        if messagebox.askokcancel("Salir", "¿Quieres salir de la aplicación?"):
            self.send_command("STOP")
            self.serial.disconnect()
            logger.info("Aplicación cerrada por el usuario.")
            self.stop_event.set()
            self.command_thread.join(timeout=1)
            self.master.destroy()

    def send_command(self, command: str, priority: int = 1) -> bool:
        current_time = time.time()
        if current_time - self.last_command_time < self.command_throttle:
            logger.warning(f"Comando '{command}' descartado por throttle.")
            self.log_message(f"Comando '{command}' descartado por throttle.", level="WARNING")
            return False

        with self.command_lock:
            self.command_queue.put((priority, current_time, command))
            self.last_command_time = current_time
        return True

    def process_command_queue(self) -> None:
        while not self.stop_event.is_set():
            try:
                priority, timestamp, command = self.command_queue.get_nowait()
                if time.time() - timestamp > 5.0:
                    logger.warning(f"Comando '{command}' descartado por antigüedad.")
                    self.log_message(f"Comando '{command}' descartado por antigüedad.", level="WARNING")
                    continue

                success = self.serial.send_command(command)
                if not success:
                    self.handle_command_error(command)
            except queue.Empty:
                pass
            except Exception as e:
                logger.error(f"Error procesando comando: {e}")
                self.log_message(f"Error procesando comando: {e}", level="ERROR")
            time.sleep(0.05)

    def check_system_health(self) -> None:
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()

        if cpu_usage > 80 or memory_info.percent > 80:
            self.system_health = max(0, self.system_health - 10)
            self.log_message(
                f"Uso elevado de recursos: CPU {cpu_usage}%, Memoria {memory_info.percent}%",
                level="WARNING"
            )
            logger.warning(f"Uso elevado: CPU {cpu_usage}%, Memoria {memory_info.percent}%")

        if self.error_count > 5:
            self.system_health = max(0, self.system_health - 10)
            self.attempt_system_recovery()

        if not self.serial.is_connected:
            self.attempt_reconnect()

        self.master.after(5000, self.check_system_health)

    def attempt_system_recovery(self) -> None:
        self.log_message("Intentando recuperar el sistema...", level="WARNING")
        logger.info("Intentando recuperación del sistema.")
        self.stop_motor()
        self.error_count = 0
        self.system_health = min(100, self.system_health + 20)
        self.log_message("Recuperación exitosa.", level="INFO")
        logger.info("Recuperación del sistema exitosa.")

    def attempt_reconnect(self) -> None:
        if self.reconnect_attempts < 3:
            self.log_message("Intentando reconectar...", level="WARNING")
            logger.info("Intentando reconectar al dispositivo serial.")
            success = self.serial.connect()
            if success:
                self.reconnect_attempts = 0
                self.log_message("¡Reconexión exitosa!", level="INFO")
                logger.info("Reconexión exitosa.")
                self.system_status.set("Operando en Modo Real")
                self.system_status_label.config(foreground="#ff00ff")
            else:
                self.reconnect_attempts += 1
                self.log_message(
                    f"Reconexión fallida. Intento {self.reconnect_attempts}/3.",
                    level="ERROR"
                )
                logger.warning(f"Reconexión fallida. Intento {self.reconnect_attempts}/3.")
        else:
            self.log_message("Máximo de intentos de reconexión alcanzado.", level="ERROR")
            logger.error("Se alcanzó el máximo de intentos de reconexión.")

    def handle_command_error(self, command: str) -> None:
        self.error_count += 1
        self.last_error_time = time.time()
        self.log_message(f"Comando fallido: {command}", level="ERROR")
        logger.error(f"Fallo en comando: {command}")

        if self.error_count <= 3:
            retry_priority = 5  # Menor prioridad en reintentos
            self.send_command(command, priority=retry_priority)
            self.log_message(f"Reintentando comando: {command}", level="WARNING")
            logger.info(f"Reintentando comando: {command}")
        else:
            self.log_message("Se alcanzó el límite de reintentos para comandos.", level="ERROR")
            logger.error("Límite de reintentos alcanzado.")
