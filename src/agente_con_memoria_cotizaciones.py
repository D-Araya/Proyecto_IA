
from datetime import datetime, timezone
import json
import queue
import threading
from dotenv import load_dotenv
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

# === Configuraciones e Inicializaciones ===
load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

# === Persistencia y Análisis de Trazabilidad ===
def registrar_traza(
    session_id: str,
    entrada: str,
    resultado: dict,
    ruta_archivo: str = "trazas_cotizaciones.jsonl",
) -> None:
    """Registra la traza de ejecución, herramientas invocadas y respuesta final."""
    historial_actual = obtener_historial(session_id).messages
    registro = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": session_id,
        "mensajes_en_historial": len(historial_actual),
        "entrada": entrada,
        "acciones": [
            {
                "herramienta": accion.tool,
                "argumentos": accion.tool_input,
                "observacion": observacion,
            }
            for accion, observacion in resultado.get("intermediate_steps", [])
        ],
        "respuesta_final": resultado.get("output", ""),
    }

    with open(ruta_archivo, "a", encoding="utf-8") as archivo:
        archivo.write(json.dumps(registro, ensure_ascii=False) + "\n")


# === Auditoría / Human in the Loop ===
registro_aprobaciones = []


def esperar_aprobacion(mensaje: str, tiempo_limite_segundos: int = 15) -> bool:
    """Solicita aprobación humana con tiempo límite para evitar bloqueos indefinidos."""
    cola_respuesta = queue.Queue()

    def pedir_entrada():
        try:
            texto = input(mensaje)
            cola_respuesta.put(texto.strip().lower())
        except (EOFError, KeyboardInterrupt):
            cola_respuesta.put("")

    hilo = threading.Thread(target=pedir_entrada, daemon=True)
    hilo.start()

    try:
        respuesta = cola_respuesta.get(timeout=tiempo_limite_segundos)
        return respuesta == "s"
    except queue.Empty:
        print("Tiempo de espera agotado. Acción denegada por timeout.")
        return False


def registrar_aprobacion(
    herramienta: str,
    argumentos: dict,
    aprobado: bool,
) -> None:
    registro_aprobaciones.append({
        "herramienta": herramienta,
        "argumentos": argumentos,
        "aprobado": aprobado,
        "fecha_hora": datetime.now().isoformat(),
    })


