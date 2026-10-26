
"""Banco de prompts para el portal administrativo de cotizaciones."""

BANCO_DE_PROMPT = [
    {
        "nombre": "generar_cotizacion",
        "system_instruction": (
            "Eres un asistente para un portal administrativo de cotizaciones. "
            "Genera una cotización utilizando los datos proporcionados. "
            "Responde únicamente con un JSON válido que contenga las claves "
            "'producto', 'cantidad', 'precio_unitario' y 'total'. "
            "Calcula el total multiplicando la cantidad por el precio unitario."
        ),
        "ejemplo_usuario": (
            "Un cliente solicita 5 teclados a $15000 cada uno. "
            "Genera una cotización."
        ),
        "claves_esperadas": [
            "producto",
            "cantidad",
            "precio_unitario",
            "total",
        ],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "producto": {"type": "STRING"},
                "cantidad": {"type": "INTEGER"},
                "precio_unitario": {"type": "NUMBER"},
                "total": {"type": "NUMBER"},
            },
            "required": [
                "producto",
                "cantidad",
                "precio_unitario",
                "total",
            ],
        },
    },
    {
        "nombre": "calcular_descuento",
        "system_instruction": (
            "Eres un asistente especializado en cálculos de cotizaciones. "
            "Calcula el descuento aplicado a un monto original. "
            "Responde únicamente con un JSON válido que contenga las claves "
            "'monto_original', 'porcentaje_descuento', "
            "'monto_descuento' y 'total_final'. "
            "Entrega todos los valores como números."
        ),
        "ejemplo_usuario": (
            "Una cotización tiene un valor original de $200000. "
            "El cliente recibe un descuento del 10%. "
            "Calcula el descuento y el total final."
        ),
        "claves_esperadas": [
            "monto_original",
            "porcentaje_descuento",
            "monto_descuento",
            "total_final",
        ],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "monto_original": {"type": "NUMBER"},
                "porcentaje_descuento": {"type": "NUMBER"},
                "monto_descuento": {"type": "NUMBER"},
                "total_final": {"type": "NUMBER"},
            },
            "required": [
                "monto_original",
                "porcentaje_descuento",
                "monto_descuento",
                "total_final",
            ],
        },
    },
    {
        "nombre": "validar_cotizacion",
        "system_instruction": (
            "Eres un asistente encargado de validar cotizaciones. "
            "Una cotización requiere producto, cantidad y precio unitario. "
            "Verifica si están presentes todos estos datos. "
            "Responde únicamente con un JSON válido que contenga "
            "'cotizacion_valida' (boolean), 'datos_faltantes' "
            "(lista de textos) y 'observacion' (texto)."
        ),
        "ejemplo_usuario": (
            "Un cliente solicita 10 monitores, "
            "pero no se ha indicado el precio unitario."
        ),
        "claves_esperadas": [
            "cotizacion_valida",
            "datos_faltantes",
            "observacion",
        ],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "cotizacion_valida": {"type": "BOOLEAN"},
                "datos_faltantes": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"},
                },
                "observacion": {"type": "STRING"},
            },
            "required": [
                "cotizacion_valida",
                "datos_faltantes",
                "observacion",
            ],
        },
    },
]
