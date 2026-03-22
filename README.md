<div align="center">

# ⚙️ Generador de Analizadores Léxicos

### Proyecto 01 - Implementación de un generador de analizadores léxicos usando YALex

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-Lexer_Generado-yellow?logo=javascript&logoColor=black)


*Herramienta capaz de leer una especificación en YALex, construir los autómatas correspondientes y generar un analizador léxico funcional e independiente.*



</div>

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Características Principales](#-características-principales)
- [Objetivos del Proyecto](#-objetivos-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Ejecución del Proyecto](#-ejecución-del-proyecto)
- [Flujo de Funcionamiento](#-flujo-de-funcionamiento)
- [Pruebas Formales](#-pruebas-formales)
- [Salida Generada](#-salida-generada)
- [Restricciones Cumplidas](#-restricciones-cumplidas)
- [Integrantes](#-integrantes)
- [Repositorio](#-repositorio)

---

## 🧠 Descripción General

Este proyecto consiste en la implementación de un **generador de analizadores léxicos**.  
El sistema toma como entrada un archivo escrito en **YALex** y produce como salida:

1. La construcción de los **autómatas finitos deterministas (AFD)** correspondientes a las reglas léxicas.
2. La generación de un archivo fuente llamado `lexer_generado.js`, el cual funciona como un **analizador léxico independiente**.
3. La impresión en pantalla de los **tokens reconocidos** y, en caso de existir, los **errores léxicos detectados**.
4. La generación de **diagramas de transición de estados** para visualizar cada regla del lexer.

El proyecto fue desarrollado aplicando teoría de **expresiones regulares**, **construcción directa de AFD**, **minimización de autómatas** y **análisis léxico**.

---

## ✨ Características Principales

### 📄 Lectura de especificaciones YALex
- Soporte para definiciones `let`
- Soporte para reglas `rule`
- Expansión de definiciones dentro de otras expresiones
- Manejo de operadores léxicos y precedencia

### 🤖 Construcción de autómatas
- Conversión de expresiones YALex a una representación interna
- Construcción de árbol sintáctico de regex
- Cálculo de `nullable`, `firstpos`, `lastpos` y `followpos`
- Construcción directa de AFD
- Minimización del autómata resultante

### 🔎 Análisis léxico
- Reconocimiento de tokens válidos
- Detección de errores léxicos
- Aplicación de la regla de **máximo lexema válido**
- Desempate por **prioridad según orden de definición**
- Soporte para reglas `skip`, como espacios y saltos de línea

### 📦 Generación automática
- Generación automática de `lexer_generado.js`
- El lexer generado funciona de forma **independiente del generador**
- Exportación de diagramas de estados en formato `.dot` y `.png`

---

## 🎯 Objetivos del Proyecto

### Objetivo general
Implementar un generador de analizadores léxicos funcional basado en especificaciones escritas en YALex.

### Objetivos específicos
- Aplicar la teoría de analizadores léxicos en una herramienta de software.
- Implementar un generador capaz de construir analizadores léxicos funcionales.
- Utilizar autómatas finitos como base para el reconocimiento léxico.
- Producir un lexer independiente capaz de analizar nuevos archivos de entrada.

---

## 🛠 Tecnologías Utilizadas

### Lenguajes
- **Python** para la construcción del generador
- **JavaScript** para el lexer generado

### Conceptos teóricos aplicados
- Expresiones regulares
- Árboles sintácticos
- Construcción directa de AFD
- Minimización de AFD
- Análisis léxico
- Regla de longest match
- Prioridad por orden de reglas

### Herramientas
- **Graphviz** para la generación de diagramas de estados
- **Node.js** para ejecutar el lexer generado
- **GitHub** para control de versiones

---

## 📁 Estructura del Proyecto

```bash
Proyecto01_Generador-de-analizadores-lexicos/
├── codegen.py                  # Generación del lexer en JavaScript
├── errors.py                   # Manejo de errores y mensajes
├── lexer_builder.py            # Construcción del lexer y tokenización
├── main.py                     # Punto de entrada principal
├── regex_engine.py             # Construcción y minimización de AFD
├── token_utils.py              # Utilidades para nombres y tokens
├── yalex_converter.py          # Conversión de YALex a regex interna
├── yalex_parser.py             # Parser del archivo YALex
│
├── generated/
│   ├── lexer_generado.js       # Lexer generado automáticamente
│   └── diagrams/               # Diagramas de estados generados
│
├── tests/                      # Archivos de prueba
│   ├── Ejemplo_basico.yal
│   └── entrada1.txt
```

---

## ▶️ Ejecución del Proyecto

### 1. Ejecutar el generador
Desde Python:

```bash
python main.py
```

Esto realiza las siguientes tareas:
- Lee el archivo `.yal`
- Construye las reglas del lexer
- Genera los AFD
- Tokeniza el archivo de entrada
- Muestra tokens y errores léxicos
- Genera `lexer_generado.js`
- Genera los diagramas de estados

---

### 2. Ejecutar el lexer generado
Una vez creado el archivo `lexer_generado.js`, puede ejecutarse de forma independiente:

```bash
node generated/lexer_generado.js tests/entrada1.txt
```


---

## 🔄 Flujo de Funcionamiento

El flujo general del proyecto es el siguiente:

1. Se lee un archivo de especificación escrito en **YALex**.
2. Se extraen las definiciones `let` y las reglas del lexer.
3. Cada expresión se convierte a una representación interna.
4. Se construye un **AFD** por cada regla.
5. Se tokeniza el archivo de entrada aplicando:
   - máximo lexema válido
   - prioridad por orden de aparición
6. Se reportan:
   - tokens encontrados
   - errores léxicos
7. Se genera un archivo `lexer_generado.js`
8. Se generan diagramas de transición de estados

---

## 📤 Salida Generada

Durante la ejecución, el sistema produce:

### En consola
- Definiciones `let`
- Reglas del lexer
- Tokens encontrados
- Errores léxicos
- Archivo generado
- Diagramas generados

### En archivos
- `generated/lexer_generado.js`
- `generated/diagrams/*.dot`
- `generated/diagrams/*.png`

---

## 👥 Integrantes

- **Diego Ramírez**
- **Nina Nájera**
- **Eliazar Canastuj**

---

## 🔗 Repositorio

Repositorio del proyecto:

```bash
https://github.com/can23384/Proyecto01_Generador-de-analizadores-l-xicos
```
---


<div align="center">

### Proyecto académico de construcción de compiladores / lenguajes

**Generador de Analizadores Léxicos con YALex**

</div>
