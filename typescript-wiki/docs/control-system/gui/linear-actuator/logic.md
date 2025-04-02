---
id: la_logic
title: Lógica del actuador
sidebar_position: 2
---

# Lógica del Actuador

El subsistema de lógica asociado al actuador lineal determina los algoritmos y la sincronía de procesos que permiten un gobierno adecuado del movimiento, la interpretación de datos sensoriales y la conciliación entre órdenes provenientes de la interfaz de usuario y las restricciones físicas del entorno. Esta entidad gestiona, en un contexto de tiempo casi real, el seguimiento de estados internos y la evolución de la posición en función de los umbrales definidos y la retroalimentación sensorial disponible.

## Objetivos Principales

1. **Procesamiento de Comandos**  
   Interpreta cadenas de instrucción (por ejemplo, movimiento continuo, cambios bruscos de modo o alteraciones en la velocidad nominal) y las traduce en actualizaciones del vector de referencia para la capa de motor, modulando la aceleración o la dirección con base en las reglas de seguridad preestablecidas.

2. **Supervisión de Condiciones Críticas**  
   Verifica de manera periódica la distancia reportada por el subsistema sensor, comprobando si el actuador se aproxima al umbral inferior o superior (DIST_LOWER_TARGET, DIST_UPPER_TARGET) y si se han excedido los límites de tolerancia (DIST_MARGIN), procediendo a suspender o revertir el movimiento en caso de detectar una anomalía inminente.

3. **Ajuste de Parámetros**  
   Maneja las directrices que dictan la aceleración (MOTOR_ACCELERATION) y la velocidad máxima (MOTOR_MAX_SPEED), asegurándose de que los valores establecidos no entren en contradicción con las capacidades mecánicas del sistema o con el diseño lógico de la plataforma de control.

## Estructura y Componentes

- **Mecanismo de Ciclo Periódico:**  
  Implementa un bucle de alta frecuencia que recopila datos sensoriales (a intervalos regidos por SENSOR_READ_INTERVAL_MS) y calcula la estrategia de movimiento requerida para el momento actual, aplicando mecanismos de amortiguación de impulsos y lógica de prioridad ante sucesos críticos.

- **Gestor de Modo Operativo:**  
  Coordina las transiciones entre estado manual (UP, DOWN) y estado automático (AUTO), administrando bloqueos temporales (delays) o pausas de seguridad cuando la distancia está por debajo de los límites tolerables o cuando se requiere un intervalo de inactividad para realizar ajustes o capturas de datos externos.

- **Régimen de Errores y Alarmas:**  
  Observa los indicadores de tiempo sin respuesta sensorial, desviaciones de posición no compensadas o intentos de sobrepasar el límite mecánico. En tales eventualidades, se disparan rutinas de detención inmediata y se notifica a la capa superior (GUI) mediante un log o evento de error para informar al usuario.

## Parámetros Internos Relevantes

- **`movingUp` / `movingDown`:** Variables lógicas que rastrean la dirección de movimiento continuo solicitado en modo manual, influenciando la meta posicional calculada en cada ciclo de actualización.  
- **`targetPosition`:** Almacena la posición objetivo en unidades de pasos, permitiendo la sincronización con la capa de control del motor y el seguimiento de los avances de la plataforma mecánica.  
- **`autoMode_`:** Indica si el subsistema está ejecutando un modo automático, en el cual la lógica invoca transiciones cíclicas entre límites predefinidos o emplea algoritmos avanzados de ida y vuelta, priorizando la seguridad frente a las órdenes manuales.

## Interacción con Otros Módulos

El presente núcleo lógico se fundamenta en la información suministrada por el módulo sensor para determinar su política de ajuste posicional, mientras que las órdenes efectivas de pulsos y la gestión de la dirección se encomiendan al módulo motor. Adicionalmente, la comunicación con la GUI se produce a través de la capa de serial_comm, la cual inyecta los comandos recibidos y notifica la capa superior de incidencias relacionadas con la imposibilidad de alcanzar o mantener un estado de operación estable.
