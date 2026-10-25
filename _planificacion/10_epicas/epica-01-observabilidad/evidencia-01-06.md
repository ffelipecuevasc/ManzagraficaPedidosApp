# Evidencia 01-06 · Despliegue y validación de la observabilidad

- **Fecha del pedido:** 2026-10-25
- **Pedido por:** Claude Code (Opus 5.5)
- **Iteración:** [01-06](iteracion-01-06-despliegue-validacion.md). Etiqueta `v1.1-observabilidad`; partida y destino de retroceso `v0.2-correcciones`.
- **Criterios que dependen de esta evidencia:** todos los de la 01-06.

> Este archivo existe porque el agente no puede tocar producción, crear etiquetas ni abrir respaldos. Responde solo lo que se pide, sin datos de clientes: conteos, horas, tipos de error y códigos.
>
> **Orden:** parte A (tu PC: comprobación, respaldo y ensayo en la réplica) → el agente revisa la parte A → parte B (despliegue) → parte C (validación, el mismo día) → parte D (siete días después).
>
> **Terminales** (`docs/operacion/despliegue.md`, sección 0): **[PC · PowerShell 7]** en la raíz del repositorio con `.venv` activo; **[PA · Bash]** consola Bash de PythonAnywhere; **[PA · Panel]** panel web; **[Navegador]**.
>
> **Horas:** `error.log` y `access.log` están en **UTC** y PythonAnywhere antepone su fecha a cada línea de `error.log`; `server.log` está en **hora de Chile**. En octubre, Chile continental es UTC-3.

## Particularidades ya conocidas (aplicadas en los comandos)

- `python manage.py shell -c` imprime una línea extra («N objects imported automatically»): se toma solo la última con `| Select-Object -Last 1` (PowerShell) o `| tail -n 1` (Bash).
- En PowerShell 7.6, `Invoke-WebRequest -MaximumRedirection 0` lanza un error en vez de devolver la respuesta: para ver redirecciones se usa `curl.exe`.
- La restauración en la réplica va dentro de `cmd /c` para que PowerShell no cambie la codificación del volcado (`replica-local.md`, sección 5).
- El mensaje de la etiqueta se calcula con la fecha del día al crearla; no se escribe a mano ni con relleno (incidente de 00-06).
- «Generar Nuevo Respaldo BD» es un enlace GET: cada visita crea un volcado y desplaza al más antiguo. Un solo clic.

---

## Parte A · En tu PC, antes de tocar el servidor

### A1. Lista de comprobación **[PC · PowerShell 7]**

Con `main` ya con commit y `push`, y `docker compose up -d`:

```powershell
git status --short
$env:DB_NAME = 'manzagrafica_replica'
python manage.py test pedidos
$env:DEBUG = 'False'; python manage.py check --deploy; Remove-Item Env:DEBUG
python manage.py makemigrations --check --dry-run
python manage.py sqlmigrate pedidos 0007
python manage.py test pedidos.tests.test_errores.ErroresSinMiddlewareTests.test_regresion_eliminar_pago_deja_tipo_y_traza
```

**Esperado:**

- `git status` vacío.
- `Ran 72 tests` y `OK` (puede salir la advertencia `mysql.W002`, esperada).
- `check --deploy`: solo `W004`, `W008`, `W009`, `W012` y `W016`.
- `No changes detected`.
- El SQL de la 0007 idéntico al de `bitacora-01-06.md`: un `CREATE TABLE`, un `ALTER TABLE … ADD CONSTRAINT … FOREIGN KEY` sobre `pedidos_registroevento` y dos `CREATE INDEX`. Pega el SQL completo.
- La prueba de regresión de eliminar pago en `OK`: el caso del error controlado sigue existiendo en el código que se despliega.

| # | Comprobación | Resultado |
| :- | :----------- | :-------- |
| 1 | Pruebas (`Ran N tests`, `OK`) | |
| 2 | `check --deploy` (códigos) | |
| 3 | `makemigrations --check` | |
| 4 | `sqlmigrate 0007` igual a la bitácora; Clase 2 | |
| 5 | Respaldo verificado (A2) | |
| 6 | Estilos compilados | No aplica |
| 7 | Etiqueta publicada (A5) | |
| 8 | Solo la Épica 01 (más el bloque de pruebas de 02-01) | |

