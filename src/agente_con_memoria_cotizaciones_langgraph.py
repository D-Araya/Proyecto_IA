# ==============================================================================
# AGENTE CON MEMORIA Y SUPERVISIÓN HUMANA (HITL) CON LANGGRAPH Y GEMINI
# ==============================================================================
# Este módulo implementa un agente de IA para un portal administrativo de cotizaciones
# utilizando el stack moderno de LangChain v1 y LangGraph.
#
# Principales capacidades implementadas:
#   1. Llamada a herramientas (Tool Calling) con validación estricta vía Pydantic.
#   2. Memoria conversacional multi-turno persistida por sesión (thread_id) con InMemorySaver.
#   3. Aislamiento estricto de memoria entre diferentes hilos/clientes.
#   4. Supervisión humana en el bucle (Human-in-the-Loop - HITL) con pausas automáticas
#      antes de ejecutar acciones críticas o irreversibles (ej. aplicar descuentos).
#   5. Reanudación segura del grafo mediante primitivas Command(resume=...).
#   6. Observabilidad completa: Auditoría en memoria y registro de trazas en JSON Lines (.jsonl).
# ==============================================================================

from datetime import datetime, timezone
import json
from typing import Any
from dotenv import load_dotenv

# Importaciones de LangChain y LangGraph
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from pydantic import BaseModel, Field

# ==============================================================================
# 1. CONFIGURACIÓN Y MODELO LLM
# ==============================================================================

# Carga variables de entorno desde el archivo .env (GOOGLE_API_KEY o GEMINI_API_KEY)
load_dotenv()

# Inicialización del modelo de lenguaje de Google Gemini:
# - model: Versión del modelo optimizada para velocidad y llamada a herramientas.
# - temperature=0: Determinismo máximo, esencial para tareas de cálculo y administración.
# - timeout=30: Límite de espera de 30 segundos para evitar bloqueos por latencia de red.
# - max_retries=0: Desactiva reintentos automáticos ocultos de la librería para permitir
#                  capturar y reportar excepciones de cuota o red de forma inmediata.
modelo = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
    timeout=30,
    max_retries=0,
)

# InMemorySaver actúa como el "Checkpointer" de LangGraph:
# Guarda el estado de la conversación (mensajes, pasos intermedios y variables) en memoria RAM
# indexado por una clave única llamada 'thread_id'. Esto reemplaza al antiguo RunnableWithMessageHistory.
checkpointer = InMemorySaver()

# Lista en memoria para auditar todas las decisiones humanas (HITL) tomadas en la sesión
registro_aprobaciones: list[dict[str, Any]] = []


# ==============================================================================
# 2. FUNCIONES DE UTILIDAD: EXTRACCIÓN Y OBSERVABILIDAD
# ==============================================================================

def extraer_texto(contenido: Any) -> str:
    """
    Normaliza y extrae el texto plano de la respuesta de un modelo.
    
    ¿Por qué es necesaria?
    Los modelos modernos (incluido Gemini) a veces devuelven el contenido como un simple 'str',
    pero en llamadas con herramientas o respuestas multimodales pueden devolver una lista de
    bloques/diccionarios (ej. [{'type': 'text', 'text': '...'}]). Esta función garantiza que
    siempre obtengamos una cadena legible y limpia.
    """
    if isinstance(contenido, str):
        return contenido
    if isinstance(contenido, list):
        partes = []
        for bloque in contenido:
            if isinstance(bloque, dict) and bloque.get("type") == "text":
                partes.append(bloque.get("text", ""))
            elif isinstance(bloque, str):
                partes.append(bloque)
        return "\n".join(p for p in partes if p).strip()
    return str(contenido)


