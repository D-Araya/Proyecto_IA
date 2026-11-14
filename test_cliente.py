import pytest
from unittest.mock import patch, Mock

import cliente
from cliente import (
    enviar_peticion,
    con_reintento,
    registrar_costo,
    consultar_modelo,
)


@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    """
    Fixture que se ejecuta automáticamente antes de cada prueba (autouse=True).
    Reinicia el acumulador global de costo a cero para evitar que una prueba
    contamine el estado de la siguiente.
    """
    cliente.costo_total_sesion = 0.0
    yield


# ==============================================================================
# 1. Pruebas para enviar_peticion
# ==============================================================================

def test_enviar_peticion_credencial_invalida():
    """
    Verifica que un código de estado 401 (o 403) lance ValueError
    indicando problema de credenciales o permisos.
    """
    respuesta_falsa = Mock(status_code=401)
    
    with patch("consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})


def test_enviar_peticion_limite_de_uso():
    """
    Verifica que un código de estado 429 (límite excedido) o 500+ (error del servidor)
    lance TimeoutError para que el cliente pueda reintentar.
    """
    respuesta_falsa = Mock(status_code=429)
    
    with patch("consumir_gemini.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})


def test_enviar_peticion_exito():
    """
    Verifica que una respuesta exitosa (HTTP 200) devuelva el diccionario JSON tal cual.
    """
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {"texto": "respuesta simulada"}
    
    with patch("consumir_gemini.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion("https://ejemplo.invalid", {"pregunta": "test"})
        
    assert resultado == {"texto": "respuesta simulada"}


# ==============================================================================
# 2. Pruebas para con_reintento
# ==============================================================================

def test_con_reintento_agota_intentos():
    """
    Verifica que cuando la función siempre lanza TimeoutError, con_reintento
    agote todos los intentos configurados y finalmente deje propagarse el TimeoutError original.
    Se mockea time.sleep para que la prueba se ejecute al instante.
    """
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep"):
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3)


def test_con_reintento_no_reintenta_value_error():
    """
    Verifica que con_reintento NO reintente ante excepciones distintas a TimeoutError
    (como ValueError por credenciales inválidas). La excepción debe propagarse de inmediato
    sin llamar a time.sleep ni realizar un segundo intento.
    """
    contador = {"intentos": 0}

    def falla_inmediato():
        contador["intentos"] += 1
        raise ValueError("credencial inválida")

    with patch("cliente.time.sleep") as mock_sleep:
        with pytest.raises(ValueError):
            con_reintento(falla_inmediato, intentos=3)

    assert contador["intentos"] == 1
    mock_sleep.assert_not_called()


# ==============================================================================
# 3. Pruebas para registrar_costo
# ==============================================================================

def test_registrar_costo_acumula():
    """
    Verifica que calcular el costo a partir de los tokens de una respuesta
    calcule el valor esperado y lo sume al acumulador global costo_total_sesion.
    """
    respuesta_falsa = {"usageMetadata": {"totalTokenCount": 1000}}
    costo = registrar_costo(respuesta_falsa)

    assert costo == cliente.COSTO_POR_1000_TOKENS
    assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS


# ==============================================================================
# 4. Pruebas para consultar_modelo
# ==============================================================================

def test_consultar_modelo_convierte_error():
    """
    Verifica que cuando con_reintento agota los reintentos y lanza TimeoutError,
    consultar_modelo capture esa excepción técnica y la transforme en un RuntimeError
    con un mensaje comprensible para el usuario.
    """
    error_simulado = TimeoutError("simulado")

    with patch("cliente.con_reintento", side_effect=error_simulado):
        with pytest.raises(RuntimeError):
            consultar_modelo("pregunta de prueba")

















#    necesito que el UX/UI de los 3 portales sea consistente entre ellos, ya que el portal del cliente ligeramente diferente al portal del admin y del asesor