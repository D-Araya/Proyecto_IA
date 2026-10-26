
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURACIÓN
# ============================================================

URL_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
API_KEY = os.getenv("GEMINI_API_KEY")
REPETICIONES = 4

# Precios en USD por token, correspondientes al nivel estándar
# de pago publicado por Google al 20-10-2026.
# El precio de salida incluye los tokens de razonamiento.
MODELOS = {
    "Gemini 3.6 Flash": {
        "id": "gemini-3.6-flash",
        "precio_entrada": 0.75 / 1_000_000,
        "precio_salida": 3.75 / 1_000_000,
    },
    "Gemini 3.8 Flash": {
        "id": "gemini-3.8-flash",
        "precio_entrada": 0.75 / 1_000_000,
        "precio_salida": 3.75 / 1_000_000,
    },
    "Gemini 3.1 Flash Lite": {
        "id": "gemini-3.1-flash-lite",
        "precio_entrada": 0.25 / 1_000_000,
        "precio_salida": 1.50 / 1_000_000,
    },
}

# MISMO prompt para todos los modelos y las cuatro repeticiones.
PREGUNTA = """
Actúa como asistente inteligente de un portal administrativo de cotizaciones que utiliza 
RAG (Retrieval-Augmented Generation). El sistema recupera información desde una base de 
conocimiento con catálogos de productos, tarifas, políticas de descuentos y condiciones comerciales.
Explica cómo procesarías la siguiente solicitud de un administrador: generar una cotización 
para un cliente que solicita tres unidades de un producto, con entrega en diez días y un posible 
descuento por volumen. Describe cómo utilizarías el contexto recuperado para verificar precios 
y condiciones, calcular el importe cuando los datos sean suficientes, identificar información 
faltante y presentar una cotización clara. No inventes precios, descuentos ni condiciones 
que no estén respaldados por las fuentes recuperadas. Si falta información, indícala explícitamente.
Responde en español, en un máximo de 180 palabras, utilizando los apartados: Procedimiento, 
Validaciones y Resultado esperado.
"""


# ============================================================
# 1. CONSTRUIR LA PETICIÓN
# ============================================================

def armar_peticion(pregunta, modelo):
    if not isinstance(pregunta, str) or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    if not API_KEY:
        raise RuntimeError(
            "No se encontró GEMINI_API_KEY. "
            "Revisa tu archivo .env."
        )

    url = f"{URL_BASE}{modelo}:generateContent?key={API_KEY}"

    body = {
        "contents": [
            {
                "parts": [
                    {"text": pregunta}
                ]
            }
        ]
    }

    return url, body


# ============================================================
# 2. ENVIAR LA PETICIÓN
# ============================================================

def enviar_peticion(url, body):
    try:
        respuesta = requests.post(
            url,
            json=body,
            timeout=60
        )

    except requests.exceptions.Timeout as error:
        raise RuntimeError(
            "Se agotó el tiempo de espera."
        ) from error

    except requests.exceptions.ConnectionError as error:
        raise RuntimeError(
            "No se pudo conectar con Gemini."
        ) from error

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Error de comunicación: {error}"
        ) from error

    if not respuesta.ok:
        try:
            detalle = respuesta.json().get("error", {}).get(
                "message", respuesta.text
            )
        except ValueError:
            detalle = respuesta.text

        raise RuntimeError(
            f"HTTP {respuesta.status_code}: {detalle}"
        )

    try:
        return respuesta.json()

    except ValueError as error:
        raise RuntimeError(
            "La respuesta no contiene JSON válido."
        ) from error


# ============================================================
# 3. EXTRAER EL TEXTO GENERADO
# ============================================================

