from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from enrutamiento_cotizaciones import construir_cadena_con_enrutamiento

def test_enrutamiento_ruta_cotizacion():
    # 1. Forzamos la categoría "cotizacion"
    paso_clasificacion_falso = MagicMock()
    paso_clasificacion_falso.return_value = "cotizacion"

    modelo_falso = MagicMock()
    modelo_falso.invoke.return_value = AIMessage(content="Propuesta de cotización generada con éxito.")

    cadena = construir_cadena_con_enrutamiento(modelo_falso, paso_clasificacion_custom=paso_clasificacion_falso)

    resultado = cadena.invoke({"mensaje": "Quiero comprar 5 unidades"})
    
    assert "cotización" in resultado

def test_enrutamiento_ruta_consulta_stock():
    # 2. Forzamos la categoría "consulta_stock"
    paso_clasificacion_falso = MagicMock()
    paso_clasificacion_falso.return_value = "consulta_stock"

    modelo_falso = MagicMock()
    modelo_falso.invoke.return_value = AIMessage(content="Stock disponible: 15 unidades en bodega.")

    cadena = construir_cadena_con_enrutamiento(modelo_falso, paso_clasificacion_custom=paso_clasificacion_falso)

    resultado = cadena.invoke({"mensaje": "¿Hay stock de servidores?"})
    
    assert "Stock disponible" in resultado

def test_enrutamiento_ruta_default_reclamo():
    # 3. Forzamos la ruta por defecto o "reclamo" (evaluando también una categoría inesperada o inventada)
    paso_clasificacion_falso = MagicMock()
    paso_clasificacion_falso.return_value = "reclamo"

    modelo_falso = MagicMock()
    modelo_falso.invoke.return_value = AIMessage(content="Lamentamos el inconveniente, lo revisaremos.")

    cadena = construir_cadena_con_enrutamiento(modelo_falso, paso_clasificacion_custom=paso_clasificacion_falso)

    resultado = cadena.invoke({"mensaje": "El precio está erróneo"})
    
    assert "inconveniente" in resultado