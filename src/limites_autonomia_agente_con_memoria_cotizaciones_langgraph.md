# Límites de autonomía: agente_con_memoria_cotizaciones_langgraph

## Archivos de referencia del core
- Script del agente: [`agente_con_memoria_cotizaciones_langgraph.py`](./agente_con_memoria_cotizaciones_langgraph.py)
- Archivo de trazas: [`trazas_cotizaciones_modernas.jsonl`](./trazas_cotizaciones_modernas.jsonl)

## Herramientas y nivel de riesgo
- `consultar_cotizacion_detallada`: bajo (solo consulta el estado, ítems y vigencia de una cotización existente desde `COTIZACIONES`; no modifica registros persistentes ni dispara acciones externas).
- `calcular_subtotal_cotizacion`: bajo (calcula `unidades * precio_unitario` y valida valores inválidos; no altera datos ni ejecuta efectos secundarios externos).
- `aplicar_descuento_especial`: alto (modifica condiciones comerciales de una cotización con impacto económico directo y difícil de revertir si se aplica un porcentaje indebido).

## Herramientas que requieren aprobación humana
- `aplicar_descuento_especial`: requiere supervisión humana previa antes de ejecutarse (`HumanInTheLoopMiddleware` con decisiones `approve`, `edit` o `reject` gestionadas mediante `ejecutar_con_hitl` y `Command(resume=...)`, y registradas en `registro_aprobaciones` dentro de [`agente_con_memoria_cotizaciones_langgraph.py`](./agente_con_memoria_cotizaciones_langgraph.py)), porque otorga un descuento económico sobre una cotización. Las herramientas de lectura y cálculo permanecen autónomas para no generar fatiga de aprobación en tareas rutinarias.

## Revisión de trazas
- Frecuencia: revisión periódica semanal (o cada 20 interacciones) mediante muestreo de casos extremos, más revisión del 100% de las ejecuciones de `aplicar_descuento_especial`.
- Qué se busca en [`trazas_cotizaciones_modernas.jsonl`](./trazas_cotizaciones_modernas.jsonl): repeticiones consecutivas de la misma herramienta con argumentos similares, ejecuciones de `aplicar_descuento_especial` sin registro correspondiente en `registro_aprobaciones`, respuestas finales desconectadas de la observación de la herramienta o fragmentación/repetición al extraer texto de bloques de salida.

## Qué hacer ante un comportamiento inesperado
1. Desactivar o bloquear `aplicar_descuento_especial` (o cambiar su configuración en `HumanInTheLoopMiddleware` dentro de [`agente_con_memoria_cotizaciones_langgraph.py`](./agente_con_memoria_cotizaciones_langgraph.py)) para detener nuevas ejecuciones automáticas.
2. Inspeccionar la última línea relevante en [`trazas_cotizaciones_modernas.jsonl`](./trazas_cotizaciones_modernas.jsonl) y el historial de `registro_aprobaciones` para identificar si el fallo ocurrió en la selección de herramienta, en los argumentos, en la interrupción HITL o en el formateo de salida.
3. Ajustar el esquema `ArgumentosConsultaCotizacion`, la descripción de la herramienta, el `system_prompt`, `extraer_texto` o las reglas de `HumanInTheLoopMiddleware` en [`agente_con_memoria_cotizaciones_langgraph.py`](./agente_con_memoria_cotizaciones_langgraph.py) según la causa detectada.
4. Volver a ejecutar pruebas dirigidas (cubriendo continuidad en hilo, aislamiento entre hilos, `approve` / `edit` / `reject` y entradas inválidas) y verificar en [`trazas_cotizaciones_modernas.jsonl`](./trazas_cotizaciones_modernas.jsonl) que el comportamiento quedó corregido antes de habilitar nuevamente la herramienta.