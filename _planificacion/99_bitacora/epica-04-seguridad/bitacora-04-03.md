# Bitácora 04-03 · Credenciales y secretos

- **Fecha:** 2026-11-19
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Implementada, pendiente de despliegue. Etiqueta prevista `v4.5-credenciales`, sin fecha fija (RDA-021); retroceso `v4.4-hsts-semana`.
- **Regla de la iteración:** ningún valor de clave o contraseña, actual o del historial, aparece en este documento ni en las salidas que vio el agente.

## Resumen

D1: `mysqldump` y `mysql` reciben la contraseña en un archivo temporal de opciones (`--defaults-extra-file`, primer argumento), creado con `mkstemp` (solo el dueño) fuera de `backups/` y borrado en `finally`. D2: sin `SECRET_KEY` no arranca en ningún entorno; con `SEGURIDAD_PRODUCCION`, además se exige la regla de W009 (50 caracteres, 5 distintos, sin `django-insecure-`). Pruebas primero. Sin migraciones. Falta el ensayo en la réplica y la verificación en producción.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/utils.py` | Ayudante `archivo_opciones_mysql()`; respaldo y restauración lo usan (CRLF conservado). |
| `PedidosApp/settings.py` | Bloque «Clave secreta obligatoria» después del bloque de la 04-02 (CRLF conservado). Consulta previa aprobada el 2026-11-19. |
| `pedidos/tests/test_credenciales.py` | Nuevo: 15 pruebas (8 del archivo de opciones, 7 de la clave en proceso hijo). |
| `pedidos/tests/test_seguridad_produccion.py` | Los procesos hijos reciben una clave válida generada: ya no dependen de la del `.env` local. |
| `docs/operacion/despliegue.md` | Advertencias esperadas desde la 04-03; medición de la clave en 3.1 bis; fila «pendiente de despliegue» en la sección 5 (CRLF). |
| `_planificacion/10_epicas/epica-04-seguridad/iteracion-04-03-credenciales-y-secretos.md` | Estado, corrección de las advertencias esperadas, implementación, verificación 0. |
| `_planificacion/10_epicas/epica-04-seguridad/definicion-epica-04.md` | Estado de la 04-03. |
| `_planificacion/00_producto/registro-pendientes.md` | Estado, dos pendientes nuevos, historial (CRLF). |
| `.env.example` | **No editado** (decisión del desarrollador). Texto propuesto, abajo. |

## Verificación

- Línea base: `python manage.py test pedidos` → 327 pruebas, `OK (expected failures=4)`.
- Pruebas nuevas antes del cambio: 15, `FAILED (failures=3, errors=7)`. Las 5 que ya pasaban: las dos «sin clave» (Django ya fallaba, con su mensaje genérico; se agregó la comprobación del mensaje propio y entonces falló), la clave válida, la clave débil en local y «el error no trae la contraseña».
- Primer intento con el cambio: 5 errores en las pruebas de clave porque el hijo escribía el mensaje (con tildes) en cp1252; se fijó `PYTHONIOENCODING=utf-8` en el entorno del hijo.
- Después: `python manage.py test pedidos` → **342 pruebas, `OK (expected failures=4)`**.
- `python manage.py check` → sin problemas. `makemigrations --check --dry-run` → `No changes detected`.
- `DEBUG=False check --deploy` (variable apagada): W004, W008, W009, W012, W016 (las de siempre).
- `DEBUG=False SEGURIDAD_PRODUCCION=True check --deploy` con el `.env` local: **`ImproperlyConfigured: SECRET_KEY no es segura`**. La clave local no cumple la regla de W009 (coherente con la W009 local de la 04-02). No afecta `runserver` ni las pruebas: en local la variable va apagada y solo se exige que la clave exista.
- Mismo comando con una clave generada solo para ese proceso: **W005 y W021**.
- Sin revisión de pantallas: la iteración no toca plantillas.

### Corrección a la iteración (advertencias)

La iteración esperaba «solo W009» (paso 1) y «sin advertencias» (verificación 2). Tras la 04-02, W005 y W021 se quedan siempre (aceptadas). Corregido: local con la variable, W005, W009 y W021 antes de la 04-03 (y ahora, arranque fallido con una clave débil); producción, solo W005 y W021.

## Revisiones pendientes de la redacción (sin valores)

- **`compose.yaml`:** 3 líneas con `PASSWORD`. Dos son comentarios sin valor; la tercera, `MYSQL_ROOT_PASSWORD`, es una variable `${…:?}` obligatoria. **Ninguna contraseña literal.**
- **Patrón `mysql://usuario:clave@` en `cfe5e26`, `27f7ff9` y `da0cbcd`:** 5 coincidencias, clasificadas por forma sin mostrar el valor: 4 marcadores (`replica-local.md`, `evidencia-00-03.md`, `bitacora-00-04.md`, una línea retirada de `replica-local.md`) y 1 en `.env.example` (`da0cbcd`), comentada, con una palabra de ejemplo en la clave y un host de ejemplo. **Inferido: todos son ejemplos.** No se comparó contra ninguna contraseña real (el agente no lee `.env`).
- Historial ya registrado en la redacción, sin cambios: la clave de `713260c` (quemada, no coincide con producción, 00-01) y la contraseña local de `08a1a44` a `da0cbcd` (riesgo aceptado, D4; que no coincide lo dijo el desarrollador, no lo verificó el agente).

