from datetime import datetime, timezone
import json
from typing import Any
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from pydantic import BaseModel, Field

# === Configuraciones e Inicializaciones ===
load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
checkpointer = InMemorySaver()

registro_aprobaciones: list[dict[str, Any]] = []


def extraer_texto(contenido: Any) -> str:
    """Normaliza respuestas que pueden venir como str o lista de bloques."""
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
    """Registra el estado final del hilo, mensajes y trazas de herramientas."""
    mensajes = estado_resultado.get("messages", [])
    resumen_mensajes = []
    for msg in mensajes:
        item: dict[str, Any] = {
            "tipo": getattr(msg, "type", type(msg).__name__),
            "contenido": extraer_texto(getattr(msg, "content", "")),
        }
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            item["tool_calls"] = tool_calls
        if getattr(msg, "name", None):
            item["herramienta"] = msg.name
        resumen_mensajes.append(item)

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

    with open(ruta_archivo, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


def registrar_aprobacion(
    herramienta: str,
    argumentos: dict[str, Any],
    decision: str,
    motivo: str | None = None,
) -> None:
    """Guarda en memoria la decisión humana tomada ante una interrupción."""
    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": argumentos,
        "decision": decision,
        "motivo": motivo,
        "fecha_hora": datetime.now().isoformat(),
    })


# === Esquemas de Validación (Pydantic) ===
class ArgumentosConsultaCotizacion(BaseModel):
    """Esquema para validar parámetros al consultar una cotización."""

    codigo_cotizacion: str = Field(
        description="Código identificador de la cotización, por ejemplo 'COT-101'."
    )
    incluir_detalle_items: bool = Field(
        default=False,
        description=(
            "Si es True, incluye ítems y fecha de vigencia; "
            "si es False, devuelve solo el estado general."
        ),
    )


# === Datos de Referencia del Portal ===
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


# === Herramientas ===
@tool("consultar_cotizacion_detallada", args_schema=ArgumentosConsultaCotizacion)
def consultar_cotizacion_detallada(
    codigo_cotizacion: str,
    incluir_detalle_items: bool = False,
) -> str:
    """Consulta el estado de una cotización existente y, si se solicita, su detalle."""
    cotizacion = COTIZACIONES.get(codigo_cotizacion.upper())
    if cotizacion is None:
        return f"No se encontró una cotización registrada con el código {codigo_cotizacion}."

    if not incluir_detalle_items:
        return cotizacion["estado"]

    detalle = ", ".join(cotizacion["items"])
    return f"{cotizacion['estado']} (detalle: {detalle}; {cotizacion['vigencia']})"


@tool
def calcular_subtotal_cotizacion(unidades: int, precio_unitario: float) -> str:
    """Calcula el subtotal de una línea de cotización según unidades y precio unitario."""
    if unidades <= 0 or precio_unitario < 0:
        return "Valores inválidos: las unidades deben ser mayores a 0 y el precio no negativo."
    subtotal = unidades * precio_unitario
    return f"El subtotal calculado es de ${subtotal:.2f} USD."


@tool
def aplicar_descuento_especial(codigo_cotizacion: str, porcentaje_descuento: float) -> str:
    """Aplica un descuento especial a una cotización tras ser aprobado por supervisión."""
    return (
        f"Descuento especial del {porcentaje_descuento}% aplicado y registrado "
        f"en la cotización {codigo_cotizacion.upper()}."
    )


herramientas = [
    consultar_cotizacion_detallada,
    calcular_subtotal_cotizacion,
    aplicar_descuento_especial,
]


# === Construcción del Agente con LangGraph Checkpointer + HITL Middleware ===
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
                # Solo las acciones sensibles/irreversibles pausan para revisión humana
                "aplicar_descuento_especial": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "consultar_cotizacion_detallada": False,
                "calcular_subtotal_cotizacion": False,
            },
            description_prefix="Revisión comercial requerida antes de ejecutar",
        )
    ],
    checkpointer=checkpointer,
)


