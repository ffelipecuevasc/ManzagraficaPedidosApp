# Iteración 04-05 · Correcciones de configuración

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** **Completada y verificada en producción (2026-11-19, 23:06 Chile = 2026-11-20 02:06 UTC)** con `v4.7-correcciones-config` (`7187d03`); detalle en «Despliegue y verificación». Retroceso vigente desde aquí: `v4.7-correcciones-config` (el previo, `v4.6-restauracion`). AUD-01-016 queda con los puntos 1 y 2 verificados y la hibernación como observación posterior. ~~Implementada, pendiente de despliegue (2026-11-19)~~ ([bitacora-04-05](../../99_bitacora/epica-04-seguridad/bitacora-04-05.md)). ~~Etiqueta prevista `v4.7-correcciones-config`, sin fecha fija (RDA-021); retroceso `v4.6-restauracion`. Pendiente del desarrollador: la revisión manual en la réplica (`despliegue.md`, 3.12 A) y el despliegue (3.12 B).~~ La hibernación (verificación 3) es observación posterior que no bloquea el cierre (decisión del 2026-11-19). D5 de la 04-03 sigue `PENDIENTE_DESARROLLADOR`. ~~Pendiente (redactada, decisiones resueltas).~~ Redactada el 2026-11-17 ([bitacora-04-05-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-05-redaccion.md)); D1 a D4 resueltas por el desarrollador el mismo día ([bitacora-04-05-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-05-cierre.md)).
- **Subfase del plan:** 4.5 «Correcciones de configuración» (`plan-de-trabajo.md`; `definicion-epica-04.md`, alcance 5).
- **Depende de:** 04-02 (también edita `settings.py`: `SEGURIDAD_PRODUCCION`, HSTS, `CSRF_TRUSTED_ORIGINS`) y 04-04 (también edita `views.py` y `utils.py` en la restauración). Se redactó en paralelo a la vigilancia de la 03-05; ~~**su ejecución en local no empieza hasta cerrar esa vigilancia** (decisión del desarrollador, 2026-11-17). **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).**~~ **Superado el 2026-11-18 (RDA-021): no hay vigilancia que cerrar; la 14-01 se despliega antes de la 04-01 (RDA-022).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → 04-10 → 04-02 → 04-03 → 04-04 → **04-05**.
- **RDA relacionadas:** RDA-007 (un despliegue, un propósito).
- **Hallazgos que cierra:** AUD-01-009 (`from PedidosApp import settings`), AUD-01-016 (`CONN_HEALTH_CHECKS`), AUD-01-025 (importaciones duplicadas y código muerto) y AUD-02-016 (`TEMPLATES['DIRS']` y `BASE_DIR` duplicado). Además, la parte (2) de AUD-05-008 (ver «Contradicciones»).
- **Clase de cambio:** **Clase 1** en el sentido amplio de esta épica: sin cambios de comportamiento visibles ni de base de datos, **sin migraciones**. `CONN_HEALTH_CHECKS` cambia cómo se reutiliza la conexión, no qué datos se leen ni se escriben.
- **Respaldo previo al despliegue:** sí, el de rutina (`respaldo.md`); no hay migraciones.
- **Archivos que tocará la ejecución:** `PedidosApp/settings.py` (**consulta previa**, `AGENTS.md` sección 6), `pedidos/views.py`, `pedidos/urls.py`, `pedidos/utils.py` y las pruebas que parchan `views.settings` (lista abajo).

## Objetivo

