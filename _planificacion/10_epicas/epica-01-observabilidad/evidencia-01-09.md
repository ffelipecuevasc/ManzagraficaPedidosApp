# Evidencia 01-09 · Despliegue de `v1.2-capturas`

- **Fecha del pedido:** 2026-10-27
- **Pedido por:** Claude Code (Opus 5.5)
- **Iteraciones que viajan:** 01-09 (capturas amplias), 01-08 (comentarios del registro) y 01-07 reabierta (emojis 🔴 🟡 🔵 🔴🔴 🟢), más las pruebas de la Épica 02 (no se ejecutan en el servidor).
- **Etiqueta:** `v1.2-capturas` sobre `81005df`. **Partida y destino de retroceso:** `v1.1-observabilidad` (`d6768d0`).
- **Criterios que dependen de esta evidencia:** respaldo previo verificado (decisión 6 de la 01-09); despliegue con etiqueta propia sin migraciones, `pip` ni `collectstatic`; validación posterior con un respaldo por el camino normal que se descarga (decisión 7); `server.log` sin errores nuevos y con los emojis de la 01-07.
- **Actualización 2026-11-04:** las partes A a E se ejecutaron entre el 2026-11-03 (parte A, 22:34:09) y el 2026-11-04 (reinicio efectivo de uWSGI a las 00:11:49, hora de Chile), no el domingo 2026-11-01 previsto. Hubo un incidente en el servidor (parte D) y una diferencia entre la hora informada de la recarga y la del registro de uWSGI; ambos están documentados abajo. **Decisión del desarrollador (2026-11-04): la hora oficial de la recarga es 00:11:49** (hora de Chile, la de `Starting uWSGI`). Consolidación en [bitacora-01-09-despliegue](../../99_bitacora/epica-01-observabilidad/bitacora-01-09-despliegue.md).

> Este archivo existe porque el agente no puede obtener estos datos por su cuenta. Responde solo lo que se pide.
>
> **Orden previsto para el ~~domingo 2026-11-01~~ (decisión del desarrollador; fecha real: 2026-11-03 y 2026-11-04, ver la actualización de arriba):** parte A (respaldo previo) → parte D de la 01-06 desde las 21:27 de Chile ([evidencia-01-06](evidencia-01-06.md)) → parte B (lista de comprobación) → parte C (etiqueta) → parte D (despliegue) → parte E (validación) → solo si quedó validada, la 00-07 ([evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md), partes B4 y C).

## Qué intentó el agente

| Dato | Qué hizo en local | Por qué se necesita al desarrollador |
| :--- | :---------------- | :----------------------------------- |
| Contenido de la etiqueta | `git log` y `git diff --stat` de solo lectura (2026-10-27): entre `v1.1-observabilidad` y `81005df` no cambian plantillas, `pedidos/static`, `requirements.txt` ni migraciones; entre `81005df` y `main` solo cambia `pedido_form.html` (la 00-07) | Las etiquetas y el `push` son del desarrollador |
| Pruebas | `Ran 184 tests`, `OK (expected failures=19)` el 2026-10-27 ([bitacora-00-07-revision](../../99_bitacora/epica-00-blindaje/bitacora-00-07-revision.md)) | Se repiten el día del despliegue sobre el commit que se etiqueta |
| Respaldo, despliegue y validación | Preparó los pasos | El agente no genera ni abre volcados y no toca PythonAnywhere (`AGENTS.md`, sección 6) |

---

## Parte A · Respaldo previo (antes de la parte D de la 01-06)

Procedimiento de `docs/operacion/respaldo.md`. **Este volcado cuenta también como el respaldo semanal de rutina de la parte D de la 01-06**: no hace falta otro.

1. **[Navegador]** Inicia sesión y abre «Respaldar BD» (`/base_datos/respaldar_bd/`). Pulsa **una sola vez** «Generar Nuevo Respaldo BD» y espera la descarga.
   - Ese botón es un enlace GET: cada visita crea un volcado y desplaza al más antiguo de los cinco (AUD-02-006). No recargues ni repitas el clic.
   - Si la descarga no empieza o se corta (la recarga de la página a los 2 segundos, AUD-03-002), **no repitas el clic**: revisa si el volcado quedó listado en la misma pantalla y descárgalo desde la pestaña **Files** (`respaldo.md`, sección 2, paso 3).
