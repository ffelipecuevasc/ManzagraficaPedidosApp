# Procedimiento de despliegue

Cómo etiquetar una versión, comprobar que está lista y publicarla en PythonAnywhere. Si algo sale mal durante o después del despliegue, sigue `docs/operacion/retroceso.md`.

- **Creado en:** iteración 00-05 (2026-10-21).
- **Lo ejecuta:** el desarrollador. Los agentes no crean etiquetas, no hacen `push` y no tocan PythonAnywhere.
- **Un despliegue, un propósito:** cada despliegue publica una sola iteración (o una fase cerrada), nunca una mezcla.

## 0. Dónde se ejecuta cada comando

Cada bloque de comandos dice arriba en qué terminal va:

| Marca | Terminal | Cómo abrirla |
| :---- | :------- | :----------- |
| **[PC · PowerShell 7]** | PowerShell 7 (`pwsh`) en tu computador, en la raíz del repositorio, con el `.venv` activo | Terminal de PyCharm o `pwsh`; activa con `.venv\Scripts\Activate.ps1` |
| **[PA · Bash]** | Consola Bash de PythonAnywhere | Pestaña **Consoles** → **Bash** (o una consola Bash que ya tengas abierta) |
| **[PA · Panel]** | Panel web de PythonAnywhere, sin terminal | Pestañas **Web**, **Files** o **Databases** |

**Variables `PROYECTO` y `VENV`.** Los comandos del servidor usan `"$PROYECTO"` (la carpeta del proyecto, la que tiene `manage.py`) y `"$VENV"` (la carpeta del entorno virtual). Son **los mismos valores que usaste como `PROYECTO` y `VENV` con `scripts/diagnostico/linea_base.sh`** en la 00-01; si no los tienes a mano, salen de la pestaña **Web**, sección *Code* (*Source code* y *Virtualenv*). Al abrir cada consola Bash, defínelos primero:

**[PA · Bash]**

```bash
PROYECTO="/home/manzagrafica/ManzagraficaPedidosApp"
VENV="/home/manzagrafica/ManzagraficaPedidosApp/venv"
test -f "$PROYECTO/manage.py" && test -x "$VENV/bin/python" && echo "PROYECTO y VENV correctos"
```

Esperado: `PROYECTO y VENV correctos`. Si no aparece, revisa los dos valores antes de seguir. Las variables se pierden al cerrar la consola.

**Registros:** pestaña **Web**, sección *Log files*. Desde `v1.1-observabilidad` (2026-10-25) cada error queda en dos archivos:

| Archivo | Hora | Qué tiene |
| :------ | :--- | :-------- |
| `/var/log/manzagrafica.pythonanywhere.com.server.log` | **Chile** | **El archivo de diagnóstico.** Nuestra línea con emoji y `clave=valor` (nivel, registrador, método, ruta, usuario, excepción y mensaje), con la traza en la misma línea y los saltos escritos como `#012`. Emojis desde `v1.2` (01-07 reabierta): 🔴 ERROR, 🟡 WARNING, 🔵 INFO, 🔴🔴 CRITICAL, 🟢 DEBUG; en `v1.1-observabilidad` eran ❌ ⚠️ ❕ ❗❌❗ 🛠️. |
| `/var/log/manzagrafica.pythonanywhere.com.error.log` | **UTC** | Los mismos errores en el formato de PythonAnywhere (`fecha,ms: mensaje` y la traza debajo), sin método, ruta ni usuario. Se deja como está. |

**Registrador de los errores de vista (03-01, RDA-019):** desde el despliegue que lleve la 03-01 (viaja con la 03-05), un error en cualquier vista deja **una sola** línea con `registrador=django.request`, con método, ruta, usuario y traza; el nombre de la vista se lee en la traza. Las líneas con `registrador=pedidos.decorators` son de versiones anteriores, que dejaban dos líneas por error en las 17 vistas con `@transaccion_segura`.

Para leer la traza de `server.log`, recupera los saltos de línea con `sed 's/#012/\n/g'`. En `error.log`, las líneas de la traza no llevan fecha: para cortar por hora, empieza en la primera línea con fecha ≥ la buscada y deja pasar las siguientes, porque comparar texto con `substr($0,1,19)` deja pasar como «nuevas» las líneas antiguas que empiezan con letra.

La consola Bash consume tus 100 segundos diarios de CPU. Los comandos de este documento son cortos; no dejes procesos corriendo.

## 1. Convención de etiquetas

Decidida por el desarrollador el 2026-10-21 (reemplaza el formato `fase<N>-<propósito>-AAAA-MM-DD` anotado el 2026-10-20).

**Formato:** `v<fase>.<correlativo>-<propósito>`

- `<fase>`: número de la fase del plan (igual al de la épica), sin ceros a la izquierda: `0`, `1`… `7`.
- `<correlativo>`: número del despliegue dentro de esa fase. **Cada fase parte en `1`** (aprobado por el desarrollador el 2026-10-22) y sigue sin saltos: `v0.1`, `v0.2`…, `v1.1`. El `.0` queda reservado para `v0.0-inicial`.
- `<propósito>`: una o dos palabras en minúsculas, ASCII y con guiones: `higiene`, `correcciones`, `observabilidad`.
- La etiqueta es **anotada** (`git tag -a`). Su mensaje dice la iteración y la fecha del despliegue (hora de Chile): `Iteración 00-04 · desplegada el 2026-10-22`. Es la única fecha que lleva.
- Una etiqueta publicada no se mueve ni se borra. Si un despliegue se repite con cambios, lleva el correlativo siguiente.
- `v0.0-inicial`: etiqueta especial que marca el código que estaba en producción antes del primer despliegue con este procedimiento (se crea en el paso 3.1, antes de traer la versión nueva; sección 4, punto 1). Sirve como destino de retroceso.
- **Etiquetas de ensayo** (por ejemplo `ensayo-retroceso`): solo locales, empiezan con `ensayo-`, nunca se publican con `push` y se borran al terminar el ensayo.

Ejemplos: `v0.1-higiene` (00-04), `v0.2-correcciones` (00-06), `v1.1-observabilidad`.

**[PC · PowerShell 7]** Crear y publicar la etiqueta (después de hacer commit y `git push` de `main`):

```powershell
git status --short
git tag -a v0.1-higiene -m "Iteración 00-04 · desplegada el 2026-10-22"
git push origin v0.1-higiene
git tag -n
```

- `git status --short` no debe mostrar nada. Si muestra archivos, haz commit o déjalos fuera antes de etiquetar: la etiqueta marca un commit, no lo que tienes sin guardar.
- `git tag -n` debe listar la etiqueta con su mensaje.
- Si `push` responde `rejected` o `already exists`, la etiqueta ya existe en GitHub: no la fuerces. Usa el correlativo siguiente.

**Etiquetar un commit anterior a la punta.** Cuando `main` ya tiene el trabajo del despliegue siguiente (por ejemplo, la 00-07 sobre `v1.2-capturas`), la etiqueta se crea sobre el hash del último commit que pertenece a este despliegue, no sobre la punta:

```powershell
git log --oneline -n 15
git diff --stat <hash>..main -- . ":(exclude)_planificacion" ":(exclude)docs"
$hoy = Get-Date -Format "yyyy-MM-dd"
git tag -a <etiqueta> <hash> -m "Iteración XX-YY · desplegada el $hoy"
git tag -n <etiqueta>
git push origin <etiqueta>
```

- El `diff` debe listar solo los archivos ejecutables del despliegue siguiente; cualquier otro archivo significa que el hash elegido deja fuera algo de este despliegue o mete algo del siguiente: detente.
- El resto de las reglas no cambia: `git status --short` vacío y `main` igual a `origin/main` antes de etiquetar.
- El destino de retroceso del despliegue siguiente es esta etiqueta, aunque su número de fase sea mayor (por ejemplo, `v0.3-doble-envio` vuelve a `v1.2-capturas`). El destino es la etiqueta desplegada antes, no la anterior en el orden de `git tag -n`.

## 2. Lista de comprobación previa

Se completa **antes** de tocar el servidor. Cópiala en la evidencia del despliegue con el resultado de cada punto. Si un punto falla, no despliegues.

| # | Comprobación | Terminal | Resultado esperado |
| :- | :----------- | :------- | :----------------- |
| 1 | Pruebas en verde | PC | Con el contenedor encendido, `python manage.py test pedidos` termina en `OK`, o en `OK (expected failures=N)` solo si N coincide con las regresiones declaradas (etiqueta `regresion`). Cualquier `failures`, `errors` o `unexpected successes` detiene el despliegue. Procedimiento en `pruebas.md`. |
| 2 | Revisión de producción | PC | `check --deploy` con `DEBUG=False` (abajo). Cada advertencia anotada con su iteración. |
| 3 | Sin cambios de modelo sin migración | PC | `makemigrations --check --dry-run` → `No changes detected`. |
| 4 | Migraciones nuevas clasificadas | PC | Cada migración nueva con su clase según `sqlmigrate`. Ninguna de Clase 3. |
| 5 | Respaldo verificado | PC | Si el despliegue toca datos o esquema (o es el primer despliegue de una fase): volcado descargado y `verificar_respaldo.py` con código `0` (`docs/operacion/respaldo.md`). |
| 6 | Estilos compilados | PC | Cuando el proyecto compile Tailwind (08-05; antes 05-04, RDA-014). Hasta entonces: «no aplica». |
| 7 | Etiqueta anotada creada y publicada | PC | Sección 1. `git ls-remote --tags origin <etiqueta>` devuelve una línea. |
| 8 | Pasos propios del despliegue | PA | Los que indique la evidencia de la iteración (por ejemplo, la sección 4 para la 00-04). |

**[PC · PowerShell 7]** Puntos 2 a 4:

```powershell
$env:DEBUG = "False"
python manage.py check --deploy
Remove-Item Env:DEBUG
python manage.py makemigrations --check --dry-run
python manage.py showmigrations pedidos
```

- `check --deploy` usa tu `.env` local, así que la advertencia `security.W009` (clave secreta) describe tu clave local, no la de producción.
- Advertencias medidas el 2026-10-21 (00-05): `W004` (HSTS), `W008` (redirección a HTTPS), `W009` (clave secreta), `W012` (cookie de sesión segura) y `W016` (cookie CSRF segura). Se corrigen en 04-02 y 04-03. **Desde la 04-02 (2026-11-19):** con `DEBUG=False` y `SEGURIDAD_PRODUCCION=True`, lo esperado en local es `W005` (HSTS sin `includeSubDomains`), `W021` (HSTS sin `preload`) y `W009` (hasta la 04-03); en producción, solo `W005` y `W021`. **Desde la 04-03 (`v4.5-credenciales`):** con `SEGURIDAD_PRODUCCION=True`, una clave local que no cumpla la regla de W009 ya no da la advertencia sino `ImproperlyConfigured` (medido el 2026-11-19 con el `.env` local: falla). Para revisar en local, pasa una clave generada solo a ese comando (`$env:SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`, y después `Remove-Item Env:SECRET_KEY`): lo esperado es solo `W005` y `W021`. Las dos de HSTS son **esperadas y no se silencian**: el dominio es de PythonAnywhere (04-02, D1, decisión del 2026-11-17). Con la variable apagada, en local siguen saliendo las cinco de arriba. Si aparece una advertencia que no está en esta lista o un error (`ERRORS:`), detente y revísala antes de desplegar.
- `showmigrations`: anota las migraciones que aparecen. Para saber cuáles son nuevas, compáralas con la lista que da el servidor en el paso 5.3. Para cada migración nueva:

  ```powershell
  python manage.py sqlmigrate pedidos <numero>
  ```

  Clasifícala con la regla 1 de la sección 8 de `AGENTS.md`. Si ves `DROP COLUMN`, `RENAME`, `MODIFY` o `NOT NULL` sobre una columna existente, es Clase 3: no despliegues.

## 3. Pasos del despliegue en PythonAnywhere

Antes de empezar, ten a mano el nombre de la etiqueta que se despliega y la de destino de retroceso (la anterior).

### 3.1 Abrir la consola y ubicarse

**[PA · Bash]**

```bash
cd "$PROYECTO"
source "$VENV/bin/activate"
git status --short
git rev-parse --short HEAD
git describe --tags --always
```

- `git status --short` **no debe mostrar nada**. Si muestra archivos modificados (` M`), alguien editó código directamente en el servidor: detente, no hagas `fetch` ni `checkout`, y anota la lista. Esos cambios se pierden o bloquean el despliegue.
  - Aparecer `?? media/...` o `?? staticfiles/` es normal hasta que el servidor tenga el `.gitignore` de la 00-04.
- `git rev-parse --short HEAD`: el commit que está hoy en producción. **Anótalo**.
- `git describe`: muestra la etiqueta actual si la hay.
- **Si producción no tiene etiqueta** (solo en el primer despliegue con este procedimiento), crea ahora `v0.0-inicial` sobre ese commit, **antes de seguir con el paso 3.2**. Así el caso 1 de `retroceso.md` ya tiene a dónde volver si el despliegue falla. **[PC · PowerShell 7]**:

  ```powershell
  git tag -a v0.0-inicial <commit anotado> -m "Estado de producción antes del primer despliegue con el protocolo 00-05"
  git push origin v0.0-inicial
  git ls-remote --tags origin v0.0-inicial
  ```

  Esperado: `ls-remote` devuelve una línea. Si `git tag` responde `Not a valid object name`, ese commit no está en tu repositorio local (se hizo directo en el servidor o no se publicó): no sigas con el despliegue y revísalo.

### 3.1 bis Variables del `.env` del servidor (desde la 04-02)

**Orden obligatorio: primero `.env`, luego código, luego Reload.** Desde `v4.3-configuracion-produccion`, si el `.env` del servidor tiene `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com` y **no** tiene `SEGURIDAD_PRODUCCION=True`, Django no arranca (`ImproperlyConfigured`) y el sitio cae hasta corregirlo.

**[PA · Panel o Bash]** Abre el `.env` del proyecto con el editor de PythonAnywhere (pestaña **Files**) y agrega, si faltan, estas dos líneas sin tocar las demás:

```text
SEGURIDAD_PRODUCCION=True
CSRF_TRUSTED_ORIGINS=https://manzagrafica.pythonanywhere.com
```

- `True` con mayúscula inicial; cualquier otro texto deja la variable apagada.
- El código anterior a la 04-02 ignora las dos variables: agregarlas antes del checkout no cambia nada hasta el Reload.
- Comprueba sin mostrar el resto del archivo: `grep -cE "^(SEGURIDAD_PRODUCCION=True|CSRF_TRUSTED_ORIGINS=https://manzagrafica.pythonanywhere.com)$" .env` → `2`.