Que la aplicación lea la configuración como manda Django, que sobreviva a una conexión muerta tras la hibernación y que `settings.py`, `views.py` y `urls.py` no arrastren duplicados ni restos que confundan a quien los lea, sin cambiar nada de lo que ve el usuario.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main` (después de `526bdcb`), con archivo y línea, por búsqueda (`grep`) y lectura.
- **Inferido:** sale de leer el código o la documentación de Django; se dice cómo se confirma.
- **No verificado (producción):** solo se ve en el servidor.

## Qué hay hoy (verificado)

### Importación de la configuración (AUD-01-009 y AUD-05-008, parte 2)

- `pedidos/views.py:19`: `from PedidosApp import settings`. Es el **único** archivo de la aplicación que lo hace; `utils.py:5`, `urls.py` del proyecto (`PedidosApp/urls.py:20`) y las pruebas ya usan `django.conf.settings`. `wsgi.py`, `asgi.py` y `scripts/diagnostico/paridad_replica.py` solo nombran el módulo en `DJANGO_SETTINGS_MODULE`, que es lo correcto.
- `views.py` usa `settings` solo para `settings.BASE_DIR` (`:81`, `:1194`, `:1265`, `:1331`).
- **Seis pruebas parchan `views.settings.BASE_DIR`** con `mock.patch.object`: `test_acceso.py:73`, `test_capturas_amplias.py:57`, `test_contrato_error.py:54` y `:68`, `test_dinero.py:294`, `test_eventos_negocio.py:154`. Con el módulo importado, el parche solo afecta a `views.py`; con `django.conf.settings`, el mismo parche cambiaría `BASE_DIR` para todo el proceso mientras dura (inferido del funcionamiento de `LazySettings`; se confirma corriendo la suite). Por D2 pasan a `override_settings`.

### Conexión a la base (AUD-01-016)

- `settings.py:130-136`: con `DATABASE_URL` (producción), `dj_database_url.config(conn_max_age=60, ssl_require=False)`, **sin** `conn_health_checks`. Con conexiones persistentes de 60 s y un worker que hiberna, la primera petición tras la inactividad puede recibir una conexión cerrada por MySQL (inferido; consistente con el episodio de hibernación del plan).
- En local (`settings.py:115-124`) no hay `CONN_MAX_AGE`: cada petición abre y cierra su conexión, así que el chequeo no tiene efecto ahí (inferido de la documentación de Django).

### `settings.py` (AUD-02-016)

- **`BASE_DIR` definido dos veces**, con el mismo valor: `:21` (con los comentarios «1.», «2.», «3.» de carga del `.env`) y `:30` (comentario de plantilla de Django en `:29`).
- **`TEMPLATES['DIRS']`** (`:84`) apunta a `BASE_DIR / 'templates'`, con una coma suelta en la línea `:85`. **Matiz:** la carpeta `templates/` **existe vacía en esta copia de trabajo** y **no está en Git** (Git no versiona carpetas vacías; `git ls-files templates` no devuelve nada). En un clon limpio no existe. Django no falla por una carpeta inexistente en `DIRS`; solo la busca en cada carga de plantilla (inferido).
- `MEDIA_ROOT` (`:204`) usa `os.path.join` y el resto `Path`: estilo, no defecto. **Fuera** (ver «Alcance»).

### Importaciones duplicadas y sin uso (AUD-01-025)

Búsqueda por nombre en el cuerpo de cada archivo, sin contar la línea de importación:

| Archivo y línea | Hallazgo |
| :-------------- | :------- |
| `pedidos/views.py:6` | `F` importado **dos veces** en la misma línea (`Q, Count, Sum, F, ProtectedError, F, Value, IntegerField`). |
| `pedidos/views.py:8` | `HttpResponseForbidden` importado y **sin uso** (0 apariciones en el resto del archivo). |
| `pedidos/urls.py:2` | `from .views import respaldar_bd, generar_respaldo_bd` **redundante**: las rutas usan `views.respaldar_bd` y `views.generar_respaldo_bd` (`:48-49`) a través de `from . import views` (`:3`). |

Las demás importaciones de `views.py`, `utils.py`, `models.py`, `forms.py`, `admin.py`, `eventos.py`, `senales.py`, `registro.py` y `envio_unico.py` **tienen uso** según la búsqueda.

### Código muerto

| Archivo y línea | Hallazgo |
| :-------------- | :------- |
| `pedidos/utils.py:25` | Línea comentada `# db_port = db_config.get('PORT', '3306') ...`: código comentado. **Ojo:** `mysqldump` y `mysql` hoy no reciben el puerto; si producción usa uno distinto del 3306 importaría, pero no es el caso conocido (no verificado). Se borra la línea; pasar el puerto sería cambio de comportamiento y queda fuera. |
| `settings.py:29` | Comentario de plantilla que acompaña al `BASE_DIR` duplicado: se va con él. |

