# Evidencia 01-06 · Despliegue y validación de la observabilidad

- **Fecha del pedido:** 2026-10-25
- **Pedido por:** Claude Code (Opus 5.5)
- **Iteración:** [01-06](iteracion-01-06-despliegue-validacion.md). Etiqueta `v1.1-observabilidad`; partida y destino de retroceso `v0.2-correcciones`.
- **Criterios que dependen de esta evidencia:** todos los de la 01-06.
- **Estado (2026-10-25, noche; 2026-10-26 en UTC):** partes A, B y C completadas; el error controlado, la página 500, el PDF y los eventos se validaron en producción. Hallazgo: cada error queda en dos archivos con dos formatos (decisión pendiente). B8: pruebas del agente hechas, verificación en el PC pendiente. D pendiente (hacia el domingo 2026-11-01).

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
- `Ran 79 tests` y `OK` (contadas el 2026-10-25: 79 métodos `test_` en `pedidos/tests/`; puede salir la advertencia `mysql.W002`, esperada).
- `check --deploy`: solo `W004`, `W008`, `W009`, `W012` y `W016`.
- `No changes detected`.
- El SQL de la 0007 idéntico al de `bitacora-01-06.md`: un `CREATE TABLE`, un `ALTER TABLE … ADD CONSTRAINT … FOREIGN KEY` sobre `pedidos_registroevento` y dos `CREATE INDEX`. Pega el SQL completo.
- La prueba de regresión de eliminar pago en `OK`: el caso del error controlado sigue existiendo en el código que se despliega.

**SQL de `sqlmigrate pedidos 0007` (pegado por el desarrollador, 2026-10-25):**

```sql
--
-- Create model RegistroEvento
--
CREATE TABLE `pedidos_registroevento` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `momento` datetime(6) NOT NULL, `tipo` varchar(40) NOT NULL, `entidad` varchar(30) NOT NULL, `entidad_id` integer UNSIGNED NULL CHECK (`entidad_id` >= 0), `resumen` varchar(255) NOT NULL, `usuario_id` integer NULL);
ALTER TABLE `pedidos_registroevento` ADD CONSTRAINT `pedidos_registroevento_usuario_id_b991a708_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`);
CREATE INDEX `evento_momento_idx` ON `pedidos_registroevento` (`momento`);
CREATE INDEX `evento_tipo_momento_idx` ON `pedidos_registroevento` (`tipo`, `momento`);
```

Estructura: un `CREATE TABLE`, un `ALTER TABLE … ADD CONSTRAINT … FOREIGN KEY` sobre la tabla nueva y dos `CREATE INDEX`. Sin `DROP`, `RENAME` ni cambios sobre tablas existentes: **Clase 2**. La comparación literal con `bitacora-01-06.md` queda para la revisión del agente.

| # | Comprobación | Resultado |
| :- | :----------- | :-------- |
| 1 | Pruebas (`Ran N tests`, `OK`) | `Ran 79 tests in 71.016s` · `OK` (advertencia `mysql.W002`, esperada) |
| 2 | `check --deploy` (códigos) | `W004`, `W008`, `W009`, `W012`, `W016` (5 avisos, 0 silenciados) |
| 3 | `makemigrations --check` | `No changes detected` |
| 4 | `sqlmigrate 0007` igual a la bitácora; Clase 2 | Estructura esperada (ver SQL arriba); Clase 2. Comparación literal pendiente del agente |
| 5 | Respaldo verificado (A2) | Sí: `VÁLIDO`, 18 de 18, código 0 |
| 6 | Estilos compilados | No aplica |
| 7 | Etiqueta publicada (A5) | Sí: `v1.1-observabilidad` en el remoto |
| 8 | Solo la Épica 01 (más el bloque de pruebas de 02-01) | Según el mensaje de la etiqueta (01-01 a 01-05, 01-07 y el bloque de pruebas de 02-01). Contraste con `git diff` pendiente del agente |

Prueba de regresión de eliminar pago: `Ran 1 test in 2.722s` · `OK`.

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
| Nombre del archivo (hora de Chile del nombre) | `respaldo_25-10-2026_21-02-34.sql` (21:02:34, hora de Chile) |
| Tamaño (bytes) | 1.446.507 (mínimo exigido: 500.000) |
| SHA-256 | `f3163addfce276441938c03419d646770ffecd10ef48d96739c8b2fc89490aa9` |
| Tablas | 18 de 18 esperadas; faltantes: ninguna; adicionales: ninguna |
| Código | `0` · `Resultado: VÁLIDO` · línea de cierre «-- Dump completed» presente |

Agrega la fila en `docs/operacion/respaldo.md`, sección 6 (motivo: «Previo al despliegue `v1.1-observabilidad` (iteración 01-06)»). _(Pendiente de registrar en el documento.)_

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
| Código y segundos de la restauración | Código `0` · 3,6 segundos |
| Tablas | 18 |
| Últimas migraciones | `[X] 0006_remove_pedido_valor_abonado_and_more` y `[ ] 0007_registroevento` |
| ¿Existe `pedidos_registroevento`? | `False` |