## D5 · Acceso al panel de PythonAnywhere

`PENDIENTE_DESARROLLADOR`: el registro por rol, sin nombres, lo entrega el desarrollador. Lo único registrado hasta hoy: el cliente tiene acceso al panel (recargó la aplicación dos veces el 2026-10-27).

## Ensayo en la réplica (paso 5): propuesta, sin ejecutar

**Problema.** La aplicación llama a `mysqldump` y `mysql` del equipo, que no están instalados (no se instala nada). El cliente está en el contenedor `manzagrafica-mysql`, y el archivo de opciones se crea en la carpeta temporal del equipo, que el contenedor no ve. Además, `replica-local.md` dice que en la réplica no se usan «Respaldar BD» ni «Restaurar».

**Propuesta (recomendada): puente fuera del repositorio, lo ejecuta el desarrollador.** Un script en la carpeta temporal del agente (fuera del repo; requiere consulta previa) que:

1. Importa Django con la configuración local y llama a las funciones reales `generar_respaldo_mysql()` y `restaurar_bd_mysql()`, con `settings.BASE_DIR` apuntando a una carpeta de respaldos **fuera del repositorio** (la que el desarrollador use para volcados), para que nada con datos reales caiga en `backups/` del repo.
2. Reemplaza solo `subprocess.run` por un puente: copia el archivo de opciones al contenedor con `docker cp` a `/tmp/`, ejecuta `docker exec -i manzagrafica-mysql <programa> --defaults-extra-file=/tmp/<archivo> …` con los mismos argumentos y la misma entrada o salida, y borra la copia del contenedor en su propio `finally`. Lo que se prueba de verdad: que MySQL acepta `--defaults-extra-file` primero y el escapado de la contraseña; el borrado del archivo del equipo lo hace el código de la aplicación.
3. Durante el respaldo, lista los procesos del equipo (`Get-CimInstance Win32_Process`, línea de órdenes) y del contenedor (`/proc/*/cmdline`) y cuenta cuántas líneas contienen `--password` o `-p` seguido de texto: esperado 0. Imprime solo conteos.
4. Restaura **el mismo archivo** recién generado (los datos no cambian), y al final imprime: tamaño del volcado, si su última línea es la de cierre de `mysqldump` (sin mostrar contenido), código de salida de la restauración y cuántos `mysql_opciones_*` quedan en la carpeta temporal del equipo y en `/tmp` del contenedor (esperado 0 y 0).
5. Antes de correrlo, el volcado de seguridad de `replica-local.md` (comando nativo en Docker).

Esto no usa los botones de la web; **sí es una excepción a la regla de la réplica** en lo que importa (escribe un volcado con datos y reemplaza la base con su propio contenido), por eso se pide consulta. El respaldo desde la web queda para la verificación en producción (paso 3). La restauración no se prueba en producción.

**Alternativa:** montar una carpeta del equipo en el contenedor desde `compose.yaml` y apuntar `TMPDIR` a ella. Exige editar el compose (configuración, consulta previa) y traducir rutas de Windows a las del contenedor igual: no la recomiendo.

## Comandos de medición de la clave (condición previa del Reload)

Imprimen solo largo, caracteres distintos y si empieza con `django-insecure-`; nunca la clave. Están en `despliegue.md`, 3.1 bis.

Consola Bash de PythonAnywhere (entorno virtual activo, en la carpeta del proyecto) y PowerShell local (en la raíz del repo), la misma línea:

```text
python -c "from dotenv import dotenv_values as d; k = d('.env').get('SECRET_KEY') or ''; print('largo', len(k), '| distintos', len(set(k)), '| django-insecure', k.startswith('django-insecure-'))"
```

Producción debe dar `largo` ≥ 50, `distintos` ≥ 5 y `False`. En local, el resultado ya se conoce por `check --deploy`: no cumple; no impide `runserver` ni las pruebas.

## Texto propuesto para `.env.example` (lo pega el desarrollador)

Reemplazar el comentario o la línea de `SECRET_KEY` por:

```text
# Clave secreta de Django. OBLIGATORIA en todo entorno: sin ella, la aplicación no arranca (04-03).
# Con SEGURIDAD_PRODUCCION=True debe tener al menos 50 caracteres, al menos 5 distintos y no
# empezar con django-insecure- (la misma regla de la advertencia security.W009).
# Genera una con: python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
# Nunca reutilices la clave que quedó en el historial de Git.
SECRET_KEY=
```

## Riesgos y lo que no se vio

- No se ejecutó `mysqldump` ni `mysql` reales con el archivo de opciones: la posición de `--defaults-extra-file` y el escapado están probados solo contra la documentación de MySQL, hasta el ensayo.
- `mkstemp` en Windows no aplica permisos POSIX; en PythonAnywhere (Linux) el archivo nace con `0600` (documentado por Python, no medido en el servidor).
- No se vio el `.env` local ni el del servidor, ni el archivo WSGI del servidor (si definiera `SECRET_KEY`, ganaría al `.env`; por eso `check --deploy` antes del Reload).
- Archivo huérfano si el worker muere entre crear y borrar: riesgo residual aceptado en la iteración.
