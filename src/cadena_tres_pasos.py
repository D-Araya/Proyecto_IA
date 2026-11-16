
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI #llamar al modelo
from langchain_core.prompts import PromptTemplate #llamar a la plantilla, prompt dinamico
from langchain_core.output_parsers import StrOutputParser   #llamar al parser para parsear la respuesta y la transforma en solo texto
from langchain_core.prompts import ChatPromptTemplate  # Plantilla que incluye rol del sistema e instrucción

load_dotenv()

modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

plantilla_extraccion = PromptTemplate.from_template("Lee el siguiente texto y devuelve solo sus 3 puntos clave, uno por línea, sin desarrollarlos:\n\n{texto}")

#paso_extraccion = plantilla_extraccion | modelo | StrOutputParser()

texto_prueba = (
    "Los modelos de lenguaje grandes generan texto "
    "prediciendo un token a la vez, basándose en el " 
    "texto que ya generaron antes. Cada token puede "
    "ser una palabra completa, parte de una palabra, "
    "o un signo de puntuación. Antes de que el modelo "
    "genere una respuesta, el texto de entrada se "
    "divide en tokens, un proceso llamado tokenización."
)

""" puntos = paso_extraccion.invoke(
    {"texto": texto_prueba}
)

print(puntos) """

plantilla_simplificacion = PromptTemplate.from_template("Reescribe estos puntos en lenguaje simple, sin jerga técnica para alguien sin conocimientos previos:\n\n{puntos}")
"""
paso_simplificacion = plantilla_simplificacion | modelo | StrOutputParser()

 simple = paso_simplificacion.invoke(
    {"puntos": puntos}
)

print(simple) """

plantilla_formateo = PromptTemplate.from_template(
    "Convierte este texto en una lista de viñetas markdown de máximo 3 líneas, sin introducción:\n\n{texto_simple}"
)
""" 
paso_formateo = plantilla_formateo | modelo | StrOutputParser()

formato = paso_formateo.invoke(
    {"texto_simple": simple}
)

print(formato) """


"""
1.Generar una plantilla para cada uno de los pasos del proceso. 
2.Realizar la petición correspondiente a cada paso. 
3.Pasar la respuesta de un paso a otro, para complementar y obtener una nueva respuesta basada en la anterior. 
4.Obtener un producto completo y terminado como resultado final. 
Además, mencionó que comenzaría realizando las importaciones, igual a las utilizadas anteriormente. 
"""
"""
 el proceso está dividido en 3 pasos: 12

1.Extracción — Extraer la información del texto mediante una plantilla, pasarla al modelo y parsear el resultado como texto. 13
2.Reescritura — Tomar la respuesta del paso anterior y reescribirla, complementando la información obtenida. 24
2.Formateo — Formatear el resultado final, por ejemplo, como una lista de viñetas, para obtener un producto completo y terminado. 45
"""


# Sintaxis lambda -> lambda argumentos: expresion
cadena_tres_pasos = (
    plantilla_extraccion
    | modelo
    | StrOutputParser()
    | (lambda puntos: {"puntos": puntos})
    | plantilla_simplificacion
    | modelo
    | StrOutputParser()
    | (lambda simple: {"texto_simple": simple})
    | plantilla_formateo
    | modelo
    | StrOutputParser()
)

respuesta = cadena_tres_pasos.invoke(
    {"texto": texto_prueba}
) #Aquí se pasa el primer textos

print(respuesta)