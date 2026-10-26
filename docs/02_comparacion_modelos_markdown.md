# Comparación de modelos Gemini para cotizaciones con RAG

```powershell
(venv) PS C:\Bootcamp_Skillnest_IA_generativa\Proyecto_IA> py .\comparar_modelos.py
```

## Modelo: Gemini 3.6 Flash

- **ID:** `gemini-3.6-flash`

### Petición 1/4

> **ERROR: HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.**

### Petición 2/4

- **Latencia:** 7.84 segundos
- **Costo estimado:** $0.00446700 USD
- **Tokens de entrada:** 191
- **Tokens de salida facturables:** 1153

**Respuesta:**

**Procedimiento:**
Analizo la solicitud (tres unidades, entrega en diez días y descuento por volumen) y ejecuto una búsqueda semántica mediante RAG en la base de conocimiento para recuperar: catálogo de productos, lista de tarifas vigentes, tabla de descuentos por cantidad y políticas de tiempos de entrega.

**Validaciones:**
Contrasto la solicitud con el contexto recuperado para verificar:
1. Existencia del producto y su precio unitario base.
2. Si la cantidad de 3 unidades alcanza el umbral para aplicar descuento por volumen según la normativa vigente.
3. Si el plazo de 10 días cumple con el tiempo de entrega estándar.

*Nota:* No inventaré precios ni condiciones. Si el contexto recuperado no contiene el producto exacto, la política de descuentos para 3 unidades o los plazos de envío, lo señalaré explícitamente como información faltante.

**Resultado esperado:**
Si los datos son suficientes, presento una cotización estructurada con: precio unitario, descuento aplicado, costo de envío y total calculado. De lo contrario, emito un borrador parcial indicando con precisión los campos requeridos para completar el cálculo.

### Petición 3/4

> **ERROR: HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.**

### Petición 4/4

- **Latencia:** 9.37 segundos
- **Costo estimado:** $0.00525450 USD
- **Tokens de entrada:** 191
- **Tokens de salida facturables:** 1363

**Respuesta:**

**Procedimiento**
Consulto la base de conocimiento mediante RAG para extraer el precio unitario del producto exacto, la escala de descuentos por volumen y las políticas de tiempo y costo de entrega asociadas al plazo de 10 días.

**Validaciones**
Verifico en los documentos recuperados si 3 unidades alcanzan el umbral necesario para un descuento por volumen y si el tiempo de entrega solicitado es viable. Si el contexto contiene datos completos, calculo el subtotal, el descuento aplicable y el total. Si falta información crítica (como el nombre/código exacto del producto, la ubicación de entrega o las tarifas vigentes), señalo explícitamente los campos faltantes sin inventar precios ni condiciones.

**Resultado esperado**
Una propuesta desglosada y clara que incluye: precio base, descuento aplicado (si procede), confirmación del plazo de entrega y costo total, todo respaldado por las fuentes. En caso de información insuficiente en la base de datos, presento un informe con los datos faltantes necesarios para procesar la solicitud.

## Modelo: Gemini 3.8 Flash

- **ID:** `gemini-3.8-flash`

### Petición 1/4

- **Latencia:** 39.66 segundos
- **Costo estimado:** $0.00418200 USD
- **Tokens de entrada:** 191
- **Tokens de salida facturables:** 1077

**Respuesta:**

**Procedimiento:**
Ejecuto una búsqueda semántica en la base de conocimiento para recuperar: el precio unitario del producto, la política de descuentos por volumen (verificando el umbral para 3 unidades) y los términos logísticos para entregas en 10 días.

**Validaciones:**
1. **Precios y descuentos:** Compruebo en las fuentes si 3 unidades califican para rebaja por volumen; si la política exige un mínimo mayor (ej. 5 o 10 unidades), no aplico descuento.
2. **Plazos:** Valido si el catálogo logístico respalda el compromiso de entrega en 10 días.
3. **Información faltante:** Si el contexto omite el SKU exacto, impuestos o costos de flete, los declaro explícitamente como datos pendientes, sin inventar cifras.

**Resultado esperado:**
Si los datos están completos, genero un desglose formal: precio base, porcentaje de descuento respaldado, costos adicionales, fecha estimada e importe total calculado. Si faltan datos, presento una cotización preliminar detallando con precisión la información comercial o logística que el administrador debe suministrar.

### Petición 2/4

- **Latencia:** 25.67 segundos
- **Costo estimado:** $0.00433575 USD
- **Tokens de entrada:** 191
- **Tokens de salida facturables:** 1118

**Respuesta:**

**Procedimiento**
Consulto la base de conocimiento mediante RAG para recuperar la tarifa vigente del producto, la escala de descuentos por volumen y los plazos estándar de logística y entrega.

**Validaciones**
1. **Precios y descuentos:** Verifico si tres unidades alcanzan el umbral para descuento por volumen. Si la política exige un mínimo mayor, aplico el precio de lista oficial.
2. **Plazo de entrega:** Valido si diez días cumplen con las condiciones comerciales y tiempos de despacho estipulados.
3. **Información faltante:** Si no se recupera el SKU exacto, costo de flete, impuestos aplicables o disponibilidad de inventario, lo indico explícitamente sin asumir valores.

**Resultado esperado**
- **Con datos completos:** Genero un desglose formal con precio unitario, porcentaje de descuento (si aplica), subtotal, impuestos, total y confirmación de entrega en diez días.
- **Con datos incompletos:** Presento una cotización preliminar que detalla los cálculos posibles y lista puntualmente los datos pendientes (por ejemplo, confirmación de stock o validación de flete) para que el administrador los complete.

### Petición 3/4

- **Latencia:** 18.25 segundos
- **Costo estimado:** $0.00386700 USD
- **Tokens de entrada:** 191
- **Tokens de salida facturables:** 993

**Respuesta:**

