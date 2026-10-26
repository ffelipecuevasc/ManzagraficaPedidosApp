# Iteración 01-06 · Despliegue y validación de la observabilidad

- **Épica:** 01 · Observabilidad
- **Estado:** En curso (desplegada el 2026-10-25 como `v1.1-observabilidad`; partes A, B y C validadas; falta la parte D, medición de siete días hacia el 2026-11-01). No pasa a `En revisión` ni a `Terminada` hasta medir la parte D, porque el criterio de la semana depende de ella.
- **Subfase del plan:** 1.6
- **Depende de:** 01-01, 01-02, 01-03, 01-04 y 01-05 (terminadas el 2026-10-25), 01-07 (marcas visuales; terminada el 2026-10-25) y 02-01 (su bloque de `settings.py` viaja aquí)
- **RDA relacionadas:** RDA-003, RDA-007, RDA-008, RDA-013
- **Hallazgos que cierra:** AUD-01-005 (con 01-01 a 01-05). Confirma en producción el cierre de AUD-01-004 (01-03).
- **Cambio de esquema:** Clase 2 (migración `0007_registroevento` de 01-01)
- **Respaldo previo al despliegue:** Sí (obligatorio: hay migración y es el primer despliegue de la fase 1)
- **Ventana:** domingo 2026-10-25 (decisión del desarrollador): el negocio cierra el sábado en la tarde y no hay uso hasta el lunes.
- **Etiqueta:** `v1.1-observabilidad`. **Partida y destino de retroceso:** `v0.2-correcciones`.
- **Evidencia:** [evidencia-01-06](evidencia-01-06.md)

## Objetivo

Llevar la observabilidad a producción con el protocolo de 00-05 y demostrar con un error real que se diagnostica en menos de cinco minutos desde `error.log`, que `error.log` queda sin ruido de `fontTools` y sin líneas duplicadas, y que los eventos de negocio quedan en el admin; después, medir una semana de crecimiento de la tabla de eventos contra la estimación de 01-01.

## Qué se despliega (de `v0.2-correcciones` a `v1.1-observabilidad`)

| Iteración | Cambio | Efecto en producción |
| :-------- | :----- | :------------------- |
| 01-01 | Modelo `RegistroEvento`, migración `0007` (Clase 2), purga y orden `purgar_registros` | Tabla nueva `pedidos_registroevento`, vacía al migrar |
| 02-01 | Bloque 3 de `settings.py`: base de pruebas `test_manzagrafica` con bloqueo de nombres reales; paquete `pedidos/tests/` | Ninguno en ejecución; el bloqueo se evalúa al cargar la configuración (tarea 5) |
| 01-02 | `LOGGING` a stderr con formato `clave=valor` y filtro de contexto; `fontTools` sin propagación; servicio `registrar_evento` | Cambia el formato de `error.log`; se van las líneas de `fontTools` y los 404 |
| 01-03 | Sin `ErrorHandlingMiddleware`; `@transaccion_segura` con `logger.exception`; `print` a `logging`; página 500 nueva | Trazas completas en `error.log`; `server.log` deja de recibir los mensajes de errores |
| 01-04 | 15 eventos (13 vistas y señales de acceso); acceso fallido sin lo escrito | Filas nuevas en la tabla al operar |
| 01-05 | Admin de eventos de solo lectura para superusuarios | Nueva sección en el admin |
| 01-07 | Emoji del nivel al inicio de cada línea del registro (`❌ nivel=ERROR …`) | Las líneas de `server.log` empiezan con el emoji, después de la fecha del recolector (corregido el 2026-10-25: `error.log` conserva el formato de PythonAnywhere) |

Sin cambios en `requirements.txt` ni en `pedidos/static`.

## Tareas

