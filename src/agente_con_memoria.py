#Herramientas Personalizadas
#Intro a Memoria

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from pydantic import BaseModel, Field, ValidationError
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

import queue
import threading

#Configuraciones e Inicializaciones
load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")


# === Auditoría/Human in the Loop ===
registro_aprobaciones = []

def esperar_aprobacion(mensaje: str, tiempo_limite_segundos: int = 300) -> bool:
    cola_respuesta = queue.Queue()

    def pedir_entrada():
        try:
            texto = input(mensaje)
            cola_respuesta.put(texto.strip().lower())
        except (EOFError, KeyboardInterrupt):
            cola_respuesta.put("")

    # AGREGAR daemon=True AQUÍ
    hilo = threading.Thread(target=pedir_entrada, daemon=True)
    hilo.start()

    try:
        respuesta = cola_respuesta.get(timeout=tiempo_limite_segundos)
        aprobado = (respuesta == "s")
        registro_aprobaciones.append(aprobado)
        return aprobado
    except queue.Empty:
        print("Tiempo de espera agotado. Solicitud denegada por timeout")
        registro_aprobaciones.append(False)
        return False
        

class ArgumentosConsultaEnvio(BaseModel):
    """
    Esquema para documentar y validar argumentos campo por campo ante el LLM.
    """
    numero_seguimiento: str = Field(
        description="Número de seguimiento del envío, por ejemplo 'AR129012'."
    )
    incluir_historial: bool = Field(
        default=False,
        description="Si es True, incluye en historial completo de los estados, no solo el actual."
    )

#Base de Datos
ESTADOS = {
    "AR12345": {
        "actual": "En transito",
        "historial": [
            "Recibido en depósito",
            "En tránsito"
        ]
    },
    "AR12346": {
        "actual": "Entregado",
        "historial": [
            "Recibido en depósito",
            "En tránsito"
        ]
    }
}

#Herramientas
#@tool("nuevo_nombre")
@tool(args_schema=ArgumentosConsultaEnvio) #LangChain transforma esta clase en un esquema JSON que se envía al LLM. El modelo lo lee textualmente
def consultar_estado_envio_detallado(numero_seguimiento: str, incluir_historial: bool = False):
    """
    Consulta el estado de un envío, con la opción de incluir el historial completo.
    """
    envio = ESTADOS.get(numero_seguimiento) #AR12346
    #envio = {
    #    "actual": "Entregado",
    #    "historial": [
    #        "Recibido en depósito",
    #        "En tránsito"
    #    ]
    #}
    if envio is None:
        return f"No se encontró un envío con el número {numero_seguimiento}."

    #Si no se solicita el historial, retornamos solo el estado actual
    if not incluir_historial:
        return envio["actual"]

    #Si sí se solicita el historial, formatear y retornar la info
    historial = ", ".join(envio["historial"]) # "Recibido en depósito, En tránsito"
    return f"{envio['actual']} (historial: {historial})" # "Entregado (historial: Recibido en depósito, En tránsito)"

#gradio puede servir para UI

@tool
def calcular_costo_envio(peso_kg: float, distancia_km: float) -> str:
    """Calcula el costo estimado de un envío según su peso y la distancia a recorrer.
    Usar cuando el usuario pregunta cuánto va a costar enviar algo."""
    costo = 500 + (peso_kg * 120) + (distancia_km * 3)
    return f"El costo estimado es de ${costo:.2f}"

#Listado de herramientas
herramientas = [consultar_estado_envio_detallado, calcular_costo_envio]

#Gestión de historial en memoria
historiales = {}
"""
historiales = {
    'cliente_123': {MENSAJES},
    'cliente_345': {MENSAJES},
}
"""

def obtener_historial(session_id: str): #cliente_567
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]

#Construcción del agente
prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system", "Eres un asistente de logística que responde preguntas usando las herramientas disponibles."
    ),
    #Todo: historial de chats
    MessagesPlaceholder("chat_history"),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad")
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=True
)