**Clave secreta (desde la 04-03, condición previa del Reload).** Desde `v4.5-credenciales`, sin `SECRET_KEY`, o con `SEGURIDAD_PRODUCCION=True` y una clave de menos de 50 caracteres, de menos de 5 distintos o que empiece con `django-insecure-`, Django no arranca. Antes del checkout, con el entorno virtual activo y en la carpeta del proyecto, mide la clave **sin mostrarla**:

```bash
python -c "from dotenv import dotenv_values as d; k = d('.env').get('SECRET_KEY') or ''; print('largo', len(k), '| distintos', len(set(k)), '| django-insecure', k.startswith('django-insecure-'))"
```

- Debe dar `largo` 50 o más, `distintos` 5 o más y `django-insecure False`. Si no, **no sigas**: genera una clave nueva con `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`, reemplázala en el `.env` y vuelve a medir. Cambiar la clave cierra las sesiones abiertas.
- El mismo comando sirve en tu equipo, en PowerShell, sobre tu `.env` local. En local solo se exige que la clave exista; la medición dice si podrías revisar `check --deploy` con la variable activa sin pasar otra clave.
- Mide el `.env`, que es de donde la lee `settings.py`. Si el archivo WSGI del servidor definiera `SECRET_KEY` por su cuenta, ganaría esa: por eso, después del checkout y **antes** del Reload, corre `check --deploy` (paso 3.7): si sale `ImproperlyConfigured`, el worker sigue con el código anterior y vuelves a la etiqueta previa sin caída.

### 3.2 Traer la versión etiquetada

**[PA · Bash]**

```bash
git fetch origin --tags
git checkout <etiqueta>
git describe --tags
```

- El despliegue se hace **sobre la etiqueta, no sobre la punta de `main`**: `main` puede tener trabajo sin desplegar (RDA-007).
- `git checkout <etiqueta>` dice `You are in 'detached HEAD' state`. Es lo esperado: producción queda fija en esa etiqueta.
- `git describe --tags` debe responder exactamente `<etiqueta>`.
- Si responde `error: Your local changes ... would be overwritten`, detente: hay cambios locales (paso 3.1). No uses `--force`.
- Si `fetch` falla por red, vuelve a intentarlo una vez; GitHub está en la lista blanca de PythonAnywhere.

> **Advertencia (incidente del 2026-11-03).** En la consola del servidor solo se ejecutan `git fetch origin --tags` y `git checkout <etiqueta>`. **Nunca** el checkout de una rama (`main` u otra), `git pull`, `merge`, `rebase` ni `reset`. Los comandos de la lista de comprobación (`git checkout main`, pruebas, `check --deploy`) son del PC.
>
> - **El prompt de la consola debe decir `(HEAD detached at <etiqueta>)`** antes de cada comando de Git. Si dice `main` u otra rama, detente.
> - **La rama `main` local del servidor está atrasada** (con ella, `git describe` da `v0.0-inicial`; el 2026-11-03 Git indicó 32 commits de atraso). Un `git checkout main` ahí deja en disco código viejo. Es probable que la web app siga sirviendo el que ya tiene cargado hasta el siguiente reinicio, pero eso es una inferencia, no está comprobado.
> - Si te equivocas, no hagas `git pull`: vuelve con `git checkout <etiqueta anterior>`, comprueba `git describe --tags`, `git rev-parse --short HEAD` y que `git status --short` quede vacío, y revisa en el registro de uWSGI que no hubo reinicios entre el error y la restauración (comando de 3.6).
> - Opcional: `git branch --show-current` no imprime nada con `HEAD` suelto (si la versión de Git del servidor lo admite). En el servidor solo debería haber `HEAD` suelto sobre una etiqueta; si responde el nombre de una rama, es una alarma.

### 3.3 Dependencias (solo si cambió `requirements.txt`)

**[PA · Bash]**

```bash
git diff --stat <etiqueta o commit anterior> <etiqueta> -- requirements.txt
```

- Si no muestra nada, salta este paso.
- Si muestra cambios: `pip install -r requirements.txt` y después `pip freeze | wc -l`, que debe dar el mismo número de líneas que `requirements.txt` (hoy, 21). Revisa que el disco no se acerque a la cuota (pestaña **Files**, barra de uso).

### 3.4 Migraciones

**[PA · Bash]**

```bash
python manage.py showmigrations pedidos
python manage.py migrate --plan
```

- Si `migrate --plan` responde `No planned migration operations.`, no hay migraciones: salta al paso 3.5.
- Si lista migraciones, cada una debe estar en la lista de comprobación (punto 4) con su clase y el respaldo del punto 5 debe estar verificado. Entonces:

  ```bash
  python manage.py migrate
  python manage.py showmigrations pedidos
  ```

  Todas deben quedar con `[X]`. Si `migrate` falla a medio camino, detente y sigue el caso 2 de `retroceso.md`.

### 3.5 Archivos estáticos (solo si cambiaron)

**[PA · Bash]**

```bash
git diff --stat <etiqueta o commit anterior> <etiqueta> -- pedidos/static
```

Si muestra cambios: `python manage.py collectstatic --noinput`. Debe terminar con `N static files copied`. Si no muestra nada, salta el paso.

### 3.6 Recargar la web app

**[PA · Panel]** Pestaña **Web** → botón verde **Reload manzagrafica.pythonanywhere.com**. Espera a que el botón vuelva a su estado normal.

Anota la hora de la recarga (hora de Chile): sirve para filtrar el registro de errores.

**Qué hora se anota (regla vigente desde el 2026-11-04).** La hora oficial de una recarga es la del **reinicio efectivo**: la línea `Starting uWSGI` de `server.log`, cuyo prefijo está en hora de Chile. No es la del reloj del desarrollador ni la de la consola de PythonAnywhere (que marca UTC: Chile + 3 h en horario de verano y + 4 h en invierno). La línea `received message 0 from emperor` marca el clic de **Reload** (orden recibida) y va unos segundos antes del reinicio: en la 00-07, 01:32:45 y 01:32:51. Con la hora del clic no se filtra el registro; se usa la del reinicio.

**Detectar reinicios de uWSGI (solo lectura, con filtro por fecha).** **[PA · Bash]**

```bash
S=/var/log/manzagrafica.pythonanywhere.com.server.log
DESDE_CL="2026-11-03 23:30:00"
echo "$DESDE_CL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE_CL válido"
for f in "$S" "$S".*; do [ -f "$f" ] && zcat -f "$f"; done \
  | awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9:]+ \*\*\* Starting uWSGI/ && substr($0,1,19) >= d { print substr($0,1,19), "Starting uWSGI" }' \
  | sort
```

- `DESDE_CL` va en hora de Chile, sin `<` ni `>`. Cada línea impresa es un reinicio efectivo; sin líneas, no hubo reinicios desde esa hora. Solo imprime la fecha y una etiqueta fija, nunca la línea del registro.
- **No uses `zcat -f $S*` sin filtro de fecha:** el glob recorre también los archivos rotados y devuelve líneas antiguas. El filtro exige que la línea empiece con fecha, sea de arranque y sea posterior a `DESDE_CL`.
- **Probado el 2026-11-04** (consulta de solo lectura, sin modificar el servidor): con `DESDE_CL="2026-11-03 23:30:00"` imprimió solo la línea de las 00:11:49.

### 3.7 Verificar después

En el navegador, en una ventana privada:

1. `https://manzagrafica.pythonanywhere.com/` → pantalla de inicio de sesión (o el panel, si ya tienes sesión). Inicia sesión.
2. **Panel** (`/`) → carga con sus tarjetas y cifras.
3. **Listado de pedidos** (`/pedidos/lista/`) → carga la tabla.
4. **Detalle de un pedido** (abre cualquiera desde el listado) → carga los ítems y pagos.

No uses «Estadísticas» para verificar: cada visita agrega una fila a `pedidos_historialbd` (AUD-01-006).

Si cualquiera responde **400 Bad Request**, revisa `ALLOWED_HOSTS` en el `.env` del servidor (sección 4, paso 4.3). Si responde **500** o *Something went wrong*, revisa el registro de errores y sigue `retroceso.md`.

**[PA · Bash]** Registro de errores después de la recarga:

```bash
L=/var/log/manzagrafica.pythonanywhere.com.server.log
TZ=America/Santiago date "+%F %T (hora de Chile)"
grep -c "^$(TZ=America/Santiago date +%F)" $L
grep "nivel=" $L | tail -n 20 | cut -c1-200
# Traza completa de una línea: grep "ruta=/la/ruta/" $L | sed 's/#012/\n/g'
```

- `L` apunta a `server.log`, el archivo de diagnóstico (opción A del 2026-10-25), que escribe la hora de **Chile**. Si quieres mirar `error.log`, recuerda que está en **UTC** (Chile está 3 horas atrás en horario de verano).
- Filtra por `nivel=ERROR` (o `nivel=`), nunca por el emoji: «🔴🔴 nivel=CRITICAL» contiene «🔴 nivel=».
- Revisa solo las líneas con hora posterior a la recarga. Lo esperado es ninguna línea `Error`, `Traceback` ni `DisallowedHost` después de la recarga.
- Si hay errores, copia en la evidencia **solo el tipo de error y la hora**, no el texto completo: puede traer datos de clientes.

**Imágenes de referencia sin pedido (`media/referencias/`).** Desde la 03-03 (decisión del 2026-11-04), si crear o editar un pedido falla después de guardar la imagen del formulario, la base se revierte pero el archivo ya escrito en disco queda sin pedido: el sistema de archivos no participa en la transacción. Se acepta y no se borra de forma automática. Si un `nivel=ERROR` de `crear_pedido` o `editar_pedido` coincide con un formulario que traía imagen, anótalo. **No borres archivos de `media/` sin comprobar antes que ningún pedido los usa**: `duplicar_pedido` copia la ruta de la imagen, así que dos pedidos pueden compartir el mismo archivo, y `media/` no tiene copia (AUD-02-023).

### 3.8 Cierre

- Anota en la evidencia de la iteración: etiqueta desplegada, commit, lista de comprobación, resultado de las pantallas y del registro.
- Vuelve a la terminal de tu PC y deja el `.venv` y Docker como estaban.
- Desde el 2026-11-18 no hay un periodo de vigilancia ni una lectura de «día 7» después del despliegue (RDA-021): el despliegue se valida con la lectura del día 0 y se respalda con el plan de retroceso (`retroceso.md`).

### 3.9 Cuando un usuario reporta un error (desde la 03-04)

No hay código de error ni identificador (RDA-013). La página 500 y los avisos le piden al usuario **en qué pantalla estaba y a qué hora**. Con eso se busca la traza en `server.log`, que escribe la hora de **Chile**.

| Qué ve el usuario | Qué queda en `server.log` |
| :---------------- | :------------------------ |
| Página «Algo salió mal» (500) | Una línea `django.request` con método, ruta, usuario y traza |
| Aviso «No pudimos guardar el detalle de productos…» (pedido o cotización, devuelve el formulario) | Una línea `nivel=ERROR` de `pedidos.views` con la traza («Un ítem del pedido…» o «Un ítem de la cotización… no se pudo guardar»). La respuesta es 200: **no aparece como 500 en `access.log`** |
| Aviso «Este formulario venció y no se guardó…» | ~~**Por verificar en producción (03-05):** se espera una línea `nivel=INFO` «Envío sin token válido…» con método, ruta y usuario; en la réplica local sí sale, en producción aún no se ha comprobado.~~ **Verificada en producción el 2026-11-16 (03-05, partes C4 y C5):** sale una línea `nivel=INFO` «Envío sin token válido…» con método, ruta y usuario (dicho por el desarrollador; la línea no se copió a la evidencia). No es un error del sistema: el formulario venció, se abrió en otra sesión o ya había más de 20 formularios abiertos |
| Aviso de respaldo o restauración | Una línea `nivel=ERROR` de `pedidos.views` con la traza |

**[PA · Bash]** Buscar por día, hora y pantalla (reemplaza la fecha, la hora y la ruta por lo que informó el usuario):

```bash
L=/var/log/manzagrafica.pythonanywhere.com.server.log
# Errores de esa hora (hora de Chile)
grep "^2026-11-05 15:" $L | grep "nivel=ERROR" | cut -c1-200
# Solo una pantalla
grep "nivel=ERROR" $L | grep "ruta=/pedidos/nuevo/" | cut -c1-200
# Traza completa de la línea elegida
grep "^2026-11-05 15:" $L | grep "ruta=/pedidos/nuevo/" | sed 's/#012/\n/g'
```

- Rutas más frecuentes: crear pedido `/pedidos/nuevo/`, editar pedido `/pedido/editar/<n.º>/`, crear cotización `/cotizaciones/nueva/`, editar cotización `/cotizaciones/editar/<n.º>/`, convertir `/cotizaciones/convertir/<n.º>/`, registrar pago `/pagos/ingresar/`.
- Si la pantalla era un formulario con un aviso de ítem, el usuario **no perdió lo escrito**: sigue en pantalla y puede guardar de nuevo.
- Nunca copies a la evidencia el texto completo de una línea: puede traer datos de clientes. Anota el tipo de error y la hora.

### 3.10 Despliegue de la 04-03 (`v4.5-credenciales`): ensayo y orden

**Estado (2026-11-19): ~~implementada, pendiente de ensayo y despliegue~~ desplegada y verificada (`v4.5-credenciales`, sección 5). El ensayo se realizó con `CUMPLE`.** La sección se conserva como registro; el script ya no se necesita. El script puente vive fuera del repo: `C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-03\puente_ensayo_04_03.py`. Detalle en `bitacora-04-03.md`; excepción en `replica-local.md`, sección 8.

#### Orden de despliegue

1. Medir la clave de producción (3.1 bis): largo ≥ 50, distintos ≥ 5, `django-insecure False`. Si no, cambiarla en el `.env` del servidor y volver a medir.
2. Pegar el texto propuesto en `.env.example` (lo edita el desarrollador; está en `bitacora-04-03.md`) y hacer el commit **antes** de crear la etiqueta.
3. Respaldo previo en producción `VÁLIDO` (`respaldo.md`).
4. Ensayo en la réplica con `RESULTADO: CUMPLE` (pasos siguientes).
5. Etiqueta anotada `v4.5-credenciales` y `git push` de la etiqueta.
6. En el servidor: checkout de la etiqueta (3.2) y `git describe` → `v4.5-credenciales`.
7. `check --deploy` **antes** del Reload: solo W005 y W021. Si sale `ImproperlyConfigured`, no recargues: corrige la clave o vuelve al checkout de `v4.4-hsts-semana` (el worker sigue con el código anterior).
8. Reload y verificaciones del mismo día: la aplicación arranca, un respaldo desde la web se descarga completo y sale `VÁLIDO`, `server.log` sin errores de `mysqldump`, `ls /tmp/mysql_opciones_* 2>/dev/null | wc -l` → `0`.
9. Retroceso: `retroceso.md`, caso 1, a `v4.4-hsts-semana` (sin migraciones). Si solo falla el arranque por la clave, se corrige el `.env` y se recarga.

