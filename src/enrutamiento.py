from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI #llamar al modelo
from langchain_core.prompts import PromptTemplate #llamar a la plantilla, prompt dinamico
from langchain_core.output_parsers import StrOutputParser   #llamar al parser para parsear la respuesta y la transforma en solo texto
from langchain_core.runnables import (RunnableBranch, RunnablePassthrough, RunnableLambda) #Bifurcaciones/Branches/Ramificaciones

import logging #Generar un archivo de log con los errores que se me presenten

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", #2026-11-04 16:40 [WARNING] main: No se pudo ejecutar x
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="error.log",
    filemode="a", #añade nuerva linea al final del archivo, "append"
    encoding="utf-8",
    force=True
)
logger = logging.getLogger(__name__)

load_dotenv()
os.environ.pop("GEMINI_API_KEY", None)  

modelo = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")

plantilla_clasificacion = PromptTemplate.from_template(
    "Clasifica el siguiente mensaje de soporte en una sola palabra: "
    "pregunta, queja o sugerencia. Responde solo con esa palabra. \n\n {mensaje}"
)

paso_clasificacion = (
    plantilla_clasificacion
    | modelo
    | StrOutputParser()
    | (lambda texto: texto.strip().lower())
)

""" mensaje_prueba = "Eres linda"

clasificacion = paso_clasificacion.invoke(
    {"mensaje": mensaje_prueba}
)

print(clasificacion)  """

cadena_pregunta = (
    PromptTemplate.from_template("Responde esta pregunta técnica con precisión: \n\n {mensaje}")
    | modelo
    | StrOutputParser()
)

cadena_queja = (
    PromptTemplate.from_template("Responde esta queja con empatía, reconociendo el problema antes de ofrecer una solución: \n\n {mensaje}")
    | modelo
    | StrOutputParser()
)

cadena_sugerencia = (
    PromptTemplate.from_template("Agradece esta sugerencia y explica cómo se evaluará dentro del producto: \n\n {mensaje}")
    | modelo
    | StrOutputParser()
)

#Sintaxis RunnableBranch
# caminos = RunnableBranch(
#     (condicion_1, rama_1), #if
#     (condicion_2, rama_2), #elif
#     (condicion_3, rama_3), #elif
#     rama_por_defecto #else
# ) #Cada condicion debe ser una función; suele ser un lambda


#x = {"clasificacion": "queja", "mensaje": "Mi teléfono no funciona"}
bifurcacion = RunnableBranch(
    (lambda x: x["clasificacion"] == "queja", cadena_queja),
    (lambda x: x["clasificacion"] == "sugerencia", cadena_sugerencia),
    cadena_pregunta
)

cadena_con_enrutamiento = (
    RunnablePassthrough.assign(clasificacion=paso_clasificacion) #{"mensaje": "Deberían de tener más agentes disponibles.", "clasificacion": resultado de paso_clasificacion}
    | bifurcacion
)

#Fallback: cadena de respaldo. Captura las caídas de mi LLM (RateLimitError, 401, APIConnectionError, respuestas vacías)

def fallback_con_log(x):
    logger.warning("Cadena principal falló. Activando respuesta genérica")
    return "Gracias por tu mensaje. Un miembro de nuestro equipo te va a responder pronto."

respuesta_generica = RunnableLambda(
    fallback_con_log
)


""" respuesta_generica = RunnableLambda(
    #Todo: log
    lambda x: (
        "Gracias por tu mensaje. Un miembro de nuestro equipo te va a responder pronto."
    )
) """

cadena_robusta = cadena_con_enrutamiento.with_fallbacks([respuesta_generica])

def procesar_mensaje_seguro(cadena, mensaje):
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error("Error procesando mensaje: %s", error)
        return "No pudimos procesar tu mensaje en este momento. Intenta de nuevo más tarde"


if __name__ == "__main__":  #Solamente ejecuta el siguiente bloque de código si la ejecución es directa del archivo. NO EJECUTES si es import
    mensaje = "Llevo varios días sin poder entrar a mi cuenta."
    print(procesar_mensaje_seguro(cadena_robusta, mensaje))



""" resultado = cadena_robusta.invoke(
    {"mensaje": "Deberían de tener más agentes disponibles."}
)
 """
""" resultado = cadena_con_enrutamiento.invoke(
    {"mensaje": "La encomienda no me llega"}
) """

#print(resultado)


#[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', $null, 'User')
#Remove-Item Env:\GEMINI_API_KEY