limpiar_salida = RunnableLambda(
    lambda d: {**d, "output": d["output"][0]["text"] if isinstance(d.get("output"), list) else d.get("output")}
)

cadena_agente = ejecutor_agente | limpiar_salida

# agente con memoria
agente_con_memoria = RunnableWithMessageHistory(
    cadena_agente,
    obtener_historial,
    input_messages_key="entrada",
    history_messages_key="chat_history",
    output_messages_key="output"
)

if __name__ == "__main__":
#    resultado = ejecutor_agente.invoke(
#        {"entrada": "¿Cuál es el estado del envío AR12345, con su historial?"}
#    )
#    print("Respuesta: ", resultado["output"][0]["text"])

    config1 = {"configurable": {"session_id": "cliente_456"}}
    resultado1 = agente_con_memoria.invoke(
        {"entrada": "¿Cuál es el estado del envío AR12345, con su historial?"},
        config1
    )

    print("Turno 1: ", resultado1["output"])

    resultado2 = agente_con_memoria.invoke(
        {"entrada": "¿Y ese mismo envío ya fue entregado?"},
        config1
    )

    print("Turno 2: ", resultado2["output"])

    config2 = {"configurable": {"session_id": "cliente_567"}}
    resultado3 = agente_con_memoria.invoke(
        {"entrada": "¿Cuánto cuesta enviar un paquete de 3kg a 300km"},
        config2
    )

    print("Turno 3:", resultado3['output'])

    resultado4 = agente_con_memoria.invoke(
        {"entrada": "¿Y cuánto costaría con el doble de peso?"},
        config2
    )

    print("Turno 4:", resultado4['output'])


