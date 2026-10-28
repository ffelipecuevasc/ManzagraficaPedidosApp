# Evidencia 01-09 · Despliegue de `v1.2-capturas`

- **Fecha del pedido:** 2026-10-27
- **Pedido por:** Claude Code (Opus 5.5)
- **Iteraciones que viajan:** 01-09 (capturas amplias), 01-08 (comentarios del registro) y 01-07 reabierta (emojis 🔴 🟡 🔵 🔴🔴 🟢), más las pruebas de la Épica 02 (no se ejecutan en el servidor).
- **Etiqueta:** `v1.2-capturas` sobre `81005df`. **Partida y destino de retroceso:** `v1.1-observabilidad` (`d6768d0`).
- **Criterios que dependen de esta evidencia:** respaldo previo verificado (decisión 6 de la 01-09); despliegue con etiqueta propia sin migraciones, `pip` ni `collectstatic`; validación posterior con un respaldo por el camino normal que se descarga (decisión 7); `server.log` sin errores nuevos y con los emojis de la 01-07.

> Este archivo existe porque el agente no puede obtener estos datos por su cuenta. Responde solo lo que se pide.
>
> **Orden del domingo 2026-11-01 (decisión del desarrollador):** parte A (respaldo previo) → parte D de la 01-06 desde las 21:27 de Chile ([evidencia-01-06](evidencia-01-06.md)) → parte B (lista de comprobación) → parte C (etiqueta) → parte D (despliegue) → parte E (validación) → solo si quedó validada, la 00-07 ([evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md), partes B4 y C).

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
| Hora del clic (Chile) | |
| ¿Se descargó directo o desde **Files**? | |
| Tamaño (bytes) | |
| Tablas (`N de 19`) y resultado | |
| SHA-256 (12 primeros) | |
| Código de salida | |
| Fila agregada en `respaldo.md` §6 | |

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
| 1 | Pruebas | `Ran 184 tests` y `OK (expected failures=19)` (`pruebas.md`: valor vigente 19) | |
| 2 | `check --deploy` | Solo `W004`, `W008`, `W009`, `W012` y `W016`; ningún `ERRORS` | |
| 3 | Migraciones sin crear | `No changes detected` | |
| 4 | Migraciones nuevas | Ninguna: la última sigue siendo `0007_registroevento` | |
| 5 | Respaldo verificado | Parte A | |
| 6 | Estilos compilados | No aplica | |
| 7 | Etiqueta | Parte C | |
| 8 | Pasos propios | Partes D y E | |

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
| `git status -sb` (primera línea) | |
| Salida del `diff --stat` | |
| `git tag -n v1.2-capturas` | |
| `rev-parse` | |
| `ls-remote` | |

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
| D1 (`describe` y `status`) | |
| D2 (`describe`, `migrate --plan` y los dos `diff`) | |
| Hora de la recarga (Chile) | |

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
| E1 Acceso, panel, listado y detalle | |
| E2 Respaldo por el camino normal (¿se descargó?) | |
| E3 Conteo por `nivel=` desde la recarga | |
| E3 Emojis nuevos en las líneas (si hubo) | |
| E4 Fila en `despliegue.md` §5 | |

## Si algo sale mal

`docs/operacion/retroceso.md`, **caso 1** (sin migraciones): `git checkout v1.1-observabilidad`, `check`, **Reload** y las pantallas. **La 00-07 se pospone:** no se crea `v0.3-doble-envio` ese día (decisión 5 de la 00-07).

## Lo que no se pudo verificar

- La restauración real sigue «no verificada en real» (decisión 7 de la 01-09): no se prueba en producción.
- El camino de error del respaldo en producción: no se provoca a propósito.

## Respuesta del desarrollador

_(Pendiente.)_
