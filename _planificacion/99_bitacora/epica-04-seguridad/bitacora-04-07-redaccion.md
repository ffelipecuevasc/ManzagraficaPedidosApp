# Bitácora 04-07 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-07 queda **Pendiente (redactada, decisiones abiertas D1 a D4)**. Solo documentos; sin código, pruebas, `manage.py` ni consultas a la base.

## Resumen

Se redactó [iteracion-04-07](../../10_epicas/epica-04-seguridad/iteracion-04-07-sanitizacion-html-e-inyeccion-sql.md): lista blanca para los tres campos de Summernote, revisión de inyección SQL con una prueba-guardia, revisión del HTML guardado en la réplica (solo conteos, la ejecuta el desarrollador) y RDA-020 si se elige `nh3`.

## Verificación (solo lectura, búsquedas reales)

- `|safe`: `pedido_detail.html:115`, `cotizacion_detail.html:150`, `producto_detail.html:53`. Sin `mark_safe`, `format_html`, `SafeString` ni `autoescape off` en la aplicación.
- Ya seguros (`|striptags` sin `|safe`): `cotizacion_pdf.html:289` y `:318`, `producto_list.html:77`.
- Summernote 0.8.18 desde CDN (`base.html:38`, `:327`); barra en `index.js:94-102` (negrita, cursiva, limpiar, listas).
- `producto.descripcion` también entra por `api_crear_producto_rapido` (`views.py:1147`, `ProductoForm`).
- SQL: única consulta directa en `utils.py:161-162`, parametrizada; ningún `.raw(`, `.extra(` ni `RawSQL`.
- `requirements.txt` sin sanitizador. Última RDA: RDA-019, así que la siguiente es la RDA-020.

## Contradicciones

1. La revisión «del HTML guardado en producción» se hace en la réplica: vale hasta su último refresco.
2. Summernote viene de un CDN (regla 8.17); lo resuelve la 08-07, no esta iteración.

## Qué no se pudo ver

- Las etiquetas exactas que genera Summernote 0.8.18 (inferidas de la barra).
- El HTML guardado en la réplica y en producción.
- El peso de `nh3` y si su rueda instala en PythonAnywhere.

## Decisiones abiertas

D1 cuándo sanitizar, D2 herramienta, D3 lista blanca, D4 datos guardados y forma de la guardia SQL. Fila en la sección 3 del registro.

## Archivos

Nuevo `iteracion-04-07-sanitizacion-html-e-inyeccion-sql.md`; `definicion-epica-04.md`; `00_producto/registro-pendientes.md` (fila, decisiones, próximo hito 04-08, historial); esta bitácora.
