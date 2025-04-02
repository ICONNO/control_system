---
id: gui_architecture
title: Arquitectura de la Interfaz Gráfica
sidebar_position: 3
---

# Arquitectura de la interfaz gráfica (GUI) 

El módulo de interfaz gráfica (GUI) representa el punto de interacción esencial entre los operadores del sistema y el subsistema de control que rige el movimiento del actuador lineal, la configuración de parámetros y la captura de datos externos. Se fundamenta en un modelo de ventanas y eventos sincronizados mediante hilos de gestión de procesos concurrentes, y coordina la comunicación con la capa de firmware mediante un canal de intercambio serial.

## Finalidad y Alcance

1. **Control de Operaciones Manuales y Automáticas**  
   La GUI suministra los elementos visuales (botones, paneles, menús) que habilitan la ejecución de acciones inmediatas (p. ej., subir o bajar el actuador) o la asignación de rutinas automáticas (modo AUTO), mientras registra el estado global del sistema y sus subsistemas.

2. **Supervisión en Tiempo Real**  
   Provee indicadores en pantalla para la distancia, el modo operativo, la disponibilidad del puerto serial y el estado de módulos periféricos (como la bomba de vacío), asegurando que el usuario disponga de información suficiente para la toma de decisiones operativas.

3. **Configuración de Parámetros**  
   Facilita la modificación de umbrales (DIST_LOWER_TARGET, DIST_UPPER_TARGET), la selección de velocidades y aceleraciones (MOTOR_ACCELERATION, MOTOR_MAX_SPEED) y la activación/desactivación de utilidades complementarias (captura remota, modos de prueba).

## Estructura Interna

La GUI se organiza en componentes funcionales, cada uno asignado a la administración de una porción distinta del ecosistema de control:

- **Ventana Principal y Layout**  
  Integra los paneles informativos (modo, distancia, estado de conexión) y los controles de usuario (botones, sliders, menús) en una disposición coordinada, optimizada para reducir el tiempo de acceso a funcionalidades críticas.

- **Gestor de Eventos y Lógica de Interacción**  
  Implementa la lógica que reacciona a presiones de botones, interrupciones de teclado y otros eventos del sistema operativo, comunicándose con el módulo de comunicación serial para traducir dichas interacciones en comandos concretos (e.g., “DOWN”, “SET_SPEED 10000”).

- **Mecanismo de Logging y Visualización**  
  Comprende un panel de registros que recibe entradas (logs) en tiempo casi real, mostrando mensajes de estado, alertas y verificaciones de seguridad. Esto permite una auditoría inmediata del comportamiento del sistema y la detección de fallas incipientes.

## Parámetros Relevantes

Si bien la mayor parte de los parámetros se establecen en el firmware o se definen en la configuración global (ver secciones precedentes), la GUI se asocia con una serie de constantes y variables que influencian su comportamiento:

- **Frecuencia de Actualización de la Interfaz**  
  Determina la periodicidad con la que la GUI solicita información de la capa de control (sensores, estado del motor), equilibrando responsividad y carga de procesamiento.

- **Opciones de Intervalo de Pulso**  
  Selección de intervalos (p. ej., 100, 200, 300, 500 microsegundos) que la GUI utiliza para instruir la capa de firmware sobre la cadencia de pasos del motor, ajustando la velocidad máxima resultante.

- **Estados de Conexión Serial**  
  Variables que reflejan la disponibilidad del puerto, la tasa de baudios configurada y la robustez de la conexión (reintentos y umbrales de reconexión).

## Manejo de Concurrencia y Seguridad

La GUI ejecuta hilos concurrentes para la lectura de mensajes entrantes y la gestión de eventos de usuario, previniendo bloqueos en la interfaz o retrasos excesivos en la respuesta a acciones críticas. Asimismo, se han definido rutinas de seguridad que invalidan órdenes manuales si el sistema reporta condiciones anómalas (distancia fuera de rango o imposibilidad de detener el motor).
