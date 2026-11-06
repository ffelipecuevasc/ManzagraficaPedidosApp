# Evidencia 03-05 · Validación y despliegue de la integridad

- **Fecha del pedido:** 2026-11-06
- **Pedido por:** Claude Code (Sonnet 5.5)
- **Iteración:** [03-05](iteracion-03-05-validacion-y-despliegue-de-la-integridad.md). Etiqueta `v3.1-integridad`; partida y destino de retroceso `v0.3-doble-envio`. Decisiones del desarrollador del 2026-11-06 registradas en la iteración.
- **Criterios que dependen de esta evidencia:** todos los de la 03-05 salvo «Las decisiones 1 a 8 están registradas antes de ejecutar».
- **Estado (2026-11-06):** **Pendiente. No se ejecutó nada.** Ni pruebas, ni respaldo, ni etiqueta, ni despliegue. Este archivo solo deja los pasos listos. Nada se ejecuta antes de la medición de la 00-07 (2026-11-11, hacia las 01:32).

> Este archivo existe porque el agente no puede tocar producción, crear etiquetas ni abrir respaldos. Responde solo lo que se pide, sin datos de clientes: conteos, horas, tipos de error y códigos. Nunca pegues el texto completo de una línea del registro (`despliegue.md`, 3.9).
>
> **Orden:** parte A (tu PC: comprobaciones, respaldo y etiqueta) → parte B (servidor: despliegue) → parte C (día 0: la misma noche) → parte D (día 7 y cierre) → parte E (retroceso: **solo si** se cumple su regla) → parte F (limpieza de la réplica, último paso).
>
> **Terminales** (`docs/operacion/despliegue.md`, sección 0): **[PC · PowerShell 7]** en la raíz del repositorio con `.venv` activo; **[PA · Bash]** consola Bash de PythonAnywhere; **[PA · Panel]** panel web; **[Navegador]**.
>
> **Horas:** `access.log` y `error.log` están en **UTC**; `server.log` está en **hora de Chile**. En noviembre, Chile continental es UTC-3. La ventana elegida (20:00 a 23:00, hora de Chile) cae entre las 23:00 y las 02:00 UTC: **desde las 21:00 de Chile la fecha UTC ya es la del día siguiente**. Por eso la parte C y la D filtran por instantes y no por día.

## Decisiones que fijan estos pasos (2026-11-06)

| Tema | Decisión | Dónde se aplica |
| :--- | :------- | :-------------- |
| Qué viaja | 03-01 a 03-04 en una sola etiqueta, sin migraciones | A3, B3 |
| Respaldo | Nuevo el día del despliegue, verificado antes de recargar | A2 |
| Ventana | `v3.1-integridad`, entre las 20:00 y las 23:00 (hora de Chile), un día entre el 2026-11-11 (después de anotar la medición de la 00-07) y el 2026-11-13 | A0, B |
| Aviso | Breve antes y Ctrl+F5 después (texto de la iteración; **aprobación literal pendiente de tu lectura**) | A4, C3 |
| Vigilancia | Lecturas solo los días 0 y 7 | C, D |
| Retroceso | Datos incorrectos o 5xx repetido: sí. Un `ERROR` aislado de ítem fallido: no | E |
| Réplica y AUD-05-002 | Último paso, después de la vigilancia | F |
| Pruebas | Una ejecución con `OK (expected failures=9)` y 267 pruebas, más `check --deploy` y `makemigrations` | A1 |

## Particularidades ya conocidas (aplicadas en los comandos)

- `python manage.py shell -c` imprime una línea extra («N objects imported automatically»): se toma solo la última con `| Select-Object -Last 1` (PowerShell) o `| tail -n 1` (Bash).
- Las variables con fecha y hora (`DESDE_CL`, `DESDE`) se escriben **sin** `<`, `>` ni texto, y se validan con el `grep` que sigue a cada una. En la 01-06, un valor con la plantilla puesta dejó los filtros sin resultado.
- El mensaje de la etiqueta se calcula con la fecha del día al crearla; no se escribe a mano (incidente de la 00-06).
- «Generar Nuevo Respaldo BD» es un enlace GET: cada visita crea un volcado y desplaza al más antiguo. **Un solo clic.** Si la descarga se corta (AUD-03-002), bájalo desde Files (`respaldo.md`, sección 2).
- En el servidor solo se ejecutan `git fetch origin --tags` y `git checkout <etiqueta>`. El prompt debe decir `(HEAD detached at <etiqueta>)` (`despliegue.md`, 3.2; incidente del 2026-11-03).
- El `index.js` no tiene nombre con hash: el navegador puede conservar el anterior. Solo lo usan los formularios con `data-bloquear-envio` (cotización, pago, cliente, producto, conversión y las confirmaciones de eliminar). **`pedido_form.html` no lo usa**: conserva su propio script de la 00-07 (decisión 8-C de la 03-04).

---

## Parte A · En tu PC, antes de tocar el servidor

### A0. Precondiciones

- [ ] La medición de la 00-07 está hecha y su resultado anotado en la parte D de [evidencia-00-07](../epica-00-blindaje/evidencia-00-07.md) (2026-11-11, hacia las 01:32).
- [ ] La web app está renovada (2026-11-10, vence el 2026-11-20).
- [ ] Elegiste el día del despliegue: entre el 2026-11-11 y el 2026-11-13, de 20:00 a 23:00 (hora de Chile).
- [ ] `git status --short` vacío y `main` igual a `origin/main` (A1).

**Cuenta de días.** Con `R` a las 20:00–23:00, el día 7 es la misma hora siete días después: `R` el 11-11 → día 7 el 11-18; el 11-12 → el 11-19; el 11-13 → el **11-20, el día del vencimiento de la web app y del informe C2** (2026-11-20). Si la renovación del 11-10 se hizo y extiende el plazo, no hay problema; si no se pudo verificar, conviene `R` el 11-11 o el 11-12 (sugerencia, tú decides).

| Dato | Valor |
| :--- | :---- |
| Día y hora planeados para `R` (hora de Chile) | … |
| Renovación de la web app (hecha / fecha de vencimiento nueva) | … |
| Resultado de la 00-07 (`segundos_repetidos`) | … |

### A1. Lista de comprobación **[PC · PowerShell 7]**

Con `docker compose up -d` encendido. El código no debe haber cambiado desde `7e14398` (último commit de código; después solo documentos).