1. **Lista de comprobación previa** (`docs/operacion/despliegue.md`, sección 2), completa en local y copiada en la evidencia:
   1. `python manage.py test pedidos` → `Ran 79 tests` y `OK` (contadas el 2026-10-25: 79 métodos `test_` en `pedidos/tests/`, igual que la última ejecución de la 01-07; si cambia, se anota la nueva). Sin regresiones declaradas todavía, así que no se acepta `expected failures`.
   2. `check --deploy` con `DEBUG=False` → solo las 5 advertencias conocidas (`W004`, `W008`, `W009`, `W012`, `W016`, para 04-02 y 04-03). Cualquier otra, o un error, detiene el despliegue.
   3. `makemigrations --check --dry-run` → `No changes detected`.
   4. `sqlmigrate pedidos 0007` → el SQL completo, copiado en la bitácora y clasificado: `CREATE TABLE` de la tabla nueva, `ALTER TABLE … ADD CONSTRAINT … FOREIGN KEY` **sobre la tabla nueva** (aprobado como Clase 2 en 01-01: no toca `auth_user` ni ninguna tabla existente) y dos `CREATE INDEX`. Si el SQL difiere del de [bitacora-01-06](../../99_bitacora/epica-01-observabilidad/bitacora-01-06.md), detente.
   5. Respaldo previo verificado (tarea 2).
   6. Estilos compilados: no aplica (05-04).
   7. Etiqueta anotada `v1.1-observabilidad` creada y publicada **solo después** de que todo esté con commit y `push` en `main` (`git status` vacío y `main` igual a `origin/main`) y de revisar la lista, con su mensaje final y la fecha real calculada al crearla (nunca un texto de relleno como `<AAAA-MM-DD>`; lección de 00-06).
   8. El despliegue publica solo la Épica 01 (con el bloque de pruebas de 02-01, que no cambia el comportamiento).
2. **Respaldo previo**: un solo clic en «Generar Nuevo Respaldo BD» (enlace GET: no recargar), descarga a la carpeta cifrada, `scripts/verificar_respaldo.py` con código `0` (18 de 18 tablas: todavía sin `pedidos_registroevento`) y fila en `docs/operacion/respaldo.md`, sección 6.
3. **Ensayo en la réplica antes de tocar el servidor** (parte A de la evidencia):
   1. **Restauración como ensayo de retroceso (caso 3):** refrescar `manzagrafica_replica` con el respaldo de la tarea 2 (`docs/operacion/replica-local.md`, sección 9), medir el tiempo y comprobar 18 tablas, sin `pedidos_registroevento` y con la 0006 como última migración. Los 8 eventos de la revisión de 01-05 se pierden: es esperado.
   2. **Migración y retroceso de la 0007 (casos 2 y 1):** aplicar la 0007 midiendo su duración, revertirla a la 0006 con el código nuevo (caso 2 de `retroceso.md`), comprobar que la tabla desaparece y volver a aplicarla. Tiempos en la evidencia.
   3. `test pedidos` y `check` con la réplica restaurada y migrada.
4. **Prueba de que la migración no se aplicó antes de tiempo** (parte B de la evidencia): en el servidor, antes del `checkout`, `showmigrations pedidos` termina en `[X] 0006` sin `0007`, `pedidos_registroevento` no existe y `migrate --plan` dice `No planned migration operations.`; después del `checkout`, `migrate --plan` lista **solo** `pedidos.0007_registroevento`.
5. **Configuración de pruebas de 02-01** (agregado el 2026-10-25): el bloque 3 de `settings.py` viaja en este despliegue. En el servidor, `check --deploy` antes y después del `checkout` debe dar las mismas advertencias y ningún error nuevo (con `DATABASE_URL`, el nombre de producción no coincide con `test_manzagrafica`). Ambas salidas, resumidas por código, en la evidencia.
6. **Sin líneas duplicadas en `error.log`** (agregado el 2026-10-25, 01-02): la hipótesis es que el cargador WSGI de PythonAnywhere instala un manejador propio en la raíz (explica que hoy lleguen `Internal Server Error` y los INFO de `fontTools` sin `LOGGING`). `LOGGING` reemplaza el manejador de la raíz. Tras el error controlado, cada línea aparece una sola vez y no queda ninguna línea en el formato antiguo (sin `nivel=`) para esa petición.
   **Resultado y corrección (2026-10-25, opción A del desarrollador):** el error queda en dos archivos. En `server.log` (hora de Chile) va nuestra línea con emoji y `clave=valor`, con la traza en la misma línea (`#012`). En `error.log` (UTC) va la misma traza en el formato de PythonAnywhere, sin `nivel=`. La tarea se cumple así: **cada registro aparece una sola vez dentro de cada archivo**, y `error.log` conserva el formato de PythonAnywhere por decisión. El manejador de PythonAnywhere sigue siendo una deducción ([bitacora-01-06-produccion](../../99_bitacora/epica-01-observabilidad/bitacora-01-06-produccion.md)).