Anota el refresco en la tabla de `replica-local.md`, sección 9. _(Pendiente de registrar en el documento.)_

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
| Aplicar 0007 | `Applying pedidos.0007_registroevento... OK` | 1,46 |
| Plan de reversión | Solo `Undo Create model RegistroEvento` | — |
| Revertir a 0006 (tabla existe: `False`) | `Unapplying pedidos.0007_registroevento... OK` · tabla: `False` | 1,07 |
| Aplicar de nuevo | `Applying pedidos.0007_registroevento... OK` · queda `[X] 0007_registroevento` | 1,78 |

### A5. Pruebas con la réplica restaurada y etiqueta **[PC · PowerShell 7]**

```powershell
python manage.py test pedidos
python manage.py check
```

Si todo cumple y el agente revisó la parte A, crea la etiqueta **el día del despliegue** (domingo 2026-10-25, decisión del desarrollador), **solo con todo subido a `main`**. El mensaje toma la fecha del día:

```powershell
git fetch origin
git status --short
git status -sb | Select-Object -First 1
git rev-parse HEAD origin/main
$fecha = Get-Date -Format 'yyyy-MM-dd'
git tag -a v1.1-observabilidad -m "Épica 01 · iteraciones 01-01 a 01-05 y 01-07 (y bloque de pruebas de 02-01) · desplegada el $fecha"
git tag -n v1.1-observabilidad
git push origin v1.1-observabilidad
git ls-remote --tags origin v1.1-observabilidad
```

**Esperado:** `git status --short` vacío; la primera línea de `git status -sb` es `## main...origin/main` **sin** `[ahead N]` ni `[behind N]`; los dos hashes de `rev-parse` son iguales (si no, haz `git push` o revisa antes de etiquetar); `git tag -n` muestra el mensaje con la fecha real (revísalo **antes** del `push`; si está mal, `git tag -d v1.1-observabilidad` y créala de nuevo, porque todavía no está publicada), y `ls-remote` devuelve una línea.

| Dato | Valor |
| :--- | :---- |
| Pruebas y `check` | `Ran 79 tests in 76.296s` · `OK` · `check`: «no issues (0 silenced)» |
| Mensaje de la etiqueta | `Épica 01 · iteraciones 01-01 a 01-05 y 01-07 (y bloque de pruebas de 02-01) · desplegada el 2026-10-25` |
| Commit de la etiqueta | `d6768d00274a575e48b1a800f6d9145231784b9b` (`HEAD` = `origin/main`, sin `[ahead]` ni `[behind]`) |
| Objeto de la etiqueta en el remoto | `45817771de0a8101be1b5ee7ba01f5d276c6da88` (`git ls-remote`) |

**Nota:** la etiqueta se publicó al terminar A5, antes de la revisión del agente de la parte A. Todas las comprobaciones de A1 a A5 ya habían dado el resultado esperado, y el servidor todavía no la ha traído, así que no hay efecto. Si la revisión del agente encontrara un problema antes de B3, la etiqueta se puede borrar y recrear (`git tag -d` y `git push origin :refs/tags/v1.1-observabilidad`); después de B3 ya no se toca.

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
| Últimas migraciones | `[X] 0005_pedido_creado_por_pedido_estado_pago_and_more` y `[X] 0006_remove_pedido_valor_abonado_and_more` (sin 0007) |
| `tabla_eventos` | `False` |
| `migrate --plan` | `No planned migration operations.` |
| `check --deploy` antes (códigos) | `security.W004 security.W008 security.W012 security.W016` (4 códigos; sin `W009`, a diferencia del PC: la clave secreta de producción pasa esa revisión) |

Estado verificado antes del cambio: el servidor estaba en `v0.2-correcciones` (`HEAD detached`), con `git status` vacío, a las 00:19–00:21 UTC (21:19–21:21, hora de Chile).

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

| Dato | Valor |
| :--- | :---- |
| `git fetch origin --tags` | `7944943..d6768d0  main -> origin/main` y `[new tag] v1.1-observabilidad` |
| `git checkout v1.1-observabilidad` | `HEAD is now at d6768d0 Épica 1 - Iteración 01-06: fija la ventana del despliegue, agrega la tabla de eventos al verificador tras migrar y comprueba los emojis de la 01-07 en error.log.` |
| `git describe --tags` | `v1.1-observabilidad` (`detached HEAD`) |
| `diff` de `requirements.txt` y `pedidos/static` | Sin salida: no hay dependencias nuevas ni `collectstatic` |
| `diff` de `pedidos/migrations` | Solo `pedidos/migrations/0007_registroevento.py` (98 inserciones) |