"""Lo último que dijo Cynthia fue sobre la clase Runnable Pass Through (RunnablePassthrough). 1

Explicó que esta clase es la segunda que importaron al principio del archivo de enrutamiento, y su función es agregar al diccionario original la información que viene pasando desde el inicio del flujo. 1

El contexto de por qué se necesita es el siguiente:

Para que la bifurcación funcione correctamente, necesita recibir un diccionario que tenga dos claves: la clasificación (resultado del paso de clasificación) y el mensaje original del usuario. 2
El RunnablePassthrough permite conservar el mensaje original mientras también se obtiene la clasificación del primer paso, para así poder armar ese diccionario completo. 13
Este diccionario combinado es el que luego recibe el RunnableBranch para decidir qué cadena ejecutar (pregunta, queja o sugerencia). 2
En resumen, RunnablePassthrough actúa como un mecanismo que "pasa" la información original junto con la nueva, para que el siguiente paso tenga todos los datos que necesita. 1

----------------------------

Lo último que dijo Cynthia fue sobre la necesidad de usar RunnablePassthrough para armar correctamente el diccionario que necesita la cadena de enrutamiento. 1

El problema que explicó es el siguiente:

Si solo se ejecuta el paso de clasificación, el resultado que se retiene es únicamente la clasificación (queja, pregunta o sugerencia). 1
Sin embargo, la bifurcación necesita dos datos: la clasificación y el mensaje original del usuario. 12
El RunnablePassthrough permite conservar el mensaje original y agregarle al diccionario la clasificación obtenida del primer paso. 2
En resumen, sin RunnablePassthrough, se perdería el mensaje original al pasar por el paso de clasificación, y las cadenas de queja, pregunta o sugerencia no tendrían el mensaje para generar una respuesta adecuada. 

-------------------------------------

Lo último que explicó Cynthia fue sobre cómo RunnablePassthrough construye el diccionario final que necesita la cadena de enrutamiento. 1

El resultado de usar RunnablePassthrough es un diccionario que contiene dos claves: 1

mensaje — el mensaje original del usuario que viene pasando desde el inicio del flujo. 2
clasificación — el resultado obtenido del paso de clasificación (queja, pregunta o sugerencia). 3
La razón por la que se necesitan ambas claves es: 4

La clasificación es necesaria para que RunnableBranch evalúe la condición y decida qué rama ejecutar. 5
El mensaje es necesario para que la cadena seleccionada (queja, pregunta o sugerencia) pueda generar una respuesta adecuada. 6
En resumen, RunnablePassthrough garantiza que el diccionario final tenga ambos datos disponibles para que todo el flujo de bifurcación funcione correctamente. 


------------------------------------

Lo último que explicó Cynthia fue sobre cómo funciona la cadena de enrutamiento completa y el rol de RunnablePassthrough dentro de ella. 12

Explicó que al momento de hacer la invocación de la cadena de enrutamiento, el primer paso que se ejecuta es el RunnablePassthrough. 1 Este paso, a su vez, ejecuta el paso de clasificación, que es en sí mismo una cadena de pasos. 2

El paso de clasificación necesita recibir un diccionario con el mensaje del usuario. 23 Por eso, al invocar la cadena, se envía un diccionario que incluye el mensaje, por ejemplo:

{"mensaje": "deberían tener más agentes disponibles"} 4
El flujo completo sería: 123

Se invoca la cadena de enrutamiento con el diccionario que contiene el mensaje.
El RunnablePassthrough ejecuta el paso de clasificación, que recibe ese mensaje.
El resultado es un diccionario con dos claves: mensaje y clasificación.
Ese diccionario se pasa a la bifurcación (RunnableBranch), que evalúa la clasificación y decide qué cadena ejecutar (queja, sugerencia o pregunta).
Al final, se imprime el resultado. 3
En resumen, todo el flujo arranca con un simple diccionario con el mensaje, y la cadena de enrutamiento se encarga de clasificarlo y dirigirlo al camino correcto. 15

-----------------------

Aquí está el resumen del código que construyó Cynthia durante la sesión:

1. Plantilla de clasificación Recibe un mensaje y lo clasifica en una sola palabra: pregunta, queja o sugerencia. 12 Se agrega un lambda con .strip().lower() para normalizar la respuesta y evitar inconsistencias de mayúsculas o espacios. 34

2. Tres cadenas independientes Cada una tiene su propio PromptTemplate, modelo y StringOutputParser: 56

Cadena pregunta: responde de forma técnica y precisa. 7
Cadena queja: responde con empatía, reconociendo el problema y ofreciendo solución. 8
Cadena sugerencia: agradece la sugerencia y explica cómo se evaluará. 910
3. RunnablePassthrough + paso de clasificación Ejecuta el paso de clasificación y fusiona su resultado con el mensaje original, generando un diccionario con dos claves: clasificación y mensaje. 1112 Esto es necesario porque las cadenas necesitan ambos datos para funcionar. 13

4. RunnableBranch (bifurcación) Evalúa el diccionario resultante y decide qué cadena ejecutar: 1415

Si clasificación == "queja" → ejecuta cadena queja. 16
Si clasificación == "sugerencia" → ejecuta cadena sugerencia. 17
Por defecto → ejecuta cadena pregunta. 1819
5. Invocación final Se invoca la cadena de enrutamiento enviando un diccionario con el mensaje del usuario, y el flujo se ejecuta de forma secuencial y automática, retornando la respuesta final. 


"""