```powershell
git fetch origin --tags
git status --short
git status -sb | Select-Object -First 1
git rev-parse HEAD origin/main
git diff --stat 7e14398..main -- . ":(exclude)_planificacion" ":(exclude)docs"
$env:DB_NAME = 'manzagrafica_replica'
python manage.py test pedidos
$env:DEBUG = 'False'; python manage.py check --deploy; Remove-Item Env:DEBUG
python manage.py makemigrations --check --dry-run
python manage.py showmigrations pedidos | Select-Object -Last 3
git diff --stat 5dc82a8..main -- pedidos/migrations requirements.txt PedidosApp/settings.py
git diff --stat 5dc82a8..main -- pedidos/static
```

**Esperado:**

- `git status --short` vacío; `## main...origin/main` **sin** `[ahead N]` ni `[behind N]`; los dos hashes de `rev-parse` iguales.
- El primer `git diff --stat` **sin salida** (si lista algo, hay código nuevo después de `7e14398`: detente y no etiquetes ese hash).
- `Ran 267 tests` y **`OK (expected failures=9)`**. Cualquier otro número de pruebas, `failures`, `errors` o `unexpected successes` **detiene el despliegue** (`despliegue.md`, punto 1). Las nueve son R6a, R6b, R6c, R7, R8, R9, R14, R15 y R19 (`pruebas.md`, sección 7.1). Puede salir la advertencia `mysql.W002`, esperada.
- `check --deploy`: solo `W004`, `W008`, `W009`, `W012` y `W016`. Una advertencia nueva o un `ERRORS:` detiene el despliegue.
- `makemigrations`: `No changes detected`.
- `showmigrations`: la última línea es `[X] 0007_registroevento`; ninguna migración nueva.
- Los dos últimos `git diff --stat` (`5dc82a8` es el commit de `v0.3-doble-envio`): el de migraciones, `requirements.txt` y `settings.py` **sin salida**; el de `pedidos/static` lista solo `pedidos/static/pedidos/js/index.js` (por eso hay `collectstatic`).

| # | Comprobación | Resultado |
| :- | :----------- | :-------- |
| 1 | `git status` vacío y `main` = `origin/main` | … |
| 2 | `git diff --stat 7e14398..main` (sin documentos) sin salida | … |
| 3 | Pruebas: `Ran N tests` y cierre | … (esperado `Ran 267 tests` · `OK (expected failures=9)`) |
| 4 | `check --deploy` (códigos) | … (esperado `W004 W008 W009 W012 W016`) |
| 5 | `makemigrations --check --dry-run` | … (esperado `No changes detected`) |
| 6 | `showmigrations pedidos`: última migración | … (esperado `[X] 0007_registroevento`) |
| 7 | `diff` de migraciones, `requirements.txt` y `settings.py` desde `5dc82a8` | … (esperado sin salida) |
| 8 | `diff` de `pedidos/static` desde `5dc82a8` | … (esperado solo `index.js`) |
| 9 | Estilos compilados | No aplica (se compila Tailwind desde la 08-05) |

### A2. Respaldo previo **[Navegador]** y **[PC · PowerShell 7]**

El día del despliegue y lo más cerca posible de `R`: en un retroceso del caso 3, se pierde todo lo registrado después del respaldo (`retroceso.md`, sección 4). Si cae en el mismo día del semanal (2026-11-10 u 11), cuenta como el semanal.

1. En producción, como superusuario: «Respaldar BD» → **un solo clic** en «Generar Nuevo Respaldo BD». Guarda la descarga directo en la carpeta cifrada.
2. Verifica:

```powershell
python scripts\verificar_respaldo.py "<ruta del volcado en la carpeta cifrada>"
$LASTEXITCODE
```

**Esperado:** `Tablas esperadas encontradas: 19 de 19`, `Tablas adicionales …: ninguna` y `Resultado: VÁLIDO`, código `0`. Referencia: el del 2026-11-04 00:12:37 (1.481.788 bytes; mínimo exigido, 500.000).

| Dato | Valor |
| :--- | :---- |
| Nombre del archivo (hora de Chile del nombre) | … |
| Tamaño (bytes) | … |
| SHA-256 | … |
| Tablas | … de 19 esperadas; faltantes: …; adicionales: … |
| Código | … |

Agrega la fila en `docs/operacion/respaldo.md`, sección 6 (motivo: «Previo al despliegue `v3.1-integridad` (iteración 03-05)»). _(Lo hace el agente al cerrar, con tus datos.)_

### A3. Etiqueta **[PC · PowerShell 7]**

Se crea el **día del despliegue**, solo con todo subido a `main`, sobre el último commit de código (`despliegue.md`, sección 1, «Etiquetar un commit anterior a la punta»). El mensaje toma la fecha del día.

```powershell
$hash = '7e14398'
git cat-file -t $hash
git log -1 --format='%h %s' $hash | Select-Object -First 1
git ls-remote --tags origin v3.1-integridad
git ls-remote --tags origin v0.3-doble-envio
git diff --stat $hash..main -- . ":(exclude)_planificacion" ":(exclude)docs"
$fecha = Get-Date -Format 'yyyy-MM-dd'
git tag -a v3.1-integridad $hash -m "Iteraciones 03-01 a 03-04 · desplegada el $fecha"
git tag -n v3.1-integridad
git push origin v3.1-integridad
git ls-remote --tags origin v3.1-integridad
```

**Esperado:**

- `git cat-file -t` responde `commit`.
- El primer `ls-remote` (`v3.1-integridad`) **no devuelve nada**: la etiqueta está libre. Si devuelve una línea, no la fuerces: usa el correlativo siguiente (`despliegue.md`, sección 1).
- El segundo `ls-remote` (`v0.3-doble-envio`) **devuelve una línea**: el destino de retroceso existe en GitHub.
- El `diff --stat` sin salida.
- `git tag -n` muestra el mensaje con la fecha real de hoy (revísalo **antes** del `push`; si está mal, `git tag -d v3.1-integridad` y créala de nuevo, porque todavía no está publicada).
- El último `ls-remote` devuelve una línea.

| Dato | Valor |
| :--- | :---- |
| Mensaje de la etiqueta | … |
| Commit de la etiqueta | … |
| Objeto de la etiqueta en el remoto (`ls-remote`) | … |
| Destino de retroceso en el remoto (`v0.3-doble-envio`) | … |

### A4. Aviso al cliente

- [ ] Leíste el texto propuesto en [la iteración, decisión 4](iteracion-03-05-validacion-y-despliegue-de-la-integridad.md) y lo **aprobaste tal cual o con tus cambios** (anótalos abajo). Es texto nuevo para el usuario: no estaba entre los «Textos aprobados» de la 03-04.
- [ ] Lo mandaste antes de `R`, con la hora real en lugar de `HH:MM`.