El commit del servidor (`d6768d0`) coincide con el de la etiqueta registrado en A5.

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
| `migrate --plan` | Solo `pedidos.0007_registroevento` (`Create model RegistroEvento`) |
| `check --deploy` después (códigos) y `ERRORS` | `security.W004 security.W008 security.W012 security.W016` (igual que en B2) · `ERRORS`: `0` |
| Duración de `migrate` (`real`) | `0m2,659s` (`user` 0,504 s; `sys` 0,100 s) |
| Últimas migraciones | `[X] 0006_remove_pedido_valor_abonado_and_more` y `[X] 0007_registroevento` |

`Applying pedidos.0007_registroevento... OK`, a las 00:23 UTC (21:23, hora de Chile). Se confirmó que el bloque de pruebas de 02-01 no rompe la configuración de producción (tarea 5).

Avisa al agente apenas B4 termine con `[X] 0007_registroevento`: es la señal para el paso B8.

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

| Dato | Valor |
| :--- | :---- |
| Plantilla `pago_confirm_delete.html` | `plantilla falta: el caso sigue` |
| `pago_id` para C1 | `1056` (el pago del caso real del 2026-10-22 todavía existe) |
| Eventos antes de recargar | `eventos: 0` |
| Hora UTC antes de la recarga | `2026-10-26 00:24:29` (21:24:29, hora de Chile) |

### B6. Recargar **[PA · Panel]**

Pestaña **Web** → **Reload manzagrafica.pythonanywhere.com**. Anota la hora de la recarga en Chile y en UTC.

En la consola Bash, guarda la hora UTC de la recarga para los conteos (formato exacto `AAAA-MM-DD HH:MM:SS`, la de tu anotación):

```bash
DESDE="<AAAA-MM-DD HH:MM:SS de la recarga, en UTC>"
L=/var/log/manzagrafica.pythonanywhere.com.error.log
echo "$DESDE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE válido"
```

**Esperado:** `DESDE válido`. Esta es la única línea que se completa a mano. Si la consola se cierra, define `DESDE` y `L` otra vez.

| Dato | Valor |
| :--- | :---- |
| Hora de la recarga | Anotada por el desarrollador: `00:27:15` UTC (21:27:15 Chile). Según `server.log`, el reinicio ocurrió a las **21:26:25** Chile (`00:26:25` UTC) |
| `L` | `/var/log/manzagrafica.pythonanywhere.com.error.log` (definida) |
| Validación de `DESDE` (primer intento) | **No pasó:** la consola no imprimió «DESDE válido». `DESDE` quedó con el texto de la plantilla entre `<` y `>`: `<2026-10-26 00:27:15 de la recarga, en UTC>` |

**Corrección obligatoria antes de la parte C:** `DESDE` debe llevar **solo** la fecha y la hora, sin `<`, `>` ni texto. En la misma consola:

```bash
DESDE="2026-10-26 00:27:15"
echo "$DESDE" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE válido"
```

Debe imprimir `DESDE válido`. **Resultado:** se corrigió a las 00:31 UTC e imprimió `DESDE válido`. Con el valor incorrecto, los filtros `awk 'substr($0,1,19) >= d'` de la parte C no devolverían ninguna línea.

> **Nota (2026-10-25):** después de las 21:00 hora de Chile, la fecha en UTC ya es **2026-10-26** (Chile está en UTC-3). Si recargas, por ejemplo, a las 21:30 de Chile, `DESDE` es `2026-10-26 00:30:00`, no `2026-10-25`. Usa la hora UTC que muestre `date -u` o la del panel, no la de tu reloj.

> Los filtros `awk 'substr($0,1,19) >= d'` de las partes C y D suponen que cada línea de `error.log` empieza con la fecha `AAAA-MM-DD HH:MM:SS` que antepone PythonAnywhere. No se pudieron probar contra el archivo real. Si en C2 no aparece nada, pega la salida de `tail -n 2 $L | cut -c1-40` y el agente ajusta el filtro.

### B7. Verificar después **[Navegador]**

Ventana privada: inicio de sesión, panel, listado de pedidos y detalle de un pedido (`despliegue.md`, paso 3.7). No uses «Estadísticas» (AUD-01-006).

| Revisión | Resultado |
| :------- | :-------- |
| Hora de la recarga (Chile / UTC) | 21:27:15 Chile / 00:27:15 UTC (2026-10-26), según lo anotado |
| Acceso y panel | Correcto, según el desarrollador |
| Listado y detalle de pedido | Correcto: se revisó hasta el detalle de un pedido y están todos los datos (según el desarrollador) |

Sin respuestas 500 en las pantallas revisadas: no corresponde retroceso. Se esperaba un evento `acceso_exitoso` por el inicio de sesión de B7, pero la tabla estaba vacía al revisarla en C5. La explicación probable es una sesión reutilizada (no verificada); la prueba directa de C5 confirmó que el servicio escribe.

