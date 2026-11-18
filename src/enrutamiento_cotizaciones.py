from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda

import logging

# Configuración de logging para registrar fallos o excepciones de la cadena
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="error_cotizaciones.log",
    filemode="a",
    encoding="utf-8",
    force=True
)
logger = logging.getLogger(__name__)

load_dotenv()

# Instanciación del modelo recomendado
modelo = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

# 1. Prompt de Clasificación adaptado al dominio comercial
plantilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de un portal administrativo de cotizaciones en una sola palabra: "
    "cotizacion, consulta_stock o reclamo. Responde solo con esa palabra.\n\n{mensaje}"
)

paso_clasificacion = (
    plantilla_clasificacion
    | modelo
    | StrOutputParser()
    | (lambda texto: texto.strip().lower())
)

# 2. Cadenas especializadas para cada ruta del negocio
# Ruta A: Generación de cotización (Basado en Prompt 1 de tu banco)
cadena_cotizacion = (
    PromptTemplate.from_template(
        "Actúa como asistente inteligente de un portal de cotizaciones. "
        "Redacta una respuesta comercial estructurada para la siguiente solicitud, indicando producto, cantidad y observaciones si hay datos:\n\n{mensaje}"
    )
    | modelo
    | StrOutputParser()
)

# Ruta B: Consulta de stock o condiciones comerciales (Basado en Prompt 5)
cadena_stock = (
    PromptTemplate.from_template(
        "Actúa como asistente de consulta de un portal administrativo. "
        "Responde a esta consulta sobre precios, existencias o condiciones comerciales con precisión:\n\n{mensaje}"
    )
    | modelo
    | StrOutputParser()
)

# Ruta C (Default / Reclamos o solicitudes ambiguas)
cadena_reclamo = (
    PromptTemplate.from_template(
        "Responde a esta solicitud o incidencia comercial con empatía, reconociendo el problema y canalizándolo con un administrador humano:\n\n{mensaje}"
    )
    | modelo
    | StrOutputParser()
)

# 3. Bifurcación condicional con RunnableBranch
bifurcacion = RunnableBranch(
    (lambda x: x["clasificacion"] == "cotizacion", cadena_cotizacion),
    (lambda x: x["clasificacion"] == "consulta_stock", cadena_stock),
    cadena_reclamo  # Ruta por defecto
)

# Integración del passthrough para conservar el mensaje original junto a la clasificación
cadena_con_enrutamiento = (
    RunnablePassthrough.assign(clasificacion=paso_clasificacion)
    | bifurcacion
)

# 4. Mecanismo de Fallback (Respaldo ante caídas de API o Rate Limits)
def fallback_con_log(x):
    logger.warning("La cadena principal de cotizaciones falló. Activando respuesta genérica de respaldo.")
    return "En este momento no podemos procesar tu solicitud comercial. Un ejecutivo de cuentas revisará tu caso a la brevedad."

respuesta_generica = RunnableLambda(fallback_con_log)
cadena_robusta = cadena_con_enrutamiento.with_fallbacks([respuesta_generica])

def procesar_mensaje_comercial(cadena, mensaje):
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error("Error crítico procesando mensaje comercial: %s", error)
        return "Ocurrió un error inesperado al gestionar tu cotización. Por favor, intenta más tarde."


if __name__ == "__main__":
    # Pruebas simuladas para cada ruta del sistema de cotizaciones
    print("=== PRUEBA 1: Solicitud de Cotización ===")
    print(procesar_mensaje_comercial(cadena_robusta, "Hola, necesito cotizar 3 unidades del Servidor Rack Enterprise."))
    
    print("\n=== PRUEBA 2: Consulta de Stock ===")
    print(procesar_mensaje_comercial(cadena_robusta, "¿Cuál es el precio vigente y la disponibilidad de stock para los discos duros SSD?"))
    
    print("\n=== PRUEBA 3: Reclamo / Incidencia ===")
    print(procesar_mensaje_comercial(cadena_robusta, "El precio que figura en el sistema no coincide con la cotización que me enviaron ayer."))


"""    # Reporte de Integración: Enrutamiento Condicional y Banco de Prompts

## 1. Resumen de lo Realizado
En las últimas sesiones de [U2.3 LangChain y orquestación de flujos](https://learning-pro.skillnest.com/course/section.php?id=807), completamos el paso desde flujos lineales hacia un sistema orquestado y robusto mediante:
* **Clasificación automatizada:** Un paso inicial que categoriza la entrada del usuario en una sola palabra clave (normalizada mediante `.strip().lower()`).
* **Bifurcación dinámica (`RunnableBranch`):** Permite derivar la ejecución hacia cadenas especializadas según el resultado de la clasificación.
* **Conservación de contexto (`RunnablePassthrough.assign`):** Asegura que el mensaje original del usuario no se pierda al momento de evaluar las condiciones, fusionándolo con la categoría detectada en un diccionario compartido.
* **Resiliencia y Logging (`with_fallbacks`):** Incorporación de un mecanismo de respaldo y registro de errores ante caídas de la API del modelo.

Para este flujo comercial, adaptaremos las categorías del enrutador a tres escenarios reales de gestión:
1.cotizacion: Solicitudes de compra o emisión de nuevas cotizaciones (utilizando la lógica del Prompt 1 de tu banco de prompts).
2.consulta_stock: Dudas sobre disponibilidad, precios vigentes o catálogos (alineado al Prompt 5).
3.reclamo (o ruta por defecto): Inconvenientes, errores o desacuerdos comerciales que requieren atención y empatía.
---

## 2. Conexión con tu Banco de Prompts

La arquitectura desarrollada no opera con plantillas genéricas, sino que traduce de manera directa las mejores prácticas de tu **banco de prompts comercial**:

* **Prompt 1 (Generación de cotización) e Inspiración:** 
  Sirvió de base directa para estructurar la `cadena_cotizacion`. Este prompt instruye al modelo a comportarse como un asistente inteligente de un portal administrativo, asegurando que extraiga productos, cantidades y entregue una respuesta comercial estructurada basándose estrictamente en los requerimientos.
  
* **Prompt 5 (Consulta de condiciones comerciales) e Inspiración:** 
  Guió el diseño de la `cadena_stock`, orientando al modelo para responder de forma precisa sobre catálogos, precios vigentes o existencias sin asumir información no verificada.

### El rol de `RunnablePassthrough.assign` y `RunnableBranch`
Gracias a estas piezas de [LangChain](https://learning-pro.skillnest.com/mod/page/view.php?id=15655), el sistema garantiza que un mensaje comercial (ya sea específico o ambiguo) sea:
1. Recibido e interpretado por el clasificador.
2. Enriquecido con el contexto completo mediante `RunnablePassthrough.assign` (conservando tanto el mensaje como la categoría).
3. Derivado de forma limpia y automática al prompt especializado correspondiente (`cotizacion`, `consulta_stock` o la ruta por defecto) sin alterar ni perder los datos originales del usuario. """