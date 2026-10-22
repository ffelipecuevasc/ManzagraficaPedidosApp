# Evidencia 00-04 · Higiene del repositorio

- **Fecha del pedido:** 2026-10-21
- **Pedido por:** Claude Code (Opus 5.5)
- **Criterios que dependen de esta evidencia:** `git ls-files` sin `.idea/`, sin `.sql` fuera de `scripts/` y sin `.env`; `check` y `runserver` contra la réplica; `ALLOWED_HOSTS` en local; sitio publicado después del despliegue.

> Este archivo existe solo porque el agente no pudo obtener estos datos por su cuenta. Responde solo lo que se pide.

## Qué intentó el agente

| Dato | Qué intentó en local | Por qué se necesita al desarrollador |
| :--- | :------------------- | :----------------------------------- |
| Sacar `.idea/` y la imagen de `media/` del índice | Preparó el comando y comprobó con `git check-ignore -v` que quedan ignorados. | `git rm --cached` modifica el índice: lo hace solo el desarrollador (`AGENTS.md`, sección 6). |
| `runserver` contra la réplica | Probó `settings.py` en 11 procesos aislados, sin leer `.env` y con valores falsos (ver bitácora). | Conectarse a la réplica requiere la contraseña del `.env`, que el agente no lee. |
| Sitio publicado | Nada. | Es producción. |

## Qué necesito del desarrollador

Todo en PowerShell 7, desde la raíz del repositorio y con el `.venv` activo.

### 1. Sacar del índice `.idea/` y la imagen de `media/`

- **Para qué:** primer criterio (AUD-01-023).
- **Cómo obtenerlo:** los archivos siguen en el disco; solo dejan de versionarse.

  ```powershell
  git rm -r --cached .idea
  git rm --cached "media/pedidos/Captura_de_pantalla_2026-01-20_152121.jpg"
  git ls-files .idea media
  git ls-files | Select-String -Pattern '\.sql$', '(^|/)\.env'
  ```

  `git ls-files .idea media` no debe mostrar nada. La última línea solo debe mostrar `scripts/diagnostico/linea_base.sql` y `.env.example` (este último aparece después de que lo agregues al commit).
- **Respuesta:** la salida de las dos últimas líneas.

### 2. `check` y `runserver` contra la réplica, sin tocar `settings.py`

- **Para qué:** criterios de `check`, `runserver` contra la réplica y `ALLOWED_HOSTS` en local (AUD-02-022).
- **Antes:** confirma que tu `.env` tiene `DB_PASSWORD` y **no** tiene `ALLOWED_HOSTS` ni `DATABASE_URL`. No me pegues el `.env`: responde solo «sí» o «no».
- **Cómo obtenerlo:**

  ```powershell
  docker compose up -d
  $env:DB_NAME = "manzagrafica_replica"
  python -c "import os, django; os.environ['DJANGO_SETTINGS_MODULE'] = 'PedidosApp.settings'; django.setup(); from django.conf import settings; from django.db import connection; c = connection.cursor(); c.execute('SELECT DATABASE()'); print('Base:', c.fetchone()[0]); print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)"
  python manage.py check
  python manage.py runserver
  ```

  Con `runserver` encendido, en **otra** terminal de PowerShell 7:

  ```powershell
  curl.exe -s -o NUL -w "127.0.0.1: %{http_code}`n" http://127.0.0.1:8000/accounts/login/
  curl.exe -s -o NUL -w "localhost: %{http_code}`n" http://localhost:8000/accounts/login/
  curl.exe -s -o NUL -w "otro host: %{http_code}`n" -H "Host: otro-host.example.com" http://127.0.0.1:8000/accounts/login/
  ```

  Esperado: `Base: manzagrafica_replica`, `ALLOWED_HOSTS: ['localhost', '127.0.0.1']`, `check` sin problemas, y `200`, `200` y `400`. Después detén `runserver` (Ctrl+C) y ejecuta `Remove-Item Env:DB_NAME`.
- **Respuesta:** la confirmación sobre el `.env` y las salidas.

### 3. Antes de desplegar (no ahora): `ALLOWED_HOSTS` en el servidor

- **Para qué:** sin esta variable, producción responde 400 en cuanto se despliegue la 00-04.
- **Cómo:** agrega `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com` al `.env` del servidor **antes** de recargar la web app. Este paso va en la lista de comprobación de 00-05. Comprueba también que el `.env` del servidor sigue teniendo `DATABASE_URL`: en producción, la app no usa las `DB_*`.
- **Respuesta:** cuando despliegues: «definida».

### 4. Después del despliegue (no ahora): sitio publicado

- **Para qué:** último criterio.
- **Cómo obtenerlo:**

  ```powershell
  curl.exe -s -o NUL -w "%{http_code}`n" https://manzagrafica.pythonanywhere.com/accounts/login/
  ```

  Esperado: `200`. Si da `400`, falta `ALLOWED_HOSTS` en el servidor. Si da `500`, revisa el registro de errores del servidor y vuelve a la etiqueta anterior.
- **Respuesta:** el código y la fecha del despliegue.

## Lo que no se pudo verificar

- La conexión real a la réplica con la configuración nueva (paso 2).
- El comportamiento en producción (pasos 3 y 4).

## Respuesta del desarrollador (2026-10-21)

Sin contraseñas ni valores del `.env`.

### 1. Índice de Git

- Commit `965227d`: saca `.idea/` y `media/pedidos/Captura_de_pantalla_2026-01-20_152121.jpg` del índice. Los archivos siguen en el disco.
- `git ls-files .idea media`: sin salida (el agente también lo comprobó).
- `.sql` y `.env` versionados: solo `scripts/diagnostico/linea_base.sql` y `.env.example`.
- La captura no contiene datos sensibles: basta con sacarla del índice; no hace falta limpiar el historial por ella.

### 2. `check` y `runserver` contra la réplica

- `.env` local: tiene `DB_PASSWORD` y no tiene `ALLOWED_HOSTS` ni `DATABASE_URL`.
- Sesión con `DB_NAME = manzagrafica_replica`:
  - `Base: manzagrafica_replica`
  - `ALLOWED_HOSTS: ['localhost', '127.0.0.1']`
  - `python manage.py check`: «System check identified no issues (0 silenced).»
- `runserver` arrancó sin cambios manuales en `settings.py` y sirvió `/static/pedidos/css/index.css` y `/static/pedidos/js/index.js` con 200.
- `curl.exe` a `/accounts/login/`: `127.0.0.1` 200, `localhost` 200, `Host: otro-host.example.com` **400**. El servidor registró `DisallowedHost` para ese host.
- Inicio de sesión en el navegador contra la réplica: correcto, después de dos intentos fallidos por error de escritura.

### 3 y 4. Servidor y sitio publicado

- No aplican todavía: la 00-04 se despliega en la 00-05. Los pasos quedaron en la lista de comprobación de `iteracion-00-05-protocolo-despliegue.md` (tarea 2, punto 8), junto con la revisión de `media/` en el servidor.