Si algo responde 500 en estas pantallas, sigue `retroceso.md`, caso 1, con destino `v0.2-correcciones` (la tabla nueva puede quedarse: el código anterior la ignora).

### B8. Verificador de respaldos con la tabla de eventos (después de migrar)

Decisión del desarrollador (2026-10-25): `pedidos_registroevento` se agrega a las tablas esperadas **después** de B4, nunca antes (el respaldo de A2 tiene 18 tablas).

1. **El agente**, al recibir el aviso de B4: agrega la tabla a `TABLAS_ESPERADAS` de `scripts/verificar_respaldo.py` (19 tablas), la prueba con dos volcados sintéticos fabricados en su scratchpad (con la tabla: código `0`, 19 de 19; sin ella: código `1`, «1 tabla(s) faltante(s)») y actualiza `docs/operacion/respaldo.md`, sección 3. Te entrega la salida de las dos pruebas.
2. **Tú**, en **[PC · PowerShell 7]**, con el script nuevo y el respaldo de A2:

```powershell
python scripts\verificar_respaldo.py "<ruta del volcado de A2>"
$LASTEXITCODE
```

**Esperado:** `Tablas esperadas encontradas: 18 de 19`, `Tablas faltantes: pedidos_registroevento`, `Resultado: NO VÁLIDO (1 tabla(s) faltante(s))` y código `1`. Es correcto: confirma que ese volcado es anterior al despliegue. Los volcados previos a `v1.1-observabilidad` se verifican con la versión anterior: `git show v0.2-correcciones:scripts/verificar_respaldo.py > "$env:TEMP\verificar_respaldo_v02.py"`.

> Corrección (2026-10-25): en la versión anterior de este archivo, las rutas de estos dos comandos habían perdido una barra invertida y una letra (`scriptserificar_respaldo.py` y `$env:TEMPerificar_respaldo_v02.py`). Quedaron como arriba.

El cambio va en un commit después de la etiqueta: el script corre en tu PC, no en el servidor, así que no requiere otro despliegue.

| Dato | Valor |
| :--- | :---- |
| Pruebas sintéticas del agente (con y sin la tabla) | Con la tabla: `19 de 19`, VÁLIDO, código `0`. Sin ella: `18 de 19`, NO VÁLIDO (1 tabla faltante), código `1` |
| Respaldo de A2 con el script nuevo (tablas y código) | _Pendiente: se ejecuta en el PC (esperado `18 de 19`, falta `pedidos_registroevento`, código `1`)_ |

---

## Parte C · Validación (el mismo día)

> **Hallazgo de la validación (2026-10-25):** en PythonAnywhere cada error queda escrito en **dos archivos con dos formatos**:
>
> - **`error.log`** (UTC): lo escribe PythonAnywhere. Lleva el mensaje, la **traza completa** y `Internal Server Error: <ruta>`. Sin emoji, sin `nivel=` y sin método, ruta ni usuario en la primera línea.
> - **`server.log`** (hora de Chile): lleva **nuestro formato** (`❌ nivel=ERROR registrador=… metodo=… ruta=… usuario=… excepcion=… mensaje="…"`), con los saltos de línea de la traza escritos como `#012`.
>
> La suposición de las iteraciones 01-02 a 01-06 («nuestras líneas caen en `error.log`») era incorrecta. Claude Code investiga la causa y las opciones; la decisión sobre qué hacer está pendiente (`registro-pendientes.md`, sección 3). Los comandos de esta parte quedaron **adaptados** a lo que realmente ocurre.

### Preparación de la consola **[PA · Bash]**

Define estas variables y la función `desde` en la consola Bash (si la cierras, vuelve a definirlas):

```bash
cd "$PROYECTO"; source "$VENV/bin/activate"
desde() { awk -v d="$2" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] / && substr($0,1,19) >= d {f=1} f' "$1"; }
ID=<ID de B5>
L=/var/log/manzagrafica.pythonanywhere.com.error.log
S=/var/log/manzagrafica.pythonanywhere.com.server.log
DESDE="<AAAA-MM-DD HH:MM:SS de la recarga, en UTC>"
DESDE_CL="<AAAA-MM-DD HH:MM:SS de la recarga, en hora de Chile>"
```

- **`DESDE` va en UTC** (para `error.log` y `access.log`) y **`DESDE_CL` en hora de Chile** (para `server.log`). Escribe solo la fecha y la hora, **sin** `<`, `>` ni texto.
- La función `desde` corta el archivo en la **primera línea con fecha ≥ la indicada** y muestra desde ahí hasta el final. Reemplaza al filtro `awk 'substr($0,1,19) >= d'` de la versión anterior, que dejaba pasar las líneas que empiezan con una letra (`Traceback`, `django.…`) aunque fueran antiguas, porque las letras ordenan después de los números.
- Referencia del despliegue real: reinicio del servidor a las **21:26:25** (hora de Chile) = **00:26:25** UTC del 2026-10-26, según `server.log`.

