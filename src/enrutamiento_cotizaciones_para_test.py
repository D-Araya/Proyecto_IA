from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnablePassthrough, RunnableLambda
import logging

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="error_cotizaciones.log",
    filemode="a",
    encoding="utf-8",
    force=True
)
logger = logging.getLogger(__name__)

load_dotenv()

def construir_paso_clasificacion(modelo):
    """Construye el paso de clasificación normalizado."""
    plantilla = PromptTemplate.from_template(
        "Clasifica el siguiente mensaje de un portal de cotizaciones en una sola palabra: "
        "cotizacion, consulta_stock o reclamo. Responde solo con esa palabra.\n\n{mensaje}"
    )
    return plantilla | modelo | StrOutputParser() | (lambda texto: texto.strip().lower())

def construir_cadena_con_enrutamiento(modelo, paso_clasificacion_custom=None):
    """
    Construye la cadena completa con enrutamiento condicional.
    Permite inyectar un paso de clasificación personalizado (útil para mocks en tests).
    """
    paso_clasificacion = paso_clasificacion_custom or construir_paso_clasificacion(modelo)

    cadena_cotizacion = (
        PromptTemplate.from_template("Redacta una cotización comercial formal para:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    cadena_stock = (
        PromptTemplate.from_template("Responde a esta consulta sobre stock y condiciones comerciales:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    cadena_reclamo = (
        PromptTemplate.from_template("Responde a esta incidencia o reclamo comercial con empatía:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    bifurcacion = RunnableBranch(
        (lambda x: x["clasificacion"] == "cotizacion", cadena_cotizacion),
        (lambda x: x["clasificacion"] == "consulta_stock", cadena_stock),
        cadena_reclamo  # Ruta por defecto
    )

    return RunnablePassthrough.assign(clasificacion=paso_clasificacion) | bifurcacion


if __name__ == "__main__":
    modelo_real = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    cadena_robusta = construir_cadena_con_enrutamiento(modelo_real)
    print(cadena_robusta.invoke({"mensaje": "Necesito cotizar 3 servidores rack."}))



""" # Reporte Técnico: Adaptación de `enrutamiento_cotizaciones.py` para Testing

## 1. El Problema del Acoplamiento y la Ejecución Global (Hardcoding)
En las versiones iniciales de nuestros scripts de [LangChain](https://learning-pro.skillnest.com/mod/page/view.php?id=15658), todos los componentes se construían de manera fija y directa en el ámbito global del archivo:
* El modelo (`ChatGoogleGenerativeAI`) se instanciaba automáticamente apenas se importaba el módulo.
* Las cadenas, plantillas y ramas (`RunnableBranch`) estaban acopladas rígidamente a ese modelo global.

**¿Por qué esto afectaba a las pruebas unitarias?**
Cuando ejecutas `pytest`, el framework importa los archivos de código para buscar funciones de prueba. Si el script tiene conexiones y llamadas estructuradas globalmente, intentará comunicarse con la API real de Gemini de inmediato, consumiendo tokens, dependiendo de una conexión a internet activa y volviendo los tests lentos e impredecibles.

---

## 2. La Solución: Inyección de Dependencias
Para resolverlo, transformamos el script encapsulando la lógica dentro de funciones constructoras como `construir_paso_clasificacion(modelo)` y `construir_cadena_con_enrutamiento(modelo, paso_clasificacion_custom)`.

* **Cero llamadas automáticas al importar:** Al modularizarlo, el script ya no ejecuta nada al ser importado por `pytest`[cite: 1]. La construcción de la cadena solo ocurre cuando se le llama explícitamente pasando los componentes como argumentos.
* **Uso de Mocks:** En el archivo de pruebas (`test_enrutamiento_cotizaciones.py`), esto nos permite pasar objetos simulados (`MagicMock`) en lugar del modelo real. Las pruebas corren localmente en milisegundos, de forma totalmente determinista y sin gastar recursos de la API.

---

## 3. Control Explícito del Clasificador en las Pruebas
Uno de los mayores retos al probar flujos condicionales con `RunnableBranch`[cite: 1] es que la ruta elegida depende del resultado del **paso de clasificación**. 
Si dejábamos que el clasificador utilizara el modelo real, el resultado de la categoría podría variar o requerir que el LLM devuelva exactamente la palabra esperada en cada ejecución.

Para solucionarlo, añadimos un parámetro opcional en el constructor:
```python
paso_clasificacion = paso_clasificacion_custom or construir_paso_clasificacion(modelo) """