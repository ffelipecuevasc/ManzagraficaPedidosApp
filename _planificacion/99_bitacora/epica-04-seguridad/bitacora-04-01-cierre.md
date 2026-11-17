# Bitácora 04-01 · Cierre documental de la redacción (P1 y P2)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-01 queda **Pendiente (redactada, decisiones resueltas)**, sin decisiones abiertas salvo etiqueta y fecha del despliegue. Solo documentos; sin código ni pruebas.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

- **P1:** se crea `pedidos/templates/pedidos/pago_confirm_delete.html`. GET muestra la confirmación (200) y POST borra. **R7 se mantiene sin cambios** y pasa a verde. Única excepción a la decisión (a), que sigue vigente para cambiar estado, duplicar y respaldo. Se descarta reescribir R7 a 405.
- **P2:** la escritura con GET del panel (`registrar_metricas_diarias`, `views.py:73`) queda en la 06-01 (RDA-009). Motivo: no mezclar fases en un despliegue (RDA-007). Única excepción a la decisión (b).

## Cambios en la iteración

- `eliminar_pago` no lleva `@require_POST`: ya escribe solo con POST (`views.py:1577`); falta la plantilla.
- Los enlaces a eliminar pago (`pedido_detail.html:343`, `pago_list.html:108`) siguen siendo GET hacia la confirmación; el modal `data-confirm` queda solo en `pedido_detail.html` para duplicar.
- **Pruebas que dependían del cambio a 405, revisadas:** ya no hay prueba nueva de «GET 405 en eliminar pago»; R7 sigue igual; `test_errores.test_regresion_eliminar_pago_deja_tipo_y_traza` falla igual con P1 (el GET pasa a 200) y se retira; en `test_acceso.PkInexistenteTests`, eliminar pago puede dejar de ser excepción con GET (404 inferido por `get_object_or_404` antes del `render`). Las pruebas de 302 de la 02-05 no cambian.
- Riesgo de formularios en filas de tabla retirado; se suma el de la plantilla nueva (`DESIGN.md`, 360 px, teclado).

## Coherencia revisada

Definición, iteración y registro dicen lo mismo: estado «Pendiente (redactada, decisiones resueltas)», fecha 2026-11-17, R6a, R6b, R6c, R7 y R19 a verde, y **4 fallos esperados** al terminar (R8, R9, R14, R15; hoy 9, dato de la 03-04 y la 03-05, no medido aquí). `registro-pendientes.md` se editó por bytes, sin cambiar su fin de línea CRLF.

## Archivos

`10_epicas/epica-04-seguridad/iteracion-04-01-mutaciones-solo-por-post.md`, `definicion-epica-04.md`, `00_producto/registro-pendientes.md` (fila, sección 3 con P1 y P2 tachados como resueltos, historial) y esta bitácora.