### C0. Fotografía previa **[PA · Bash]**

Antes de provocar el error, para conocer la forma real de los registros y tener una base de comparación:

```bash
tail -n 6 $L | cut -c1-120
grep -c 'Error capturado por decorador' "$S"
desde $S "$DESDE_CL" | grep -o 'nivel=[A-Z]*' | sort | uniq -c
```

| Dato | Valor |
| :--- | :---- |
| Últimas líneas de `error.log` | Líneas de PythonAnywhere con fecha (`AAAA-MM-DD HH:MM:SS,mmm: mensaje`), por ejemplo `OSError: write error` (2026-10-24 y 2026-10-26 00:02:40, anteriores al despliegue) y restos de `fontTools` del 2026-10-23 |
| «Error capturado por decorador» en `server.log` (base) | `0` |
| Líneas con `nivel=` desde la recarga (antes del error controlado) | Ninguna |

### C1. Error controlado y página 500 **[Navegador]**

1. Con la sesión iniciada, anota la hora de tu reloj y abre **una sola vez** `https://manzagrafica.pythonanywhere.com/pagos/eliminar/<ID de B5>/`. Solo se abre: no hay nada que confirmar, porque la página falla antes de mostrarse.
2. **Página 500** (tarea 7): debe decir «Algo salió mal», sin «500», sin la broma de los correos y sin detalles técnicos. Recorre con Tab: «Recargar» e «Ir al inicio» muestran su foco. Repite a 360 px (modo dispositivo del navegador).
3. Pon en marcha un cronómetro y pasa a C2: el tiempo de diagnóstico cuenta desde aquí hasta tener la línea con todo el contexto.

| Dato | Valor |
| :--- | :---- |
| Hora de la petición (Chile) | Anotada por el desarrollador: 21:41. Los registros dan **21:40:36** (`server.log`) = 00:40:36 UTC (`error.log`): es la hora que se usa |
| Página 500 en escritorio | Dice «Algo salió mal», sin «500», sin la broma de los correos y sin detalles técnicos; se ve bien |
| Página 500 a 360 px | Se ve bien |
| Foco visible en los botones | Sí: «Recargar» e «Ir al inicio» muestran su foco con Tab |

### C2. Diagnóstico desde los registros **[PA · Bash]**

```bash
desde $S "$DESDE_CL" | grep "ruta=/pagos/eliminar/$ID/" | cut -c1-260
desde $L "$DESDE" | cut -c1-200
```

**Esperado:**

- **`server.log`:** dos líneas con `❌ nivel=ERROR`: la del decorador (`registrador=pedidos.decorators metodo=GET ruta=/pagos/eliminar/<ID>/ usuario=<tu id> excepcion=TemplateDoesNotExist mensaje="Error capturado por decorador en eliminar_pago"` y la traza con `#012`) y la de `django.request` (`mensaje="Internal Server Error: /pagos/eliminar/<ID>/"`).
- **`error.log`:** `Error capturado por decorador en eliminar_pago`, `Traceback (most recent call last):`, la traza, `django.template.exceptions.TemplateDoesNotExist: pedidos/pago_confirm_delete.html` e `Internal Server Error: /pagos/eliminar/<ID>/`. Sin emoji.
- Además, mira el `server log` en el visor del panel (**[PA · Panel]**, pestaña **Web** → *Log files*) y anota si el emoji se ve.

Pega solo esas líneas (cabeceras, `Traceback` y la última línea de la traza). Detén el cronómetro.

| Dato | Valor |
| :--- | :---- |
| Cabecera del decorador en `server.log` (nivel, método, ruta, usuario, excepción) | `❌ nivel=ERROR registrador=pedidos.decorators metodo=GET ruta=/pagos/eliminar/1056/ usuario=1 excepcion=TemplateDoesNotExist mensaje="Error capturado por decorador en eliminar_pago"` (hora de Chile 21:40:36) |
| Línea de `django.request` en `server.log` | `❌ nivel=ERROR registrador=django.request metodo=GET ruta=/pagos/eliminar/1056/ usuario=1 excepcion=- mensaje="Internal Server Error: /pagos/eliminar/1056/"` |
| ¿Empieza con `❌`? ¿Se ve? | `server.log`: sí, y se ve bien en el visor del panel. `error.log`: sin emoji (formato de PythonAnywhere) |
| Hora UTC en `error.log` | `2026-10-26 00:40:36,355` (decorador) y `00:40:36,362` (`Internal Server Error`) |
| ¿Traza completa con `TemplateDoesNotExist` al final? | Sí, en ambos archivos. En `error.log`: de `decorators.py` línea 19 a `django.template.exceptions.TemplateDoesNotExist: pedidos/pago_confirm_delete.html` |
| Tiempo de diagnóstico | Unos **2 minutos**: error a las 21:40:36; causa y traza a la vista a las 21:42; C2 terminó a las 21:43 (según el desarrollador). El 2026-10-22 el mismo error (las dos líneas de las 19:19:05 y 19:19:08 UTC) quedó sin traza ni causa |