def extraer_texto(datos):
    try:
        candidatos = datos.get("candidates", [])

        if not candidatos:
            motivo = datos.get(
                "promptFeedback", {}
            ).get("blockReason", "sin candidatos")

            raise RuntimeError(
                f"Gemini no devolvió texto: {motivo}"
            )

        partes = candidatos[0]["content"]["parts"]

        textos = [
            parte["text"]
            for parte in partes
            if isinstance(parte.get("text"), str)
        ]

        if not textos:
            raise RuntimeError(
                "La respuesta no contiene texto generado."
            )

        return "\n".join(textos)

    except (KeyError, IndexError, TypeError) as error:
        raise RuntimeError(
            "No se pudo interpretar la respuesta de Gemini."
        ) from error


# ============================================================
# 4. CALCULAR EL COSTO
# ============================================================

def calcular_costo(datos, precio_entrada, precio_salida):
    uso = datos.get("usageMetadata", {})

    tokens_entrada = uso.get("promptTokenCount", 0)
    tokens_salida = uso.get("candidatesTokenCount", 0)
    tokens_razonamiento = uso.get("thoughtsTokenCount", 0)

    # Los tokens de razonamiento se cobran como salida.
    # Se suman aquí una sola vez.
    costo_entrada = tokens_entrada * precio_entrada

    costo_salida = (
        tokens_salida + tokens_razonamiento
    ) * precio_salida

    return costo_entrada + costo_salida


# ============================================================
# 5. EJECUTAR LAS CUATRO PRUEBAS DE UN MODELO
# ============================================================
RESPUESTAS_EXITOSAS_REQUERIDAS = 4
MAX_INTENTOS = 12


def probar_modelo(nombre, configuracion, pregunta):
    resultados = []
    exitosas = 0
    intento = 0

    print("\n" + "=" * 75)
    print(f"MODELO: {nombre}")
    print(f"ID: {configuracion['id']}")
    print(f"Respuestas exitosas requeridas: "
          f"{RESPUESTAS_EXITOSAS_REQUERIDAS}")
    print("=" * 75)

    while (
        exitosas < RESPUESTAS_EXITOSAS_REQUERIDAS
        and intento < MAX_INTENTOS
    ):
        intento += 1

        print(
            f"\n--- Intento {intento}/{MAX_INTENTOS} | "
            f"Respuestas exitosas: {exitosas}/"
            f"{RESPUESTAS_EXITOSAS_REQUERIDAS} ---"
        )

        try:
            url, body = armar_peticion(
                pregunta,
                configuracion["id"]
            )

            inicio = time.perf_counter()
            datos = enviar_peticion(url, body)
            latencia = time.perf_counter() - inicio

            texto = extraer_texto(datos)

            costo = calcular_costo(
                datos,
                configuracion["precio_entrada"],
                configuracion["precio_salida"]
            )

            uso = datos.get("usageMetadata", {})
            tokens_entrada = uso.get("promptTokenCount", 0)
            tokens_salida = uso.get("candidatesTokenCount", 0)
            tokens_razonamiento = uso.get("thoughtsTokenCount", 0)

            resultado = {
                "intento": intento,
                "latencia": latencia,
                "costo": costo,
                "respuesta": texto,
                "tokens_entrada": tokens_entrada,
                "tokens_salida": tokens_salida,
                "tokens_razonamiento": tokens_razonamiento,
                "error": None,
            }

            resultados.append(resultado)
            exitosas += 1

            print(f"Estado: EXITOSA ({exitosas}/"
                  f"{RESPUESTAS_EXITOSAS_REQUERIDAS})")
            print(f"Latencia: {latencia:.2f} segundos")
            print(f"Costo: ${costo:.8f} USD")
            print(f"Respuesta:\n{texto}")

        except (ValueError, RuntimeError) as error:
            print(f"Estado: FALLIDA")
            print(f"Motivo: {error}")

            resultados.append({
                "intento": intento,
                "latencia": None,
                "costo": None,
                "respuesta": None,
                "tokens_entrada": None,
                "tokens_salida": None,
                "tokens_razonamiento": None,
                "error": str(error),
            })

        # Pausa entre solicitudes para reducir la frecuencia
        # de peticiones. No garantiza evitar errores HTTP 429.
        if exitosas < RESPUESTAS_EXITOSAS_REQUERIDAS:
            if intento < MAX_INTENTOS:
                time.sleep(2)

    print(f"\nResultado final de {nombre}:")
    print(f"Intentos realizados: {intento}")
    print(f"Respuestas exitosas: {exitosas}")
    print(f"Respuestas fallidas: {intento - exitosas}")

    if exitosas < RESPUESTAS_EXITOSAS_REQUERIDAS:
        print(
            "ADVERTENCIA: No se alcanzaron las cuatro "
            "respuestas exitosas dentro del límite de intentos."
        )

    return resultados

