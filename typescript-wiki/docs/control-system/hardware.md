---
id: hardware
title: Componentes de hardware
sidebar_position: 5
---

# Componentes de Hardware

Esta sección ofrece una descripción técnica detallada de los dispositivos que conforman el **Control System**. Se especifican las características, parámetros y funcionamiento de cada componente, permitiendo comprender la integración y el desempeño global del sistema.

---

## 1. Bomba de Vacío VN-C3

**Descripción:**  
La bomba de vacío VN-C3 es un dispositivo industrial diseñado para generar condiciones de baja presión mediante la extracción de aire y gases. Se utiliza para procesos que requieren la creación de un vacío constante en entornos de alta exigencia.

**Características Técnicas:**

- **Eficiencia Operativa:**  
  Diseñada para funcionamiento continuo con alta estabilidad en la presión.
- **Capacidad de Extracción:**  
  Permite alcanzar niveles de vacío profundos, lo que es esencial en aplicaciones de precisión.
- **Construcción:**  
  Componentes robustos y sellados que garantizan resistencia a condiciones ambientales adversas.
  
**Funcionamiento:**  
La VN-C3 opera mediante la rotación de un impulsor interno, que crea un flujo de aire en dirección opuesta. La salida de aire se regula para mantener un vacío constante, permitiendo una operación confiable en procesos automatizados.

---

## 2. Actuador Lineal con Motor NEMA 17

**Descripción:**  
El actuador lineal se basa en un mecanismo de tornillo, acoplado a un motor paso a paso NEMA 17. Este conjunto convierte el movimiento rotatorio en un desplazamiento lineal preciso, fundamental en aplicaciones de posicionamiento.

**Características Técnicas:**

- **Motor NEMA 17:**  
  - **Torque y Precisión:** Proporciona un equilibrio óptimo entre torque y precisión para movimientos controlados.
  - **Repetibilidad:** Alta precisión en el posicionamiento, con una resolución que permite movimientos minúsculos.
- **Mecanismo de Tornillo:**  
  - **Conversión de Movimiento:** Transforma el movimiento rotativo en lineal con alta eficiencia.
  - **Durabilidad:** Construido en materiales de alta resistencia para soportar cargas mecánicas elevadas.
  
**Funcionamiento:**  
El motor NEMA 17, controlado mediante señales de microstepping, gira un husillo que a su vez mueve un bloque lineal. Este mecanismo es monitoreado por sensores y controlado por algoritmos de posicionamiento implementados en el firmware.

---

## 3. Fuente de Poder LRS-350-12

**Descripción:**  
La fuente de poder LRS-350-12 suministra una tensión de 12V con una potencia máxima de 350W. Es esencial para garantizar un suministro estable a todos los componentes del sistema.

**Características Técnicas:**

- **Tensión y Potencia:**  
  - Salida de 12V y hasta 350W, permitiendo alimentar motores, sensores y controladores.
- **Regulación de Voltaje:**  
  - Alta precisión en la regulación, lo que minimiza fluctuaciones y protege contra sobrecargas.
- **Protección Integrada:**  
  - Incluye protecciones contra sobrecarga, cortocircuitos y sobrecalentamiento.
  
**Funcionamiento:**  
La LRS-350-12 convierte la corriente de entrada en una salida de 12V de alta estabilidad. Su diseño asegura que las variaciones en la red eléctrica no afecten el rendimiento de los dispositivos conectados.

---

## 4. Arduino UNO R3

**Descripción:**  
El Arduino UNO R3 es una placa de microcontrolador basada en el ATmega328P, ampliamente utilizada en proyectos de prototipos y aplicaciones industriales por su robustez y versatilidad.

**Características Técnicas:**

- **Capacidad de Entrada/Salida:**  
  - 14 pines digitales y 6 entradas analógicas, que permiten la conexión de múltiples sensores y actuadores.
- **Comunidad y Soporte:**  
  - Amplio soporte en la comunidad y abundante documentación técnica.
- **Facilidad de Integración:**  
  - Compatible con numerosas librerías y módulos, lo que facilita su uso en sistemas complejos.
  
