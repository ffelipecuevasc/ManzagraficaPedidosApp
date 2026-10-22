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

**Respuesta A1 (commit):**

### A2. Estado inicial

```powershell
python manage.py showmigrations pedidos
```

Esperado: `0001` a `0006`, todas con `[X]`.

```powershell
python manage.py shell -c "from django.db import connection; from django.db.migrations.recorder import MigrationRecorder as R; print('tabla:', 'ensayo_retroceso' in connection.introspection.table_names(), '| filas 0007:', R.Migration.objects.filter(app='pedidos', name__startswith='0007').count())"
```

Esperado: `tabla: False | filas 0007: 0`.

**Respuesta A2 (pega ambas salidas):**

### A3. Etiqueta de la versión anterior (solo local)

```powershell
git tag -a ensayo-retroceso -m "Ensayo de retroceso 00-05, solo local"
git tag -n
```

Esperado: `ensayo-retroceso` con su mensaje. **No la publiques con `push`.**

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

**Respuesta A4 (salida de `sqlmigrate`, `migrate` y las dos últimas):**

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

**Respuesta A5 (pega todas las salidas y los minutos):**

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

**Respuesta A6 (pega las salidas):**

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
| 8 | Punto 8 (media/, conteo, `.env`) | (de B5 y B6) |

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

```bash
cd <carpeta del proyecto>
source <ruta del virtualenv>/bin/activate
git status --short
git rev-parse --short HEAD
git describe --tags --always
python manage.py showmigrations pedidos
```

Esperado: `git status` sin líneas ` M` (se aceptan `??`); un commit corto (el que está hoy en producción); `0001` a `0006` con `[X]`. **Si hay líneas ` M`, detente** y pégame solo los nombres de archivo.

**Respuesta B4 (commit en producción y salida de `git status`):**

### B5. Punto 8.1 y 8.2: `media/` y la captura · [PA · Bash]

```bash
find media -type f | wc -l
find media/pedidos -type f | wc -l
ls -l media/pedidos/Captura_de_pantalla_2026-01-20_152121.jpg
python manage.py shell -c "from pedidos.models import Pedido as P; print('captura:', P.objects.filter(imagen_referencia='pedidos/Captura_de_pantalla_2026-01-20_152121.jpg').count(), '| en pedidos/:', P.objects.filter(imagen_referencia__startswith='pedidos/').count())"
```

- Los dos `find` solo cuentan archivos; no pegues nombres.
- `ls -l`: si dice `No such file`, la captura no está en el servidor y el `checkout` no borra nada.
- **Si `captura:` es mayor que 0, detente:** copia la imagen fuera del repositorio (`cp media/pedidos/Captura_de_pantalla_2026-01-20_152121.jpg ~/`) antes de B7 y avísame.

**Respuesta B5 (los dos conteos, si existe la captura y la línea `captura: … | en pedidos/: …`):**

### B6. Punto 8.3: `.env` del servidor · [PA · Bash]

No muestres el contenido del `.env`: estos comandos solo cuentan líneas.

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

**Respuesta B6 (los dos conteos y la última línea):**

### B7. Traer la etiqueta · [PA · Bash]

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
- `check`: `System check identified no issues (0 silenced).` Si falla con `ImproperlyConfigured`, no recargues y avísame: la app vieja sigue funcionando mientras no recargues.
- `migrate --plan`: `No planned migration operations.`

No hace falta `pip install` ni `collectstatic`: comprobado en el paso 3.3 y 3.5 de `despliegue.md` (`requirements.txt` cambia solo de codificación; sin cambios en `pedidos/static`). Si quieres confirmarlo: `git diff --stat <commit de B4> v0.1-higiene -- requirements.txt pedidos/static`.

**Respuesta B7 (salidas):**

### B8. Recargar · [PA · Panel]

Pestaña **Web** → **Reload manzagrafica.pythonanywhere.com**.

**Respuesta B8 (hora de la recarga, hora de Chile):**

### B9. Verificación posterior

**Navegador, ventana privada:**

| Pantalla | Dirección | Esperado | Resultado |
| :------- | :-------- | :------- | :-------- |
| Inicio de sesión y panel | `https://manzagrafica.pythonanywhere.com/` | Inicio de sesión; después, el panel con sus cifras | |
| Listado de pedidos | `/pedidos/lista/` | Tabla de pedidos | |
| Detalle de un pedido | Cualquiera desde el listado | Ítems y pagos | |

Un **400** significa `ALLOWED_HOSTS` mal definido: vuelve a B6. Un **500** o un error en pantalla: sigue el caso 1 de `retroceso.md` hacia `v0.0-inicial` (B10) o el commit de B4.

**[PA · Bash]** Registro de errores:

```bash
L=/var/log/manzagrafica.pythonanywhere.com.error.log
date -u "+%F %T UTC"
grep -c "^$(date -u +%F)" $L
tail -n 20 $L | cut -c1-160
```

Revisa solo las líneas posteriores a la recarga (el registro está en UTC: suma 3 horas a la hora de Chile). Esperado: ningún `Error`, `Traceback` ni `DisallowedHost` después de la recarga.

**Respuesta B9 (tabla completa y, del registro, cuántas líneas hay después de la recarga y de qué tipo; no pegues el texto completo):**

### B10. Etiqueta del estado anterior · [PC · PowerShell 7]

Con el commit anotado en B4 (lo que estaba en producción antes de este despliegue):

```powershell
git tag -a v0.0-inicial <commit de B4> -m "Estado de producción antes del primer despliegue con el protocolo 00-05"
git push origin v0.0-inicial
git tag -n
```

Si `git tag` responde `Not a valid object name`, ese commit no está en tu repositorio local (se hizo directo en el servidor o no se publicó): no crees la etiqueta y avísame.

**Respuesta B10 (salida de `git tag -n`):**

### B11. Registros

Agrega una fila en `docs/operacion/despliegue.md`, sección 5 (o pásame los datos y la agrego yo).

## Lo que no se pudo verificar

- Todo lo de esta evidencia: el agente no ejecuta migraciones de ensayo, etiquetas ni pasos en PythonAnywhere.
- `security.W009` en `check --deploy` se midió con el `.env` local; la clave de producción se revisa en 04-03.
