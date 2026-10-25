# Épica 01 · Observabilidad

- **Estado:** En curso
- **Fase del plan:** 1 (`plan-de-trabajo.md`, «FASE 1»)
- **Objetivo:** dejar de estar ciego, con dos herramientas para dos públicos distintos. **Para el desarrollador:** que todo error de producción quede en el registro de errores de PythonAnywhere (`error.log`) con su traza completa y el contexto de la petición, en un formato ordenado y sin ruido. **Para el negocio:** que las acciones críticas dejen constancia de quién hizo qué y cuándo, consultable en el admin de Django.
- **Precondición:** Épica 00 cerrada (2026-10-25). Puede avanzar en paralelo con la Épica 02; la iteración 01-02 necesita la infraestructura de pruebas de 02-01.
- **Última revisión:** 2026-10-25, rediseño por decisión del desarrollador (ver «Decisiones de la épica»).

## Alcance

1. **Registro de la aplicación (logging):** configuración de `logging` de Python que envía los errores a la salida de error, que PythonAnywhere guarda en `error.log`. Formato `clave=valor` fácil de leer y de filtrar con `grep`, traza completa, sin datos sensibles y sin el ruido de `fontTools`.
2. **Retiro de la supresión de trazas:** se retira `ErrorHandlingMiddleware` y el `print` de `@transaccion_segura` pasa a `logger.exception`, para que ninguna excepción se pierda.
3. **Registro de eventos de negocio:** una tabla nueva (Clase 2) con índices, retención y purga desde el inicio, y un servicio que escribe en ella solo cuando la operación se confirmó.
4. **Instrumentación** del inventario de eventos de negocio.
5. **Consulta de eventos en el admin de Django**, solo lectura y solo superusuarios.
6. **Despliegue y validación activa** en producción.

**Fuera de la épica:** no hay tabla de errores, ni código de error visible para el usuario, ni identificador de petición en los registros.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 01-01 | Modelo de registro de eventos (Terminada) | 1.1 |
| 01-02 | Configuración del registro y servicio de eventos (Terminada) | 1.2 |
| 01-03 | Retiro del middleware y trazas completas (Terminada) | 1.3 |
| 01-04 | Instrumentación de eventos de negocio (Terminada) | 1.4 |
| 01-05 | Consulta de eventos en el admin (Terminada) | 1.5 |
| 01-06 | Despliegue y validación de la observabilidad (redactada, en revisión) | 1.6 |

## Decisiones de la épica

- **2026-10-25 · Errores en el registro del servidor, no en MySQL (RDA-013, decisión del desarrollador).** La observabilidad técnica es responsabilidad del desarrollador, no del usuario final. Los errores se escriben con `logging` a la salida de error (The Twelve-Factor App, factor XI: la aplicación emite sus registros como flujo y el entorno los guarda) y se leen en `error.log` de PythonAnywhere. Se descarta la tabla de errores y el código visible en la página 500 (YAGNI). Con esto desaparecen dos de las cuatro trampas originales: el aislamiento transaccional y la dependencia circular de los errores.
- **2026-10-25 · Eventos en MySQL, consultados en el admin de Django (decisión del desarrollador).** Los eventos son registro de auditoría del negocio («quién hizo qué y cuándo»): se guardan en la base, se respaldan con ella y se consultan en `/admin`. Una pantalla propia con el diseño de la app queda fuera de la épica.
- **2026-10-25 · Los 404 no van a `error.log` (decisión del desarrollador).** `django.request` queda en nivel `ERROR`: los 404 siguen visibles en `access.log`, pero no en `error.log`, porque los rastreadores y bots que piden rutas inexistentes llenarían de ruido el registro de errores. `LOGGING` no cambia.
- **2026-10-25 · Un evento por acción del usuario (decisión del desarrollador, 01-04).** Una operación compuesta deja una sola fila: crear un pedido con abono inicial registra `pedido_creado` («… con abono inicial»), convertir una cotización registra `cotizacion_convertida` (aunque cree pedido, ítems y pago) y restaurar registra `restauracion_ejecutada` (aunque genere antes un respaldo). Mantiene la estimación de 01-01. Consecuencia: filtrar por `pago_registrado` no muestra los abonos iniciales.
- **2026-10-25 · Acceso fallido sin lo escrito (decisión del desarrollador, ajuste de 01-04).** El evento `acceso_fallido` guarda el nombre de usuario solo si existe como usuario (el registrado en la base); si no existe, el resumen dice «usuario desconocido». **Motivo:** que una contraseña escrita por error en el campo de usuario nunca quede en la tabla ni en los respaldos.
- **2026-10-25 · Admin de eventos sin jerarquía por fecha (decisión del desarrollador, 01-05).** `date_hierarchy` agrupa con truncado y conversión de zona horaria en MySQL, contra la regla técnica 6 de `AGENTS.md`. La fecha se filtra con `DateFieldListFilter` (rangos de instantes en hora de Chile).
- **2026-10-25 · Error controlado de la 01-06 (decisión del desarrollador).** Se abre la página de eliminar un pago (`/pagos/eliminar/<id>/`, AUD-02-002) sin confirmar: falla por la plantilla faltante y no escribe nada. `id` 1056 (caso real del 2026-10-22) o el último pago; antes se confirma que la plantilla sigue sin existir.
- **2026-10-25 · Sin identificador de petición (decisión del desarrollador).** Cada línea de error lleva hora, método, ruta y usuario; con eso basta para cruzar `error.log` con `access.log` en una aplicación de este tamaño.
- Las iteraciones 01-01 a 01-05 se trabajan en local, contra la réplica, y se despliegan **juntas** en 01-06 con la etiqueta `v1.1-observabilidad` (RDA-007: cada fase parte en `.1`). La migración de la tabla de eventos va en un único despliegue con respaldo previo.
- Mientras exista `@transaccion_segura` (hasta la Épica 03), el decorador captura las excepciones antes de que lleguen a Django. Por eso 01-03 cambia su `print` por `logger.exception`, sin tocar todavía su lógica.

