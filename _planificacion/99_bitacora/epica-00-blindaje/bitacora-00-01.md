# Bitácora 00-01 · Línea base de producción

- **Fecha:** 2026-10-20
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (pendiente de la evidencia de producción; tareas 1 a 5 hechas, tarea 6 sin hacer)

## Resumen

Se prepararon los guiones de solo lectura para medir producción (SQL y Bash), el fragmento que comprueba la clave secreta sin revelarla, la plantilla de la línea base y el archivo de evidencia con los pasos para el desarrollador. No se tocó código de la aplicación, esquema ni plantillas. El guion SQL **no se pudo ejecutar** contra el MySQL local porque no está encendido; queda «sin ejecutar». Las cifras de producción siguen pendientes: se consolidan en `bitacora-00-01-produccion.md` cuando el desarrollador responda `evidencia-00-01.md`.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `scripts/diagnostico/linea_base.sql` | Nuevo. 13 `SELECT` y 1 `SHOW`, solo agregados. |
| `scripts/diagnostico/linea_base.sh` | Nuevo. Solo lectura; el código vive en una función para que un error de rutas no cierre la consola. |
| `_planificacion/00_producto/linea-base-produccion.md` | Nuevo. Plantilla `Métrica · Valor · Fecha de medición · Fuente`, sin valores. |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-01.md` | Nuevo. Pasos exactos, fragmento de la clave con el hash, formato de respuesta. |
| `_planificacion/00_producto/registro-pendientes.md` | Estado de 00-01, pendiente del desarrollador e historial. |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-01-linea-base-produccion.md` | Solo la línea de estado. |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-01.md` | Esta bitácora. |

## Verificación

- `git log` y `git show --stat 713260c`: el commit existe («Versión 1.0 - Lista para Producción», 2026-01-13, autor del repositorio).
- Búsqueda sin distinguir mayúsculas de `insert|update|delete|alter|drop|create|truncate|replace|grant` en `linea_base.sql`: **0 coincidencias** (búsqueda por subcadena, incluidos los comentarios).
- Sentencias del guion SQL, contadas con su primera palabra: 13 `SELECT`, 1 `SHOW`. Archivo en ASCII (0 bytes fuera de ASCII) y fin de línea LF.
- **Ejecución del guion SQL contra el MySQL local: sin ejecutar.** Comprobado: `127.0.0.1:3306` rechaza la conexión (error 2002 en `makemigrations --check --dry-run` y al generar SQL con Django). No se simuló. Los nombres de tablas y columnas se tomaron de `pedidos/models.py` (sin `db_table`) y `makemigrations --check --dry-run` informó «No changes detected», es decir, modelos y migraciones coinciden.
- `linea_base.sh`: `bash -n` sin errores. Ejecutado contra una carpeta simulada en el scratchpad (volcados de prueba, `requirements.txt` en UTF-16 LE con BOM `ff fe` como el real, `pip` de prueba): imprime fecha, disco, volcados con número, tamaño y antigüedad, `media/`, Python y diferencias de paquetes. Con rutas sin definir, avisa y no hace nada. Durante la prueba apareció un fallo (no detectaba UTF-16 big endian con BOM `fe ff`); se corrigió aceptando ambos BOM y se volvió a probar. No se ejecutó nada sobre el `backups/` del repositorio.
- Fragmento de la clave: hash SHA-256 calculado con `git show` y `ast` leyendo `SECRET_KEY` de `713260c:PedidosApp/settings.py` (literal con prefijo `django-insecure-`, 66 caracteres). Probado con tres claves de prueba inyectadas por variable de entorno (la histórica, otra insegura, otra segura): respuestas `True/True`, `True/False` y `False/False`. La clave no se imprimió ni se copió en ningún archivo. En `HEAD`, `settings.py` ya no tiene la clave escrita: la lee de la variable de entorno `SECRET_KEY`.
- Fragmento de registros (`contar_logs`): probado contra registros simulados rotados (planos y `.gz`).
- Pruebas (`python manage.py test pedidos`): no ejecutadas. No se modificó código de la aplicación y el MySQL local está apagado.
- Revisión de pantallas: no aplica, no se tocaron plantillas.

## Migraciones

- Ninguna. Cambio de esquema: Ninguno.

## Criterios de aceptación

- [x] `linea_base.sql` no contiene `INSERT`, `UPDATE`, `DELETE`, `ALTER`, `DROP`, `CREATE`, `TRUNCATE`, `REPLACE` ni `GRANT` (0 coincidencias, sin distinguir mayúsculas).
- [ ] El guion SQL se ejecuta sin errores contra el MySQL local antes de entregarlo: **sin ejecutar**, MySQL local apagado.
- [ ] `linea-base-produccion.md` con todas las cifras y su fecha: plantilla creada; faltan los valores (evidencia).
- [x] Ningún archivo de la iteración contiene nombres, teléfonos, correos, montos de clientes ni la clave secreta. Comprobado con un programa que busca en los cinco archivos nuevos el texto completo de la clave del commit `713260c` (0 coincidencias), correos (0) y `+56` (0). El prefijo `django-insecure-` aparece solo como texto de la pregunta, sin la clave.
- [ ] Los cuatro hallazgos tienen su resultado medido en `auditoria-tecnica.md`: pendiente de la evidencia (tarea 6).

## Decisiones tomadas

- El guion SQL replica el cálculo real de `registrar_metricas_diarias` y del gráfico anual: `fecha_registro__date` (con `CONVERT_TZ`) y la agrupación mensual con conversión; el filtro por año se replica como rango.
- Se agregaron al guion, como contexto de solo lectura, `@@sql_mode` (paridad con la réplica de 00-03), la vigencia de las estadísticas de `information_schema` (`SHOW VARIABLES`, porque MySQL 8 las guarda en caché hasta 24 horas), el día calculado en UTC y en hora de Chile para `HistorialBD`, y los pedidos con valor $0 (regla de negocio pendiente). No hay sumas de montos.
- Las desconexiones se cuentan por archivo de registro rotado, con su fecha de modificación, para no depender del formato de fecha de cada línea. El patrón (`Broken pipe`, `write error`, `SIGPIPE`) no está verificado contra producción; la evidencia incluye una consulta de los mensajes más repetidos para confirmarlo.

## Pendientes y riesgos

- **Discrepancia con `AGENTS.md` (sección 8, regla 6) y con la descripción de AUD-02-007.** Esos textos dicen que el filtro `__year` hace que MySQL convierta la zona horaria. Al generar el SQL con Django 6.0.1 se comprobó que `fecha_solicitud__year=2026` produce `BETWEEN 2026-01-01 03:00:00 AND 2027-01-01 02:59:59.999999` (un rango, sin `CONVERT_TZ`), mientras que `fecha_registro__date=...` produce `DATE(CONVERT_TZ(..., UTC, America/Santiago))`. `TruncMonth` no se pudo generar sin conexión, pero usa la conversión de zona horaria de la base. La medición no se ve afectada porque el guion replica cada mecanismo tal como es. Consecuencia sin verificar: si las tablas de zona horaria no están cargadas, `TruncMonth` devuelve NULL y la vista, al hacer `d['mes'].month`, fallaría con un error en lugar de mostrar el gráfico vacío. Se propone al desarrollador ajustar el texto de `AGENTS.md` (no se editó, es documento protegido); la propuesta va en el resumen de entrega.
- Conviene encender el MySQL local y ejecutar el guion SQL para cerrar el criterio 2. Hay que autorizarlo en el momento: base `manzagrafica_local`, `127.0.0.1:3306`, usuario `root` de desarrollo, tomados de `settings.py`.
- `PENDIENTE_DESARROLLADOR`: rutas del proyecto y del entorno virtual en PythonAnywhere (las dos variables del inicio de `linea_base.sh`).
- La tarea 6 (consolidar la línea base, `bitacora-00-01-produccion.md` y actualizar los cuatro hallazgos) no se hizo: depende de la evidencia respondida.

## Commit sugerido

`Épica 0 - Iteración 00-01: guiones de solo lectura y pedido de evidencia para medir la línea base de producción`