#### Ensayo en la réplica, paso a paso (PowerShell 7, en tu equipo)

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

`$LASTEXITCODE` debe ser `0` (paridad, con o sin diferencias aceptadas). Si es `1`, no sigas: anota la fila que sale «No».

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

**Paso 6. Lee los conteos.**

| Línea | Qué debe decir |
| :---- | :------------- |
| `Carpeta del ensayo: …` | Una ruta dentro de tu carpeta, **anótala** (la usas en el paso 8). |
| `[1] Antes: N tablas, F filas` | Cualquier número. |
| `[2] Respaldo de la app: … línea de cierre: sí` | `sí`. |
| `[3] Volcado de seguridad nativo: … línea de cierre: sí` | `sí`. |
| `[4] Restauración del mismo volcado: terminó sin error` | Esa frase. |
| `[5] Después: N tablas, F filas; tablas con conteo distinto: 0` | Mismos N y F que en `[1]`, y `0`. |
| `[6] … procesos del ensayo vistos: X` | X de 1 o más (si es 0, fue tan rápido que no probó nada: repite el paso 5). |
| `con contraseña en argumentos: equipo 0, contenedor 0` | `0` y `0`. |
| `[7] Archivos de opciones residuales: equipo 0, contenedor 0` | `0` y `0`. |
| `RESULTADO: CUMPLE` y `$LASTEXITCODE` = `0` | **Éxito.** |

**Paso 7. Si falla.**

- `NO SE EJECUTA: …` (código 2): no tocó nada. Corrige lo que dice (casi siempre falta el paso 2 o el 3) y repite el paso 5.
- `[2]` con `NO`, o se corta antes de `[4]`: la base **no** se restauró. Guarda la salida.
- Error **durante** `[4]` (traza de Python después de `[3]`): la réplica puede haber quedado a medias. Restaura el volcado nativo con `replica-local.md`, sección 5, usando como ruta `<Carpeta del ensayo>\seguridad_nativo.sql`, y repite el paso 3.
- `[5]` con conteos distintos, o `[6]` o `[7]` con algo distinto de 0: el ensayo **no cumple**; no despliegues.
- Residuales en `[7]`: bórralos con `docker exec manzagrafica-mysql sh -c "rm -f /tmp/mysql_opciones_*"` (contenedor) o `Remove-Item "$env:TEMP\mysql_opciones_*"` (equipo).

**Paso 8. Limpieza (siempre, cumpla o no).**

```powershell
Remove-Item Env:DB_NAME
Remove-Item -Recurse -Force "<Carpeta del ensayo que anotaste en el paso 6>"
Remove-Item -Recurse -Force "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-03"
docker compose stop
```

- Borra la carpeta del ensayo **solo si salió `CUMPLE`**: tiene volcados con datos reales. Si falló, consérvala hasta resolverlo.
- Comprueba que no quedó la variable: `$env:DB_NAME` no debe mostrar nada.

### 3.11 Despliegue de la 04-04 (`v4.6-restauracion`): ensayo y orden

**Estado (2026-11-19): implementada, pendiente de ensayo y despliegue. El ensayo y la revisión del formato D2 están pendientes de ejecutar por el desarrollador.** Sin fecha fija: se despliega el día en que quede ensayada, con verificación el mismo día (RDA-021). Retroceso: `v4.5-credenciales`. Scripts fuera del repo, en `C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-04\`: `revisar_volcado_d2.py` (formato D2) y `puente_ensayo_04_04.py` (ensayo). Excepción en `replica-local.md`, sección 8.

#### Orden de despliegue

1. **Formato D2 con un respaldo real de producción** (paso 6 de abajo): `RESULTADO: CUMPLE D2`. Si una regla da `False`, **no despliegues**: la aplicación rechazaría sus propios respaldos.
2. **Ensayo en la réplica** con `RESULTADO: CUMPLE` (pasos de abajo, con el respaldo del paso 0).
3. **Respaldo previo en producción** `VÁLIDO` (`respaldo.md`) y, sobre ese mismo archivo, `revisar_volcado_d2.py` → `CUMPLE D2`.
4. Etiqueta anotada `v4.6-restauracion` y `git push` de la etiqueta.
5. En el servidor: checkout de la etiqueta (3.2) y `git describe` → `v4.6-restauracion`. Sin migraciones, `pip` ni `collectstatic` (comprueba con `git diff --stat v4.5-credenciales v4.6-restauracion`: código en `utils.py`, `views.py`, `restaurar_bd.html` y `respaldar_bd.html`).
6. `check --deploy` **antes** del Reload: solo W005 y W021.
7. Reload y verificaciones del mismo día:
   - «Restaurar» carga y muestra el campo «Para confirmar, escribe RESTAURAR».
   - Sube un `.sql` vacío creado en tu equipo (`New-Item vacio.sql`), escribe `RESTAURAR` y confirma: debe salir «El archivo no es un respaldo válido de esta aplicación (o supera los 20 MB). No se tocó la base.» y **no** debe aparecer un `emergencia_` nuevo en «Respaldar BD» ni en `ls "$PROYECTO"/backups/`.
   - Un respaldo desde la web («Generar Nuevo Respaldo BD») se descarga completo y sale `VÁLIDO`.
   - `server.log` y `error.log` sin errores nuevos desde el Reload.
   - **No se ejecuta una restauración real en producción:** la cubre el ensayo.
8. Retroceso: `retroceso.md`, caso 1, a `v4.5-credenciales` (sin migraciones). Un `emergencia_` que haya quedado no estorba al código anterior: lo rota como cualquier `.sql`.

#### Ensayo en la réplica y formato D2, paso a paso (PowerShell 7, en tu equipo)

Todo en **una sola ventana** de PowerShell 7. Si la cierras a la mitad, vuelve a empezar desde el paso 1. **Nunca** uses `docker compose down -v` ni `docker volume rm`: borran la base.

**Paso 1. Ubícate en el proyecto y activa el entorno virtual.**

```powershell
cd "D:\Trabajo\Proyectos PYTHON\Proyectos Personales\Pedidos Manzagrafica\PedidosApp"
.\.venv\Scripts\Activate.ps1
```

Debe verse `(.venv)` al inicio de la línea. Si no, no sigas.

**Paso 2. Comprueba que el contenedor está arriba.**

```powershell
docker compose up -d
docker inspect -f "{{.State.Running}}" manzagrafica-mysql
```

Debe responder `true`. Si no: abre Docker Desktop, espera «Engine running» y repite; si sigue sin subir, mira `docker compose logs db --tail 30` y detente.

**Paso 3. Apunta la sesión a la réplica y comprueba la paridad.**

```powershell
$env:DB_NAME = "manzagrafica_replica"
python scripts\diagnostico\paridad_replica.py
$LASTEXITCODE
```

Debe dar `0`. Si da `1`, no sigas: anota la fila que sale «No».

**Paso 4. Elige la carpeta de volcados, fuera del repositorio.**

```powershell
$carpeta = "<tu carpeta de respaldos descargados, fuera del repo>"
Test-Path $carpeta
```

Debe dar `True`. Si da `False`, créala con `New-Item -ItemType Directory $carpeta` o corrige la ruta.

**Paso 5 (paso 0 de la iteración). Guarda un respaldo de la réplica y verifícalo.** Se genera dentro del contenedor (la contraseña va por `MYSQL_PWD`, no en los argumentos) y se copia a tu carpeta:

```powershell
docker exec manzagrafica-mysql sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot --no-tablespaces --set-gtid-purged=OFF manzagrafica_replica > /tmp/replica_paso0.sql'
docker cp manzagrafica-mysql:/tmp/replica_paso0.sql "$carpeta\replica_paso0_04-04.sql"
docker exec manzagrafica-mysql rm -f /tmp/replica_paso0.sql
python scripts\verificar_respaldo.py "$carpeta\replica_paso0_04-04.sql"
```

El último comando debe terminar en `VÁLIDO` (19 de 19). Si dice `NO VÁLIDO` o un comando da error, no sigas.

**Paso 6. Formato D2 sobre respaldos reales.** Primero el de la réplica del paso 5 y después un respaldo real de producción que ya tengas descargado y verificado (por ejemplo, el del despliegue de la 04-03):

```powershell
$d2 = "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-04\revisar_volcado_d2.py"
python $d2 "$carpeta\replica_paso0_04-04.sql"
$LASTEXITCODE
python $d2 "<ruta de un respaldo de producción, por ejemplo respaldo_19-11-2026_14-13-28.sql>"
$LASTEXITCODE
```

Cada uno imprime ocho reglas con `True` o `False`, termina en `RESULTADO: CUMPLE D2` y `$LASTEXITCODE` = `0`. **Si alguna regla da `False`, detente y pégame las ocho líneas** (no traen datos): la validación habría que ajustarla antes de desplegar.

**Paso 7. Ejecuta el ensayo.**

```powershell
python "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-04\puente_ensayo_04_04.py" --carpeta $carpeta --respaldo-paso0 "$carpeta\replica_paso0_04-04.sql"
$LASTEXITCODE
```

Tarda lo que tardan dos respaldos y una restauración de la réplica (minutos). No cierres la ventana.

**Paso 8. Lee los conteos.**

| Línea | Qué debe decir |
| :---- | :------------- |
| `[0] Respaldo del paso 0: existe y cumple D2` | Esa frase. |
| `Carpeta del ensayo: …` | **Anótala** (la usas en el paso 10). |
| `[1] Antes: N tablas, F filas` | Cualquier número. |
| `[2] Volcado A: … cumple D2: sí` | `sí`. |
| `[3] Volcado de seguridad nativo: … cumple D2: sí` | `sí`. |
| `[4] Volcado inválido rechazado sin respaldo ni restauración: sí` | `sí`. |
| `[5] Sin RESTAURAR, rechazado sin tocar nada: sí` | `sí`. |
| `[6] Restauración con RESTAURAR: correcta sí, X s` | `sí`; anota los segundos. |
| `Respaldo emergencia_: 1 archivo(s), cumple D2: sí; mensaje lo nombra: sí` | `1`, `sí`, `sí`. |
| `Subida borrada de backups/tmp: sí` | `sí`. |
| `[7] … «Restauración iniciada» 1, «resultado=correcta» 1` | `1` y `1`. |
| `[8] Después: … tablas con conteo distinto: 1 (esperado 1: eventos +1, esperado +1)` | `1` y `+1` (solo el evento de la restauración). |
| `[9] … procesos del ensayo vistos: X; con contraseña en argumentos: equipo 0, contenedor 0` | X de 1 o más; `0` y `0`. |
| `Archivos de opciones residuales: equipo 0, contenedor 0` | `0` y `0`. |
| `RESULTADO: CUMPLE` y `$LASTEXITCODE` = `0` | **Éxito.** Pégame las líneas (son solo conteos). |

**Paso 9. Si falla.**

- `NO SE EJECUTA: …` (código 2): no tocó nada. Corrige lo que dice y repite el paso 7.
- Se corta en `[2]` o `[3]`: la base **no** se restauró. Pégame la salida.
- `[4]` o `[5]` con `NO`: la validación no funciona como se espera; no despliegues. Pégame la salida.
- Error o `NO` en `[6]` (traza de Python después de `[5]`): la réplica puede haber quedado a medias. Restaura `<Carpeta del ensayo>\seguridad_nativo.sql` con `replica-local.md`, sección 5, y repite el paso 3. Si eso también falla, usa `replica_paso0_04-04.sql`.
- `[8]` con otro conteo distinto, o `[9]` con algo distinto de 0: el ensayo **no cumple**; no despliegues.
- Residuales: `docker exec manzagrafica-mysql sh -c "rm -f /tmp/mysql_opciones_*"` (contenedor) o `Remove-Item "$env:TEMP\mysql_opciones_*"` (equipo).

**Paso 10. Limpieza (siempre, cumpla o no).**

```powershell
Remove-Item Env:DB_NAME
Remove-Item -Recurse -Force "<Carpeta del ensayo que anotaste en el paso 8>"
Remove-Item -Force "$carpeta\replica_paso0_04-04.sql"
Remove-Item -Recurse -Force "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-04"
docker compose stop
```

- Borra la carpeta del ensayo y el respaldo del paso 0 **solo si salió `CUMPLE`**: tienen datos reales. Si falló, consérvalos hasta resolverlo.
- Si todavía existe la carpeta del ensayo de la 04-03 (no se informó su borrado), bórrala también.
- `$env:DB_NAME` no debe mostrar nada.

### 3.12 Despliegue de la 04-05 (`v4.7-correcciones-config`): revisión manual y orden

La 04-05 no cambia datos ni pantallas: cambia cómo se lee la configuración (`django.conf.settings`), agrega `conn_health_checks=True` (solo con `DATABASE_URL`, es decir, en producción), deja `TEMPLATES['DIRS']` vacío y limpia importaciones. Sin migraciones, `pip` ni `collectstatic`. Retroceso: `v4.6-restauracion`.

#### A. Revisión manual en la réplica (PowerShell 7, en tu PC, antes de etiquetar)

Todo en **una sola ventana**. **Nunca** `docker compose down -v` ni `docker volume rm`.

**Paso 1. Proyecto y entorno virtual.**

```powershell
cd "D:\Trabajo\Proyectos PYTHON\Proyectos Personales\Pedidos Manzagrafica\PedidosApp"
.\.venv\Scripts\Activate.ps1
git status --short
```

Debe verse `(.venv)` al inicio de la línea. `git status` muestra los archivos de la 04-05 sin confirmar (o nada, si ya hiciste el commit). Si no ves `(.venv)`, no sigas.

**Paso 2. Contenedor arriba.**

```powershell
docker compose up -d
docker inspect -f "{{.State.Running}}" manzagrafica-mysql
```

Debe responder `true`. Si no: abre Docker Desktop, espera «Engine running» y repite; si sigue, `docker compose logs db --tail 30` y detente.

**Paso 3. Réplica y paridad.**

```powershell
$env:DB_NAME = "manzagrafica_replica"
python scripts\diagnostico\paridad_replica.py
$LASTEXITCODE
```

Debe dar `0`. Si da `1`, no sigas (`replica-local.md`, sección 7).

**Paso 4. Arrancar la aplicación.**

```powershell
python manage.py runserver
```

Debe terminar en `Starting development server at http://127.0.0.1:8000/`. Si sale un error (`ImproperlyConfigured`, `OperationalError` o `TemplateDoesNotExist`), pégalo y detente: es justo lo que esta revisión busca.

**Paso 5. Pantallas, en el navegador (escritorio).** Inicia sesión en `http://127.0.0.1:8000/` con un superusuario de la réplica y abre, una por una:

| Pantalla | Dirección | Qué debe verse |
| :------- | :-------- | :------------- |
| Panel | `/` | Igual que antes: tarjetas, tablas y la fecha del último respaldo de tu `backups/` local. |
| Lista | `/pedidos/lista/` | La tabla de pedidos con su paginación. |
| Detalle | Clic en un pedido de la lista (`/<número>/`) | Datos, ítems y pagos del pedido. |
| Respaldos | `/base_datos/respaldar_bd/` | La lista de respaldos (nombre, fecha y tamaño). **No pulses «Generar respaldo».** |
| Restaurar | `/base_datos/restaurar_bd/` | El formulario con el campo `RESTAURAR`. **Solo carga: no subas ningún archivo.** |
| PDF de cotización | `/cotizaciones/lista/` → una cotización → botón del PDF (`/cotizaciones/<número>/pdf/`) | El PDF se abre o se descarga con el formato de siempre. |

Ninguna debe dar error 500 ni «TemplateDoesNotExist». En la ventana de `runserver` cada pantalla debe dar `200` (o `302` al iniciar sesión).

**Paso 6. Las mismas pantallas a 360 px.** En el navegador, `F12` → icono de dispositivo (`Ctrl+Shift+M`) → ancho `360`. Recorre las cinco primeras: sin barra horizontal de la página y con los botones visibles. El PDF no se revisa a 360 px.

**Paso 7. Si algo falla.**

- Error 500 o `TemplateDoesNotExist`: copia las últimas 30 líneas de la ventana de `runserver` (sin datos de clientes) y detente. **No despliegues.**
- Una pantalla se ve distinta de `v4.6-restauracion`: para comparar, detén `runserver` (`Ctrl+C`), `git stash`, vuelve a arrancar y mira la misma pantalla; después `Ctrl+C` y `git stash pop`. Si la diferencia es de la 04-05, no despliegues.
- El PDF falla: anota el mensaje; WeasyPrint no cambia en esta iteración, así que avisa antes de seguir.

**Paso 8. Limpieza (siempre).**

```powershell
# Ctrl+C en la ventana de runserver
Remove-Item Env:DB_NAME
$env:DB_NAME
docker compose stop
```

`$env:DB_NAME` no debe mostrar nada.

#### B. Orden del despliegue (en este orden, sin saltar pasos)

1. **Respaldo de producción ANTES del checkout** (lección de la 04-04: el respaldo `17-40-30` se tomó con el código nuevo ya activo). Genera y descarga el respaldo desde la web con `v4.6-restauracion` todavía activo (`respaldo.md`, sección 2). En tu PC:

   ```powershell
   python scripts\verificar_respaldo.py "<ruta del respaldo descargado>"
   python "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\f2f9a3a5-9ccf-4bf1-97a7-8cd78d581188\scratchpad\despliegue-04-05\revisar_volcado_d2.py" "<ruta del respaldo descargado>"
   $LASTEXITCODE
   Get-FileHash "<ruta del respaldo descargado>" -Algorithm SHA256
   ```

   Debe dar `VÁLIDO` (19 de 19), `RESULTADO: CUMPLE D2` y `0`. Anota nombre, tamaño y SHA-256. Si algo no cumple, no sigas. (Si la carpeta temporal del agente ya no existe, pídele de nuevo `revisar_volcado_d2.py`.)
2. **Etiqueta** anotada `v4.7-correcciones-config` sobre el commit de la 04-05 y `git push` de la etiqueta (sección 1). Antes, en el PC: `git diff --stat v4.6-restauracion v4.7-correcciones-config` debe mostrar solo `PedidosApp/settings.py`, `pedidos/views.py`, `pedidos/urls.py`, pruebas y documentos; **sin** `requirements.txt`, `pedidos/migrations/` ni `pedidos/static/`.
3. **Checkout** en el servidor (3.2): `git fetch origin --tags`, `git checkout v4.7-correcciones-config` y `git describe` → `v4.7-correcciones-config`. Sin migraciones, `pip` ni `collectstatic`.
4. **`check --deploy` antes del Reload** (3.7): solo `W005` y `W021`. Si sale `ImproperlyConfigured` u otra advertencia, **no recargues**: vuelve al checkout de `v4.6-restauracion` (el worker sigue con el código anterior).
5. **UN solo Reload.** Pulsa Reload **una vez** y confirma el reinicio con el comando «Detectar reinicios de uWSGI» (3.6), con `DESDE_CL` igual a la hora de Chile de un minuto antes del clic. Debe imprimir **una** línea `Starting uWSGI`; anota su hora. **No repitas el Reload** aunque la pantalla tarde: si no aparece la línea tras dos minutos, vuelve a correr el comando, no el Reload. Si después de cinco minutos sigue sin aparecer, detente y avisa.
6. **Verificaciones del mismo día (RDA-021):**
   1. El respaldo del paso 1 quedó como respaldo previo (ya verificado).
   2. Acceso, panel, una lista y el PDF de una cotización responden como antes, sin 500.
   3. `server.log` y `error.log` sin `Traceback`, `OperationalError`, `IntegrityError` (agregado el 2026-11-27), «MySQL server has gone away» ni `TemplateDoesNotExist` **desde el último `Starting uWSGI`, sin filtrar por fecha**. Lección de la 04-05: un `grep` por la fecha al inicio de la línea no ve las líneas de traza de `error.log` (no empiezan con fecha) y `DESDE_CL` quedó sin definir en esa consola. **[PA · Bash]**:

      ```bash
      S=/var/log/manzagrafica.pythonanywhere.com.server.log
      E=/var/log/manzagrafica.pythonanywhere.com.error.log
      awk 'FNR==NR { if (/\*\*\* Starting uWSGI/) n=FNR; next } FNR==n { print substr($0,1,19), "último Starting uWSGI" } FNR>n && /Traceback|OperationalError|IntegrityError|gone away|TemplateDoesNotExist/ { c++ } END { print "coincidencias desde el arranque:", c+0 }' "$S" "$S"
      tail -n 80 "$E"
      ```

      `awk` lee `server.log` dos veces: la primera ubica la última línea `Starting uWSGI`; la segunda cuenta desde ella (en `server.log` la traza va en la misma línea, con `#012`). Solo imprime la hora del arranque y un conteo, nunca la línea. Debe mostrar la hora de tu Reload y `coincidencias desde el arranque: 0`. `tail` muestra el final de `error.log` (UTC) con las trazas completas: lee desde la hora UTC del arranque hacia abajo; lo anterior es histórico. Ese archivo puede no estar en orden cronológico en algún tramo (visto en la 04-05, sin causa conocida): no cortes por la primera fecha que veas. No pegues líneas con datos de clientes. **`IntegrityError` (agregado el 2026-11-27, desde la 14-04):** es el error que lanza Django cuando MySQL rechaza un dato por una restricción, por ejemplo un folio repetido contra un índice único; los despliegues que agregan una restricción nueva lo necesitan en el conteo. Casi siempre ya sale junto a un `Traceback`, pero así también se cuenta si el error se registra como un mensaje corto. Los despliegues anteriores (3.13 a 3.16) usaron el comando sin esta palabra; sus resultados de la sección 5 no se reescriben.
7. **Observación posterior (no bloquea el cierre, decisión del 2026-11-19):** después de una hibernación, la primera petición responde sin 500 y `server.log` no muestra `OperationalError` ni «gone away». AUD-01-016 queda «corregido en código, pendiente de verificar en producción» hasta esa observación.
8. **Retroceso:** `retroceso.md`, caso 1, a `v4.6-restauracion` (sin migraciones; no hay datos que deshacer).

### 3.13 Despliegue de la 04-06 (`v4.8-historial-clientes`): réplica, migración y orden

La 04-06 cambia `Pedido.cliente` y `Cotizacion.cliente` de `CASCADE` a `PROTECT`: un cliente con pedidos o cotizaciones ya no se puede borrar (ni desde la aplicación ni desde el admin) y la pantalla dice por qué. **Trae la migración `0008_proteger_historial_cliente`, Clase 1:** `sqlmigrate` da solo `(no-op)` (2026-11-20, bitácora 04-06), es decir, MySQL no cambia ninguna tabla. Sin `pip` ni `collectstatic`. Retroceso: `v4.7-correcciones-config`.

Desde la 04-06 el script del formato D2 está versionado: `scripts\diagnostico\revisar_volcado_d2.py` (ya no se usa la copia de la carpeta temporal del agente).

#### A. Réplica: respaldo, migración y revisión manual (PowerShell 7, en tu PC, antes de etiquetar)

Todo en **una sola ventana**. **Nunca** `docker compose down -v` ni `docker volume rm`.

**Paso 1. Proyecto, entorno y contenedor.** Igual que 3.12 A, pasos 1 a 3: `cd` al proyecto, `.\.venv\Scripts\Activate.ps1`, `docker compose up -d`, `$env:DB_NAME = "manzagrafica_replica"` y `python scripts\diagnostico\paridad_replica.py` → `0`. Si algo no da lo esperado, no sigas.

**Paso 2. Respaldo de la réplica (obligatorio antes de `migrate`).**

```powershell
$carpeta = "<tu carpeta de respaldos descargados, fuera del repo>"
docker exec manzagrafica-mysql sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot --no-tablespaces --set-gtid-purged=OFF manzagrafica_replica > /tmp/replica_04-06.sql'
docker cp manzagrafica-mysql:/tmp/replica_04-06.sql "$carpeta\replica_antes_04-06.sql"
docker exec manzagrafica-mysql rm -f /tmp/replica_04-06.sql
python scripts\verificar_respaldo.py "$carpeta\replica_antes_04-06.sql"
python scripts\diagnostico\revisar_volcado_d2.py "$carpeta\replica_antes_04-06.sql"
```

Debe dar `VÁLIDO` (19 de 19) y `RESULTADO: CUMPLE D2`. Si no, no sigas.

**Paso 3. Estructura de las tablas ANTES.** Guarda la salida en tu carpeta (no en el repo):

```powershell
docker exec manzagrafica-mysql sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot manzagrafica_replica -e "SHOW CREATE TABLE pedidos_pedido\G SHOW CREATE TABLE pedidos_cotizacion\G"' > "$carpeta\estructura_antes_04-06.txt"
(Get-FileHash "$carpeta\estructura_antes_04-06.txt").Hash
```

Anota el hash.

**Paso 4. Plan y migración.**

```powershell
python manage.py migrate pedidos --plan
python manage.py sqlmigrate pedidos 0008
python manage.py migrate pedidos
python manage.py showmigrations pedidos
```

- `--plan` debe listar **solo** `pedidos.0008_proteger_historial_cliente` con dos `Alter field cliente`.
- `sqlmigrate` debe mostrar solo `-- (no-op)` dos veces. **Si aparece `ALTER`, `DROP` o `ADD CONSTRAINT`, no ejecutes `migrate`** y avisa.
- `showmigrations` debe dejar `[X] 0008_proteger_historial_cliente`. (La advertencia `mysql.W002` de modo estricto es conocida, AUD-02-020; no bloquea.)

**Paso 5. Estructura DESPUÉS y conteos.** Repite el paso 3 cambiando `antes` por `despues` y compara:

```powershell
(Get-FileHash "$carpeta\estructura_despues_04-06.txt").Hash
```

Debe ser **igual** al hash del paso 3. Si cambia, avisa: la migración no fue Clase 1. Cuenta las filas de cada tabla con `SELECT COUNT(*)` (solo números; ejecútalo también **antes** de migrar, junto al paso 3, y guarda ambas salidas):

```powershell
docker exec manzagrafica-mysql sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysql -uroot manzagrafica_replica -e "SELECT COUNT(*) AS clientes FROM pedidos_cliente; SELECT COUNT(*) AS pedidos FROM pedidos_pedido; SELECT COUNT(*) AS items_pedido FROM pedidos_itempedido; SELECT COUNT(*) AS pagos FROM pedidos_pago; SELECT COUNT(*) AS cotizaciones FROM pedidos_cotizacion; SELECT COUNT(*) AS items_cotizacion FROM pedidos_itemcotizacion;"'
```

Los seis números deben ser iguales antes y después de migrar. (Antes existía aquí una referencia a un «script de conteos» que no está en el repositorio; corregido el 2026-11-20. Los conteos de la bitácora 04-06, 825 clientes, son anteriores a un borrado accidental en la réplica: hoy son 824.)

**Paso 6. Arrancar la aplicación.** `python manage.py runserver` → `Starting development server at http://127.0.0.1:8000/`. Inicia sesión con un superusuario de la réplica.

**Paso 7. Las tres pruebas en el navegador (escritorio).**

| Prueba | Cómo | Qué debe verse |
| :----- | :--- | :------------- |
| Cliente con historial | `/clientes/lista/` → un cliente que tenga pedidos → «Eliminar». En la confirmación, pulsa «Sí, Eliminar». | Antes de pulsar: la advertencia «Solo se puede eliminar un cliente sin pedidos ni cotizaciones» y el botón visible. Después: la misma pantalla con el recuadro «No se eliminó: No se puede eliminar este cliente porque tiene pedidos o cotizaciones registrados. Para conservar su historial, no está permitido borrarlo.» El cliente sigue en la lista y sus pedidos siguen en `/pedidos/lista/`. En `runserver`, `200`, no `500`. |
| Cliente de prueba sin historial | Crea un cliente `Prueba 04-06` en `/clientes/nuevo/` y elimínalo. | Vuelves a la lista y el cliente ya no está. |
| Admin | `/acceso-manzagrafica-admin/` → Clientes → el mismo cliente con historial → «Eliminar». | El admin dice que no se puede borrar porque hay objetos protegidos (pedidos o cotizaciones) y **no ofrece confirmar**. No borres nada más desde el admin. |

**Paso 8. A 360 px.** `F12` → `Ctrl+Shift+M` → ancho `360`. Repite la confirmación y el rechazo del cliente con historial: el recuadro de error y los botones se ven completos, sin barra horizontal de la página.

**Paso 9. Si algo falla.**

- Error 500 al rechazar: copia las últimas 30 líneas de `runserver` (sin datos de clientes) y detente. **No despliegues.**
- El cliente con historial se borró: detente de inmediato y restaura la réplica desde `replica_antes_04-06.sql` (`replica-local.md`); avisa al agente.
- El admin ofrece borrar en cascada: la migración no está aplicada; vuelve al paso 4.

**Paso 10. Limpieza (siempre).** `Ctrl+C` en `runserver`, `Remove-Item Env:DB_NAME`, `$env:DB_NAME` (vacío) y `docker compose stop`. La réplica queda con `0008` aplicada; para volverla atrás: `python manage.py migrate pedidos 0007` con `DB_NAME` de la réplica.

#### B. Orden del despliegue (en este orden, sin saltar pasos)

