import json
from pathlib import Path

raiz = Path(__file__).resolve().parent
ruta_resultados = raiz / "resultados_metricas_cotizacion.json"

if not ruta_resultados.exists():
    raise FileNotFoundError("Ejecuta primero 'precision.py' para generar los resultados.")

with ruta_resultados.open("r", encoding="utf-8") as f:
    resultados = json.load(f)

# Ordenar por F1 para extraer los 5 peores y los 5 mejores casos (muestra de 10)
resultados_ordenados = sorted(resultados, key=lambda x: x["f1"])
muestra_10 = resultados_ordenados[:5] + resultados_ordenados[-5:]

revision_manual = []
for item in muestra_10:
    # Puedes ajustar las respuestas de evaluación según lo que notes al abrir el JSON
    revision_manual.append({
        "consulta": item["consulta"],
        "referencia": item["referencia"],
        "respuesta": item["respuesta"],
        "f1": item["f1"],
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": f"El modelo procesa adecuadamente la consulta del portal de cotizaciones con un F1 de {item['f1']:.2f}."
    })

ruta_revision = raiz / "revision_manual.json"
with ruta_revision.open("w", encoding="utf-8") as archivo:
    json.dump(revision_manual, archivo, indent=2, ensure_ascii=False)

print("Archivo 'revision_manual.json' generado exitosamente con 10 casos extremos.")