- **Funciones sin uso:** ninguna. Toda función de nivel superior de `views.py`, `utils.py` y `forms.py` aparece en `urls.py`, otra función o una plantilla.
- **`@login_required` sobre `es_superusuario`** (nota de AUD-01-025, H3 de la 02-05): **hoy ya no está** (`views.py:1176`, sin decorador). No se buscó en qué commit se quitó. La nota de la auditoría queda desactualizada y se corrige al cerrar la iteración.

### Fuera, aunque aparezca en la búsqueda

- `TruncMonth` (`views.py:7`, usado en `:561`) contradice `AGENTS.md`, regla 8.6, pero corregirlo cambia una consulta: no es Clase 1 ni de esta iteración. Se anota como propuesta para la Épica 06.
- Estilos `animate-pulse` y `text-red-500` (AUD-05-008, parte 1): Épica 08.

## Contradicciones con la planificación

- **AUD-05-008 asigna `views.py:19` a la Épica 08; AUD-01-009 lo asigna a la 04-05.** Es el mismo defecto con dos IDs. **Decisión del agente, con evidencia:** corresponde a la **04-05**, porque (1) AUD-01-009 es anterior, de severidad Alta y ya nombra esta iteración; (2) el plan (4.5) y la definición (alcance 5) lo ponen aquí; (3) es configuración, no interfaz, y la Épica 08 no toca `views.py` por eso; (4) la Épica 08 parte de lo que deje la 04-05. **Aviso:** al cerrar la 04-05, AUD-05-008 se edita para que su parte (2) remita a AUD-01-009 (corregido en la 04-05) y la Épica 08 conserve solo la parte (1). No se duplica trabajo. La redacción ya anota esto en la auditoría como nota.
- **AUD-02-020 prometía probar el modo estricto de `sql_mode` «en 04-05»** (también `iteracion-02-01:39` y `:71`, `definicion-epica-02.md:158`, documentos cerrados que no se reescriben). Resuelto por D4: sale de la 04-05 y pasa a la Épica 06 como medición; AUD-02-020, la definición de la Épica 06 y el registro ya lo dicen.
- **«`TEMPLATES['DIRS']` inexistente»:** en el repositorio es cierto; en esta copia de trabajo hay una carpeta vacía sin versionar. Por D1, `DIRS` queda vacío y la carpeta local no se toca (no se borra ni se versiona).
- **H3 de la 02-05 ya está corregido** en el código (ver «Código muerto»).

## Alcance

1. `views.py:19` → `from django.conf import settings`; las seis pruebas que parchan `views.settings` pasan a `override_settings(BASE_DIR=...)` (D2).
2. `conn_health_checks=True` en `dj_database_url.config`, manteniendo `conn_max_age=60` (D3).
3. `BASE_DIR` una sola vez, con sus comentarios ordenados.
4. `TEMPLATES['DIRS']` vacío (`[]`) hasta la 08-02 (D1), sin la coma suelta.
5. Importaciones: `F` una vez y sin `HttpResponseForbidden` (`views.py`); sin la importación redundante de `urls.py:2`.
6. ~~Código comentado de `utils.py:25`.~~ **Retirado el 2026-11-19** (decisión del desarrollador): la línea ya no existe en `main`.
7. **Coordinación con la 04-02:** la 04-05 se desarrolla **sobre** la 04-02 ya integrada en `main` y no toca sus bloques (`SEGURIDAD_PRODUCCION`, HSTS, cookies, `CSRF_TRUSTED_ORIGINS`, regla de arranque). Si la 04-02 no está integrada al empezar, se espera.
8. **Fuera:** modo estricto de `sql_mode` (Épica 06, D4), `TruncMonth` (Épica 06), `MEDIA_ROOT` con `Path`, AUD-05-008 parte (1) (Épica 08), crear contenido en `templates/` (Épica 08, 08-02), traducir comentarios de plantilla de Django.