### C3. Sin duplicados dentro de un archivo, sin formato perdido **[PA · Bash]**

```bash
echo "--- server.log (nuestro formato; hora de Chile) ---"
desde $S "$DESDE_CL" | grep -c "ruta=/pagos/eliminar/$ID/"
desde $S "$DESDE_CL" | grep -c "❌ nivel=ERROR .*ruta=/pagos/eliminar/$ID/"
desde $S "$DESDE_CL" | grep 'nivel=' | grep -vcE '(❗❌❗|❌|⚠️|❕|🛠️) nivel='
desde $S "$DESDE_CL" | grep -cE 'Logging error|UnicodeEncodeError'
echo "--- error.log (lo que escribe PythonAnywhere; UTC) ---"
desde $L "$DESDE" | grep -c 'Error capturado por decorador'
desde $L "$DESDE" | grep -c "Internal Server Error: /pagos/eliminar/$ID/"
desde $L "$DESDE" | grep -c 'Traceback (most recent call last)'
desde $L "$DESDE" | grep -c 'TemplateDoesNotExist: pedidos/pago_confirm_delete.html'
desde $L "$DESDE" | grep -cE 'Logging error|UnicodeEncodeError'
desde $L "$DESDE" | wc -l
```

| Archivo | Conteo | Esperado | Resultado |
| :------ | :----- | :------- | :-------- |
| `server.log` | Líneas de la ruta | `2` | `2` |
| `server.log` | Líneas con `❌ nivel=ERROR` de la ruta | `2` | `2` |
| `server.log` | Líneas con `nivel=` sin emoji | `0` | `0` |
| `server.log` | `Logging error` o `UnicodeEncodeError` | `0` | `0` |
| `error.log` | «Error capturado por decorador» | `1` | `1` |
| `error.log` | «Internal Server Error» de la ruta | `1` | `1` |
| `error.log` | Trazas | `1` | `1` |
| `error.log` | `TemplateDoesNotExist` | `1` | `1` |
| `error.log` | `Logging error` o `UnicodeEncodeError` | `0` | `0` |
| `error.log` | Líneas desde `DESDE` | 14 (el mensaje, `Traceback`, 10 líneas de la traza, la excepción e `Internal Server Error`) | `14` (medido después del PDF y de la prueba de C5) |

Interpretación:

- El error controlado quedó registrado **una sola vez en cada archivo**: no hay duplicación dentro de un mismo archivo.
- La salida admite UTF-8: el `❌` se escribe sin problemas y no hay `Logging error`.
- Lo que se repite es el **destino** (el mismo error en `error.log` y en `server.log`, con formatos distintos). Es el hallazgo descrito al inicio de esta parte.
- Desde la recarga no hay otras líneas `ERROR` ni `WARNING` además de las del pago.

### C4. PDF sin `fontTools` y sin `django.server` **[Navegador]** y **[PA · Bash]**

1. **[Navegador]** Abre una cotización y genera su **PDF**.
2. **[PA · Bash]** Comprueba primero que el PDF se generó dentro del período medido, con `access.log` (UTC, sin mostrar IP):

```bash
A=/var/log/manzagrafica.pythonanywhere.com.access.log
grep -E '26/Oct/2026:00:(2[7-9]|[3-5][0-9])' $A | grep -i pdf | awk '{print $4, $5, $6, $7, $9}'
```

3. Luego los conteos:

```bash
desde $L "$DESDE" | grep -c 'fontTools'
desde $S "$DESDE_CL" | grep -c 'fontTools'
desde $S "$DESDE_CL" | grep -c 'registrador=django.server'
desde $S "$DESDE_CL" | grep -o 'nivel=[A-Z]*' | sort | uniq -c
```

**Esperado:** la petición del PDF con código `200`; `0` líneas de `fontTools` en ambos archivos (antes, cientos por PDF); `0` de `django.server`; y, por nivel, solo los `ERROR` del error controlado (2), salvo otros errores reales.

| Dato | Valor |
| :--- | :---- |
| PDF generado | `GET /cotizaciones/27/pdf/ 200` a las `26/Oct/2026:00:54:55 +0000` (21:54:55, hora de Chile) |
| Líneas de `fontTools` | `0` en `error.log` y `0` en `server.log` |
| Líneas de `django.server` | `0` |
| Líneas por nivel | `2 nivel=ERROR` (las del error controlado) |

Además, `error.log` mide 14 líneas desde `DESDE` (después del PDF): el ruido de `fontTools` (cientos de líneas por PDF antes del cambio, como las del 2026-10-23) no volvió.