## Documentos que la épica debe ajustar

- `decisiones.md`: escribir **RDA-013** («Errores en el registro del servidor con `logging`; eventos de negocio en MySQL») y marcar RDA-005 como «Reemplazada en parte por RDA-013». RDA-008 sigue vigente para los eventos (01-01, tarea 1).
- `auditoria-tecnica.md`: actualizar la solución de AUD-01-005 según RDA-013 (01-01, tarea 1).
- `registro-pendientes.md`: la decisión «Retención de las tablas de errores y de eventos» pasa a ser solo de eventos; la del «método para provocar el error controlado» se mantiene para 01-06.
- `plan-de-trabajo.md` menciona el identificador de correlación y las tablas de registro en fases posteriores (por ejemplo, el contrato de error hacia el usuario de la Fase 3 y los índices de la Fase 5). No se reescribe ahora: cuando esas épicas se detallen, se aplican según RDA-013.
- **`PENDIENTE_DESARROLLADOR` · `AGENTS.md`, regla 4:** habla del «servicio de registro del proyecto». Sigue siendo compatible (ahora es `logging` para errores y el servicio de eventos para el negocio), pero si el desarrollador quiere precisar el texto, la edición es suya: `AGENTS.md` es inmutable para el agente. El agente propone el texto en la bitácora de 01-03 (propuesta escrita el 2026-10-25, [bitacora-01-03](../../99_bitacora/epica-01-observabilidad/bitacora-01-03.md)).

## Datos conocidos al iniciar (Épica 00)

- **Hora de los registros de PythonAnywhere:** `error.log` y `access.log` están en **UTC**; `server.log` está en **hora de Chile** (comprobado el 2026-10-25: el error de `/pagos/eliminar/1056/` figura a las 19:19 en `error.log` y a las 16:19 en `server.log`; el Reload de la 00-06 figura a las 18:34 en `server.log`, hora chilena). PythonAnywhere antepone su propia fecha a cada línea de `error.log`.
- **Ejemplo real del problema (2026-10-22):** `error.log` solo dice `Internal Server Error: /pagos/eliminar/1056/` y `server.log` solo dice `⚠️ Error capturado por decorador en eliminar_pago: pedidos/pago_confirm_delete.html`. No hay traza, tipo de excepción ni usuario. Es AUD-02-002; sirve de caso de prueba para 01-03 y de candidato para el error controlado de 01-06.
- **Ruido:** la mayoría de las ~1.100 líneas de `error.log` revisadas el 2026-10-25 son mensajes informativos de `fontTools` al generar PDFs.
- **Disco:** 180,8 MB usados de 512 MB (2026-10-20); base de ~2,2 MB; volcado más reciente de ~1,44 MB (`linea-base-produccion.md`).
- **Despliegue:** protocolo de `docs/operacion/despliegue.md` y `retroceso.md`; producción en `v0.2-correcciones`.

## Pistas registradas para la épica

Observaciones de otras iteraciones que la épica debe revisar. Son hipótesis, no hallazgos confirmados.

- **2026-10-23 (00-05):** el `OSError: write error` del 2026-10-23 a las 02:56:38 UTC ocurrió 2 segundos después de generar un respaldo (`respaldo_22-10-2026_23-56-36.sql`, hora de Chile) y coincide con su descarga. Es de la misma familia que los `Broken pipe` y `SIGPIPE` medidos en 00-01. Hay que comprobar si esos cortes se relacionan con la descarga de respaldos (evidencia-00-05, B10).
- **2026-10-23 (00-05):** los mensajes informativos de `fontTools` al generar PDFs con WeasyPrint llegan a `error.log` y lo ensucian. Se resuelven en 01-02 subiendo ese registrador a `WARNING`. **Actualización 2026-10-25 (01-02):** el nivel no bastaba; WeasyPrint baja `fontTools` a `DEBUG` durante el recorte de fuentes (`capture_logs`) sin cortar la propagación. Se resolvió con `propagate=False` (ver bitacora-01-02).
- **2026-10-25:** con las trazas completas de 01-03 en producción, el próximo error «Template: …» de `crear_pedido`, `crear_cotizacion` o `crear_cliente` dejará su causa en `error.log`. Eso desbloquea AUD-02-021, que hoy espera el mensaje completo.
- **2026-10-25:** el conteo de `Broken pipe` por fecha de la 00-06 usó `server.log`, que está en hora de Chile y no en UTC. No cambia la conclusión de C1, pero el conteo de C2 (2026-11-20) debe decirlo.
- **2026-10-25 (01-02):** sin `LOGGING`, en local y con `DEBUG=False` no llega a stderr ni el `Internal Server Error` de `django.request` ni el INFO de `fontTools`, pero en producción sí. Hipótesis: el cargador WSGI de PythonAnywhere instala un manejador en la raíz con nivel INFO. La configuración de 01-02 reemplaza el manejador de la raíz, así que en 01-06 hay que comprobar que `error.log` no tenga líneas duplicadas.

## Criterio de término

- Un error real en producción se diagnostica en menos de cinco minutos desde `error.log`: tipo de excepción, traza completa, método, ruta, usuario y hora, medido en 01-06.
- `error.log` no tiene líneas informativas de `fontTools` después del despliegue.
- Una semana después del despliegue, el crecimiento real de la tabla de eventos está medido y dentro de la estimación de 01-01 (o el inventario se ajustó).