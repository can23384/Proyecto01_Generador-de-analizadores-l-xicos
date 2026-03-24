# Proyecto 01 - Generador de analizadores léxicos

## Integrantes

- **Diego Ramírez**
- **Nina Nájera**
- **Eliazar Canastuj**

## Descripción general

Este proyecto implementa un **generador de analizadores léxicos** a partir de especificaciones escritas en un subconjunto funcional de **YALex**. A partir de un archivo `.yal`, el sistema construye autómatas finitos deterministas para cada regla léxica, genera sus diagramas de transición y produce un archivo fuente independiente en JavaScript llamado `lexer_generado.js`.

Además, el proyecto incluye ejecución de pruebas con archivo de entrada, reporte de tokens encontrados, detección de errores léxicos y una interfaz gráfica de usuario en la versión que incluye la carpeta `ui/`.

## Objetivo del proyecto

Desarrollar una herramienta capaz de:

- leer una especificación léxica en YALex,
- interpretar definiciones `let` y reglas `rule tokens`,
- convertir expresiones regulares a autómatas finitos,
- generar analizadores léxicos funcionales,
- reportar tokens y errores léxicos,
- producir diagramas de estados para las reglas implementadas.

## Funcionalidades implementadas

### 1. Parser de especificaciones YALex

El sistema analiza archivos `.yal` y extrae:

- definiciones `let`,
- nombre de la regla principal,
- expresiones regulares asociadas a cada token,
- acciones léxicas,
- validaciones básicas de sintaxis.

Se implementó soporte para los siguientes elementos de la especificación:

- identificadores definidos previamente con `let`,
- literales entre comillas simples y dobles,
- clases de caracteres `[ ... ]`,
- clases negadas `[^ ... ]`,
- diferencia de conjuntos `expr1 # expr2`,
- operador comodín `_`,
- regla especial `eof`,
- caracteres escapados como `\n`, `\t`, `\r`, `\\`, `\'`, `\"` y escapes de operadores como `\+`.

También se agregó validación para detectar identificadores no definidos en reglas o expresiones.

### 2. Conversión de YALex a expresión para el motor interno

Las expresiones YALex se traducen a una representación compatible con el motor de expresiones regulares del proyecto. En esta etapa se resuelven:

- expansión de definiciones `let`,
- cadenas literales,
- clases de caracteres y clases negadas,
- diferencia de conjuntos,
- símbolos especiales internos para distinguir operadores de símbolos literales.

Esta fase evita el problema de procesar la entrada únicamente carácter por carácter sin distinguir correctamente operadores, símbolos escapados o componentes estructurales de la expresión regular.

### 3. Motor de expresiones regulares

El proyecto implementa un motor propio de expresiones regulares sin usar librerías externas de regex para el reconocimiento.

El flujo general es el siguiente:

1. tokenización de la expresión regular,
2. inserción explícita de concatenación,
3. conversión a notación postfix,
4. construcción del árbol sintáctico,
5. cálculo de `nullable`, `firstpos`, `lastpos` y `followpos`,
6. construcción del AFD directo,
7. minimización del autómata.

De esta manera, el reconocimiento se basa en **autómatas finitos**, como exige el enunciado del proyecto.

### 4. Construcción del analizador léxico

A partir de las reglas definidas en YALex, el sistema construye un lexer que:

- escoge el **lexema más largo**,
- rompe empates por **prioridad según el orden de definición**,
- permite reglas que se ignoran con acciones de tipo `skip`,
- reconoce tokens y sus posiciones de línea y columna,
- reporta errores léxicos.

La estrategia de recuperación ante error fue ajustada para consumir únicamente el carácter inválido y continuar el análisis, evitando que se pierdan tokens válidos posteriores.

### 5. Generación del archivo independiente

El proyecto genera un archivo JavaScript independiente:

- `generated/lexer_generado.js`

Este archivo incluye:

- las reglas del lexer,
- los AFD serializados,
- la lógica de avance de estados,
- tokenización del texto de entrada,
- detección de errores léxicos,
- soporte para `EOF`.

El analizador generado puede ejecutarse de manera independiente del generador.

### 6. Generación de diagramas de estados

Para cada regla léxica, el proyecto genera:

- un archivo `.dot`,
- y, si Graphviz está instalado, una imagen `.png`.

Los diagramas se almacenan en:

- `generated/diagrams/`

Esto permite visualizar el AFD correspondiente a cada token implementado.

### 7. Interfaz gráfica

En la versión del proyecto que incluye la carpeta `ui/`, se implementó una interfaz gráfica en Python para facilitar el uso del generador. La interfaz permite:

- abrir archivos `.yal`,
- abrir archivos `.txt`,
- guardar cambios,
- ejecutar la generación del lexer,
- visualizar tokens,
- visualizar errores,
- mostrar el archivo `lexer_generado.js`,
- previsualizar diagramas generados.

La interfaz fue diseñada con estilo oscuro y distribución tipo mini IDE para hacerla más amigable para el usuario.

## Estructura general del proyecto

La estructura incluye estos módulos:

- `yalex_parser.py`: parser del archivo `.yal`.
- `yalex_converter.py`: traducción de expresiones YALex al formato del motor interno.
- `regex_engine.py`: implementación del motor de expresiones regulares y construcción del AFD.
- `lexer_builder.py`: armado del lexer y tokenización.
- `codegen.py`: generación del archivo JavaScript independiente.
- `errors.py`: manejo y formateo de errores.
- `token_utils.py`: inferencia y normalización de nombres de tokens.
- `main.py`: ejecución por consola.
- `tests/`: archivos de prueba.
- `generated/`: salida generada por el sistema.
- `ui/`: interfaz gráfica.

## Flujo de funcionamiento

### Entrada del generador

- Un archivo `.yal` con la especificación del analizador léxico.

### Salida del generador

- diagramas `.dot` y `.png` de los AFD,
- archivo fuente independiente `lexer_generado.js`.

### Entrada del analizador léxico generado

- un archivo de texto plano con cadenas de entrada.

### Salida del analizador léxico

- tokens reconocidos,
- errores léxicos detectados con línea y columna.

## Casos de prueba implementados

Se trabajó con al menos los siguientes tipos de prueba:

### Caso de complejidad baja

Prueba de:

- palabras reservadas,
- identificadores,
- números,
- operador `+`,
- asignación,
- espacios ignorados.

### Caso de complejidad media

Prueba de:

- operadores relacionales de uno y dos caracteres,
- prioridad de reglas,
- palabras reservadas,
- paréntesis, llaves y punto y coma,
- identificadores y números,
- omisión de whitespace.

### Caso de complejidad alta

Prueba de:

- diferencia de conjuntos con `#`,
- reconocimiento de palabras formadas solo por consonantes,
- distinción entre `CONS` e `ID`,
- operador `:=`,
- operador `+` escapado,
- palabras reservadas,
- números y espacios.

### Caso adicional de error léxico

Se probó una entrada con símbolo inválido en medio de tokens válidos para confirmar que:

- el error se detecta correctamente,
- se reporta con línea y columna,
- el análisis continúa sin perder los tokens posteriores.

## Cómo ejecutar el proyecto

### Ejecución por consola

Desde la carpeta raíz del proyecto:

```bash
python main.py
```

La ejecución por consola:

1. parsea el archivo YALex configurado en `main.py`,
2. construye el lexer,
3. procesa el archivo de entrada,
4. imprime tokens y errores,
5. genera el archivo `generated/lexer_generado.js`,
6. genera diagramas `.dot` y, si es posible, `.png`.

### Ejecución de la interfaz gráfica

Se puede ejecutar con:

```bash
python -m ui.app
```

En esta versión se recomienda usar un entorno con **Python de 64 bits** si la interfaz depende de PySide6.

## Dependencias

### Obligatorias

- Python 3.x

### Opcionales o recomendadas

- Graphviz, para convertir automáticamente los archivos `.dot` a `.png`
- PySide6, en la versión con interfaz gráfica

## Decisiones de diseño relevantes

- Se evitó el uso de librerías de expresiones regulares para el reconocimiento léxico.
- Se usaron autómatas finitos para cumplir con la restricción principal del proyecto.
- Se separó el generador del analizador generado para mantener independencia entre ambos.
- Se implementó priorización por orden de regla y política de lexema más largo.
- Se agregaron archivos de prueba representativos de baja, media y alta complejidad.

## Repositorio

```bash
https://github.com/can23384/Proyecto01_Generador-de-analizadores-l-xicos
```

## Documentación del código

El código está organizado por responsabilidades para facilitar su comprensión:

- parsing de la especificación,
- conversión a regex interna,
- construcción del autómata,
- tokenización,
- generación de código,
- visualización de resultados.

Esto permite explicar el proyecto por módulos durante la presentación y defender con claridad el flujo completo de generación.

## Observaciones finales

El proyecto logra construir analizadores léxicos funcionales a partir de una especificación YALex, generar su representación por autómatas y producir un archivo fuente independiente para el análisis léxico. Además, incorpora pruebas representativas y, en su versión gráfica, una interfaz orientada a mejorar la experiencia de uso.
