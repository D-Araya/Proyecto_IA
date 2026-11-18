from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda
from langchain_core.callbacks import BaseCallbackHandler
import logging

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="error_cotizaciones_core.log",
    filemode="a",
    encoding="utf-8",
    force=True
)
logger = logging.getLogger(__name__)

load_dotenv()

def construir_paso_clasificacion(modelo):
    """Paso 1: Clasificación de la solicitud comercial."""
    plantilla = PromptTemplate.from_template(
        "Clasifica el siguiente mensaje de un portal administrativo de cotizaciones en una sola palabra: "
        "cotizacion, consulta_stock o reclamo. Responde solo con esa palabra.\n\n{mensaje}"
    )
    return plantilla | modelo | StrOutputParser() | (lambda texto: texto.strip().lower())

def construir_cadena_comercial_robusta(modelo, paso_clasificacion_custom=None, cadena_reclamo_custom=None):
    """
    Construye la cadena completa de cotizaciones aplicando inyección de dependencias 
    y manejadores de fallos granulares por paso (Bloque 20).
    """
    paso_clasificacion = paso_clasificacion_custom or construir_paso_clasificacion(modelo)

    cadena_cotizacion = (
        PromptTemplate.from_template("Redacta una propuesta comercial estructurada para la siguiente solicitud:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    cadena_stock = (
        PromptTemplate.from_template("Responde a esta consulta sobre stock, precios o disponibilidad:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    # Cadena base de reclamos
    cadena_reclamo_base = (
        PromptTemplate.from_template("Responde a esta incidencia comercial con empatía y canalízala con soporte:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    # Aplicamos fallback granular específico para la ruta de reclamos (Bloque 20)
    fallback_reclamo_fn = RunnableLambda(lambda x: "Estimado cliente, su reclamo ha sido recibido y derivado a un supervisor comercial.")
    cadena_reclamo = cadena_reclamo_custom or cadena_reclamo_base.with_fallbacks([fallback_reclamo_fn])

    bifurcacion = RunnableBranch(
        (lambda x: x["clasificacion"] == "cotizacion", cadena_cotizacion),
        (lambda x: x["clasificacion"] == "consulta_stock", cadena_stock),
        cadena_reclamo  # Ruta por defecto
    )

    cadena_con_enrutamiento = (
        RunnablePassthrough.assign(clasificacion=paso_clasificacion)
        | bifurcacion
    )

    # Fallback global de respaldo para toda la cadena
    fallback_global_fn = RunnableLambda(lambda x: "Gracias por comunicarse. Un ejecutivo comercial le responderá a la brevedad.")
    return cadena_con_enrutamiento.with_fallbacks([fallback_global_fn])


class CapturadorErrorComercial(BaseCallbackHandler):
    def on_chain_error(self, error: BaseException, **kwargs):
        logger.warning("Error capturado en la cadena comercial: [%s] -> %s", type(error).__name__, error)

manejador_error = CapturadorErrorComercial()

def procesar_mensaje_comercial_seguro(cadena, mensaje):
    """Manejo global try/except exigido por la actividad core."""
    try:
        return cadena.invoke({"mensaje": mensaje}, config={"callbacks": [manejador_error]})
    except Exception as error:
        logger.error("Error crítico procesando mensaje comercial: %s", error)
        return "No pudimos procesar su solicitud en este momento. Intente más tarde."


if __name__ == "__main__":
    modelo_real = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
    cadena_final = construir_cadena_comercial_robusta(modelo_real)
    
    mensaje_prueba = "Necesito cotizar urgentemente 3 unidades del Servidor Rack."
    print("=== Resultado de Ejecución Principal ===")
    print(procesar_mensaje_comercial_seguro(cadena_final, mensaje_prueba))


"""
En este código se incorpora:

1.Las tres rutas comerciales (cotizacion, consulta_stock y reclamo por defecto).
2.Manejo de errores granular y por paso mediante with_fallbacks.
3.Inyección de dependencias para poder someterlo a pruebas con pytest sin consumir 
tokens ni realizar llamadas reales.
"""