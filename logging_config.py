# logging_config.py

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configura el sistema de logging para todo el proyecto.
    """
    log_dir = os.path.join('gui', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter_console = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter_console)
    logger.addHandler(console)