## Decisiones (resueltas por el desarrollador, 2026-11-17)

| # | Decisión | Resuelta como |
| :- | :------- | :------------ |
| D1 | `TEMPLATES['DIRS']` | **Vacío (`[]`) hasta la 08-02**, que lo vuelve a apuntar a `BASE_DIR / 'templates'` cuando cree la carpeta con contenido. |
| D2 | Pruebas que parchan `views.settings.BASE_DIR` | Las seis pasan a **`override_settings(BASE_DIR=...)`** (o `self.settings(...)`), para aislar el cambio. |
| D3 | Salud de la conexión | **`conn_health_checks=True`**, manteniendo **`conn_max_age=60`**. Sin efecto en local. |
| D4 | Modo estricto de `sql_mode` (AUD-02-020) | **Sale de la 04-05** y pasa a la **Épica 06 como medición** contra la réplica, sin cambio en producción (iteración por definir). |

## Pasos

0. **Consulta previa para editar `settings.py`** (`AGENTS.md`, sección 6): las decisiones de esta iteración no la reemplazan; se pide al empezar la ejecución. Confirmar que la 04-02 está integrada en `main`.
1. Línea base: `test pedidos` (número de pruebas y fallos esperados tras la 04-04), `check`, `check --deploy` con `DEBUG=False`, `makemigrations --check --dry-run`. Se anotan en la bitácora.
2. Pruebas de D2 y de D3 (tabla siguiente): primero las seis pasan a `override_settings` con el import viejo y siguen en verde; después se cambia `views.py:19`.
3. Cambios del alcance, uno por uno, corriendo la suite tras cada uno.
4. Repetir el paso 1: mismos resultados, y `diff` de las salidas.
5. Revisión manual en la réplica: panel, una lista, un detalle, `respaldar_bd` y `restaurar_bd` (solo carga), y el PDF de una cotización; escritorio y 360 px.
6. Bitácora, registro, auditoría (AUD-01-009, AUD-01-016, AUD-01-025, AUD-02-016 y la parte 2 de AUD-05-008), estado «En revisión».

## Cómo se comprueba que es Clase 1

| Comprobación | Esperado |
| :----------- | :------- |
| `python manage.py test pedidos` | Mismo número de pruebas y **los mismos** fallos esperados que antes (más las pruebas nuevas en verde). |
| `python manage.py makemigrations --check --dry-run` | «No changes detected», antes y después. |
| `python manage.py check` y `check --deploy` (`DEBUG=False`) | Misma salida que la línea base (ninguna advertencia nueva ni perdida). |
| `python -c` con `django.setup()` que imprime `settings.BASE_DIR`, `TEMPLATES`, `DATABASES['default']['CONN_MAX_AGE']` y `CONN_HEALTH_CHECKS` | Mismo `BASE_DIR`; `DIRS == []`; con `DATABASE_URL`, `CONN_MAX_AGE == 60` y `CONN_HEALTH_CHECKS is True`. |
| Plantillas | Toda pantalla de la revisión manual carga: confirma que ninguna plantilla vivía en `templates/` de la raíz (hoy vacía). |
| Búsqueda | `grep -rn "from PedidosApp import" pedidos` sin resultados; ninguna importación duplicada en las líneas de la tabla. |
| Revisión manual (paso 5) | Pantallas idénticas a la línea base. |

## Pruebas

| Punto | Prueba |
| :---- | :----- |
| 1 · `django.conf.settings` | Las seis pruebas (`test_acceso.py:73`, `test_capturas_amplias.py:57`, `test_contrato_error.py:54` y `:68`, `test_dinero.py:294`, `test_eventos_negocio.py:154`) usan `override_settings(BASE_DIR=...)` y siguen en verde; una prueba comprueba que `views.settings is django.conf.settings`. |
| 2 · Salud de la conexión | Con una `DATABASE_URL` de ejemplo (sin credenciales reales) en el entorno de un subproceso, la configuración resultante trae `CONN_HEALTH_CHECKS=True` y `CONN_MAX_AGE=60`; sin ella, la configuración local no cambia. No hay prueba automática de la reconexión tras hibernar: se observa en producción. |
| 3 a 6 | Sin prueba propia: los cubre la suite completa y la tabla de Clase 1. |