| Dato | Valor |
| :--- | :---- |
| Texto aprobado (tal cual / con cambios) | … |
| Canal y hora del envío (hora de Chile) | … |

---

## Parte B · Despliegue en PythonAnywhere

Los pasos son los de `despliegue.md`, 3.1 a 3.6, con las salidas que hay que anotar. Esta etiqueta **no** cambia dependencias ni migraciones y **sí** cambia estáticos (`index.js`).

### B1. Ubicarse **[PA · Bash]**

```bash
PROYECTO="/home/manzagrafica/ManzagraficaPedidosApp"
VENV="/home/manzagrafica/ManzagraficaPedidosApp/venv"
test -f "$PROYECTO/manage.py" && test -x "$VENV/bin/python" && echo "PROYECTO y VENV correctos"
cd "$PROYECTO"; source "$VENV/bin/activate"
git status --short
git rev-parse --short HEAD
git describe --tags --always
```

**Esperado:** `PROYECTO y VENV correctos`; `git status` vacío (o solo `?? media/…` y `?? staticfiles/`); `git rev-parse` = `5dc82a8`; `git describe` = `v0.3-doble-envio`. Si dice otra cosa, **detente**.

### B2. Estado previo, sin cambiar nada **[PA · Bash]**

```bash
python manage.py showmigrations pedidos | tail -n 2
python manage.py migrate --plan
python manage.py check --deploy 2>&1 | grep -oE '[a-z_]+\.[EW][0-9]{3}' | sort -u | tr '\n' ' '; echo
python manage.py shell -c "from django.contrib.sessions.models import Session; print('sesiones:', Session.objects.count())" | tail -n 1
date -u "+%F %T (UTC)"; TZ=America/Santiago date "+%F %T (hora de Chile)"
```

**Esperado:** última migración `[X] 0007_registroevento`; `No planned migration operations.`; la lista de códigos de producción antes del cambio (hasta ahora `security.W004 security.W008 security.W012 security.W016`; anótala para B5); el número de sesiones (opcional: es la línea base del riesgo «el token suma entradas a la sesión», todavía no medido); la hora.

| Dato | Valor |
| :--- | :---- |
| Commit y etiqueta antes | … |
| Últimas migraciones y `migrate --plan` | … |
| `check --deploy` antes (códigos) | … |
| Filas de `django_session` antes (opcional) | … |
| Hora antes de recargar (UTC / Chile) | … |

### B3. Traer la etiqueta **[PA · Bash]**

```bash
git fetch origin --tags
git checkout v3.1-integridad
git describe --tags
git rev-parse --short HEAD
git diff --stat v0.3-doble-envio v3.1-integridad -- requirements.txt pedidos/migrations PedidosApp/settings.py
git diff --stat v0.3-doble-envio v3.1-integridad -- pedidos/static
```

**Esperado:**

- `git describe --tags` responde exactamente `v3.1-integridad` (en `detached HEAD`, como siempre) y `git rev-parse` da el mismo commit que anotaste en A3.
- El primer `diff` **sin salida**: sin dependencias nuevas (3.3), sin migraciones (3.4) y sin cambios de configuración.
- El segundo `diff` lista **solo** `pedidos/static/pedidos/js/index.js`: hay `collectstatic` (3.5).

| Dato | Valor |
| :--- | :---- |
| `git describe --tags` y commit | … |
| `diff` de `requirements.txt`, migraciones y `settings.py` | … |
| `diff` de `pedidos/static` | … |

### B4. Migraciones y estáticos **[PA · Bash]**

```bash
python manage.py migrate --plan
python manage.py showmigrations pedidos | tail -n 2
python manage.py collectstatic --noinput | tail -n 2
grep -c 'bloquearBoton' "$PROYECTO/staticfiles/pedidos/js/index.js"
```

**Esperado:** `No planned migration operations.` (si lista algo, **detente**: no debería haber migraciones); la última migración sigue en `[X] 0007_registroevento`; `collectstatic` termina con `N static files copied` (con `N` mayor que 0, y el resto `unmodified`); el último `grep` da `3` o más (la función aparece definida y usada en `index.js`; si da `0`, la copia no llegó).

| Dato | Valor |
| :--- | :---- |
| `migrate --plan` | … |
| `collectstatic` (última línea) | … |
| Conteo de `bloquearBoton` en `staticfiles/…/index.js` | … |

### B5. Revisión de configuración **[PA · Bash]**

```bash
python manage.py check
python manage.py check --deploy 2>&1 | grep -oE '[a-z_]+\.[EW][0-9]{3}' | sort -u | tr '\n' ' '; echo
python manage.py check --deploy 2>&1 | grep -c 'ERRORS'
```

**Esperado:** `System check identified no issues (0 silenced).`; la lista de códigos **igual** a la de B2; `ERRORS` en `0`.

| Dato | Valor |
| :--- | :---- |
| `check` | … |
| `check --deploy` después (códigos) y `ERRORS` | … |

### B6. Recargar **[PA · Panel]** y anotar `R` **[PA · Bash]**

1. Anota la hora de tu reloj y pestaña **Web** → **Reload manzagrafica.pythonanywhere.com**. Espera a que el botón vuelva a su estado normal.
2. **La hora oficial `R` es la del reinicio efectivo** (línea `Starting uWSGI` de `server.log`, en hora de Chile), no la de tu reloj ni la del clic (`despliegue.md`, 3.6). Escribe aquí la hora **de tu reloj menos unos minutos**, sin `<` ni `>`:

```bash
S=/var/log/manzagrafica.pythonanywhere.com.server.log
DESDE_CL="AAAA-MM-DD HH:MM:SS"
echo "$DESDE_CL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE_CL válido"
for f in "$S" "$S".*; do [ -f "$f" ] && zcat -f "$f"; done \
  | awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9:]+ \*\*\* Starting uWSGI/ && substr($0,1,19) >= d { print substr($0,1,19), "Starting uWSGI" }' \
  | sort
```

**Esperado:** `DESDE_CL válido` y **una** línea con la hora del reinicio. Esa es `R`. Con `R` en la mano, fija las dos variables definitivas (la hora de Chile y su equivalente en UTC, que es Chile + 3 horas en noviembre):

```bash
DESDE_CL="AAAA-MM-DD HH:MM:SS"
echo "$DESDE_CL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE_CL válido"
DESDE=$(date -u -d "$DESDE_CL UTC +3 hours" "+%F %T"); echo "R: $DESDE_CL (Chile) = $DESDE (UTC)"
```

