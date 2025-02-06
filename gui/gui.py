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

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Definición de códigos de comando (deben coincidir con el firmware)
CMD_AUTO      = 0xA0
CMD_UP        = 0xA1
CMD_DOWN      = 0xA2
CMD_STOP      = 0xA3
CMD_SET_SPEED = 0xA4

class CreateToolTip:
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
    def __init__(self, master: tk.Tk, serial_comm: SerialInterface) -> None:
        self.master = master
        self.serial = serial_comm
        self.serial.register_callback(self.enqueue_serial_data)
        self.style = ttkb.Style(theme='superhero')
        logger.info("Inicializando GUI.")

        self.mode = tk.StringVar(value="Manual")
        self.current_distance = tk.StringVar(value="Desconocida")
        self.pulse_interval = tk.IntVar(value=800)
        self.system_status = tk.StringVar(
            value="Operando en Modo Real" if self.serial.is_connected else "Modo Simulación"
        )

        self.up_pressed = False
        self.down_pressed = False
        self.up_repeat_job = None
        self.down_repeat_job = None

        self.queue = queue.Queue()
        set_styles()
        self.create_widgets()
        self.master.after(100, self.process_queue)
        logger.info("GUI inicializada.")

        self.command_lock = threading.Lock()
        self.last_command_time = 0.0
        self.command_throttle = 0.1

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
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

        # Controles del Motor
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
        CreateToolTip(btn_up, "Mueve el motor hacia arriba mientras se presione.")
        btn_down = ttkb.Button(control_frame, text="Bajar")
        btn_down.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        btn_down.bind('<ButtonPress>', self.on_down_press)
        btn_down.bind('<ButtonRelease>', self.on_down_release)
        CreateToolTip(btn_down, "Mueve el motor hacia abajo mientras se presione.")
        btn_stop = ttkb.Button(control_frame, text="Detener", command=self.stop_motor)
        btn_stop.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        CreateToolTip(btn_stop, "Detiene el motor inmediatamente.")

        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        # Ajuste de Velocidad
        speed_frame = ttkb.LabelFrame(left_frame, text="Ajuste de Velocidad", padding=20)
        speed_frame.pack(padx=10, pady=10, fill="x")
        speed_label = ttkb.Label(speed_frame, text="Intervalo de Pulsos (μs):")
        speed_label.pack(side="left", padx=10, pady=10)
        self.speed_slider = ttkb.Scale(speed_frame, from_=200, to=2000,
                                       orient="horizontal", variable=self.pulse_interval,
                                       command=self.update_speed)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.speed_display = ttkb.Label(speed_frame, text="800 μs")
        self.speed_display.pack(side="left", padx=10, pady=10)

        # Información del Sistema
        info_frame = ttkb.LabelFrame(left_frame, text="Información del Sistema", padding=20)
        info_frame.pack(padx=10, pady=10, fill="x")
        status_frame = ttkb.Frame(info_frame)
        status_frame.pack(pady=10, fill="x")
        mode_label = ttkb.Label(status_frame, text="Modo Actual:")
        mode_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        mode_value = ttkb.Label(status_frame, textvariable=self.mode,
                                foreground="#a020f0", font=("Consolas", 12, "bold"))
        mode_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        distance_label = ttkb.Label(status_frame, text="Distancia Actual:")
        distance_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        distance_value = ttkb.Label(status_frame, textvariable=self.current_distance,
                                    foreground="#00ff00", font=("Consolas", 12, "bold"))
        distance_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        system_status_frame = ttkb.Frame(info_frame)
        system_status_frame.pack(pady=10, fill="x")
        status_label = ttkb.Label(system_status_frame, text="Estado del Sistema:",
                                  font=("Consolas", 12, "bold"))
        status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.system_status_label = ttkb.Label(system_status_frame, textvariable=self.system_status,
                                              foreground="#ff00ff", font=("Consolas", 12, "bold"))
        self.system_status_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Logs del Sistema
        log_frame = ttkb.LabelFrame(right_frame, text="Logs del Sistema", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.text_log = tk.Text(log_frame, state='disabled', wrap='word',
                                 height=30, bg="#1e1e1e", fg="#ffffff",
                                 font=("Consolas", 10, "bold"))
        self.text_log.pack(side="left", fill="both", expand=True)
        scrollbar = ttkb.Scrollbar(log_frame, orient="vertical", command=self.text_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_log.configure(yscrollcommand=scrollbar.set)
        logger.info("Widgets creados.")

    def enqueue_serial_data(self, data: bytes) -> None:
        self.queue.put(data)

    def process_queue(self) -> None:
        try:
            while not self.queue.empty():
                data = self.queue.get_nowait()
                self.handle_serial_data(data)
        except Exception as e:
            logger.error(f"Error al procesar la cola: {e}")
        finally:
            self.master.after(100, self.process_queue)

    def on_up_press(self, event: Optional[tk.Event] = None) -> None:
        if not self.up_pressed:
            self.up_pressed = True
            logger.debug("Tecla 'Subir' presionada.")
            self.start_up_repeat()

    def start_up_repeat(self) -> None:
        if self.up_pressed:
            self.move_up()
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
            self.move_down()
            self.down_repeat_job = self.master.after(100, self.start_down_repeat)

    def on_down_release(self, event: Optional[tk.Event] = None) -> None:
        if self.down_pressed:
            self.down_pressed = False
            if self.down_repeat_job:
                self.master.after_cancel(self.down_repeat_job)
                self.down_repeat_job = None
            logger.debug("Tecla 'Bajar' liberada.")
            self.stop_motor()

    # Funciones de comando: se envían comandos binarios
    def activate_auto(self) -> None:
        if self.send_command(CMD_AUTO, 0x00):
            self.mode.set("Automático")
            self.system_status.set("Modo Automático Activado")

    def activate_manual(self) -> None:
        if self.send_command(CMD_STOP, 0x00):
            self.mode.set("Manual")
            self.system_status.set("Modo Manual Activado")

    def move_up(self) -> None:
        if self.send_command(CMD_UP, 0x00):
            self.mode.set("Manual")

    def move_down(self) -> None:
        if self.send_command(CMD_DOWN, 0x00):
            self.mode.set("Manual")

    def stop_motor(self) -> None:
        if self.send_command(CMD_STOP, 0x00):
            self.mode.set("Manual")

    def update_speed(self, event: Optional[tk.Event] = None) -> None:
        speed = self.pulse_interval.get()
        self.speed_display.config(text=f"{int(speed)} μs")
        if self.send_command(CMD_SET_SPEED, int(speed)):
            logger.info(f"Comando SET_SPEED {int(speed)} enviado.")

    def handle_serial_data(self, data: bytes) -> None:
        if len(data) != 2:
            logger.error("Paquete recibido con longitud incorrecta.")
            return
        msg = f"Recibido: {data[0]:02X} {data[1]:02X}"
        logger.info(msg)
        self.text_log.configure(state='normal')
        self.text_log.insert(tk.END, msg + "\n")
        self.text_log.configure(state='disabled')
        self.text_log.see(tk.END)

    def send_command(self, cmd: int, payload: int) -> bool:
        import time
        current_time = time.time()
        if current_time - self.last_command_time < self.command_throttle:
            logger.warning(f"Comando {cmd:02X} descartado por throttle.")
            return False
        with self.command_lock:
            self.last_command_time = current_time
        return self.serial.send_command(cmd, payload)

    def on_closing(self) -> None:
        if messagebox.askokcancel("Salir", "¿Quieres salir de la aplicación?"):
            self.send_command(CMD_STOP, 0x00)
            self.serial.disconnect()
            self.master.destroy()

def main():
    root = tk.Tk()
    app = MotorControlGUI(root, SerialInterface())
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