**Funcionamiento:**  
El Arduino UNO R3 se encarga de recibir comandos, procesar señales de entrada de sensores y generar salidas para controlar el actuador. Su programación se realiza en el entorno Arduino IDE, y se comunica con otros módulos (por ejemplo, la GUI) mediante protocolos seriales.

---

## 5. Driver TB6560

**Descripción:**  
El TB6560 es un driver para motores paso a paso, diseñado para aplicaciones que requieren un control preciso y la capacidad de manejar altos niveles de corriente y torque.

**Características Técnicas:**

- **Microstepping:**  
  Permite subdividir cada paso del motor para lograr una mayor resolución y suavidad en el movimiento.
- **Alto Manejo de Corriente:**  
  Soporta cargas elevadas, lo que lo hace adecuado para motores que requieren alta potencia.
- **Eficiencia Energética:**  
  Optimizado para minimizar la generación de calor y maximizar el rendimiento.
  
**Funcionamiento:**  
El TB6560 recibe señales de control del Arduino y las convierte en impulsos precisos para el motor paso a paso. Su capacidad de microstepping permite movimientos extremadamente precisos, mientras que sus protecciones internas aseguran un funcionamiento seguro.

---

## 6. Raspberry Pi 5

**Descripción:**  
El Raspberry Pi 5 es una computadora de placa única que se utiliza como centro de procesamiento para tareas avanzadas, como la ejecución de la interfaz gráfica y la captura remota de imágenes.

**Características Técnicas:**

- **Alto Rendimiento:**  
  Procesador de múltiples núcleos y memoria suficiente para ejecutar aplicaciones complejas en tiempo real.
- **Conectividad:**  
  WiFi, Ethernet y múltiples puertos USB para la integración de periféricos.
- **Versatilidad:**  
  Soporta diversos sistemas operativos y puede ejecutar scripts en Python, facilitando la automatización y procesamiento de datos.
  
**Funcionamiento:**  
El Raspberry Pi 5 actúa como plataforma central para la GUI y las utilidades de captura remota, permitiendo la integración de datos de los módulos y la ejecución de algoritmos de procesamiento avanzado.

---

## 7. Módulos de Cámara ARDUCAM Hawkeye (x2)

**Descripción:**  
Los módulos de cámara ARDUCAM Hawkeye son dispositivos de captura de imágenes de alta resolución, diseñados para aplicaciones de monitoreo y análisis en tiempo real.

**Características Técnicas:**

- **Alta Resolución:**  
  Permiten obtener imágenes detalladas para análisis visual.
- **Integración:**  
  Se conectan fácilmente al Raspberry Pi para procesamiento en tiempo real.
- **Rendimiento en Condiciones Variables:**  
  Adaptabilidad a diferentes condiciones de iluminación y entornos dinámicos.
  
**Funcionamiento:**  
Estos módulos capturan imágenes y las envían al Raspberry Pi para su procesamiento. Se utilizan en aplicaciones donde se requiere monitoreo visual continuo, integrándose con el resto del sistema mediante protocolos de comunicación definidos.

---

## Integración del Sistema

### Interconexión
Cada uno de estos componentes se integra en un sistema global mediante interfaces eléctricas y protocolos de comunicación. El Arduino, por ejemplo, se comunica con el driver TB6560 para controlar el motor y con los sensores para obtener datos en tiempo real. La GUI, ejecutada en el Raspberry Pi, se conecta a través del puerto serial para enviar comandos y recibir actualizaciones del sistema.

### Seguridad y Robustez
El sistema incorpora múltiples niveles de protección:
- **Hardware:** Protección contra sobrecargas, cortocircuitos y sobrecalentamientos en la fuente de poder.
- **Firmware:** Algoritmos de control y medidas de seguridad que detienen el motor al alcanzar límites predefinidos.
- **Software:** Gestión de errores y reconexión automática en el módulo de comunicación serial.

### Configuración y Calibración
Los parámetros críticos (por ejemplo, `DIST_LOWER_TARGET`, `MOTOR_MAX_SPEED`, `SENSOR_READ_INTERVAL_MS`) se definen en el archivo `config.h` y pueden ser ajustados para optimizar el rendimiento según el entorno operativo.