Revisa que el segundo valor sea el primero más 3 horas (por ejemplo, 21:34:10 de Chile = 00:34:10 UTC **del día siguiente**). Si cierras la consola, vuelve a definir `S`, `DESDE_CL` y `DESDE`.

| Dato | Valor |
| :--- | :---- |
| Hora del clic de Reload (tu reloj, Chile) | … |
| **`R` oficial** (`Starting uWSGI`, Chile) | … |
| `R` en UTC | … |
| Reinicios desde `DESDE_CL` (cuántas líneas) | … (esperado 1) |

---

## Parte C · Día 0: la misma noche

Todo lo de esta parte se hace **después de `R`**, el mismo día. Es solo lectura, salvo la prueba de C4, que **no debe crear nada**. Si cualquier pantalla responde 500 o un formulario no guarda, **no sigas**: pasa a la parte E.

### C0. Preparación de la consola **[PA · Bash]**

Se usa también en la parte D. Si cierras la consola, vuelve a pegarlo.

```bash
PROYECTO="/home/manzagrafica/ManzagraficaPedidosApp"; VENV="$PROYECTO/venv"
cd "$PROYECTO"; source "$VENV/bin/activate"
S=/var/log/manzagrafica.pythonanywhere.com.server.log
D=manzagrafica.pythonanywhere.com
desde() { awk -v d="$2" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] / && substr($0,1,19) >= d {f=1} f' "$1"; }
ventana() { (cd /var/log && zcat -f $D.access.log*) | awk -v a="$1" -v b="$2" 'BEGIN{split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec",M," ");for(i=1;i<=12;i++)m[M[i]]=sprintf("%02d",i)} match($0,/\[[0-9]+\/[A-Za-z]+\/[0-9]+:[0-9:]+ /){t=substr($0,RSTART+1,RLENGTH-2);split(t,p,/[\/:]/);k=p[3] m[p[2]] p[1] p[4] p[5] p[6]; if(k>=a&&k<b)print}'; }
DESDE_CL="AAAA-MM-DD HH:MM:SS"; DESDE="AAAA-MM-DD HH:MM:SS"
echo "$DESDE_CL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE_CL válido"
echo "$DESDE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE válido"
```

Antes de pegarlo, reemplaza **solo** los dos valores de la penúltima línea por los de B6 (Chile y UTC). **Esperado:** `DESDE_CL válido` y `DESDE válido`. La función `desde` corta `server.log` en la primera línea con fecha ≥ la indicada (la de la 01-06); `ventana A B` imprime las líneas de `access.log` (también las rotadas) cuyo instante UTC cae entre `A` y `B`, con `A` y `B` como `AAAAMMDDHHMMSS`. Esa función **no se probó contra el archivo real**: se probó solo con líneas sintéticas en el formato `[12/Nov/2026:23:41:05 +0000]`. Si en C5 no sale nada, pega `tail -n 1` del `access.log` con la IP recortada y el agente ajusta el filtro.

### C1. Verificación inmediata **[Navegador]**

En ventana privada (`despliegue.md`, 3.7). No uses «Estadísticas» (AUD-01-006). **No envíes ningún formulario.**

1. Inicia sesión; abre el panel, el listado de pedidos y el detalle de un pedido.
2. Abre `/pedidos/nuevo/`, `/cotizaciones/nueva/` y `/pagos/ingresar/`: cargan, sin 500.
3. En cada una, ver código fuente (Ctrl+U) y busca `token_envio`: debe aparecer `<input type="hidden" name="token_envio" value="…">` (no copies el valor).

| Revisión | Resultado |
| :------- | :-------- |
| Acceso, panel, listado y detalle de pedido | … |
| `/pedidos/nuevo/` carga y trae `token_envio` | … |
| `/cotizaciones/nueva/` carga y trae `token_envio` | … |
| `/pagos/ingresar/` carga y trae `token_envio` | … |

### C2. Estáticos: Ctrl+F5 y prueba del botón **[Navegador]**

Prueba sin enviar nada al servidor, en `/pagos/ingresar/` (usa `index.js`). Muestra a la vez si el navegador conservó el `index.js` anterior y si el bloqueo funciona.

1. Abre `/pagos/ingresar/` con una recarga **normal** (F5, no Ctrl+F5).
2. En la consola del navegador (F12) pega:

```js
const f = document.querySelector('form[data-bloquear-envio]'); f.noValidate = true;
f.addEventListener('submit', e => { e.preventDefault(); const b = f.querySelector('button[type="submit"]'); console.log('bloqueado=', b.disabled, '| texto=', b.textContent.trim()); });
```

3. Pulsa **una vez** el botón de guardar. `preventDefault` evita el envío: **no sale ninguna petición al servidor**.
4. **Esperado con el `index.js` nuevo:** `bloqueado= true | texto= Guardando…`. Si sale `bloqueado= false`, el navegador tiene el `index.js` anterior en caché: haz **Ctrl+F5** y repite desde el paso 2; ahora debe salir `true`. Anota cuál fue tu caso (es la prueba de lo que hoy es «inferido, no probado»).

| Dato | Valor |
| :--- | :---- |
| Recarga normal (F5): `bloqueado` y texto | … |
| Tras Ctrl+F5 (solo si hizo falta): `bloqueado` y texto | … |
| ¿Se vio el `index.js` anterior en caché? | … |

### C3. Aviso a quien usa la aplicación

- [ ] Pediste cerrar la pestaña y abrir la aplicación de nuevo (o Ctrl+F5), como dice el texto aprobado en A4.

### C4. La línea `INFO` del rechazo **[Navegador]**

Verificación deliberada de la decisión 5b de la iteración. Debe terminar **sin crear nada**: el servidor revisa el token antes de validar el formulario (`views.py`, `ingresar_pago`), y además dejas el formulario vacío.

1. Anota la hora de tu reloj. Abre `/pagos/ingresar/` (carga nueva).
2. En la consola (F12) pega:

```js
document.querySelector('[name="token_envio"]').value = '';
document.querySelector('form[data-bloquear-envio]').noValidate = true;
```

3. Pulsa **una vez** el botón de guardar, con el formulario **vacío** (no elijas pedido ni escribas monto).
4. **Esperado:** vuelve el formulario con el aviso rojo «Este formulario venció y no se guardó. Revisa los datos y vuelve a guardar.» y **ningún pago nuevo**.

