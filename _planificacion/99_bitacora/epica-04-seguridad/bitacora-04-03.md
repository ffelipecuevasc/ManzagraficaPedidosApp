# Bitácora 04-03 · Credenciales y secretos

- **Fecha:** 2026-11-19
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** ~~Implementada, pendiente de despliegue.~~ **Implementada, pendiente de ensayo y despliegue** (2026-11-19; el ensayo está pendiente de ejecutar por el desarrollador). Etiqueta prevista `v4.5-credenciales`, sin fecha fija (RDA-021); retroceso `v4.4-hsts-semana`.
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

## Ensayo en la réplica (paso 5): propuesta original (aprobada el 2026-11-19, ver la sección siguiente)

**Problema.** La aplicación llama a `mysqldump` y `mysql` del equipo, que no están instalados (no se instala nada). El cliente está en el contenedor `manzagrafica-mysql`, y el archivo de opciones se crea en la carpeta temporal del equipo, que el contenedor no ve. Además, `replica-local.md` dice que en la réplica no se usan «Respaldar BD» ni «Restaurar».

**Propuesta (recomendada): puente fuera del repositorio, lo ejecuta el desarrollador.** Un script en la carpeta temporal del agente (fuera del repo; requiere consulta previa) que:

1. Importa Django con la configuración local y llama a las funciones reales `generar_respaldo_mysql()` y `restaurar_bd_mysql()`, con `settings.BASE_DIR` apuntando a una carpeta de respaldos **fuera del repositorio** (la que el desarrollador use para volcados), para que nada con datos reales caiga en `backups/` del repo.
2. Reemplaza solo `subprocess.run` por un puente: copia el archivo de opciones al contenedor con `docker cp` a `/tmp/`, ejecuta `docker exec -i manzagrafica-mysql <programa> --defaults-extra-file=/tmp/<archivo> …` con los mismos argumentos y la misma entrada o salida, y borra la copia del contenedor en su propio `finally`. Lo que se prueba de verdad: que MySQL acepta `--defaults-extra-file` primero y el escapado de la contraseña; el borrado del archivo del equipo lo hace el código de la aplicación.
3. Durante el respaldo, lista los procesos del equipo (`Get-CimInstance Win32_Process`, línea de órdenes) y del contenedor (`/proc/*/cmdline`) y cuenta cuántas líneas contienen `--password` o `-p` seguido de texto: esperado 0. Imprime solo conteos.
4. Restaura **el mismo archivo** recién generado (los datos no cambian), y al final imprime: tamaño del volcado, si su última línea es la de cierre de `mysqldump` (sin mostrar contenido), código de salida de la restauración y cuántos `mysql_opciones_*` quedan en la carpeta temporal del equipo y en `/tmp` del contenedor (esperado 0 y 0).
5. Antes de correrlo, el volcado de seguridad de `replica-local.md` (comando nativo en Docker).

Esto no usa los botones de la web; **sí es una excepción a la regla de la réplica** en lo que importa (escribe un volcado con datos y reemplaza la base con su propio contenido), por eso se pide consulta. El respaldo desde la web queda para la verificación en producción (paso 3). La restauración no se prueba en producción.

**Alternativa:** montar una carpeta del equipo en el contenedor desde `compose.yaml` y apuntar `TMPDIR` a ella. Exige editar el compose (configuración, consulta previa) y traducir rutas de Windows a las del contenedor igual: no la recomiendo.

## Ensayo en la réplica: aprobado e implementado el puente (2026-11-19)

Consulta previa aprobada el 2026-11-19: (a) el script puente fuera del repositorio y (b) una excepción única en `replica-local.md`. No se monta ninguna carpeta en `compose.yaml`. **Ensayo: pendiente de ejecutar por el desarrollador.** El agente solo comprobó que el script compila (`py_compile`); no lo ejecutó.