### A2. Respaldo previo **[Navegador]** y **[PC · PowerShell 7]**

1. En producción, como superusuario: «Respaldar BD» → **un solo clic** en «Generar Nuevo Respaldo BD». Guarda la descarga directo en la carpeta cifrada.
2. Verifica:

```powershell
python scripts\verificar_respaldo.py "<ruta del volcado en la carpeta cifrada>"
$LASTEXITCODE
```

**Esperado:** `Tablas esperadas encontradas: 18 de 18`, `Tablas adicionales …: ninguna` (todavía no existe `pedidos_registroevento` en producción) y `Resultado: VÁLIDO`, código `0`.

| Dato | Valor |
| :--- | :---- |
| Nombre del archivo (hora de Chile del nombre) | |
| Tamaño (bytes) | |
| SHA-256 | |
| Tablas | |
| Código | |

Agrega la fila en `docs/operacion/respaldo.md`, sección 6 (motivo: «Previo al despliegue `v1.1-observabilidad` (iteración 01-06)»).

### A3. Ensayo de retroceso por restauración en la réplica **[PC · PowerShell 7]**

Refresca la réplica con el respaldo de A2 (`replica-local.md`, sección 9). Revisa dos veces el nombre de la base: **solo `manzagrafica_replica`**.

```powershell
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE manzagrafica_replica; CREATE DATABASE manzagrafica_replica CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
$t = Measure-Command { cmd /c "docker compose exec -T db sh -c ""exec mysql -uroot -p`$MYSQL_ROOT_PASSWORD manzagrafica_replica"" < ""<ruta del volcado de A2>""" }
"Código: $LASTEXITCODE · Segundos: $([math]::Round($t.TotalSeconds, 1))"
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "SELECT COUNT(*) AS tablas FROM information_schema.tables WHERE table_schema = ''manzagrafica_replica'';"'
$env:DB_NAME = 'manzagrafica_replica'
python manage.py showmigrations pedidos | Select-Object -Last 2
python manage.py shell -c "from django.db import connection; print('pedidos_registroevento' in connection.introspection.table_names())" | Select-Object -Last 1
```

**Esperado:** código `0`, `tablas = 18`, la última migración aplicada es `[X] 0006_…` con `[ ] 0007_registroevento` debajo, y `False` (la tabla de eventos no existe todavía). Los 8 eventos de la revisión de 01-05 desaparecen: es esperado.

| Dato | Valor |
| :--- | :---- |
| Código y segundos de la restauración | |
| Tablas | |
| Últimas migraciones | |
| ¿Existe `pedidos_registroevento`? | |

Anota el refresco en la tabla de `replica-local.md`, sección 9.

### A4. Ensayo de la migración y de su reversión **[PC · PowerShell 7]**

```powershell
$env:DB_NAME = 'manzagrafica_replica'
$t = Measure-Command { python manage.py migrate pedidos 0007 | Out-Host }; "Aplicar: $([math]::Round($t.TotalSeconds, 2)) s"
python manage.py migrate pedidos 0006 --plan
$t = Measure-Command { python manage.py migrate pedidos 0006 | Out-Host }; "Revertir: $([math]::Round($t.TotalSeconds, 2)) s"
python manage.py shell -c "from django.db import connection; print('pedidos_registroevento' in connection.introspection.table_names())" | Select-Object -Last 1
$t = Measure-Command { python manage.py migrate pedidos 0007 | Out-Host }; "Aplicar de nuevo: $([math]::Round($t.TotalSeconds, 2)) s"
python manage.py showmigrations pedidos | Select-Object -Last 2
```

**Esperado:**

- `Applying pedidos.0007_registroevento... OK`.
- El plan de reversión lista solo `Undo Create model RegistroEvento`.
- `Unapplying pedidos.0007_registroevento... OK` y `False` (la tabla desapareció).
- De nuevo `Applying … OK`; queda `[X] 0007_registroevento`.

Es el caso 2 de `retroceso.md`. En producción no se revierte salvo que la tabla estorbe: basta con el caso 1 (volver el código).

| Paso | Resultado | Segundos |
| :--- | :-------- | :------- |
| Aplicar 0007 | | |
| Plan de reversión | | — |
| Revertir a 0006 (tabla existe: `False`) | | |
| Aplicar de nuevo | | |

### A5. Pruebas con la réplica restaurada y etiqueta **[PC · PowerShell 7]**

```powershell
python manage.py test pedidos
python manage.py check
```

Si todo cumple y el agente revisó la parte A, crea la etiqueta **el día del despliegue** (decisión abierta: ventana). El mensaje toma la fecha del día:

```powershell
git status --short
$fecha = Get-Date -Format 'yyyy-MM-dd'
git tag -a v1.1-observabilidad -m "Épica 01 · iteraciones 01-01 a 01-05 (y bloque de pruebas de 02-01) · desplegada el $fecha"
git tag -n v1.1-observabilidad
git push origin v1.1-observabilidad
git ls-remote --tags origin v1.1-observabilidad
```

**Esperado:** `git tag -n` muestra el mensaje con la fecha real (revísalo **antes** del `push`; si está mal, `git tag -d v1.1-observabilidad` y créala de nuevo, porque todavía no está publicada), y `ls-remote` devuelve una línea.

| Dato | Valor |
| :--- | :---- |
| Pruebas y `check` | |
| Mensaje de la etiqueta | |
| Commit de la etiqueta | |

---

## Parte B · Despliegue en PythonAnywhere

### B1. Ubicarse **[PA · Bash]**

```bash
PROYECTO="/home/manzagrafica/ManzagraficaPedidosApp"
VENV="/home/manzagrafica/ManzagraficaPedidosApp/venv"
test -f "$PROYECTO/manage.py" && test -x "$VENV/bin/python" && echo "PROYECTO y VENV correctos"
cd "$PROYECTO"; source "$VENV/bin/activate"
git status --short
git describe --tags --always
```

**Esperado:** `PROYECTO y VENV correctos`; `git status` vacío (o solo `?? media/…` y `?? staticfiles/`); `v0.2-correcciones`.

### B2. Prueba de que la 0007 no se aplicó antes de tiempo **[PA · Bash]**

Todavía en `v0.2-correcciones`, antes del `fetch`:

```bash
python manage.py showmigrations pedidos | tail -n 2
python manage.py shell -c "from django.db import connection; print('tabla_eventos:', 'pedidos_registroevento' in connection.introspection.table_names())" | tail -n 1
python manage.py migrate --plan
python manage.py check --deploy 2>&1 | grep -oE '[a-z_]+\.[EW][0-9]{3}' | sort -u | tr '\n' ' '; echo
```

**Esperado:**

- Las dos últimas líneas son `[X] 0005_…` y `[X] 0006_…`, sin `0007`.
- `tabla_eventos: False`.
- `No planned migration operations.`
- La lista de códigos de `check --deploy` de producción **antes** del cambio (anótala para compararla en B4).

| Dato | Valor |
| :--- | :---- |
| Últimas migraciones | |
| `tabla_eventos` | |
| `migrate --plan` | |
| `check --deploy` antes (códigos) | |

### B3. Traer la etiqueta **[PA · Bash]**

```bash
git fetch origin --tags
git checkout v1.1-observabilidad
git describe --tags
git diff --stat v0.2-correcciones v1.1-observabilidad -- requirements.txt pedidos/static
git diff --stat v0.2-correcciones v1.1-observabilidad -- pedidos/migrations
```

**Esperado:**

- `v1.1-observabilidad` (en `detached HEAD`, como siempre).
- El primer `diff` sin salida: no hay que instalar dependencias ni ejecutar `collectstatic`.
- El segundo `diff` muestra solo `pedidos/migrations/0007_registroevento.py`.

### B4. Migración y configuración **[PA · Bash]**

```bash
python manage.py migrate --plan
python manage.py check --deploy 2>&1 | grep -oE '[a-z_]+\.[EW][0-9]{3}' | sort -u | tr '\n' ' '; echo
python manage.py check --deploy 2>&1 | grep -c 'ERRORS'
time python manage.py migrate
python manage.py showmigrations pedidos | tail -n 2
```

**Esperado:**

- `migrate --plan` lista **solo** `pedidos.0007_registroevento` (`Create model RegistroEvento`). Si lista otra cosa, detente.
- La lista de códigos es igual a la de B2 y el conteo de `ERRORS` es `0`: el bloque de pruebas de 02-01 no rompe la configuración de producción (tarea 5).
- `Applying pedidos.0007_registroevento... OK` y `[X] 0007_registroevento`.

Si `migrate` falla, detente y sigue `retroceso.md`, caso 2.

| Dato | Valor |
| :--- | :---- |
| `migrate --plan` | |
| `check --deploy` después (códigos) y `ERRORS` | |
| Duración de `migrate` (`real`) | |
| Últimas migraciones | |

### B5. Antes de recargar: el caso del error controlado sigue existiendo **[PA · Bash]**

```bash
test -f pedidos/templates/pedidos/pago_confirm_delete.html && echo "plantilla EXISTE: detente" || echo "plantilla falta: el caso sigue"
python manage.py shell -c "from pedidos.models import Pago; print('pago_id:', 1056 if Pago.objects.filter(pk=1056).exists() else Pago.objects.order_by('-pk').values_list('pk', flat=True).first())" | tail -n 1
python manage.py shell -c "from pedidos.models import RegistroEvento as R; print('eventos:', R.objects.count())" | tail -n 1
date -u "+%F %T"
```

**Esperado:**

- `plantilla falta: el caso sigue` (si dice que existe, AUD-02-002 ya no sirve como error controlado: detente y avisa).
- `pago_id: 1056`, o el `id` del último pago si el 1056 ya no existe. Ese es el `ID` que usas en C1.
- `eventos: 0`.
- La hora UTC antes de la recarga.

### B6. Recargar **[PA · Panel]**

Pestaña **Web** → **Reload manzagrafica.pythonanywhere.com**. Anota la hora de la recarga en Chile y en UTC.

En la consola Bash, guarda la hora UTC de la recarga para los conteos (formato exacto `AAAA-MM-DD HH:MM:SS`, la de tu anotación):

```bash
DESDE="<AAAA-MM-DD HH:MM:SS de la recarga, en UTC>"
L=/var/log/manzagrafica.pythonanywhere.com.error.log
echo "$DESDE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE válido"
```

**Esperado:** `DESDE válido`. Esta es la única línea que se completa a mano. Si la consola se cierra, define `DESDE` y `L` otra vez.

> Los filtros `awk 'substr($0,1,19) >= d'` de las partes C y D suponen que cada línea de `error.log` empieza con la fecha `AAAA-MM-DD HH:MM:SS` que antepone PythonAnywhere. No se pudieron probar contra el archivo real. Si en C2 no aparece nada, pega la salida de `tail -n 2 $L | cut -c1-40` y el agente ajusta el filtro.

### B7. Verificar después **[Navegador]**

Ventana privada: inicio de sesión, panel, listado de pedidos y detalle de un pedido (`despliegue.md`, paso 3.7). No uses «Estadísticas» (AUD-01-006).

| Revisión | Resultado |
| :------- | :-------- |
| Hora de la recarga (Chile / UTC) | |
| Acceso y panel | |
| Listado y detalle de pedido | |

Si algo responde 500 en estas pantallas, sigue `retroceso.md`, caso 1, con destino `v0.2-correcciones` (la tabla nueva puede quedarse: el código anterior la ignora).

---

## Parte C · Validación (el mismo día)

### C1. Error controlado y página 500 **[Navegador]**

1. Con la sesión iniciada, anota la hora de tu reloj y abre **una sola vez** `https://manzagrafica.pythonanywhere.com/pagos/eliminar/<ID de B5>/`. Solo se abre: no hay nada que confirmar, porque la página falla antes de mostrarse.
2. **Página 500** (tarea 7): debe decir «Algo salió mal», sin «500», sin la broma de los correos y sin detalles técnicos. Recorre con Tab: «Recargar» e «Ir al inicio» muestran su foco. Repite a 360 px (modo dispositivo del navegador).
3. Pon en marcha un cronómetro y pasa a C2: el tiempo de diagnóstico cuenta desde aquí hasta tener la línea con todo el contexto.

| Dato | Valor |
| :--- | :---- |
| Hora de la petición (Chile) | |
| Página 500 en escritorio | |
| Página 500 a 360 px | |
| Foco visible en los botones | |

### C2. Diagnóstico desde `error.log` **[PA · Bash]**

```bash
ID=<ID de B5>
awk -v d="$DESDE" 'substr($0,1,19) >= d' $L | grep "ruta=/pagos/eliminar/$ID/" | cut -c1-260
N=$(grep -n "registrador=pedidos.decorators.*ruta=/pagos/eliminar/$ID/" $L | tail -n 1 | cut -d: -f1)
sed -n "${N},$((N+60))p" $L | grep -nE 'Traceback|^[^ ]+ [^ ]+: [A-Za-z_.]+(Error|DoesNotExist|Exception)' | cut -c1-200
```

**Esperado:**

- Dos líneas para esa ruta:
  - `nivel=ERROR registrador=pedidos.decorators metodo=GET ruta=/pagos/eliminar/<ID>/ usuario=<tu id> excepcion=TemplateDoesNotExist mensaje="Error capturado por decorador en eliminar_pago"`;
  - `nivel=ERROR registrador=django.request … mensaje="Internal Server Error: /pagos/eliminar/<ID>/"`.
- Debajo de la primera, `Traceback (most recent call last):` y, al final de la traza, `django.template.exceptions.TemplateDoesNotExist: pedidos/pago_confirm_delete.html`.

Pega **solo** esas líneas (cabeceras, `Traceback` y la última línea de la traza). Detén el cronómetro.

| Dato | Valor |
| :--- | :---- |
| Cabecera del decorador (nivel, método, ruta, usuario, excepción) | |
| Hora UTC de la línea | |
| ¿Traza completa con `TemplateDoesNotExist` al final? | |
| Tiempo de diagnóstico (minutos y segundos) | |

### C3. Sin líneas duplicadas ni formato antiguo **[PA · Bash]**

```bash
awk -v d="$DESDE" 'substr($0,1,19) >= d' $L | grep -c "ruta=/pagos/eliminar/$ID/"
awk -v d="$DESDE" 'substr($0,1,19) >= d' $L | grep -v 'nivel=' | grep -c "Internal Server Error: /pagos/eliminar/$ID/"
awk -v d="$DESDE" 'substr($0,1,19) >= d' $L | grep -c 'Traceback (most recent call last)'
```

**Esperado:**

- `2`: una línea del decorador y una de `django.request`, por **una** apertura. Con `4` hay duplicación.
- `0`: no queda el formato antiguo, sin `nivel=`, que dejaba el manejador propio de PythonAnywhere.
- `1`: una sola traza.

Si los números son el doble, la hipótesis del manejador de PythonAnywhere se confirma: no hagas retroceso por esto (la información está completa); anótalo y el agente propondrá el ajuste.

| Conteo | Valor |
| :----- | :---- |
| Líneas de la ruta | |
| Formato antiguo | |
| Trazas | |

### C4. PDF sin `fontTools` y sin `django.server` **[Navegador]** y **[PA · Bash]**

1. **[Navegador]** Abre una cotización y genera su **PDF**.
2. **[PA · Bash]**:

```bash
awk -v d="$DESDE" 'substr($0,1,19) >= d' $L | grep -c 'fontTools'
awk -v d="$DESDE" 'substr($0,1,19) >= d' $L | grep -c 'registrador=django.server'
awk -v d="$DESDE" 'substr($0,1,19) >= d' $L | grep -o 'nivel=[A-Z]*' | sort | uniq -c
```

**Esperado:**

- `0` líneas de `fontTools` (antes, cientos por PDF).
- `0` de `django.server`: solo existe en `runserver`, y los accesos siguen en `access.log`.
- Por nivel, solo los `ERROR` del error controlado (2), salvo otros errores reales: en ese caso, anota solo su tipo y su hora.

| Dato | Valor |
| :--- | :---- |
| PDF generado | |
| Líneas de `fontTools` | |
| Líneas de `django.server` | |
| Líneas por nivel | |

### C5. Eventos en el admin y purga **[Navegador]** y **[PA · Bash]**

1. **[Navegador]** Abre `https://manzagrafica.pythonanywhere.com/acceso-manzagrafica-admin/pedidos/registroevento/`. Debe haber al menos un `acceso_exitoso` con tu usuario y la hora de tu inicio de sesión de B7, con `(UTC-0300)`. No debe haber un `pago_eliminado`: la página de C1 solo se abrió.
2. **[PA · Bash]**:

```bash
python manage.py purgar_registros
python manage.py shell -c "from collections import Counter; from pedidos.models import RegistroEvento as R; print(sorted(Counter(R.objects.values_list('tipo', flat=True)).items()))" | tail -n 1
grep -c 'Error capturado por decorador' "/var/log/manzagrafica.pythonanywhere.com.server.log"
```

**Esperado:**

- `Eventos eliminados: 0 (… retención de 365 días).`
- Los eventos por tipo: al menos `('acceso_exitoso', 1)`.
- El conteo de `server.log` no sube respecto de antes del despliegue: desde 01-03, esos mensajes van a `error.log` con `logging`, no a `server.log`.

| Dato | Valor |
| :--- | :---- |
| Evento en el admin (tipo, usuario, hora) | |
| ¿Hay `pago_eliminado`? | |
| Salida de `purgar_registros` | |
| Eventos por tipo | |

Agrega la fila en `docs/operacion/despliegue.md`, sección 5, con la etiqueta, el commit, el SHA-256 del respaldo (12 primeros) y el resultado.

---

## Parte D · Siete días después del despliegue

**[PA · Bash]** (define `PROYECTO`, `VENV`, `DESDE` y `L` como en B1 y B6):

```bash
cd "$PROYECTO"; source "$VENV/bin/activate"
python manage.py shell -c "
from collections import Counter
from django.db import connection
from django.utils import timezone as tz
from pedidos.models import RegistroEvento as R
qs = R.objects.all()
print('total', qs.count())
print('por_tipo', sorted(Counter(qs.values_list('tipo', flat=True)).items()))
print('por_dia_chile', sorted(Counter(tz.localtime(m).date().isoformat() for m in qs.values_list('momento', flat=True)).items()))
with connection.cursor() as c:
    c.execute(\"SELECT table_rows, data_length, index_length FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = 'pedidos_registroevento'\")
    print('information_schema', c.fetchone())
    c.execute('SELECT AVG(CHAR_LENGTH(resumen)) FROM pedidos_registroevento')
    print('resumen_promedio', c.fetchone()[0])
" | tail -n 5
zcat -f $L* | awk -v d="$DESDE" 'substr($0,1,19) >= d' | grep -o 'nivel=[A-Z]*' | sort | uniq -c
zcat -f $L* | awk -v d="$DESDE" 'substr($0,1,19) >= d' | grep -o 'registrador=[a-zA-Z_.]*' | sort | uniq -c
zcat -f $L* | awk -v d="$DESDE" 'substr($0,1,19) >= d' | grep -c 'fontTools'
```

- El `print` dentro de `shell -c` es parte de la consulta en la consola, no código de la aplicación.
- `information_schema` puede tener hasta 24 horas de atraso (`linea-base-produccion.md`, sección 2): el peso es referencial. El agente lo contrasta con filas × tamaño estimado.
- `zcat -f $L*` lee también los registros rotados (método de 00-01).
- Pega también el uso de disco de **[PA · Panel]** (Dashboard: MB usados de 512).

| Dato | Valor |
| :--- | :---- |
| Fecha y hora de la medición (Chile) | |
| Filas totales | |
| Filas por tipo | |
| Filas por día | |
| `information_schema` (filas, datos, índices) | |
| Largo promedio del resumen | |
| Líneas de `error.log` por nivel | |
| Líneas por registrador | |
| Líneas de `fontTools` | |
| Disco del panel | |

**Contraste (lo hace el agente en `bitacora-01-06-produccion.md`):** estimación de 01-01 = ~1.200 filas al mes (~40 por día, ~280 en 7 días) y ~0,6 MB al mes. Si el real supera la estimación, el agente propone ajustar el inventario antes de cerrar.

## Si algo sale mal

`docs/operacion/retroceso.md`. Con la 0007 aplicada es el **caso 2**, que en la práctica es el **caso 1** (volver el código a `v0.2-correcciones`): la tabla nueva no molesta al código anterior. Revierte la migración solo si estorba, y siempre **antes** de volver el código.

## Respuesta del desarrollador

_(pendiente)_
