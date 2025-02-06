import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_dir = os.path.join('gui', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler = RotatingFileHandler(os.path.join(log_dir, 'app.log'), maxBytes=5*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
