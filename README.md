# Turing Machine Final

### 1. Descripción del Proyecto

Este proyecto consiste en el diseño, simulación y prototipado de una Máquina de Turing electromecánica capaz de realizar operaciones aritméticas fundamentales (Suma y Resta).

El sistema materializa el concepto teórico abstracto de Alan Turing mediante un enfoque de Gemelo Digital (Digital Twin). Utiliza un robot móvil como "cabezal" que se desplaza sobre una superficie que actúa como la "cinta infinita". El robot posee capacidad de locomoción diferencial, visión artificial para la lectura de símbolos y un actuador de doble cabezal para la escritura y reescritura de datos.

El objetivo principal es demostrar la ejecución de algoritmos a nivel fundamental, validando la teoría de autómatas mediante una implementación física viable controlada por lógica en Python.


### 2. Contenido de los Archivos

El repositorio del proyecto se organiza de la siguiente manera:

- /Scripts: Contiene la lógica de programación del robot

    - ControllerWebot.py: Script principal en Python. Implementa la lectura de sensores, control de motores paso a paso/servos y, los diccionarios que definen las Tablas de Transición (Suma y Resta)
    - RaspberryScript.py: Misma logica implementada a raspberry en python

- /Proyecto: Archivos de entorno para el simulador Webots

    - TuringMachineWebots.rar: Mundo y Proyecto importable a webots

- /Diseño: Esquemas

    - PlanosTuringMachine.pdf: Planos de diseño del robot

- /Docs: Documentación teórica

   - LogicaTuringMachine: Definicion visual del automata de turing

   - DiarioProyecto.md: Registro cronológico de avances y decisiones técnicas

### 3. Explicación Lógica

La máquina opera sobre un sistema Determinista basado en una codificación unaria.

- 3.1 Alfabeto y Representación

  - 1 (Negro/Unidad): Representa el valor numérico. Ejemplo: El número 3 es 111.

  - 0 (Amarillo/Separador): Delimita el fin de un número y el inicio del otro.

  - B (Gris/Blank): Representa el vacío de la cinta infinita.


- 3.2 Funcionamiento del Autómata
  - El núcleo del software es una Máquina de Estados Finitos. El ciclo de operación es:

  - Lectura: La cámara captura el color del suelo. Se procesa mediante umbrales RGB para seleccionar el valor en 1, 0 o B.

  - Transición: Se consulta la Tabla de Estados cargada (Suma o Resta). Se busca la tupla:
 
    $$\delta(Estado_{actual}, Símbolo_{leído}) \rightarrow (Estado_{nuevo}, Símbolo_{escribir}, Movimiento)$$

- 3.3 Algoritmos Implementados

  - Suma ($A+B$): Convierte el separador 0 central en un 1 (fusionando ambas cadenas) y elimina un 1 del final para mantener la consistencia unaria.

  - Resta ($A-B$): Utiliza un algoritmo de correspondencia. Borra un 1 del sustraendo (lado B), viaja al inicio y borra un 1 del minuendo (lado A). Repite hasta que el sustraendo se agota.