7. **Revisión visual de la página 500** (trasladada desde 01-03 el 2026-10-25): la página que muestra el error controlado («Algo salió mal») en escritorio y a 360 px: texto legible, botones «Recargar» e «Ir al inicio» visibles y con foco al recorrerlos con Tab, sin código de error, sin detalles técnicos ni la broma de los correos.
8. **Error controlado** (decisión del desarrollador del 2026-10-25): **abrir la página de eliminar un pago** (`/pagos/eliminar/<id>/`, AUD-02-002). Solo se abre, **nunca se confirma**: con GET, `eliminar_pago` solo intenta mostrar la plantilla `pedidos/pago_confirm_delete.html`, que no existe, y no escribe nada (tampoco un evento: `pago_eliminado` se registra solo con POST).
   - **Qué `id` usar:** el `1056`, el pago del caso real del 2026-10-22, si todavía existe; si no, el pago de mayor `id`. La evidencia trae el comando que lo decide en el servidor.
   - **Cómo confirmar antes que el caso sigue existiendo:** en el servidor, después del `checkout`, que la plantilla no exista (`test -f` responde «falta») y que el pago elegido exista. En local, la prueba `test_regresion_eliminar_pago_deja_tipo_y_traza` pasa en la lista de comprobación. Si la plantilla existiera (AUD-02-002 corregido antes), detente: hay que elegir otro método.
   - **Medición:** hora de la petición (Chile y UTC) y tiempo hasta encontrar en `error.log` la línea `❌ nivel=ERROR registrador=pedidos.decorators … excepcion=TemplateDoesNotExist` con método, ruta, usuario y traza completa.
   - **Emoji (01-07):** el `❌` va justo después de la fecha que antepone PythonAnywhere, así que los filtros buscan `nivel=…` dentro de la línea y nunca asumen que la línea empieza con el texto del nivel. La línea lleva `❌` y se ve bien en el visor de registros del panel y en la consola Bash. Si la salida no admite UTF-8, el riesgo no es solo el emoji: `logging` no puede escribir **la línea completa** (`UnicodeEncodeError`), informa «--- Logging error ---» y la petición sigue, pero el error se pierde (bitacora-01-07). Por eso C2 debe encontrar la línea con el `❌`; si no aparece ninguna línea nueva o aparece «Logging error», detente: el agente propone el ajuste (por ejemplo, reemplazar los caracteres no codificables). `error.log` está en UTC y PythonAnywhere antepone su fecha a cada línea; `server.log` está en hora de Chile.
