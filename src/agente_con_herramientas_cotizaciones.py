from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Instanciar el modelo de Gemini para el agente
modelo = ChatGoogleGenerativeAI(model="gemini-3.8-flash")

"""
Introducción al Código del Agente
A diferencia de las cadenas estáticas o enrutadas (RunnableBranch) que 
construiste en los bloques anteriores, este script implementa un Agente 
ReAct (Razonamiento, Acción y Observación) utilizando LangChain.
El agente no sigue un camino fijo: evalúa dinámicamente la pregunta del 
usuario, decide autónomamente qué herramienta invocar, lee la observación 
resultante y redacta la respuesta final. Para lograrlo de forma robusta, 
el script incorpora:
Herramientas tipadas y decoradas con @tool, dotadas de un docstring descriptivo 
y manejo interno de excepciones con try/except.
El patrón AgentExecutor y create_tool_calling_agent importado desde 
langchain_classic.agents.
El buffer MessagesPlaceholder("agent_scratchpad"), que actúa como la memoria 
a corto plazo donde el agente anota el historial de razonamiento paso a paso.
"""

# 1. Definición de Herramientas Personalizadas con manejo de excepciones propio
@tool
def consultar_precio_producto(codigo_producto: str) -> str:
    """Consulta el precio unitario y la vigencia comercial de un producto 
    a partir de su código interno. Usar estrictamente cuando el usuario pregunta 
    cuánto cuesta o cuál es el precio de un artículo específico."""
    catalogo_precios = {
        "SRV-001": "Servidor Rack Enterprise: $1,200.00 USD (Vigente)",
        "SSD-500": "Disco SSD 500GB NVMe: $85.00 USD (Vigente)"
    }
    try:
        return catalogo_precios[codigo_producto]
    except KeyError:
        return f"No se encontró un producto registrado con el código {codigo_producto}."

@tool
def calcular_presupuesto_total(cantidad: int, precio_unitario: float) -> str:
    """Calcula el importe total de una línea de cotización multiplicando 
    la cantidad de unidades por el precio unitario. Usar cuando el usuario 
    necesite calcular subtotales o presupuestos matemáticos."""
    try:
        total = cantidad * precio_unitario
        return f"El importe total calculado es de ${total:.2f} USD."
    except Exception as e:
        return f"Error al calcular el presupuesto: {str(e)}"

# 2. Configuración del Prompt del Agente con rol de sistema y scratchpad
prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente inteligente para la administración de un portal de cotizaciones. "
        "Usa las herramientas disponibles cuando necesites consultar precios o calcular subtotales.",
    ),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# 3. Creación del Agente y el Executor de ejecución con parámetros de protección
herramientas = [consultar_precio_producto, calcular_presupuesto_total]
agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

ejecutor_agente = AgentExecutor(
    agent=agente, 
    tools=herramientas, 
    verbose=True, 
    return_intermediate_steps=True,
    max_iterations=5,                  # Limita los intentos máximos para evitar colgarse
    handle_parsing_errors=True         # Maneja errores de formato de forma segura
)

if __name__ == "__main__":
    print("=== PRUEBA 1: Consulta de Herramienta de Precios ===")
    resultado_1 = ejecutor_agente.invoke({
        "entrada": "¿Cuál es el precio del producto SRV-001?"
    })
    
    # Verificación de la traza de decisión mediante intermediate_steps
    herramienta_usada_1 = resultado_1["intermediate_steps"][0][0].tool
    assert herramienta_usada_1 == "consultar_precio_producto"
    print("\n[✓] Prueba 1 superada. Herramienta utilizada:", herramienta_usada_1)
    print("Respuesta final:", resultado_1["output"])

    print("\n=== PRUEBA 2: Pregunta General (Sin Herramienta) ===")
    resultado_2 = ejecutor_agente.invoke({
        "entrada": "¿Cómo puedo contactar a soporte administrativo?"
    })
    assert resultado_2["intermediate_steps"] == []
    print("[✓] Prueba 2 superada. El agente respondió directamente sin invocar herramientas.")
    print("Respuesta final:", resultado_2["output"])