2. Guarda el archivo **directamente** en la carpeta cifrada de respaldos, fuera del repositorio.
3. **[PC · PowerShell 7]**

   ```powershell
   python scripts\verificar_respaldo.py "<ruta del volcado>"
   $LASTEXITCODE
   ```

   **Esperado:** `19 de 19`, `Tablas faltantes: ninguna`, `VÁLIDO` y código `0`.
4. Agrega una fila a `docs/operacion/respaldo.md`, sección 6: «Previo al despliegue `v1.2-capturas` (iteración 01-09); también semanal de rutina de la parte D de la 01-06».

> Generar el respaldo deja un evento `respaldo_generado` en la tabla de eventos. Si se hace antes de la medición de la parte D de la 01-06, ese evento entra en su conteo: anótalo allí.

| Dato | Valor |
| :--- | :---- |
| Hora del clic (Chile) | 2026-11-03 22:34:09. Coincide con la hora del nombre del archivo (`respaldo_03-11-2026_22-34-09.sql`) y con la línea `INFO` de `pedidos.utils` en `server.log` (22:34:09) |
| ¿Se descargó directo o desde **Files**? | No informado |
| Tamaño (bytes) | 1.481.608 (mínimo exigido: 500.000: OK); línea de cierre «-- Dump completed» presente |
| Tablas (`N de 19`) y resultado | 19 de 19 (19 sentencias `CREATE TABLE`); faltantes: ninguna; adicionales: ninguna · `VÁLIDO` |
| SHA-256 (12 primeros) | `600993c55d75` (completo en `respaldo.md` §6) |
| Código de salida | `0` |
| Fila agregada en `respaldo.md` §6 | Sí (2026-11-03) |

> **Nota (2026-11-03):** la parte A se ejecutó el **2026-11-03**, no el domingo 2026-11-01 previsto, y se respetó el orden de la evidencia: respaldo a las 22:34:09 y, enseguida, la medición de la parte D de la 01-06 a las 22:37:58. El archivo se guardó en la carpeta cifrada de respaldos, fuera del repositorio (ruta no registrada). La coincidencia entre la hora del clic y la del nombre del archivo vale para el respaldo normal; no se generaliza al respaldo de emergencia de la restauración, que sigue sin comprobar. El evento `respaldo_generado` de este clic es el único de ese tipo en la medición de la parte D, y está incluido en sus 172 filas ([bitacora-01-06-medicion](../../99_bitacora/epica-01-observabilidad/bitacora-01-06-medicion.md)).

## Parte B · Lista de comprobación **[PC · PowerShell 7]**

`docs/operacion/despliegue.md`, sección 2, desde la raíz del repositorio, con `.venv` activo y `docker compose up -d`.

```powershell
git checkout main
python manage.py test pedidos
$env:DEBUG = "False"; python manage.py check --deploy; Remove-Item Env:DEBUG
python manage.py makemigrations --check --dry-run
python manage.py showmigrations pedidos
```

- Las pruebas corren sobre la punta de `main`, que incluye la 00-07. Entre `81005df` y `main` solo cambia `pedido_form.html`, y ninguna prueba depende de ese archivo.
- No ejecutes `git checkout 81005df`: dejaría el repositorio local en `detached HEAD` sin necesidad.

| # | Comprobación | Esperado | Resultado |
| :- | :----------- | :------- | :-------- |
| 1 | Pruebas | `Ran 184 tests` y `OK (expected failures=19)` (`pruebas.md`: valor vigente 19) | Dos ejecuciones: `Ran 184 tests`, `OK (expected failures=19)` en ambas (174,975 s y 283,578 s) |
| 2 | `check --deploy` | Solo `W004`, `W008`, `W009`, `W012` y `W016`; ningún `ERRORS` | Exactamente `W004`, `W008`, `W009`, `W012` y `W016` (5 issues); sin `ERRORS` |
| 3 | Migraciones sin crear | `No changes detected` | `No changes detected` |
| 4 | Migraciones nuevas | Ninguna: la última sigue siendo `0007_registroevento` | Ninguna: el `diff` de la parte C solo lista `pedido_form.html` y `migrate --plan` del servidor (D2) no planifica nada. `showmigrations` en la base local: `0007` sin aplicar |
| 5 | Respaldo verificado | Parte A | Parte A: `respaldo_03-11-2026_22-34-09.sql`, 19 de 19, `VÁLIDO`, código 0 |
| 6 | Estilos compilados | No aplica | No aplica |
| 7 | Etiqueta | Parte C | Parte C: `v1.2-capturas` anotada sobre `81005df`, publicada |
| 8 | Pasos propios | Partes D y E | Partes D y E: abajo |

