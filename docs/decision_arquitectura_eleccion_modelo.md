# Decisión de arquitectura: elección de modelo

**Fecha de la comparación:** Martes 20 de octubre de 2026  
**Nombre de la miniaplicación:** Asistente de cotizaciones con RAG

## Modelo elegido

Elegí el modelo: **Gemini 3.1 Flash Lite** (`gemini-3.1-flash-lite`).

Mi miniaplicación sirve para: **generar cotizaciones comerciales fundamentadas en información recuperada mediante RAG**, consultando el catálogo de productos, precios vigentes, políticas de descuento y condiciones logísticas.

Se compararon tres modelos para responder una solicitud administrativa de cotización mediante RAG. La pregunta exige que el asistente:

- Recupere del contexto el producto, el precio vigente, las políticas de descuento por volumen y las condiciones de entrega.
- Compruebe si tres unidades califican para descuento y si la entrega en diez días es viable.
- Calcule el importe solo cuando disponga de datos suficientes.
- Identifique explícitamente los datos faltantes y no invente precios, descuentos ni condiciones.
- Responda en español, con los apartados **Procedimiento**, **Validaciones** y **Resultado esperado**, en un máximo de 180 palabras.

## Diagrama de arquitectura

**Pendiente de generar.** Se añadirá el diagrama cuando esté listo.

[Diagrama de Arquitectura](docs/diagrama_arquitectura.png)

## Comparación de candidatos

Estas son las preguntas y condiciones con las cuales se midieron los modelos, y son especififcas para este prompt:

> """
Actúa como asistente inteligente de un portal administrativo de cotizaciones que utiliza 
RAG (Retrieval-Augmented Generation). El sistema recupera información desde una base de 
conocimiento con catálogos de productos, tarifas, políticas de descuentos y condiciones comerciales.
Explica cómo procesarías la siguiente solicitud de un administrador: generar una cotización 
para un cliente que solicita tres unidades de un producto, con entrega en diez días y un posible 
descuento por volumen. Describe cómo utilizarías el contexto recuperado para verificar precios 
y condiciones, calcular el importe cuando los datos sean suficientes, identificar información 
faltante y presentar una cotización clara. No inventes precios, descuentos ni condiciones 
que no estén respaldados por las fuentes recuperadas. Si falta información, indícala explícitamente.
Responde en español, en un máximo de 180 palabras, utilizando los apartados: Procedimiento, 
Validaciones y Resultado esperado.
"""


1. ¿Cómo recuperarías mediante RAG el precio unitario del producto y las políticas vigentes de descuentos por volumen?
2. ¿Cómo verificarías si una compra de tres unidades califica para un descuento, sin asumir que existe uno?
3. ¿Cómo comprobarías si la entrega en diez días es viable según las condiciones logísticas recuperadas?
4. ¿Qué harías si faltan datos como el identificador del producto, el destino, el costo de envío, los impuestos o la disponibilidad?
5. ¿Cómo evitarías inventar datos y presentarías una cotización verificable cuando la información sea incompleta?
6. ¿La respuesta respeta la estructura solicitada, el idioma español y el límite de 180 palabras?

| Criterio | Gemini 3.6 Flash | Gemini 3.8 Flash | Gemini 3.1 Flash Lite |
|---|---:|---:|---:|
| Tarifa de entrada en USD por millón de tokens | $0.75 | $0.75 | $0.25 |
| Tarifa de salida en USD por millón de tokens | $3.75 | $3.75 | $1.50 |
| Latencias observadas en segundos (ejecuciones 1, 2 y 3) | 8.60; 9.34; 8.03 | 24.30; 17.09; 34.98 | 19.01; 13.10; 4.97 |
| Latencia promedio de las tres ejecuciones | 8.66 s | 25.46 s | 12.36 s |
| Costo promedio por petición observado | $0.00486075 (ej. 1); $0.00488400 (ej. 2); $0.00477337 (ej. 3) | $0.00428138 (ej. 1); $0.00437962 (ej. 2); $0.00457275 (ej. 3) | $0.00041225 (ej. 1); $0.00042450 (ej. 2); $0.00042150 (ej. 3) |
| Calidad para nuestra miniaplicación | Buena: respuestas estructuradas, verificaciones explícitas y velocidad relativamente estable | Buena y detallada: analiza logística y datos faltantes, pero presenta mayor latencia y más fallos en la tercera ejecución | Adecuada: cubre las validaciones esenciales y evita asumir datos; destaca por costo y por su mejor latencia en la tercera ejecución |
| Respuestas exitosas registradas (ejecuciones 1, 2 y 3) | 2/4; 4/4; 4/5 | 4/4; 4/4; 4/8 | 2/4; 4/4; 4/5 |

