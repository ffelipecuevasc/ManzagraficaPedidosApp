# Evidencia 00-06 · Correcciones tempranas de riesgo nulo

- **Fecha del pedido:** 2026-10-23
- **Pedido por:** Claude Code (Opus 5.5)
- **Criterios que dependen de esta evidencia:** importación de `pedidos.urls` más rápida que antes; `weasyprint` fuera de `sys.modules`; PDF, `robots.txt`, `pagos/lista/` y botón de acceso revisados en local; despliegue con etiqueta propia; 404 de `/robots.txt` en 0 por día.

> Este archivo existe porque el agente no puede obtener estos datos por su cuenta. Responde solo lo que se pide.
>
> **Orden:** parte A (local) → el agente la revisa → parte B (despliegue) → uno o dos días después, parte C1. La parte C2 (28 días) va en paralelo y no bloquea la Épica 01.

## Qué intentó el agente

| Dato | Qué hizo en local | Por qué se necesita al desarrollador |
| :--- | :---------------- | :----------------------------------- |
| Medición de arranque | Preparó los comandos | La medición «antes» se pidió antes de editar código; se repite igual después |
| Verificación en la réplica | `test pedidos` (5 pruebas en `OK`), `check` y `makemigrations --check` | Revisar el PDF y el botón en el navegador con datos de la réplica |
| Despliegue y conteos | Preparó los pasos | Etiquetas, `push`, PythonAnywhere y sus registros los maneja solo el desarrollador |

---

## Parte A · Mediciones y verificación local

Todo en **[PC · PowerShell 7]**, desde la raíz del repositorio, con `.venv` activo y `docker compose up -d`.

### A1. Medición «antes» (entregada el 2026-10-23, sobre el código de `v0.1-higiene`)

| Corrida | Importar `pedidos.urls` |
| :------ | ----------------------: |
| 1 | 1.723,9 ms |
| 2 | 690,6 ms |
| 3 | 672,4 ms |
| Media | 1.029,0 ms (681,5 ms sin la primera, en frío de disco) |

`'weasyprint' in sys.modules` después de importar `pedidos.views`: `True`.

> El número de corrida no salió en la impresión (`corrida  :`). El orden es el de ejecución. Los comandos de A2 pasan el número como argumento.

### A2. Medición «después» (mismo procedimiento, con los cambios de la 00-06)

```powershell
$env:DB_NAME = 'manzagrafica_replica'
$env:DJANGO_SETTINGS_MODULE = 'PedidosApp.settings'
foreach ($i in 1..3) {
  python -c "import sys, time, django; django.setup(); t=time.perf_counter(); import pedidos.urls; print(f'corrida {sys.argv[1]}: {(time.perf_counter()-t)*1000:.1f} ms')" $i
}
python -c "import sys, django; django.setup(); import pedidos.views; print('weasyprint' in sys.modules)"
```

**Esperado:** tres tiempos claramente menores que los de A1 y `False`.

| Corrida | Importar `pedidos.urls` |
| :------ | ----------------------: |
| 1 | 40,6 ms |
| 2 | 22,4 ms |
| 3 | 16,0 ms |
| Media | 26,3 ms (frente a 1.029,0 ms antes: unas 39 veces más rápido; 681,5 ms sin la primera corrida, unas 26 veces) |

`'weasyprint' in sys.modules`: `False`

### A3. Pruebas y revisiones

```powershell
python manage.py test pedidos
python manage.py check
python manage.py makemigrations --check --dry-run
```

**Esperado:** `Ran 6 tests` y `OK` (5 en la primera revisión; la sexta, HEAD de `robots.txt`, se agregó con `require_safe`) (puede aparecer la advertencia `mysql.W002`, modo estricto; existía antes y no viene de esta iteración); `System check identified no issues (0 silenced).`; `No changes detected`.

**Resultado (desarrollador):** `Ran 5 tests` y `OK` (con la advertencia `mysql.W002`, como se esperaba); `check` sin problemas; `makemigrations`: `No changes detected`.

### A4. Servidor local y sesión

En una terminal aparte:

```powershell
$env:DB_NAME = 'manzagrafica_replica'
python manage.py runserver
```

En la terminal de trabajo:

```powershell
$base = 'http://127.0.0.1:8000'
$s = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$login = Invoke-WebRequest "$base/accounts/login/" -WebSession $s
$csrf = ($s.Cookies.GetCookies($base) | Where-Object Name -eq 'csrftoken').Value
$cred = Get-Credential -Message 'Usuario de la réplica'
$r = Invoke-WebRequest "$base/accounts/login/" -Method Post -WebSession $s `
  -Headers @{ Referer = "$base/accounts/login/" } `
  -Body @{ csrfmiddlewaretoken = $csrf; username = $cred.UserName; password = $cred.GetNetworkCredential().Password; next = '/' }
$r.BaseResponse.RequestMessage.RequestUri.AbsolutePath
($s.Cookies.GetCookies($base) | Where-Object Name -eq 'sessionid').Count
```