1. **Respaldo de producción ANTES del checkout**, con `v4.7-correcciones-config` todavía activo (`respaldo.md`, sección 2). En tu PC:

   ```powershell
   python scripts\verificar_respaldo.py "<ruta del respaldo descargado>"
   python scripts\diagnostico\revisar_volcado_d2.py "<ruta del respaldo descargado>"
   $LASTEXITCODE
   Get-FileHash "<ruta del respaldo descargado>" -Algorithm SHA256
   ```

   Debe dar `VÁLIDO` (19 de 19), `RESULTADO: CUMPLE D2` y `0`. Anota nombre, tamaño y SHA-256. **Con migración, este respaldo es obligatorio:** si algo no cumple, no sigas.
2. **Etiqueta** anotada `v4.8-historial-clientes` sobre el commit de la 04-06 y `git push` de la etiqueta (sección 1). Antes, en el PC: `git diff --stat v4.7-correcciones-config v4.8-historial-clientes` debe mostrar `pedidos/models.py`, `pedidos/views.py`, `pedidos/migrations/0008_proteger_historial_cliente.py`, `cliente_confirm_delete.html`, `scripts/diagnostico/revisar_volcado_d2.py`, pruebas y documentos; **sin** `requirements.txt`, `settings.py` ni `pedidos/static/`.
3. **Checkout** en el servidor (3.2): `git fetch origin --tags`, `git checkout v4.8-historial-clientes` y `git describe` → `v4.8-historial-clientes`.
4. **Plan y revisión, antes de migrar** (3.4 y 3.7):

   ```bash
   python manage.py migrate --plan
   python manage.py check --deploy
   ```

   `--plan` debe listar **solo** `pedidos.0008_proteger_historial_cliente`. `check --deploy`: solo W005 y W021. Si sale otra migración, otra advertencia o un error, **no migres ni recargues**: vuelve al checkout de `v4.7-correcciones-config`.
5. **Migración, después del checkout y antes del Reload** (3.4):

   ```bash
   python manage.py migrate
   python manage.py showmigrations pedidos
   ```

   Debe terminar en `Applying pedidos.0008_proteger_historial_cliente... OK` y dejar `[X] 0008_proteger_historial_cliente`. Si falla, detente y sigue el paso 8.
6. **UN solo Reload**, confirmado con el comando «Detectar reinicios de uWSGI» (3.6) con `DESDE_CL` definido en esa misma consola (hora de Chile de un minuto antes del clic): **una** línea `Starting uWSGI`; anota su hora. No repitas el Reload. **`DESDE_CL` lleva la fecha y hora reales de hoy** (no la del ejemplo de 3.6) y el comando de validación debe imprimir `DESDE_CL válido`; **sin esa línea, la consulta no sirve** (no filtra o no imprime nada): corrige `DESDE_CL` y repítela antes de seguir.
7. **Verificaciones del mismo día (RDA-021):**
   1. Acceso, panel y `/clientes/lista/` sin 500.
   2. Abre la confirmación de eliminar de un cliente **con historial** y comprueba que dice «Solo se puede eliminar un cliente sin pedidos ni cotizaciones». **No pulses «Sí, Eliminar»:** el rechazo ya se probó en la réplica.
   3. Registros **desde el último `Starting uWSGI`, sin filtro por fecha**: el `awk` sobre `server.log` y el `tail -n 80` de `error.log` de 3.12 B, paso 6.3. Debe dar la hora de tu Reload y `coincidencias desde el arranque: 0`, y `error.log` sin entradas nuevas tras la hora UTC del arranque.
8. **Retroceso** (decisión del desarrollador, 2026-11-19): `retroceso.md`, caso 1, a `v4.7-correcciones-config` y Reload. **No hace falta revertir la `0008`:** es Clase 1 y MySQL no cambió; el código anterior la ignora. `python manage.py migrate pedidos 0007` es **opcional**, solo si estorba (caso 2, que rige también para Clase 1), y siempre **antes** de volver el código. Si los datos se dañaran, caso 3 con el respaldo del paso 1.

### 3.14 Despliegue de la 04-07 (`v4.9-sanitizacion-html`): dependencia `nh3` y orden

La 04-07 limpia el HTML del editor con `nh3`, en dos momentos: al guardar y al mostrar (RDA-020). **Trae una dependencia nueva, `nh3==0.3.8`, en `requirements.txt`.** No trae migraciones ni `collectstatic`. Retroceso: `v4.8-historial-clientes`.

`nh3` ya está instalado en el venv de la web app: lo instalaste en el paso 0 del 2026-11-20, con 837 kB, 1,17 s de CPU y el venv de 135 M a 137 M. El código lo importa recién al sanitizar, no al arrancar. Por eso, **si el Reload va antes de que `nh3` esté instalado, el arranque no falla, pero los detalles y los formularios responden 500.** Revisa que esté instalado antes de recargar.

#### A. Antes (en tu PC)

1. Réplica: la revisión manual del paso 6 de la iteración, en escritorio y a 360 px. Si sale un 500 o se pierde formato que no esperabas, no sigas.
2. `python manage.py test pedidos` → `Ran 411 tests`, `OK (expected failures=3)`.

#### B. Orden del despliegue

1. **Respaldo de producción ANTES del checkout**, con `v4.8-historial-clientes` todavía activo, igual que en 3.13 B, paso 1. Tiene que salir `VÁLIDO` (19 de 19), `RESULTADO: CUMPLE D2` y `0`. Anota el nombre, el tamaño y el SHA-256. Es el respaldo de rutina: no hay migración ni limpieza de datos.
2. **Etiqueta** anotada `v4.9-sanitizacion-html` sobre el commit de la 04-07, y `git push` de la etiqueta (sección 1). Antes, en el PC, `git diff --stat v4.8-historial-clientes v4.9-sanitizacion-html` debe mostrar `requirements.txt` (+1), `pedidos/forms.py`, `pedidos/sanitizar.py`, `pedidos/templatetags/` y las tres plantillas de detalle, además de pruebas y documentos. **No** debe mostrar `pedidos/migrations/`, `settings.py`, `views.py` ni `pedidos/static/`.
3. **Checkout** en el servidor (3.2): `git fetch origin --tags`, luego `git checkout v4.9-sanitizacion-html`, y `git describe` debe dar `v4.9-sanitizacion-html`.
4. **Dependencia, antes del Reload** (3.3), en la consola, con el venv de la web app:

   ```bash
   "$VENV/bin/pip" install -r requirements.txt
   "$VENV/bin/pip" show nh3 | grep -E '^(Name|Version):'
   "$VENV/bin/python" -c "import nh3; print(nh3.clean('<p>a</p><script>b</script>', tags={'p'}))"
   ```

   - `pip show` debe mostrar `Version: 0.3.8`. **Corregido el 2026-11-20:** antes decía `| head -2`, que corta la tubería cuando `pip` todavía escribe y deja un `BrokenPipeError` inofensivo pero confuso; `grep` lee toda la salida y no lo provoca.
   - La última línea debe imprimir `<p>a</p>`.
   - `pip install` no debería descargar nada nuevo (todo `Requirement already satisfied`).
   - Si la versión no es `0.3.8` o la importación falla, **no recargues**: vuelve con `git checkout v4.8-historial-clientes`.
   - `pip freeze | wc -l` debe dar lo mismo que `wc -l < requirements.txt` (22 desde la 04-07).
5. **Revisión, antes del Reload:** `python manage.py migrate --plan` debe decir que no hay migraciones (`No planned migration operations.`). `python manage.py check --deploy` solo puede mostrar W005 y W021. Si sale otra cosa, no recargues.
6. **UN solo Reload**, confirmado con «Detectar reinicios de uWSGI» (3.6), con `DESDE_CL` válido definido en esa misma consola. Tiene que aparecer **una** línea `Starting uWSGI`: anota su hora y no repitas el Reload. Justo **antes** de pulsar Reload, calcula `DESDE_CL`, muéstralo y valídalo en la misma consola:

   ```bash
   DESDE_CL="$(TZ=America/Santiago date -d '1 minute ago' '+%Y-%m-%d %H:%M:%S')"
   echo "DESDE_CL=$DESDE_CL"
   echo "$DESDE_CL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE_CL válido"
   ```

   Tienen que salir la hora de Chile de un minuto antes y `DESDE_CL válido`. Si falta alguna de las dos líneas, no sigas con el comando de 3.6. (Agregado el 2026-11-20: en el despliegue de la 04-07 se omitió mostrarlo y validarlo; el filtro funcionó igual.)
7. **Verificaciones del mismo día (RDA-021):**
   1. Abre el detalle de un pedido, una cotización y un producto que tengan negrita, cursiva o listas. Se tienen que ver igual que antes y sin 500.
   2. Abre el formulario de edición de uno de ellos y **guárdalo sin cambios**. El detalle debe seguir igual. ~~**No uses los pedidos 46 ni 56:** si se guardan, se borra su imagen incrustada.~~ **(2026-11-20) No guardes ninguno de los 15 pedidos con HTML fuera de la lista blanca:** 46, 56, 37, 54, 909, 209, 907, 67, 222, 131, 438, 933, 47, 953 y 541. Al guardarlos, `nh3` borra lo que está fuera de la lista (en el 46 y el 56, su imagen incrustada). La lista sale de la réplica del 2026-11-18; **producción puede tener más**, así que para esta prueba usa un producto o un pedido creado después de ese día, o uno que sepas que solo tiene negrita, cursiva o listas.
   3. Abre el PDF de una cotización y revisa que salga.
   4. Revisa los registros desde el último `Starting uWSGI`, sin filtro por fecha: el `awk` sobre `server.log` y el `tail -n 80` de `error.log` (3.12 B, paso 6.3). Debe dar `coincidencias desde el arranque: 0`. Cuéntalo **después** de usar las pantallas.
8. **Retroceso:** `retroceso.md`, caso 1 (sin migraciones). Vuelve a `v4.8-historial-clientes` y haz Reload. **`nh3` puede quedarse instalado**, porque el código anterior no lo usa. Si el único problema es que falta `nh3` (500 en detalles y formularios), basta con instalarlo (paso 4) y recargar; no hace falta retroceder.

### 3.15 Despliegue de la 04-08 (`v4.10-acceso-limites`): migración, variables y medición de la dirección

La 04-08 limita los intentos de acceso (5 por usuario y 20 por conexión en 15 minutos, bloqueo de 15) en `accounts/login/` y en el admin, deja un evento `acceso_bloqueado` por bloqueo, redirige al panel si ya hay sesión, limita la imagen de referencia a 5 MB y rechaza sin leerlo un POST demasiado grande a crear o editar pedidos y a restaurar. **Trae la migración `0009_acceso_bloqueado`, Clase 1:** `sqlmigrate` da solo `-- (no-op)` (agente, 2026-11-21, contra la réplica). Toca `settings.py` (caché, límites de subida, un middleware nuevo y dos variables) y `urls.py`. Sin `pip` ni `collectstatic`. Retroceso: `v4.9-sanitizacion-html`.

**El riesgo principal:** si la aplicación ve a todos con la misma dirección (la del proxy de PythonAnywhere), 20 errores de cualquiera bloquean a todos. Por eso el despliegue entra con el contador por conexión **en modo medición** y la dirección se mide (C) antes de dejar los valores finales. Esa medición necesita **un segundo Reload, de ajuste**: el despliegue tiene un solo Reload (B.6) y el ajuste otro (C.4), cada uno confirmado con `DESDE_CL`.

Las dos variables nuevas del `.env` (ninguna es obligatoria; un valor que no sea un entero ≥ 0 detiene el arranque con `ImproperlyConfigured`):

| Variable | Sin definir | Para qué |
| :------- | :---------- | :------- |
| `ACCESO_PROXIES_CONFIABLES` | `0`: usa `REMOTE_ADDR` | Cuántos proxies propios hay delante. Con `1`, toma el último valor de `X-Forwarded-For`. **Se mide (C), no se supone.** |
| `ACCESO_FALLOS_POR_DIRECCION` | `20` | Fallos por conexión antes del bloqueo. `0` apaga solo ese contador: es el interruptor de emergencia ([desbloqueo-de-acceso](desbloqueo-de-acceso.md)). |

#### A. Antes (en tu PC)

1. Réplica (la del refresco del 2026-11-18, con la `0009` ya aplicada por el agente el 2026-11-21 después del respaldo `replica_antes_04-08.sql`). Igual que 3.13 A, pasos 1 y 6: entorno, `docker compose up -d`, `$env:DB_NAME = "manzagrafica_replica"`, paridad `0`, `runserver`. Revisión manual del paso 6 de la iteración, en escritorio y a 360 px:
   1. `/accounts/login/` con un usuario de la réplica y contraseña equivocada **5 veces**: la quinta todavía dice «Credenciales incorrectas»; la sexta, con la contraseña **correcta**, dice «Acceso bloqueado por 15 minutos» y no entra.
   2. Detén `runserver` (`Ctrl+C`) y vuelve a arrancarlo: equivale a recargar y desbloquea. Entra con la contraseña correcta.
   3. Con sesión iniciada, abre `/accounts/login/`: te lleva al panel.
   4. Cierra sesión y repite el punto 1 en `/acceso-manzagrafica-admin/`: el mensaje de bloqueo aparece arriba del formulario del admin.
   5. Admin → Registro de eventos, filtro por tipo «Acceso bloqueado»: un evento por bloqueo, sin dirección ni nombre escrito.
   6. Crear pedido con una imagen de referencia de menos de 5 MB: se guarda. ~~Con una de más de 5 MB~~ **Corregido el 2026-11-22:** con una **imagen real de 5 a 7 MB** (un archivo que no es imagen da otro error, y sobre 7,5 MB el chequeo temprano del cuerpo la rechaza antes, con el mensaje de tamaño): el formulario dice «La imagen de referencia supera los 5 MB…» y no guarda.
   7. Restaurar (`/base_datos/restaurar_bd/`) con un archivo `.sql` de más de 21 MB (~~puedes crear uno con `fsutil file createnew "$carpeta\grande.sql" 23000000`~~ **corregido el 2026-11-22:** `fsutil` pide administrador; créalo con `$f = [IO.File]::Create("$carpeta\grande.sql"); $f.SetLength(23000000); $f.Dispose()`): vuelve al formulario con «El archivo supera el tamaño permitido y no se recibió. No se guardó nada.» **No** uses un respaldo real. Borra el archivo al terminar.
   8. A 360 px (`F12`, `Ctrl+Shift+M`, ancho `360`): el recuadro del bloqueo se lee completo, sin barra horizontal.
   9. Limpieza: `Ctrl+C`, `Remove-Item Env:DB_NAME`, `docker compose stop`. Para volver la réplica atrás: `python manage.py migrate pedidos 0008` con `DB_NAME` de la réplica.
2. `python manage.py test pedidos` → `Ran 446 tests`, `OK (expected failures=3)`.
3. `.env.example`: pega el texto de la bitácora 04-08 (el agente no pudo leer ni editar ese archivo) y haz el commit **antes** de la etiqueta.