> **Observación (sin acción):** `showmigrations` marca la `0007` sin aplicar en la base **local** del PC. Esa base no es la réplica ni producción y no afecta al despliegue (en producción, `0007` se aplicó el 2026-10-25 con `v1.1-observabilidad`).

## Parte C · Etiqueta `v1.2-capturas` sobre `81005df` **[PC · PowerShell 7]**

Es la **misma etiqueta** que la B3 de la `evidencia-00-07`: se crea **una sola vez**, aquí. Procedimiento de `despliegue.md`, sección 1, «Etiquetar un commit anterior a la punta».

```powershell
git status --short
git fetch origin
git status -sb
git log --oneline -n 6
git diff --stat 81005df..main -- . ":(exclude)_planificacion" ":(exclude)docs"
$hoy = Get-Date -Format "yyyy-MM-dd"
git tag -a v1.2-capturas 81005df -m "Iteraciones 01-09, 01-08 y 01-07 · desplegada el $hoy"
git tag -n v1.2-capturas
git rev-parse --short "v1.2-capturas^{commit}"
git push origin v1.2-capturas
git ls-remote --tags origin v1.2-capturas
```

- `git status --short` vacío y la primera línea de `git status -sb` es `## main...origin/main`, sin `[ahead N]` ni `[behind N]`.
- `git log` muestra `81005df` como el commit anterior a `4560874`, el primero que cambia `pedido_form.html`.
- El `diff` lista **solo** `pedidos/templates/pedidos/pedido_form.html`. Si aparece otro archivo, detente.
- El mensaje toma la fecha de `$hoy`; no se escribe a mano. Revisa `git tag -n` **antes** del `push`: si está mal, `git tag -d v1.2-capturas` y créala otra vez (todavía no está publicada).
- `rev-parse` responde `81005df` y `ls-remote` devuelve una línea.

| Dato | Valor |
| :--- | :---- |
| `git status -sb` (primera línea) | No informado |
| Salida del `diff --stat` | Solo `pedido_form.html`: 1 archivo, 41 inserciones, 3 eliminaciones |
| `git tag -n v1.2-capturas` | Mensaje informado: «Iteraciones 01-09, 01-08 y 01-07 · desplegada el 2026-11-04». Etiqueta anotada, objeto `567db391d5d1bf818f63d7d33758be7898c8abcc`, publicada |
| `rev-parse` | `git rev-parse --short "v1.2-capturas^{commit}"` = `81005df` |
| `ls-remote` | Devuelve una línea |

> **Nota (2026-11-04):** el desarrollador no informó la primera línea de `git status -sb` ni la salida literal de `git tag -n`; se registra solo lo que entregó. El objeto de la etiqueta (`567db39…`) es el de la etiqueta anotada; el commit al que apunta es `81005df`.

## Parte D · Despliegue

### D1. Ubicarse **[PA · Bash]**

```bash
PROYECTO="/home/manzagrafica/ManzagraficaPedidosApp"
VENV="/home/manzagrafica/ManzagraficaPedidosApp/venv"
test -f "$PROYECTO/manage.py" && test -x "$VENV/bin/python" && echo "PROYECTO y VENV correctos"
cd "$PROYECTO"; source "$VENV/bin/activate"
git status --short
git describe --tags
```

- **Esperado:** `PROYECTO y VENV correctos`, `git status --short` vacío y `git describe --tags` responde `v1.1-observabilidad`. Si no, detente.

### D2. Traer la etiqueta **[PA · Bash]**

```bash
git fetch origin --tags
git checkout v1.2-capturas
git describe --tags
python manage.py migrate --plan
git diff --stat v1.1-observabilidad v1.2-capturas -- requirements.txt
git diff --stat v1.1-observabilidad v1.2-capturas -- pedidos/static
```

- `git describe --tags` responde `v1.2-capturas` (`detached HEAD` es lo esperado). **Nunca `git pull`.**
- `migrate --plan` → `No planned migration operations.`
- Los dos `diff` salen **vacíos**: **sin `pip install`, sin `collectstatic` y sin `migrate`**.

### D3. Recargar **[PA · Panel]**