| Dato | Valor |
| :--- | :---- |
| Hora del envío (tu reloj, Chile) | … |
| Aviso en pantalla (texto) | … |
| ¿Se creó algún pago? (revisa el listado de pagos) | … |

### C5. Lectura de `server.log` **[PA · Bash]**

```bash
desde $S "$DESDE_CL" | grep -o 'nivel=[A-Z]*' | sort | uniq -c
desde $S "$DESDE_CL" | grep 'nivel=ERROR' | grep -oE 'registrador=[^ ]+( metodo=[A-Z]+ ruta=[^ ]+)?' | sort | uniq -c
desde $S "$DESDE_CL" | grep 'nivel=INFO' | grep -c 'Envío sin token válido'
desde $S "$DESDE_CL" | grep 'nivel=INFO' | grep 'Envío sin token válido' | cut -c1-200
```

**Esperado:**

- Por nivel: **ningún `ERROR` nuevo** (salvo `registrador=root` con `OSError: write error`, ya clasificado en AUD-04-004), y los `INFO`.
- La línea `INFO` de C4: **al menos una**, con `metodo=POST ruta=/pagos/ingresar/ usuario=<tu id>` y `mensaje="Envío sin token válido; no se guardó nada"`. Si alguien tenía un formulario abierto al reiniciar, puede haber más: no son errores (`despliegue.md`, 3.9).
- Pega solo las líneas pedidas (cabecera y `INFO`), nunca el texto de una traza.

| Dato | Valor |
| :--- | :---- |
| Conteo por nivel desde `R` | … |
| `ERROR` por registrador (y ruta) | … |
| Líneas `INFO` «Envío sin token válido» (cuántas) y su cabecera | … |
| ¿La de C4 aparece (método, ruta, usuario)? | … |

Si C4 no deja la línea `INFO`, no es un error: anótalo y, al cerrar, el agente deja la fila de `despliegue.md`, 3.9, como «sin verificar» o la retira (decisión 5b, opción C).

### C6. Duplicados, línea base del día 0 **[PA · Bash]**

Compara los `POST /pedidos/nuevo/` que respondieron 302 en `access.log` con los pedidos nuevos de la base, en la misma ventana (desde `R` hasta ahora). Con el token, un envío repetido también responde 302 y termina en el pedido ya creado, así que `access.log` solo no distingue un duplicado de un repetido rechazado.

```bash
HASTA=$(date -u "+%F %T"); echo "ventana UTC: $DESDE -> $HASTA"
A=$(echo "$DESDE" | tr -d ' :-'); B=$(echo "$HASTA" | tr -d ' :-')
ventana "$A" "$B" | grep '"POST /pedidos/nuevo/ ' | grep -oE '" [0-9]{3} ' | sort | uniq -c
export DESDE HASTA
python manage.py shell <<'PY' | tail -n 1
import os
from datetime import datetime, timezone as tz
from django.db.models import Count
from pedidos.models import Pedido, RegistroEvento

fmt = '%Y-%m-%d %H:%M:%S'
a = datetime.strptime(os.environ['DESDE'], fmt).replace(tzinfo=tz.utc)
b = datetime.strptime(os.environ['HASTA'], fmt).replace(tzinfo=tz.utc)
eventos = RegistroEvento.objects.filter(momento__gte=a, momento__lt=b)
creado = eventos.filter(tipo='pedido_creado').count()
duplicado = eventos.filter(tipo='pedido_duplicado').count()
convertida = eventos.filter(tipo='cotizacion_convertida').count()
pedidos = Pedido.objects.filter(fecha_solicitud__gte=a, fecha_solicitud__lt=b)
grupos = (pedidos.values('cliente_id', 'resumen_pedido', 'valor_venta')
          .annotate(n=Count('id')).filter(n__gt=1).count())
print('pedidos_nuevos=%d eventos_creado=%d eventos_duplicado=%d eventos_convertida=%d grupos_repetidos=%d'
      % (pedidos.count(), creado, duplicado, convertida, grupos))
PY
```

Solo imprime conteos: ninguna IP, nombre ni monto. Es de **solo lectura** (`filter` y `count`); no escribe en la base.

**Cómo se lee:**

- El primer bloque da los `POST /pedidos/nuevo/` por código en la ventana: los `302` son los pedidos creados **más** los envíos repetidos redirigidos; los `200` son formularios devueltos con aviso (validación, ítem fallido o token vencido, como el de C4); un `500` es motivo de la parte E.
- `eventos_creado` (`crear_pedido`) cuadra con los `302` cuando no hubo repetidos. `302 − eventos_creado` = envíos repetidos que el token redirigió (informativo, no es un defecto).
- `pedidos_nuevos` debe ser igual a `eventos_creado + eventos_duplicado + eventos_convertida` (las tres vías que crean un pedido). Si no coincide, anota los números y no concluyas.
- **`grupos_repetidos=0` es el criterio de «sin duplicados»:** grupos de pedidos con el mismo cliente, el mismo resumen y el mismo valor de venta creados dentro de la ventana. Es un criterio **provisorio** de esta evidencia, no el de la consulta histórica de la 06-04 (`PENDIENTE_DESARROLLADOR`). Dos pedidos legítimos iguales también cuentan: si sale mayor que 0, mira cuándo se crearon con la hora de `fecha_solicitud` antes de concluir.
- El guion queda probado solo en sintaxis y con líneas sintéticas: no se ejecutó contra la base.

| Dato | Valor |
| :--- | :---- |
| `POST /pedidos/nuevo/` por código (200 / 302 / otros) | … |
| `pedidos_nuevos`, `eventos_creado`, `eventos_duplicado`, `eventos_convertida` | … |
| `grupos_repetidos` | … |

### C7. Cierre del día 0

- [ ] Sin 500 en las pantallas; los tres formularios traen `token_envio` (C1).
- [ ] `server.log` desde `R` sin `ERROR` nuevo (C5), o clasificados con la tabla de `despliegue.md`, 3.9.
- [ ] La línea `INFO` verificada o su estado explicado (C4 y C5).
- [ ] Botón y caché de `index.js` probados (C2).
- [ ] Sin pedidos duplicados en la línea base (C6).

**Riesgo anotado (decisión 5 del 2026-11-06).** Con lecturas solo los días 0 y 7, **un problema de los días 1 a 6 solo se vería si el cliente lo reporta**. Además, la lectura del día 0 ocurre de noche, antes del primer uso real del negocio (inferido: es la hora de menor uso). **Sugerencia, sin decidir:** una lectura extra **a demanda** (con los mismos comandos de C5 y C6), por ejemplo la primera mañana tras `R` o apenas el cliente avise de un «no se guardó» o de un botón que no responde. Cada lectura es corta, pero consume parte de los 100 s diarios de CPU de la consola.