#### B. Orden del despliegue

1. **Respaldo de producción ANTES del checkout**, con `v4.9-sanitizacion-html` todavía activo, igual que en 3.13 B, paso 1: `VÁLIDO` (19 de 19), `RESULTADO: CUMPLE D2` y `0`. Anota el nombre, el tamaño y el SHA-256. **Con migración, es obligatorio:** si algo no cumple, no sigas.
2. **Etiqueta** anotada `v4.10-acceso-limites` sobre el commit de la 04-08 y `git push` de la etiqueta (sección 1). Antes, en el PC, `git diff --stat v4.9-sanitizacion-html v4.10-acceso-limites` debe mostrar `PedidosApp/settings.py`, `PedidosApp/urls.py`, `.env.example`, `pedidos/limite_acceso.py`, `pedidos/forms.py`, `pedidos/senales.py`, `pedidos/admin.py`, `pedidos/models.py`, `pedidos/migrations/0009_acceso_bloqueado.py`, `registration/login.html`, pruebas y documentos. **No** debe mostrar `requirements.txt`, `pedidos/views.py` ni `pedidos/static/`.
3. **`.env` del servidor, antes del checkout** (3.1 bis, pestaña **Files**): agrega **solo** esta línea, de medición:

   ```
   ACCESO_FALLOS_POR_DIRECCION=3
   ```

   No agregues `ACCESO_PROXIES_CONFIABLES` todavía. El código anterior ignora la variable. Comprueba: `grep -c '^ACCESO_FALLOS_POR_DIRECCION=3$' .env` → `1`.
4. **Checkout** (3.2): `git fetch origin --tags`, `git checkout v4.10-acceso-limites` y `git describe` → `v4.10-acceso-limites`.
5. **Plan, revisión y migración, antes del Reload** (3.4 y 3.7). **Agregado el 2026-11-22:** en una consola nueva, activa primero el entorno virtual (`source "$VENV/bin/activate"`, 3.1) y solo después corre `manage.py`. El 2026-11-21 a las 23:12, un checkout en una consola sin el entorno dio `ModuleNotFoundError` y hubo que volver a `v4.9-sanitizacion-html` sin migrar.

   ```bash
   python manage.py migrate --plan
   python manage.py check --deploy
   python manage.py migrate
   python manage.py showmigrations pedidos
   ```

   - `--plan` debe listar **solo** `pedidos.0009_acceso_bloqueado` con `Alter field tipo on registroevento`. Si lista otra cosa, **no migres**: vuelve al checkout de `v4.9-sanitizacion-html`.
   - `check --deploy`: solo W005 y W021. Si sale `ImproperlyConfigured` (por ejemplo, una variable `ACCESO_` mal escrita), corrige el `.env` y repite; **no recargues** mientras tanto.
   - `migrate` debe terminar en `Applying pedidos.0009_acceso_bloqueado... OK` y `showmigrations`, en `[X] 0009_acceso_bloqueado`.
6. **UN solo Reload**, con `DESDE_CL` calculado, mostrado y validado en la misma consola justo antes (igual que 3.14 B, paso 6) y confirmado con «Detectar reinicios de uWSGI» (3.6): **una** línea `Starting uWSGI`. Anota su hora.
7. **Verificaciones del mismo día (RDA-021):**
   1. Entra con tu contraseña correcta: panel sin 500. Con la sesión abierta, `/accounts/login/` te lleva al panel.
   2. Sube una imagen de referencia de menos de 5 MB a un pedido de prueba y otra de más de 5 MB: la primera se guarda; la segunda muestra el mensaje y no se guarda. **No** intentes restaurar archivos en producción.
   3. Registros desde el último `Starting uWSGI`, sin filtro por fecha (3.12 B, paso 6.3): `coincidencias desde el arranque: 0`. Cuéntalo **después** de C.

#### C. Medición de la dirección real (obligatoria, el mismo día, justo después de B; hazla cuando nadie más esté usando la aplicación)

Con `ACCESO_PROXIES_CONFIABLES` sin definir, la aplicación usa `REMOTE_ADDR`. Esta prueba dice si `REMOTE_ADDR` es tu conexión o la del proxy. Usa **un nombre de usuario que no exista** (por ejemplo `medicion-0408`), nunca tu cuenta real.

1. **Desde tu red (computador):** en `/accounts/login/`, `medicion-0408` con cualquier contraseña, **3 veces**. Al cuarto intento debe salir «Acceso bloqueado por 15 minutos». Si no sale, detente: el contador por conexión no está funcionando; avisa sin cambiar nada.
2. **Desde otra red (teléfono con datos móviles, wifi apagado):** entra a `/accounts/login/` con tu usuario y contraseña correctos.
   - **Entra:** `REMOTE_ADDR` es la dirección real de cada persona. Valor final: `ACCESO_PROXIES_CONFIABLES` sin definir (o `0`).
   - **Dice «Acceso bloqueado»:** `REMOTE_ADDR` es la del proxy, la misma para todos. Valor final: `ACCESO_PROXIES_CONFIABLES=1`.
   - Anota cuál de los dos pasó (es la evidencia que cierra la verificación 3 de la iteración).
3. **Valores finales en el `.env`:** cambia `ACCESO_FALLOS_POR_DIRECCION=3` por `ACCESO_FALLOS_POR_DIRECCION=20` y, solo si en C.2 saliste bloqueado, agrega `ACCESO_PROXIES_CONFIABLES=1`. Comprueba con `grep -E '^ACCESO_' .env`. **Resultado del 2026-11-21 (dicho):** en C.2 salió bloqueado, así que el `.env` final de producción lleva **ambas** variables: `ACCESO_FALLOS_POR_DIRECCION=20` y `ACCESO_PROXIES_CONFIABLES=1`. Consérvalas en los despliegues siguientes.
4. **Reload de ajuste** (uno, con `DESDE_CL` y 3.6; una línea `Starting uWSGI`). Borra además todos los contadores de la prueba.
5. **Comprobación** (solo si pusiste `ACCESO_PROXIES_CONFIABLES=1`): ~~repite C.1 con `medicion-0408` **20 veces** desde tu red (bloquea al intento 21) y luego C.2 desde el teléfono: **debe entrar**.~~ **Corregido el 2026-11-22:** desde tu red, 20 intentos, **cada uno con un nombre inexistente distinto** (`medicion-0408-01` a `medicion-0408-20`) y cualquier contraseña. El 20.º todavía dice «Credenciales incorrectas»; el 21.º, con otro nombre inexistente (`medicion-0408-21`), dice «Acceso bloqueado por 15 minutos». Luego C.2 desde el teléfono: **debe entrar**. Los nombres son distintos porque con un mismo nombre el bloqueo por usuario corta al 5.º fallo, antes de `authenticate()`, y los intentos bloqueados ya no suman al contador por dirección: nunca se llegaría a 20. (C.1 no tiene ese problema: 3 fallos con un nombre no alcanzan el límite de 5 por usuario.) Si sale bloqueado, `X-Forwarded-For` no trae lo esperado: pon `ACCESO_FALLOS_POR_DIRECCION=0`, Reload y avisa al agente. Tu red queda bloqueada 15 minutos: espera (sin otro Reload).
6. **Falsificación de la cabecera:** la prueba automatizada `FalsificacionTests` comprueba que cambiar lo que el cliente escribe a la izquierda de `X-Forwarded-For` no evita el bloqueo. **No se repite en producción** (enviar cabeceras propias exige un cliente HTTP con token CSRF); queda como diferencia anotada respecto de la verificación 3 (c) de la iteración.
7. Admin → Registro de eventos: hay eventos «Acceso bloqueado» de la medición (uno por bloqueo). Se quedan; se purgan con la retención de 365 días.

#### D. Retroceso

- **Si el bloqueo afecta a todos:** `ACCESO_FALLOS_POR_DIRECCION=0` en el `.env` y Reload. No hace falta volver el código ([desbloqueo-de-acceso](desbloqueo-de-acceso.md), punto 3).
- **Si hay que volver el código:** `retroceso.md`, caso 2 (rige también para Clase 1), a `v4.9-sanitizacion-html`. La `0009` es Clase 1 y MySQL no cambió: revertirla es **opcional**. Si lo haces, **antes** de volver el código: `python manage.py migrate pedidos 0008` (debe decir `Unapplying pedidos.0009_acceso_bloqueado... OK`). Después, checkout de `v4.9-sanitizacion-html` y Reload. Las variables `ACCESO_` pueden quedarse: el código anterior las ignora.
- Los eventos `acceso_bloqueado` ya escritos quedan en la tabla y el admin los muestra sin nombre legible del tipo. No dañan nada.
- **Si los datos se dañaran** (no se espera: la iteración no escribe datos de negocio): caso 3 con el respaldo de B.1.

### 3.16 Despliegue de la 04-09 (`v4.11-csp-observacion`): cabecera de observación

La 04-09 agrega `Content-Security-Policy-Report-Only` a todas las respuestas, **solo para observar**: no bloquea nada ([politica-de-contenido](politica-de-contenido.md)). Toca `settings.py` (un middleware, `CSP_OBSERVACION` y `SECURE_CSP_REPORT_ONLY`) y `.env.example`. **Sin migraciones, sin `pip` y sin `collectstatic`.** Va **antes** que la 14-04 (decisión del desarrollador, 2026-11-22). Retroceso: `v4.10-acceso-limites`.

#### A. Antes (en tu PC)

1. Revisión manual en la réplica: hecha (2026-11-27, dicha; iteración 04-09, «Ejecución y revisión manual»).
2. `python manage.py test pedidos` → `Ran 461 tests`, `OK (expected failures=3)`.

#### B. Orden del despliegue

1. **Respaldo de producción ANTES del checkout**, con `v4.10-acceso-limites` todavía activo, igual que en 3.13 B, paso 1: `VÁLIDO` (19 de 19), `RESULTADO: CUMPLE D2` y `0`. Anota el nombre, el tamaño y el SHA-256. Es el respaldo de rutina: no hay migración ni datos.
2. **Etiqueta** anotada `v4.11-csp-observacion` sobre el commit de la 04-09 y `git push` de la etiqueta (sección 1). Antes, en el PC, `git diff --stat v4.10-acceso-limites v4.11-csp-observacion` debe mostrar `PedidosApp/settings.py`, `.env.example`, `pedidos/tests/test_csp.py` y documentos. **No** debe mostrar `requirements.txt`, `pedidos/migrations/`, plantillas, `pedidos/static/` ni `views.py`.
3. **`.env` del servidor:** no hace falta agregar nada (`CSP_OBSERVACION` sin definir = activa). **Conserva** `ACCESO_PROXIES_CONFIABLES=1` y `ACCESO_FALLOS_POR_DIRECCION=20` (3.15 C.3); compruébalo con `grep -E '^ACCESO_' .env` → las dos líneas. Si falta `ACCESO_PROXIES_CONFIABLES=1`, 20 fallos de cualquiera bloquean a todos: agrégala antes del Reload. Comprueba también que no haya un `CSP_OBSERVACION=False` olvidado: `grep -c '^CSP_OBSERVACION' .env` → `0`.
4. **Checkout** (3.2), en una consola con el entorno virtual activo (3.15 B.5): `git fetch origin --tags`, `git checkout v4.11-csp-observacion` y `git describe` → `v4.11-csp-observacion`.
5. **Revisión, antes del Reload:** `python manage.py migrate --plan` → `No planned migration operations.`; `python manage.py check --deploy` → solo W005 y W021 (la política no agrega advertencias). Si sale otra cosa, no recargues.
6. **UN solo Reload**, con `DESDE_CL` calculado, mostrado y validado en la misma consola justo antes (3.14 B, paso 6) y confirmado con «Detectar reinicios de uWSGI» (3.6): **una** línea `Starting uWSGI`. Anota su hora.
7. **Verificaciones del mismo día (RDA-021):**
   1. Abre `/accounts/login/` con `F12`, pestaña **Red**: la respuesta del documento trae `Content-Security-Policy-Report-Only` (confirma que el proxy de PythonAnywhere no la quita) y **no** trae `Content-Security-Policy`. Anota si trae también `Strict-Transport-Security` y `X-Frame-Options: DENY`.
   2. Entra y abre el panel: en la consola aparecen mensajes `[Report Only]`; el sitio se ve y funciona igual (estilos, editor, selectores).
   3. Registros desde el último `Starting uWSGI`, sin filtro por fecha (3.12 B, paso 6.3): `coincidencias desde el arranque: 0`. Cuéntalo **después** de usar las pantallas y anota la hora del conteo.

#### C. Retroceso

- **Por variable (sin tocar el código):** `CSP_OBSERVACION=False` en el `.env` y **un** Reload; confirma en la pestaña Red que la cabecera desapareció ([politica-de-contenido](politica-de-contenido.md)). No deja memoria en el navegador: rige desde la siguiente carga.
- **Por etiqueta:** `retroceso.md`, caso 1 (sin migraciones): checkout de `v4.10-acceso-limites` y Reload. Las variables `ACCESO_` se quedan.
- No hay datos que deshacer.

## 4. Primer uso: despliegue de la 00-04 (`v0.1-higiene`)

El paso a paso exacto, con las salidas que hay que anotar, está en `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-05.md`, parte B. Resume lo propio de este despliegue (punto 8 de la lista):

1. **[PC · PowerShell 7]** Crear y publicar `v0.0-inicial` sobre el commit que está en producción (anotado en el paso 3.1), **antes de tocar nada más en el servidor**, para que el retroceso ya tenga destino.
2. **[PA · Bash]** Contar los archivos de `media/` y `media/pedidos/`, y comprobar que existe la captura.
3. **[PA · Bash]** Con un conteo, comprobar que ningún pedido referencia `pedidos/Captura_de_pantalla_2026-01-20_152121.jpg`. El commit `965227d` saca esa imagen del índice y el `checkout` la borra del disco del servidor. Si el conteo es mayor que 0, copia la imagen fuera del repositorio antes del `checkout`.
4. **[PA · Bash o Files]** Confirmar que el `.env` del servidor tiene `DATABASE_URL` y agregar `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com` **antes** de recargar. Sin esa variable el sitio responde 400.

## 5. Registro de despliegues

