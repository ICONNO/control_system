import tkinter as tk
from tkinter import ttk

def set_styles():
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.map('TButton',
              foreground=[('active', 'black')],
              background=[('active', '#d9d9d9')])
    style.configure('TLabel', font=('Helvetica', 12))
    style.configure('TLabelframe.Label', font=('Helvetica', 14, 'bold'))