**Procedimiento**
Consulto la base vectorial indexando el identificador del producto, la cantidad (3 unidades) y el plazo (10 días). Recupero la tarifa base vigente, las escalas de descuentos por volumen y las condiciones de logística/entrega.

**Validaciones**
1. *Precios y Descuentos:* Verifico si 3 unidades alcanzan el umbral mínimo para descuento por volumen según la política comercial.
2. *Tiempos de entrega:* Valido si los 10 días hábiles son viables según los acuerdos de nivel de servicio (SLA) del catálogo.
3. *Datos faltantes:* Si el contexto recuperado omite el SKU exacto, la disponibilidad de stock, el destino para calcular fletes o impuestos, lo señalo explícitamente sin inventar cifras ni plazos.

**Resultado esperado**
- *Con información suficiente:* Emito una cotización desglosada con precio unitario, porcentaje de descuento aplicado, costos de envío, impuestos, total y vigencia de la oferta.
- *Con información faltante:* Presento un informe al administrador indicando los datos ausentes indispensables para poder generar el importe definitivo.

### Petición 4/4

- **Latencia:** 13.61 segundos
- **Costo estimado:** $0.00474075 USD
- **Tokens de entrada:** 191
- **Tokens de salida facturables:** 1226

**Respuesta:**

**Procedimiento:**
Consulto la base de conocimiento mediante RAG utilizando el producto solicitado. Recupero las tarifas vigentes, la matriz de descuentos por volumen ylas políticas de tiempos de entrega y logística.

**Validaciones:**
1. **Precios y descuentos:** Verifico en las fuentes si tres unidades alcanzan el umbral mínimo para descuento por volumen; si no aplica o no existe política para esa cantidad, mantengo la tarifa unitaria estándar.
2. **Plazo de entrega:** Valido si el compromiso de diez días es viable según los SLAs logísticos documentados.
3. **Información faltante:** Identifico vacíos críticos (SKU exacto, impuestos, gastos de envío o disponibilidad de inventario). Jamás invento cifras ausentes en los documentos.

**Resultado esperado:**
- **Con datos completos:** Presento una cotización desglosada con precio base, porcentaje de descuento aplicado (si procede), importe total y confirmación del plazo de entrega de diez días.
- **Con datos incompletos:** Presento un borrador parcial señalando explícitamente la información faltante (ej. producto no especificado o tarifas noencontradas) para que el administrador la complete antes de emitir el documento final.

## Modelo: Gemini 3.1 Flash Lite

- **ID:** `gemini-3.1-flash-lite`

### Petición 1/4

- **Latencia:** 26.89 segundos
- **Costo estimado:** $0.00041075 USD
- **Tokens de entrada:** 191
- **Tokens de salida facturables:** 242

**Respuesta:**

Aquí tienes el procedimiento para procesar la solicitud:

**Procedimiento**
1. **Recuperación:** Consultaré la base de conocimiento mediante búsqueda semántica utilizando el ID del producto para extraer su precio unitario, disponibilidad en stock y políticas de descuento por volumen.
2. **Análisis:** Compararé el plazo solicitado (10 días) contra los tiempos de entrega estándar y verificaré si las tres unidades califican para un descuento según la tabla de rangos vigente.
3. **Cálculo:** Multiplicaré el precio base por las tres unidades, aplicando el porcentaje de descuento si el contexto lo autoriza explícitamente.

**Validaciones**
- Verificación de existencia del producto y precio actualizado.
- Confirmación de que el plazo de 10 días es viable según las condiciones logísticas.
- Identificación de datos faltantes: nombre del cliente, dirección de entrega o condiciones de pago si no están en el contexto.

**Resultado esperado**
Presentaré un borrador de cotización con el desglose del importe total y los términos aplicados. Si falta información relevante, solicitaré al administrador los datos faltantes antes de finalizar.

### Petición 2/4

- **Latencia:** 11.14 segundos
- **Costo estimado:** $0.00041375 USD
- **Tokens de entrada:** 191
- **Tokens de salida facturables:** 244

**Respuesta:**

Como asistente de cotizaciones, mi proceso es el siguiente:

**Procedimiento**
1. **Consulta RAG**: Extraigo del catálogo técnico el precio unitario del producto y de las políticas comerciales los umbrales para descuentos por volumen.
2. **Análisis de viabilidad**: Verifico en los registros logísticos si el plazo de entrega de diez días cumple con los niveles de servicio estándar orequiere una gestión especial.

**Validaciones**
- **Existencia**: Confirmo que el producto y su precio estén vigentes en la base de datos.
- **Condiciones**: Evalúo si tres unidades califican para un descuento según la política vigente.
- **Integridad**: Identifico datos faltantes, como el perfil del cliente (necesario para aplicar descuentos específicos o impuestos) o la ubicación de entrega.

**Resultado esperado**
Presentaré un desglose claro: precio unitario, subtotal, descuento aplicado (o justificación de su ausencia) e importe final. Si la información es insuficiente, solicitaré explícitamente los datos faltantes antes de emitir cualquier cálculo final, garantizando que toda cifra presentada sea verificable y exacta.

### Petición 3/4

> **ERROR: Se agotó el tiempo de espera.**

### Petición 4/4

> **ERROR: HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.**

## Tabla comparativa de modelos

| Criterio | Gemini 3.6 Flash | Gemini 3.8 Flash | Gemini 3.1 Flash Lite |
|---|---:|---:|---:|
| Costo por 1.000 tokens de entrada | $0.000750 | $0.000750 | $0.000250 |
| Costo por 1.000 tokens de salida | $0.003750 | $0.003750 | $0.001500 |
| Latencia promedio observada | 8.60 s | 24.30 s | 19.01 s |
| Costo promedio por petición | 0.00486075 USD | 0.00428138 USD | 0.00041225 USD |
| Costo total de pruebas exitosas | 0.00972150 USD | 0.01712550 USD | 0.00082450 USD |
Gemini 3.6 Flash: 2 exitosas, 2 fallidas.
Gemini 3.8 Flash: 4 exitosas, 0 fallidas.
Gemini 3.1 Flash Lite: 2 exitosas, 2 fallidas.

