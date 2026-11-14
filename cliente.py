import time
import random
import os
from typing import Callable, Any
from src.consumir_gemini import armar_peticion, extraer_texto, enviar_peticion

MODELO = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

def con_reintento(
    funcion: Callable[[], Any], 
    intentos: int = 3, 
    espera_base: float = 2, 
    espera_maxima: float = 30,
) -> Any:
    """
    Ejecuta una función implementando el patrón de resiliencia 'Exponential Backoff con Jitter'.
    Si la función lanza un TimeoutError (por ejemplo, saturación de la API o caída de red), 
    reintenta la llamada aumentando el tiempo de espera de forma exponencial.
    
    :param funcion: Función o lambda sin argumentos que se desea ejecutar.
    :param intentos: Cantidad máxima de intentos permitidos antes de rendirse.
    :param espera_base: Tiempo inicial de espera en segundos para el primer reintento.
    :param espera_maxima: Límite superior en segundos para que la espera no crezca indefinidamente.
    :return: El resultado retornado por la ejecución exitosa de 'funcion'.
    """
    # Itera desde el intento 1 hasta el número máximo configurado
    for intento in range(1, intentos + 1):
        try:
            # 1. Intenta ejecutar la función objetivo
            # Si tiene éxito, retorna el resultado de inmediato y termina el bucle
            return funcion()
        except TimeoutError:
            # 2. Si falló por tiempo de espera y ya estamos en el último intento,
            # no esperamos más y propagamos la excepción (raise) hacia afuera
            if intento == intentos:
                raise
            
            # 3. Retroceso Exponencial (Exponential Backoff):
            # Calcula el tiempo multiplicando por potencias de 2 en cada intento fallido:
            # Intento 1: 2 * (2^0) = 2s
            # Intento 2: 2 * (2^1) = 4s
            # Intento 3: 2 * (2^2) = 8s ...
            # min(...) asegura que la espera nunca supere el tope de 'espera_maxima'
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            
            # 4. Jitter (Variación aleatoria):
            # Suma un pequeño valor aleatorio (entre 0% y 10% del tiempo de espera)
            # Evita el 'Thundering Herd Problem' (que miles de clientes reintenten en el mismo milisegundo)
            espera_con_jitter = espera + random.uniform(0, espera * 0.1)
            
            # 5. Notifica en consola el fallo y la pausa estimada
            print(f"Intento {intento} de {intentos} falló. Reintentando en {espera_con_jitter:.1f}s...")
            
            # 6. Pausa la ejecución del programa antes de comenzar el siguiente intento
            time.sleep(espera_con_jitter)


# ==========================================
# CONFIGURACIÓN DE TARIFAS (Gemini 3.1 Flash Lite)
# ==========================================
# Los proveedores de IA cobran precios diferentes dependiendo de si el token 
# es enviado por ti (entrada/prompt) o generado por el modelo (salida/respuesta).
# Por eso es obligatorio separarlos en lugar de usar un único total global.
COSTO_ENTRADA_POR_MILLON = 0.25  # $0.25 USD por cada 1,000,000 tokens de entrada
COSTO_SALIDA_POR_MILLON = 1.50   # $1.50 USD por cada 1,000,000 tokens de salida
COSTO_POR_1000_TOKENS = 0.00015  # Tarifa base referencial por cada 1,000 tokens

# Variable global para llevar el acumulado de la sesión actual
costo_total_sesion = 0.0

