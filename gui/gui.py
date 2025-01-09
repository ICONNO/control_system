# gui/gui.py

import tkinter as tk
from tkinter import messagebox, ttk
import threading
import time
from .serial_comm import SerialInterface, MockSerialComm  # Importación relativa
import logging
import queue
from .matplotlib_gauge import MatplotlibGauge  # Importación relativa
from .styles import set_styles  # Importar la función de estilos
import psutil

class MotorControlGUI:
    """
    Clase principal para la interfaz gráfica de control del motor paso a paso.
    """
    def __init__(self, master, serial_comm):
        self.master = master
        self.serial = serial_comm
        self.serial.register_callback(self.enqueue_serial_data)

        # Configuración de logging
        logging.basicConfig(filename='logs/app.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Inicializando la interfaz GUI.")

        # Variables de estado
        self.mode = tk.StringVar(value="Manual")
        self.current_distance = tk.StringVar(value="Desconocida")
        self.pulse_interval = tk.IntVar(value=800)  # Valor inicial coherente con la etiqueta
        self.system_status = tk.StringVar(value="Operando en Modo Real" if self.serial.is_connected else "Modo Simulación")

        # Variables para rastrear el estado de los botones
        self.up_pressed = False
        self.down_pressed = False

        # Cola para comunicación entre hilos
        self.queue = queue.Queue()

        # Aplicar estilos personalizados
        set_styles()

        # Crear Widgets de la GUI
        self.create_widgets()

        # Iniciar procesamiento de la cola
        self.master.after(100, self.process_queue)

        logging.info("Interfaz GUI inicializada correctamente.")
        
        # Command queue and thread safety
        self.command_queue = queue.PriorityQueue()
        self.command_lock = threading.Lock()
        self.last_command_time = 0
        self.command_throttle = 0.1  # seconds
        
        # System monitoring variables
        self.system_health = 100.0
        self.error_count = 0
        self.last_error_time = 0
        self.reconnect_attempts = 0
        
        # Start command processor thread
        self.command_thread = threading.Thread(target=self.process_command_queue, daemon=True)
        self.command_thread.start()
        
        # Start periodic health check
        self.master.after(5000, self.check_system_health)
        
        # Manejar el cierre de la ventana
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """
        Crea y organiza todos los widgets de la interfaz gráfica.
        """
        # Marco Principal Dividido en Izquierda y Derecha
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Marco Izquierdo para Controles y Gauges
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0,10))

        # Marco Derecho para Logs
        right_frame = ttk.Frame(main_frame, width=400)  # Establecer ancho aquí
        right_frame.pack(side="right", fill="both", expand=False)  # Eliminar width de pack

        # ------------------ Marco Izquierdo ------------------ #

        # Frame de Controles
        control_frame = ttk.LabelFrame(left_frame, text="Controles del Motor", padding=20)
        control_frame.pack(padx=10, pady=10, fill="x")

        # Botón para Modo Automático
        btn_auto = ttk.Button(control_frame, text="Modo Automático", command=self.activate_auto)
        btn_auto.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Botón para Modo Manual
        btn_manual = ttk.Button(control_frame, text="Modo Manual", command=self.activate_manual)
        btn_manual.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Botón para Mover hacia Arriba
        btn_up = ttk.Button(control_frame, text="Subir")
        btn_up.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        btn_up.bind('<ButtonPress>', self.on_up_press)
        btn_up.bind('<ButtonRelease>', self.on_up_release)

        # Botón para Mover hacia Abajo
        btn_down = ttk.Button(control_frame, text="Bajar")
        btn_down.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        btn_down.bind('<ButtonPress>', self.on_down_press)
        btn_down.bind('<ButtonRelease>', self.on_down_release)

        # Botón para Detener el Motor
        btn_stop = ttk.Button(control_frame, text="Detener", command=self.stop_motor)
        btn_stop.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # Botón para Encender la Bomba de Vacío
        btn_pump_on = ttk.Button(control_frame, text="Encender Bomba", command=self.pump_on)
        btn_pump_on.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        # Botón para Apagar la Bomba de Vacío
        btn_pump_off = ttk.Button(control_frame, text="Apagar Bomba", command=self.pump_off)
        btn_pump_off.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Configurar columnas para que los botones se expandan equitativamente
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        # Frame de Velocidad
        speed_frame = ttk.LabelFrame(left_frame, text="Ajuste de Velocidad", padding=20)
        speed_frame.pack(padx=10, pady=10, fill="x")

        # Etiqueta para el Control Deslizante de Velocidad
        speed_label = ttk.Label(speed_frame, text="Intervalo de Pulsos (μs):")
        speed_label.pack(side="left", padx=10, pady=10)

        # Control Deslizante para Ajustar la Velocidad
        self.speed_slider = ttk.Scale(
            speed_frame, 
            from_=200, 
            to=2000, 
            orient="horizontal",
            variable=self.pulse_interval, 
            command=self.update_speed
        )
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        # Etiqueta para Mostrar el Valor Actual del Control Deslizante
        self.speed_display = ttk.Label(speed_frame, text=f"{self.pulse_interval.get()} μs")
        self.speed_display.pack(side="left", padx=10, pady=10)

        # Frame de Gauges
        gauges_frame = ttk.LabelFrame(left_frame, text="Indicadores de Rendimiento", padding=20)
        gauges_frame.pack(padx=10, pady=10, fill="x")

        # Gauge para Distancia
        distance_gauge = MatplotlibGauge(gauges_frame, label="Distancia (cm)", min_value=0, max_value=50, initial_value=0)
        distance_gauge.pack(side="left", padx=20, pady=20)
        self.distance_gauge = distance_gauge

        # Gauge para Velocidad
        speed_gauge = MatplotlibGauge(gauges_frame, label="Velocidad (μs)", min_value=200, max_value=2000, initial_value=self.pulse_interval.get())
        speed_gauge.pack(side="left", padx=20, pady=20)
        self.speed_gauge = speed_gauge

        # Frame de Información del Sistema
        info_frame = ttk.LabelFrame(left_frame, text="Información del Sistema", padding=20)
        info_frame.pack(padx=10, pady=10, fill="x")

        # Indicadores de Estado
        status_frame = ttk.Frame(info_frame)
        status_frame.pack(pady=10, fill="x")

        # Etiqueta y Valor para Modo Actual
        mode_label = ttk.Label(status_frame, text="Modo Actual:")
        mode_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        mode_value = ttk.Label(status_frame, textvariable=self.mode, foreground="cyan", font=("Arial", 12, "bold"))
        mode_value.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Etiqueta y Valor para Distancia Actual
        distance_label = ttk.Label(status_frame, text="Distancia Actual:")
        distance_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        distance_value = ttk.Label(status_frame, textvariable=self.current_distance, foreground="lime", font=("Arial", 12, "bold"))
        distance_value.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Frame de Estado del Sistema
        system_status_frame = ttk.Frame(info_frame)
        system_status_frame.pack(pady=10, fill="x")

        status_label = ttk.Label(system_status_frame, text="Estado del Sistema:", font=("Arial", 12, "bold"))
        status_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.system_status_label = ttk.Label(system_status_frame, textvariable=self.system_status, foreground="magenta", font=("Arial", 12, "bold"))
        self.system_status_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # ------------------ Marco Derecho ------------------ #

        # Área de Texto para Logs
        log_frame = ttk.LabelFrame(right_frame, text="Logs del Sistema", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.text_log = tk.Text(log_frame, state='disabled', wrap='word', height=30, bg="#2e2e2e", fg="white")
        self.text_log.pack(side="left", fill="both", expand=True)

        # Scrollbar para el Área de Texto
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.text_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_log.configure(yscrollcommand=scrollbar.set)

        # ------------------ Vinculación de Eventos de Teclado ------------------ #

        # Vincular eventos de presión y liberación de teclas
        self.master.bind("<KeyPress-Up>", self.on_up_press)
        self.master.bind("<KeyRelease-Up>", self.on_up_release)
        self.master.bind("<KeyPress-Down>", self.on_down_press)
        self.master.bind("<KeyRelease-Down>", self.on_down_release)

        # Asegurar que la ventana tenga el foco para recibir eventos de teclado
        self.master.focus_set()

        logging.info("Widgets de la GUI creados y organizados.")

    def enqueue_serial_data(self, data):
        """
        Encola los datos recibidos desde el Arduino para su procesamiento en el hilo principal.
        """
        self.queue.put(data)

    def process_queue(self):
        """
        Procesa los datos encolados y los maneja adecuadamente.
        """
        try:
            while not self.queue.empty():
                data = self.queue.get_nowait()
                self.handle_serial_data(data)
        except queue.Empty:
            pass
        except Exception as e:
            logging.error(f"Error al procesar la cola: {e}")
        finally:
            self.master.after(100, self.process_queue)

    def on_up_press(self, event):
        """
        Maneja la presión del botón de subir.
        
        :param event: Evento de botón presionado.
        """
        if not self.up_pressed:
            self.up_pressed = True
            logging.debug("Botón 'Subir' presionado.")
            self.move_up()

    def on_up_release(self, event):
        """
        Maneja la liberación del botón de subir.
        
        :param event: Evento de botón liberado.
        """
        if self.up_pressed:
            self.up_pressed = False
            logging.debug("Botón 'Subir' liberado.")
            self.stop_motor()

    def on_down_press(self, event):
        """
        Maneja la presión del botón de bajar.
        
        :param event: Evento de botón presionado.
        """
        if not self.down_pressed:
            self.down_pressed = True
            logging.debug("Botón 'Bajar' presionado.")
            self.move_down()

    def on_down_release(self, event):
        """
        Maneja la liberación del botón de bajar.
        
        :param event: Evento de botón liberado.
        """
        if self.down_pressed:
            self.down_pressed = False
            logging.debug("Botón 'Bajar' liberado.")
            self.stop_motor()

    def activate_auto(self):
        """
        Activa el modo automático enviando el comando correspondiente al Arduino.
        """
        success = self.send_command("AUTO")
        if success:
            self.mode.set("Automático")
            self.system_status.set("Modo Automático Activado")
            self.system_status_label.config(foreground="orange")
            self.log_message("Activando modo automático.", color="blue")
            logging.info("Modo automático activado.")

    def activate_manual(self):
        """
        Activa el modo manual enviando el comando correspondiente al Arduino.
        """
        success = self.send_command("STOP")
        if success:
            self.mode.set("Manual")
            self.system_status.set("Modo Manual Activado")
            self.system_status_label.config(foreground="cyan")
            self.log_message("Modo manual activado. Motor detenido.", color="white")
            logging.info("Modo manual activado.")

    def move_up(self):
        """
        Envía el comando para mover el motor hacia arriba.
        """
        success = self.send_command("UP")
        if success:
            self.mode.set("Manual")
            self.log_message("Moviendo hacia arriba.", color="cyan")
            logging.info("Comando 'UP' enviado.")

    def move_down(self):
        """
        Envía el comando para mover el motor hacia abajo.
        """
        success = self.send_command("DOWN")
        if success:
            self.mode.set("Manual")
            self.log_message("Moviendo hacia abajo.", color="cyan")
            logging.info("Comando 'DOWN' enviado.")

    def stop_motor(self):
        """
        Envía el comando para detener el motor.
        """
        success = self.send_command("STOP")
        if success:
            self.mode.set("Manual")
            self.log_message("Motor detenido.", color="white")
            logging.info("Comando 'STOP' enviado.")

    def update_speed(self, event):
        """
        Actualiza la velocidad del motor según el valor del control deslizante.
        Envía el comando correspondiente al Arduino.
        """
        speed = self.pulse_interval.get()
        self.speed_display.config(text=f"{int(speed)} μs")
        self.speed_gauge.update_value(int(speed))
        success = self.send_command(f"SET_SPEED {int(speed)}")
        if success:
            self.log_message(f"Ajustando velocidad a {int(speed)} μs.", color="white")
            logging.info(f"Comando 'SET_SPEED {int(speed)}' enviado.")

    def handle_serial_data(self, data):
        """
        Maneja los datos recibidos desde el Arduino o desde la simulación.
        Actualiza la GUI en consecuencia.
        
        :param data: Cadena de texto recibida.
        """
        logging.debug(f"Datos recibidos para manejo: {data}")
        if "Distancia actual" in data:
            try:
                distance_str = data.split(":")[-1].strip().replace(" cm", "")
                distance = float(distance_str)
                distance = self.distance_gauge.clamp(distance)  # Asegura que esté dentro del rango
                self.current_distance.set(f"{distance} cm")
                self.distance_gauge.update_value(distance)
                self.log_message(f"Distancia: {distance} cm", color="white")
                logging.info(f"Distancia actualizada a {distance} cm.")
            except ValueError:
                self.log_message(f"Error al parsear distancia: {data}", color="red")
                logging.error(f"Error al parsear distancia: {data}")
        elif "Velocidad actual" in data:
            try:
                speed_str = data.split(":")[-1].strip().replace(" μs", "")
                speed = int(speed_str)
                speed = self.speed_gauge.clamp(speed)  # Asegura que esté dentro del rango
                self.speed_gauge.update_value(speed)
                self.pulse_interval.set(speed)  # Sincronizar el control deslizante
                self.speed_display.config(text=f"{speed} μs")
                self.log_message(f"Velocidad: {speed} μs", color="white")
                logging.info(f"Velocidad actualizada a {speed} μs.")
            except ValueError:
                self.log_message(f"Error al parsear velocidad: {data}", color="red")
                logging.error(f"Error al parsear velocidad: {data}")
        elif "Motor detenido" in data:
            self.mode.set("Manual")
            self.log_message("Motor detenido por Arduino.", color="white")
            logging.info("Motor detenido por Arduino.")
        elif "Activando modo automático" in data:
            self.mode.set("Automático")
            self.system_status.set("Modo Automático Activado")
            self.system_status_label.config(foreground="orange")
            self.log_message("Modo automático activado por Arduino.", color="blue")
            logging.info("Modo automático activado por Arduino.")
        elif "Desactivando modo automático" in data:
            self.mode.set("Manual")
            self.system_status.set("Modo Manual Activado")
            self.system_status_label.config(foreground="cyan")
            self.log_message("Modo automático desactivado por Arduino.", color="white")
            logging.info("Modo automático desactivado por Arduino.")
        elif "Bomba de vacío encendida." in data:
            self.log_message("Bomba de vacío encendida.", color="lime")
            logging.info("Bomba de vacío encendida.")
        elif "Bomba de vacío apagada." in data:
            self.log_message("Bomba de vacío apagada.", color="red")
            logging.info("Bomba de vacío apagada.")
        else:
            self.log_message(data, color="white")
            logging.info(f"Mensaje recibido: {data}")

    def log_message(self, message, color="white"):
        """
        Añade un mensaje al área de logs con un color específico.
        
        :param message: Mensaje a mostrar.
        :param color: Color del texto.
        """
        self.text_log.configure(state='normal')
        self.text_log.insert(tk.END, f"{message}\n")
        
        # Limitar el número de líneas en el log para optimizar el rendimiento
        max_lines = 1000
        current_lines = int(self.text_log.index('end-1c').split('.')[0])
        if current_lines > max_lines:
            # Eliminar las primeras 100 líneas para evitar el crecimiento indefinido
            self.text_log.delete('1.0', f"{100}.0")
        
        # Obtener la última línea añadida
        last_line = int(self.text_log.index("end-1c").split('.')[0])
        tag_name = f"log_{last_line}"
        self.text_log.tag_add(tag_name, f"{last_line}.0", f"{last_line}.end")
        self.text_log.tag_config(tag_name, foreground=color)
        self.text_log.configure(state='disabled')
        self.text_log.see(tk.END)
        logging.debug(f"Mensaje logueado: {message}")

    def pump_on(self):
        """
        Envía el comando para encender la bomba de vacío.
        """
        success = self.send_command("PUMP_ON")
        if success:
            self.log_message("Encendiendo bomba de vacío.", color="lime")
            logging.info("Comando 'PUMP_ON' enviado.")

    def pump_off(self):
        """
        Envía el comando para apagar la bomba de vacío.
        """
        success = self.send_command("PUMP_OFF")
        if success:
            self.log_message("Apagando bomba de vacío.", color="red")  # Corrección del error tipográfico
            logging.info("Comando 'PUMP_OFF' enviado.")

    def on_closing(self):
        """
        Maneja el cierre de la aplicación de manera segura.
        Envía el comando 'STOP' y cierra la comunicación serial.
        """
        if messagebox.askokcancel("Salir", "¿Quieres salir de la aplicación?"):
            self.send_command("STOP")
            self.serial.disconnect()
            logging.info("Aplicación cerrada por el usuario.")
            self.master.destroy()
            
    def send_command(self, command, priority=1):
        """
        Encola un comando con prioridad (1-5, menor número es mayor prioridad)
        """
        current_time = time.time()
        if current_time - self.last_command_time < self.command_throttle:
            logging.warning(f"Comando '{command}' descartado por throttle.")
            return False
            
        with self.command_lock:
            self.command_queue.put((priority, current_time, command))
            self.last_command_time = current_time
        return True
        
    def process_command_queue(self):
        """
        Procesa la cola de comandos y maneja los errores
        """
        while True:
            try:
                priority, timestamp, command = self.command_queue.get()
                if time.time() - timestamp > 5.0:  # Command too old
                    logging.warning(f"Comando '{command}' descartado por antigüedad.")
                    continue
                    
                success = self.serial.send_command(command)
                if not success:
                    self.handle_command_error(command)
                    
            except Exception as e:
                self.log_message(f"Error processing command: {e}", color="red")
                logging.error(f"Command processing error: {e}")
            time.sleep(0.05)  # Reducir el sleep para evitar sobrecarga

    def check_system_health(self):
        """
        Monitor system health and attempt recovery if needed
        """
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        
        if cpu_usage > 80 or memory_info.percent > 80:
            self.system_health = max(0, self.system_health - 10)
            self.log_message(f"High resource usage detected: CPU {cpu_usage}%, Memory {memory_info.percent}%", color="red")
            logging.warning(f"High resource usage: CPU {cpu_usage}%, Memory {memory_info.percent}%")
        
        if self.error_count > 5:
            self.system_health = max(0, self.system_health - 10)
            self.attempt_system_recovery()
        
        if not self.serial.is_connected:
            self.attempt_reconnect()
            
        self.master.after(5000, self.check_system_health)

    def attempt_system_recovery(self):
        """
        Intenta recuperar el sistema de errores
        """
        self.log_message("Intentando recuperar el sistema...", color="yellow")
        logging.info("Intentando recuperar el sistema.")
        self.stop_motor()
        self.error_count = 0
        self.system_health = min(100, self.system_health + 20)
        self.log_message("Recuperación exitosa.", color="green")
        logging.info("Recuperación del sistema exitosa.")
        
    def attempt_reconnect(self):
        """
        Intenta reconectarse al dispositivo serial
        """
        if self.reconnect_attempts < 3:
            self.log_message("Intentando reconectar...", color="yellow")
            logging.info("Intentando reconectar al dispositivo serial.")
            success = self.serial.connect()
            if success:
                self.reconnect_attempts = 0
                self.log_message("¡Reconexión exitosa!", color="green")
                logging.info("Reconexión exitosa al dispositivo serial.")
                # Actualizar el estado del sistema
                self.system_status.set("Operando en Modo Real")
                self.system_status_label.config(foreground="magenta")
            else:
                self.reconnect_attempts += 1
                self.log_message(f"Reconexión fallida. Intento {self.reconnect_attempts}/3.", color="red")
                logging.warning(f"Reconexión fallida. Intento {self.reconnect_attempts}/3.")
        else:
            self.log_message("Máximo de intentos de reconexión alcanzado.", color="red")
            logging.error("Máximo de intentos de reconexión alcanzado.")
        
    def handle_command_error(self, command):
        """
        Maneja comandos fallidos e implementa lógica de reintento
        """
        self.error_count += 1
        self.last_error_time = time.time()
        self.log_message(f"Comando fallido: {command}", color="red")
        logging.error(f"Comando fallido: {command}")
        
        if self.error_count <= 3:
            retry_priority = 5  # Lower priority
            self.send_command(command, priority=retry_priority)
            self.log_message(f"Reintentando comando: {command}", color="yellow")
            logging.info(f"Reintentando comando: {command}")
        else:
            self.log_message("Se alcanzó el límite de reintentos para comandos.", color="red")
            logging.error("Se alcanzó el límite de reintentos para comandos.")

# Ejemplo de cómo iniciar la aplicación
if __name__ == "__main__":
    import sys
    from .serial_comm import SerialInterface, MockSerialComm  # Asegúrate de tener estos módulos implementados

    def main():
        root = tk.Tk()
        root.title("Control de Motor y Bomba de Vacío")

        # Seleccionar la interfaz serial adecuada (real o mock)
        use_mock = False  # Cambia a True para usar MockSerialComm
        if use_mock:
            serial_comm = MockSerialComm()
            serial_comm.connect()
            logging.info("Modo simulación activado.")
        else:
            serial_comm = SerialInterface(port='COM3', baudrate=9600)  # Ajusta el puerto y baudrate según tu configuración
            logging.info(f"Seleccionado modo real en puerto {serial_comm.port}.")
            if not serial_comm.connect():
                logging.error("No se pudo establecer conexión serial. Cambiando a modo simulación.")
                serial_comm = MockSerialComm()
                serial_comm.connect()

        app = MotorControlGUI(root, serial_comm)
        root.mainloop()

        # Cerrar conexión serial al cerrar la aplicación
        serial_comm.disconnect()
        logging.info("Aplicación cerrada correctamente.")

    main()