```powershell
(venv) PS C:\Bootcamp_Skillnest_IA_generativa\Proyecto_IA> py .\comparar_modelos.py
```

## Modelo: Gemini 3.6 Flash

- **ID:** `gemini-3.6-flash`
- **Respuestas exitosas requeridas: 4**

### Intento 1/12 | Respuestas exitosas: 0/4

- **Estado: EXITOSA (1/4)**
- **Latencia:** 9.93 segundos
- **Costo:** $0.00524400 USD

**Respuesta:**

**Procedimiento**
Consulto la base de conocimiento mediante RAG para extraer el precio base del producto, la política de descuentos aplicable a un volumen de tres unidades y las condiciones de tiempos de entrega para confirmar la factibilidad del plazo de diez días.

**Validaciones**
Verifico en el contexto recuperado el precio unitario exacto y si tres unidades alcanzan el umbral para un descuento por volumen según la normativa vigente. Compruebo que el tiempo de preparación y logística no supere los diez días. Si la información es suficiente, calculo el subtotal, descuento e importe total. Si detecto vacíos (como el código exacto del producto, costos de envío o impuestos), jamás invento datos y los señalo formalmente.

**Resultado esperado**
Presento una cotización clara y estructurada. Si la información fuente está completa, detallo: precio unitario, porcentaje de descuento aplicado, confirmación del plazo de entrega y monto total. En caso contrario, muestro únicamente los datos verificados y desgloso explícitamente la información faltante requerida para finalizar la cotización.

### Intento 2/12 | Respuestas exitosas: 1/4

- **Estado: EXITOSA (2/4)**
- **Latencia:** 8.34 segundos
- **Costo:** $0.00474900 USD

**Respuesta:**

**Procedimiento**
Consulto la base de conocimiento mediante RAG utilizando la solicitud (3 unidades, entrega en 10 días y descuento por volumen) para recuperar el catálogo del producto especificado, la lista de precios vigentes, la tabla de descuentos por cantidad y las políticas de tiempos de envío.

**Validaciones**
1. **Precio unitario:** Verifico el costo base oficial del producto en el catálogo.
2. **Descuento por volumen:** Compruebo si 3 unidades alcanzan el umbral mínimo exigido por la política para aplicar un descuento.
3. **Plazo logístico:** Confirmo si el margen de 10 días cumple con las condiciones comerciales de entrega.
4. **Faltantes:** Identifico explícitamente si falta el código exacto del producto, la ubicación del cliente para el flete o la tarifa de envío, absteniéndome de inventar cualquier valor.

**Resultado esperado**
Si la información recuperada es completa, genero un desglose formal con el subtotal, descuento aplicado, impuestos y costo total. Si faltan datos en la base de conocimiento, presento un reporte claro indicando exactamente qué información se requiere para finalizar la cotización.

### Intento 3/12 | Respuestas exitosas: 2/4

- **Estado: EXITOSA (3/4)**
- **Latencia:** 9.69 segundos
- **Costo:** $0.00527775 USD

**Respuesta:**

**Procedimiento**
Como asistente RAG, recibo la solicitud (3 unidades, entrega en 10 días, descuento por volumen) y ejecuto una búsqueda vectorial en la base de conocimiento para recuperar la ficha del producto, tarifas vigentes, escalas de descuento y tiempos de despacho logístico.

**Validaciones**
Analizo exclusivamente el contexto recuperado, sin inventar información:
1. Verifico el precio unitario base y la disponibilidad del producto.
2. Compruebo si el volumen de 3 unidades alcanza el umbral mínimo para aplicar a la política de descuentos.
3. Valido si el tiempo de entrega de 10 días cumple con los plazos estándar de la empresa.
*Si las fuentes no contienen el precio, la escala de descuentos o el producto exacto, lo identifico explícitamente como información faltante.*

**Resultado esperado**
Presento un desglose claro. Si la información recuperada es suficiente, calculo el importe total (precio base × 3 − descuento) y confirmo la factibilidad de entrega. Si faltan datos en la base de conocimiento, emito un reporte indicando los campos específicos requeridos para completar la cotización.

### Intento 4/12 | Respuestas exitosas: 3/4

- **Estado: EXITOSA (4/4)**
- **Latencia:** 9.41 segundos
- **Costo:** $0.00426525 USD

**Respuesta:**

**Procedimiento**
Consulto la base de conocimiento mediante RAG recuperando el producto específico, su precio de lista, la tabla de descuentos por volumen y las políticas de tiempos de entrega.

**Validaciones**
Verifico en el contexto recuperado si el precio unitario está vigente, si el volumen de tres unidades alcanza el umbral para aplicar descuento y si el plazo de diez días cumple las políticas de despacho. Basándome estrictamente en las fuentes, identifico si los datos son suficientes para calcular el importe total. Si falta información (como el producto exacto, reglas de flete o escala de descuentos), la indico explícitamente sin inventar tarifas ni condiciones.

**Resultado esperado**
Con información completa, presento un borrador claro detallando: precio unitario, descuento aplicable, plazo de entrega (10 días) y el monto total final. Si existen datos faltantes, entrego un reporte preciso señalando los campos requeridos para poder completar la cotización.

**Resultado final de Gemini 3.6 Flash:**

- **Intentos realizados:** 4
- **Respuestas exitosas:** 4
- **Respuestas fallidas:** 0

## Modelo: Gemini 3.8 Flash

- **ID:** `gemini-3.8-flash`
- **Respuestas exitosas requeridas: 4**

### Intento 1/12 | Respuestas exitosas: 0/4

- **Estado: EXITOSA (1/4)**
- **Latencia:** 15.21 segundos
- **Costo:** $0.00449025 USD

**Respuesta:**