### C5. Eventos en el admin y purga **[Navegador]** y **[PA · Bash]**

1. **[Navegador]** Abre `https://manzagrafica.pythonanywhere.com/acceso-manzagrafica-admin/pedidos/registroevento/`. Debe haber al menos un `acceso_exitoso` con tu usuario y la hora de tu inicio de sesión, con `(UTC-0300)`. No debe haber un `pago_eliminado`: la página de C1 solo se abrió.
2. **[PA · Bash]**:

```bash
python manage.py purgar_registros
python manage.py shell -c "from collections import Counter; from pedidos.models import RegistroEvento as R; print(sorted(Counter(R.objects.values_list('tipo', flat=True)).items()))" | tail -n 1
grep -c 'Error capturado por decorador' "$S"
```

**Esperado:**

- `Eventos eliminados: 0 (… retención de 365 días).`
- Los eventos por tipo: al menos `('acceso_exitoso', 1)`.
- El conteo de `server.log` pasa de `0` (C0) a `1`: ahora es **nuestra propia línea** con formato, no el `print` antiguo, que ya no existe.

**Primera medición (después de B7 y de C1):** la tabla estaba **vacía** (`0 Registro de eventos` en el admin y `[]` en el conteo por tipo), aunque se había revisado la aplicación. La explicación más probable es que B7 se hizo con una **sesión ya iniciada** antes del despliegue: Django guarda las sesiones en la base de datos y sobreviven a la recarga, y una sesión que continúa no registra un «acceso exitoso» (las lecturas tampoco generan eventos, por diseño). El desarrollador no confirmó si B7 fue con sesión nueva, así que esta explicación **no está verificada**. Para descartar una falla del servicio se hizo una prueba directa.

**Prueba directa en producción:** cerrar sesión; en el acceso, escribir el usuario `nacho` con una contraseña **inventada** (rechazada); entrar con la contraseña real; revisar el admin y el conteo por tipo.

| Dato | Valor |
| :--- | :---- |
| Evento en el admin (tipo, usuario, hora) | «Acceso fallido» (usuario `-`, resumen «Usuario intentado: nacho») a las `25-10-2026 22:12:58 (UTC-0300)` y «Acceso exitoso» (usuario `nacho`, «Acceso de usuario #1») a las `25-10-2026 22:13:10 (UTC-0300)`. 2 registros |
| ¿Hay `pago_eliminado`? | No |
| Salida de `purgar_registros` | `Eventos eliminados: 0 (anteriores al 25-10-2025 22:05, hora de Chile; retención de 365 días).` |
| Eventos por tipo | Antes de la prueba: `[]`. Después: `[('acceso_exitoso', 1), ('acceso_fallido', 1)]` |
| «Error capturado por decorador» en `server.log` | `1` (base `0`): es nuestra línea con formato |
| Otros `ERROR` o `WARNING` en `server.log` | Ninguno (salvo los del pago controlado) |

Conclusión: el servicio de eventos escribe en producción con el formato esperado, y el acceso fallido guarda el nombre del usuario que existe sin la contraseña escrita.

---

## Parte D · Siete días después del despliegue

> **Nota (2026-10-25):** los comandos de registros están **adaptados** a lo que se observó en la parte C: el formato `nivel=…` está en **`server.log`** (hora de Chile) y no en `error.log`. Si la decisión pendiente sobre los dos destinos de registro cambia dónde escribe la aplicación, el agente ajusta esta parte antes de que se ejecute.

**[PA · Bash]** (define `PROYECTO`, `VENV`, `L`, `S`, `DESDE` y `DESDE_CL` como en B1, B6 y la preparación de la parte C; la medición sirve al cumplirse los siete días, hacia el domingo 2026-11-01 a la misma hora del despliegue):

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
zcat -f $S* | awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] / && substr($0,1,19) >= d' | grep -o 'nivel=[A-Z]*' | sort | uniq -c
zcat -f $S* | awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] / && substr($0,1,19) >= d' | grep -o 'registrador=[a-zA-Z_.]*' | sort | uniq -c
zcat -f $L* | awk -v d="$DESDE" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] / && substr($0,1,19) >= d' | grep -c 'fontTools'
zcat -f $S* | awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] / && substr($0,1,19) >= d' | grep -c 'fontTools'
```

- El `print` dentro de `shell -c` es parte de la consulta en la consola, no código de la aplicación.
- `information_schema` puede tener hasta 24 horas de atraso (`linea-base-produccion.md`, sección 2): el peso es referencial. El agente lo contrasta con filas × tamaño estimado.
- `zcat -f $S*` y `zcat -f $L*` leen también los registros rotados (método de 00-01). Los filtros descartan las líneas sin fecha; en `server.log` las líneas de la aplicación son de una sola línea (los saltos de la traza van como `#012`), así que el conteo por nivel y por registrador es exacto. Las líneas de la traza de `error.log` no se cuentan aquí.
- Pega también el uso de disco de **[PA · Panel]** (Dashboard: MB usados de 512).
- **Respaldo semanal de rutina** (`respaldo.md`, sección 5): verifícalo con el script nuevo de B8. Esperado: `19 de 19`, `Tablas faltantes: ninguna`, código `0`.

