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
- Advertencias medidas el 2026-10-21 (00-05): `W004` (HSTS), `W008` (redirección a HTTPS), `W009` (clave secreta), `W012` (cookie de sesión segura) y `W016` (cookie CSRF segura). Se corrigen en 04-02 y 04-03. Si aparece una advertencia que no está en esta lista o un error (`ERRORS:`), detente y revísala antes de desplegar.
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

### 3.8 Cierre

- Anota en la evidencia de la iteración: etiqueta desplegada, commit, lista de comprobación, resultado de las pantallas y del registro.
- Vuelve a la terminal de tu PC y deja el `.venv` y Docker como estaban.

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
