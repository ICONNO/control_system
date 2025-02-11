# gui/styles.py

import tkinter as tk
from tkinter import ttk

def set_styles():
    """
    Define y aplica estilos personalizados a los widgets de la GUI.
    """
    style = ttk.Style()
    style.theme_use('clam')  # Elegir un tema moderno
    
    # Estilo para botones
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.map('TButton',
              foreground=[('active', 'black')],
              background=[('active', '#d9d9d9')])
    
    # Estilo para labels
    style.configure('TLabel', font=('Helvetica', 12))
    
    # Estilo para LabelFrames
    style.configure('TLabelframe.Label', font=('Helvetica', 14, 'bold'))