Pestaña **Web** → **Reload**. Anota la hora (Chile). La recarga deja unos 10 s de 502 (AUD-04-002).

| Dato | Valor |
| :--- | :---- |
| D1 (`describe` y `status`) | El resultado de D1 antes del incidente no se informó. Después de la restauración de las 00:09: `git describe` = `v1.1-observabilidad`, `rev-parse` = `d6768d0` y `git status --short` vacío, que es el estado que pedía D1. Ver el incidente abajo |
| D2 (`describe`, `migrate --plan` y los dos `diff`) | Hacia las 00:10: `fetch origin --tags` trajo `bd07f21` y la etiqueta; `checkout v1.2-capturas` dejó HEAD en `81005df` (`describe` = `v1.2-capturas`); `migrate --plan` → «No planned migration operations.» (con la advertencia conocida `mysql.W002`); los dos `diff --stat` (`requirements.txt` y `pedidos/static`) salieron vacíos |
| Hora de la recarga (Chile) | **Oficial: 00:11:49** (decisión del desarrollador, 2026-11-04): la de `Starting uWSGI` en el registro (mensaje interno `[Wed Nov  4 03:11:48 2026]` en UTC). La hora que el desarrollador había **informado**, **00:14:00**, queda anotada como «informada»: es 2 min 11 s posterior |

#### Incidente del 2026-11-03: `git checkout main` en la consola del servidor

- **Qué pasó:** hacia las 23:41 (02:41 UTC) se ejecutó por error `git checkout main` en la consola del **servidor**. Era un comando de la parte B, que va en el PC. El servidor quedó en la rama `main` **del servidor**, atrasada: `git describe` = `v0.0-inicial` y Git indicó 32 commits de atraso. **No se hizo `git pull`.** `git status` no mostró cambios en archivos versionados, solo líneas `??` de `media/` y `staticfiles/`.
- **Cómo se restauró:** hacia las 00:09 (03:09 UTC), `git checkout v1.1-observabilidad`: `describe` = `v1.1-observabilidad`, `rev-parse` = `d6768d0` y `git status --short` vacío. El desfase fue de unos 28 minutos (horas informadas «hacia», aproximadas).
- **Reinicios de uWSGI durante el incidente:** ninguno. La consulta se hizo con filtro por fecha sobre los archivos de registro, **incluidos los rotados**, desde `2026-11-03 23:30:00` (hora de Chile), y mostró **una sola** línea `Starting uWSGI`: la de `2026-11-04 00:11:49` (`2026-11-04 00:11:49 *** Starting uWSGI 2.0.28 (64bit) on [Wed Nov  4 03:11:48 2026] ***`). No hubo reinicios entre las 23:41 y las 00:09.
- **Ventana del incidente (2026-11-03 23:41 a 2026-11-04 00:09): NO VERIFICADA** (decisión del desarrollador, 2026-11-04). No se comprobó si alguna petición leyó archivos del árbol atrasado ni si `server.log` tuvo líneas nuevas en ese tramo: la parte D de la 01-06 se midió a las 22:37:58, antes del incidente, y E3 empieza a las 00:11:49. Contexto que se conoce: sin cambios en archivos versionados (solo líneas `??` de `media/` y `staticfiles/`), sin `git pull`, restauración con `git checkout v1.1-observabilidad` (`describe` = `v1.1-observabilidad`, `rev-parse` = `d6768d0`) y las cuatro pantallas de E1 funcionaron. **Inferencia, no comprobada:** la web app tenía cargado en memoria el código de `v1.1-observabilidad`.
- **Propuesta (no aplicada):** advertencia para `despliegue.md`, sección 3, y comando para detectar reinicios, en [bitacora-01-09-despliegue](../../99_bitacora/epica-01-observabilidad/bitacora-01-09-despliegue.md).

#### La hora de la recarga: la oficial y la informada

- El desarrollador informó la recarga a las **00:14:00**. Pero el respaldo de E2 se llama `respaldo_04-11-2026_00-12-37.sql` (00:12:37), anterior a esa hora, y la línea `Starting uWSGI` figura a las **00:11:49**.
- **Decisión del desarrollador (2026-11-04):** la hora oficial de la recarga, en `despliegue.md` y en el registro, es **00:11:49** (hora de Chile; 03:11:49 UTC al convertir el prefijo del registro, mientras que el mensaje interno de uWSGI marca 03:11:48). La hora informada, **00:14:00**, queda anotada como «informada», 2 min 11 s posterior, y respaldada por ningún registro.
- Para el filtro de E3 se usó la hora oficial (00:11:49).