**Esperado:** `/` (el `302` del acceso llevó al panel) y `1` (hay cookie de sesión). Si sale `/accounts/login/` y `0`, el usuario o la contraseña no son válidos. El `302` también se ve en la terminal de `runserver`: `"POST /accounts/login/ HTTP/1.1" 302`.

> Corregido el 2026-10-23: en PowerShell 7.6, `-MaximumRedirection 0` lanza un error en lugar de devolver la respuesta. Ahora se sigue la redirección y se comprueba el destino final.

**Resultado (desarrollador):** en PowerShell 7.6, `-MaximumRedirection 0` lanza el error «Se ha superado el número máximo de redireccionamientos» en lugar de devolver la respuesta (no es un fallo de la app). La prueba se dio por buena con el registro del servidor, que muestra `POST /accounts/login/ 302`, y con las cookies `csrftoken` y `sessionid` presentes tras el intento.

### A5. PDF de una cotización

```powershell
$pk = (python manage.py shell -c "from pedidos.models import Cotizacion; print(Cotizacion.objects.order_by('-pk').values_list('pk', flat=True).first())" | Select-Object -Last 1).Trim()
$r = Invoke-WebRequest "$base/cotizaciones/$pk/pdf/" -WebSession $s
$r.StatusCode; $r.Headers['Content-Type']; [System.Text.Encoding]::ASCII.GetString($r.RawContentStream.ToArray()[0..3])
```

**Esperado:** `200`, `application/pdf`, `%PDF`. Es la primera vez que se importa WeasyPrint en ese proceso: tarda algo más que el resto de las páginas.

**Resultado (desarrollador):** cotización `5`: `200`, `application/pdf`, `%PDF`. La importación diferida de WeasyPrint no rompe la exportación. En el primer intento, `$pk` capturó también la línea «objects imported automatically» y dio 404; se corrigió con `| Select-Object -Last 1` y `.Trim()`.

### A6. `robots.txt` sin sesión

```powershell
$r = Invoke-WebRequest "$base/robots.txt" -SkipHttpErrorCheck
$r.StatusCode; $r.Headers['Content-Type']; $r.Content
(Invoke-WebRequest "$base/robots.txt" -Method Head -SkipHttpErrorCheck).StatusCode
(Invoke-WebRequest "$base/robots.txt" -Method Post -SkipHttpErrorCheck).StatusCode
```

**Esperado:** `200`, `text/plain; charset=utf-8`, el texto `User-agent: *` y `Disallow: /`; `200` para HEAD; `403` para el POST, porque el middleware CSRF responde antes que la vista. El `405` solo se ve en las pruebas, porque el cliente de pruebas no exige CSRF. Sin `-WebSession`: es una petición sin sesión.

**Resultado (desarrollador):** `200`, `text/plain; charset=utf-8`, `User-agent: *` y `Disallow: /`. El POST dio `403`, no `405`: el middleware CSRF responde antes de que la vista compruebe el método. Es aceptable; el `405` aplica solo al cliente de pruebas.

### A7. Lista de pagos

```powershell
(Invoke-WebRequest "$base/pagos/lista/" -WebSession $s).StatusCode
$sid = ($s.Cookies.GetCookies($base) | Where-Object Name -eq 'sessionid').Value
curl.exe -s -o NUL -w "%{http_code} %{redirect_url}`n" -b "sessionid=$sid" "$base/pagos/lista"
```

`curl.exe` viene con Windows 10 y no sigue redirecciones por defecto: muestra el código y el destino sin el error de `-MaximumRedirection 0`. Corregido el 2026-10-23.

**Esperado:** `200`; después `301 http://127.0.0.1:8000/pagos/lista/`.

**Resultado (desarrollador):** `/pagos/lista/` dio `200` (59.982 bytes). `/pagos/lista` redirigió con `301` a `/pagos/lista/`, según la salida y el registro del servidor (misma peculiaridad de `-MaximumRedirection 0` de A4).

### A8. Botón de acceso (navegador)

Cierra la sesión o usa una ventana privada en `http://127.0.0.1:8000/accounts/login/`. Revisa en escritorio y con las herramientas de desarrollo en un ancho de 360 px:

1. Ingresa una contraseña incorrecta y presiona **Ingresar al Sistema** → el botón cambia a **Ingresando…** con un ícono que gira y queda deshabilitado; un segundo clic no hace nada.
2. La página vuelve con «Credenciales incorrectas» → el botón está habilitado y dice **Ingresar al Sistema**.
3. Ingresa bien, entra al panel y presiona **atrás** en el navegador → el botón de acceso está habilitado.
4. A 360 px: el texto del botón cabe en una línea y no hay desplazamiento horizontal.
5. Con el teclado (Tab) el botón muestra su foco.