"""
que hac eel MessagesPlaceholder
Curso Especialización IA para roles emergentes Accenture Septiembre 2026
06:45 PM
AI chat said
Thought process
Show
MessagesPlaceholder serves as a space within the prompt template to store and inject a history of messages. Specifically:

For the agent: It stores the notes of the agent — tracking which tools were called and what they returned (Agent Scratchpad). 1
For conversation history: It stores the chat history of the session under a key (e.g., chat_history), enabling a basic form of memory. 2
Key rule: The name used in the MessagesPlaceholder must match exactly the key name used elsewhere in the chain — both must be identical. 3


Show sources (1)
You Said: en español
en español
Curso Especialización IA para roles emergentes Accenture Septiembre 2026
06:45 PM
AI chat said
Thought process
Show
El MessagesPlaceholder cumple dos funciones principales:

Notas del agente (Agent Scratchpad): Es el espacio donde LangChain va registrando qué herramientas llamó y qué devolvieron. 1

Historial de conversación (chat_history): Permite guardar los mensajes de la sesión bajo una clave (por ejemplo, chat_history), funcionando como una memoria básica. 2

Regla importante: El nombre que se le asigne al MessagesPlaceholder debe coincidir exactamente con la clave utilizada en el resto de la cadena — ambos nombres deben ser idénticos. 3


Show sources (1)
You Said: necesito que expliques de forma detallada, lo que explico la profe, sobre el uso de los historiales y la relacion con las sesiones
necesito que expliques de forma detallada, lo que explico la profe, sobre el uso de los historiales y la relacion con las sesiones 
Curso Especialización IA para roles emergentes Accenture Septiembre 2026
07:36 PM
AI chat said
Thought process
Show
Historial de Conversación y Sesiones
¿Qué es el historial de chat?
El historial almacena los mensajes de cada sesión de conversación. 1 Se guarda bajo una clave llamada chat_history dentro del MessagesPlaceholder. 2

Session ID: el identificador clave
Cada conversación tiene un Session ID único que la separa de otras. 3
Si el Session ID no existe, se crea una conversación nueva. 4
Si el Session ID ya existe, se recupera el historial previo de esa sesión. 4
El desarrollador es responsable de generar Session IDs únicos y seguros. 5
¿Cómo se usa en el código?
Al invocar al agente, se envía una configuración con el Session ID: 6

Se pasa un objeto config con la clave configurable y dentro el session_id. 56
Esto le indica al agente cuál historial debe recuperar o crear. 7
Múltiples sesiones (múltiples clientes)
Dos usuarios o conversaciones diferentes tienen Session IDs distintos → están completamente separadas. 3
El historial se guarda en un diccionario donde cada clave es un Session ID diferente. 8
Un mismo cliente puede tener múltiples Session IDs (por ejemplo, al abrir una nueva conversación). 8
¿Por qué es importante?
Sin memoria, si se pregunta "¿ya fue entregado ese envío?" sin especificar cuál, el agente no sabría de qué envío se habla. 9 Gracias al historial, el agente ya conoce el contexto de la conversación anterior y puede responder correctamente. 10


Show sources (1)
You Said: dame la explicacion del codigo que dijo la profe
dame la explicacion del codigo que dijo la profe
Curso Especialización IA para roles emergentes Accenture Septiembre 2026
08:01 PM
AI chat said
Thought process
Show
Explicación del Código: Agente con Memoria
1. Importaciones clave
Se utilizan dos importaciones principales para el historial: 1

InMemoryChatMessageHistory: Guarda una lista de mensajes en memoria por sesión. 2
RunnableWithMessageHistory: Envuelve al agente para que pueda recibir y usar ese historial. 3
2. Estructura del historial
Se crea una variable historiales (diccionario) donde cada clave es un Session ID y el valor es un objeto InMemoryChatMessageHistory. 4
Limitación: cada vez que se re-ejecuta el script, el diccionario se vacía. Para persistencia real, se debe guardar en un archivo JSON o base de datos. 56
3. Plantilla con MessagesPlaceholder
La plantilla incluye dos MessagesPlaceholder: 78

Uno para las notas del agente (Agent Scratchpad).
Otro para el historial del chat (chat_history).
4. Limpieza de salida (paso adicional)
Gemini devuelve la respuesta en un formato especial (lista, índice 0, clave text). Para que sea compatible con InMemoryChatMessageHistory, se crea una función limpiar_salida que extrae solo el texto. 9 Luego se encadena: cadena_agente = ejecutor | limpiar_salida. 10

5. Invocación con configuración
Al invocar al agente, se envía una configuración con el Session ID: 1112

config = {"configurable": {"session_id": "cliente_456"}}
agente_con_memoria.invoke({"input": "..."}, config=config)
Si el Session ID no existe → nueva conversación. 13
Si ya existe → recupera el historial previo. 13
6. Múltiples sesiones
Distintos clientes usan Session IDs diferentes, manteniendo conversaciones completamente separadas. 1214


Show sources (1)
You Said: dime lo que respondio la profe, cuando le preguntaron: consulta profe, para esto al humano deberia llegarle una notificacion, sino el humano tendria que estar frente a la consola 24/7
dime lo que respondio la profe, cuando le preguntaron: 
consulta profe, para esto al humano deberia llegarle una notificacion, sino el humano tendria que estar frente a la consola 24/7
Curso Especialización IA para roles emergentes Accenture Septiembre 2026
08:36 PM
AI chat said
Thought process
Show
Cynthia respondió que ese escenario es un caso bastante hipotético e irreal, ya que todo se está haciendo desde consola. 1 Lo que se tiene en la vida real es un equipo de Frontend que se encargue de mostrar las notificaciones y gestionar las aprobaciones. 2

Específicamente, Cynthia explicó que:

En un sistema real, ante una petición de aprobación, el Frontend mostraría la notificación correspondiente al supervisor. 2
Las aprobaciones pendientes se mostrarían en una tabla dentro del panel del sistema, no en la consola. 2
Lo que se está implementando en clase es solo una representación simplificada a través de la consola, pero en producción sería completamente diferente. 12
En resumen, Cynthia reconoció que la implementación mostrada es solo didáctica, y que en un ambiente de producción real, el humano recibiría notificaciones a través de un Frontend adecuado, sin necesidad de estar frente a la consola. 2

"""