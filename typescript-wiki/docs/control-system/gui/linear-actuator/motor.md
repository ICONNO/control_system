---
id: la_motor
title: Control del Motor
sidebar_position: 3
---

# Control del Motor

El subsistema de control del motor orquesta las señales de paso y de dirección que permiten al actuador lineal desplazarse con la precisión y la celeridad requeridas por los modos de operación, ajustándose a las restricciones físicas y a las directrices provenientes de la lógica de control. Se fundamenta en rutinas de aceleración progresiva, algoritmos de frenado y enfoques de sincronización temporal que aseguran la coherencia de movimiento en contextos de exigencia industrial.

## Objetivos Fundamentales

1. **Administración de Señales Pulsantes**  
   Genera las secuencias de impulsos para el motor paso a paso, modulando la cadencia de emisión para definir tanto la velocidad instantánea como la dirección actual, con base en parámetros como MOTOR_MAX_SPEED y MOTOR_ACCELERATION.

2. **Ejecución de Instrucciones Bloqueantes o No Bloqueantes**  
   Responde a las órdenes de la capa lógica para efectuar movimientos con monitorización continua (no bloqueantes) o para completar un desplazamiento específico y confirmarlo antes de continuar (bloqueantes), preservando la integridad del bucle de actualización general.

3. **Seguimiento de la Posición**  
   Mantiene y actualiza un indicador de la posición actual (en pasos), que se comunica a la lógica del actuador para su referencia en la toma de decisiones sobre seguridad, límites y comportamientos automáticos.

## Estructura Interna

- **Sistema de Rampa de Velocidad:**  
  Inicia cada movimiento con una fase de incremento paulatino de pulsos, configurada por MOTOR_ACCELERATION, y reduce gradualmente la velocidad antes de llegar a la posición destino o al límite operativo para evitar picos de inercia no controlados.

- **Módulo de Dirección Invertible:**  
  Determina, con base en señales lógicas (p. ej., `movingUp` vs. `movingDown`), la polaridad de la salida de dirección. El intercambio de esta señal es gestionado para evitar choques de fase en la transmisión de pulsos.

- **Ciclo de Actualización Individual:**  
  El subsistema invoca métodos de ejecución en intervalos cortos, alimentando la biblioteca especializada de manejo de motor con datos acerca de la distancia restante y el tiempo transcurrido, a fin de refinar la tasa de emisión de pulsos y la respuesta mecánica.

## Parámetros Imprescindibles

- **`MOTOR_ACCELERATION`:** Regula la magnitud del cambio de velocidad en función del tiempo, garantizando transiciones suaves y minimizando la vibración o el sobreesfuerzo en la estructura del actuador.  
- **`MOTOR_MAX_SPEED`:** Indica la velocidad tope en pasos por segundo, estableciendo un techo de rendimiento seguro para la operación, en equilibrio con los factores térmicos y de torque.  
- **`stepPin` / `dirPin`:** Definen los pines de la placa que transmiten las señales de paso y de dirección, vinculados directamente a la capa de hardware (driver de motor).
