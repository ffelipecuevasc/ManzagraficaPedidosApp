# Evidencia 00-05 · Protocolo de versionado, despliegue y retroceso

- **Fecha del pedido:** 2026-10-21
- **Pedido por:** Claude Code (Opus 5.5)
- **Criterios que dependen de esta evidencia:** ensayo de retroceso medido en menos de 15 minutos con `showmigrations` igual antes y después; migración temporal fuera de `git status` y de `pedidos/migrations/`; etiqueta del despliegue de 00-04 en `git tag -n` y lista de comprobación completada.

> Este archivo existe solo porque el agente no pudo obtener estos datos por su cuenta. Responde solo lo que se pide.
>
> **Orden:** primero la parte A (ensayo en la réplica). La parte B (despliegue de 00-04) se ejecuta solo después de que el agente revise la parte A.

## Qué intentó el agente

| Dato | Qué intentó en local | Por qué se necesita al desarrollador |
| :--- | :------------------- | :----------------------------------- |
| Ensayo de retroceso | Escribió el procedimiento y el contenido de la migración temporal; ejecutó `check`, `check --deploy` y `makemigrations --check` | Crear y borrar etiquetas lo hace solo el desarrollador (`AGENTS.md`, sección 6), y aplicar migraciones en local requiere su consulta |
| Despliegue de 00-04 | Preparó la lista de comprobación y el paso a paso | Toca PythonAnywhere, la base de producción y el `.env` del servidor: prohibido al agente |

---

## Parte A · Ensayo de retroceso en la réplica local

Todo en **[PC · PowerShell 7]**, desde la raíz del repositorio. Ejecuta **un comando a la vez** y compara con lo esperado. Si algo difiere, detente y pégame la salida.

**Qué se ensaya:** el caso 2 de `docs/operacion/retroceso.md` (Clase 2 que estorba: revertir la migración y después volver el código). La «versión anterior» es la etiqueta local `ensayo-retroceso`; la «versión nueva» es la misma más una migración temporal sin versionar que crea la tabla vacía `ensayo_retroceso`.

### A1. Preparar la sesión

```powershell
git status --short
```

Esperado: nada. Si aparecen los archivos de la 00-05 sin commit, haz el commit antes (es más limpio) o anota que estaban.

```powershell
.venv\Scripts\Activate.ps1
docker compose up -d
$env:DB_NAME = "manzagrafica_replica"
python manage.py shell -c "from django.db import connection; print(connection.settings_dict['NAME'])"
```

Esperado: `manzagrafica_replica`. **Si dice otra cosa, detente:** no sigas en `manzagrafica_local`.

```powershell
git rev-parse --short HEAD
```

**Respuesta A1 (commit):** `8b492f8` (punta de `main`). `git status --short` no mostró nada (árbol limpio). La sesión apuntó a `manzagrafica_replica`.

```text
manzagrafica_replica
8b492f8
```

Nota: el primer `docker compose up -d` falló con `500 Internal Server Error` al consultar la imagen `mysql:8.0.46` (Docker Desktop todavía estaba arrancando). El segundo intento levantó el contenedor (`Container manzagrafica-mysql Started`).

### A2. Estado inicial

```powershell
python manage.py showmigrations pedidos
```

Esperado: `0001` a `0006`, todas con `[X]`.

```powershell
python manage.py shell -c "from django.db import connection; from django.db.migrations.recorder import MigrationRecorder as R; print('tabla:', 'ensayo_retroceso' in connection.introspection.table_names(), '| filas 0007:', R.Migration.objects.filter(app='pedidos', name__startswith='0007').count())"
```

Esperado: `tabla: False | filas 0007: 0`.

**Respuesta A2:**

```text
pedidos
 [X] 0001_initial
 [X] 0002_itemcotizacion
 [X] 0003_alter_itemcotizacion_cantidad_and_more
 [X] 0004_historialbd
 [X] 0005_pedido_creado_por_pedido_estado_pago_and_more
 [X] 0006_remove_pedido_valor_abonado_and_more

tabla: False | filas 0007: 0
```

### A3. Etiqueta de la versión anterior (solo local)

```powershell
git tag -a ensayo-retroceso -m "Ensayo de retroceso 00-05, solo local"
git tag -n
```