# === Esquemas de Validación ===
class ArgumentosConsultaCotizacion(BaseModel):
    """Esquema para validar parámetros al consultar el estado de una cotización."""

    codigo_cotizacion: str = Field(
        description="Código identificador de la cotización, por ejemplo 'COT-101'."
    )
    incluir_detalle_items: bool = Field(
        default=False,
        description=(
            "Si es True, incluye el detalle de ítems y vigencia; "
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
@tool(args_schema=ArgumentosConsultaCotizacion)
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
    """Aplica un descuento especial a una cotización. Requiere supervisión humana previa."""
    mensaje = (
        f"[SUPERVISIÓN HUMANA REQUERIDA] Aplicar {porcentaje_descuento}% de descuento "
        f"a la cotización {codigo_cotizacion}. ¿Desea aprobar? (s/n): "
    )
    aprobado = esperar_aprobacion(mensaje, tiempo_limite_segundos=15)
    registrar_aprobacion(
        herramienta="aplicar_descuento_especial",
        argumentos={
            "codigo_cotizacion": codigo_cotizacion,
            "porcentaje_descuento": porcentaje_descuento,
        },
        aprobado=aprobado,
    )

    if not aprobado:
        return "Descuento especial no aprobado por el supervisor o cancelado por timeout."

    return f"Descuento del {porcentaje_descuento}% aprobado y aplicado a {codigo_cotizacion}."


herramientas = [
    consultar_cotizacion_detallada,
    calcular_subtotal_cotizacion,
    aplicar_descuento_especial,
]

# === Gestión de Historial en Memoria ===
historiales: dict[str, InMemoryChatMessageHistory] = {}


def obtener_historial(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in historiales:
        historiales[session_id] = InMemoryChatMessageHistory()
    return historiales[session_id]


def cerrar_sesion(session_id: str) -> None:
    """Limpia el historial de una sesión cuando finaliza o se reinicia una prueba."""
    historiales.pop(session_id, None)


# === Construcción del Agente ===
prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente administrativo para un portal de cotizaciones. "
        "Usa las herramientas disponibles para consultar cotizaciones, calcular subtotales "
        "o gestionar descuentos especiales con supervisión humana.",
    ),
    MessagesPlaceholder("chat_history"),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=True,
    return_intermediate_steps=True,
)

limpiar_salida = RunnableLambda(
    lambda d: {
        **d,
        "output": (
            d["output"][0]["text"]
            if isinstance(d.get("output"), list) and d["output"]
            else d.get("output")
        ),
    }
)

cadena_agente = ejecutor_agente | limpiar_salida

agente_con_memoria = RunnableWithMessageHistory(
    cadena_agente,
    obtener_historial,
    input_messages_key="entrada",
    history_messages_key="chat_history",
    output_messages_key="output",
)

# === Ejecución ===
if __name__ == "__main__":
# === Verificación de continuidad en una misma sesión ===
    config_sesion = {"configurable": {"session_id": "admin_cotizaciones_01"}}

    turno_1 = "Consulta el estado de la cotización COT-101 incluyendo su detalle."
    res_1 = agente_con_memoria.invoke({"entrada": turno_1}, config_sesion)
    print("Turno 1:", res_1["output"])
    registrar_traza(config_sesion["configurable"]["session_id"], turno_1, res_1)

    turno_2 = "¿Y cuál sería el subtotal de 4 unidades a 1200.0 USD?"
    res_2 = agente_con_memoria.invoke({"entrada": turno_2}, config_sesion)
    print("Turno 2:", res_2["output"])
    registrar_traza(config_sesion["configurable"]["session_id"], turno_2, res_2)

    print(
        "Mensajes acumulados en sesión:",
        len(obtener_historial("admin_cotizaciones_01").messages),
    )

    # === Verificación de aislamiento entre dos sesiones distintas ===
    config_cliente_1 = {"configurable": {"session_id": "cliente_1"}}
    config_cliente_2 = {"configurable": {"session_id": "cliente_2"}}

    agente_con_memoria.invoke(
        {"entrada": "Estoy consultando por la cotización COT-101."},
        config_cliente_1,
    )
    res_aislamiento = agente_con_memoria.invoke(
        {"entrada": "¿De qué cotización te pregunté?"},
        config_cliente_2,
    )
    print("Aislamiento cliente_2:", res_aislamiento["output"])
    print("Mensajes cliente_1:", len(obtener_historial("cliente_1").messages))
    print("Mensajes cliente_2:", len(obtener_historial("cliente_2").messages))

    # Limpieza de sesiones de prueba
    cerrar_sesion("admin_cotizaciones_01")
    cerrar_sesion("cliente_1")
    cerrar_sesion("cliente_2")


"""
¡Excelente código el que comparte tu profesora! Ya reúne las piezas clave de [Herramienta personalizada e integración al agente (Bloque 22) / Que tu agente recuerde: memoria entre interacciones](https://learning-pro.skillnest.com/mod/page/view.php?id=15705&forceview=1): esquema tipado con `BaseModel` y `Field`, herramientas `@tool`, `MessagesPlaceholder("chat_history")` antes de `("human", "{entrada}")` y `MessagesPlaceholder("agent_scratchpad")` al final, `RunnableWithMessageHistory` con `InMemoryChatMessageHistory`, trazabilidad en `.jsonl` y supervisión humana (`Human-in-the-Loop`) con timeout.

Para llevar esta misma arquitectura a tu **portal de cotizaciones**, conviene trasladar los conceptos de logística a tu dominio comercial (cotizaciones, stock y condiciones de descuento/aprobación) sin perder el diseño modular del script.

---

### 1. Mapeo de Piezas al Proyecto de Cotizaciones

| Componente del Script Base | Adaptación a Cotizaciones |
| --- | --- |
| `ArgumentosConsultaEnvio` (`numero_seguimiento`, `incluir_historial`) | `ArgumentosConsultaCotizacion` (`codigo_cotizacion`, `incluir_detalle_items`) |
| `consultar_estado_envio_detallado` | `consultar_cotizacion_detallada` (estado de cotización, ítems y vigencia) |
| `calcular_costo_envio` | `calcular_subtotal_cotizacion` (cálculo de monto base según unidades y precio unitario) |
| `generar_reembolso` + `esperar_aprobacion` | `aplicar_descuento_especial` (acción sensible/irreversible que exige aprobación humana con timeout) |
| `registrar_traza` (`trazas_agente.jsonl`) | `registrar_traza` (`trazas_cotizaciones.jsonl` con `session_id`, `entrada`, `acciones` y `respuesta_final`) |
| `RunnableWithMessageHistory` + `limpiar_salida` | Mantiene el orden `chat_history` → `human` → `agent_scratchpad` y normaliza `output` cuando viene en lista |


### 3. Puntos de Control al Integrarlo

* **Claves alineadas:** `input_messages_key="entrada"` coincide con `("human", "{entrada}")` y `history_messages_key="chat_history"` coincide con `MessagesPlaceholder("chat_history")`.


* **Aislamiento por `session_id`:** Cada sesión mantiene su propio `InMemoryChatMessageHistory`, por lo que conviene usar `cerrar_sesion(session_id)` al terminar pruebas para no acumular sesiones en memoria.


* **Costo y contexto creciente:** Cada turno reenvía el historial acumulado, por lo que registrar `len(obtener_historial(session_id).messages)` en `trazas_cotizaciones.jsonl` te ayuda a auditar el crecimiento del contexto.



¿Quieres que revisemos luego la siguiente unidad (**Bloque 23: Límites de autonomía y supervisión humana del agente**) o probamos antes algún flujo con aprobación de descuento en tu entorno?


-----------------------------

¡Sí, este codigo te sirve perfectamente como base! A nivel de estructura y compatibilidad técnica con tu entorno y el [Bloque 22](https://learning-pro.skillnest.com/mod/page/view.php?id=15706) ([Tu herramienta personalizada, ya construida e integrada](https://learning-pro.skillnest.com/mod/page/view.php?id=15706)):

* **Imports y paquetes correctos:** Usa `langchain_classic.agents` para `AgentExecutor` y `create_tool_calling_agent`, junto con `pydantic`, `langchain_core` y `langchain_google_genai`, alineado con lo que pide la lección de prerrequisitos de [Skillnest](https://learning-pro.skillnest.com/mod/page/view.php?id=15706).
* **Esquema y herramienta multiparámetro:** `ArgumentosConsultaCotizacion` valida `codigo_cotizacion` e `incluir_detalle_items` (con valor por defecto `False`), y `consultar_cotizacion_detallada` utiliza ambos parámetros según se pida o no el detalle.
* **Orden del prompt y memoria:** Coloca `MessagesPlaceholder("chat_history")` antes de `("human", "{entrada}")` y `MessagesPlaceholder("agent_scratchpad")` al final, conectado a `RunnableWithMessageHistory` con `InMemoryChatMessageHistory` e `input_messages_key="entrada"` / `history_messages_key="chat_history"`.

---

### Dos ajustes prácticos antes de darlo por cerrado en el Bloque 22

1. **Alineación con el checklist de cierre de la lección:** En [Tu herramienta personalizada, ya construida e integrada](https://learning-pro.skillnest.com/mod/page/view.php?id=15706) se pide verificar explícitamente dos cosas:
* Una conversación de al menos dos turnos con el mismo `session_id` (ya la tienes en `admin_cotizaciones_01`).
* Que dos `session_id` distintos no mezclen su historial (por ejemplo, probando `cliente_1` y `cliente_2` en el bloque `if __name__ == "__main__":`).


2. **Aislamiento de la supervisión humana (`Human-in-the-Loop`):** Tu función `aplicar_descuento_especial` con `esperar_aprobacion` y `registrar_traza` viene del código de clase y adelanta temas de [Memoria de contexto y límites de autonomía del agente (Bloque 23) / Límites de autonomía y supervisión humana del agente](https://learning-pro.skillnest.com/mod/page/view.php?id=15707). Funciona en consola interactiva, pero si ejecutas el script de forma no interactiva (o en pruebas automáticas), `esperar_aprobacion` esperará hasta el `timeout` de **15 segundos** y denegará por tiempo agotado; si solo quieres validar el cierre del **Bloque 22**, te conviene probar primero los turnos de consulta y cálculo sin disparar pausas de consola.

¿Quieres que agreguemos al final del bloque `if __name__ == "__main__":` la prueba rápida de aislamiento entre dos sesiones (`cliente_1` y `cliente_2`) para completar el checklist del **Bloque 22**?



"""