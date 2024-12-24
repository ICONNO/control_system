import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import serial
import threading
import time

class MotorControlGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Control de Motor Paso a Paso")
        self.master.geometry("700x500")
        self.master.resizable(False, False)

        # Configuración de la GUI
        self.create_widgets()

        # Configuración de la Comunicación Serial
        self.serial_port = self.detect_serial_port()
        self.baud_rate = 9600
        self.ser = None
        self.connect_serial()

        # Iniciar hilo para leer datos del Arduino
        self.running = True
        self.read_thread = threading.Thread(target=self.read_serial, daemon=True)
        self.read_thread.start()

    def detect_serial_port(self):
        """
        Detecta automáticamente el puerto serial al que está conectado el Arduino.
        """
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if 'Arduino' in port.description or 'ttyACM' in port.device or 'ttyUSB' in port.device:
                return port.device
        return 'COM3'  # Puerto por defecto, cámbialo si es necesario

    def connect_serial(self):
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            time.sleep(2)  # Esperar a que la conexión se establezca
            print(f"Conectado a {self.serial_port} a {self.baud_rate} bps.")
            self.append_text(f"Conectado a {self.serial_port} a {self.baud_rate} bps.")
        except serial.SerialException as e:
            messagebox.showerror("Error de Conexión", f"No se puede abrir el puerto {self.serial_port}.\n{e}")
            self.master.destroy()

    def create_widgets(self):
        # Marco para Botones de Control
        control_frame = ttk.LabelFrame(self.master, text="Controles del Motor")
        control_frame.pack(padx=10, pady=10, fill="x")

        btn_auto = ttk.Button(control_frame, text="Modo Automático", command=self.activate_auto)
        btn_auto.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        btn_up = ttk.Button(control_frame, text="Subir", command=self.move_up)
        btn_up.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        btn_down = ttk.Button(control_frame, text="Bajar", command=self.move_down)
        btn_down.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        btn_stop = ttk.Button(control_frame, text="Detener", command=self.stop_motor)
        btn_stop.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Configurar las columnas para que los botones se expandan
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)

        # Marco para Ajuste de Velocidad
        speed_frame = ttk.LabelFrame(self.master, text="Ajuste de Velocidad")
        speed_frame.pack(padx=10, pady=10, fill="x")

        self.speed_var = tk.IntVar(value=800)
        speed_label = ttk.Label(speed_frame, text="Intervalo de Pulsos (μs):")
        speed_label.pack(side="left", padx=10, pady=10)

        self.speed_slider = ttk.Scale(speed_frame, from_=200, to=2000, orient="horizontal",
                                      variable=self.speed_var, command=self.update_speed)
        self.speed_slider.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        self.speed_display = ttk.Label(speed_frame, text="800 μs")
        self.speed_display.pack(side="left", padx=10, pady=10)

        # Marco para Mostrar Información
        info_frame = ttk.LabelFrame(self.master, text="Información del Sistema")
        info_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Área de texto para información
        self.text_info = tk.Text(info_frame, height=15, width=80, state='disabled', wrap='word')
        self.text_info.pack(padx=10, pady=10, fill="both", expand=True)

        # Scrollbar para el área de texto
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.text_info.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_info.configure(yscrollcommand=scrollbar.set)

        # Marco para Estado del Sistema
        status_frame = ttk.LabelFrame(self.master, text="Estado del Sistema")
        status_frame.pack(padx=10, pady=10, fill="x")

        self.status_var = tk.StringVar(value="Modo: Manual")
        lbl_status = ttk.Label(status_frame, textvariable=self.status_var, foreground="blue", font=("Arial", 12, "bold"))
        lbl_status.pack(padx=10, pady=10)

        # Botón para Cerrar la Aplicación Correctamente
        exit_button = ttk.Button(self.master, text="Salir", command=self.on_closing)
        exit_button.pack(pady=10)

    def activate_auto(self):
        self.send_command("AUTO")

    def move_up(self):
        self.send_command("UP")

    def move_down(self):
        self.send_command("DOWN")

    def stop_motor(self):
        self.send_command("STOP")

    def update_speed(self, event):
        speed = self.speed_var.get()
        self.speed_display.config(text=f"{speed} μs")
        # Enviar el comando para ajustar la velocidad
        self.send_command(f"SET_SPEED {speed}")

    def send_command(self, command):
        if self.ser and self.ser.is_open:
            try:
                self.ser.write((command + '\n').encode())
                print(f"Enviado: {command}")
                self.append_text(f"Enviado: {command}")
            except serial.SerialException as e:
                messagebox.showerror("Error de Comunicación", f"No se pudo enviar el comando.\n{e}")
        else:
            messagebox.showerror("Error de Comunicación", "El puerto serial no está abierto.")

    def read_serial(self):
        while self.running:
            if self.ser and self.ser.is_open:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        self.append_text(line)
                except serial.SerialException:
                    self.append_text("Error de comunicación serial.")
                except UnicodeDecodeError:
                    # Ignorar caracteres no decodificables
                    pass
            time.sleep(0.1)

    def append_text(self, text):
        self.text_info.configure(state='normal')
        self.text_info.insert(tk.END, text + '\n')
        self.text_info.configure(state='disabled')
        self.text_info.see(tk.END)

        # Actualizar el estado basado en el texto recibido
        if "Activando modo automático" in text:
            self.status_var.set("Modo: Automático")
        elif "Modo manual" in text or "Motor detenido" in text:
            self.status_var.set("Modo: Manual")

    def on_closing(self):
        if messagebox.askokcancel("Salir", "¿Quieres salir de la aplicación?"):
            self.running = False
            if self.ser and self.ser.is_open:
                try:
                    self.ser.write(b"STOP\n")
                    time.sleep(0.5)
                    self.ser.close()
                except serial.SerialException:
                    pass
            self.master.destroy()

def main():
    root = tk.Tk()
    app = MotorControlGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