## Parte E · Validación

### E1. Pantallas **[Navegador]**

Las cuatro de `despliegue.md`, sección 3.7, en una ventana privada: acceso, panel, listado de pedidos y detalle de un pedido. No uses «Estadísticas» (cada visita escribe en `pedidos_historialbd`).

### E2. Un respaldo por el camino normal **[Navegador]**

Decisión 7 de la 01-09: **un solo** clic en «Generar Nuevo Respaldo BD» y comprobar que el archivo se descarga. **No** se provoca a propósito ningún fallo de respaldo ni de restauración.

- Si aparece «No se pudo generar el respaldo. El detalle quedó en el registro del servidor.», es el texto nuevo de la 01-09 (`:1128`) ante un fallo real: anota la hora y revisa E3.
- Si el volcado se genera y queda listado pero la descarga se corta, es la recarga a los 2 segundos (AUD-03-002), un defecto anterior a `v1.2` que corrige la 04-01: no es motivo de retroceso. Anótalo y descárgalo desde **Files** si quieres conservarlo.
- Este volcado no reemplaza al de la parte A: no hace falta verificarlo, pero si lo descargas, guárdalo en la carpeta cifrada.

### E3. `server.log` después de la recarga **[PA · Bash]**

```bash
S=/var/log/manzagrafica.pythonanywhere.com.server.log
DESDE_CL="<AAAA-MM-DD HH:MM:SS de la recarga, en hora de Chile>"
echo "$DESDE_CL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE_CL válido"
awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] / && substr($0,1,19) >= d' $S | grep -o 'nivel=[A-Z]*' | sort | uniq -c
awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] / && substr($0,1,19) >= d' $S | grep 'nivel=' | tail -n 5 | cut -c1-120
```

- `DESDE_CL` lleva solo la fecha y la hora, sin `<` ni `>`; debe imprimir `DESDE_CL válido`.
- **Esperado:** ningún `nivel=ERROR` nuevo. Las líneas con `nivel=` que aparezcan empiezan con los emojis de la 01-07 (🔴 ERROR, 🟡 WARNING, 🔵 INFO, 🔴🔴 CRITICAL, 🟢 DEBUG), ya no con ❌ ⚠️ ❕. **Se filtra por `nivel=`, nunca por el emoji.**
- Si no hay ninguna línea con `nivel=` después de la recarga, es normal: sin errores ni avisos no se escribe nada. Anótalo así.
- Si hay errores, copia **solo el tipo de excepción y la hora**, no la línea completa (puede traer datos de clientes).

### E4. Registro del despliegue **[PC]**

Fila en `docs/operacion/despliegue.md`, sección 5: fecha y hora (Chile), `v1.2-capturas`, commit `81005df`, «01-09, 01-08 y 01-07 reabierta (partida `v1.1-observabilidad`); sin migraciones», SHA-256 de la parte A y el resultado.

| Revisión | Resultado |
| :------- | :-------- |
| E1 Acceso, panel, listado y detalle | Sin problemas en las cuatro pantallas |
| E2 Respaldo por el camino normal (¿se descargó?) | Sí. `respaldo_04-11-2026_00-12-37.sql` (hora del nombre: 2026-11-04 00:12:37), 1.481.788 bytes, línea de cierre presente, 19 `CREATE TABLE`, 19 de 19, faltantes: ninguna, SHA-256 `348f44c3eb91a333a5cc3f44a6900b6605822743916e180ef8811e6c40595937`, `VÁLIDO`, código 0. Descargado y guardado en la carpeta cifrada (ruta no registrada). Fila en `respaldo.md` §6 |
| E3 Conteo por `nivel=` desde la recarga | **Ejecución definitiva**, con `DESDE_CL="2026-11-04 00:11:49"` (reinicio efectivo): `1 nivel=ERROR` y `1 nivel=INFO`. La primera ejecución, con `DESDE_CL="2026-11-04 00:14:00"` (hora informada), salió vacía porque el filtro empezaba después de los eventos: **no es la validación definitiva** |
| E3 Emojis nuevos en las líneas (si hubo) | Sí. A las 00:12:39: línea `INFO` de `pedidos.utils` con 🔵 y línea `ERROR` de `root` con 🔴 (ver abajo). Son los emojis de `v1.2`; `v1.1-observabilidad` usaba ❕ y ❌ |
| E4 Fila en `despliegue.md` §5 | Sí (2026-11-04) |