## Implementación (2026-11-19)

**Decisiones del desarrollador del 2026-11-19 (dichas por él):** consulta previa aprobada para `settings.py`, solo para `conn_health_checks`, `BASE_DIR`, `DIRS` y la coma suelta, sin tocar los bloques de la 04-02; D2 cubre **nueve** pruebas, no seis; el punto 6 del alcance queda **retirado** (la línea `db_port` de `utils.py` ya no existe); la verificación 3 (hibernación) es observación posterior que no bloquea el cierre, y los puntos 1 y 2 se verifican el mismo día.

**Correcciones a la redacción:**

- Líneas al 2026-11-19: import en `views.py:21` (no `:19`); `DIRS` en `settings.py:141` (no `:84`); `conn_max_age` en `:191` (no `:130-136`); `TruncMonth` usado en `views.py:611`.
- Las pruebas que parchaban `views.settings.BASE_DIR` eran **nueve** en siete archivos: las seis de la redacción (con `test_contrato_error.py:53` y `:66`) más `test_eventos_negocio.py:165`, `test_regresiones.py:257` y `test_restauracion_endurecida.py:168` (este último, en un ciclo de parches de la 04-04). Verificado con `grep`.
- **El orden del paso 2 no era posible:** con el import viejo, `override_settings` cambia `django.conf.settings` pero `views.py` seguía leyendo el módulo, así que las pruebas habrían usado el `backups/` real. Se cambió primero el import (las pruebas con `mock.patch.object` siguen funcionando sobre `django.conf.settings`, suite en verde) y después las nueve pruebas.
- La comprobación con `python -c` choca con `AGENTS.md`, sección 5: se hizo con un script en la carpeta temporal del agente.
- `utils.py:151` lee `BASE_DIR` de `django.conf.settings`: con `override_settings` también usa la carpeta temporal, que es lo buscado.

**Cambios:**

- `pedidos/views.py`: `from django.conf import settings`; `F` una vez; sin `HttpResponseForbidden`.
- `pedidos/urls.py`: sin `from .views import respaldar_bd, generar_respaldo_bd`.
- `PedidosApp/settings.py`: `BASE_DIR` una vez con sus comentarios ordenados; `DIRS: []` (D1) sin la coma suelta; `conn_health_checks=True` con `conn_max_age=60` (D3). Bloques de la 04-02 y `archivo_opciones_mysql()` de la 04-03 sin tocar.
- Pruebas: las nueve pasan a `self.settings(BASE_DIR=...)` (D2); `test_dinero.py` pierde las importaciones `mock` y `views` que quedaron sin uso; nueva `test_configuracion.py` (4 pruebas: `views.settings is django.conf.settings`, `DIRS` vacío, salud de la conexión con `DATABASE_URL` de ejemplo y local sin cambios). Las dos de `DIRS` y de salud se vieron fallar antes del cambio.
- Resultados antes y después: tabla en la bitácora.

## Verificación en producción (la hace el desarrollador; **no verificado** hasta entonces)

0. Orden y comandos: `despliegue.md`, 3.12 B (respaldo **antes** del checkout, `check --deploy` antes del Reload, **un solo** Reload confirmado con `Starting uWSGI`).
1. Respaldo previo (`respaldo.md`).
2. Tras el Reload: acceso, panel, una lista y el PDF de una cotización responden como antes.
3. Dejar hibernar la aplicación y volver a entrar: la primera petición responde sin error 500; `server.log` sin `OperationalError` ni «MySQL server has gone away» (que hoy no sabemos si ocurre: no verificado).
4. `server.log` sin errores nuevos ~~durante tres días~~ **desde el reinicio efectivo, en la verificación del mismo día (RDA-021, 2026-11-18)**.

## Despliegue y verificación (2026-11-19, datos pegados o dichos por el desarrollador)

Horas: consola en UTC; `server.log` en hora de Chile (UTC−3).

