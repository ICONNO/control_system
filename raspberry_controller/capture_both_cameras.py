#!/usr/bin/env python3

import subprocess
import time
import os
import logging
from logging.handlers import RotatingFileHandler
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
import signal
import sys
import psutil
from typing import List, Dict, Any

# ------------------- Configuración -------------------

# Directorios para guardar las fotos y logs
LOG_DIR = "/home/dev/Pictures/capturas/logs"
CAMERA_0_DIR = "/home/dev/Pictures/camara0"
CAMERA_1_DIR = "/home/dev/Pictures/camara1"

# Parámetros de captura
CAMERAS: List[Dict[str, Any]] = [
    {
        "id": 0,
        "dir": CAMERA_0_DIR,
        "name_prefix": "cam0"
    },
    {
        "id": 1,
        "dir": CAMERA_1_DIR,
        "name_prefix": "cam1"
    }
]

# Configuración de captura
MAX_RETRIES: int = 3
RETRY_DELAY: int = 2  # segundos

# Resolución máxima
WIDTH: int = 9152
HEIGHT: int = 6944

# Parámetros de espacio en disco
MIN_FREE_SPACE_MB: int = 100

# Parámetros de monitoreo de recursos
CPU_USAGE_THRESHOLD_PERCENT: int = 90
MEMORY_USAGE_THRESHOLD_PERCENT: int = 90

# -----------------------------------------------------

# Crear directorios si no existen
os.makedirs(LOG_DIR, exist_ok=True)
for cam in CAMERAS:
    os.makedirs(cam["dir"], exist_ok=True)

# Configuración de logging con rotación de archivos
logger = logging.getLogger("CameraCapture")
logger.setLevel(logging.INFO)

log_file = os.path.join(LOG_DIR, "captura_log.log")
handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)  # 5MB por archivo, 3 backups
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Añadir StreamHandler para ver los logs en la consola
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# Manejo de señales para shutdown graceful
def shutdown_gracefully(signum, frame):
    logger.info(f"Señal {signum} recibida. Cerrando el script de manera ordenada.")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_gracefully)
signal.signal(signal.SIGTERM, shutdown_gracefully)

# Verificar espacio disponible en disco
def verificar_espacio_disponible(min_space_mb: int = 100) -> bool:
    total, used, free = shutil.disk_usage("/")
    free_mb = free // (2**20)
    if free_mb < min_space_mb:
        logger.error(f"Espacio en disco insuficiente: {free_mb} MB disponibles, se requieren al menos {min_space_mb} MB.")
        return False
    return True

# Capturar una foto usando libcamera-still con autofocus
def capturar_camara(camara_id: int, salida: str, retries: int = MAX_RETRIES) -> bool:
    comando = [
        "libcamera-still",
        "--camera", str(camara_id),
        "--width", str(WIDTH),
        "--height", str(HEIGHT),
        "--autofocus-mode", "auto",        # Activar autofocus automático
        "--autofocus-on-capture",          # Activar autofocus justo antes de la captura
        "-t", "500",                        # Tiempo de espera antes de capturar (ms)
        "-n",                               # No mostrar la vista previa
        "-o", salida                        # Ruta de salida de la imagen
    ]
    try:
        logger.info(f"Iniciando captura en cámara {camara_id} con autofocus.")
        subprocess.run(comando, check=True)
        logger.info(f"Foto capturada en {salida}.")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"Error al capturar con la cámara {camara_id}: {e}. Retentando en {RETRY_DELAY} segundos.")
        if retries > 0:
            time.sleep(RETRY_DELAY)
            return capturar_camara(camara_id, salida, retries - 1)
        else:
            logger.error(f"Fallo al capturar con la cámara {camara_id} después de múltiples intentos.")
            return False
    except Exception as e:
        logger.critical(f"Error inesperado en la cámara {camara_id}: {e}")
        return False

# Monitorear recursos del sistema
def monitorear_recursos(cpu_threshold: int = 90, memory_threshold: int = 90) -> None:
    cpu_percent = psutil.cpu_percent(interval=1)
    memory_percent = psutil.virtual_memory().percent
    if cpu_percent > cpu_threshold:
        logger.warning(f"Uso de CPU alto: {cpu_percent}%")
    if memory_percent > memory_threshold:
        logger.warning(f"Uso de Memoria alto: {memory_percent}%")

# Capturar fotos de ambas cámaras en paralelo
def tomar_fotos() -> None:
    if not verificar_espacio_disponible(MIN_FREE_SPACE_MB):
        logger.error("No hay suficiente espacio en disco para capturar las fotos.")
        return

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    procesos = []

    with ThreadPoolExecutor(max_workers=len(CAMERAS)) as executor:
        for cam in CAMERAS:
            salida = os.path.join(cam["dir"], f"{cam['name_prefix']}_{timestamp}.jpg")
            procesos.append(executor.submit(capturar_camara, cam["id"], salida))
            logger.info(f"Proceso de captura iniciado para cámara {cam['id']} con salida {salida}")

        for futuro in as_completed(procesos):
            resultado = futuro.result()
            if not resultado:
                logger.error("Hubo errores al capturar algunas de las fotos.")

    # Monitorear recursos después de la captura
    monitorear_recursos()

    if all(fut.result() for fut in procesos):
        logger.info(f"Fotos capturadas exitosamente: {', '.join([cam['name_prefix']+'_'+timestamp+'.jpg' for cam in CAMERAS])}")
    else:
        logger.error("Algunas capturas no se realizaron correctamente.")

# Función principal
def main() -> None:
    logger.info("Inicio del proceso de captura de fotos simultáneas con autofocus.")
    try:
        tomar_fotos()
    except Exception as e:
        logger.critical(f"Error crítico en la captura de fotos: {e}")
    finally:
        logger.info("Proceso de captura finalizado.")

if __name__ == "__main__":
    main()