def registrar_costo(respuesta: dict) -> float:
    """
    Calcula, acumula y muestra el costo en USD de una llamada a la API 
    basándose en el uso real de tokens reportado en la respuesta.
    """
    global costo_total_sesion
    
    # Extraemos el diccionario de metadatos que devuelve la API
    uso = respuesta.get("usageMetadata", {})
    
    # 1. Separamos los contadores (crucial porque tienen precios distintos)
    tokens_entrada = uso.get("promptTokenCount", 0)     # Lo que tú le envías al modelo
    tokens_salida = uso.get("candidatesTokenCount", 0)  # Lo que el modelo te responde
    total_tokens = uso.get("totalTokenCount", 0)        # La suma de ambos (o total reportado)
    
    # 2. Cálculo de costo:
    # Si la respuesta incluye el desglose de entrada y salida, usamos tarifas diferenciadas.
    # Si solo incluye totalTokenCount (como en respuestas estándar o pruebas), usamos la tarifa por cada 1,000 tokens.
    if tokens_entrada > 0 or tokens_salida > 0:
        costo_entrada = (tokens_entrada / 1_000_000) * COSTO_ENTRADA_POR_MILLON
        costo_salida = (tokens_salida / 1_000_000) * COSTO_SALIDA_POR_MILLON
        costo_estimado = costo_entrada + costo_salida
    else:
        costo_estimado = (total_tokens / 1000) * COSTO_POR_1000_TOKENS
    
    # 3. Acumulamos en la sesión global
    costo_total_sesion += costo_estimado
    
    # 4. Mostramos el desglose en consola para monitoreo
    print(
        f"Operación: {total_tokens} tokens "
        f"(Entrada: {tokens_entrada}, Salida: {tokens_salida}) | "
        f"Costo llamada: ${costo_estimado:.6f} USD | "
        f"Acumulado sesión: ${costo_total_sesion:.6f} USD"
    )
    
    return costo_estimado
 

def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    """
    Función orquestadora principal para interactuar con el modelo de Gemini.
    Une todos los pasos: armado de solicitud, envío resiliente con reintentos,
    registro de consumo/costos en USD y extracción limpia del texto final.

    :param pregunta: El mensaje o consulta que el usuario le hace al modelo.
    :param system_instruction: (Opcional) El rol, contexto o comportamiento que debe adoptar el modelo.
    :return: El texto de la respuesta generado por el modelo.
    """
    # 1. Prepara la URL con el endpoint/API key y el cuerpo JSON (body) con los parámetros
    url, cuerpo = armar_peticion(pregunta, system_instruction)
    
    try:
        # 2. Envía la solicitud HTTP dentro de la función de resiliencia 'con_reintento'.
        # Se usa 'lambda:' (función anónima sin argumentos) para pasar la llamada retrasada en el tiempo;
        # así 'con_reintento' decide cuándo y cuántas veces ejecutarla según falle o tenga éxito.
        respuesta = con_reintento(lambda: enviar_peticion(url, cuerpo))
    except TimeoutError:
        # 3. Si se agotaron todos los reintentos y el servicio siguió sin responder,
        # convertimos el TimeoutError técnico en un mensaje amigable para el usuario.
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    
    # 4. Analiza los metadatos de tokens en la respuesta (usageMetadata), calcula el costo y lo acumula
    registrar_costo(respuesta)
    
    # 5. Parsea la estructura JSON de la respuesta de Google y extrae únicamente el texto final
    return extraer_texto(respuesta)
 
 
# ==========================================
# PUNTO DE ENTRADA / PRUEBA DEL ARCHIVO
# ==========================================
# '__name__ == "__main__"' asegura que este bloque SOLO se ejecute si corres 'py .\cliente.py' directamente.
# Si otro archivo importa 'consultar_modelo' desde este archivo, este código de prueba no se ejecutará.
if __name__ == "__main__":
    """  
    # Realizamos una consulta de prueba pasando la pregunta y definiendo un rol de sistema
    resultado = consultar_modelo(
        pregunta="¿Cuál es la capital de Chile?", 
        system_instruction="Eres un experto en geografía"
    )
    # Mostramos en consola la respuesta generada por el modelo
    print(resultado)

"""    
    for i in range(10):
        try:
            respuesta = consultar_modelo(f"Pregunta de prueba número {i}")
            print(f"Respuesta {i} : {respuesta[:40]}...")
        except RuntimeError as error:
            print(f"Respuesta {i} falló definitivamente: {error}")
    
    print(f"Costo total del ensayo: ${costo_total_sesion:.5f}")