| Paso | Resultado |
| :--- | :-------- |
| Réplica (3.12 A) | 379 pruebas, `OK (expected failures=4)`; `backups/` real con 1 archivo antes y después de la suite; paridad sin diferencias no aceptadas; pantallas en escritorio y a 360 px sin 500 (dicho; el agente no las vio). |
| Respaldo previo | Con `v4.6-restauracion` activo y **antes del checkout**: `respaldo_19-11-2026_23-00-20.sql`, `VÁLIDO` (19 de 19), `CUMPLE D2`, 1.549.306 bytes, SHA-256 `607db45f…9b8a`. Lección de la 04-04 aplicada. |
| Etiqueta | `v4.7-correcciones-config` sobre `7187d03`; diff `v4.6…v4.7`: código solo `settings.py`, `views.py` y `urls.py`; sin `requirements.txt`, migraciones ni estáticos. |
| Servidor, antes del Reload | Checkout a las 02:06 UTC (2026-11-20); `check --deploy` solo W005 y W021. |
| Reload | **Un solo** arranque de uWSGI tras el checkout: 23:06:46 Chile (02:06:44 UTC), Reload del desarrollador (dicho). El anterior fue el de las 17:41:57 (04-04). |
| Después del Reload | `check --deploy` (02:15 UTC) solo W005 y W021. Panel, listas, detalle y PDF sin error 500 (dicho). |
| Registros | `error.log` sin errores nuevos tras el Reload. Las 3 coincidencias que aparecen son históricas: `TemplateDoesNotExist` de `pago_confirm_delete.html` del 2026-10-26, anterior a la 04-01. Último `OSError`: 2026-11-18 18:40:18; ninguno el 2026-11-19 (dato para AUD-04-004). Ese tramo del archivo no está en orden cronológico (observado; no se concluye la causa). |
| Hibernación (punto 3) | No observada todavía: observación posterior, no bloquea el cierre (decisión del 2026-11-19). |

**Lección:** el `grep` por fecha al inicio de la línea no detecta las líneas de traza (no empiezan con fecha) y `DESDE_CL` quedó sin definir en la consola. Por eso la revisión de registros de esta ventana descansa en la lectura de `error.log` pegada, no en ese filtro. `despliegue.md`, 3.12 B, paso 6.3, queda corregido: `server.log` desde el último `Starting uWSGI` (con `awk`) y `tail` de `error.log`, sin filtro por fecha.

Criterio de término: cumplido (Clase 1 sin cambios, pruebas, auditoría y puntos 1, 2 y 4 de producción). El punto 3 queda como observación posterior.

## Plan de retroceso

`retroceso.md`, caso 1 (sin migraciones): volver a la etiqueta anterior y Reload. No hay datos que deshacer.

## Criterio de término

- Tabla de Clase 1 con los mismos resultados antes y después, copiada en la bitácora.
- Pruebas en verde, salvo los fallos esperados heredados.
- Auditoría actualizada (incluida la remisión de AUD-05-008 a AUD-01-009 y la nota de H3).
- Verificación de producción hecha (puntos 1 ~~a 3~~ y 2, y el 4 el mismo día; el 3 es observación posterior, decisión del 2026-11-19).

## Riesgos

- **Conflictos con la 04-02 y la 04-04:** las tres tocan `settings.py` o `views.py`. Mitigado con el orden: la 04-05 se desarrolla y despliega después de ambas.
- **`override_settings(BASE_DIR=...)` cambia `BASE_DIR` para todo el código durante la prueba (D2):** es lo buscado (aísla y restaura el valor), pero `utils.py` también escribirá en la carpeta temporal; las pruebas ya usan carpetas temporales, así que no se escribe en `backups/` real (inferido; se confirma con la suite y mirando que `backups/` no cambie).
- **`DIRS` vacío (D1):** si alguna plantilla viviera en `templates/` de la raíz dejaría de encontrarse; hoy la carpeta está vacía y no versionada, así que no hay ninguna (verificado en esta copia).
- **Un cambio «de limpieza» que sí cambia comportamiento:** por eso el puerto de `utils.py:25` no se activa y `TruncMonth` queda fuera.
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-04.