- **Script:** `C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-03\puente_ensayo_04_03.py` (fuera del repo, carpeta temporal de la sesión del agente: si se borra antes del ensayo, se pide de nuevo).
- **Se niega a correr** (código 2) si no se ejecuta desde la raíz del repo, si `--carpeta` está dentro del repo o no existe, si hay `DATABASE_URL` en la sesión, si `DB_NAME` no es `manzagrafica_replica`, si el host no es local o si el contenedor no está corriendo.
- **Hace:** conteo de tablas y filas → respaldo con la función real (puente: `docker cp` del archivo de opciones a `/tmp` del contenedor, `chmod 600`, `docker exec -i`, borrado en `finally`) → línea de cierre → volcado de seguridad nativo (`MYSQL_PWD` dentro del contenedor, sin contraseña en argumentos) → restauración del mismo volcado con la función real → conteo después → archivos residuales. Mientras corre cada comando, muestrea los procesos del equipo y del contenedor y cuenta los que llevan contraseña en argumentos.
- **Volcados:** en `<carpeta>\ensayo-04-03_<fecha>\backups\` y `seguridad_nativo.sql`, nunca en `backups/` del repo. Una subcarpeta nueva para que la rotación de 5 de la app no borre otros volcados.
- **Límite:** prueba el comportamiento de MySQL con el archivo de opciones dentro del contenedor (mismo `mysql:8.0.46`), no el cliente de PythonAnywhere; eso lo cubre la verificación en producción.

### Paso a paso del ensayo (PowerShell 7)

Todo en **una sola ventana** de PowerShell 7. Si cierras la ventana a la mitad, vuelve a empezar desde el paso 1.

**Paso 1. Ubícate en el proyecto y activa el entorno virtual.**

```powershell
cd "D:\Trabajo\Proyectos PYTHON\Proyectos Personales\Pedidos Manzagrafica\PedidosApp"
.\.venv\Scripts\Activate.ps1
```

Debe verse `(.venv)` al inicio de la línea. Si no aparece, no sigas: revisa que exista la carpeta `.venv`.

**Paso 2. Comprueba que el contenedor está arriba.**

```powershell
docker compose up -d
docker inspect -f "{{.State.Running}}" manzagrafica-mysql
```

Debe responder `true`. Si dice `false` o da error: abre Docker Desktop, espera a que diga «Engine running» y repite. Si sigue sin subir, mira `docker compose logs db --tail 30` y detente. **Nunca** uses `docker compose down -v` ni `docker volume rm`: borran la base.

**Paso 3. Apunta la sesión a la réplica y comprueba la paridad.**

```powershell
$env:DB_NAME = "manzagrafica_replica"
python scripts\diagnostico\paridad_replica.py
$LASTEXITCODE
```

`$LASTEXITCODE` debe ser `0` (paridad, con o sin diferencias aceptadas). Si es `1`, no sigas: anota la fila que sale «No» y avísame.

**Paso 4. Elige la carpeta de volcados, fuera del repositorio.**

```powershell
$carpeta = "<tu carpeta de respaldos descargados, fuera del repo>"
Test-Path $carpeta
```

Debe responder `True`. Si dice `False`, créala con `New-Item -ItemType Directory $carpeta` o corrige la ruta.

**Paso 5. Ejecuta el ensayo.**

```powershell
python "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-03\puente_ensayo_04_03.py" --carpeta $carpeta
$LASTEXITCODE
```

Tarda lo que tarde un respaldo y una restauración de la réplica (minutos). No cierres la ventana mientras corre.

**Paso 6. Lee los conteos.** Debe verse algo así, con tus números:

| Línea | Qué debe decir |
| :---- | :------------- |
| `Carpeta del ensayo: …` | Una ruta dentro de tu carpeta, **anótala** (la usas en el paso 8). |
| `[1] Antes: N tablas, F filas` | Cualquier número. |
| `[2] Respaldo de la app: … línea de cierre: sí` | `sí`. |
| `[3] Volcado de seguridad nativo: … línea de cierre: sí` | `sí`. |
| `[4] Restauración del mismo volcado: terminó sin error` | Esa frase. |
| `[5] Después: N tablas, F filas; tablas con conteo distinto: 0` | Mismos N y F que en `[1]`, y `0`. |
| `[6] … procesos del ensayo vistos: X` | X de 1 o más (si es 0, el ensayo fue tan rápido que no probó nada: repite el paso 5). |
| `con contraseña en argumentos: equipo 0, contenedor 0` | `0` y `0`. |
| `[7] Archivos de opciones residuales: equipo 0, contenedor 0` | `0` y `0`. |
| `RESULTADO: CUMPLE` y `$LASTEXITCODE` = `0` | **Éxito.** |

Pégame esas líneas tal como salen (son solo conteos).

**Paso 7. Si falla.**

- `NO SE EJECUTA: …` (código 2): no tocó nada. Corrige lo que dice (casi siempre falta el paso 3 o el 2) y repite el paso 5.
- `[2]` con `NO`, o se corta antes de `[4]`: la base **no** se restauró. Pégame la salida.
- Error **durante** `[4]` (traza de Python después de `[3]`): la réplica puede haber quedado a medias. Restaura el volcado nativo con `replica-local.md`, sección 5, usando como ruta `<Carpeta del ensayo>\seguridad_nativo.sql`, y después repite el paso 3.
- `[5]` con conteos distintos, o `[6]`/`[7]` con algo distinto de 0: el ensayo **no cumple**; no despliegues. Pégame la salida.
- `[7]` con residuales: bórralos con `docker exec manzagrafica-mysql sh -c "rm -f /tmp/mysql_opciones_*"` (contenedor) o `Remove-Item "$env:TEMP\mysql_opciones_*"` (equipo).

**Paso 8. Limpieza (siempre, cumpla o no).**

```powershell
Remove-Item Env:DB_NAME
Remove-Item -Recurse -Force "<Carpeta del ensayo que anotaste en el paso 6>"
Remove-Item -Recurse -Force "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-03"
docker compose stop
```

- Borra la carpeta del ensayo **solo si salió `CUMPLE`**: tiene volcados con datos reales. Si falló, consérvala hasta resolverlo.
- Comprueba que no quedó la variable: `$env:DB_NAME` no debe mostrar nada.

### Orden de despliegue de `v4.5-credenciales`

1. Medir la clave de producción (comando de abajo y `despliegue.md`, 3.1 bis): largo ≥ 50, distintos ≥ 5, `False`. Si no, cambiarla en el `.env` del servidor y volver a medir.
2. Pegar el texto propuesto en `.env.example` (lo edita el desarrollador) y hacer el commit **antes** de crear la etiqueta.
3. Respaldo previo en producción `VÁLIDO` (`respaldo.md`).
4. Ensayo en la réplica con `RESULTADO: CUMPLE` (pasos de arriba).
5. Etiqueta anotada `v4.5-credenciales` y `git push` de la etiqueta.
6. En el servidor: checkout de la etiqueta (`despliegue.md`, 3.2) y `git describe` → `v4.5-credenciales`.
7. `check --deploy` **antes** del Reload: solo W005 y W021. Si sale `ImproperlyConfigured`, no recargues: corrige la clave o vuelve al checkout de `v4.4-hsts-semana` (el worker sigue con el código anterior).
8. Reload y verificaciones del mismo día: la aplicación arranca, un respaldo desde la web se descarga completo y sale `VÁLIDO`, `server.log` sin errores de `mysqldump`, `ls /tmp/mysql_opciones_* 2>/dev/null | wc -l` → `0`.
9. Retroceso: `retroceso.md`, caso 1, a `v4.4-hsts-semana` (sin migraciones). Si solo falla el arranque por la clave, se corrige el `.env` y se recarga.

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
