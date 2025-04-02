"""
Logging Configuration Module

This module sets up logging for the project using Python's logging package.
It creates a rotating file handler to limit log file sizes and also configures
a console handler for real-time output.
"""

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Set up logging for the project.

    Creates a logs directory (if it doesn't exist), and sets up two handlers:
    a RotatingFileHandler to write logs to a file and a StreamHandler to output logs
    to the console. The file handler rotates when the log file reaches 5 MB and keeps
    up to 5 backup files.

    :return: None
    """
    log_dir = os.path.join('gui', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # File handler for logging to a file with rotation
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for logging to the console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter_console = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter_console)
    logger.addHandler(console)