---

## Parte D · Día 7 y criterio de cierre **[PA · Bash]**

Se hace siete días después de `R`, a la misma hora (cae entre las 20:00 y las 23:00 de Chile). **Es la única lectura de la semana además de la del día 0.** Cubre toda la semana: de `R` a ahora.

### D1. Preparación

```bash
LIMITE=$(date -u -d "$DESDE UTC +7 days" "+%F %T"); HASTA=$(date -u "+%F %T")
echo "R: $DESDE UTC | límite de 7 días: $LIMITE | ahora: $HASTA"
[[ "$HASTA" > "$LIMITE" || "$HASTA" == "$LIMITE" ]] && echo "ya pasaron 7 días" || echo "AÚN NO pasan 7 días: espera"
A=$(echo "$DESDE" | tr -d ' :-'); B=$(echo "$HASTA" | tr -d ' :-'); export DESDE HASTA
```

Usa la preparación de C0 (con `S`, `D`, `desde`, `ventana`, `DESDE_CL` y `DESDE` de B6). **Esperado:** `ya pasaron 7 días`.

### D2. `server.log` de la semana

```bash
desde $S "$DESDE_CL" | grep -o 'nivel=[A-Z]*' | sort | uniq -c
desde $S "$DESDE_CL" | grep 'nivel=ERROR' | grep -oE 'registrador=[^ ]+( metodo=[A-Z]+ ruta=[^ ]+)?' | sort | uniq -c
desde $S "$DESDE_CL" | grep 'nivel=ERROR' | grep -oE '^[0-9-]+ [0-9:]+' | sort | uniq -c
desde $S "$DESDE_CL" | grep 'nivel=INFO' | grep -c 'Envío sin token válido'
for f in "$S" "$S".*; do [ -f "$f" ] && zcat -f "$f"; done | awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9:]+ \*\*\* Starting uWSGI/ && substr($0,1,19) >= d { print substr($0,1,19), "Starting uWSGI" }' | sort
```

**Esperado:** ningún `ERROR` nuevo de `django.request` ni de `pedidos.views` en las rutas modificadas, descontando lo ya clasificado (`registrador=root` con `OSError: write error`, AUD-04-004) y los `ERROR` de ítem fallido que se expliquen (aviso en pantalla, respuesta 200; ver E). El tercer comando da la **hora** de cada `ERROR` para cruzarla con lo que reporte el cliente. El último lista los reinicios de la semana: debe estar el de `R` y ningún otro inesperado (anótalos aparte; el informe C2 de la 00-06 del 2026-11-20 los contará).

Para cada `ERROR` nuevo, clasifica con la tabla de `despliegue.md`, 3.9, y **anota solo el tipo y la hora**: nunca el texto de la traza. Si hace falta la traza: `grep "^AAAA-MM-DD HH:" $S | grep "ruta=/la/ruta/" | sed 's/#012/\n/g'` en la consola, sin copiarla.

| Dato | Valor |
| :--- | :---- |
| Conteo por nivel (semana) | … |
| `ERROR` por registrador y ruta | … |
| Horas de los `ERROR` | … |
| `INFO` «Envío sin token válido» (cuántas) | … |
| Reinicios de uWSGI desde `R` | … |
| Clasificación de cada `ERROR` (tipo y hora) | … |

### D3. `access.log` de la semana

```bash
ventana "$A" "$B" | grep -E '"(GET|POST) /(pedidos/nuevo|pedido/editar|cotizaciones/nueva|cotizaciones/editar|cotizaciones/convertir|pagos/ingresar)/' | sed -E 's/.*"(GET|POST) ([^ ?]*)[^"]*" ([0-9]{3}) .*/\1 \2 \3/; s#/[0-9]+/#/N/#' | sort | uniq -c
ventana "$A" "$B" | grep -oE '" 5[0-9]{2} ' | sort | uniq -c
ventana "$A" "$B" | grep -E '"GET /(pedidos/nuevo|cotizaciones/nueva|pagos/ingresar)/ ' | grep -oE 'response-time=[0-9.]+' | cut -d= -f2 | sort -n | awk '{v[NR]=$1} END{if(NR) printf "n=%d min=%s mediana=%s max=%s\n", NR, v[1], v[int((NR+1)/2)], v[NR]; else print "sin datos de response-time"}'
```

**Esperado:**

- El primer bloque: método, ruta (con `N` en lugar del número) y código, con su conteo. **Ningún `500`** en las rutas de creación y edición.
- El segundo: todos los `5xx` de la semana, por código. En la recarga de `R` pueden salir `502` (unos 10 s, AUD-04-002); anótalos aparte.
- El tercero: tiempo de respuesta de los tres formularios (con las +3 consultas aceptadas). La banda medida en producción es de 0,03 a 1,13 s fuera de las recargas (Auditoría 04); la primera respuesta tras `R` puede tardar de 5,6 a 9 s (AUD-04-005): si el máximo sale de la banda, mira si fue esa. **El umbral de «sin salir de la banda» es `PENDIENTE_DESARROLLADOR`.** Los nombres `response-time=` y su formato **no se probaron contra el archivo real** (solo constan en `definicion-epica-13.md`): si sale «sin datos», pega `tail -n 1` del `access.log` con la IP recortada.

| Dato | Valor |
| :--- | :---- |
| Rutas de creación y edición por método y código | … |
| `5xx` de la semana por código (y cuántos son de la recarga) | … |
| Tiempos de los tres formularios (`n`, mínimo, mediana, máximo) | … |

### D4. Duplicados de la semana (302 contra pedidos nuevos)

```bash
ventana "$A" "$B" | grep '"POST /pedidos/nuevo/ ' | grep -oE '" [0-9]{3} ' | sort | uniq -c
python manage.py shell <<'PY' | tail -n 1
import os
from datetime import datetime, timezone as tz
from django.db.models import Count
from pedidos.models import Pedido, RegistroEvento

fmt = '%Y-%m-%d %H:%M:%S'
a = datetime.strptime(os.environ['DESDE'], fmt).replace(tzinfo=tz.utc)
b = datetime.strptime(os.environ['HASTA'], fmt).replace(tzinfo=tz.utc)
eventos = RegistroEvento.objects.filter(momento__gte=a, momento__lt=b)
creado = eventos.filter(tipo='pedido_creado').count()
duplicado = eventos.filter(tipo='pedido_duplicado').count()
convertida = eventos.filter(tipo='cotizacion_convertida').count()
pedidos = Pedido.objects.filter(fecha_solicitud__gte=a, fecha_solicitud__lt=b)
grupos = (pedidos.values('cliente_id', 'resumen_pedido', 'valor_venta')
          .annotate(n=Count('id')).filter(n__gt=1).count())
print('pedidos_nuevos=%d eventos_creado=%d eventos_duplicado=%d eventos_convertida=%d grupos_repetidos=%d'
      % (pedidos.count(), creado, duplicado, convertida, grupos))
PY
python manage.py shell -c "from django.contrib.sessions.models import Session; print('sesiones:', Session.objects.count())" | tail -n 1
```

