# Límites de autonomía: agente_con_memoria_cotizaciones_langgraph

## Archivos de referencia del core
- Script del agente: [`agente_con_memoria_cotizaciones_langgraph.py`](./agente_con_memoria_cotizaciones_langgraph.py)
- Archivo de trazas: [`trazas_cotizaciones_modernas.jsonl`](./trazas_cotizaciones_modernas.jsonl)

## Herramientas y nivel de riesgo
- `consultar_cotizacion_detallada`: bajo (solo lee el estado, los ítems y la vigencia de una cotización existente; no modifica registros ni dispara acciones externas).
- `calcular_subtotal_cotizacion`: bajo (calcula `unidades * precio_unitario`; no altera datos persistentes ni ejecuta efectos externos).
- `aplicar_descuento_especial`: alto (modifica condiciones comerciales de una cotización con impacto económico directo y difícil de revertir si se aplica un porcentaje indebido).

## Herramientas que requieren aprobación humana
- `aplicar_descuento_especial`: requiere supervisión humana previa antes de ejecutarse (`HumanInTheLoopMiddleware` con decisiones `approve`, `edit` o `reject` gestionadas en `ejecutar_con_hitl` y auditadas en `registro_aprobaciones` dentro de [`agente_con_memoria_cotizaciones_langgraph.py`](./agente_con_memoria_cotizaciones_langgraph.py)), porque otorga un descuento económico sobre una cotización. Las herramientas de consulta y cálculo no requieren pausa para evitar fatiga de aprobación en tareas rutinarias.

## Revisión de trazas
- Frecuencia: revisión periódica semanal (o cada 20 interacciones) mediante muestreo de casos extremos, más revisión del 100% de las ejecuciones de `aplicar_descuento_especial`.
- Qué se busca en [`trazas_cotizaciones_modernas.jsonl`](./trazas_cotizaciones_modernas.jsonl): repeticiones consecutivas de la misma herramienta con argumentos similares, ejecuciones de `aplicar_descuento_especial` sin registro en `registro_aprobaciones`, o respuestas finales que contradigan o ignoren el resultado devuelto por las herramientas.

## Qué hacer ante un comportamiento inesperado
1. Desactivar o bloquear `aplicar_descuento_especial` en la configuración del agente ([`agente_con_memoria_cotizaciones_langgraph.py`](./agente_con_memoria_cotizaciones_langgraph.py)) para frenar nuevas ejecuciones automáticas.
2. Revisar el último registro relevante en [`trazas_cotizaciones_modernas.jsonl`](./trazas_cotizaciones_modernas.jsonl) y el historial de `registro_aprobaciones` para detectar si el fallo ocurrió en la selección de herramienta, en los argumentos o en la lógica interna.
3. Ajustar el esquema `ArgumentosConsultaCotizacion`, la descripción de la herramienta, las reglas de `HumanInTheLoopMiddleware` o el `system_prompt` según corresponda en [`agente_con_memoria_cotizaciones_langgraph.py`](./agente_con_memoria_cotizaciones_langgraph.py).
4. Ejecutar pruebas de validación (cubriendo `approve`, `edit`, `reject` y entradas inválidas) y comprobar en [`trazas_cotizaciones_modernas.jsonl`](./trazas_cotizaciones_modernas.jsonl) que el comportamiento quedó corregido antes de habilitar nuevamente la herramienta.