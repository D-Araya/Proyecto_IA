from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from cadena_tres_pasos_cotizacion import construir_cadena

def test_cadena_conecta_los_tres_pasos():
    # Creamos un mock con side_effect para simular las 3 respuestas secuenciales
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="Producto: Servidor Rack\nCantidad: 5\nPlazo: Próximo viernes\nCondición: Pago a 30 días"),
        AIMessage(content="Viabilidad: Stock disponible y despacho factible en el plazo indicado."),
        AIMessage(content="# Propuesta de Cotización\n\n- **Producto:** Servidor Rack Enterprise (x5)\n- **Condiciones:** Pago a 30 días\n- **Estado:** Viable para despacho")
    ]
    
    cadena = construir_cadena(modelo_falso)
    
    solicitud_prueba = "Solicitud de prueba simulada para la cotización"
    resultado = cadena.invoke({"solicitud": solicitud_prueba})
    
    # Verificaciones exigidas en la rúbrica del Bloque 18
    assert modelo_falso.call_count == 3
    assert "Propuesta de Cotización" in resultado or "Servidor Rack" in resultado