Es el mismo guion de C6, ahora con la semana completa (se lee igual). El último comando es opcional: compara las filas de `django_session` con la línea base de B2.

| Dato | Valor |
| :--- | :---- |
| `POST /pedidos/nuevo/` por código (semana) | … |
| `pedidos_nuevos`, `eventos_creado`, `eventos_duplicado`, `eventos_convertida` | … |
| `grupos_repetidos` | … |
| Filas de `django_session` ahora (opcional) | … |

### D5. Criterio de cierre

La iteración se cierra cuando **todas** estas casillas están marcadas, o cada excepción queda explicada por escrito. Cada una remite a la lectura que la prueba.

- [ ] **(i)** Siete días desde `R` sin `ERROR` nuevo de `django.request` ni de `pedidos.views` en las rutas modificadas, descontando lo ya clasificado y los ítems fallidos explicados (D2).
- [ ] **(ii)** Ningún `5xx` en las rutas de creación y edición (D3).
- [ ] **(iii)** Ningún pedido, cotización ni pago duplicado en la ventana: `grupos_repetidos=0` y las cuentas de D4 cuadran (D4). `access.log` solo **no** decide este punto.
- [ ] **(iv)** Tiempos de los tres formularios sin salir de la banda medida (D3). Umbral `PENDIENTE_DESARROLLADOR`.
- [ ] **(v)** La línea `INFO` verificada (C4 y C5) o su estado explicado.
- [ ] Nadie reportó un doble envío, un «no se guardó» ni un botón que no responde durante la semana (dicho por el desarrollador).

| Criterio | Resultado | Excepción explicada |
| :------- | :-------- | :------------------ |
| (i) `ERROR` nuevos | … | … |
| (ii) `5xx` en creación y edición | … | … |
| (iii) duplicados | … | … |
| (iv) tiempos | … | … |
| (v) línea `INFO` | … | … |
| Reportes del cliente | … | … |

Con esto se cierra la parte de servidor de AUD-04-001 (`auditoria-tecnica.md`) y el criterio de término de la Épica 03. El agente deja después la bitácora de producción, la fila de `despliegue.md`, sección 5, y las notas fechadas.

---

## Parte E · Retroceso (solo si se cumple la regla)

### E1. Regla (decisión 6, 2026-11-06)

| Qué aparece | ¿Retroceder? | Qué hacer |
| :---------- | :----------- | :-------- |
| **Datos incorrectos o perdidos** (montos, pedidos, pagos) | **Sí**: detén, avisa y evalúa el caso 3 (restaurar) | Parte E3 |
| **5xx repetido**, o un formulario que no guarda, en una vista modificada | **Sí**: caso 1 | Parte E2 |
| **Un `ERROR` aislado** de ítem fallido, con el aviso en pantalla y respuesta 200 | **No** | Saca la traza (`despliegue.md`, 3.9), reprodúcelo en la réplica y anota solo el tipo y la hora |
| Líneas `INFO` de rechazo («Envío sin token válido») | No: sin acción | — |

Todo `ERROR` nuevo se clasifica con la tabla de `despliegue.md`, 3.9, **antes** de decidir. Los umbrales de «repetido» y «aislado» no tienen número: **`PENDIENTE_DESARROLLADOR`**. Propuesta, sin decidir: «repetido» = dos o más `5xx` en la misma ruta de creación o edición dentro de la ventana medida; «aislado» = un solo `ERROR` de ítem fallido sin otro igual. Tampoco queda dicho qué pasa con **varios** `ERROR` de ítem fallido: se decide al verlos.

### E2. Caso 1 · Volver el código **[PA · Bash]** y **[PA · Panel]**

Sin migraciones que deshacer. Anota la hora de inicio (Chile): la meta es menos de 15 minutos (`retroceso.md`).

```bash
cd "$PROYECTO"; source "$VENV/bin/activate"
git describe --tags
git checkout v0.3-doble-envio
git describe --tags
python manage.py collectstatic --noinput | tail -n 2
python manage.py check
```

Después, **[PA · Panel]**: pestaña **Web** → **Reload**. Y de nuevo **[PA · Bash]**:

```bash
grep -c 'bloquearBoton' "$PROYECTO/staticfiles/pedidos/js/index.js"
```

**Esperado:** el primer `describe` dice `v3.1-integridad`; el segundo, exactamente `v0.3-doble-envio`; `collectstatic` termina con `N static files copied`; `check` sin problemas; el `grep` final da `0` (el `index.js` anterior no tiene `bloquearBoton`). Verifica las tres pantallas y el registro de errores (`despliegue.md`, 3.7) y anota la `R` del retroceso con la misma regla (`Starting uWSGI`).

Una sesión con la clave `tokens_envio` no debería molestar al código anterior, que no la lee (**inferido, no ensayado**): anota si pasó algo raro con las sesiones abiertas.

| Dato | Valor |
| :--- | :---- |
| Motivo (regla E1) y hora de inicio (Chile) | … |
| `describe` antes / después | … |
| `collectstatic` y conteo de `bloquearBoton` | … |
| `R` del retroceso y resultado de las tres pantallas | … |
| Minutos totales | … |

Agrega la fila en `docs/operacion/retroceso.md`, sección 6, y deja la etiqueta publicada sin moverla ni borrarla (`despliegue.md`, sección 1).

### E3. Caso 3 · Datos dañados

**Se pierde todo lo registrado después del respaldo de A2** (pedidos, pagos, cambios de estado). Úsalo solo si el caso 1 no basta. Sigue `retroceso.md`, sección 4, con el volcado de A2 (nombre y SHA-256 de la tabla de A2) y avisa al equipo de qué debe volver a ingresar.

| Dato | Valor |
| :--- | :---- |
| Motivo (datos incorrectos: cuáles, sin cifras de clientes) | … |
| Volcado usado (nombre y SHA-256) | … |
| Resultado y qué debió volver a ingresarse | … |

