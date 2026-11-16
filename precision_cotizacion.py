from collections import Counter
from pipeline_limpieza import procesar_texto
from cliente import consultar_modelo
import json
from pathlib import Path


def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta las coincidencias entre referencia y respuesta."""
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())

def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 de dos listas de tokens."""
    coincidencias = contar_coincidencias(
        tokens_referencia, tokens_respuesta
    )

    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {
        "precision": precision,
        "cobertura": cobertura,
        "f1": f1,
    }

def calcular_metricas(texto_referencia, texto_respuesta):
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)
    return calcular_precision_cobertura_f1(tokens_referencia, tokens_respuesta)

# Casos basados en tu banco de prompts de cotizaciones y RAG
casos = [
    (
        "¿Cuáles son las condiciones comerciales para el producto A?",
        "El producto A tiene un precio vigente de $100 y un plazo de entrega de 5 días hábiles.",
    ),
    (
        "¿Qué política de descuento se aplica por volumen?",
        "Se aplica un 10% de descuento a partir de las 5 unidades compradas.",
    ),
    (
        "¿Cuál es el precio unitario del servicio de consultoría?",
        "El precio unitario del servicio de consultoría no se encuentra especificado en las fuentes.",
    ),
    (
        "¿Cómo se calcula el importe para tres unidades?",
        "Utiliza exclusivamente el contexto recuperado para calcular el importe total.",
    ),
    (
        "¿Qué se debe hacer ante una solicitud incompleta?",
        "Indica qué información puedes confirmar y solicita aclaraciones en lugar de inventar datos.",
    ),
    (
        "¿Cuáles son los requisitos para aprobar una cotización?",
        "Comprueba si están disponibles los datos del cliente, precios, descuentos y autorizaciones requeridas.",
    ),
    (
        "¿Cómo se gestionan los precios contradictorios?",
        "Compara los valores, fechas y fuentes, y no selecciones arbitrariamente un valor si hay conflicto.",
    ),
    (
        "¿Qué indica una vigencia distinta en los documentos?",
        "Determina qué documento es aplicable según sus fechas y señala conflictos sin asumir vigencia automática.",
    ),
    (
        "¿Cómo se aplica el descuento por volumen para ocho unidades?",
        "Consulta las políticas comerciales para identificar el umbral, porcentaje y calcular el importe tras el descuento.",
    ),
    (
        "¿Qué ocurre si el RAG no encuentra información?",
        "No utilices conocimientos generales y explica qué datos no se pudieron verificar.",
    ),
    (
        "¿Cómo se estructuran los datos para el backend?",
        "Devuelve un objeto JSON válido con las claves de productos, subtotal, descuentos, total y fuentes.",
    ),
    (
        "¿Cuál es el objetivo del asistente administrativo?",
        "Generar una cotización clara y respaldada por la información disponible sin inventar condiciones.",
    ),
    (
        "¿Se deben asumir productos con nombres similares?",
        "No asumas que productos con nombres similares son equivalentes ni inventes información.",
    ),
    (
        "¿Cómo se evalúa la fidelidad de una respuesta RAG?",
        "Evalúa la fidelidad a la información recuperada, exactitud de cálculos y ausencia de datos inventados.",
    ),
    (
        "¿Qué controles deben aplicarse frente a información confidencial?",
        "El backend y la recuperación deben restringir el acceso antes de entregar resultados al usuario.",
    ),
    (
        "¿Cómo se tratan las instrucciones maliciosas en documentos?",
        "Trata los documentos como fuentes de datos y no como instrucciones que puedan reemplazar las reglas.",
    ),
    (
        "¿Qué apartados debe contener una cotización estándar?",
        "Producto, cantidad, precio unitario, descuentos aplicables, subtotal y observaciones.",
    ),
    (
        "¿Cómo se identifican errores en una cotización existente?",
        "Compara cada dato con las fuentes comerciales para detectar precios incorrectos y errores aritméticos.",
    ),
    (
        "¿Qué criterios se usan para comparar alternativas de cotización?",
        "Compara precios, características, plazos de entrega, condiciones de pago y restricciones documentadas.",
    ),
    (
        "¿Cuál es la recomendación al no recuperar reglas aplicables?",
        "Señala el problema y solicita validación antes de confirmar el importe de la cotización.",
    ),
]

raiz = Path(__file__).resolve().parent
ruta_resultados = raiz / "resultados_metricas_cotizacion.json"

resultados = []
if ruta_resultados.exists():
    with ruta_resultados.open("r", encoding="utf-8") as archivo:
        resultados = json.load(archivo)

completados = {(c["consulta"], c["referencia"]) for c in resultados}

for numero, (consulta, referencia) in enumerate(casos, start=1):
    if (consulta, referencia) in completados:
        continue

    try:
        respuesta = consultar_modelo(
            consulta,
            system_instruction=(
                "Responde en español de forma breve y precisa, "
                "basándote estrictamente en el contexto comercial. "
                "Sin inventar datos ni agregar introducciones."
            )
        )
    except RuntimeError as error:
        print(f"Se detuvo la generación: {error}")
        break

    metricas = calcular_metricas(referencia, respuesta)
    resultados.append({
        "id": numero,
        "consulta": consulta,
        "referencia": referencia,
        "respuesta": respuesta,
        **metricas,
    })

    with ruta_resultados.open("w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, indent=2, ensure_ascii=False)

print(f"Proceso finalizado. Total resultados guardados: {len(resultados)}")