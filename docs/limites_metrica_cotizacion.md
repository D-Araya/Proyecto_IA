# Límites de la métrica de evaluación

## Qué mide
Mide la similitud léxica mediante el conteo estricto de tokens superpuestos (precisión, cobertura y F1) entre la respuesta generada por el asistente del portal de cotizaciones y la oración de referencia comercial esperada.

## Modos de falla conocidos
- **Penalización severa por respuestas extensas y estructuradas en listas:** El modelo tiende a generar respuestas muy completas y profesionales para un entorno de producción (por ejemplo, detallando pasos para *precios contradictorios* o *estructuras de backend*). Aunque la información es correcta, el uso de viñetas, enumeraciones y vocabulario extenso no contemplado en una referencia corta reduce artificialmente el puntaje de F1 a rangos bajos (~0.06).
- **Desajuste por divergencia léxica conceptual:** En preguntas complejas (como *"¿Qué indica una vigencia distinta en los documentos?"* o *"¿Qué apartados debe contener una cotización estándar?"*), el modelo describe correctamente los conceptos técnicos y de negocio, pero al utilizar sinónimos y terminología propia del dominio, la superposición de tokens con la referencia es mínima.
- **Falsos negativos en respuestas de alcance comercial:** Consultas sobre políticas de descuento o cálculos operativos (como *"¿Cómo se aplica el descuento por volumen para ocho unidades?"*) obtienen puntajes de F1 moderados (ej. ~0.23 a 0.28) debido a que el modelo expande la explicación de la fórmula, a pesar de ser fácticamente correctas.

## Muestra revisada
Se evaluó una muestra de **10 casos** seleccionados a partir del total de respuestas generadas con el banco de prompts del proyecto, combinando de forma equilibrada los 5 casos con menor F1 (como la gestión de precios contradictorios con un $F1 = 0.06$) y los 5 casos con mayor F1 de la muestra (como el cálculo de importes con un $F1 = 0.29$) para evitar sesgos de revisión exclusiva en los errores.

## Recomendación de uso
- **Cuándo confiar en el número solo:** En consultas de extracción directa de catálogos y datos muy acotados donde el vocabulario del modelo y la referencia coinciden de forma estricta y superan un $F1$ de 0.80.
- **Cuándo revisar a mano:** Obligatorio cuando el pipeline arroja un $F1$ bajo o moderado (<0.30), dado que este comportamiento suele ser un falso negativo provocado por la riqueza explicativa del modelo y no por un fallo factual o de completitud real en el portal de cotizaciones.