**Procedimiento**
Consulto la base de conocimiento mediante RAG para recuperar: tarifa unitaria vigente del producto, matriz de descuentos por volumen y condiciones logísticas de envío.

**Validaciones**
Con el contexto recuperado, verifico rigurosamente:
1. **Precio:** Tarifa oficial del ítem especificado.
2. **Descuento:** Si 3 unidades alcanzan el umbral según la política de volumen recuperada; si no califica o no existe regla para esa cantidad, se descarta.
3. **Plazo:** Factibilidad del envío en 10 días y posibles costes asociados.
4. **Faltantes:** Señalo datos omitidos (como SKU exacto, inventario o destino). No invento precios ni porcentajes ausentes en el contexto.

**Resultado esperado**
- **Si los datos son suficientes:** Presento un desglose formal con precio base por 3 unidades, porcentaje de descuento aplicado (conforme a la política), confirmación del plazo de 10 días y monto total.
- **Si falta información:** Muestro la cotización preliminar indicando explícitamente los datos no localizados en el sistema (ej. «Tarifa no disponible» o «Política de descuento no encontrada para 3 unidades») para su resolución manual.

### Intento 2/12 | Respuestas exitosas: 1/4

- **Estado: EXITOSA (2/4)**
- **Latencia:** 13.57 segundos
- **Costo:** $0.00437775 USD

**Respuesta:**

**Procedimiento:**
Consulto la base vectorial con los datos del producto para recuperar: precio unitario de lista, tablas de descuento por volumen y plazos logísticos de entrega vigentes.

**Validaciones:**
1. **Precios y Descuento:** Verifico el precio unitario y si 3 unidades alcanzan el umbral para descuento por volumen según las políticas recuperadas; de no alcanzarlo, no lo aplico.
2. **Plazo de entrega:** Valido si los 10 días solicitados se ajustan a las condiciones comerciales estándar o si implican recargos.
3. **Información faltante:** Identifico lagunas críticas (ej. modelo exacto, costos de envío, impuestos o falta de stock) y las declaro explícitamente sin inventar datos.

**Resultado esperado:**
Presento un desglose formal: producto, precio base, aplicación o no del descuento (justificado según la norma recuperada), validación de la entrega en 10 días y el importe total calculado. Si el contexto recuperado no contiene el precio o los términos para este caso, emito una cotización preliminar listando los datos exactos que deben completarse.

### Intento 3/12 | Respuestas exitosas: 2/4

- **Estado: EXITOSA (3/4)**
- **Latencia:** 23.87 segundos
- **Costo:** $0.00437775 USD

**Respuesta:**

**Procedimiento**
Consulto la base vectorial indexando el nombre del producto, la cantidad (3 unidades) y el plazo solicitado (10 días). Recupero las tarifas vigentes del catálogo, las escalas de descuento por volumen y las políticas de tiempos y costos de entrega.

**Validaciones**
1. **Precio:** Verifico el precio unitario oficial en la documentación recuperada.
2. **Descuento:** Compruebo si el umbral mínimo para descuento por volumen aplica para 3 unidades según la política comercial.
3. **Plazo:** Valido si el SLA logístico estándar o exprés cubre la entrega en 10 días y si conlleva recargos.
4. **Información faltante:** Si el contexto no especifica el SKU exacto, la dirección de destino o las tarifas de flete, señalo explícitamente la omisión sin inventar valores.

**Resultado esperado**
Si la información está completa, genero un desglose formal: precio unitario, porcentaje de descuento (o aclaración de no aplicabilidad para 3 unidades), gastos de envío, importe total y vigencia de la oferta. Ante datos insuficientes, presento la cotización preliminar listando puntualmente los datos pendientes para completarla.

### Intento 4/12 | Respuestas exitosas: 3/4

- **Estado: EXITOSA (4/4)**
- **Latencia:** 15.70 segundos
- **Costo:** $0.00427275 USD

**Respuesta:**

**Procedimiento:**
Consulto la base vectorial para recuperar la ficha técnica del producto solicitado, tarifas vigentes, tablas de descuento escalonado y políticas de tiempos de despacho.

**Validaciones:**
1. **Identificación del producto:** Verifico si se especificó el SKU/nombre exacto. Si no está definido, lo señalo como dato faltante indispensable.
2. **Precios y descuentos:** Extraigo el precio unitario base. Verifico en la política recuperada si tres unidades alcanzan el umbral para descuento por volumen; si la regla no existe o no aplica, mantengo la tarifa regular sin inventar rebajas.
3. **Plazo de entrega:** Valido si la logística interna respalda el compromiso de diez días.
4. **Completitud:** Identifico si faltan impuestos, costos de envío o datos fiscales del cliente.

**Resultado esperado:**
Presento un desglose formal:
- Precio unitario y subtotal sustentados en las fuentes.
- Aplicación o desestimación justificada del descuento por volumen.
- Confirmación de viabilidad de entrega en 10 días.
- Cálculo del total únicamente si los valores son completos; de lo contrario, especifico claramente la información pendiente para emitir la cotización definitiva.

**Resultado final de Gemini 3.8 Flash:**

- **Intentos realizados:** 4
- **Respuestas exitosas:** 4
- **Respuestas fallidas:** 0

## Modelo: Gemini 3.1 Flash Lite

- **ID:** `gemini-3.1-flash-lite`
- **Respuestas exitosas requeridas: 4**

### Intento 1/12 | Respuestas exitosas: 0/4

- **Estado: EXITOSA (1/4)**
- **Latencia:** 7.11 segundos
- **Costo:** $0.00043425 USD

**Respuesta:**

Como asistente RAG, procesaré la solicitud así:

**Procedimiento**
1. **Recuperación:** Consultaré la base de conocimiento para obtener: precio unitario del producto, política de descuentos por volumen y tiempos de entrega estándar.
2. **Análisis:** Compararé los datos recuperados con la solicitud del usuario (3 unidades, 10 días).
3. **Cálculo:** Determinaré el subtotal y aplicaré el descuento solo si está explícitamente definido en las políticas recuperadas.