| Dato | Valor |
| :--- | :---- |
| Fecha y hora de la medición (Chile) | |
| Filas totales | |
| Filas por tipo | |
| Filas por día | |
| `information_schema` (filas, datos, índices) | |
| Largo promedio del resumen | |
| Líneas de `server.log` por nivel | |
| Líneas por registrador | |
| Líneas de `fontTools` (en `error.log` y en `server.log`) | |
| Disco del panel | |
| Respaldo semanal (tablas y código) | |

**Contraste (lo hace el agente en `bitacora-01-06-produccion.md`):** estimación de 01-01 = ~1.200 filas al mes (~40 por día, ~280 en 7 días) y ~0,6 MB al mes. Si el real supera la estimación, el agente propone ajustar el inventario antes de cerrar.

## Si algo sale mal

`docs/operacion/retroceso.md`. Con la 0007 aplicada es el **caso 2**, que en la práctica es el **caso 1** (volver el código a `v0.2-correcciones`): la tabla nueva no molesta al código anterior. Revierte la migración solo si estorba, y siempre **antes** de volver el código.

---

## Respuesta del desarrollador

**Parte A (2026-10-25, noche; las pruebas corrieron a las 20:59 y a las 21:11, hora de Chile):** completada sin incidencias. Las 79 pruebas pasaron dos veces (la segunda, con la réplica restaurada y la 0007 aplicada), `check --deploy` mostró solo los cinco avisos esperados, el SQL de la 0007 es Clase 2, el respaldo previo verificó 18 de 18 con código 0, la restauración en la réplica tardó 3,6 s, la migración se aplicó y se revirtió sin problemas (1,46 s, 1,07 s y 1,78 s) y la etiqueta `v1.1-observabilidad` quedó publicada sobre el commit `d6768d00274a575e48b1a800f6d9145231784b9b`.

Observación: durante las pruebas aparece un aviso de GLib sobre una aplicación de Outlook de Windows (`GLib-GIO-WARNING … supports 5 extensions but has no verbs`). Viene de las bibliotecas gráficas que usa WeasyPrint en Windows, no de la aplicación ni de Django, y no afecta los resultados.

**Parte B (2026-10-25, entre las 21:19 y las 21:27, hora de Chile; 00:19 a 00:27 UTC del 2026-10-26):** el servidor pasó de `v0.2-correcciones` a `v1.1-observabilidad` (commit `d6768d0`). Antes del cambio, la 0007 no estaba aplicada y `check --deploy` mostraba cuatro avisos. `migrate --plan` listó solo la 0007, `migrate` la aplicó en 2,659 s, y `check --deploy` quedó igual que antes, con `ERRORS` en 0. La plantilla de eliminar pago sigue faltando y el pago 1056 existe, así que el error controlado de C1 fue reproducible. La aplicación se recargó (reinicio a las 21:26:25 según `server.log`) y se revisaron acceso, panel, listado y detalle de un pedido, todo sin problemas.

Observación: la variable `DESDE` de B6 se definió la primera vez con el texto de la plantilla entre `<` y `>` y no pasó la validación; se corrigió a las 00:31 UTC y quedó válida.

**Parte C (2026-10-25, 21:40 a 22:13, hora de Chile):**

- El error controlado (pago 1056) quedó registrado **con su traza completa** en `error.log` y con el formato propio, emoji y contexto en `server.log`; el diagnóstico tomó unos 2 minutos.
- La página 500 cumplió en escritorio, a 360 px y con foco.
- El PDF de la cotización 27 se generó (`200` a las 21:54:55) sin dejar ni una línea de `fontTools` ni de `django.server`.
- El servicio de eventos escribe en producción: tras cerrar sesión, un acceso fallido con `nacho` y una contraseña inventada, y un acceso correcto, el admin mostró 2 eventos con hora de Chile. La tabla había quedado vacía después de B7; la explicación probable es una sesión reutilizada, pero **no está verificada**.
- **Hallazgo:** cada error queda escrito en dos archivos con dos formatos (`error.log`: el de PythonAnywhere; `server.log`: el nuestro con emoji y contexto). La suposición «nuestras líneas caen en `error.log`» era incorrecta. Claude Code investiga la causa y las opciones; la decisión está pendiente. No es motivo de retroceso: no se perdió ninguna línea y la traza completa está en ambos archivos.

_(Parte D: pendiente, hacia el domingo 2026-11-01. Decisión sobre los dos destinos de registro: pendiente.)_