---
id: styles
title: Estilos de la GUI
sidebar_position: 3
---

# GUI Styles

El módulo **Styles** define la apariencia visual de la interfaz utilizando el paquete **ttkbootstrap**.

## Personalización

- **Temas:**  
  Se utiliza el tema 'clam' (o 'superhero' en algunas partes) para darle un aspecto moderno.
- **Fuentes y Colores:**  
  Se definen fuentes y colores específicos para botones, etiquetas y otros elementos.
- **Mapeo de Estilos:**  
  Se configura el comportamiento visual de los botones en estados activos y deshabilitados.

## Ejemplo de Configuración

En `styles.py` se establece lo siguiente:
```python
from tkinter import ttk

def set_styles():
    """Apply custom styles to GUI widgets."""
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.map('TButton', foreground=[('active', 'black')], background=[('active', '#d9d9d9')])
    style.configure('TLabel', font=('Helvetica', 12))
    style.configure('TLabelframe.Label', font=('Helvetica', 14, 'bold'))

Este código se encarga de uniformar el estilo de los widgets de la GUI. En este caso, se establece el tema 'clam' y se aplica un estilo personalizado a los botones y etiquetas.