**Validaciones**
- Verifico la existencia del producto en catálogo.
- Confirmo si la cantidad (3 unidades) califica para descuento según la tabla de rangos.
- Valido si el plazo de entrega de 10 días cumple con las políticas de logística o requiere gestión especial.

**Resultado esperado**
Presentaré un desglose claro: precio unitario, subtotal, descuento aplicado (o justificación de su ausencia) y total final. Si la base no especifica descuentos por volumen o si los 10 días exceden el tiempo máximo, informaré explícitamente la carencia de datos o la inviabilidad, evitando inventar información no respaldada.

### Intento 2/12 | Respuestas exitosas: 1/4

- **Estado: EXITOSA (2/4)**
- **Latencia:** 11.43 segundos
- **Costo:** $0.00042225 USD

**Respuesta:**

Aquí tienes el procedimiento para procesar la solicitud:

**Procedimiento**
1. **Recuperación:** Consultaré la base de conocimiento mediante búsqueda semántica para extraer: ficha técnica del producto, lista de precios vigente y políticas de descuentos por volumen.
2. **Análisis:** Compararé los tiempos de entrega solicitados (10 días) con los niveles de inventario o tiempos de producción documentados en las políticas logísticas.

**Validaciones**
- **Precios:** Verificaré el costo unitario según el catálogo oficial vinculado al perfil del cliente.
- **Descuentos:** Aplicaré únicamente los rangos de descuentos autorizados para 3 unidades según las reglas de negocio.
- **Logística:** Confirmaré si el plazo de 10 días es factible según las condiciones comerciales recuperadas.

**Resultado esperado**
Presentaré una cotización desglosada (subtotal, descuento aplicado e importe final). Si el catálogo carece de precios, no hay política de descuento aplicable o los tiempos de entrega no están definidos, informaré explícitamente qué datos faltan para completar la gestión con precisión. No se realizarán cálculos basados en supuestos.

### Intento 3/12 | Respuestas exitosas: 2/4

- **Estado: EXITOSA (3/4)**
- **Latencia:** 16.71 segundos
- **Costo:** $0.00042675 USD

**Respuesta:**

Aquí tienes el procedimiento para procesar la solicitud:

**Procedimiento**
1. **Recuperación:** Consultaré la base de conocimiento mediante búsqueda semántica para obtener: precio unitario del producto, política de descuentos por volumen y tiempos de entrega estándar.
2. **Análisis:** Compararé los requisitos del usuario contra los datos recuperados.
3. **Cálculo:** Aplicaré las tarifas y descuentos validados exclusivamente por las fuentes.

**Validaciones**
- **Disponibilidad:** Verificaré si el producto existe y si el plazo de 10 días es factible según las políticas logísticas.
- **Descuentos:** Aplicaré solo las reglas documentadas para compras de 3 unidades. Si la política exige un mínimo mayor, el descuento no se aplicará.
- **Integridad:** Identificaré si faltan datos obligatorios como el ID del cliente, dirección de entrega o impuestos aplicables.

**Resultado esperado**
Presentaré un desglose claro: precio unitario, subtotal, descuento aplicado (o su ausencia) y total. Si falta información, solicitaré explícitamente los datos faltantes antes de finalizar la cotización para asegurar precisión y transparencia.

### Intento 4/12 | Respuestas exitosas: 3/4

- **Estado: EXITOSA (4/4)**
- **Latencia:** 17.16 segundos
- **Costo:** $0.00041475 USD

**Respuesta:**

Aquí presento el procedimiento para gestionar la solicitud:

**Procedimiento**
1. **Consulta RAG:** Interrogaré la base de conocimiento para extraer el precio unitario del producto, las políticas de descuentos por volumen y los plazos de entrega estándar.
2. **Análisis:** Compararé los datos recuperados con los requisitos del cliente (3 unidades, entrega en 10 días).
3. **Cálculo:** Aplicaré los descuentos únicamente si las fuentes confirman que el volumen solicitado califica para una rebaja.

**Validaciones**
- Verifico disponibilidad de stock y coherencia del plazo de entrega según políticas.
- Compruebo si existen restricciones comerciales para el cliente o región.
- Identifico información faltante (ej. datos fiscales del cliente, dirección exacta o vigencia de la oferta).

**Resultado esperado**
Presentaré una cotización estructurada con el desglose de costos. Si los datos son suficientes, incluiré el subtotal, descuento aplicado y total. Si falta información (ej. precio no definido o condiciones no halladas), lo comunicaré explícitamente solicitando la aclaración necesaria antes de proceder.

**Resultado final de Gemini 3.1 Flash Lite:**

- **Intentos realizados:** 4
- **Respuestas exitosas:** 4
- **Respuestas fallidas:** 0

## Tabla comparativa de modelos

| Criterio | Gemini 3.6 Flash | Gemini 3.8 Flash | Gemini 3.1 Flash Lite |
|---|---:|---:|---:|
| Costo por 1.000 tokens de entrada | $0.000750 | $0.000750 | $0.000250 |
| Costo por 1.000 tokens de salida | $0.003750 | $0.003750 | $0.001500 |
| Latencia promedio observada | 9.34 s | 17.09 s | 13.10 s |
| Costo promedio por petición | 0.00488400 USD | 0.00437962 USD | 0.00042450 USD |
| Costo total de pruebas exitosas | 0.01953600 USD | 0.01751850 USD | 0.00169800 USD |
Gemini 3.6 Flash: 4 exitosas, 0 fallidas.
Gemini 3.8 Flash: 4 exitosas, 0 fallidas.
Gemini 3.1 Flash Lite: 4 exitosas, 0 fallidas.

```powershell
PS C:\Bootcamp_Skillnest_IA_generativa\Proyecto_IA> py .\comparar_modelos.py
```