Esperado: `ensayo-retroceso` con su mensaje. **No la publiques con `push`.**

**Respuesta A3:**

```text
ensayo-retroceso Ensayo de retroceso 00-05, solo local
fase0-linea-base-2026-10-20 Estado de produccion medido el 2026-10-20
```

### A4. «Desplegar» la versión nueva con la migración temporal

Crea el archivo (no se versiona; se borra en A5):

```powershell
@'
# Migración temporal del ensayo de retroceso 00-05. No se versiona: se borra al terminar.
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("pedidos", "0006_remove_pedido_valor_abonado_and_more")]

    operations = [
        migrations.RunSQL(
            sql="CREATE TABLE ensayo_retroceso (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=InnoDB;",
            reverse_sql="DROP TABLE ensayo_retroceso;",
        ),
    ]
'@ | Set-Content -Path pedidos\migrations\0007_ensayo_retroceso.py
```

Clasifícala con su SQL:

```powershell
python manage.py sqlmigrate pedidos 0007
```

Esperado: `CREATE TABLE ensayo_retroceso (...)` y nada más. Es **Clase 2** (tabla nueva). Si aparece `ALTER`, `DROP` o algo distinto, detente.

```powershell
python manage.py makemigrations --check --dry-run
python manage.py migrate pedidos
```

Esperado: `No changes detected` y `Applying pedidos.0007_ensayo_retroceso... OK`.

```powershell
python manage.py showmigrations pedidos
python manage.py shell -c "from django.db import connection; from django.db.migrations.recorder import MigrationRecorder as R; print('tabla:', 'ensayo_retroceso' in connection.introspection.table_names(), '| filas 0007:', R.Migration.objects.filter(app='pedidos', name__startswith='0007').count())"
```

Esperado: `[X] 0007_ensayo_retroceso` y `tabla: True | filas 0007: 1`.

**Respuesta A4:**

```text
> python manage.py sqlmigrate pedidos 0007
--
-- Raw SQL operation
--
CREATE TABLE ensayo_retroceso (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=InnoDB;

> python manage.py makemigrations --check --dry-run
No changes detected

> python manage.py migrate pedidos
(advertencia mysql.W002, ver Observaciones)
Operations to perform:
  Apply all migrations: pedidos
Running migrations:
  Applying pedidos.0007_ensayo_retroceso... OK

> python manage.py showmigrations pedidos
 [X] 0001_initial
 [X] 0002_itemcotizacion
 [X] 0003_alter_itemcotizacion_cantidad_and_more
 [X] 0004_historialbd
 [X] 0005_pedido_creado_por_pedido_estado_pago_and_more
 [X] 0006_remove_pedido_valor_abonado_and_more
 [X] 0007_ensayo_retroceso

tabla: True | filas 0007: 1
```

Clasificación: **Clase 2** (una sola sentencia `CREATE TABLE`, sin `ALTER` ni `DROP`).

### A5. Retroceso medido

Desde aquí corre el reloj. Ejecuta los comandos seguidos, sin pausas largas.

```powershell
$inicio = Get-Date
```

1. Revertir la migración **con el archivo todavía presente**:

   ```powershell
   python manage.py migrate pedidos 0006 --plan
   python manage.py migrate pedidos 0006
   ```

   Esperado: el plan muestra solo `Undo` de `0007` (o `Raw SQL operation`), y después `Unapplying pedidos.0007_ensayo_retroceso... OK`.

2. Quitar el archivo de la migración (equivale a que el código anterior no lo trae):

   ```powershell
   Remove-Item pedidos\migrations\0007_ensayo_retroceso.py
   Remove-Item pedidos\migrations\__pycache__\0007_ensayo_retroceso*.pyc -ErrorAction SilentlyContinue
   ```

3. Volver el código a la etiqueta anterior:

   ```powershell
   git checkout ensayo-retroceso
   git describe --tags
   ```

   Esperado: aviso `detached HEAD` y `ensayo-retroceso`.

4. Comprobar y cerrar el reloj:

   ```powershell
   python manage.py check
   python manage.py migrate --plan
   $fin = Get-Date
   "Minutos: $([math]::Round(($fin - $inicio).TotalMinutes, 2))"
   ```

   Esperado: `System check identified no issues (0 silenced).`, `No planned migration operations.` y menos de 15 minutos.