---

## Parte F · Limpieza de la réplica y AUD-05-002 (último paso)

**Solo después de cerrar la parte D** (decisión 7): la réplica sigue disponible durante la semana para reproducir cualquier error. Con este paso se cierra la Épica 03.

### F1. Qué respaldo usar

`PENDIENTE_DESARROLLADOR`, sin decidir: el texto de AUD-05-002 y del registro dice «con el respaldo del 2026-11-04 00:12:37, sin respaldo nuevo». Con la decisión 2 habrá uno del día del despliegue, y al llegar aquí habrá además un semanal más reciente. Opciones: (a) el del despliegue; (b) el semanal verificado más reciente (más cercano al estado real de producción); (c) el del 2026-11-04, como dice hoy el texto. Anota cuál usas y por qué.

| Dato | Valor |
| :--- | :---- |
| Respaldo elegido (nombre, SHA-256, tamaño) | … |
| Motivo | … |

### F2. Trasladar el disco de Docker a D: (o cifrar C:) **[PC · PowerShell 7]**

1. Con Docker Desktop: *Settings → Resources → Advanced → Disk image location*, apúntalo a una carpeta de **D:** (la ruta exacta y el nombre del archivo dependen de tu versión de Docker Desktop: **no se pudo verificar**) y aplica el cambio. **No uses `docker compose down -v` ni borres `mysql_data`** (`AGENTS.md`, sección 5).
2. Comprueba el cifrado y la ubicación (`replica-local.md`, sección 2):

```powershell
manage-bde -status D:
Get-ChildItem "<ruta de Disk image location>" -Recurse -Filter *.vhdx | Select-Object FullName, Length
Get-ChildItem "$env:LOCALAPPDATA\Docker" -Recurse -Filter *.vhdx -ErrorAction SilentlyContinue | Select-Object FullName, Length
```

**Esperado:** `Protección activada` y `Porcentaje cifrado: 100,0 %` en D:; un `.vhdx` con ruta en D:; y el **último comando sin ningún `.vhdx` con datos en C:** (la ruta del último comando es la habitual de Docker Desktop, pero no se verificó en tu equipo: si no existe, revisa la carpeta que indique Docker).

| Dato | Valor |
| :--- | :---- |
| `manage-bde -status D:` (protección y porcentaje) | … |
| Ruta del `.vhdx` ahora (solo unidad y carpeta) | … |
| ¿Queda un `.vhdx` con datos en C:? | … |

### F3. Refrescar la réplica **[PC · PowerShell 7]**

Sigue `replica-local.md`, sección 9. **Revisa dos veces el nombre de la base: solo `manzagrafica_replica`.** Este refresco también borra los datos de prueba de las revisiones de la 03-03 y la 03-04.

```powershell
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE manzagrafica_replica; CREATE DATABASE manzagrafica_replica CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
$t = Measure-Command { cmd /c "docker compose exec -T db sh -c ""exec mysql -uroot -p`$MYSQL_ROOT_PASSWORD manzagrafica_replica"" < ""<ruta del volcado de F1>""" }
"Código: $LASTEXITCODE · Segundos: $([math]::Round($t.TotalSeconds, 1))"
$env:DB_NAME = 'manzagrafica_replica'
python manage.py showmigrations pedidos | Select-Object -Last 2
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "SELECT COUNT(*) AS tablas FROM information_schema.tables WHERE table_schema = ''manzagrafica_replica'';"'
```

**Esperado:** código `0`; la última migración aplicada es `[X] 0007_registroevento`; `tablas = 19` (las 19 de `verificar_respaldo.py`). Anota la fila en la tabla de `replica-local.md`, sección 9 (fecha del refresco, volcado en hora de Chile, segundos y paridad).

### F4. Repetir el conteo de pedidos sin ítems **[PC · PowerShell 7]**

Repite las consultas 1 a 3 de la «Evidencia P3» de la [iteración 03-02](iteracion-03-02-erradicacion-supresion-silenciosa.md) sobre la réplica refrescada (solo `SELECT` y solo agregados; sin nombres, teléfonos ni montos). La primera ejecución fue el 2026-11-04 (888 pedidos, 126 sin ítems, 38 sin ítems posteriores al primero con ítems; 27 cotizaciones, 0 sin ítems) sobre un volcado del 2026-10-25; ahora el volcado es más reciente.

| Dato | Valor |
| :--- | :---- |
| Pedidos, sin ítems, sin ítems posteriores al primero con ítems | … |
| Cotizaciones y sin ítems | … |

| Cierre de la parte F | Valor |
| :------------------- | :---- |
| Refresco (código y segundos) y tablas | … |
| AUD-05-002: disco en D: y sin `.vhdx` en C: | … |
| Conteo de F4 repetido | … |

---

## Lo que no se pudo verificar

- **Producción:** qué etiqueta corre hoy, el contenido de `server.log` y `access.log`, el nombre real de `response-time=` y el formato exacto de las líneas de `access.log`. Nada de esta evidencia se ejecutó.
- **Los guiones de las partes C y D:** `ventana` se probó solo con líneas sintéticas (GNU awk); el `sed` de rutas y el cálculo del tiempo de respuesta, también solo con líneas sintéticas; el script de Python se revisó solo en sintaxis (Python 3.13) y no se ejecutó contra ninguna base. Sus nombres de campo (`fecha_solicitud`, `momento`, `tipo`, `cliente_id`, `resumen_pedido`, `valor_venta`) salen de `models.py`.
- **El filtro de zona horaria:** la conversión Chile → UTC es una suma de 3 horas (UTC-3 en noviembre), no una consulta a la base de zonas horarias.
- **La prueba del botón (C2) y la línea `INFO` (C4):** el orden de los controladores de `submit` y de la revisión del token sale de leer `index.js` y `views.py`, no de verlos en producción.
- **El criterio de «duplicado»** (`grupos_repetidos`) es provisorio; la consulta histórica y su criterio exacto son de la 06-04.
- **Las rutas del disco de Docker** (parte F): dependen de tu versión de Docker Desktop.
- **`git tag`:** no se pudo comprobar que `v3.1-integridad` esté libre (el agente no ejecuta `git tag`); lo comprueba A3.
- **Horas de uso del cliente entre semana:** sigue sin medirse; la ventana de 20:00 a 23:00 es decisión del desarrollador.

## Respuesta del desarrollador

_Pendiente._ Se consolidará aquí, parte por parte, cuando se ejecute la iteración.
