# Bitácora 00-01 · Línea base de producción (consolidación de la evidencia)

- **Fecha:** 2026-10-20
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión

## Resumen

El desarrollador midió producción el 2026-10-20 (UTC) con los pasos de `evidencia-00-01.md` y entregó la salida procesada de las consolas y del panel de PythonAnywhere. Con eso se completó `linea-base-produccion.md`, se anotó lo medido en seis hallazgos y se abrieron dos nuevos (AUD-02-020 y AUD-02-021). Se corrigió `linea_base.sh`, que contaba `.gitkeep` como volcado, y la evidencia ahora deja un método de conteo por fecha que 00-06 puede reutilizar. Lo más grave de la medición: el 70,1 % de los pedidos tiene `estado_pago` incorrecto y la métrica diaria cubre solo el 47 % de los días.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/00_producto/linea-base-produccion.md` | Valores medidos con fecha y fuente en las nueve secciones. |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-01.md` | Registro de la respuesta (sin registros crudos) y método de conteo por fecha para 00-06. |
| `_planificacion/00_producto/auditoria-tecnica.md` | Estado de AUD-01-006, AUD-02-002, AUD-02-004, AUD-02-007 y AUD-02-010; filas nuevas AUD-02-020 y AUD-02-021; sección «Mediciones de producción · 2026-10-20». |
| `_planificacion/00_producto/decisiones.md` | Actualización fechada en RDA-004. |
| `_planificacion/00_producto/registro-pendientes.md` | Estado, enlace a esta bitácora, decisiones por tomar, dato del pedido con valor $0 e historial. |
| `scripts/diagnostico/linea_base.sh` | Excluye `.gitkeep` del conteo de volcados. Además se devolvieron las líneas `PROYECTO=` y `VENV=` a su forma original (ver «Pendientes y riesgos»). |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-01-produccion.md` | Esta bitácora. |

## Verificación

- **Fuente de las cifras:** salida de las consolas MySQL y Bash y del panel de PythonAnywhere, pegada por el desarrollador. El agente no accedió a producción. Ninguna cifra se estimó: lo que no vino en la evidencia quedó como `PENDIENTE_DESARROLLADOR` (tamaño de `backups/` completo, desglose de datos e índices por tabla, uso de CPU del Dashboard).
- **Cálculos del agente:** cobertura de `HistorialBD`, 121 días con registro sobre 256 transcurridos = 47 %; antigüedad del volcado más antiguo, 2026-03-26 a 2026-10-20 = 208 días; disco, 180,8 / 512 = 35 %; `estado_pago`, 610 / 870 = 70,1 %, y la matriz suma 234 + 4 + 563 + 47 + 22 = 870; pedidos por mes, la suma de enero a octubre da 870; `/robots.txt` en todos los archivos de acceso, 6 + 10 + 7 + 7 + 14 = 44; `Broken pipe`, 39 en 89 días = 0,44 por día.
- **`linea_base.sh`:** `bash -n` sin errores. Probado contra una carpeta simulada en el scratchpad con `backups/.gitkeep` y un volcado de prueba: informa «Volcados: 1 archivos» (antes habría dicho 2). `HOME` apuntaba a la carpeta simulada para que `du` no recorriera el disco local.
- **Conteo por fecha de `/robots.txt`** (`evidencia-00-01.md`): probado contra un registro de accesos simulado (uno plano y uno `.gz`) con el formato de línea que informó el desarrollador: agrupa por día y código de respuesta.
- **Código de `eliminar_producto` y `eliminar_cotizacion`:** `git log -L` y `git show` muestran que la captura de `ProtectedError` (`73cc8e6`) y la plantilla `cotizacion_confirm_delete.html` (`59801a4`) entraron el 2026-02-03; producción corre `2442f3b` (2026-03-12).
- **Datos personales:** los archivos tocados no contienen nombres, teléfonos, correos, montos de clientes, IP ni la clave. Las rutas del servidor no quedaron en el repositorio.
- Pruebas (`python manage.py test pedidos`): no ejecutadas; no se tocó código de la aplicación.
- Revisión de pantallas: no aplica.

## Migraciones

- Ninguna.

## Resultados por hallazgo

| Hallazgo | Resultado medido |
| :------- | :--------------- |
| AUD-01-006 | Confirmado. 187 filas en 121 días (UTC), máximo 16 por día, 66 sobrantes. Cobertura del 47 %: no hay tarea programada y la métrica depende de que alguien abra estadísticas. |
| AUD-02-002 | Confirmado: 14 errores en `eliminar_pago` por la plantilla inexistente. |
| AUD-02-004 | Confirmado a gran escala: 610 de 870 pedidos; 563 en `PENDIENTE` que deberían estar en `PAGADO`. |
| AUD-02-007 | No confirmado: tablas de zona horaria cargadas y gráfico con datos (870 pedidos, 0 nulos). Se propone bajar a Baja. |
| AUD-02-010 | Mitigado en producción: la clave no es la expuesta. La expuesta sigue en el historial. |
| AUD-02-019 | Existe (no se agregó). Cinco volcados suman 6,19 MB, un 1,2 % de la cuota. |
| AUD-02-020 (nuevo) | Producción sin modo estricto de MySQL (`NO_ENGINE_SUBSTITUTION`). Paridad en 00-03, prueba en 04-05. |
| AUD-02-021 (nuevo) | 13 errores de plantilla en `crear_pedido`, `crear_cotizacion` y `crear_cliente`. Alta, causa pendiente. |

## Criterios de aceptación

- [x] `linea_base.sql` sin sentencias de escritura (`bitacora-00-01.md`).
- [x] El guion SQL se ejecuta sin errores contra el MySQL local (`bitacora-00-01-sql-local.md`).
- [x] `linea-base-produccion.md` registra, con fecha de medición, todos los datos de la lista del criterio: `HistorialBD` (187 filas, 121 días, máximo 16), peso de la base (2,20 MB, referencial), disco (180,8 de 512 MB, 35 %), volcados (5, 6,19 MB, 208 y 0 días), `media/` (3 MB), filas por tabla, MySQL (8.0.46, `utf8mb4`, `utf8mb4_unicode_ci`, UTC), tablas de zona horaria (sí), gráfico anual (sí), `estado_pago` (610), Python (3.13.1), tarea programada (disponible, ninguna creada), expiración (2026-11-20) y renovación, desconexiones (4 y 12), `/robots.txt` (7) y clave (no y no). La fecha de expiración tiene una confirmación pendiente.
- [x] Ningún archivo de la iteración contiene nombres, teléfonos, correos, montos de clientes ni la clave secreta.
- [x] Los cuatro hallazgos relacionados tienen su resultado medido en `auditoria-tecnica.md`.

## Decisiones tomadas

- **Aclaración sobre `__year` y AUD-02-007** (acordada en `bitacora-00-01-sql-local.md`): `fecha_solicitud__year=2026` se traduce a un rango de instantes sin `CONVERT_TZ`; solo `TruncMonth` convierte la zona horaria en la base. Con las tablas cargadas, el gráfico funciona. La nota va en la auditoría sin reescribir el hallazgo.
- **No se abrió un hallazgo para `eliminar_producto`.** El pedido suponía que un `ProtectedError` termina en error 500, pero la vista lo captura y muestra un mensaje desde el 2026-02-03, antes del código que corre producción. Los 4 errores del registro, igual que los 2 de `eliminar_cotizacion`, son probablemente anteriores a esa corrección. Se confirma con sus fechas. Si alguno es posterior al 2026-03-12, se abre el hallazgo y se asocia al contrato de error de 03-04.
- **AUD-02-021 sin causa.** El mensaje está truncado a 110 caracteres. No se dedujo la causa.
- **Conteo por fecha en lugar de por archivo** para los registros, porque los archivos rotan de forma irregular.

## Pendientes y riesgos

- **`linea_base.sh` tenía un cambio local sin commit** en las líneas `PROYECTO=` y `VENV=`, con la forma `"${/ruta}"`. En Bash eso da «bad substitution», y además dejaba las rutas del servidor en el repositorio, algo que la evidencia pedía evitar. Se devolvieron a `"${PROYECTO:-PENDIENTE_DESARROLLADOR}"` y `"${VENV:-...}"`. Para la próxima ejecución, define las variables antes de pegar el guion (`PROYECTO=/ruta VENV=/ruta`) o cambia las líneas solo en el texto que pegas.
- `PENDIENTE_DESARROLLADOR`: confirmar si la expiración del 2026-11-20 viene de una renovación hecha el mismo día.
- `PENDIENTE_DESARROLLADOR`: mensaje completo y fechas de los errores del decorador (AUD-02-021, `eliminar_producto` y `eliminar_cotizacion`).
- `PENDIENTE_DESARROLLADOR`: bloque exacto que se usó para contar el registro del servidor por fecha. Hay que guardarlo para 00-06; el formato de fecha de esas líneas no quedó registrado.
- **Riesgo de expiración:** la web app depende de un clic mensual del titular. Mientras no exista 07-01, el aviso por correo de PythonAnywhere es la única alarma.
- **Señal débil para 00-06:** unas 3 desconexiones `Broken pipe` por semana. La propuesta de redacción se entregó al desarrollador.
- La corrección de AUD-02-004 en 03-03 no repara los 610 pedidos existentes. Repararlos es una escritura masiva sobre datos vivos y tiene que planificarse aparte.

## Commit sugerido

`Épica 0 - Iteración 00-01: consolida la línea base de producción, actualiza seis hallazgos, abre AUD-02-020 y AUD-02-021 y excluye .gitkeep del conteo de volcados`