#### E3 en detalle (últimas líneas con `nivel=`, recortadas a 120 caracteres)

```text
2026-11-04 00:12:39 🔵 nivel=INFO registrador=pedidos.utils metodo=- ruta=- usuario=- excepcion=- mensaje="Respaldo an
2026-11-04 00:12:39 🔴 nivel=ERROR registrador=root metodo=- ruta=- usuario=- excepcion=- mensaje="OSError: write erro
```

- **El único `ERROR`** es `OSError: write error` con `registrador=root`, sin método, ruta, usuario ni excepción: el ruido conocido, de la misma familia que las 7 líneas `root` anteriores al despliegue (clasificadas como AUD-04-004, sin acción). No hay errores nuevos.
- **Coincidencia horaria, sin concluir nada:** esa línea tiene la misma hora (00:12:39) que el `INFO` del respaldo de E2, igual que la pista del 2026-10-23 de la 00-05 (un `write error` 2 s después de generar un respaldo). El archivo de E2 se descargó y salió `VÁLIDO` (19 de 19), así que el `write error` no lo dañó. No es sistemática: en los nueve días de la medición solo hubo un `respaldo_generado` (22:34 del 2026-11-03) y a esa hora no hubo `OSError`. Hipótesis, no conclusión: la recarga de la página a los 2 segundos (AUD-03-002) corta la descarga. Sin acción (detalle en la bitácora).
- **Respaldo posterior al reinicio:** el reinicio efectivo fue a las 00:11:49; el nombre del respaldo dice 00:12:37 y el `INFO`, 00:12:39. El respaldo es posterior al reinicio (48 s y 50 s) y, además, el `INFO` lleva el emoji de `v1.2`: se hizo bajo `v1.2-capturas`. Entre el nombre y el registro hay 2 s; en la parte A coincidían al segundo. No se explica y no cambia la conclusión.
- **No ejecutado, a propósito:** ningún fallo de respaldo ni de restauración (decisión 7). No se probó el texto nuevo de `:1128`.

## Si algo sale mal

`docs/operacion/retroceso.md`, **caso 1** (sin migraciones): `git checkout v1.1-observabilidad`, `check`, **Reload** y las pantallas. **La 00-07 se pospone:** no se crea `v0.3-doble-envio` ese día (decisión 5 de la 00-07).

## Lo que no se pudo verificar

- La restauración real sigue «no verificada en real» (decisión 7 de la 01-09): no se prueba en producción.
- El camino de error del respaldo en producción: no se provoca a propósito.
- **Añadido el 2026-11-04:** si alguna petición leyó archivos del árbol atrasado entre las 23:41 y las 00:09, y el contenido de `server.log` en esa ventana (no se revisó; registrada como no verificada). La primera línea de `git status -sb` y la salida literal de `git tag -n` de la parte C (no informadas). Si la descarga de E2 fue directa o desde **Files** (no informado).

## Respuesta del desarrollador

Partes B a E respondidas el 2026-11-04 y consolidadas en las tablas de arriba, con estos puntos propios del despliegue:

- **Etiqueta y partida:** `v1.2-capturas`, anotada, sobre `81005df` (objeto `567db391d5d1bf818f63d7d33758be7898c8abcc`), publicada; partida y destino de retroceso `v1.1-observabilidad` (`d6768d0`). Sin migraciones, sin `pip`, sin `collectstatic`.
- **Incidente:** `git checkout main` por error en la consola del servidor hacia las 23:41 del 2026-11-03; restaurado hacia las 00:09 con `git checkout v1.1-observabilidad`; sin `git pull` y sin reinicios de uWSGI en ese tramo (parte D).
- **Hora de la recarga:** oficial 00:11:49 (decisión del desarrollador, 2026-11-04); la informada, 00:14:00, queda como «informada», 2 min 11 s posterior (parte D).
- **E3:** primera ejecución vacía por un `DESDE_CL` posterior a los eventos; la definitiva usa 00:11:49: 1 `ERROR` (`OSError: write error`, `root`, ruido conocido) y 1 `INFO`, con 🔴 y 🔵.
- **Sin retroceso.**
