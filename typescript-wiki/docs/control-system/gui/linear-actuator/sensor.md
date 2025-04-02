---
id: la_sensor
title: Módulo del sensor
sidebar_position: 4
---

# Módulo del sensor

El subsistema del sensor proporciona la retroalimentación primordial para la lógica de control del actuador lineal, ofreciendo mediciones de distancia o proximidad necesarias para garantizar la precisión en la ejecución de órdenes y la adherencia a los límites de seguridad establecidos. Este componente realiza lecturas periódicas, descarta valores espurios y transmite resultados consolidados a la capa lógica, donde se decide la continuidad o interrupción de los movimientos.

## Finalidad Operativa

1. **Adquisición de Datos Sensibles**  
   Envía impulsos de activación y detecta ecos u otras señales de retorno, calculando la distancia con base en la velocidad de propagación (normalmente utilizando un sensor ultrasónico u otro dispositivo análogo) y en la corrección por factores ambientales.

2. **Prevención de Estados de Riesgo**  
   Evalúa el acercamiento a umbrales definidos (DIST_LOWER_TARGET, DIST_UPPER_TARGET) y alerta al módulo lógico cuando la distancia reportada indica una inminente violación de los límites, posibilitando detenciones o reducciones de velocidad anticipadas.

3. **Manejo de Errores de Tiempo Muerto**  
   Aplica un timeout que evita bloqueos en la adquisición de datos cuando la superficie de retorno no produce eco detectable o el entorno es excesivamente ruidoso, reportando valores de error para su tratamiento en capas superiores.

## Estructura de la Lectura

- **Ciclo de Disparo:**  
  El sistema emite señales de activación (trigPin) en intervalos específicos (SENSOR_READ_INTERVAL_MS), lo que desencadena el mecanismo de medición interna del sensor.

- **Recepción y Cálculo:**  
  Una vez que la señal de eco se detecta (echoPin), el subsistema mide el lapso transcurrido y, mediante la fórmula de conversión, obtiene la distancia en centímetros. Dicha distancia se confronta con los umbrales de seguridad y, si corresponde, se genera una notificación o señal interna de advertencia.

- **Descartes de Ruido y Ajustes Marginales:**  
  Para contrarrestar mediciones erráticas por interferencias o reflexiones atípicas, se aplica un filtrado de valores o una verificación de consistencia con lecturas anteriores, estableciendo un margen de tolerancia (DIST_MARGIN).

## Parámetros Relevantes

- **`SENSOR_READ_INTERVAL_MS`:** Intervalo de tiempo en milisegundos entre dos lecturas consecutivas, equilibrando la inmediatez de la respuesta con la carga computacional.  
- **`ULTRASONIC_TIMEOUT_US`:** Límite superior, en microsegundos, que finaliza la espera de eco para evitar la suspensión indefinida del subsistema, marcando lecturas como fallidas si no se detecta retorno en ese plazo.  
- **`trigPin` / `echoPin`:** Pines específicos asignados en la configuración de hardware para emitir y recibir las señales correspondientes al sensor ultrasónico.

## Integración con la Lógica Principal

El sensor reporta constantemente a la lógica del actuador la distancia computada, para permitir la activación o el cese de movimiento cuando se detectan aproximaciones excesivas a los umbrales límite. Además, en caso de error por timeout o por valores que se salen de las bandas aceptables, se propaga al subsistema lógico la necesidad de actuar (p. ej., deteniendo el motor o emitiendo un log de advertencia).