**Respuesta A5:**

```text
> python manage.py migrate pedidos 0006 --plan
(advertencia mysql.W002, ver Observaciones)
Planned operations:
pedidos.0007_ensayo_retroceso
    Raw SQL operation -> DROP TABLE ensayo_retroceso;

> python manage.py migrate pedidos 0006
(advertencia mysql.W002, ver Observaciones)
Operations to perform:
  Target specific migration: 0006_remove_pedido_valor_abonado_and_more, from pedidos
Running migrations:
  Rendering model states... DONE
  Unapplying pedidos.0007_ensayo_retroceso... OK

> Remove-Item pedidos\migrations\0007_ensayo_retroceso.py          (sin errores)
> Remove-Item pedidos\migrations\__pycache__\0007_ensayo_retroceso*.pyc   (sin errores)

> git checkout ensayo-retroceso
Note: switching to 'ensayo-retroceso'.
You are in 'detached HEAD' state. ...
HEAD is now at 8b492f8 Épica 0 - Iteración 00-05: agrega los procedimientos de despliegue y retroceso, ...

> git describe --tags
ensayo-retroceso

> python manage.py check
System check identified no issues (0 silenced).

> python manage.py migrate --plan
(advertencia mysql.W002, ver Observaciones)
Planned operations:
  No planned migration operations.

Minutos: 1.31
```

### A6. Estado final y limpieza

```powershell
python manage.py showmigrations pedidos
python manage.py shell -c "from django.db import connection; from django.db.migrations.recorder import MigrationRecorder as R; print('tabla:', 'ensayo_retroceso' in connection.introspection.table_names(), '| filas 0007:', R.Migration.objects.filter(app='pedidos', name__startswith='0007').count())"
```

Esperado: igual que A2 (`0001` a `0006` con `[X]`; `tabla: False | filas 0007: 0`).

```powershell
git switch main
git status --short
Get-ChildItem pedidos\migrations -Recurse -Filter "0007*"
git tag -d ensayo-retroceso
git tag -l "ensayo-*"
Remove-Item Env:DB_NAME
docker compose stop
```

Esperado: `git status --short` sin `0007`; `Get-ChildItem` sin resultados; `Deleted tag 'ensayo-retroceso'`; la última lista vacía.

**Respuesta A6:**

```text
> python manage.py showmigrations pedidos
 [X] 0001_initial
 [X] 0002_itemcotizacion
 [X] 0003_alter_itemcotizacion_cantidad_and_more
 [X] 0004_historialbd
 [X] 0005_pedido_creado_por_pedido_estado_pago_and_more
 [X] 0006_remove_pedido_valor_abonado_and_more

tabla: False | filas 0007: 0

> git switch main
Switched to branch 'main'
Your branch is up to date with 'origin/main'.

> git status --short                                  (sin salida)
> Get-ChildItem pedidos\migrations -Recurse -Filter "0007*"   (sin resultados)
> git tag -d ensayo-retroceso
Deleted tag 'ensayo-retroceso' (was ec1f98f)
> git tag -l "ensayo-*"                               (sin salida)
> Remove-Item Env:DB_NAME
> docker compose stop
 ✔ Container manzagrafica-mysql  Stopped
```

---

## Resultado de la parte A

- **Ejecutada:** 2026-10-22, por el desarrollador, en **[PC · PowerShell 7]** (terminal integrada de PyCharm), sobre `manzagrafica_replica`.
- **Revisión del agente (2026-10-22):** **aprobado**. Retroceso en 1,31 minutos (menos de 15); `showmigrations` y el estado de la tabla y de `django_migrations` iguales en A2 y A6; sin `0007` en `git status` ni en `pedidos/migrations/`; etiqueta de ensayo borrada sin publicar.
- **No se hizo ningún commit** durante el ensayo, y `git status --short` terminó vacío.

