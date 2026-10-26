# Evaluación comparativa de modelos Gemini para cotizaciones con RAG

> **Documentos relacionados, para mas profundidad:** [Evaluación comparativa de modelos Gemini para cotizaciones con RAG](01_resumen_evaluacion_modelos_rag.md) y [Comparación de modelos Gemini: resultados completos](comparacion_modelos_markdown.md).

> Este informe sintetiza las tres ejecuciones registradas en el documento vinculado y evalúa los modelos para el caso de uso descrito. Para realizar la evaluación me he basado en  los resultados obtenidos en las pruebas realizadas.  con el codigo de [comparar_modelos.py](../src/comparar_modelos.py)

## 1. Objetivo y criterio de evaluación

Se compararon tres modelos para responder una solicitud administrativa de cotización mediante RAG. La pregunta exige que el asistente:

- Recupere del contexto el producto, el precio vigente, las políticas de descuento por volumen y las condiciones de entrega.
- Compruebe si tres unidades califican para descuento y si la entrega en diez días es viable.
- Calcule el importe solo cuando disponga de datos suficientes.
- Identifique explícitamente los datos faltantes y no invente precios, descuentos ni condiciones.
- Responda en español, con los apartados **Procedimiento**, **Validaciones** y **Resultado esperado**, en un máximo de 180 palabras.

> **Mismo prompt para todos los modelos y las cuatro repeticiones.**  
>
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


La evaluación considera tanto el contenido de las respuestas como las métricas observadas: latencia, costo y éxito de las solicitudes. Las tasas de error HTTP 503 y de tiempo de espera se interpretan como fallos observados durante las pruebas; los registros no permiten atribuirlos exclusivamente al razonamiento del modelo.

## 2. Tabla resumen de las tres ejecuciones

Los valores de cada fila proceden de la tabla comparativa correspondiente a esa ejecución. Los costos están expresados en USD. El costo total corresponde al total de las pruebas exitosas indicado por el registro.

| Ejecución | Modelo | Latencia promedio | Costo promedio por petición | Costo total de pruebas exitosas | Solicitudes exitosas | Solicitudes fallidas | Lectura principal |
|---|---|---:|---:|---:|---:|---:|---|
| 1 | Gemini 3.6 Flash | 8,60 s | $0.00486075 | $0.00972150 | 2/4 (50 %) | 2/4 (50 %) | Rápido y con respuestas alineadas con el proceso de cotización, pero con fallos de disponibilidad. |
| 1 | Gemini 3.8 Flash | 24,30 s | $0.00428138 | $0.01712550 | 4/4 (100 %) | 0/4 (0 %) | Respuestas consistentes y completas en esta ejecución, a costa de mayor latencia. |
| 1 | Gemini 3.1 Flash Lite | 19,01 s | $0.00041225 | $0.00082450 | 2/4 (50 %) | 2/4 (50 %) | Mucho más económico; hubo fallos y una latencia media elevada en esta primera prueba. |
| 2 | Gemini 3.6 Flash | 9,34 s | $0.00488400 | $0.01953600 | 4/4 (100 %) | 0/4 (0 %) | Respuestas estructuradas, verificaciones explícitas y buen tiempo de respuesta. |
| 2 | Gemini 3.8 Flash | 17,09 s | $0.00437962 | $0.01751850 | 4/4 (100 %) | 0/4 (0 %) | Respuestas detalladas y completas; más lento que Gemini 3.6 Flash. |
| 2 | Gemini 3.1 Flash Lite | 13,10 s | $0.00042450 | $0.00169800 | 4/4 (100 %) | 0/4 (0 %) | Mantuvo la estructura y las reglas de no inventar datos con un costo muy inferior. |
| 3 | Gemini 3.6 Flash | 8,03 s | $0.00477337 | $0.01909350 | 4/4 (100 %) | 1/5 (20 % de los intentos) | Rápido y consistente en contenido; necesitó un intento adicional por un HTTP 503. |
| 3 | Gemini 3.8 Flash | 34,98 s | $0.00457275 | $0.01829100 | 4/8 (50 % de los intentos) | 4/8 (50 %) | Respuestas de buena calidad, pero latencia alta y más fallos de disponibilidad en esta ejecución. |
| 3 | Gemini 3.1 Flash Lite | 4,97 s | $0.00042150 | $0.00168600 | 4/5 (80 % de los intentos) | 1/5 (20 % de los intentos) | El más rápido y económico; completó las cuatro respuestas requeridas tras un fallo HTTP 503. |