## Modelo: Gemini 3.6 Flash

- **ID:** `gemini-3.6-flash`
- **Respuestas exitosas requeridas: 4**

### Intento 1/12 | Respuestas exitosas: 0/4

- **Estado: EXITOSA (1/4)**
- **Latencia:** 7.89 segundos
- **Costo:** $0.00426900 USD

**Respuesta:**

**Procedimiento**
Consulto la base de conocimiento mediante RAG recuperando la ficha técnica del producto, la tabla de tarifas vigente, la política de descuentos por volumen y las condiciones logísticas de envío.

**Validaciones**
1. **Precio y Descuento:** Verifico el precio unitario base respaldado en el catálogo. Compruebo si el tramo de tres unidades califica para un descuento por volumen según la normativa recuperada.
2. **Logística:** Valido si el plazo de entrega de diez días cumple con los tiempos estándar o si aplica un cargo adicional por envío.
3. **Omisiones:** Si el contexto no especifica el modelo exacto del producto, la ubicación del cliente o la disponibilidad de stock, identifico expresamente estos datos faltantes sin asumir ni inventar valores.

**Resultado esperado**
Si la información recuperada es suficiente, presento una cotización estructurada con el precio base, desglose de descuentos, costo de envío y total calculado. De lo contrario, entrego un reporte con los datos verificados e indico explícitamente la información requerida para completar el proceso.

### Intento 2/12 | Respuestas exitosas: 1/4

- **Estado: EXITOSA (2/4)**
- **Latencia:** 7.54 segundos
- **Costo:** $0.00443400 USD

**Respuesta:**

**Procedimiento**
Consulto el sistema RAG vectorizando los parámetros de la solicitud (producto, 3 unidades, entrega en 10 días y políticas de descuento). Recupero delcontexto el precio unitario del catálogo, las escalas de descuentos por volumen y las condiciones logísticas aplicables.

**Validaciones**
- **Precios y Descuentos:** Verifico el precio base y compruebo en el contexto si 3 unidades aplican para algún tramo de descuento.
- **Plazos:** Valido si el tiempo de entrega de 10 días cumple con las políticas logísticas recuperadas.
- **Datos faltantes:** Identifico vacíos de información (ej. modelo exacto, impuestos o costos de envío) sin inventar ninguna cifra o condición no respaldada.

**Resultado esperado**
- **Con información completa:** Presento una cotización clara con el desglose del precio unitario, descuento aplicado, costo total y confirmación de la entrega.
- **Con información faltante:** Emito un resumen preliminar indicando explícitamente los datos requeridos para finalizar el cálculo (ej. *"Falta confirmar dirección de destino para calcular el envío"*).

### Intento 3/12 | Respuestas exitosas: 2/4

- **Estado: EXITOSA (3/4)**
- **Latencia:** 8.06 segundos
- **Costo:** $0.00452400 USD

**Respuesta:**

**Procedimiento**
Consulto la base de conocimiento mediante RAG para extraer el precio base del producto, la tabla de tarifas, la política de descuentos por volumen (evaluando el umbral de 3 unidades) y las condiciones logísticas para entregas en 10 días.

**Validaciones**
1. **Precio y Descuento:** Verifico el precio unitario oficial y compruebo si la política recuperada otorga descuento por 3 unidades. Si aplica, ejecuto el cálculo estricto.
2. **Viabilidad de Entrega:** Valido si el plazo de 10 días cumple con los tiempos de preparación y envío registrados.
3. **Faltantes:** Identifico si falta información (SKU exacto, dirección de destino o impuestos). Si no está en el contexto, lo indico explícitamente sin asumir ni inventar valores.

**Resultado esperado**
Si la información recuperada es suficiente, presento un desglose claro: precio unitario, descuento aplicado, costo/condiciones de envío y total final. Si faltan datos, entrego una respuesta parcial señalando con precisión los insumos requeridos para completar la cotización.

### Intento 4/12 | Respuestas exitosas: 3/4

- **Estado: FALLIDA**
- **Motivo:** HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.

### Intento 5/12 | Respuestas exitosas: 3/4

- **Estado: EXITOSA (4/4)**
- **Latencia:** 8.63 segundos
- **Costo:** $0.00586650 USD

**Respuesta:**

**Procedimiento**
Consulto la base de conocimiento mediante RAG para extraer el precio de lista del producto, la tabla de descuentos por volumen (evaluando el tramo de3 unidades) y las condiciones o tarifas de envío aplicables a un plazo de 10 días.

**Validaciones**
1. Verifico la existencia y precio base del producto en el catálogo recuperado.
2. Valido si 3 unidades alcanzan el umbral para un descuento por volumen según la política comercial documentada.
3. Confirmo la viabilidad logística y costo de entrega en 10 días.
4. Detecto vacíos de información (ej. SKU exacto, ubicación de entrega). Jamás invento precios, porcentajes ni condiciones no respaldados explícitamente por el contexto.

**Resultado esperado**
Si los datos están completos, genero una cotización clara con desglose de precio unitario, descuento aplicado, gastos de envío y total. Si la información en la base de conocimiento es insuficiente, indico explícitamente los datos faltantes requeridos para procesar la solicitud.

**Resultado final de Gemini 3.6 Flash:**

- **Intentos realizados:** 5
- **Respuestas exitosas:** 4
- **Respuestas fallidas:** 1

## Modelo: Gemini 3.8 Flash

- **ID:** `gemini-3.8-flash`
- **Respuestas exitosas requeridas: 4**

### Intento 1/12 | Respuestas exitosas: 0/4

- **Estado: EXITOSA (1/4)**
- **Latencia:** 48.53 segundos
- **Costo:** $0.00461025 USD

**Respuesta:**

**Procedimiento:**
Recupero de la base de conocimiento el precio unitario del producto, las tablas de descuento por volumen y las condiciones de logística. Con los datos validados, calculo el importe: (precio base × 3) menos el descuento correspondiente, agregando impuestos o flete si el contexto lo estipula.