9. **`fontTools`**: generar un PDF de una cotización y comprobar que `error.log` no recibe ninguna línea de `fontTools` después de la recarga (en local, un PDF generaba 540 líneas antes de 01-02).
10. **Evento en el admin**: el propio inicio de sesión del desarrollador deja un `acceso_exitoso` con su usuario; se revisa en el admin de eventos (01-05). Sin cambiar datos de negocio. Además, `python manage.py purgar_registros` una vez en el servidor (esperado: `Eventos eliminados: 0`).
11. **`django.server` solo existe en `runserver`** (hallazgo de 01-02 y 01-05): en producción no hay líneas de `django.server`; los accesos siguen en `access.log` (uWSGI) y los 404 no van a `error.log` (decisión del 2026-10-25). La evidencia lo comprueba con un conteo de `registrador=django.server` en `error.log` (esperado: 0).
12. **Una semana después** (parte D de la evidencia): filas nuevas de eventos por tipo y por día, peso de la tabla, líneas de `error.log` por nivel y por registrador, y contraste con la estimación de 01-01 (~1.200 filas y ~0,6 MB por mes; ~40 filas por día). Si el crecimiento real supera la estimación, proponer el ajuste del inventario antes de cerrar.
13. **`verificar_respaldo.py` con la tabla de eventos, justo después de migrar** (decisión del desarrollador del 2026-10-25; parte B8 de la evidencia):
   - Cuando B4 confirme `[X] 0007_registroevento` en producción, el agente agrega `pedidos_registroevento` a `TABLAS_ESPERADAS` de `scripts/verificar_respaldo.py` (de 18 a 19 tablas). **No antes:** el respaldo previo (tarea 2) tiene 18 tablas y fallaría.
   - **Prueba con volcados sintéticos**, fabricados en el scratchpad y fuera del repositorio, como en 00-02: uno **con** la tabla de eventos (código `0`, 19 de 19) y otro **sin** ella (código `1`, «1 tabla(s) faltante(s)»). Además, el respaldo previo real de la tarea 2, verificado de nuevo, debe dar código `1` por la tabla faltante: confirma que ese volcado es anterior al despliegue.
   - `docs/operacion/respaldo.md`, sección 3: «las 18 tablas esperadas» pasa a «las 19 tablas esperadas (18 hasta `v0.2-correcciones`; `pedidos_registroevento` desde `v1.1-observabilidad`)», con una nota de que los volcados previos a `v1.1-observabilidad` se verifican con la versión anterior del script (`git show v0.2-correcciones:scripts/verificar_respaldo.py`). Las filas ya registradas y `bitacora-00-02` no se reescriben.
   - El script corre en el PC del desarrollador, no en el servidor: el cambio va en un commit posterior a la etiqueta y no requiere otro despliegue.
   - El respaldo semanal de la parte D se verifica con el script nuevo (19 de 19).

14. **Registro**: fila en `docs/operacion/despliegue.md`, sección 5 (y la de `v0.2-correcciones`, que no figura); bitácora de producción `bitacora-01-06-produccion.md` con el contraste de la semana.

## Decisiones del desarrollador (2026-10-25)

1. **Error controlado:** abrir la página de eliminar un pago, sin confirmar (tarea 8).
2. **Ventana del despliegue:** hoy, domingo 2026-10-25; el negocio cierra el sábado en la tarde y no hay uso hasta el lunes. La etiqueta se crea ese mismo día.
3. **`verificar_respaldo.py`:** la tabla de eventos se agrega en esta iteración, justo después de migrar (tarea 13).

No quedan decisiones abiertas.

## Criterios de aceptación

