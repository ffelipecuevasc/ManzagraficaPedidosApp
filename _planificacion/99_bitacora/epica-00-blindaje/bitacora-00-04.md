# Bitácora 00-04 · Higiene del repositorio

- **Fecha:** 2026-10-21
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada (sin desplegar; el despliegue se hace en la 00-05)

## Resumen

- **`.gitignore`:** ignora `.idea/`, `*.sql` salvo bajo `scripts/`, `staticfiles/`, `media/`, `node_modules/` y `.env.*` salvo `.env.example`.
- **`.gitattributes`:** fija LF para `requirements.txt`.
- **`requirements.txt`:** pasa de UTF-16 a UTF-8 con LF, con el mismo contenido.
- **`.env.example`:** nueva plantilla con las 9 variables que lee el código, sin valores.
- **`settings.py`:**
  - `ALLOWED_HOSTS` sale del entorno, con un valor por defecto local, y rechaza `'*'`.
  - La base local sale de las variables `DB_*`. Ya no tiene la contraseña fija `'root'`: si faltan `DB_PASSWORD` y `DATABASE_URL`, la app falla con un mensaje claro.
  - El bloque de producción con `DATABASE_URL` mantiene la misma llamada a `dj_database_url.config`.
- **`docs/operacion/replica-local.md`:** se actualizó para usar `DB_NAME` en la sesión.
- **Sin ejecutar:** el agente no ejecutó `git add` ni `git rm`, no leyó `.env` y no tocó producción.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `.gitignore` | Nuevas reglas (tarea 1). Se mantiene CRLF, como el archivo original. |
| `.gitattributes` | Nuevo, una regla: `requirements.txt text eol=lf`. Aprobado por el desarrollador. |
| `.env.example` | Nuevo (tarea 4). |
| `requirements.txt` | UTF-16 LE con CRLF → UTF-8 sin BOM con LF (tarea 5). |
| `PedidosApp/settings.py` | Tareas 3 y 7. |
| `docs/operacion/replica-local.md` | Tabla de variables, sección 6 (`DB_NAME` en lugar de `DATABASE_URL`), sección 7 y nota de `ALLOWED_HOSTS` en la sección 8. |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-04-higiene-repositorio.md` | Estado, tres ajustes anotados y el primer criterio ajustado, sin borrar el texto original. |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-04.md` | Nuevo. |
| `_planificacion/00_producto/registro-pendientes.md` | Estado, pendiente de evidencia e historial. |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-04.md` | Esta bitácora. |

## Verificación

- **`git check-ignore -v --no-index`:**
  - Quedan ignorados: `volcado.sql`, `backups/x.sql`, `docs/x.sql`, `pedidos/x.sql`, `.env`, `.env.local`, `.idea/misc.xml`, `staticfiles/a.css`, `media/a.jpg`, `node_modules/a/b.js`, `.venv/`, `venv/` y `__pycache__/`.
  - No quedan ignorados (regla de negación o sin regla): `scripts/diagnostico/linea_base.sql`, `scripts/nuevo.sql`, `.env.example`, `backups/.gitkeep`, `compose.yaml` y `requirements.txt`.
- **Archivos versionados antes del cambio** que deberían salir del índice: 9 bajo `.idea/` y `media/pedidos/Captura_de_pantalla_2026-01-20_152121.jpg`. `.idea/dataSources.xml` solo tiene `jdbc:mysql://localhost:3306`, sin contraseña. La imagen no se abrió.
- **`requirements.txt`:** lectura de bytes con Python, antes y después:
  - Antes empezaba con `FF FE`.
  - Después no tiene BOM ni `\r`.
  - Tiene 21 líneas, idénticas una a una a las anteriores decodificadas.
  - Las 21 tienen `==`.
- **`settings.py`:** 11 casos en procesos aislados, con un script del scratchpad que anula `load_dotenv` (no se lee `.env`) y usa valores falsos. Peticiones a `/` con `django.test.Client`, sin la configuración del ejecutor de pruebas:

  | Caso | Resultado |
  | :--- | :-------- |
  | Sin `ALLOWED_HOSTS` | `['localhost', '127.0.0.1']`: 127.0.0.1 302, localhost 302, `otro-host.example.com` **400**, dominio de producción 400 |
  | `ALLOWED_HOSTS` vacía | Igual al anterior |
  | `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com` | Producción 302; 127.0.0.1, localhost y otro host 400 |
  | `" localhost , 127.0.0.1 "` | Se eliminan los espacios: `['localhost', '127.0.0.1']` |
  | `ALLOWED_HOSTS=*` | `ImproperlyConfigured: ALLOWED_HOSTS no puede contener '*'…` |
  | Sin `DB_PASSWORD` ni `DATABASE_URL` | `ImproperlyConfigured: Falta la contraseña de la base de datos: define DB_PASSWORD en el archivo .env (ver .env.example) o define DATABASE_URL.` |
  | `DB_PASSWORD` vacía | El mismo error |
  | Todas las `DB_*` definidas | `NAME`, `USER`, `HOST` y `PORT` salen de las variables |
  | `DATABASE_URL` sin `DB_PASSWORD` | Arranca; la base sale de la URL |
  | `DATABASE_URL` y `DB_NAME` | Gana `DATABASE_URL` |
  | `DEBUG=True` sin `ALLOWED_HOSTS` | Igual al primer caso; un host ajeno recibe 400 |

  El 302 es la redirección al inicio de sesión: significa que el host fue aceptado.
