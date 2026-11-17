# Bitácora 04-10 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** la 04-10 queda **Pendiente (redactada, decisiones abiertas D1 a D4)**. Solo documentos; sin código, pruebas, `manage.py` ni consultas a la base.

## Resumen

Se redactó [iteracion-04-10](../../10_epicas/epica-04-seguridad/iteracion-04-10-confirmacion-reforzada-al-eliminar-un-pedido-con-pagos.md): antes de eliminar un pedido con pagos, la pantalla dice cuántos pagos y qué monto se borrarán, el servidor exige una confirmación explícita y el evento guarda la cantidad de pagos. No cambia la cascada, no anula y no usa `PROTECT`. Origen: decisión del desarrollador sobre la pregunta `PENDIENTE_CLIENTE` (el cliente no ha respondido).

## Verificación (solo lectura)

- `Pago.pedido` es `CASCADE` (`models.py:92`); `Pago.monto` es un entero (`:93`).
- `eliminar_pedido` (`views.py:378-385`): GET muestra la confirmación, POST borra y registra `pedido_eliminado`; no cuenta ni menciona los pagos.
- **El evento `pedido_eliminado` ya existe** (`models.py:254`, `views.py:383`, `test_eventos_negocio.py:62-66`) con el resumen `Pedido #N eliminado`; no dice cuántos pagos se perdieron. Los eventos guardan solo identificadores (`models.py:276`): se registra la cantidad, no el monto.
- La pantalla (`pedido_confirm_delete.html`) no dice que hay pagos; tiene el bloqueo de doble envío de la 03-04.
- Producción (2026-10-20): 870 pedidos y 1.033 pagos; no se midió cuántos pedidos tienen pagos.
- Migraciones: hoy la última es la `0007`; la `0008` es de la 04-06 y la `0009` de la 04-08, así que una migración de la 04-10 sería la `0010`.

## Contradicciones

1. El enunciado pedía definir el tipo de evento y su migración de Clase 1; el tipo **ya existe**. Se recomienda reutilizarlo (sin migración) y se deja el tipo nuevo con `0010` como opción.
2. `DESIGN.md` habla de modal; las confirmaciones de la aplicación son páginas. Se mantiene el patrón vigente.
3. RDA-017 (doble confirmación) es para usuarios, no para pedidos.

## Qué no se pudo ver

- Cuántos pedidos de producción tienen pagos, cuántos se eliminaron y si el cliente los elimina a propósito.
- Lo que muestra el admin de Django al borrar un pedido (inferido) y la pantalla en 360 px.
- El criterio exacto de comparación de `RESTAURAR` que fije la 04-04 (aún sin ejecutar).

## Decisiones abiertas

D1 tipo de evento (recomendada: el mismo `pedido_eliminado`), D2 forma de la confirmación (recomendada: escribir `ELIMINAR`), D3 cuándo se exige (recomendada: solo con pagos) y D4 cambio de pagos entre mostrar y confirmar (recomendada: comparar y repintar).

## Archivos

Nuevo `iteracion-04-10-confirmacion-reforzada-al-eliminar-un-pedido-con-pagos.md`; `definicion-epica-04.md`; `00_producto/registro-pendientes.md` (fila, decisiones, pregunta del cliente, historial); esta bitácora.