**Validaciones:**
Constato si tres unidades alcanzan el umbral mínimo para descuento por volumen y si la entrega en diez días es viable según los acuerdos de nivel de servicio (SLA). Identifico datos faltantes clave (código/nombre exacto del producto, ubicación de entrega o impuestos). No genero precios ni términos ausentes en los documentos recuperados.

**Resultado esperado:**
Si el contexto es suficiente, presento un desglose claro: precio unitario, porcentaje de descuento aplicado, validación del plazo de diez días y monto total. Ante información faltante, especifico los datos requeridos (ej. producto no especificado o política de flete no encontrada) antes de emitir la cotización formal.

### Intento 2/12 | Respuestas exitosas: 1/4

- **Estado: FALLIDA**
- **Motivo:** HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.

### Intento 3/12 | Respuestas exitosas: 1/4

- **Estado: FALLIDA**
- **Motivo:** HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.

### Intento 4/12 | Respuestas exitosas: 1/4

- **Estado: FALLIDA**
- **Motivo:** HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.

### Intento 5/12 | Respuestas exitosas: 1/4

- **Estado: FALLIDA**
- **Motivo:** HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.

### Intento 6/12 | Respuestas exitosas: 1/4

- **Estado: EXITOSA (2/4)**
- **Latencia:** 18.99 segundos
- **Costo:** $0.00405150 USD

**Respuesta:**

**Procedimiento**
Ejecuto una búsqueda semántica en la base de conocimiento para recuperar: catálogo del producto, tarifas vigentes, escalas de descuento por volumen yplazos de entrega logística.

**Validaciones**
1. **Precios y producto:** Verifico el SKU exacto y su precio unitario en las tarifas recuperadas.
2. **Descuento por volumen:** Valido en la política comercial si tres unidades califican para descuento; de no existir regla que lo respalde, no lo aplico.
3. **Plazos:** Corroboro si el estándar de entrega cubre los diez días solicitados.
4. **Información faltante:** Si el contexto omite el nombre exacto del producto, costos de envío o stock, lo notifico explícitamente sin inventar cifras.

**Resultado esperado**
Si la información es suficiente, genero el desglose: precio unitario, subtotal (3 unidades), descuento aplicado (según política), costo total y confirmación de entrega en 10 días. Si faltan datos, emito un reporte indicando puntualmente qué variables comerciales deben definirse para emitir la cotización.

### Intento 7/12 | Respuestas exitosas: 2/4

- **Estado: EXITOSA (3/4)**
- **Latencia:** 46.73 segundos
- **Costo:** $0.00498150 USD

**Respuesta:**

**Procedimiento:**
Consulto la base vectorial con el producto solicitado para recuperar: precio de lista vigente, matriz de descuentos por escala y condiciones de entrega logística.

**Validaciones:**
1. **Precio:** Verifico el valor unitario oficial en el catálogo recuperado.
2. **Descuento:** Valido si el umbral de volumen aplica para 3 unidades según la política comercial.
3. **Plazo:** Confirmo si la política de envíos permite el despacho en 10 días hábiles/naturales.
4. **Completitud:** Si el contexto omite el SKU exacto, stock, costos de envío o condiciones de pago, lo declaro explícitamente sin inventar datos.

**Resultado esperado:**
- **Si los datos son suficientes:** Presento un desglose formal con precio unitario, porcentaje de descuento aplicado (o la aclaración de que 3 unidades no alcanzan el beneficio), subtotal, impuestos, total final y confirmación de la fecha de entrega.
- **Si falta información:** Emito un reporte estructurado señalando exactamente los datos ausentes (ej. producto no especificado, cobertura de envío)necesarios para emitir la cotización definitiva.

### Intento 8/12 | Respuestas exitosas: 3/4

- **Estado: EXITOSA (4/4)**
- **Latencia:** 25.65 segundos
- **Costo:** $0.00464775 USD

**Respuesta:**

**Procedimiento**
Consulto la base vectorial mediante el producto solicitado, volumen (3 unidades) y plazo (10 días). Recupero las fichas de catálogo, listas de tarifas vigentes, matrices de descuentos escalonados y condiciones logísticas.

**Validaciones**
1. **Precio y descuento:** Verifico el precio unitario base. Valido en la política comercial si 3 unidades califican para descuento por volumen; si no alcanza el umbral o no existe registro, aplico tarifa estándar.
2. **Logística:** Confirmo si el plazo de 10 días cumple los tiempos estándar recuperados.
3. **Información faltante:** Si el contexto carece del SKU exacto, costos de envío o vigencia de precios, no asumo valores y lo señalo explícitamente.

**Resultado esperado**
Emito una propuesta estructurada con:
* Desglose: precio unitario, porcentaje de descuento sustentado (o indicación de "no aplica"), subtotales e impuestos.
* Factibilidad del plazo de 10 días.
* Alertas claras indicando variables no encontradas en la base de conocimiento para que el administrador las precise antes del envío final.

**Resultado final de Gemini 3.8 Flash:**

- **Intentos realizados:** 8
- **Respuestas exitosas:** 4
- **Respuestas fallidas:** 4

## Modelo: Gemini 3.1 Flash Lite

- **ID:** `gemini-3.1-flash-lite`
- **Respuestas exitosas requeridas: 4**

### Intento 1/12 | Respuestas exitosas: 0/4

- **Estado: EXITOSA (1/4)**
- **Latencia:** 4.88 segundos
- **Costo:** $0.00043275 USD

**Respuesta:**

Aquí tienes el procedimiento para procesar la solicitud:

**Procedimiento**
1. **Recuperación:** Consultaré la base de conocimiento mediante búsqueda semántica para extraer: ficha técnica del producto, precio unitario vigente, políticas de descuento por volumen y plazos de entrega estándar.
2. **Análisis:** Compararé los requisitos (3 unidades, 10 días) contra los datos recuperados para determinar la viabilidad operativa y comercial.
3. **Cálculo:** Aplicaré los descuentos solo si el catálogo lo estipula explícitamente para dicho volumen.

