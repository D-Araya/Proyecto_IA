import time
from typing import Callable, Any

from src.consumir_gemini import armar_peticion, extraer_texto, enviar_peticion

def con_reintento(
    funcion: Callable[..., Any],
    intentos: int = 3,
    espera_segundos: int = 2
) -> Any:

    for intento in range(intentos):
        try:
            return funcion()
        except TimeoutError as e:
            if intento == intentos-1:
                raise e
            print(f"Intento {intento+1} de {intentos} falló por limites de uso/servidor Reintentando...")
            time.sleep(espera_segundos)



"""

for intento in range(1, intentos + 1):
    try:
        return funcion()
    except TimeoutError as e:
        if intento == intentos:
            raise
        print(f"Intento {intento} de {intentos} falló. Reintentando en {espera_segundos} segundos...")
        time.sleep(espera_segundos)

"""