def ejecutar_con_hitl(
    entrada: str,
    config: dict[str, Any],
    decision_manual: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Ejecuta un turno y, si hay interrupción HITL, reanuda con Command(resume=...)."""
    thread_id = config["configurable"]["thread_id"]
    resultado = agente.invoke(
        {"messages": [{"role": "user", "content": entrada}]},
        config=config,
    )

    while "__interrupt__" in resultado:
        interrupciones = resultado["__interrupt__"]
        for interrupcion in interrupciones:
            print("\n[PAUSA HITL] Interrupción detectada:", interrupcion.value)

        # Si no se inyecta una decisión programática, se solicita en consola
        if decision_manual is None:
            raw = input("Aprobar descuento? (a = approve / e = edit / r = reject): ").strip().lower()
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
        else:
            decision = decision_manual

        # Registrar auditoría de la decisión
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

        # Reanudar exactamente el mismo hilo con Command(resume=...)
        resultado = agente.invoke(
            Command(resume={"decisions": [decision]}),
            config=config,
        )

    registrar_traza(thread_id=thread_id, entrada=entrada, estado_resultado=resultado)
    return resultado


if __name__ == "__main__":
    # 1. Continuidad en un mismo hilo (thread_id)
    cfg_hilo_1 = {"configurable": {"thread_id": "hilo_cotizaciones_01"}}

    r1 = ejecutar_con_hitl(
        "Consulta el estado de la cotización COT-101 incluyendo su detalle.",
        cfg_hilo_1,
    )
    print("\nTurno 1:", extraer_texto(r1["messages"][-1].content))

    r2 = ejecutar_con_hitl(
        "¿Y cuál sería el subtotal de 4 unidades a 1200.0 USD?",
        cfg_hilo_1,
    )
    print("Turno 2:", extraer_texto(r2["messages"][-1].content))

    # 2. Aislamiento entre hilos distintos
    cfg_hilo_2 = {"configurable": {"thread_id": "hilo_cotizaciones_02"}}
    ejecutar_con_hitl(
        "Estoy revisando la cotización COT-102.",
        cfg_hilo_2,
    )
    r_aislado = ejecutar_con_hitl(
        "¿De qué cotización te pregunté en este hilo?",
        {"configurable": {"thread_id": "hilo_cotizaciones_03"}},
    )
    print("Aislamiento hilo_03:", extraer_texto(r_aislado["messages"][-1].content))

    # 3. Supervisión humana (HITL) aprobando un descuento especial de forma programática
    r_hitl = ejecutar_con_hitl(
        "Aplica un 12% de descuento especial a la cotización COT-101.",
        cfg_hilo_1,
        decision_manual={"type": "approve"},
    )
    print("Resultado HITL:", extraer_texto(r_hitl["messages"][-1].content))
    print("Auditoría de aprobaciones:", registro_aprobaciones)



"""Adaptación completa de tu flujo de **cotizaciones** usando el stack moderno de **LangChain v1 + LangGraph**, sin guardarte nada y manteniendo cada pieza equivalente a lo que tenías en el código anterior:

* **Agente moderno con `create_agent**` (`langchain.agents`), reemplazando `create_tool_calling_agent` + `AgentExecutor` de `langchain_classic` (que como indica el material del [Bloque 22](https://learning-pro.skillnest.com/mod/page/view.php?id=15706), se movió al paquete de compatibilidad `langchain-classic`).
* **Memoria nativa por `thread_id` con `InMemorySaver**` (`langgraph.checkpoint.memory`), en vez de `RunnableWithMessageHistory` + `InMemoryChatMessageHistory` + `session_id` (que emite aviso de deprecación en favor del `checkpointer` de LangGraph).
* **Supervisión humana (`Human-in-the-Loop`) nativa con `HumanInTheLoopMiddleware` y `Command(resume=...)**`, reemplazando el `input()` dentro de un hilo (`threading.Thread` + `queue.Queue` con `timeout`), porque en LangGraph pausar con interrupciones y reanudar con `Command(resume=...)` sobre el mismo `thread_id` es el patrón pensado para producción y no bloquea hilos de consola.
* **Trazabilidad en `.jsonl` y extracción limpia de texto** (`trazas_cotizaciones_modernas.jsonl` y auditoría de aprobaciones), preservando el registro de entradas, salidas y eventos.

### Diferencias Clave Frente a la Versión Anterior "agente_con_memoria_profe"

* **Sin `RunnableWithMessageHistory` ni `AgentExecutor`:** Todo el ciclo del agente y su memoria viven en `create_agent(..., checkpointer=InMemorySaver())`, usando `thread_id` dentro de `config["configurable"]` y el estado `{"messages": [...]}`.
* **HITL sin bloquear hilos con `input()`:** `HumanInTheLoopMiddleware` detiene la ejecución antes de ejecutar `aplicar_descuento_especial` y guarda el checkpoint en `InMemorySaver`; luego `Command(resume={"decisions": [decision]})` retoma el grafo (`approve`, `edit` o `reject`) en el mismo `thread_id`.
* **Regla práctica al usar `interrupt` / HITL:** El estado intermedio debe ser serializable y la lógica previa a una pausa no debe tener efectos secundarios duplicables al reanudar el nodo. Para producción, basta cambiar `InMemorySaver()` por un checkpointer persistente (como SQLite o Postgres).

¿Quieres que revisemos ahora el [Bloque 23](https://learning-pro.skillnest.com/mod/page/view.php?id=15707) (`Límites de autonomía y supervisión humana del agente`) o probamos el comportamiento con `edit` y `reject` en tu entorno?
"""