| Criterio | Resultado | Dónde se ve |
| :------- | :-------- | :---------- |
| Retroceso medido en menos de 15 minutos | **1,31 minutos** | A5 |
| `showmigrations` igual antes y después | Igual: `0001` a `0006` con `[X]`; `tabla: False \| filas 0007: 0` | A2 y A6 |
| Migración temporal fuera de `git status` y de `pedidos/migrations/` | Cumple: sin salida en ambos | A6 |
| Clasificación de la migración temporal | Clase 2 (un solo `CREATE TABLE`) | A4 |
| Orden de retroceso del caso 2 (migración primero, código después) | Funcionó: `Unapplying ... OK` con el archivo todavía presente; después `migrate --plan` sin operaciones pendientes | A5 |
| Etiqueta de ensayo solo local y eliminada | Cumple: `Deleted tag 'ensayo-retroceso'`; no se publicó | A3 y A6 |

### Observaciones

1. **Advertencia `mysql.W002`** (modo estricto de MySQL no activado) en cada `migrate`: es la configuración decidida en 00-03 (`sql_mode` igual al de producción, opción A). No es un hallazgo nuevo; el modo estricto se evalúa en 02-01.
2. **Error transitorio de Docker** al primer `docker compose up -d` (`500 Internal Server Error` al consultar la imagen): Docker Desktop todavía estaba arrancando; el segundo intento funcionó. Conviene esperar a que Docker Desktop termine de iniciar antes de levantar el contenedor.
3. **Alcance de la medición:** los 1,31 minutos cubren la base de datos y el código en local. En producción se suman los pasos de la consola de PythonAnywhere y la recarga de la web app; el margen contra los 15 minutos sigue siendo amplio, pero la cifra real de producción solo se conocerá en un retroceso real.
4. **Lo que este ensayo no cubre:** solo ensayó el caso 2 de `retroceso.md`. El caso 1 (sin migraciones) es un subconjunto de él, y el caso 3 (restaurar un respaldo) se practicó por separado en la 00-03 (restauración de 4,17 s en la réplica), pero no con la función de restauración de la aplicación en producción.

---

## Parte B · Primer uso real: despliegue de la 00-04 como `v0.1-higiene`

**No ejecutar hasta que el agente revise la parte A.** Sigue `docs/operacion/despliegue.md`; aquí van los valores concretos de este despliegue. La 00-04 no trae migraciones, no cambia versiones de `requirements.txt` (solo su codificación) ni estáticos.

**Qué se despliega:** el commit `64655f8` (cierre de la 00-04). Se etiqueta ese commit y no la punta de `main`, para que los documentos de la 00-05 no viajen en este despliegue (un despliegue, un propósito).

### B1. Respaldo previo · [PC · PowerShell 7] y navegador

1. Genera y descarga un respaldo (`docs/operacion/respaldo.md`, sección 2: un solo clic).
2. Verifícalo:

   ```powershell
   python scripts\verificar_respaldo.py "<ruta del volcado>"
   $LASTEXITCODE
   ```

   Esperado: `0` y 18 de 18 tablas. Si da `1`, sigue «Si la verificación falla» de `respaldo.md` y no despliegues.
3. Agrega la fila al registro de `respaldo.md`, sección 6 (motivo: «Previo al despliegue v0.1-higiene»).

**Respuesta B1 (fecha del volcado, tamaño, SHA-256 y código):**

### B2. Lista de comprobación · [PC · PowerShell 7]

```powershell
$env:DEBUG = "False"
python manage.py check --deploy
Remove-Item Env:DEBUG
python manage.py makemigrations --check --dry-run
python manage.py showmigrations pedidos
```

Esperado: las 5 advertencias conocidas (`W004`, `W008`, `W009`, `W012`, `W016`) y ninguna otra; `No changes detected`; `0001` a `0006`.

**Respuesta B2 (completa la tabla):**

| # | Comprobación | Resultado |
| :- | :----------- | :-------- |
| 1 | Pruebas | Sin pruebas (02-01) |
| 2 | `check --deploy` | |
| 3 | `makemigrations --check` | |
| 4 | Migraciones nuevas | Ninguna (se confirma en B4) |
| 5 | Respaldo verificado | (de B1) |
| 6 | Estilos compilados | No aplica (05-04) |
| 7 | Etiqueta publicada | (de B3) |
| 8 | Punto 8 (media/, conteo, `.env`) | (de B6 y B7) |
| — | Etiqueta de partida `v0.0-inicial` | (de B5) |

### B3. Etiqueta · [PC · PowerShell 7]