| Fecha (hora de Chile) | Etiqueta | Commit | Iteración | Respaldo previo (SHA-256, 12 primeros) | Resultado |
| :-------------------- | :------- | :----- | :-------- | :------------------------------------- | :-------- |
| 2026-10-23 00:26 | `v0.1-higiene` | `64655f8` | 00-04 (primer uso del protocolo; partida `v0.0-inicial`, `2442f3b`) | `90765c548e5c` | Correcto, sin retroceso: panel, listado y detalle de pedido; sin errores después de la recarga |
| 2026-10-23 18:35 | `v0.2-correcciones` | `7944943` | 00-06 (partida `v0.1-higiene`, `64655f8`) | No aplica (sin cambios de datos ni de esquema; evidencia-00-06) | Correcto, sin retroceso: una sola línea nueva en el registro, `Not Found: /favicon.ico` (hallazgo menor registrado) |
| 2026-10-25 21:26 | `v1.1-observabilidad` | `d6768d0` | 01-01 a 01-05, 01-07 y el bloque de pruebas de 02-01 (partida `v0.2-correcciones`); migración 0007, Clase 2, en 2,659 s | `f3163addfce2` | Correcto, sin retroceso: acceso, panel, listado y detalle; error controlado diagnosticado en unos 2 minutos en `server.log`. Hallazgo: cada error queda en `server.log` y en `error.log` (opción A). Parte D pendiente (2026-11-01) |
| 2026-11-04 00:11 (recarga a las 00:11:49, hora oficial: la de `Starting uWSGI` en el registro; el desarrollador la había informado a las 00:14:00, 2 min 11 s posterior) | `v1.2-capturas` | `81005df` | 01-09, 01-08 y 01-07 reabierta (partida `v1.1-observabilidad`, `d6768d0`); sin migraciones, `pip` ni `collectstatic` | `600993c55d75…` (`respaldo_03-11-2026_22-34-09.sql`, 19 de 19) | Correcto, sin retroceso. E1: acceso, panel, listado y detalle sin problemas. E2: respaldo por el camino normal a las 00:12:37 (nombre; `INFO` en `server.log` a las 00:12:39, posterior al reinicio), 19 de 19, `VÁLIDO`, descargado. E3 desde 00:11:49: 1 `ERROR` (`root`, `OSError: write error`, ruido conocido, AUD-04-004) y 1 `INFO`, con los emojis 🔴 y 🔵 de `v1.2`. Incidente previo, a las 23:41 del 2026-11-03: `git checkout main` por error en el servidor, restaurado hacia las 00:09 sin `git pull` ni reinicios de uWSGI (evidencia-01-09, parte D) |
| 2026-11-04 01:32 (reinicio efectivo a las 01:32:51; orden de Reload recibida a las 01:32:45) | `v0.3-doble-envio` | `5dc82a8` | 00-07 (partida `v1.2-capturas`); sin migraciones, `pip` ni `collectstatic` | No aplica: no toca datos ni esquema; el último verificado es `respaldo_04-11-2026_00-12-37.sql` (`348f44c3eb91…`, 19 de 19) | Correcto, sin retroceso. Acceso, panel, listado, detalle, «Nuevo pedido» y «Editar pedido» abren y muestran el cambio (sin enviar formularios); 0 líneas con `nivel=` desde el reinicio. Pruebas y `check --deploy` no se repitieron: el código es idéntico al de `bd07f21`, donde corrieron el mismo día. Falta la medición de `access.log` del 2026-11-11 (evidencia-00-07, parte D). **Nota 2026-11-17:** no se hizo ese día; se midió el 2026-11-16 y cumple (evidencia-00-07, parte D) |
| 2026-11-16 23:48 (reinicio efectivo a las 23:48:12, hora de Chile; 2026-11-17 02:48:12 UTC) | `v3.1-integridad` | `7e14398` | 03-01 a 03-05 (las cuatro iteraciones de la Fase 3 en una etiqueta; partida y retroceso `v0.3-doble-envio`, `5dc82a8`); sin migraciones ni `pip`, con `collectstatic` (1 archivo, `index.js`) | `74e6e2a352d6…` (`respaldo_16-11-2026_23-34-18.sql`, 19 de 19) | Día 0 correcto, sin retroceso; ~~la vigilancia sigue hasta el día 7 (desde el 2026-11-23 a las 23:48:12)~~ (superado el 2026-11-18, ver la nota al final de la fila). Pruebas previas: 267, `OK (expected failures=9)`. C1: sin 500 y `token_envio` en las tres pantallas. C2: botón bloqueado con «Guardando…» en ventana privada (el caché no se probó). C4 a las 23:58:23: línea `INFO` «Envío sin token válido» verificada y ningún pago creado. Desde `R`: 1 `ERROR` (`root`, `OSError: write error`, 23:55:10, AUD-04-004) y 1 `INFO`; ningún `POST /pedidos/nuevo/`. Desviaciones: despliegue un día antes de lo reprogramado, `R` fuera de las 20:00 a 23:00 (decisión del desarrollador) y aviso con las 22:30. Hallazgo nuevo: AUD-05-009 (idéntico en `v0.3-doble-envio`: no es regresión). Datos dichos por el desarrollador (evidencia-03-05, partes A a C). **Nota 2026-11-18 (RDA-021):** se canceló la lectura del día 7; lectura anticipada hasta el 2026-11-18 17:22 UTC (38 h 34 min): sin `ERROR` nuevo salvo el `OSError` ya clasificado y sin `5xx`; no cumple el tiempo de `/pagos/ingresar/` (de 2,7 a 8,0 s en las pruebas del día 0; AUD-05-011) ni «nadie reporta un “no se guardó”» (AUD-05-010); ambos son defectos anteriores, iguales en `v0.3-doble-envio` (dicho por el desarrollador); sin retroceso. 03-05 y Épica 03 Terminadas el 2026-11-18 (evidencia-03-05, partes D y F) |
| 2026-11-18 ~19:30 (hora del Reload dicha por el desarrollador; la de `Starting uWSGI` no se informó) | `v14.1-pagos` | no informado | 14-01 (arreglo urgente de pagos, AUD-05-010 y AUD-05-011; partida y retroceso `v3.1-integridad`, `7e14398`); sin migraciones, `pip` ni `collectstatic` | No aplica (no toca datos ni esquema); el último verificado es `respaldo_18-11-2026_14-26-45.sql` (19 de 19, dicho) | Día 0 correcto, sin retroceso (dicho por el desarrollador): pedido de prueba, pago de $1.000 guardado y pedido borrado (opción A); la edición del pedido funcionó y el selector de «Ingresar pago» carga muy rápido; después, el cliente registró pagos sin problemas. **No verificado:** `error.log` y `server.log` desde el Reload y tiempos medidos de `/pagos/ingresar/`. Pruebas previas: 273, `OK (expected failures=9)` (en local). Desde aquí, el destino de retroceso del despliegue siguiente es `v14.1-pagos` |
| 2026-11-18 ~22:16 (Reload a las 22:16:26 y uWSGI arriba a las 22:16:31, según `server.log`; 2026-11-19 01:16 UTC) | `v4.1-mutaciones-post` | no informado (el commit de la 04-01 en `main` es `39a9bb8`; no se verificó que sea el de la etiqueta) | 04-01 (mutaciones solo por POST; partida y retroceso `v14.1-pagos`); sin migraciones ni `pip`, **con `collectstatic`** (`index.js`) y Ctrl+F5 del cliente | No aplica (no toca datos ni esquema) | Día 0 correcto, sin retroceso (dicho por el desarrollador): con pedidos de prueba, borrados después, funcionaron cambiar estado, «Reabrir Pedido», eliminar pago con confirmación y el respaldo desde la web (descarga completa y sin recarga). Registros pegados: `server.log` sin errores desde el Reload, con solo un `INFO` «Respaldo antiguo eliminado» a las 22:25; `error.log` sin errores desde las 01:16 UTC. Dos `OSError: write error` anteriores al despliegue (AUD-04-004). Pruebas previas: 282, `OK (expected failures=4)` (en local). Hallazgos nuevos: AUD-05-012 a AUD-05-014. **Desde aquí, el destino de retroceso del despliegue siguiente es `v4.1-mutaciones-post`**, con `collectstatic` si el cambio incluye estáticos |
| 2026-11-19 ~00:18 (uWSGI arriba a las 00:17:15; 03:17 UTC) | `v4.2-confirmar-eliminar-pedido` | `3442a5e` | 04-10 (confirmación reforzada al eliminar un pedido con pagos; partida y retroceso `v4.1-mutaciones-post`); sin migraciones, `pip` ni `collectstatic` (`git diff --stat` de `requirements.txt`, migraciones, `settings.py` y estáticos vacío); checkout confirmado con `git describe` | `225c3b30…1747` (`respaldo_19-11-2026_00-09-05.sql`, `VÁLIDO`, 19 de 19) | Correcto, sin retroceso. Día 0 (dicho por el desarrollador): aviso con cifras en un pedido real con pagos, sin enviar; dos pedidos de prueba borrados, con y sin pagos, con eventos correctos. `error.log` pegado sin errores desde el Reload (último `OSError`, anterior: 2026-11-18 18:40:18 UTC). Pruebas previas: 298, `OK (expected failures=4)` (en local). Hallazgos nuevos: AUD-05-015 y AUD-05-016. **Desde aquí, el destino de retroceso del despliegue siguiente es `v4.2-confirmar-eliminar-pedido`** |
| 2026-11-19 01:32 (Reload a las 01:32:05, uWSGI arriba a las 01:32:12 y listo a las 01:32:39, según `server.log`; el desarrollador no informó la hora) | `v14.2-duplicar-items` | `068be10` | 14-02 (Reabrir Pedido copia los ítems y pide la fecha de entrega, AUD-05-012; partida y retroceso `v4.2-confirmar-eliminar-pedido`); sin migraciones, `pip` ni `collectstatic` (`git diff --stat` de `requirements.txt`, migraciones, `settings.py` y estáticos vacío); checkout confirmado con `git describe` | `e13a10a0…022bd` (`respaldo_19-11-2026_01-29-31.sql`, `VÁLIDO`, 19 de 19) | Correcto, sin retroceso. Día 0 (dicho por el desarrollador, pedidos de prueba ya borrados): fecha vacía al abrir, la de hoy rechazada, con fecha desde mañana el nuevo trae los dos ítems con sus precios, el mismo total, sin pagos y el autor correcto. Un solo evento «Pedido duplicado» solo con identificadores (captura). `error.log` y `server.log` pegados sin errores nuevos desde el Reload. Pruebas previas: 316, `OK (expected failures=4)` (en local). Hallazgos nuevos: AUD-05-017 a AUD-05-019. **Desde aquí, el destino de retroceso del despliegue siguiente es `v14.2-duplicar-items`** |
| 2026-11-19 11:24 (uWSGI reinicia a las 11:23:50 y queda listo a las 11:24:07, según `server.log`; se había dicho 11:25, vale el registro) | `v4.3-configuracion-produccion` | `c62a92e` | 04-02, escalón 1 (HSTS 3600, cookies seguras, `SECURE_SSL_REDIRECT`, `CSRF_TRUSTED_ORIGINS`, arranque que falla; partida y retroceso `v14.2-duplicar-items`); sin migraciones, `pip` ni `collectstatic` (`git diff` solo con `settings.py`, +38); `.env` editado antes del código (`SEGURIDAD_PRODUCCION=True`, `CSRF_TRUSTED_ORIGINS`) | `d239d9dd…898a` (`respaldo_19-11-2026_11-13-02.sql`, `VÁLIDO`, 19 de 19) | Correcto, sin retroceso. `check --deploy` con el código nuevo antes del Reload: solo W005 y W021 (no se repitió después). «Force HTTPS» activo (dicho). `curl.exe` a las 11:26: HTTP 302 a `https://` (del proxy), HTTPS 200 sin bucle con `max-age=3600` y `csrftoken` `Secure`. Ventana privada sin 403 en pedido, pago, respaldo y «Reabrir Pedido» (dicho); sin «csrf» ni «forbidden» en `server.log` ni `error.log`. **No verificado:** `sessionid` `Secure` en el navegador. Pruebas previas: 327, `OK (expected failures=4)` (en local). **Desde aquí, el destino de retroceso del despliegue siguiente (`v4.4-hsts-semana`) es `v4.3-configuracion-produccion`** |
| 2026-11-19 12:10 («Starting» a las 12:10:01 y listo a las 12:10:08, según `server.log`; se citó 11:25, que es la hora del escalón 1: vale el registro) | `v4.4-hsts-semana` | `854cd74` | 04-02, escalón 2 (HSTS 604800; partida y retroceso `v4.3-configuracion-produccion`); sin migraciones, `pip` ni `collectstatic` (`git diff` de `v4.3` a `v4.4`: `settings.py`, la prueba y documentos); `.env` sin cambios; `git describe` en el servidor da `v4.4-hsts-semana` | `b7d320f6…ba11c` (`respaldo_19-11-2026_12-07-14.sql`, `VÁLIDO`, 19 de 19, 1.542.750 bytes) | Correcto, sin retroceso. `check --deploy` después del Reload: solo W005 y W021 (esperadas, sin silenciar). `curl.exe` (15:13 UTC): HTTPS 200 con `max-age=604800` y `csrftoken` `Secure`; HTTP 302 a HTTPS y luego 200, sin bucle. DevTools (captura): `sessionid` HttpOnly, Secure, Lax; `csrftoken` Secure, Lax. Ventana privada sin 403 (dicho); sin «csrf» ni «forbidden» en los registros. Hallazgo nuevo: AUD-05-020 (cookies `_ga` de un dominio de Tailwind). **HSTS de una semana ya emitido: un retroceso no lo borra de los navegadores hasta 7 días.** Pruebas previas: 327, `OK (expected failures=4)` (en local). **Desde aquí, el destino de retroceso del despliegue siguiente es `v4.4-hsts-semana`** |
| 2026-11-19 14:11 («Starting uWSGI» a las 14:11:27, hora de Chile; 17:11:24 UTC, según `server.log`; se dijo 14:12, vale el registro) | `v4.5-credenciales` | `81e0ebf` | 04-03 (contraseña de MySQL en un archivo temporal de opciones y `SECRET_KEY` obligatoria; partida y retroceso `v4.4-hsts-semana`); sin migraciones, `pip` ni `collectstatic` (diff `v4.4…v4.5`: código solo `utils.py` y `settings.py`); `.env.example` editado por el desarrollador en `81e0ebf` | `0d93d4eb…9740` (`respaldo_19-11-2026_14-06-52.sql`, `VÁLIDO`, 19 de 19, 1.545.575 bytes) | Correcto, sin retroceso. **Antes:** clave de producción con largo 61, 25 distintos y sin `django-insecure-`; ensayo en la réplica `CUMPLE` (4999 filas antes y después, 0 procesos con contraseña, 0 residuales); `git describe` = `v4.5-credenciales`; `check --deploy` a las 14:10, solo W005 y W021. **Después:** `check --deploy` solo W005 y W021; respaldo desde la web a las 14:13 (`respaldo_19-11-2026_14-13-28.sql`, `VÁLIDO`, 19 de 19, 1.545.818 bytes, `6a5af0bb…df87`; descarga dicha); `server.log` y `error.log` sin `mysqldump`, `mysql_opciones`, `Traceback` ni `OSError` del 2026-11-19; `ls /tmp/mysql_opciones_*` en la consola → 0 (no mide el `/tmp` del worker). **No verificado:** permisos del archivo temporal. Restauración en producción no probada por diseño (la cubre el ensayo). Pruebas previas: 342, `OK (expected failures=4)` (en local). **Desde aquí, el destino de retroceso del despliegue siguiente es `v4.5-credenciales`** |
| 2026-11-19 17:22 (checkout a las 20:21 UTC; arranques de uWSGI a las 17:22:49, 17:29:34 y 17:41:57, hora de Chile, según `server.log`: los tres son Reloads pulsados por el desarrollador, que repitió el Reload creyendo que los anteriores no se habían ejecutado (dicho); ninguno de origen desconocido) | `v4.6-restauracion` | `58d7c3d` | 04-04 (restauración endurecida: tope de 20 MB, estructura D2, `RESTAURAR`, constancia en `server.log`, `emergencia_` fuera de la rotación, sin `.sql` vacío ni subida huérfana; partida y retroceso `v4.5-credenciales`); sin migraciones, `pip` ni `collectstatic` (diff `v4.5…v4.6`: código solo `utils.py`, `views.py`, `restaurar_bd.html` y `respaldar_bd.html`; sin `requirements.txt`, migraciones ni estáticos) | **Último respaldo con `v4.5`:** `respaldo_19-11-2026_14-13-28.sql` (`6a5af0bb…df87`, `VÁLIDO`, `CUMPLE D2`). **Salvedad:** `respaldo_19-11-2026_17-40-30.sql` (`457a9e8a…998b`, `VÁLIDO`, `CUMPLE D2`, 1.547.705 bytes) se generó con `v4.6` ya activo (después del Reload de las 17:22:49): **no es un respaldo previo con el código anterior** | Correcto, sin retroceso. **Antes:** D2 `CUMPLE` sobre la réplica y sobre `respaldo_19-11-2026_14-13-28.sql`; ensayo en la réplica `CUMPLE` (restauración 6,2 s; inválido y sin `RESTAURAR` rechazados; 1 `emergencia_` con D2; subida borrada; 4999 → 5000 filas, solo eventos +1; 0 contraseñas en argumentos; 0 residuales); pantalla en escritorio y a 360 px revisada (dicho); `git describe` = `v4.6-restauracion`; `check --deploy` solo W005 y W021; `emergencia_` en `backups/`: 0. **Después:** `check --deploy` solo W005 y W021; `vacio.sql` (0 bytes) con `RESTAURAR` rechazado con el mensaje fijo (dicho), `emergencia_` sigue en 0 y sin «Restauración» en `server.log`; respaldo desde la web `respaldo_19-11-2026_17-48-17.sql` (`b804277d…b622`, `VÁLIDO`, 19 de 19, `CUMPLE D2`, 1.547.831 bytes); registros del día sin `Traceback`, `OSError`, `mysqldump` ni `mysql_opciones`; `/tmp/mysql_opciones_*` → 0 (consola, no el `/tmp` del worker). Sin restauración real en producción, por diseño. Pruebas previas: 375, `OK (expected failures=4)` (en local). **Desde aquí, el destino de retroceso del despliegue siguiente (`v4.7-correcciones-config`) es `v4.6-restauracion`** |
| 2026-11-19 23:06 (checkout a las 02:06 UTC del 2026-11-20; un solo arranque de uWSGI a las 23:06:46, hora de Chile, 02:06:44 UTC, según `server.log`: Reload del desarrollador (dicho); el arranque anterior fue el de las 17:41:57) | `v4.7-correcciones-config` | `7187d03` | 04-05 (correcciones de configuración: `django.conf.settings` en `views.py`, `conn_health_checks=True` con `conn_max_age=60`, `BASE_DIR` una vez, `DIRS` vacío, importaciones; partida y retroceso `v4.6-restauracion`); sin migraciones, `pip` ni `collectstatic` (diff `v4.6…v4.7`: código solo `settings.py`, `views.py` y `urls.py`; sin `requirements.txt`, migraciones ni estáticos) | `607db45f…9b8a` (`respaldo_19-11-2026_23-00-20.sql`, `VÁLIDO`, 19 de 19, `CUMPLE D2`, 1.549.306 bytes; tomado con `v4.6` activo, **antes del checkout**) | Correcto, sin retroceso. **Antes:** réplica con 379 pruebas, `OK (expected failures=4)`; `backups/` real con 1 archivo antes y después; paridad sin diferencias no aceptadas; pantallas en escritorio y a 360 px (dicho); `check --deploy` tras el checkout, solo W005 y W021. **Después:** `check --deploy` (02:15 UTC) solo W005 y W021; panel, listas, detalle y PDF sin 500 (dicho); `error.log` sin errores nuevos tras el Reload (3 coincidencias históricas de `TemplateDoesNotExist`, del 2026-10-26, anteriores a la 04-01; último `OSError` el 2026-11-18 18:40:18, ninguno el 2026-11-19). **Lección:** el `grep` por fecha no detecta trazas y `DESDE_CL` quedó sin definir; 3.12 B, paso 6.3, corregido. Hibernación: observación posterior (AUD-01-016). Pruebas previas: 379, `OK (expected failures=4)` (en local). **Desde aquí, el destino de retroceso del despliegue siguiente (`v4.8-historial-clientes`) es `v4.7-correcciones-config`** |
| 2026-11-20 10:22 (un solo arranque de uWSGI a las 10:22:07, hora de Chile, único hasta las 10:54 según `server.log`; Reload del desarrollador) | `v4.8-historial-clientes` | `8f4e396` | 04-06 (protección del historial: `Pedido.cliente` y `Cotizacion.cliente` a `PROTECT`, rechazo con mensaje en `eliminar_cliente`, advertencia en la confirmación; script D2 versionado como excepción a «un despliegue, un propósito»; partida y retroceso `v4.7-correcciones-config`); **con migración `0008`, Clase 1** (`sqlmigrate`: `(no-op)`), sin `pip` ni `collectstatic` | `524c32fc27ef…09fe` (`respaldo_20-11-2026_10-16-37.sql`, 1.549.877 bytes, 19 de 19, `CUMPLE D2`; tomado con `v4.7` activo, **antes del checkout**: rotación en `error.log` a las 10:16:41, `git describe --tags` = `v4.7-correcciones-config` a las 10:20, checkout a las 10:21, visto en consola) | Correcto, sin retroceso. **Antes:** `migrate --plan` solo `0008`; `check --deploy` solo W005 y W021. `migrate` OK, `[X] 0008`. **Después:** conteo de `Traceback`, `OperationalError`, «gone away» y `TemplateDoesNotExist` desde el arranque: 0 (a las 10:27, **antes** del uso en navegador). **Réplica (3.13 A, consola):** `SHOW CREATE TABLE` con el mismo SHA-256 antes y después (`0830026E…7E3F`, 2324 bytes), conteos 824, 992, 999, 1198, 33 y 65 (clientes 825 → 824 por un borrado accidental); pruebas A a D en escritorio y 360 px, dichas. Producción: panel y `/clientes/lista/` sin 500 y confirmación de un cliente con pedidos con la advertencia, sin pulsar eliminar (dicho por el desarrollador); **sin conteo de errores posterior al uso**. Pruebas previas: 388, `OK (expected failures=3)` (en local). **Desde aquí, el destino de retroceso del despliegue siguiente es `v4.8-historial-clientes`** (previo `v4.7-correcciones-config`; `migrate pedidos 0007` opcional, caso 2) |
| 2026-11-20 17:27 (un solo arranque de uWSGI, «Starting uWSGI» a las 17:27:05, hora de Chile; seguía siendo el último a las 17:31; checkout a las 20:23 UTC, 17:23 hora de Chile) | `v4.9-sanitizacion-html` | `6b79f63` | 04-07 (sanitización del HTML enriquecido con `nh3` al guardar y al mostrar, RDA-020, AUD-03-001, y guardia de SQL; partida y retroceso `v4.8-historial-clientes`); **con `pip`** (`nh3==0.3.8`, ya instalado), sin migraciones ni `collectstatic` (diff `v4.8…v4.9` sin migraciones, `settings.py`, `views.py` ni estáticos). Procedimiento: 3.14 | `D217AAE663C8…ED10F` (`respaldo_20-11-2026_17-19-15.sql`, 1.553.051 bytes, 19 de 19, `CUMPLE D2`, código 0; tomado con `v4.8` activo, **antes del checkout**: rotación en `error.log` a las 20:19:17 UTC, checkout a las 20:23 UTC) | Correcto, sin retroceso. **Consola, antes del Reload:** checkout limpio desde `v4.8`; `pip install -r`: 22 líneas `Requirement already satisfied`; `nh3` 0.3.8; `nh3.clean` → `<p>a</p>`; `pip freeze` = `requirements.txt` = 22; `migrate --plan` sin operaciones; `check --deploy` solo W005 y W021. **Consola, después:** conteo de `Traceback`, `OperationalError`, «gone away» y `TemplateDoesNotExist` desde el arranque, **después del uso**: 0; `error.log` sin entradas posteriores al arranque. **Dicho por el desarrollador:** detalle de pedido, cotización y producto con formato, guardado sin cambios de un producto o pedido fuera de los 15, y PDF de cotización, sin 500. **No consta:** copia de las imágenes de los pedidos 46 y 56; `DESDE_CL` no se mostró ni validó (el filtro funcionó; paso 6 corregido). **Observación sin causa conocida:** en el `tail` de `error.log` apareció repetida una línea antigua (2026-10-24 15:36:18,282) dentro del bloque del 2026-10-23; no se interpreta. Pruebas previas: 411, `OK (expected failures=3)` (en local). **Desde aquí, el destino de retroceso del despliegue siguiente es `v4.9-sanitizacion-html`** (previo `v4.8-historial-clientes`) |
| 2026-11-21 23:18 (Reload de despliegue: un solo «Starting uWSGI» a las 23:18:55; Reload de ajuste: uno solo a las 23:36:31; hora de Chile) | `v4.10-acceso-limites` | `c995647` | 04-08 (protección del acceso y límites de entrada, AUD-03-004; partida y retroceso `v4.9-sanitizacion-html`); **con migración `0009_acceso_bloqueado`, Clase 1** (`-- (no-op)`), sin `pip` ni `collectstatic` (diff sin `requirements.txt`, `views.py` ni estáticos); `.env` con `ACCESO_FALLOS_POR_DIRECCION=3` para medir y luego valores finales (3.15 C) | `0543243735D7…35B5` (`respaldo_21-11-2026_22-54-42.sql`, 1.557.435 bytes, 19 de 19, `CUMPLE D2`, código 0; tomado con `v4.9` activo, **antes del checkout**) | Correcto, sin retroceso. **Consola:** `migrate --plan` solo `0009`; `check --deploy` solo W005 y W021; `migrate` OK, `[X] 0009`; errores desde las 23:18: 0, contados a las 23:53 (02:53 UTC), antes del acceso de las 00:00:58; `error.log` sin entradas nuevas. **Incidente sin efecto:** a las 23:12, checkout en una consola sin el entorno virtual → `ModuleNotFoundError`; se volvió a `v4.9` sin migrar ni recargar (3.15 B.5 corregido); el segundo checkout (02:17 UTC) se hizo con el entorno activo: prompt «(venv)», `which python` al entorno virtual y «modulos OK» (consola). **Pantalla:** 2 «Acceso bloqueado» por dirección (23:30:03 y 23:40:29), 23 «Acceso fallido» de usuario desconocido (3 + 20), accesos exitosos a las 23:41:13 y 00:00:58. **Dicho:** C.2 bloqueado desde el teléfono → `REMOTE_ADDR` es la del proxy; valores finales `ACCESO_FALLOS_POR_DIRECCION=20` y `ACCESO_PROXIES_CONFIABLES=1`; en C.5 el 21.º intento bloqueado y el teléfono entró durante ese bloqueo; imagen de más de 5 MB rechazada; redirección sin 500. **No consta:** falsificar `X-Forwarded-For` en producción (solo la prueba automatizada) ni si PythonAnywhere corta la conexión con un cuerpo grande sin leer. Pruebas previas: 446, `OK (expected failures=3)` (en local). **Desde aquí, el destino de retroceso del despliegue siguiente es `v4.10-acceso-limites`** (previo `v4.9-sanitizacion-html`; `migrate pedidos 0008` opcional, caso 2) |
| 2026-11-27 10:54 (un solo «Starting uWSGI» a las 10:54:00, hora de Chile; checkout a las 13:52 UTC, 10:52 hora de Chile) | `v4.11-csp-observacion` | `37527b9` | 04-09 (política de contenido en observación: `Content-Security-Policy-Report-Only` con 9 directivas, interruptor `CSP_OBSERVACION`; partida y retroceso `v4.10-acceso-limites`); sin migraciones, `pip` ni `collectstatic`. Procedimiento: 3.16 | Respaldo de rutina con `v4.10` activo: ~~nombre, tamaño y SHA-256 **no constan**~~ **(precisado el 2026-11-27)** `respaldo_27-11-2026_10-51-07.sql`, 1.585.017 bytes, SHA-256 `2126d253bace` (consola, al refrescar la réplica; que sea el de este despliegue es inferido: el nombre coincide con la rotación de las 10:51:08 y precede al checkout de las 10:52); `VÁLIDO`, 19 de 19, `CUMPLE D2`, código 0 (dicho). Rotación en `error.log` a las 13:51:08 UTC (10:51:08), checkout a las 13:52 UTC (consola): que el respaldo fue anterior al checkout es inferido | Correcto, sin retroceso. **Consola, antes:** `HEAD` en `v4.10-acceso-limites` (`c995647`), árbol limpio; `.env` con `ACCESO_FALLOS_POR_DIRECCION=20`, `ACCESO_PROXIES_CONFIABLES=1` y 0 líneas `CSP_OBSERVACION`; checkout de `v4.11-csp-observacion` = `37527b9`, árbol limpio; `migrate --plan` sin operaciones; `check --deploy` solo W005 y W021; `DESDE_CL` válido. **Consola, después:** conteo de errores a las 11:01:36: 0 coincidencias; `error.log` sin entradas posteriores al arranque. **Pantalla (captura):** `/accounts/login/` 200 con `Content-Security-Policy-Report-Only` y las 9 directivas (`Date` 13:59:41 GMT); `Content-Security-Policy` ausente (inferido por el orden alfabético de Chrome). **Dicho:** sitio igual y mensajes `[Report Only]` en la consola. **No consta:** `Strict-Transport-Security` y `X-Frame-Options` en producción; si el conteo fue después de usar las pantallas. Pruebas previas: 461, `OK (expected failures=3)` (en local). **Desde aquí, el destino de retroceso del despliegue siguiente (14-04) es `v4.11-csp-observacion`** (previo `v4.10-acceso-limites`) |