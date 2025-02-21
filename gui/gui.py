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

# ------------------- Logging Configuration -------------------
logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# -------------------------------------------------------------

class CreateToolTip:
    """Clase para crear un tooltip en un widget."""
    def __init__(self, widget: tk.Widget, text: str = 'widget info') -> None:
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
        if self.tw:
            self.tw.destroy()
            self.tw = None

class MotorControlGUI:
    """
    Interfaz de control para el motor y la bomba de vacío.
    Muestra información esencial (modo, distancia, velocidad) y proporciona botones
    para activar los distintos modos de operación, control manual y de la bomba.
    """
    def __init__(self, master: tk.Tk, serial_comm: SerialInterface) -> None:
        self.master = master
        self.serial = serial_comm
        self.serial.register_callback(self.enqueue_serial_data)

        # Tema
        self.style = ttkb.Style(theme='superhero')
        logger.info("Inicializando la interfaz GUI.")

        # Variables de estado
        self.mode = tk.StringVar(value="Manual")
        self.current_distance = tk.StringVar(value="Desconocida")
        self.pulse_interval = tk.IntVar(value=800)  # en microsegundos (para el slider)
        self.system_status = tk.StringVar(
            value="Operando en Modo Real" if self.serial.is_connected else "Desconectado"
        )

        # Control manual
        self.up_pressed = False
        self.down_pressed = False

        # Cola de comunicación interna
        self.queue = queue.Queue()

        set_styles()
        self.create_widgets()
        self.master.after(100, self.process_queue)
        logger.info("Interfaz GUI inicializada.")

        # Cola de comandos
        self.command_queue = queue.Queue()
        self.command_lock = threading.Lock()
        self.last_command_time = 0.0
        self.command_throttle = 0.1

        # Variables de monitoreo
        self.system_health = 100.0
        self.error_count = 0
        self.last_error_time = 0.0
        self.reconnect_attempts = 0

        self.stop_event = threading.Event()
        self.command_thread = threading.Thread(target=self.process_command_queue, daemon=True)
        self.command_thread.start()

        self.master.after(5000, self.check_system_health)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self) -> None:
        # Diseño simplificado: Panel superior con información, fila de botones y slider,
        # y área de logs en la parte inferior.
        main_frame = ttkb.Frame(self.master, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Panel de información
        info_frame = ttkb.Frame(main_frame)
        info_frame.pack(fill="x", pady=5)

        ttkb.Label(info_frame, text="Modo:").pack(side="left", padx=5)
        ttkb.Label(info_frame, textvariable=self.mode, foreground="#a020f0", font=("Consolas", 12, "bold")).pack(side="left", padx=5)

        ttkb.Label(info_frame, text="Distancia:").pack(side="left", padx=5)
        ttkb.Label(info_frame, textvariable=self.current_distance, foreground="#00ff00", font=("Consolas", 12, "bold")).pack(side="left", padx=5)

        ttkb.Label(info_frame, text="Estado:").pack(side="left", padx=5)
        ttkb.Label(info_frame, textvariable=self.system_status, foreground="#ff00ff", font=("Consolas", 12, "bold")).pack(side="left", padx=5)

        # Panel de botones
        button_frame = ttkb.Frame(main_frame)
        button_frame.pack(fill="x", pady=5)

        btn_auto = ttkb.Button(button_frame, text="Modo Automático", command=self.activate_auto)
        btn_auto.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_auto, "Activa el modo automático del motor.")

        btn_manual = ttkb.Button(button_frame, text="Modo Manual", command=self.activate_manual)
        btn_manual.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_manual, "Activa el modo manual del motor.")

        btn_up = ttkb.Button(button_frame, text="Subir")
        btn_up.pack(side="left", padx=5, pady=5)
        # Invertimos: tecla Up llama a on_down_press
        btn_up.bind('<ButtonPress>', self.on_down_press)
        btn_up.bind('<ButtonRelease>', self.on_down_release)
        CreateToolTip(btn_up, "Mueve el motor hacia abajo mientras se mantiene presionado.")

        btn_down = ttkb.Button(button_frame, text="Bajar")
        btn_down.pack(side="left", padx=5, pady=5)
        # Tecla Down llama a on_up_press
        btn_down.bind('<ButtonPress>', self.on_up_press)
        btn_down.bind('<ButtonRelease>', self.on_up_release)
        CreateToolTip(btn_down, "Mueve el motor hacia arriba mientras se mantiene presionado.")

        btn_stop = ttkb.Button(button_frame, text="Detener", command=self.stop_motor)
        btn_stop.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_stop, "Detiene el motor inmediatamente.")

        btn_pump_on = ttkb.Button(button_frame, text="Encender Bomba", command=self.pump_on)
        btn_pump_on.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_pump_on, "Enciende la bomba de vacío.")

        btn_pump_off = ttkb.Button(button_frame, text="Apagar Bomba", command=self.pump_off)
        btn_pump_off.pack(side="left", padx=5, pady=5)
        CreateToolTip(btn_pump_off, "Apaga la bomba de vacío.")

        # Panel del slider de velocidad
        speed_frame = ttkb.Frame(main_frame)
        speed_frame.pack(fill="x", pady=5)
        ttkb.Label(speed_frame, text="Intervalo (μs):").pack(side="left", padx=5)
        self.speed_slider = ttkb.Scale(speed_frame, from_=20, to=2000, orient="horizontal", variable=self.pulse_interval, command=self.update_speed)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.speed_display = ttkb.Label(speed_frame, text=f"{self.pulse_interval.get()} μs")
        self.speed_display.pack(side="left", padx=5)

        # Área de logs (menos verbosa; solo se muestran errores y cambios de modo)
        log_frame = ttkb.LabelFrame(main_frame, text="Logs", padding=10)
        log_frame.pack(fill="both", expand=True, pady=5)
        self.text_log = tk.Text(log_frame, state='disabled', wrap='word', height=10, bg="#1e1e1e", fg="#ffffff", font=("Consolas", 10))
        self.text_log.pack(side="left", fill="both", expand=True)
        scrollbar = ttkb.Scrollbar(log_frame, orient="vertical", command=self.text_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_log.configure(yscrollcommand=scrollbar.set)

        # Asignación de teclas (invertida)
        self.master.bind("<KeyPress-Up>", self.on_down_press)
        self.master.bind("<KeyRelease-Up>", self.on_down_release)
        self.master.bind("<KeyPress-Down>", self.on_up_press)
        self.master.bind("<KeyRelease-Down>", self.on_up_release)
        self.master.focus_set()
        logger.info("Widgets de la GUI creados y organizados.")

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
            logger.error(f"Error procesando cola: {e}")
            self.log_message(f"Error procesando cola: {e}", level="ERROR")
        finally:
            self.master.after(100, self.process_queue)

    # Inversión de eventos: Tecla Up -> función para bajar, Tecla Down -> función para subir
    def on_down_press(self, event: Optional[tk.Event] = None) -> None:
        if not self.down_pressed:
            self.down_pressed = True
            logger.debug("Tecla Up presionada (accion: bajar).")
            self.move_down()

    def on_down_release(self, event: Optional[tk.Event] = None) -> None:
        if self.down_pressed:
            self.down_pressed = False
            logger.debug("Tecla Up liberada (accion: detener).")
            self.stop_motor()

    def on_up_press(self, event: Optional[tk.Event] = None) -> None:
        if not self.up_pressed:
            self.up_pressed = True
            logger.debug("Tecla Down presionada (accion: subir).")
            self.move_up()

    def on_up_release(self, event: Optional[tk.Event] = None) -> None:
        if self.up_pressed:
            self.up_pressed = False
            logger.debug("Tecla Down liberada (accion: detener).")
            self.stop_motor()

    def activate_auto(self) -> None:
        success = self.send_command("AUTO")
        if success:
            self.mode.set("Automático")
            self.system_status.set("Modo Automático Activado")
            self.log_message("Modo automático activado.", level="INFO")
            logger.info("Modo automático activado.")

    def activate_manual(self) -> None:
        success = self.send_command("STOP")
        if success:
            self.mode.set("Manual")
            self.system_status.set("Modo Manual Activado")
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
        # Conversión: steps/s = 1,000,000 / pulse_interval (μs)
        pulse_interval = self.pulse_interval.get()
        if pulse_interval < 1:
            pulse_interval = 1
        steps_per_second = int(1_000_000 / pulse_interval)
        self.speed_display.config(text=f"{int(pulse_interval)} μs")
        success = self.send_command(f"SET_SPEED {steps_per_second}")
        if success:
            self.log_message(f"Velocidad ajustada: {steps_per_second} pasos/s (Intervalo: {pulse_interval} μs).", level="INFO")
            logger.info(f"Comando 'SET_SPEED {steps_per_second}' enviado.")

    def handle_serial_data(self, data: str) -> None:
        # Filtramos los logs del sensor para evitar saturación; actualizamos etiquetas sin loguear cada lectura
        logger.debug(f"Mensaje recibido: {data}")
        if "Distancia actual" in data:
            try:
                distance_str = data.split(":")[-1].strip().replace(" cm", "")
                distance = float(distance_str)
                self.current_distance.set(f"{distance} cm")
            except ValueError:
                self.log_message(f"Error al parsear distancia: {data}", level="ERROR")
        elif "Velocidad actual" in data:
            try:
                speed_str = data.split(":")[-1].strip().replace(" μs", "")
                speed = int(speed_str)
                self.pulse_interval.set(speed)
                self.speed_display.config(text=f"{speed} μs")
            except ValueError:
                self.log_message(f"Error al parsear velocidad: {data}", level="ERROR")
        elif "Motor detenido" in data:
            self.mode.set("Manual")
            self.log_message("Motor detenido por Arduino.", level="INFO")
        elif "Activando modo automático" in data:
            self.mode.set("Automático")
            self.system_status.set("Modo Automático Activado")
            self.log_message("Modo automático activado por Arduino.", level="INFO")
        elif "Desactivando modo automático" in data:
            self.mode.set("Manual")
            self.system_status.set("Modo Manual Activado")
            self.log_message("Modo automático desactivado por Arduino.", level="INFO")
        elif "Bomba de vacío encendida" in data:
            self.log_message("Bomba de vacío encendida.", level="INFO")
        elif "Bomba de vacío apagada" in data:
            self.log_message("Bomba de vacío apagada.", level="INFO")
        else:
            # Para mensajes no críticos, solo se registra en DEBUG
            logger.debug(f"Mensaje sin clasificar: {data}")

    def log_message(self, message: str, level: str = "INFO") -> None:
        # Solo mostrar mensajes de INFO, WARNING y ERROR en la interfaz (minimizando logs del sensor)
        if level in ["DEBUG"]:
            return
        color_map = {
            "INFO": "#ffffff",
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
        logger.info(f"Log: {message}")

    def pump_on(self) -> None:
        success = self.send_command("PUMP_ON")
        if success:
            self.log_message("Bomba de vacío encendida.", level="INFO")
            logger.info("Comando 'PUMP_ON' enviado.")

    def pump_off(self) -> None:
        success = self.send_command("PUMP_OFF")
        if success:
            self.log_message("Bomba de vacío apagada.", level="INFO")
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
                if (time.time() - timestamp) > 5.0:
                    logger.warning(f"Comando '{command}' descartado por antigüedad.")
                    self.log_message(f"Comando '{command}' descartado por antigüedad.", level="WARNING")
                    continue
                success = self.serial.send_command(command)
                if not success:
                    self.log_message(f"Error enviando '{command}'", level="ERROR")
                # No es necesario registrar cada comando exitoso en el log de la GUI
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
            self.log_message(f"Uso elevado: CPU {cpu_usage}%, Memoria {memory_info.percent}%", level="WARNING")
            logger.warning(f"Uso elevado: CPU {cpu_usage}%, Memoria {memory_info.percent}%")
        if self.error_count > 5:
            self.system_health = max(0, self.system_health - 10)
            self.log_message("Recuperando sistema...", level="WARNING")
            self.stop_motor()
            self.error_count = 0
            self.system_health = min(100, self.system_health + 20)
            self.log_message("Recuperación exitosa.", level="INFO")
            logger.info("Recuperación exitosa.")
        if not self.serial.is_connected:
            self.attempt_reconnect()
        self.master.after(5000, self.check_system_health)

    def attempt_reconnect(self) -> None:
        if self.reconnect_attempts < 3:
            self.log_message("Intentando reconexión...", level="WARNING")
            logger.info("Intentando reconectar al serial.")
            success = self.serial.connect()
            if success:
                self.reconnect_attempts = 0
                self.log_message("Reconexión exitosa.", level="INFO")
                logger.info("Reconexión exitosa.")
                self.system_status.set("Operando en Modo Real")
            else:
                self.reconnect_attempts += 1
                self.log_message(f"Reconexión fallida. Intento {self.reconnect_attempts}/3.", level="ERROR")
                logger.warning(f"Reconexión fallida. Intento {self.reconnect_attempts}/3.")
        else:
            self.log_message("Máximo de reconexiones alcanzado.", level="ERROR")
            logger.error("Máximo de reconexiones alcanzado.")

    def handle_command_error(self, command: str) -> None:
        self.error_count += 1
        self.last_error_time = time.time()
        self.log_message(f"Comando fallido: {command}", level="ERROR")
        logger.error(f"Comando fallido: {command}")
        if self.error_count <= 3:
            self.send_command(command, priority=5)
            self.log_message(f"Reintentando: {command}", level="WARNING")
            logger.info(f"Reintentando comando: {command}")
        else:
            self.log_message("Límite de reintentos alcanzado.", level="ERROR")
            logger.error("Límite de reintentos alcanzado.")