Usa la fecha real del despliegue en el mensaje:

```powershell
git tag -a v0.1-higiene 64655f8 -m "Iteración 00-04 · desplegada el AAAA-MM-DD"
git push origin v0.1-higiene
git ls-remote --tags origin v0.1-higiene
git tag -n
```

Esperado: `ls-remote` devuelve una línea; `git tag -n` muestra `v0.1-higiene` con su mensaje.

**Respuesta B3 (salida de `git tag -n`):**

### B4. Ubicarse en el servidor · [PA · Bash]

Define primero `PROYECTO` y `VENV`: son **los mismos valores que usaste con `scripts/diagnostico/linea_base.sh`** en la 00-01. Valen para B4, B6, B7, B8 y B10 mientras no cierres la consola; si la cierras, vuelve a definirlos.

```bash
PROYECTO="<mismo valor que en linea_base.sh>"
VENV="<mismo valor que en linea_base.sh>"
test -f "$PROYECTO/manage.py" && test -x "$VENV/bin/python" && echo "PROYECTO y VENV correctos"
cd "$PROYECTO"
source "$VENV/bin/activate"
git status --short
git rev-parse --short HEAD
git describe --tags --always
python manage.py showmigrations pedidos
```

Esperado: `PROYECTO y VENV correctos`; `git status` sin líneas ` M` (se aceptan `??`); un commit corto (el que está hoy en producción: **anótalo**); `0001` a `0006` con `[X]`. **Si hay líneas ` M`, detente** y pégame solo los nombres de archivo.

**Respuesta B4 (commit en producción y salida de `git status`):**

### B5. Etiqueta del estado de partida `v0.0-inicial` · [PC · PowerShell 7]

**Antes de tocar nada más en el servidor.** Así, si el despliegue falla, el caso 1 de `retroceso.md` ya tiene a dónde volver. Con el commit anotado en B4:

```powershell
git tag -a v0.0-inicial <commit de B4> -m "Estado de producción antes del primer despliegue con el protocolo 00-05"
git push origin v0.0-inicial
git ls-remote --tags origin v0.0-inicial
git tag -n
```

Esperado: `ls-remote` devuelve una línea; `git tag -n` muestra `v0.0-inicial` y `v0.1-higiene`.

- Si `git tag` responde `Not a valid object name`, ese commit no está en tu repositorio local (se hizo directo en el servidor o no se publicó): **no sigas con el despliegue** y avísame.
- Tienes una etiqueta local antigua, `fase0-linea-base-2026-10-20` («Estado de produccion medido el 2026-10-20»), con el formato anterior. Compara su commit con el de B4 (`git rev-list -n 1 fase0-linea-base-2026-10-20`) y anótalo. No la borres ni la muevas sin decidirlo antes.

**Respuesta B5 (salida de `git tag -n` y commit de `fase0-linea-base-2026-10-20`):**

### B6. Punto 8.1 y 8.2: `media/` y la captura · [PA · Bash]

En la misma consola de B4 (con `PROYECTO` y `VENV` definidos y dentro de `"$PROYECTO"`):

```bash
find media -type f | wc -l
find media/pedidos -type f | wc -l
ls -l media/pedidos/Captura_de_pantalla_2026-01-20_152121.jpg
python manage.py shell -c "from pedidos.models import Pedido as P; print('captura:', P.objects.filter(imagen_referencia='pedidos/Captura_de_pantalla_2026-01-20_152121.jpg').count(), '| en pedidos/:', P.objects.filter(imagen_referencia__startswith='pedidos/').count())"
```

- Los dos `find` solo cuentan archivos; no pegues nombres.
- `ls -l`: si dice `No such file`, la captura no está en el servidor y el `checkout` no borra nada.
- **Si `captura:` es mayor que 0, detente:** copia la imagen fuera del repositorio (`cp media/pedidos/Captura_de_pantalla_2026-01-20_152121.jpg ~/`) antes de B8 y avísame.

**Respuesta B6 (los dos conteos, si existe la captura y la línea `captura: … | en pedidos/: …`):**

### B7. Punto 8.3: `.env` del servidor · [PA · Bash]

En `"$PROYECTO"`. No muestres el contenido del `.env`: estos comandos solo cuentan líneas.