def registrar_traza(
    thread_id: str,
    entrada: str,
    estado_resultado: dict[str, Any],
    ruta_archivo: str = "trazas_cotizaciones_modernas.jsonl",
) -> None:
    """
    Registra la 'caja negra' de la ejecución en un archivo JSON Lines (.jsonl).
    
    Guarda:
      - Timestamp en formato UTC.
      - thread_id para asociar la traza al cliente o sesión.
      - Entrada original del usuario.
      - Cantidad de mensajes acumulados en el contexto (control de costos y tokens).
      - Herramientas ejecutadas, con qué argumentos y qué resultado dieron.
      - Si el turno fue interrumpido por supervisión humana.
      - Respuesta textual final entregada al usuario.
    """
    mensajes = estado_resultado.get("messages", [])
    resumen_mensajes = []
    
    # Recorremos el historial del hilo para extraer el tipo y contenido de cada mensaje
    for msg in mensajes:
        item: dict[str, Any] = {
            "tipo": getattr(msg, "type", type(msg).__name__),
            "contenido": extraer_texto(getattr(msg, "content", "")),
        }
        # Si el mensaje incluye una solicitud de llamada a herramientas, la registramos
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            item["tool_calls"] = tool_calls
        if getattr(msg, "name", None):
            item["herramienta"] = msg.name
        resumen_mensajes.append(item)

    # El último mensaje del hilo corresponde a la respuesta final del agente
    ultimo_texto = (
        extraer_texto(getattr(mensajes[-1], "content", "")) if mensajes else ""
    )

    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "thread_id": thread_id,
        "total_mensajes_en_hilo": len(mensajes),
        "entrada": entrada,
        "interrumpido": "__interrupt__" in estado_resultado,
        "mensajes": resumen_mensajes,
        "respuesta_final": ultimo_texto,
    }

    # Se usa modo 'append' ("a") para agregar una línea al final sin sobreescribir el archivo
    with open(ruta_archivo, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def registrar_aprobacion(
    herramienta: str,
    argumentos: dict[str, Any],
    decision: str,
    motivo: str | None = None,
) -> None:
    """
    Registra en la lista de auditoría la resolución humana ante una pausa HITL.
    
    Permite auditar quién, cuándo y con qué parámetros se autorizó, editó o rechazó
    una operación comercial sensible (ej. aplicar un descuento especial).
    """
    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": argumentos,
        "decision": decision,
        "motivo": motivo,
        "fecha_hora": datetime.now().isoformat(),
    })


# ==============================================================================
# 3. ESQUEMAS DE VALIDACIÓN CON PYDANTIC
# ==============================================================================

class ArgumentosConsultaCotizacion(BaseModel):
    """
    Esquema tipado y validado para la herramienta 'consultar_cotizacion_detallada'.
    Las descripciones de cada campo (Field) son leídas por el LLM como instrucciones
    para decidir qué argumentos extraer del mensaje del usuario.
    """
    codigo_cotizacion: str = Field(
        description="Código identificador único de la cotización, por ejemplo 'COT-101'."
    )
    incluir_detalle_items: bool = Field(
        default=False,
        description=(
            "Si es True, incluye los ítems presupuestados y la fecha de vigencia; "
            "si es False, devuelve únicamente el estado comercial general."
        ),
    )


# ==============================================================================
# 4. BASE DE DATOS DE REFERENCIA (SIMULADA)
# ==============================================================================

# Diccionario que simula la base de datos o ERP del portal administrativo de cotizaciones
COTIZACIONES = {
    "COT-101": {
        "estado": "Pendiente de aprobación comercial",
        "items": ["3x Servidor Rack Enterprise (SRV-001)"],
        "vigencia": "Válida hasta 2026-12-15",
    },
    "COT-102": {
        "estado": "Aprobada y emitida",
        "items": ["10x Disco SSD 500GB NVMe (SSD-500)"],
        "vigencia": "Válida hasta 2026-11-30",
    },
}


# ==============================================================================
# 5. HERRAMIENTAS DEL AGENTE (@tool)
# ==============================================================================

@tool("consultar_cotizacion_detallada", args_schema=ArgumentosConsultaCotizacion)
def consultar_cotizacion_detallada(
    codigo_cotizacion: str,
    incluir_detalle_items: bool = False,
) -> str:
    """
    Consulta en la base de datos el estado de una cotización y, opcionalmente,
    sus ítems asociados y fecha límite de vigencia.
    """
    cotizacion = COTIZACIONES.get(codigo_cotizacion.upper())
    if cotizacion is None:
        return f"No se encontró una cotización registrada con el código {codigo_cotizacion}."

    # Si no se solicitan los detalles, devuelve solo el estado breve
    if not incluir_detalle_items:
        return cotizacion["estado"]

    # Si se solicitan detalles, concatena los productos y la vigencia
    detalle = ", ".join(cotizacion["items"])
    return f"{cotizacion['estado']} (detalle: {detalle}; {cotizacion['vigencia']})"


@tool
def calcular_subtotal_cotizacion(unidades: int, precio_unitario: float) -> str:
    """
    Calcula el subtotal matemático de una línea de cotización multiplicando
    las unidades requeridas por el precio unitario en dólares estadounidenses (USD).
    """
    # Validación defensiva de datos de entrada
    if unidades <= 0 or precio_unitario < 0:
        return "Valores inválidos: las unidades deben ser mayores a 0 y el precio no negativo."
    subtotal = unidades * precio_unitario
    return f"El subtotal calculado es de ${subtotal:.2f} USD."


