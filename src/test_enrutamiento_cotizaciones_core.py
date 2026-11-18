from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from enrutamiento_cotizaciones_core import construir_cadena_comercial_robusta, procesar_mensaje_comercial_seguro

def test_enrutamiento_ruta_cotizacion():
    # 1. Forzamos clasificación como "cotizacion"
    paso_clasificacion_falso = MagicMock()
    paso_clasificacion_falso.return_value = "cotizacion"

    # 2. Usamos RunnableLambda en lugar de MagicMock para simular la respuesta limpia del modelo
    modelo_falso = RunnableLambda(lambda x: AIMessage(content="Propuesta comercial generada correctamente."))

    cadena = construir_cadena_comercial_robusta(modelo_falso, paso_clasificacion_custom=paso_clasificacion_falso)

    resultado = cadena.invoke({"mensaje": "Quiero comprar 5 servidores"})
    assert "Propuesta comercial" in resultado

def test_fallback_en_ruta_especifica():
    """Verifica que si una ruta específica falla, se active su fallback local (Bloque 20)."""
    paso_clasificacion_falso = MagicMock()
    paso_clasificacion_falso.return_value = "reclamo"

    # Simulamos que la cadena de reclamos falla lanzando una excepción
    cadena_queja_rota = RunnableLambda(lambda x: (_ for _ in()).throw(ConnectionError("Fallo de API simulado")))

    modelo_falso = MagicMock()
    
    cadena = construir_cadena_comercial_robusta(
        modelo_falso, 
        paso_clasificacion_custom=paso_clasificacion_falso, 
        cadena_reclamo_custom=cadena_queja_rota.with_fallbacks([RunnableLambda(lambda x: "Fallback de reclamo activado con éxito")])
    )

    resultado = cadena.invoke({"mensaje": "El precio está erróneo"})
    assert "Fallback de reclamo" in resultado

def test_try_except_global_en_fallo_critico():
    """Verifica que el try/except global capture errores inesperados previos al enrutamiento[cite: 1]."""
    cadena_rota = MagicMock()
    cadena_rota.invoke.side_effect = RuntimeError("Fallo crítico general")

    resultado = procesar_mensaje_comercial_seguro(cadena_rota, "Mensaje de prueba")
    assert "No pudimos procesar su solicitud" in resultado


"""
# Análisis de Resultados: Ejecución Principal y Logs del Sistema

## 1. ¿Por qué se generó esa propuesta comercial tan completa en la consola?
Tu script ejecutó con éxito el modelo real de Gemini (`gemini-3.6-flash`) utilizando el mensaje de prueba:
> *"Necesito cotizar urgentemente 3 unidades del Servidor Rack."*

El sistema hizo exactamente lo que le pedimos:
* **Clasificación:** Pasó el mensaje por el clasificador, el cual determinó correctamente que se trataba de una `"cotizacion"`.
* **Enrutamiento:** El enrutador (`RunnableBranch`) lo derivó de forma limpia hacia la `cadena_cotizacion`.
* **Generación:** El modelo procesó el prompt comercial y generó una respuesta sumamente detallada, profesional y estructurada en Markdown (con especificaciones técnicas, formato de tabla para precios y términos comerciales) lista para un entorno real de negocio.

---

## 2. ¿Qué significan las líneas en `error_cotizaciones_core.log`?
Las líneas que ves en tu archivo de logs:

```text
2026-11-18 01:56:00 [ERROR] enrutamiento_cotizaciones_core: Error crítico procesando mensaje comercial: Fallo crítico general
no corresponden a un error actual de tu ejecución exitosa. Esas entradas se registraron previamente mientras ejecutabas y probabas la función de 
pruebas unitarias (test_try_except_global_en_fallo_critico), la cual provoca a propósito un fallo crítico general para verificar que el 
bloque try/except global (procesar_mensaje_comercial_seguro) capture la excepción correctamente y no tumbe la aplicación.
El hecho de que esas líneas estén ahí demuestra que el sistema de logging está funcionando exactamente como se diseñó, registrando los fallos simulados durante los tests.
"""