```bash
grep -c '^DATABASE_URL=' .env
grep -c '^ALLOWED_HOSTS=' .env
```

Esperado: `1` y `0`.

- Si el primero da `0`, detente: la conexión a la base viene de otro lado (por ejemplo el archivo WSGI) y hay que revisarlo antes de seguir.
- Si el segundo da `1`, revisa el valor con `grep '^ALLOWED_HOSTS=' .env` (no es secreto): debe ser exactamente `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com`. Corrígelo si no.

Si el segundo dio `0`, agrega la variable. El `\n` inicial evita pegarla a la última línea si el archivo no termina en salto de línea:

```bash
printf '\nALLOWED_HOSTS=manzagrafica.pythonanywhere.com\n' >> .env
grep '^ALLOWED_HOSTS=' .env
```

Esperado: `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com`. El código actual del servidor no lee esta variable, así que agregarla antes del `checkout` no cambia nada hasta la recarga.

**Respuesta B7 (los dos conteos y la última línea):**

### B8. Traer la etiqueta · [PA · Bash]

En `"$PROYECTO"`, con el virtualenv activo:

```bash
git fetch origin --tags
git checkout v0.1-higiene
git describe --tags
git status --short
ls media/pedidos/Captura_de_pantalla_2026-01-20_152121.jpg
python manage.py check
python manage.py migrate --plan
```

Esperado:

- `detached HEAD` y `v0.1-higiene`.
- `git status` ya no lista `media/` ni `staticfiles/` (el `.gitignore` nuevo los ignora). Si aparece ` M`, detente.
- `ls`: `No such file` (el `checkout` borró la captura, como se previó).
- `check`: `System check identified no issues (0 silenced).` Si falla con `ImproperlyConfigured`, no recargues y avísame: la app vieja sigue funcionando mientras no recargues. Para dejar el código como estaba: `git checkout v0.0-inicial`.
- `migrate --plan`: `No planned migration operations.`

No hace falta `pip install` ni `collectstatic`: `requirements.txt` cambia solo de codificación y no hay cambios en `pedidos/static` (pasos 3.3 y 3.5 de `despliegue.md`). Si quieres confirmarlo: `git diff --stat v0.0-inicial v0.1-higiene -- requirements.txt pedidos/static`.

**Respuesta B8 (salidas):**

### B9. Recargar · [PA · Panel]

Pestaña **Web** → **Reload manzagrafica.pythonanywhere.com**.

**Respuesta B9 (hora de la recarga, hora de Chile):**

### B10. Verificación posterior

**Navegador, ventana privada:**

| Pantalla | Dirección | Esperado | Resultado |
| :------- | :-------- | :------- | :-------- |
| Inicio de sesión y panel | `https://manzagrafica.pythonanywhere.com/` | Inicio de sesión; después, el panel con sus cifras | |
| Listado de pedidos | `/pedidos/lista/` | Tabla de pedidos | |
| Detalle de un pedido | Cualquiera desde el listado | Ítems y pagos | |

Un **400** significa `ALLOWED_HOSTS` mal definido: vuelve a B7. Un **500** o un error en pantalla: sigue el caso 1 de `retroceso.md` hacia `v0.0-inicial`, creada en B5.

**[PA · Bash]** Registro de errores:

```bash
L=/var/log/manzagrafica.pythonanywhere.com.error.log
date -u "+%F %T UTC"
grep -c "^$(date -u +%F)" $L
tail -n 20 $L | cut -c1-160
```

Revisa solo las líneas posteriores a la recarga (el registro está en UTC: suma 3 horas a la hora de Chile). Esperado: ningún `Error`, `Traceback` ni `DisallowedHost` después de la recarga.

**Respuesta B10 (tabla completa y, del registro, cuántas líneas hay después de la recarga y de qué tipo; no pegues el texto completo):**

### B11. Registros

Agrega una fila en `docs/operacion/despliegue.md`, sección 5 (o pásame los datos y la agrego yo).

## Lo que no se pudo verificar

- Todo lo de esta evidencia: el agente no ejecuta migraciones de ensayo, etiquetas ni pasos en PythonAnywhere.
- `security.W009` en `check --deploy` se midió con el `.env` local; la clave de producción se revisa en 04-03.