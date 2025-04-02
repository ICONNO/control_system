---
id: control_system_overview
title: Visión Global del Subsistema de Control
sidebar_position: 1
---

# Visión Global del Subsistema de Control

El subsistema de control integra las rutinas de gobierno lógico y la configuración de parámetros operativos que regulan las interacciones entre el hardware de actuación lineal, los elementos de sensorización y la interfaz de usuario (GUI). Esta sección describe los objetivos funcionales, los componentes parametrizables y la naturaleza de los procesos de supervisión y sincronización inherentes a la plataforma.

## Propósito y Alcance

La meta principal es mantener un control continuo y estable de la posición de actuadores lineales, garantizando la precisión requerida para las tareas industriales y la robustez necesaria para soportar posibles condiciones anómalas (choques mecánicos, sobrecargas térmicas o fallas sensoriales). El sistema abarca:

1. **Definición de Umbrales y Límites**  
   Parametrización de distancias mínimas y máximas permitidas (e.g., `DIST_LOWER_TARGET`, `DIST_UPPER_TARGET`) para salvaguardar la integridad del dispositivo y prevenir estados de colisión.

2. **Gestión de Velocidad y Aceleración**  
   Configuración de la rampa de aceleración (`MOTOR_ACCELERATION`) y la velocidad máxima (`MOTOR_MAX_SPEED`), equilibrando la eficiencia de movimiento con la seguridad y el control cinemático.

3. **Sincronización de Lectura Sensorial**  
   Ajuste de la cadencia de muestreo (`SENSOR_READ_INTERVAL_MS`) para asegurar un flujo de datos estable y oportuno, evitando rezagos en la corrección de trayectoria o en la detección de eventos peligrosos.

## Naturaleza Jerárquica

El diseño del subsistema de control es jerárquico y se fundamenta en la separación de responsabilidades:

- **Capa Inferior (Firmware en Arduino)**  
  Encargada de la generación de pulsos de movimiento, la recepción de datos sensoriales en tiempo real y la ejecución de mecanismos de parada de emergencia. Sus funciones se estructuran alrededor de un ciclo de actualización periódico y de la reacción a comandos entrantes.

- **Capa Intermedia (Comunicación Serial y Lógica Intermedia)**  
  Gestiona la traducción de órdenes de la GUI a parámetros concretos del firmware, reflejando en la electrónica de potencia y en la lógica de posicionamiento los cambios solicitados por el usuario o definidos en la configuración. Ejerce asimismo la detección de anomalías y la coordinación de señales de error.

- **Capa Superior (Interfaz de Usuario y Configuración Global)**  
  Reúne los controles manuales y automáticos, despliega la información esencial sobre la distancia y el estado general del actuador, y define la estrategia de control (continuo, por incrementos, etc.) conforme a las políticas de la empresa.

## Parámetros Críticos

A continuación se enumeran algunos parámetros críticos controlados por este subsistema. Su modificación debe documentarse de forma inmediata en la wiki para garantizar la coherencia en toda la organización:

- **`DIST_LOWER_TARGET` y `DIST_UPPER_TARGET`**: Limitan el campo de movimiento para prevenir colisiones, configurables en centímetros.  
- **`DIST_MARGIN`**: Define la banda de tolerancia para la detección de proximidad a umbrales, reduciendo falsos positivos.  
- **`MOTOR_ACCELERATION`**: Determina la tasa de aceleración en pasos por segundo al cuadrado, impactando el comportamiento dinámico del motor.  
- **`MOTOR_MAX_SPEED`**: Establece la velocidad límite en pasos por segundo, equilibrando la rapidez de posicionamiento con la fiabilidad mecánica.  
- **`SENSOR_READ_INTERVAL_MS`**: Intervalo de lectura del sensor ultrasónico, calibrado en milisegundos, para mantener la precisión de las mediciones sin sobrecargar el ciclo de actualización.

## Políticas de Seguridad

El sistema contempla la inhabilitación de movimientos cuando los datos de posición sensorial indican que se ha alcanzado (o superado) un límite operativo, así como la emisión de señales de parada cuando la distancia calculada se aproxima al umbral crítico dentro de la banda de margen especificada. Se recomienda un proceso de verificación periódica de logs y eventos, con el fin de identificar tendencias de fallas latentes.