| Revisión | Escritorio | 360 px |
| :------- | :--------- | :----- |
| Deshabilitado al primer envío | Sí | Sí |
| Habilitado tras error | Sí | Sí |
| Habilitado con «atrás» | Sí (Firefox) | Sí (Firefox) |
| Sin desborde | Sí | Sí |
| Foco visible | Sí | Sí |

**Notas del desarrollador:** la prueba completa se repitió en Firefox. En Chrome, el botón «atrás» tras un intento fallido muestra «Confirmar reenvío del formulario» (`ERR_CACHE_MISS`): es una limitación del navegador, porque esa entrada del historial es la respuesta a un POST, y no un fallo de la app. Por separado se observó que, al volver con «atrás» después de iniciar sesión, aparece el formulario de acceso vacío: Django no redirige al panel a quien ya tiene sesión. Queda anotado como pendiente de baja prioridad (`redirect_authenticated_user=True`), propuesto para la Épica 04.

Al terminar, detén `runserver` con Ctrl+C.

---

## Parte B · Despliegue como `v0.2-correcciones`

> **Antes de empezar:** la parte A se revisó el 2026-10-23 y cumple. Después de esa revisión, `robots_txt` pasó de `require_GET` a `require_safe`. Repite A3 (esperado: `Ran 6 tests`, `OK`) y la línea HEAD de A6 (esperado: `200`). Despliega el commit que incluye ese cambio.

Sigue `docs/operacion/despliegue.md`. Lo propio de este despliegue:

- **Etiqueta:** `v0.2-correcciones` (fase 0, correlativo 2). **Partida y destino de retroceso:** `v0.1-higiene`.
- **Respaldo previo:** no aplica (no toca datos ni esquema, y no es el primer despliegue de la fase).
- **Sin migraciones, sin cambios en `requirements.txt` ni en `pedidos/static`**: los pasos 3.3, 3.4 y 3.5 deben salir vacíos.

### B1. Lista de comprobación **[PC · PowerShell 7]**

Después del commit y del `git push` de `main`:

```powershell
git status --short
$env:DEBUG = "False"; python manage.py check --deploy; Remove-Item Env:DEBUG
python manage.py makemigrations --check --dry-run
git tag -a v0.2-correcciones -m "Iteración 00-06 · desplegada el <AAAA-MM-DD>"
git push origin v0.2-correcciones
git ls-remote --tags origin v0.2-correcciones
```

| # | Comprobación | Resultado |
| :- | :----------- | :-------- |
| 1 | Pruebas en verde | `Ran 6 tests`, `OK` (repetir A3 tras `require_safe`) | Cumple: `Ran 6 tests`, `OK`; HEAD de `robots.txt` = 200 |
| 2 | `check --deploy`: solo W004, W008, W009, W012, W016 | Cumple: esas cinco, 5 issues |
| 3 | `No changes detected` | Cumple |
| 4 | Migraciones nuevas | Ninguna |
| 5 | Respaldo | No aplica |
| 6 | Estilos compilados | No aplica |
| 7 | `ls-remote` devuelve una línea | Cumple (`refs/tags/v0.2-correcciones`, commit `7944943`) |
| 8 | Solo despliegue de 00-06 | Cumple: de `v0.1-higiene` a `v0.2-correcciones`, sin otros cambios |

### B2. Servidor **[PA · Bash]**

```bash
PROYECTO="<mismo valor que en linea_base.sh>"
VENV="<mismo valor que en linea_base.sh>"
test -f "$PROYECTO/manage.py" && test -x "$VENV/bin/python" && echo "PROYECTO y VENV correctos"
cd "$PROYECTO"; source "$VENV/bin/activate"
git status --short
git describe --tags --always
```

**Esperado:** `PROYECTO y VENV correctos`, `git status` vacío y `v0.1-higiene` (el servidor está en `detached HEAD`; no uses `git pull`).

```bash
git fetch origin --tags
git checkout v0.2-correcciones
git describe --tags
git diff --stat v0.1-higiene v0.2-correcciones -- requirements.txt pedidos/static pedidos/migrations
python manage.py migrate --plan
```

**Esperado:** `v0.2-correcciones`; el `diff` sin salida; `No planned migration operations.`

**[PA · Panel]** Pestaña **Web** → **Reload**. Hora de la recarga (Chile): **2026-10-23, 18:35** (21:35 UTC)

**Resultado (desarrollador):** el servidor estaba en `v0.1-higiene` y limpio; `fetch --tags` trajo `v0.2-correcciones`; `checkout` dejó el servidor en el commit `7944943`; el `diff` de `requirements.txt`, `pedidos/static` y `pedidos/migrations` salió vacío; `migrate --plan`: `No planned migration operations` (con la advertencia conocida `mysql.W002`).

