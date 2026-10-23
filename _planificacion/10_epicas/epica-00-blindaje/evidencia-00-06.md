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
| 1 | |
| 2 | |
| 3 | |
| Media | |

`'weasyprint' in sys.modules`: ____

### A3. Pruebas y revisiones

```powershell
python manage.py test pedidos
python manage.py check
python manage.py makemigrations --check --dry-run
```

**Esperado:** `Ran 5 tests` y `OK` (puede aparecer la advertencia `mysql.W002`, modo estricto; existía antes y no viene de esta iteración); `System check identified no issues (0 silenced).`; `No changes detected`.

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
$r = Invoke-WebRequest "$base/accounts/login/" -Method Post -WebSession $s -MaximumRedirection 0 -SkipHttpErrorCheck `
  -Headers @{ Referer = "$base/accounts/login/" } `
  -Body @{ csrfmiddlewaretoken = $csrf; username = $cred.UserName; password = $cred.GetNetworkCredential().Password; next = '/' }
$r.StatusCode; $r.Headers.Location
```

**Esperado:** `302` y `/`. Si sale `200`, el usuario o la contraseña no son válidos.

### A5. PDF de una cotización

```powershell
$pk = python manage.py shell -c "from pedidos.models import Cotizacion; print(Cotizacion.objects.order_by('-pk').values_list('pk', flat=True).first())"
$r = Invoke-WebRequest "$base/cotizaciones/$pk/pdf/" -WebSession $s
$r.StatusCode; $r.Headers['Content-Type']; [System.Text.Encoding]::ASCII.GetString($r.RawContentStream.ToArray()[0..3])
```

**Esperado:** `200`, `application/pdf`, `%PDF`. Es la primera vez que se importa WeasyPrint en ese proceso: tarda algo más que el resto de las páginas.

### A6. `robots.txt` sin sesión

```powershell
$r = Invoke-WebRequest "$base/robots.txt" -SkipHttpErrorCheck
$r.StatusCode; $r.Headers['Content-Type']; $r.Content
(Invoke-WebRequest "$base/robots.txt" -Method Post -SkipHttpErrorCheck).StatusCode
```

**Esperado:** `200`, `text/plain; charset=utf-8`, el texto `User-agent: *` y `Disallow: /`, y `405` para el POST. Sin `-WebSession`: es una petición sin sesión.

### A7. Lista de pagos

```powershell
(Invoke-WebRequest "$base/pagos/lista/" -WebSession $s).StatusCode
$r = Invoke-WebRequest "$base/pagos/lista" -WebSession $s -MaximumRedirection 0 -SkipHttpErrorCheck
$r.StatusCode; $r.Headers.Location
```

**Esperado:** `200`; después `301` y `/pagos/lista/`.

### A8. Botón de acceso (navegador)

Cierra la sesión o usa una ventana privada en `http://127.0.0.1:8000/accounts/login/`. Revisa en escritorio y con las herramientas de desarrollo en un ancho de 360 px:

1. Ingresa una contraseña incorrecta y presiona **Ingresar al Sistema** → el botón cambia a **Ingresando…** con un ícono que gira y queda deshabilitado; un segundo clic no hace nada.
2. La página vuelve con «Credenciales incorrectas» → el botón está habilitado y dice **Ingresar al Sistema**.
3. Ingresa bien, entra al panel y presiona **atrás** en el navegador → el botón de acceso está habilitado.
4. A 360 px: el texto del botón cabe en una línea y no hay desplazamiento horizontal.
5. Con el teclado (Tab) el botón muestra su foco.

| Revisión | Escritorio | 360 px |
| :------- | :--------- | :----- |
| Deshabilitado al primer envío | | |
| Habilitado tras error | | |
| Habilitado con «atrás» | | |
| Sin desborde | | |
| Foco visible | | |

Al terminar, detén `runserver` con Ctrl+C.

---

## Parte B · Despliegue como `v0.2-correcciones`

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
| 1 | Pruebas en verde | (A3) |
| 2 | `check --deploy`: solo W004, W008, W009, W012, W016 | |
| 3 | `No changes detected` | |
| 4 | Migraciones nuevas | Ninguna |
| 5 | Respaldo | No aplica |
| 6 | Estilos compilados | No aplica |
| 7 | `ls-remote` devuelve una línea | |
| 8 | Solo despliegue de 00-06 | |

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

**[PA · Panel]** Pestaña **Web** → **Reload**. Hora de la recarga (Chile): ____

### B3. Verificación después

Ventana privada:

1. `https://manzagrafica.pythonanywhere.com/robots.txt` → `User-agent: *` y `Disallow: /`, sin pedir sesión.
2. Inicio de sesión → el botón muestra **Ingresando…** y entra al panel.
3. Panel, listado de pedidos y detalle de un pedido (`despliegue.md`, 3.7).
4. Menú **Pagos** → abre `/pagos/lista/`.
5. Una cotización → **PDF** → se abre el documento.

Registro de errores (`despliegue.md`, 3.7). Anota solo tipo y hora de lo que aparezca después de la recarga.

| Revisión | Resultado |
| :------- | :-------- |
| `robots.txt` | |
| Acceso | |
| Panel, pedidos, detalle | |
| Pagos | |
| PDF | |
| Errores después de la recarga | |

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
