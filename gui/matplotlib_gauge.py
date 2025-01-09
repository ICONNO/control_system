# gui/matplotlib_gauge.py

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import math
import logging

class MatplotlibGauge(ttk.Frame):
    """
    Clase para crear un gauge estético y moderno en Tkinter utilizando matplotlib.
    """
    def __init__(self, parent, label="Gauge", min_value=0, max_value=100, initial_value=0, **kwargs):
        super().__init__(parent, **kwargs)
        self.label = label
        self.min_value = min_value
        self.max_value = max_value
        self.value = self.clamp(initial_value)
        self.target_value = self.value

        # Configuración de la figura de matplotlib con fondo oscuro
        self.fig, self.ax = plt.subplots(figsize=(4, 2), subplot_kw={'projection': 'polar'})
        self.fig.patch.set_facecolor('#2e2e2e')  # Fondo oscuro
        self.ax.set_facecolor('#2e2e2e')        # Fondo oscuro del subplot
        self.fig.subplots_adjust(top=1, bottom=0, left=0, right=1)

        # Configuración del gauge
        self.ax.set_theta_offset(math.pi / 2)  # Iniciar desde la parte superior
        self.ax.set_theta_direction(-1)        # Sentido de las agujas de reloj
        self.ax.set_ylim(0, 1.2)               # Ampliar para acomodar etiquetas
        self.ax.axis('off')

        # Dibujar los ticks
        self.draw_ticks()

        # Dibujar la aguja
        self.needle, = self.ax.plot([0, 0], [0, 0.8], lw=3, color='red')

        # Agregar la etiqueta
        self.ax.text(0, -0.4, self.label, horizontalalignment='center',
                     verticalalignment='center', fontsize=12, color='white')

        # Agregar la lectura digital
        self.digital_display = self.ax.text(0, -0.6, f"{int(self.value)}",
                                            horizontalalignment='center',
                                            verticalalignment='center',
                                            fontsize=14, color='cyan')

        # Integrar matplotlib con Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Iniciar actualización periódica
        self.update_needle()

    def clamp(self, value):
        """
        Restringe el valor entre min_value y max_value.
        """
        return max(self.min_value, min(self.max_value, value))

    def draw_ticks(self):
        """
        Dibuja los ticks principales y secundarios en el gauge.
        """
        num_major_ticks = 10
        num_minor_ticks = 5
        for i in range(num_major_ticks + 1):
            # Cálculo del ángulo considerando el offset y la dirección
            angle = (math.pi / 2) - (math.radians(270 * i / num_major_ticks))
            self.ax.plot([angle, angle], [0.9, 1], lw=2, color='white')
            tick_value = self.min_value + (self.max_value - self.min_value) * i / num_major_ticks
            self.ax.text(angle, 1.1, f"{int(tick_value)}", 
                         horizontalalignment='center', verticalalignment='center',
                         fontsize=10, color='white')

        for i in range(num_major_ticks * num_minor_ticks + 1):
            angle = (math.pi / 2) - (math.radians(270 * i / (num_major_ticks * num_minor_ticks)))
            self.ax.plot([angle, angle], [0.95, 1], lw=1, color='lightgray')

    def update_value(self, new_value):
        """
        Actualiza el valor del gauge con una animación suave.
        
        :param new_value: Nuevo valor a mostrar.
        """
        self.target_value = self.clamp(new_value)

    def update_needle(self):
        """
        Actualiza la aguja hacia el valor objetivo y programa la siguiente actualización.
        """
        if self.value < self.target_value:
            self.value += 1
        elif self.value > self.target_value:
            self.value -= 1

        if self.value != self.target_value:
            self.redraw_needle()

        # Programar la siguiente actualización
        self.after(100, self.update_needle)  # 100 ms para una animación más ligera

    def redraw_needle(self):
        """
        Redibuja la aguja y la lectura digital.
        """
        try:
            # Calcular ángulo de la aguja considerando el offset y la dirección
            angle = 270 * (self.value - self.min_value) / (self.max_value - self.min_value)
            angle_rad = (math.pi / 2) - math.radians(angle)

            # Verificar si el ángulo es finito
            if not math.isfinite(angle_rad):
                raise ValueError(f"Ángulo no finito calculado: {angle_rad}")

            # Actualizar la posición de la aguja
            self.needle.set_xdata([angle_rad, angle_rad])
            self.needle.set_ydata([0, 0.8])

            # Actualizar la lectura digital
            self.digital_display.set_text(f"{int(self.value)}")

            # Redibujar el canvas
            self.canvas.draw_idle()
        except Exception as e:
            logging.error(f"Error al redibujar la aguja: {e}")
