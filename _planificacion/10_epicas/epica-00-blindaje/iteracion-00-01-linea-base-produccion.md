# Iteración 00-01 · Línea base de producción

- **Épica:** 00 · Blindaje y punto de retorno
- **Estado:** Pendiente
- **Subfase del plan:** 0.1
- **Depende de:** —
- **RDA relacionadas:** RDA-004
- **Hallazgos que cierra:** ninguno. Aporta la medición que decide la prioridad de AUD-01-006, AUD-02-004, AUD-02-007 y AUD-02-010.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no hay despliegue)

## Objetivo

Medir producción sin modificar nada y dejar las cifras en `_planificacion/00_producto/linea-base-produccion.md`. Sin esta línea base es imposible saber después si una corrección u optimización funcionó.

## Tareas

1. **Guion SQL de solo lectura** en `scripts/diagnostico/linea_base.sql`. Solo `SELECT` y `SHOW`, y solo resultados agregados (conteos, tamaños, fechas mínimas y máximas), nunca filas con datos de clientes. Debe entregar:
   1. Tabla `pedidos_historialbd`: total de filas, fecha mínima y máxima, número de días distintos y el máximo de filas registradas en un mismo día. Si hay varios registros por día, el defecto de AUD-01-006 está confirmado.
   2. Peso de la base (datos más índices) y peso por tabla, desde `information_schema.TABLES`.
   3. Conteo de filas de cada tabla de negocio: clientes, pedidos, ítems de pedido, cotizaciones, ítems de cotización, productos y pagos.
   4. Versión de MySQL, `@@character_set_database`, `@@collation_database`, `@@time_zone`, `@@system_time_zone`.
   5. Si las tablas de zona horaria de MySQL están cargadas: `CONVERT_TZ` de un instante fijo entre `'UTC'` y `'America/Santiago'` devuelve un valor o `NULL`.
   6. Conteo de pedidos del año en curso agrupados por mes con la misma conversión que usa Django (`fecha_solicitud__year` y `TruncMonth`), para saber si el gráfico anual de estadísticas sale vacío (AUD-02-007).
   7. Conteo de pedidos cuyo `estado_pago` no coincide con lo que dicen sus pagos (AUD-02-004): `PAGADO` si el saldo es menor o igual a cero, `PARCIAL` si hay pagos y saldo, `PENDIENTE` si no hay pagos.
2. **Guion de consola Bash** en `scripts/diagnostico/linea_base.sh`, para la consola de PythonAnywhere, de solo lectura: uso de disco de la cuenta, listado de `backups/` con tamaño y fecha (sin abrir los archivos), tamaño de `media/`, versión de Python del entorno de la web app y `pip freeze` para compararlo con `requirements.txt`.
3. **Comprobación de la clave secreta sin revelarla** (AUD-02-010): un fragmento que el desarrollador corre en la consola de PythonAnywhere y que imprime solo `True` o `False` para dos preguntas: si la clave de producción empieza con `django-insecure-` y si su hash SHA-256 coincide con el de la clave del commit `713260c`. El agente calcula ese hash desde el historial con `git show` y lo escribe en la evidencia; la clave nunca se copia en ningún archivo.
4. **Plantilla** de `linea-base-produccion.md` con una tabla `Métrica · Valor · Fecha de medición · Fuente` para cada dato de la lista de abajo.
5. **Archivo de evidencia** `evidencia-00-01.md` con los pasos exactos: qué guion pegar en qué consola (consola MySQL o Bash de PythonAnywhere), dónde leer en el panel la disponibilidad de la tarea programada y la fecha de expiración de la web app, cómo contar en el registro del servidor las desconexiones de los últimos siete días y las peticiones a `/robots.txt` (insumo para medir 00-06), y el formato de la respuesta. Recordatorio para el desarrollador: las consolas consumen la cuota diaria de 100 segundos de CPU.
6. Con la evidencia respondida, consolidar en `linea-base-produccion.md`, escribir `bitacora-00-01-produccion.md` y actualizar el estado de AUD-01-006, AUD-02-004, AUD-02-007 y AUD-02-010 con lo medido (siguen abiertos; ahora con evidencia).

## Criterios de aceptación

- [ ] `scripts/diagnostico/linea_base.sql` no contiene `INSERT`, `UPDATE`, `DELETE`, `ALTER`, `DROP`, `CREATE`, `TRUNCATE`, `REPLACE` ni `GRANT` (búsqueda sin distinguir mayúsculas, sin coincidencias).
- [ ] El guion SQL se ejecuta sin errores contra el MySQL local antes de entregarlo al desarrollador.
- [ ] `linea-base-produccion.md` registra, con fecha de medición: filas de `HistorialBD` (total, días distintos, máximo por día); peso de la base en MB; uso de disco de la cuenta frente a los 512 MiB; número, tamaño total y antigüedad de los volcados en `backups/`; tamaño de `media/`; conteo de filas por tabla de negocio; versión, conjunto de caracteres, colación y zona horaria de MySQL; tablas de zona horaria cargadas (sí o no); gráfico anual con datos (sí o no); pedidos con `estado_pago` inconsistente; versión de Python de producción; tarea programada disponible (sí o no); fecha de expiración de la web app y procedimiento de renovación; desconexiones en el registro durante los últimos siete días; peticiones a `/robots.txt` en el mismo periodo; clave secreta con prefijo inseguro (sí o no) y coincidente con la del historial (sí o no).
- [ ] Ningún archivo de la iteración contiene nombres, teléfonos, correos, montos de clientes ni la clave secreta.
- [ ] Los cuatro hallazgos relacionados tienen su resultado medido anotado en `auditoria-tecnica.md`.

## Fuera de alcance

- Corregir cualquier defecto encontrado, incluida la limpieza de filas duplicadas de `HistorialBD` (va en 06-01).
- Descargar o abrir respaldos (va en 00-02).

## Datos requeridos del cliente

- Ninguno.