@tool
def aplicar_descuento_especial(codigo_cotizacion: str, porcentaje_descuento: float) -> str:
    """
    Aplica un descuento comercial especial a una cotización existente.
    
    IMPORTANTE: Esta herramienta está catalogada como operación crítica y sensible;
    el middleware HumanInTheLoopMiddleware interceptará cualquier intento de ejecutarla
    para solicitar autorización o edición humana previa.
    """
    return (
        f"Descuento especial del {porcentaje_descuento}% aplicado y registrado "
        f"en la cotización {codigo_cotizacion.upper()}."
    )


# Lista de herramientas que el agente tendrá a su disposición para resolver tareas
herramientas = [
    consultar_cotizacion_detallada,
    calcular_subtotal_cotizacion,
    aplicar_descuento_especial,
]


# ==============================================================================
# 6. CONSTRUCCIÓN DEL AGENTE LANGGRAPH (CHECKPOINTER + HITL MIDDLEWARE)
# ==============================================================================

# 'create_agent' compila un StateGraph de LangGraph listo para producción:
# - model: El modelo generativo que decide los pasos a seguir.
# - tools: Conjunto de herramientas disponibles.
# - system_prompt: Directriz de rol y personalidad del asistente.
# - middleware: Interceptores de comportamiento. Aquí HumanInTheLoopMiddleware
#   configura qué herramientas requieren autorización humana antes de correr.
# - checkpointer: Sistema de persistencia que almacena el grafo y sus mensajes por 'thread_id'.
agente = create_agent(
    model=modelo,
    tools=herramientas,
    system_prompt=(
        "Eres un asistente administrativo para un portal de cotizaciones. "
        "Usa las herramientas disponibles para consultar cotizaciones, calcular subtotales "
        "o aplicar descuentos especiales. Responde siempre en español de forma clara."
    ),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # Pausa la ejecución automáticamente antes de aplicar un descuento
                "aplicar_descuento_especial": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                # Las herramientas de solo lectura corren sin interrupción (False)
                "consultar_cotizacion_detallada": False,
                "calcular_subtotal_cotizacion": False,
            },
            description_prefix="Revisión comercial requerida antes de ejecutar",
        )
    ],
    checkpointer=checkpointer,
)


# ==============================================================================
# 7. FUNCIÓN ORQUESTADORA DE EJECUCIÓN CON RESOLUCIÓN HITL
# ==============================================================================