**Nota sobre los denominadores:** En la primera ejecución se hicieron cuatro peticiones por modelo. En la segunda se completaron cuatro respuestas exitosas por modelo. En la tercera se siguió intentando hasta obtener cuatro respuestas exitosas, por lo que el número total de intentos varió. Por esa razón, la tabla muestra los conteos de éxito y fallo tal como aparecen en los registros, sin comparar directamente conteos con denominadores diferentes.

## 3. Comparación del comportamiento frente a la pregunta

### Gemini 3.6 Flash

**Comportamiento observado**
- Repite de manera consistente el flujo esperado de RAG: recuperar ficha o SKU, precio vigente, descuentos y condiciones logísticas.
- Verifica si tres unidades alcanzan el umbral de descuento y si diez días cumplen el plazo de entrega.
- Identifica datos faltantes como SKU, ubicación de destino, flete, impuestos o disponibilidad.
- En general, propone una cotización desglosada y evita inventar datos cuando el contexto no los respalda.
- Sus latencias fueron bajas y relativamente estables: entre 8,03 y 9,34 segundos en las ejecuciones segunda y tercera.
- Tuvo fallos de servicio en las ejecuciones primera y tercera, aunque en ambas logró completar cuatro respuestas exitosas.

**Evaluación para el caso de uso:** buen equilibrio entre velocidad, estructura y detalle. Su costo por petición es considerablemente superior al de Flash Lite.

### Gemini 3.8 Flash

**Comportamiento observado**
- Produce respuestas detalladas que cubren precio, umbral de descuento, plazo, logística, impuestos, stock y datos pendientes.
- Distingue entre información completa e incompleta y condiciona el cálculo a que las fuentes sean suficientes.
- Sus respuestas suelen describir de forma explícita qué hacer si el descuento no corresponde o si faltan datos.
- Presentó la mayor latencia media en la tercera ejecución (34,98 segundos).
- En la primera y segunda ejecuciones consiguió cuatro respuestas exitosas; en la tercera necesitó ocho intentos para lograr cuatro éxitos, con cuatro fallos registrados.

**Evaluación para el caso de uso:** la calidad y amplitud de las respuestas es buena, pero la demora y los fallos observados en la tercera ejecución reducen su conveniencia cuando se prioriza una respuesta rápida y un flujo administrativo estable. No se puede concluir que siempre sea menos fiable: los resultados variaron entre ejecuciones.

### Gemini 3.1 Flash Lite

**Comportamiento observado**
- Mantiene los apartados solicitados y una secuencia sencilla: recuperación, análisis, validación y cotización.
- Comprueba la existencia del producto, el precio, el umbral de descuento para tres unidades y la viabilidad de los diez días.
- Indica que solo aplicará descuentos respaldados por la política recuperada y evita hacer cálculos con supuestos.
- Puede solicitar datos pendientes, por ejemplo, ID del producto, ubicación de entrega, stock o información del cliente.
- Es el modelo más barato en las tres tablas, con un costo promedio por petición cercano a $0.00042 USD.
- En la tercera ejecución registró la menor latencia media (4,97 segundos). En la segunda completó las cuatro respuestas sin fallos; en la primera tuvo dos fallos y solo dos respuestas exitosas.

**Evaluación para el caso de uso:** ofrece la mejor relación observada entre costo y velocidad, manteniendo las validaciones centrales requeridas. Sus fallos en algunas ejecuciones hacen recomendable implementar reintentos y supervisión.

## 4. Tabla resumen del desempeño global

