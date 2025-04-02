"""
Styles Module

Defines custom styles for GUI widgets using ttk.
"""

from tkinter import ttk

def set_styles():
    """
    Applies custom styles to the GUI widgets.

    Configures fonts, padding, and theme settings for buttons, labels, and frames.
    
    :return: None
    """
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.map('TButton', foreground=[('active', 'black')], background=[('active', '#d9d9d9')])
    style.configure('TLabel', font=('Helvetica', 12))
    style.configure('TLabelframe.Label', font=('Helvetica', 14, 'bold'))
