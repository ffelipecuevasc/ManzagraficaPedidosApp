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

**Estado (2026-11-19): implementada, pendiente de ensayo y despliegue. El ensayo está pendiente de ejecutar por el desarrollador.** El script puente vive fuera del repo: `C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-03\puente_ensayo_04_03.py`. Detalle en `bitacora-04-03.md`; excepción en `replica-local.md`, sección 8.

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
| **Implementada, pendiente de ensayo y despliegue** (ensayo pendiente de ejecutar por el desarrollador, 3.10; sin fecha fija; se despliega el día en que quede ensayada, con verificación el mismo día, RDA-021) | `v4.5-credenciales` (prevista) | por fijar | 04-03 (contraseña de MySQL en un archivo temporal de opciones y `SECRET_KEY` obligatoria; partida y retroceso `v4.4-hsts-semana`); sin migraciones, `pip` ni `collectstatic`; cambia `settings.py` y `utils.py` | Pendiente: obligatorio, normal (cambia cómo se generan y restauran los respaldos) | Pendiente. **Antes:** ensayo en la réplica (04-03, paso 5), medición de la clave del `.env` del servidor (3.1 bis) y `check --deploy` tras el checkout sin `ImproperlyConfigured`. **Después del Reload:** arranca; `check --deploy` solo W005 y W021; un respaldo desde la web se descarga completo y sale `VÁLIDO`; `server.log` sin errores de `mysqldump`; `ls /tmp/mysql_opciones_* 2>/dev/null \| wc -l` → `0`. **Retroceso:** `retroceso.md`, caso 1, a `v4.4-hsts-semana`; si solo falla el arranque por la clave, se corrige el `.env` y se recarga |