**Validaciones**
* Verificaré si el plazo de 10 días es factible según las condiciones logísticas recuperadas.
* Confirmaré si existe una escala de descuento aplicable para 3 unidades.
* Validaré la disponibilidad de stock o tiempos de despacho.

**Resultado esperado**
Presentaré una cotización con el desglose de precios. Si el catálogo no menciona descuentos para 3 unidades, aplicaré el precio estándar. Si la información sobre stock o plazos específicos es insuficiente, indicaré claramente: *"No se ha podido confirmar la viabilidad del plazo de 10 días; requierevalidación con logística"*.

### Intento 2/12 | Respuestas exitosas: 1/4

- **Estado: FALLIDA**
- **Motivo:** HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.

### Intento 3/12 | Respuestas exitosas: 1/4

- **Estado: EXITOSA (2/4)**
- **Latencia:** 5.29 segundos
- **Costo:** $0.00041925 USD

**Respuesta:**

Aquí tienes el procedimiento para procesar la solicitud:

**Procedimiento**
1. **Recuperación:** Consultaré la base de conocimiento mediante búsqueda semántica para obtener: precio unitario del producto, política de descuentos por volumen y tiempos de entrega estándar.
2. **Análisis:** Compararé la cantidad solicitada (3 unidades) con las tablas de escalonamiento de precios y validaré si el plazo de 10 días es factible según las políticas logísticas.

**Validaciones**
* **Existencia:** Verificaré si el producto está en catálogo y tiene stock disponible.
* **Condiciones:** Confirmaré si el umbral de descuento se activa con tres unidades. Si los datos son insuficientes (ej. no se especifica el ID del cliente o la zona de entrega), solicitaré la información faltante.
* **Precisión:** Utilizaré exclusivamente los datos recuperados para el cálculo, evitando estimaciones.

**Resultado esperado**
Entregaré un borrador de cotización con desglose de precios unitarios, aplicación de descuentos validados, impuestos y plazos de entrega. Si falta información, detallaré qué dato específico impide completar el cálculo.

### Intento 4/12 | Respuestas exitosas: 2/4

- **Estado: EXITOSA (3/4)**
- **Latencia:** 4.86 segundos
- **Costo:** $0.00043125 USD

**Respuesta:**

Aquí presento el flujo de trabajo para procesar la solicitud:

**Procedimiento**
1. **Recuperación:** Consultaré la base de conocimiento mediante búsqueda semántica para obtener el precio unitario del producto, las políticas de descuentos por volumen y los plazos de entrega estándar.
2. **Cálculo:** Aplicaré las fórmulas de precios y descuentos según las fuentes recuperadas.
3. **Respuesta:** Integraré la información validada, destacando cualquier brecha técnica.

**Validaciones**
* **Existencia:** Verificaré si el producto y el plazo de entrega (10 días) están dentro de los parámetros permitidos.
* **Descuento:** Aplicaré únicamente las escalas de descuento explícitas en el catálogo; si el volumen (3 unidades) no alcanza el umbral mínimo para un descuento, informaré que no aplica.
* **Integridad:** Identificaré datos faltantes como identificación del cliente o dirección de envío.

**Resultado esperado**
Presentaré una tabla con el desglose: producto, cantidad, precio unitario, descuento aplicado (o su ausencia) y subtotal. Indicaré explícitamente cualquier dato faltante requerido para cerrar la cotización formal.

### Intento 5/12 | Respuestas exitosas: 3/4

- **Estado: EXITOSA (4/4)**
- **Latencia:** 4.87 segundos
- **Costo:** $0.00040275 USD

**Respuesta:**

Aquí presento el flujo de procesamiento para tu solicitud:

**Procedimiento**
1. **Recuperación:** Consultaré la base de conocimiento para extraer el precio unitario del producto, las políticas de descuento por volumen y los plazos de entrega estándar.
2. **Cálculo:** Multiplicaré el precio base por las tres unidades y aplicaré el descuento verificado si corresponde a la cantidad solicitada.
3. **Análisis:** Compararé el plazo de entrega solicitado (10 días) con la disponibilidad y políticas de logística recuperadas.

**Validaciones**
* Verificaré si el producto existe en el catálogo.
* Comprobaré si el descuento por volumen está habilitado para tres unidades (según umbrales definidos).
* Validaré si el tiempo de entrega es viable bajo las condiciones comerciales actuales.

**Resultado esperado**
Presentaré una propuesta formal con desglose de precios, aplicación de descuentos validados y confirmación de entrega. Si falta el ID del producto, el nombre del cliente o la vigencia de la oferta, lo señalaré explícitamente antes de generar cualquier cálculo.

**Resultado final de Gemini 3.1 Flash Lite:**

- **Intentos realizados:** 5
- **Respuestas exitosas:** 4
- **Respuestas fallidas:** 1

## Tabla comparativa de modelos

| Criterio | Gemini 3.6 Flash | Gemini 3.8 Flash | Gemini 3.1 Flash Lite |
|---|---:|---:|---:|
| Costo por 1.000 tokens de entrada | $0.000750 | $0.000750 | $0.000250 |
| Costo por 1.000 tokens de salida | $0.003750 | $0.003750 | $0.001500 |
| Latencia promedio observada | 8.03 s | 34.98 s | 4.97 s |
| Costo promedio por petición | 0.00477337 USD | 0.00457275 USD | 0.00042150 USD |
| Costo total de pruebas exitosas | 0.01909350 USD | 0.01829100 USD | 0.00168600 USD |
Gemini 3.6 Flash: 4 exitosas, 1 fallidas.
Gemini 3.8 Flash: 4 exitosas, 4 fallidas.
Gemini 3.1 Flash Lite: 4 exitosas, 1 fallidas.