**Incidente de etiqueta (resuelto antes del despliegue):** la etiqueta se creó primero con el texto de relleno `<AAAA-MM-DD>` en su mensaje. Como ningún servidor la había descargado, se eliminó (local y remota) y se recreó apuntando al mismo commit, con el mensaje «Iteración 00-06 · etiquetada el 2026-10-23». Lección: una etiqueta se crea solo con el mensaje final y después de la revisión.

### B3. Verificación después

Ventana privada:

1. `https://manzagrafica.pythonanywhere.com/robots.txt` → `User-agent: *` y `Disallow: /`, sin pedir sesión. Opcional **[PC · PowerShell 7]**: `curl.exe -sI https://manzagrafica.pythonanywhere.com/robots.txt` → `HTTP/1.1 200 OK` y `Content-Type: text/plain; charset=utf-8`.
2. Inicio de sesión → el botón muestra **Ingresando…** y entra al panel.
3. Panel, listado de pedidos y detalle de un pedido (`despliegue.md`, 3.7).
4. Menú **Pagos** → abre `/pagos/lista/`.
5. Una cotización → **PDF** → se abre el documento.

Registro de errores (`despliegue.md`, 3.7). Anota solo tipo y hora de lo que aparezca después de la recarga.

| Revisión | Resultado |
| :------- | :-------- |
| `robots.txt` | OK: texto directo sin pedir sesión. `curl.exe -sI`: `HTTP/1.1 200 OK` y `Content-Type: text/plain; charset=utf-8` |
| Acceso | OK: se vio «Ingresando…» con el ícono girando y luego el panel |
| Panel, pedidos, detalle | OK |
| Pagos | OK: lista y detalle |
| PDF | OK: se generó y se descargó sin problemas (WeasyPrint importado en producción) |
| Errores después de la recarga | Una sola línea nueva, a las 21:47:11 UTC: `Not Found: /favicon.ico` (la solicita el navegador solo; nuevo hallazgo menor, la app no define favicon). Sin `Traceback`, sin `ImportError`, sin 500. El último `Not Found: /robots.txt` es del 2026-10-22 22:51 UTC, antes del despliegue |

Producción quedó en `v0.2-correcciones`. Retroceso no necesario.

Si algo falla: `docs/operacion/retroceso.md`, caso 1, con destino `v0.1-higiene`.

---

## Parte C · Conteo por fecha después del despliegue

Método reutilizable de `evidencia-00-01.md` (lee todos los archivos, planos y `.gz`, y cuenta por la fecha de cada línea, en UTC). **[PA · Bash]**:

```bash
cd /var/log; D=manzagrafica.pythonanywhere.com
for i in 6 5 4 3 2 1 0; do d=$(date -u -d "-$i day" +%F); printf "%s broken_pipe=%s sigpipe=%s\n" "$d" "$(zcat -f $D.server.log* | grep "^$d" | grep -c 'Broken pipe')" "$(zcat -f $D.server.log* | grep "^$d" | grep -c 'SIGPIPE')"; done
for i in 6 5 4 3 2 1 0; do d=$(LC_ALL=C date -u -d "-$i day" +%d/%b/%Y); printf "%s robots=%s robots_404=%s\n" "$d" "$(zcat -f $D.access.log* | grep 'GET /robots.txt' | grep -c "$d")" "$(zcat -f $D.access.log* | grep 'GET /robots.txt' | grep "$d" | grep -c '" 404 ')"; done
```

Solo imprime fechas y conteos. Si el CPU del día está justo, ejecútalo al día siguiente.

### C1. Primer pedido: uno o dos días después del despliegue

Pega la salida tal cual. Los días posteriores a la recarga deben tener `robots_404=0` (y `robots` mayor que 0 si Googlebot pasó). El día de la recarga puede mezclar 404 de antes y 200 de después.

| Fecha UTC | `robots` | `robots_404` | `broken_pipe` | `sigpipe` |
| :-------- | -------: | -----------: | ------------: | --------: |
| | | | | |

**Línea base (2026-10-15 a 2026-10-21):** 7 404 de `/robots.txt` en 7 días; 4 `Broken pipe` en 7 días (0,44 por día en 89 días).

### C2. Segundo pedido: 28 días después del despliegue

Mismo bloque, con `seq 27 -1 0` en lugar de `6 5 4 3 2 1 0` en el primer `for`. Se informa la tasa diaria de `Broken pipe` frente a 0,44 por día, **sin umbral** y sin bloquear la Épica 01.

| Ventana | Días | `Broken pipe` | Por día |
| :------ | ---: | ------------: | ------: |
| | 28 | | |