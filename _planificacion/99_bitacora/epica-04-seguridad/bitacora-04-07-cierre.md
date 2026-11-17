# Bitácora 04-07 · Cierre documental de la redacción (D1 a D4)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** la 04-07 queda **Pendiente (redactada, decisiones resueltas)**. Solo documentos; sin código, pruebas, `manage.py` ni consultas a la base.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Resuelta como |
| :- | :------------ |
| D1 | Se sanitiza al guardar y al mostrar. |
| D2 | Se usa `nh3`. La consulta previa que exige `AGENTS.md` para la dependencia nueva queda **respondida**. RDA-020: **propuesto; se escribe al ejecutar la 04-07** (no se agrega a `decisiones.md` ahora). El paso 0 conserva la comprobación de instalación en PythonAnywhere (Python 3.13). |
| D3 | Lista blanca exacta de la barra actual (negrita, cursiva, limpiar formato y listas): `p`, `br`, `b`, `strong`, `i`, `em`, `ul`, `ol`, `li`, sin atributos. |
| D4 | No se limpian datos ya guardados en esta iteración (se revisan en la réplica); prueba-guardia de SQL con `ast`. |

## Ajustes

- Iteración: estado, decisiones en tabla, alcance (puntos 1 a 7), pasos (el 0 pasa a ser la comprobación de `nh3` en el servidor, que detiene la iteración si no instala), pruebas (variantes de `<script>`, atributos, idempotencia, copias por duplicación y conversión), riesgos y retroceso (la dependencia puede quedarse instalada; si falta, los detalles darían 500 y basta instalarla).
- **Corrección de la redacción:** el filtro `html_seguro` necesita un paquete `pedidos/templatetags/` que **no existe** (verificado el 2026-11-17); se agrega a los archivos de la ejecución.
- **Hallazgo nuevo (verificado):** `duplicar_pedido` (`views.py:490`) y la conversión de cotización (`views.py:982`) copian el HTML sin formulario; los cubre el filtro al mostrar.
- **Anexo:** consulta de solo lectura (solo conteos) para revisar el HTML guardado en la réplica. **No ejecutada ni probada**; la corre el desarrollador.
- Sin editar `decisiones.md` ni `requirements.txt`.

## Qué no se pudo ver

- La firma exacta de `nh3.clean` (inferida de mi conocimiento, no leída), su peso y si instala en PythonAnywhere.
- Las etiquetas reales que guarda Summernote 0.8.18 y el HTML ya guardado (réplica y producción).

## Archivos

`iteracion-04-07-sanitizacion-html-e-inyeccion-sql.md`, `definicion-epica-04.md`, `00_producto/registro-pendientes.md` (por bytes, CRLF intacto) y esta bitácora.