def ejecutar_con_hitl(
    entrada: str,
    config: dict[str, Any],
    decision_manual: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Orquesta la ejecución de un turno de conversación en el agente:
      1. Envía el mensaje del usuario al grafo dentro del hilo especificado (thread_id).
      2. Si el grafo se detiene por una interrupción HITL ('__interrupt__'):
         - Detecta qué herramienta sensible solicitó el modelo y con qué argumentos.
         - Si 'decision_manual' está definida, aplica esa decisión directamente (modo pruebas).
         - Si no, abre un prompt interactivo por consola pidiendo al operador:
             'a' (aprobar), 'e' (editar argumentos) o 'r' (rechazar).
         - Registra la decisión en la lista de auditoría.
         - Reanuda la ejecución del grafo usando Command(resume={"decisions": [decision]}).
      3. Registra la traza del turno completo en el archivo .jsonl y retorna el resultado.
    """
    thread_id = config["configurable"]["thread_id"]
    print(f"\n[{thread_id}] Iniciando consulta a Gemini...", flush=True)

    try:
        # Ejecución inicial del turno en el grafo
        resultado = agente.invoke(
            {"messages": [{"role": "user", "content": entrada}]},
            config=config,
        )
        print(f"[{thread_id}] Respuesta recibida correctamente.", flush=True)

    except Exception as error:
        # Captura defensiva si la API de Google alcanza el límite de cuota (HTTP 429)
        if any(w in str(error).lower() for w in ["rate", "quota", "429"]):
            print(
                "\n[ERROR] Se agotó la cuota de Gemini API.\n"
                "Revisa tus límites en https://ai.dev/rate-limit\n"
                "Espera el restablecimiento de la cuota antes de continuar.",
                flush=True,
            )
        raise

    # Bucle que gestiona una o más interrupciones generadas por el HumanInTheLoopMiddleware
    while "__interrupt__" in resultado:
        interrupciones = resultado["__interrupt__"]
        for interrupcion in interrupciones:
            print("\n[PAUSA HITL] Interrupción detectada:", interrupcion.value)

        # Flujo A: Interacción humana directa por consola si no se pasó decisión programática
        if decision_manual is None:
            raw = input("¿Aprobar descuento? (a = approve / e = edit / r = reject): ").strip().lower()
            if raw == "a":
                decision = {"type": "approve"}
            elif raw == "e":
                nuevo_pct = float(input("Nuevo porcentaje de descuento: ").strip())
                cod = input("Código de cotización (ej. COT-101): ").strip().upper()
                decision = {
                    "type": "edit",
                    "edited_action": {
                        "name": "aplicar_descuento_especial",
                        "args": {
                            "codigo_cotizacion": cod,
                            "porcentaje_descuento": nuevo_pct,
                        },
                    },
                }
            else:
                decision = {
                    "type": "reject",
                    "message": "Descuento rechazado por política comercial.",
                }
        # Flujo B: Inyección automática de la decisión (ideal para pruebas y pipelines automatizados)
        else:
            decision = decision_manual

        # Registramos cada acción solicitada en el log de auditoría
        for interrupcion in interrupciones:
            acciones_req = (
                interrupcion.value.get("action_requests", [])
                if isinstance(interrupcion.value, dict)
                else []
            )
            for req in acciones_req:
                registrar_aprobacion(
                    herramienta=req.get("name", "aplicar_descuento_especial"),
                    argumentos=req.get("args", {}),
                    decision=decision.get("type", "unknown"),
                    motivo=decision.get("message"),
                )

        # Reanudamos el grafo exactamente en el mismo hilo usando Command(resume=...)
        resultado = agente.invoke(
            Command(resume={"decisions": [decision]}),
            config=config,
        )

    # Registro persistente de la interacción en el archivo de trazas .jsonl
    registrar_traza(thread_id=thread_id, entrada=entrada, estado_resultado=resultado)
    return resultado


# ==============================================================================
# 8. CASOS DE PRUEBA Y VERIFICACIÓN
# ==============================================================================

if __name__ == "__main__":
    print("==================================================================")
    print("INICIANDO PRUEBAS DEL AGENTE DE COTIZACIONES CON LANGGRAPH Y HITL")
    print("==================================================================")

    # --------------------------------------------------------------------------
    # PRUEBA 1: Memoria conversacional multi-turno en un mismo hilo (thread_id)
    # --------------------------------------------------------------------------
    cfg_hilo_1 = {"configurable": {"thread_id": "hilo_cotizaciones_01"}}

    # Turno 1: Consulta inicial. El agente debe usar 'consultar_cotizacion_detallada'
    r1 = ejecutar_con_hitl(
        "Consulta el estado de la cotización COT-101 incluyendo su detalle.",
        cfg_hilo_1,
    )
    print("\nTurno 1:", extraer_texto(r1["messages"][-1].content))

    # Turno 2: Seguimiento contextual. El agente recuerda que hablamos de cotizaciones
    # y utiliza 'calcular_subtotal_cotizacion' para calcular el precio de 4 unidades
    r2 = ejecutar_con_hitl(
        "¿Y cuál sería el subtotal de 4 unidades a 1200.0 USD?",
        cfg_hilo_1,
    )
    print("Turno 2:", extraer_texto(r2["messages"][-1].content))

    # --------------------------------------------------------------------------
    # PRUEBA 2: Aislamiento estricto de memoria entre hilos independientes
    # --------------------------------------------------------------------------
    cfg_hilo_2 = {"configurable": {"thread_id": "hilo_cotizaciones_02"}}
    cfg_hilo_3 = {"configurable": {"thread_id": "hilo_cotizaciones_03"}}

    # En el hilo 02 hablamos sobre la cotización COT-102
    ejecutar_con_hitl(
        "Estoy revisando la cotización COT-102.",
        cfg_hilo_2,
    )

    # En el hilo 03 preguntamos qué cotización vimos. Como es un hilo independiente,
    # el agente NO debe saber nada de COT-102 (evita fuga de datos entre clientes)
    r_aislado = ejecutar_con_hitl(
        "¿De qué cotización te pregunté en este hilo?",
        cfg_hilo_3,
    )
    print("\nAislamiento hilo_03:", extraer_texto(r_aislado["messages"][-1].content))

    # --------------------------------------------------------------------------
    # PRUEBA 3: Interrupción Human-in-the-Loop (HITL) y Aprobación
    # --------------------------------------------------------------------------
    # Se solicita una acción sensible (descuento del 12%). El grafo pausará en
    # 'aplicar_descuento_especial', resolverá la pausa mediante la decisión
    # inyectada y reanudará el flujo completando la respuesta y el registro.
    r_hitl = ejecutar_con_hitl(
        "Aplica un 12% de descuento especial a la cotización COT-101.",
        cfg_hilo_1,
        decision_manual={"type": "approve"},
    )
    print("\nResultado HITL:", extraer_texto(r_hitl["messages"][-1].content))
    print("Auditoría de aprobaciones registradas:", registro_aprobaciones)

    print("\n==================================================================")
    print("PRUEBAS FINALIZADAS EXITOSAMENTE")
    print("==================================================================")
