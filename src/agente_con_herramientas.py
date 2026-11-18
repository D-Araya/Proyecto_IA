from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool #Herramientas
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent
)

from langchain_core.prompts import (
    ChatPromptTemplate, #Me permite agregar system_instructions y user(human)
    MessagesPlaceholder
)


modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

#Tool/Herramienta es una función común de Python. Descripción en lenguaje natural será lo que el modelo lea (prompt) para decidir si elige o no esa herramienta
@tool
def buscar_en_documentacion(consulta: str) -> str:
    """
    Busca información relevante de la documentación interna del producto.
    Usar cuando la pregunta es sobre cómo funciona algo del sistema.
    """
    documentacion = {
        "reintentos": "El cliente reintenta hasta 3 veces ante un TimeoutError, con espera creciente",
        "costos": "El costo se calcula a patir de totalTokenCount, según la tarifa vigente."
    }

    for clave, texto in documentacion.items():
        if clave in consulta.lower():
            return texto
            
    return "No se encontró información sobre esa consulta en la documentación."

@tool
def calcular(expresion: str) -> str:
    """
    Evalúa una expresión aritmética simple, como '350 + 250'.
    Usar cuando la pregunta requiere un cálculo numérico.
    """
    permitido = set("0123456789+-*/().")
    if not set(expresion) <= permitido:
        return "Expresión no permitida."
    try:
        return str(eval(expresion))
    except Exception as e:
        return f"Error al evaluar: {e}"

herramientas = [buscar_en_documentacion, calcular] #Lista de Herramientas

#Plantilla, con system_instructions
prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system", "Eres un asistente que responde preguntas usando las herramientas disponibles cuando las necesites."
    ),
    (
        "human", "{entrada}"
    ),
    MessagesPlaceholder("agent_scratchpad") #El espacio donde LangChain va anotando, pasos/ciclos razonar-actuar-observar, qué herramientas llamó y qué devolvieron
])


#Agente: modelo, herramientas, prompt, formato
agente = create_tool_calling_agent(
    modelo, herramientas, prompt_agente
)

#Orquestador: es el que controla el ciclo entre razonar-actuar-observar
ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=True, #Imprime los pasos que va siguiendo
)

resultado = ejecutor_agente.invoke(
    {"entrada": "¿Cuánto es 340+215?" }
)

print("Respuesta Final:", resultado["output"])



""" ----------------
1. Importaciones clave Se importaron módulos como load_dotenv, ChatGoogleGenerativeAI, tool, AgentExecutor, create_tool_calling_agent, ChatPromptTemplate y MessagesPlaceholder.

2. Modelo Se generó el modelo usando ChatGoogleGenerativeAI con gemini-1.5-flash. 1

3. Herramientas (@tool) Cada herramienta es una función Python decorada con @tool. La descripción en lenguaje natural es el "prompt" que el modelo lee para decidir si usa esa herramienta. 2

buscar_en_documentacion: Recibe una consulta (str) y busca coincidencias en un diccionario interno con claves como reintentos y costos. Si no hay coincidencia, retorna un mensaje de "no encontrado". 345
calcular: Recibe una expresión aritmética (str), valida que solo contenga caracteres permitidos (dígitos, +, -, *, /, ., paréntesis) y evalúa la expresión. Si no es válida, retorna "Expresión no permitida". 678
4. Lista de herramientas Se creó una lista herramientas = [buscar_en_documentacion, calcular] para indicarle al agente qué herramientas tiene disponibles. 9

5. Plantilla (ChatPromptTemplate) Se construyó con tres partes: 101112

system: instrucción del sistema ("Eres un asistente que responde usando las herramientas disponibles")
human: entrada del usuario
MessagesPlaceholder: almacena los pasos del ciclo razonar-actuar-observar (herramientas llamadas y sus respuestas) 13
6. Agente y Ejecutor

El agente se creó con create_tool_calling_agent(modelo, herramientas, prompt). 14
El orquestador AgentExecutor controla el ciclo razonar-actuar-observar, con verbose=True para imprimir los pasos en consola. 151617
7. Ejecución Se invoca con ejecutor_agente.invoke({"entrada": "¿cuánto es 340 + 215?"}). El agente intentó primero con espacios (expresión no permitida) y luego sin espacios, obteniendo 555.  """