- **`python manage.py check`:** «System check identified no issues (0 silenced)». La app usó el `.env` del desarrollador; el agente no lo abrió.
- **`python manage.py makemigrations --check --dry-run`:** «No changes detected».
- **Tarea 6, búsqueda de secretos** en los archivos versionados y en los nuevos sin ignorar (sin `.sql` ni imágenes):
  - Patrones: claves `django-insecure-`, `PASSWORD` con valor literal, `SECRET_KEY` con valor literal, URL `mysql://usuario:clave@` y `mysql -p<clave>`.
  - Resultado: 3 coincidencias y las 3 son falsos positivos. Son una referencia a `$MYSQL_ROOT_PASSWORD` en `replica-local.md`, un `-printf` en `linea_base.sh` y la descripción del formato de `DATABASE_URL` en `.env.example`. No hay secretos en el árbol de trabajo.
  - La clave expuesta del commit `713260c` sigue en el historial de Git (AUD-02-010, 04-03).
- **`python manage.py test pedidos`:** no se ejecutó. La infraestructura de pruebas contra MySQL es la 02-01. Las pruebas de configuración de arriba se pueden pasar al paquete de pruebas en 02-01.
- **Revisión de pantallas:** no aplica; no se tocaron plantillas.

## Migraciones

- Ninguna. Cambio de esquema: Ninguno.

## Criterios de aceptación

- [x] `git ls-files` sin `.idea/`, sin `.sql` fuera de `scripts/` y sin `.env`: commit `965227d`; solo quedan `scripts/diagnostico/linea_base.sql` y `.env.example`.
- [x] `requirements.txt` en UTF-8 sin BOM con LF y con el mismo contenido (verificación arriba).
- [x] Todas las líneas tienen `==` (21 de 21).
- [x] Sin `'PASSWORD': '` literal en `settings.py`: 0 coincidencias.
- [x] `.env.example` lista cada variable que lee el código. La búsqueda de `os.getenv` y `os.environ` en `PedidosApp/`, `pedidos/`, `scripts/` y `manage.py` encuentra `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`, `DB_PASSWORD`, `DB_NAME`, `DB_USER`, `DB_HOST` y `DB_PORT`, más `DJANGO_SETTINGS_MODULE`, que es interno de Django. Las 9 están en la plantilla, todas sin valor.
- [x] `check` y `runserver` contra la réplica con el `.env` basado en la plantilla: base `manzagrafica_replica`, `check` sin problemas, estáticos e inicio de sesión correctos.
- [x] `settings.py` sin `'root'` ni otra contraseña literal.
- [x] `ALLOWED_HOSTS` en local, con 400 para un host ajeno: `127.0.0.1` 200, `localhost` 200, otro host 400 con `DisallowedHost` en el registro.
- [x] `.env.example` incluye `ALLOWED_HOSTS` y las cinco `DB_*`, sin valores.
- [ ] Sitio publicado responde 200: pasa a la 00-05, que despliega la 00-04.

## Decisiones tomadas

- **`*.sql` con la excepción `scripts/`**, `.gitattributes` y sacar del índice la imagen de `media/`: decisiones del desarrollador del 2026-10-21, anotadas en la iteración sin borrar el texto original.
- **`.env.example` sin valores**, con comentarios que solo describen el uso y el formato de cada variable. Se nombran los valores por defecto que aplica el código, porque son comportamiento del código y no valores de la plantilla.
- **Valores por defecto de las `DB_*` que no son secretas:** `manzagrafica_local`, `root`, `127.0.0.1` y `3306`, para que el entorno local actual siga funcionando. Solo `DB_PASSWORD` es obligatoria. Una variable vacía cuenta como no definida.
- **`'*'` en `ALLOWED_HOSTS` se rechaza al arrancar**, para cumplir «nunca '*'» también si alguien la define así en el `.env`.
- **El bloque de producción no cambió:** se movió la lectura de `DATABASE_URL` arriba, y cuando existe se usa la misma llamada a `dj_database_url.config` con los mismos argumentos. En producción, la presencia de `DATABASE_URL` hace que no se lean las `DB_*` ni se exija `DB_PASSWORD`.
- **Réplica en local:** `$env:DB_NAME = "manzagrafica_replica"` en la sesión reemplaza a `DATABASE_URL`. Así la contraseña no se escribe en la terminal; sigue saliendo del `.env`.

## Cierre (2026-10-21)

- Evidencia del desarrollador en `evidencia-00-04.md`: índice limpio (commit `965227d`), réplica con `check` limpio, `ALLOWED_HOSTS` local con 200, 200 y 400, e inicio de sesión correcto.
- Se cierran AUD-01-023 y AUD-02-009.
- La lista de comprobación de la 00-05 suma el punto 8, propio del despliegue de 00-04: listar `media/` en el servidor y confirmar con un conteo que ningún pedido referencia la captura (el `git pull` de `965227d` la borra del servidor), confirmar `DATABASE_URL` y definir `ALLOWED_HOSTS` antes de recargar.
- La captura no tiene datos sensibles: no requiere limpieza del historial.

## Pendientes y riesgos

- **Antes de desplegar la 00-04:** definir `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com` en el `.env` del servidor. Sin ella, producción responde 400. Va en la lista de comprobación de 00-05.
- AUD-01-023 y AUD-02-009 se cierran cuando la iteración quede terminada: el primero, después del paso 1; el segundo, con el commit de `requirements.txt` y `.gitattributes`.
- `requirements.txt` cambia de codificación sin cambiar versiones: en el servidor no hace falta `pip install`.
- `.idea/` sigue en el historial de Git; limpiarlo va en 04-03 junto con la clave expuesta. La captura de `media/` no lo necesita (sin datos sensibles, según el desarrollador).

## Commit sugerido

`Épica 0 - Iteración 00-04: excluye .idea, volcados y media, agrega .env.example y .gitattributes, pasa requirements.txt a UTF-8 y lee ALLOWED_HOSTS y DB_* del entorno`
