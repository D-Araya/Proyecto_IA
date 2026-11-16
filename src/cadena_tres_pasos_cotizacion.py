import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def construir_cadena(modelo):
    """
    Construye y retorna una chain de tres pasos encadenados usando LangChain.
    Paso 1: Extracción de requerimientos y datos de la cotización.
    Paso 2: Análisis comercial y redacción de viabilidad.
    Paso 3: Formato profesional en Markdown.
    """
    # 1. Primer PromptTemplate: Extracción
    plantilla_extraccion = PromptTemplate.from_template(
        "Analiza la siguiente solicitud comercial de cotización y extrae los productos, cantidades, plazos y condiciones:\n\n{solicitud}"
    )
    paso_extraccion = plantilla_extraccion | modelo | StrOutputParser()

    # 2. Segundo PromptTemplate: Análisis de viabilidad
    plantilla_analisis = PromptTemplate.from_template(
        "A partir de los siguientes datos extraídos, redacta un resumen ejecutivo de viabilidad comercial y condiciones:\n\n{datos_extraidos}"
    )
    paso_analisis = plantilla_analisis | modelo | StrOutputParser()

    # 3. Tercer PromptTemplate: Formato final en Markdown
    plantilla_formato = PromptTemplate.from_template(
        "Convierte el siguiente análisis en una propuesta formal estructurada con un título en Markdown, tabla o viñetas ejecutivas:\n\n{analisis}"
    )
    paso_formato = plantilla_formato | modelo | StrOutputParser()

    # Encadenamiento completo con el operador '|' y funciones lambda para mapeo de diccionarios
    cadena_completa = (
        paso_extraccion 
        | (lambda datos: {"datos_extraidos": datos}) 
        | paso_analisis 
        | (lambda analisis: {"analisis": analisis}) 
        | paso_formato
    )

    return cadena_completa

def guardar_resultado_markdown(contenido_markdown, prefijo="cotizacion_reporte"):
    """
    Genera automáticamente un archivo .md nuevo con marca de tiempo única 
    para evitar sobrescribir archivos anteriores.
    """
    os.makedirs("output_cotizaciones", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = os.path.join("output_cotizaciones", f"{prefijo}_{timestamp}.md")
    
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(contenido_markdown)
        
    print(f"[✓] Reporte Markdown generado exitosamente: {nombre_archivo}")
    return nombre_archivo

if __name__ == "__main__":
    load_dotenv()
    
    # Instanciación del modelo real con Gemini
    modelo_real = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
    
    cadena = construir_cadena(modelo_real)
    
    solicitud_prueba = (
        "Hola, necesitamos cotizar urgentemente 5 unidades de Servidores Rack Enterprise "
        "para entrega en Llanquihue antes del próximo viernes, con condición de pago a 30 días."
    )
    
    print("Ejecutando chain de tres pasos...")
    resultado_final = cadena.invoke({"solicitud": solicitud_prueba})
    
    # Guardar automáticamente en un nuevo archivo .md
    guardar_resultado_markdown(resultado_final)