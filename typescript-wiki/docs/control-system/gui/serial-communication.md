---
id: serial-communication
title: Comunicación Serial
sidebar_position: 2
---

# Comunicación Serial

El módulo de **Serial Communication** se encarga de gestionar la comunicación entre la GUI y el controlador Arduino.

## Funcionalidades

- **Detección Automática del Puerto:**  
  Permite especificar el puerto (por ejemplo, COM3) y establece la conexión.
- **Lectura Continua:**  
  Se utiliza un hilo en segundo plano para leer datos del puerto serie y enviar esos datos a la GUI mediante callbacks.
- **Envío de Comandos:**  
  Los comandos (por ejemplo, "AUTO", "UP", "SET_SPEED") se envían en formato de texto a través del puerto serial.
- **Manejo de Errores:**  
  Se realizan intentos de reconexión y se loguean errores si la conexión falla.

## Implementación

El archivo `serial_comm.py` utiliza la librería `pyserial` y maneja la lectura y escritura de datos de manera asíncrona para no bloquear la interfaz de usuario.
