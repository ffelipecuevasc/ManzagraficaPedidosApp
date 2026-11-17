# Bitácora 04-01 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión (la redacción). La 04-01 queda «Pendiente (redactada, decisiones resueltas)», con P1 y P2 por confirmar. Solo documentos: sin cambios de código, pruebas ni plantillas.

## Resumen

Se redactó [iteracion-04-01](../../10_epicas/epica-04-seguridad/iteracion-04-01-mutaciones-solo-por-post.md) con evidencia leída en `main` (`253a9c2`) y las decisiones (a) y (b) del desarrollador del 2026-11-17 (dichas por él). Se registró que la Épica 04 avanza en paralelo a la vigilancia de la 03-05 y que nada se despliega hasta cerrarla (desde el lunes 2026-11-23 a las 23:48:12).

## Archivos

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-04-seguridad/iteracion-04-01-mutaciones-solo-por-post.md` | Nuevo. |
| `10_epicas/epica-04-seguridad/definicion-epica-04.md` | Estado «En curso» (solo local), última revisión, enlace en la tabla y nota del 2026-11-17. |
| `00_producto/registro-pendientes.md` | Nota de la Épica 04 en paralelo, fila 04-01, tres decisiones en la sección 3, una propuesta en la sección 4 y una fila de historial. |
| `99_bitacora/epica-04-seguridad/bitacora-04-01-redaccion.md` | Esta bitácora. |

## Verificación

Solo lectura y búsquedas; no se ejecutaron pruebas, `manage.py`, Docker ni MySQL. No se hizo `git pull` (prohibido por `AGENTS.md`, sección 6); `main` local estaba en `253a9c2`.

- **Código:** `urls.py` completo; `views.py` en las 4 vistas del alcance, las 4 de eliminar, `dashboard`, respaldo y restauración, pagos; búsqueda de todas las escrituras (`.save(`, `.create(`, `.delete(`, `registrar_evento`); `utils.py:175-205`; `envio_unico.py`; `index.js:345-385` y `:805-870`; plantillas `pedido_detail.html`, `pago_list.html`, `respaldar_bd.html`, y la lista de `templates/pedidos/` (no existe `pago_confirm_delete.html`).
- **Pruebas:** `test_regresiones.py` (R6a a R7, R19, R20), `test_acceso.py` (`:120-230`, `:270-310`), `ayudas.py` y búsqueda por texto de las cuatro rutas en `pedidos/tests/`.
- **Planificación:** `definicion-epica-04.md`, `registro-pendientes.md`, `auditoria-tecnica.md` (AUD-02-002, 02-006, 02-028, 03-002), `decisiones.md` (RDA-007 y 019; RDA-013 por la tabla), estructura de la 03-04 y de su bitácora de redacción.

## Hallazgos de la lectura

1. **Contradicción P1:** R7 exige GET 200 en eliminar pago, lo que solo se cumple con una plantilla de confirmación nueva; la decisión (a) las descarta. Se recomienda reescribir R7 (GET 405, POST borra).
2. **Contradicción P2:** la decisión (b) alcanza al panel, que escribe `HistorialBD` con GET (`views.py:73`), pero su corrección es de la 06-01 (RDA-009) y mezclaría fases (RDA-007). Se recomienda dejarlo en la 06-01.
3. Las cuatro vistas de eliminar (pedido, cliente, cotización, producto) **ya** escriben solo con POST: no se suman al alcance.
4. El modal `data-confirm` hoy navega con GET (`btnConfirmar.href = url`) y solo existe en `pedido_detail.html`: reutilizarlo exige cambiar `initDetailModals()` y poner el marcado al alcance de `pago_list.html`.
5. `@require_POST` hace que un GET a un pk inexistente dé 405 antes del 404: cambian `test_acceso.PkInexistenteTests`, R20 y `test_pedidos.py:315`. El orden de decoradores decide si las pruebas de 302 de la 02-05 siguen en verde.
6. `test_errores.test_regresion_eliminar_pago_deja_tipo_y_traza` depende del defecto y se retira con la corrección.
7. `data-bloquear-envio` dejaría bloqueado el botón del respaldo, porque una descarga no navega (inferido).
8. `eliminar_cotizacion` no registra evento: anotado como propuesta.

## Qué no se pudo ver

- Producción (descargas reales, `access.log`), la pantalla y el comportamiento del modal en el navegador.
- El texto exacto de la subfase 4.1 en `plan-de-trabajo.md` (no se leyó entero; se usó la definición de la épica).
- Si `index.js` lleva versión en la URL (caché del navegador tras el despliegue).

## Pendientes

- P1, P2, etiqueta y fecha del despliegue: `PENDIENTE_DESARROLLADOR` (registro, sección 3).
- Copiar ítems y pagos al duplicar: `PENDIENTE_CLIENTE`, sin cambios.