| Criterio | Gemini 3.6 Flash | Gemini 3.8 Flash | Gemini 3.1 Flash Lite |
|---|---|---|---|
| Recuperación RAG y consulta de fuentes | Consistente | Consistente y detallada | Adecuada y directa |
| Validación de precio y descuento por 3 unidades | Explícita | Explícita y detallada | Explícita |
| Validación de entrega en 10 días | Sí | Sí, suele considerar logística/SLA | Sí |
| Manejo de datos faltantes | Bueno; enumera SKU, flete, impuestos o destino | Muy detallado; incluye stock, impuestos, flete y condiciones | Bueno; suele pedir datos concretos pendientes |
| Respeto de la regla de no inventar | Reiterado en las respuestas | Reiterado en las respuestas | Reiterado en las respuestas |
| Estructura pedida | Generalmente respeta los tres apartados | Generalmente respeta los tres apartados | Generalmente respeta los tres apartados |
| Velocidad observada | Alta y relativamente estable en ejecuciones 2 y 3 | Variable; fue el más lento en ejecución 3 | Mejor resultado de velocidad en ejecución 3 |
| Costo observado | Alto frente a Flash Lite | Alto frente a Flash Lite | El más bajo, alrededor de 9–12 veces más barato por petición que los otros modelos según las tablas |
| Estabilidad observada | Completó 4 respuestas en cada ejecución, con reintento en la tercera | Variable; 4 fallos en la tercera ejecución | Variable; completó 4 respuestas en cada ejecución, con reintentos en primera y tercera |
| Adecuación global al caso | Buena alternativa equilibrada | Útil si prima el detalle sobre la latencia | **Mejor opción para costo y velocidad, con reintentos** |

## 5. ¿Qué modelo tuvo el mejor desempeño para este caso?

### Recomendación: Gemini 3.1 Flash Lite

**Según los registros disponibles, Gemini 3.1 Flash Lite es la mejor opción para este caso de uso si se priorizan costo, velocidad y cumplimiento de las validaciones esenciales de la cotización.**

Las razones son:

1. **Costo considerablemente menor.** Su costo promedio por petición se mantuvo entre $0.00041225 y $0.00042450 USD, mientras que los otros modelos se situaron aproximadamente entre $0.00428 y $0.00488 USD.
2. **Velocidad.** En la tercera ejecución obtuvo la menor latencia media observada: 4,97 segundos. Sus respuestas exitosas de esa ejecución cubrieron las validaciones clave de la pregunta.
3. **Alineación funcional.** Sus respuestas contemplan la consulta RAG, la verificación de precios, la regla de descuento para tres unidades, la validación del plazo de diez días y la identificación de información faltante.
4. **Resultados repetidos.** En la segunda ejecución completó cuatro respuestas con cero fallos; en la tercera completó las cuatro respuestas requeridas tras un HTTP 503.

**Matiz importante:** no fue el modelo con menos fallos en todas las pruebas. En la primera ejecución solo consiguió dos respuestas exitosas de cuatro. Gemini 3.6 Flash es una alternativa si se prefiere más detalle y latencias bajas con un costo mayor; Gemini 3.8 Flash ofrece respuestas extensas, pero su latencia fue alta y sus fallos aumentaron en la tercera ejecución.

Los errores HTTP 503 y los tiempos de espera deben tratarse como problemas observados en las llamadas al servicio, no como prueba de que el modelo razone peor. Los registros no permiten separar con certeza la disponibilidad del proveedor de la calidad de generación.

## 6. Recomendaciones para llevarlo a producción

- **Reintentos controlados:** implementar reintentos limitados para HTTP 503 y tiempos de espera, con espera incremental (*exponential backoff*) y variación aleatoria.
- **Validación determinista:** calcular subtotal, descuento, impuestos y total con código de negocio, no dejando la aritmética comercial exclusivamente al modelo.
- **Respuestas fundamentadas:** exigir que los datos usados en la cotización provengan del contexto recuperado e incluir referencias internas a las fuentes cuando sea posible.
- **Manejo de información incompleta:** si faltan SKU, precio, política de descuento, destino o tarifa de envío, devolver una cotización preliminar con esos campos pendientes.
- **Pruebas de regresión:** repetir el mismo conjunto de preguntas con suficientes muestras y medir por separado calidad de respuesta, latencia, costo y disponibilidad.
- **Control del límite de palabras:** comprobar automáticamente que la respuesta final no supere las 180 palabras y contenga los tres apartados requeridos.

## 7. Conclusión

Para una función de cotizaciones basada en RAG, **Gemini 3.1 Flash Lite es la recomendación inicial por eficiencia económica y rapidez**, siempre que se acompañe de reintentos y validaciones de negocio deterministas. Gemini 3.6 Flash es una alternativa equilibrada cuando se valora una respuesta algo más elaborada. Gemini 3.8 Flash puede ser útil cuando el detalle adicional justifique una mayor latencia.

Esta conclusión se limita a las tres ejecuciones documentadas y al tipo de pregunta evaluada; no constituye una garantía de rendimiento para otros conjuntos de consultas o condiciones de servicio.


