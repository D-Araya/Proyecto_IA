from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI #llamar al modelo
from langchain_core.prompts import PromptTemplate #llamar a la plantilla, prompt dinamico
from langchain_core.output_parsers import StrOutputParser   #llamar al parser para parsear la respuesta y la transforma en solo texto
from langchain_core.prompts import ChatPromptTemplate  # Plantilla que incluye rol del sistema e instrucción

load_dotenv()

#api_key = os.getenv("API_KEY_AI")
#modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash", api_key=api_key)
modelo = ChatGoogleGenerativeAI(model = "gemini-3.1-flash-lite")
#respuesta = modelo.invoke("¿Qué es un token?")
#print(respuesta.content)

#f-strings
plantilla = PromptTemplate.from_template(
    "Explica el concepto de {tema} en un párrafo, para alguien que recien comienza en {area}."
)

#prompt = plantilla.invoke(
#    {"tema": "tokenización", "area": "procesamiento de texto"}
#)
#print(prompt.text)

cadena_simple = plantilla | modelo | StrOutputParser()
respuesta = cadena_simple.invoke(
    {"tema": "embeddings", "area": "búsqueda semántica"}
)

print(respuesta)

plantilla_conrol = ChatPromptTemplate.from_messages([
    ("system", "Eres un experto en el área correspondiente, vas a responder siempre con texto simple para el usuario."),
    ("human",  "Explica el concepto de {tema} en un párrafo, para alguien que recién comienza en {area}.")
])

"""
A continuación, los pasos realizados durante la clase:

Planificación del proceso en 3 pasos 12

Generar una plantilla para cada paso.
Realizar la petición correspondiente.
Pasar la respuesta de un paso a otro para obtener un producto final completo.
Importaciones 2

Se copiaron las mismas importaciones utilizadas en clases anteriores.
Configuración del modelo 3

Se usó ChatGoogleGenerativeAI con el modelo versión 3.6.
Se mencionó la opción de usar modelos más baratos/antiguos (como 3.5) para ahorrar tokens. 45
Creación de plantillas de extracción 67

Se explicaron dos enfoques: PromptTemplate normal y ChatPromptTemplate (que incluye el rol del sistema).
Se mostró ambas opciones para que los estudiantes puedan probarlas.
Primera plantilla: extracción de puntos clave 8

La plantilla indica: leer un texto y devolver sus 3 puntos clave, uno por línea, sin desarrollarlos.
Sugerencias adicionales 910

Encapsular scripts en funciones externas para reutilizarlos sin copiar y pegar entre proyectos.
"""


"""
A continuación, una explicación más detallada de los pasos realizados durante la clase:

1. Planificación del proceso en 3 pasos

Cynthia explicó que el objetivo es dividir el flujo en 3 etapas distintas. 1
Generar una plantilla para cada paso. 1
Realizar la petición correspondiente a cada plantilla. 1
Pasar la respuesta de un paso al siguiente para complementarla y obtener un producto final completo. 2
2. Importaciones

Se copiaron las mismas importaciones utilizadas en clases anteriores, sin modificaciones. 2
3. Configuración del modelo

Se usó ChatGoogleGenerativeAI con la versión 3.6. 3
Se mencionó la estrategia de usar modelos más antiguos (como 3.5) para ahorrar tokens, ya que los modelos viejitos suelen ofrecer mayor capacidad de tokens. 45
Se aclaró que en producción se puede cambiar a un modelo más especializado. 5
4. Creación de plantillas de extracción

Se explicaron dos enfoques: PromptTemplate normal y ChatPromptTemplate (que incluye el rol del sistema). 6
Se mostraron ambas opciones para que los estudiantes puedan probarlas. 7
5. Primera plantilla: extracción de puntos clave

La plantilla indica: leer un texto y devolver sus 3 puntos clave, uno por línea, sin desarrollarlos. 8
6. Prueba del primer paso

Se utilizó un texto de prueba extraído de la plataforma para validar el paso de extracción. 9
Se llamó a la función inbou pasando el texto prueba como argumento. 10
7. Sugerencias adicionales

Encapsular scripts en funciones externas para reutilizarlos entre proyectos sin copiar y pegar. 11

"""