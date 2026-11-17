# Bitácora 04-06 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-06 queda **Pendiente (redactada, decisiones abiertas D1 a D4)**. Solo documentos; sin código, pruebas, `manage.py` ni `sqlmigrate`.

## Resumen

Se redactó [iteracion-04-06](../../10_epicas/epica-04-seguridad/iteracion-04-06-proteccion-del-historial.md): `Pedido.cliente` y `Cotizacion.cliente` pasan a `PROTECT`, migración `0008` de Clase 1 esperada (se detiene ante cualquier `ALTER`), `eliminar_cliente` captura `ProtectedError` como `eliminar_producto` y R14 pasa a verde.

## Verificación (solo lectura)

- `models.py`: `CASCADE` en `:37`, `:92`, `:164`, `:197`, `:214`; `PROTECT` en `:198`, `:215`; `SET_NULL` en `:58`, `:97`, `:272`.
- Migraciones `0001` a `0007_registroevento`, sin huecos: la nueva es `0008`.
- `eliminar_cliente` (`views.py:690-697`) sin captura; `eliminar_producto` (`:1122-1139`) como modelo; `cliente_confirm_delete.html` sin bloque de error y con advertencia «podrías perder el historial».
- R14 en `test_regresiones.py:371-384` (solo pedidos).
- Búsqueda de `.delete()`: solo `eliminar_cliente` y el admin (`admin.py:6`) borran clientes; `purgar_registros` solo toca eventos. Pruebas que borran clientes lo hacen sin historial o como anónimo.
- RDA-017: el borrado físico con doble confirmación es de usuarios.

## Contradicciones

1. RDA-017 no aplica a clientes (no hay doble confirmación que agregar).
2. R14 no cubre cotizaciones ni la vista (D4).
3. Pedido → pagos en cascada: no consta que sea intencional; pregunta `PENDIENTE_CLIENTE` en el registro, fuera de alcance.

## Qué no se pudo ver

- La salida real de `sqlmigrate` (inferida: sin SQL).
- Cómo responde el admin de Django 6.0 ante `PROTECT` (inferido).
- Cuántos clientes de producción tienen historial.

## Decisiones abiertas

D1 texto del mensaje, D2 advertencia de la confirmación, D3 registrar el intento rechazado, D4 pruebas adicionales. Fila en la sección 3 del registro.

## Archivos

Nuevo `iteracion-04-06-proteccion-del-historial.md`; `definicion-epica-04.md`; `00_producto/registro-pendientes.md` (fila, decisiones, pregunta al cliente, próximo hito 04-07, historial); esta bitácora.