**Fuente de las tarifas:** los valores de entrada y salida se tomaron de la tabla de comparación proporcionada. La tabla original expresa los precios por cada 1.000 tokens; aquí se convirtieron a un millón de tokens. La referencia URL del proveedor no aparece en los registros disponibles, por lo que conviene verificar las tarifas vigentes en la documentación oficial antes del despliegue.

- **Gemini 3.6 Flash:** $0.75 USD por millón de tokens de entrada y $3.75 USD por millón de tokens de salida.
- **Gemini 3.8 Flash:** $0.75 USD por millón de tokens de entrada y $3.75 USD por millón de tokens de salida.
- **Gemini 3.1 Flash Lite:** $0.25 USD por millón de tokens de entrada y $1.50 USD por millón de tokens de salida.

**Observación sobre las pruebas:** se hicieron tres ejecuciones y la cantidad de intentos no fue idéntica en todos los casos. Se registraron errores de disponibilidad HTTP 503 y tiempos de espera. Estos errores cuentan como fallos de ejecución, pero por sí solos no demuestran que el modelo razone peor. La latencia promedio de esta tabla es el promedio aritmético de las tres latencias medias informadas en cada ejecución; no es una medición única de todas las solicitudes.

## Justificación

Elegí **Gemini 3.1 Flash Lite** porque para nuestra aplicación necesitamos respuestas fundamentadas, validaciones comerciales esenciales, bajo costo y una latencia reducida.

Lo que observé en las pruebas fue que el modelo cubrió la consulta RAG, la comprobación del umbral de descuento para tres unidades, la validación de la entrega en diez días y la identificación de datos faltantes. En la segunda ejecución completó cuatro respuestas sin fallos y en la tercera completó las cuatro respuestas requeridas después de un error HTTP 503. Además, su costo promedio por petición fue de aproximadamente $0.00042 USD, considerablemente inferior al de los otros candidatos.

El criterio más relevante para mi decisión fue **la relación entre costo, velocidad y cumplimiento de las validaciones funcionales**, sin sacrificar la regla de no inventar información.

Una limitación que encontré en mi elección fue que **no estuvo libre de fallos de disponibilidad**: en la primera y tercera ejecución se registraron errores. Por eso, la integración debería incluir reintentos con espera progresiva, manejo explícito de errores y pruebas de regresión. Los cálculos comerciales finales deberían realizarse con lógica determinista en el código cuando corresponda, en lugar de depender exclusivamente del modelo.

## Alternativa descartada y por qué

Descarté **Gemini 3.6 Flash** como primera opción porque, aunque fue rápido y produjo respuestas bien estructuradas, su costo por petición fue aproximadamente diez veces mayor que el de Flash Lite en las pruebas observadas.

También descarté **Gemini 3.8 Flash** como primera opción porque sus respuestas fueron detalladas y consistentes en las dos primeras ejecuciones, pero tuvo la mayor latencia promedio calculada entre las tres ejecuciones y cuatro fallos de ocho intentos en la tercera. Puede ser una alternativa si se prioriza el nivel de detalle por encima de la rapidez.

La decisión se basa en estas pruebas concretas; antes de producción conviene ampliar la muestra y verificar nuevamente las tarifas vigentes.
