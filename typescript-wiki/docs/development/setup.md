---
id: development_setup
title: Configuración del Entorno de Desarrollo
sidebar_position: 5
---

# Configuración del Entorno de Desarrollo

Este documento especifica los pasos y las dependencias necesarias para la instauración y posterior mantenimiento del ecosistema de desarrollo en torno al subsistema de control de actuadores lineales, comprendiendo tanto el firmware basado en Arduino como la interfaz gráfica en Python y cualquier utilidad complementaria (por ejemplo, captura remota).

## Objetivos Principales

1. **Unificación de Prerrequisitos**  
   Asegurar que todos los participantes en el desarrollo manejen un conjunto uniforme de versiones de software (Arduino IDE, Python, librerías requeridas) y realicen el despliegue en un entorno homogéneo, reduciendo fallos por incompatibilidades.

2. **Procesos de Inicialización**  
   Definir los métodos de instalación y verificación de dependencias, incluyendo los parámetros relevantes en el microcontrolador (p. ej., baudios, pines asignados) y los archivos de configuración en la carpeta GUI (p. ej., requirements.txt, configuración de puertos seriales).

3. **Documentación Persistente**  
   Permitir que futuras iteraciones o expansiones del sistema conserven la coherencia con los lineamientos originales, evitando la dispersión de información en múltiples repositorios no sincronizados.

## Requisitos de Hardware

- **Arduino y periféricos:**  
  Una placa Arduino (o equipo compatible) con capacidad suficiente para gestionar el driver de motor y el sensor ultrasónico, más los pines digitales para trigPin, echoPin, stepPin y dirPin, entre otros.  
- **Actuador lineal y motor paso a paso:**  
  Dispositivo mecánico que cumpla con la especificación de corriente y torque contemplada en el diseño, acompañado de un driver de motor que soporte los parámetros de aceleración y velocidad pretendidos.  
- **Fuente de alimentación regulada:**  
  Aporta la energía estable necesaria para motor, sensor y la propia placa Arduino, contemplando picos de demanda en arranques o frenados bruscos.

## Requisitos de Software

- **Arduino IDE (versión recomendada 1.8.x o 2.x):**  
  Empleado para compilar y cargar el firmware del actuador ubicado en la carpeta lineal_actuator.  
- **Python (versión 3.10 o superior):**  
  Utilizado en la implementación de la GUI y en la ejecución de utilidades como la captura remota o scripts de testing.  
- **Dependencias de Python:**  
  Librerías enumeradas en `gui/requirements.txt`, que incluyen módulos para la comunicación serial, la interfaz gráfica con ttkbootstrap, e interfaces de registro y captura si procede.

## Pasos de Instalación

1. **Clonación del Repositorio:**  
   Obtener el árbol de archivos que contiene el firmware, la GUI y la documentación. Confirmar las ramas pertinentes según las políticas internas de versionado.

2. **Instalación de Librerías Arduino:**  
   Incluir la biblioteca AccelStepper y otras que se requieran (por ejemplo, para la lectura de sensores si corresponde).

3. **Carga del Firmware:**  
   Abrir `lineal_actuator.ino` en Arduino IDE y seleccionar la placa adecuada, ajustando baudios y puerto. Compilar y subir. Verificar que la conexión serie responde con mensajes de inicialización.

4. **Instalación de Dependencias Python:**  
   Ingresar a la carpeta `gui/` y ejecutar la instalación de paquetes (pip o gestor equivalente), confirmando la ausencia de conflictos en las versiones.

5. **Verificación de Operatividad:**  
   Ejecutar la GUI (run_gui.py) con los parámetros de puerto correctos. Revisar que la interfaz muestre el modo, la distancia (inicialmente desconocida), y que el log refleje la conexión con el firmware sin errores.

## Parámetros Ajustables

- **DIST_LOWER_TARGET / DIST_UPPER_TARGET** en `config.h`:  
  Limites de recorrido. Sus valores deben guardar coherencia con la mecánica disponible.  
- **MOTOR_ACCELERATION / MOTOR_MAX_SPEED** en `config.h`:  
  Definen la caracterización cinemática del actuador.  
- **Baudios y Puerto Serial** (en `run_gui.py` o en `serial_comm.py`):  
  Ajustar al entorno de cada estación de trabajo, asegurando la sincronía con la configuración del firmware.

## Mantenimiento y Actualizaciones

Para preservar la integridad del entorno, se recomienda versionar cuidadosamente cualquier modificación en los archivos de configuración, revisando su reflejo en este documento. En particular, se considera crítico anotar cualquier variación en los parámetros de seguridad (umbrales de distancia, aceleraciones, etc.) o en las rutas de instalación de librerías para prevenir discrepancias a largo plazo.