# ============================================================
# 6. RESUMEN DE RESULTADOS Y TABLA COMPARATIVA
# ============================================================

def resumir_resultados(resultados):
    validos = [
        r for r in resultados
        if r["error"] is None
    ]

    if not validos:
        return None

    latencias = [r["latencia"] for r in validos]
    costos = [r["costo"] for r in validos]

    return {
        "exitosas": len(validos),
        "fallidas": len(resultados) - len(validos),
        "latencia_promedio": sum(latencias) / len(latencias),
        "costo_promedio": sum(costos) / len(costos),
        "costo_total": sum(costos),
        "resultados_validos": validos,
    }


def mostrar_tabla(resumenes):
    print("\n\n")
    print("=" * 110)
    print("TABLA COMPARATIVA DE MODELOS")
    print("=" * 110)

    encabezados = (
        f"{'Criterio':<38}"
        f"{'Gemini 3.6 Flash':>23}"
        f"{'Gemini 3.8 Flash':>23}"
        f"{'Gemini 3.1 Flash Lite':>26}"
    )

    print(encabezados)
    print("-" * 110)

    filas = [
        ("Costo por 1.000 tokens de entrada", "entrada"),
        ("Costo por 1.000 tokens de salida", "salida"),
    ]

    for etiqueta, tipo in filas:
        valores = []

        for config in MODELOS.values():
            clave = (
                "precio_entrada"
                if tipo == "entrada"
                else "precio_salida"
            )
            valor = config[clave] * 1000
            valores.append(f"${valor:.6f}")

        print(
            f"{etiqueta:<38}"
            f"{valores[0]:>23}"
            f"{valores[1]:>23}"
            f"{valores[2]:>26}"
        )

    print("-" * 110)

    for criterio, clave, formato in [
        ("Latencia promedio observada", "latencia_promedio", ".2f"),
        ("Costo promedio por petición", "costo_promedio", ".8f"),
        ("Costo total de pruebas exitosas", "costo_total", ".8f"),
    ]:
        valores = []

        for nombre in MODELOS:
            resumen = resumenes.get(nombre)

            if resumen is None:
                valores.append("N/D")
            else:
                valores.append(
                    f"{resumen[clave]:{formato}}"
                )

        unidad = " s" if clave == "latencia_promedio" else " USD"

        print(
            f"{criterio:<38}"
            f"{(valores[0] + unidad):>23}"
            f"{(valores[1] + unidad):>23}"
            f"{(valores[2] + unidad):>26}"
        )

    print("-" * 110)

    for nombre in MODELOS:
        resumen = resumenes.get(nombre)

        if resumen is None:
            print(f"{nombre}: sin peticiones exitosas.")
        else:
            print(
                f"{nombre}: "
                f"{resumen['exitosas']} exitosas, "
                f"{resumen['fallidas']} fallidas."
            )


# ============================================================
# 7. ORQUESTACIÓN
# ============================================================

def comparar_modelos():
    todos_los_resultados = {}
    resumenes = {}

    for nombre, configuracion in MODELOS.items():
        resultados = probar_modelo(
            nombre,
            configuracion,
            PREGUNTA
        )

        todos_los_resultados[nombre] = resultados

        resumenes[nombre] = resumir_resultados(
            resultados
        )

    mostrar_tabla(resumenes)

    return todos_los_resultados, resumenes


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    try:
        resultados, resumenes = comparar_modelos()

    except (ValueError, RuntimeError) as error:
        print(f"No se pudo completar la comparación: {error}")