- [x] La lista de comprobación previa está completa en la bitácora (79 pruebas, `check --deploy`, `makemigrations --check`, `sqlmigrate` de la 0007 con su SQL y su clase) y el respaldo está verificado. Evidencia A1 (filas 1 a 5: `Ran 79 tests` `OK`; 5 avisos; `No changes detected`; SQL **idéntico carácter por carácter** al de bitacora-01-06 y bitacora-01-01, comparado por el agente; Clase 2) y A2 (`VÁLIDO`, 18 de 18, código 0).
- [x] El ensayo en la réplica está medido: restauración del respaldo previo, aplicación de la 0007, reversión a la 0006 y nueva aplicación, todo sin errores. Evidencia A3 (código 0, 3,6 s, 18 tablas, tabla `False`) y A4 (1,46 s, 1,07 s y 1,78 s, todo `OK`).
- [x] La evidencia prueba que la 0007 no estaba aplicada en producción antes del `checkout` y que `migrate --plan` listaba solo la 0007. Evidencia B2 (`[X] 0006` sin 0007, `tabla_eventos: False`, `No planned migration operations.`) y B4 (solo `pedidos.0007_registroevento`).
- [x] La evidencia muestra la etiqueta `v1.1-observabilidad`, la migración aplicada en producción y `check --deploy` del servidor sin errores nuevos. Evidencia A5 (objeto de la etiqueta `45817771…` sobre `d6768d0`, igual al `git rev-parse` local del agente), B3 (servidor en `d6768d0`) y B4 (`[X] 0007_registroevento`; los mismos 4 códigos que en B2; `ERRORS`: 0).
- [x] El error controlado aparece en el registro de producción con tipo de excepción, traza completa, método, ruta, usuario y hora. Corregido el 2026-10-25 por la opción A: la línea con todo el contexto está en `server.log`; `error.log` tiene la traza y la hora, sin método ni usuario. Evidencia C2 (cabecera del decorador con `metodo=GET ruta=/pagos/eliminar/1056/ usuario=1 excepcion=TemplateDoesNotExist` a las 21:40:36; traza completa en ambos archivos).
- [x] El tiempo de diagnóstico medido es menor a cinco minutos. Evidencia C2, última fila: unos 2 minutos (error a las 21:40:36; causa y traza a la vista a las 21:42; medido con el reloj del desarrollador).
- [x] Cada registro del error controlado aparece una sola vez dentro de cada archivo. Corregido el 2026-10-25 por la opción A: `error.log` conserva el formato de PythonAnywhere por decisión (tarea 6). Evidencia C3 (`server.log`: 2 líneas de la ruta, las 2 con `❌`; `error.log`: 1 mensaje del decorador, 1 `Internal Server Error`, 1 traza y 1 `TemplateDoesNotExist`; 14 líneas en total desde `DESDE`, exactamente la composición esperada).
- [x] La página 500 se revisó en escritorio y a 360 px. Evidencia C1 (texto correcto, se ve bien en ambos anchos y el foco es visible en «Recargar» e «Ir al inicio»).
- [x] Después del despliegue, ni `error.log` ni `server.log` tienen líneas de `fontTools` ni de `django.server`. Evidencia C4 (PDF `GET /cotizaciones/27/pdf/ 200` a las 00:54:55 UTC, dentro del período; `fontTools`: 0 en ambos archivos; `registrador=django.server`: 0 en `server.log`). En `error.log` no se contó `django.server` por separado, pero sus 14 líneas desde `DESDE` son todas del error controlado (C3), así que no hay ninguna.
- [x] Una acción real o de prueba aparece en el admin de eventos con su usuario, y `purgar_registros` corrió en el servidor. Evidencia C5 (un acceso fallido y un acceso exitoso, con usuario y hora `UTC-0300`; `Eventos eliminados: 0 …`; sin `pago_eliminado`). La tabla vacía tras B7 se explica porque se usó una sesión ya abierta (confirmado por el desarrollador).
- [x] Las líneas de `server.log` de producción llevan su emoji (01-07) y no hay líneas `Logging error` ni `UnicodeEncodeError` en `server.log` ni en `error.log` (corregido el 2026-10-25: el emoji no aparece en `error.log`, que conserva el formato de PythonAnywhere). Evidencia C2 (las dos cabeceras empiezan con `❌` y se ven bien en el visor del panel) y C3 (líneas con `nivel=` sin emoji: 0; `Logging error` o `UnicodeEncodeError`: 0 en `server.log` y 0 en `error.log`).
- [ ] El crecimiento de una semana de la tabla de eventos está medido en filas y MB y comparado con la estimación. **Pendiente: parte D**, hacia el domingo 2026-11-01.
- [x] `verificar_respaldo.py` exige la tabla de eventos después de migrar: volcado sintético con la tabla, código 0; sin ella, código 1; `respaldo.md` actualizado. Evidencia B8: pruebas sintéticas del agente, y verificación del desarrollador en su PC con el respaldo de A2 (18 de 19, falta `pedidos_registroevento`, `NO VÁLIDO`, código 1, SHA-256 `f3163addfce2…`, el mismo de A2).

## Fuera de alcance

- Corregir el error usado para la validación (AUD-02-002 se corrige en 04-01).
- La revisión periódica de `error.log` (va en 07-03).
- El informe de desconexiones a 28 días de 00-06 (C2, 2026-11-20), que sigue en paralelo.

## Datos requeridos del cliente

- Ninguno. Conviene avisar a Manza Gráfica de la ventana del despliegue (unos minutos de recarga).
