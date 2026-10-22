# Iteración 00-04 · Higiene del repositorio

- **Épica:** 00 · Blindaje y punto de retorno
- **Estado:** Pendiente
- **Subfase del plan:** 0.4
- **Depende de:** —
- **RDA relacionadas:** RDA-002
- **Hallazgos que cierra:** AUD-01-023, AUD-02-009
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No. Se despliega por separado porque cambia `settings.py`, con la lista de comprobación de 00-05.

## Objetivo

Que un clon limpio del repositorio no contenga artefactos locales ni credenciales, que documente las variables de entorno que necesita la aplicación y que sus dependencias se puedan leer y comparar.

## Tareas

1. **`.gitignore`** (requiere consulta): agregar `.idea/`, `*.sql` en cualquier carpeta, `staticfiles/`, `media/`, `node_modules/` y los archivos `.env.*` salvo `.env.example`. Verificar que siguen cubiertos el entorno virtual, `__pycache__/`, `.env` y `backups/*` con su `.gitkeep`.
2. **Sacar `.idea/` del índice de Git** sin borrarlo del disco: el agente entrega el comando al desarrollador, que lo ejecuta (borrar del índice es una operación de Git que no hace el agente).
3. **Credenciales locales fuera de `settings.py`** (requiere consulta): el bloque de base de datos local toma nombre, usuario, contraseña, host y puerto desde variables de entorno (`DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT`, aprobadas en 00-03), sin valores de contraseña escritos en el código. **Ampliación aprobada por el desarrollador el 2026-10-21:** se quita también la contraseña fija `'root'`, que hoy sirve como valor por defecto en local. Si falta `DB_PASSWORD` y no hay `DATABASE_URL`, la aplicación no usa una contraseña inventada. El bloque de producción con `DATABASE_URL` no cambia: producción sigue configurándose igual.
4. **`.env.example`** (requiere consulta): todas las variables que lee la aplicación (`SECRET_KEY`, `DEBUG`, `DATABASE_URL` y las de la base local), con un comentario por variable y **sin valores**.
5. **`requirements.txt`** (requiere consulta): recodificar de UTF-16 LE con CRLF a UTF-8 sin BOM con LF, sin cambiar ninguna versión. Confirmar que todas las líneas usan `==`.
6. **Revisión final** sobre el árbol de trabajo: buscar contraseñas, claves y cadenas `django-insecure-` en archivos versionados.
7. **`ALLOWED_HOSTS` desde el entorno** (requiere consulta; ampliación aprobada por el desarrollador el 2026-10-21, AUD-02-022): se lee de una variable de entorno `ALLOWED_HOSTS` (lista separada por comas). El valor por defecto es seguro para local: solo `localhost` y `127.0.0.1`, nunca `*`. **Antes del despliegue**, el desarrollador define `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com` en el `.env` del servidor; sin ella, producción respondería 400. Ese paso va en la lista de comprobación de 00-05.

## Criterios de aceptación

- [ ] `git ls-files` no lista nada bajo `.idea/` (después de que el desarrollador ejecute el comando entregado) ni ningún archivo `.sql` o `.env`.
- [ ] `requirements.txt` se detecta como UTF-8 sin BOM con fin de línea LF (comprobado leyendo sus primeros bytes con Python) y su contenido, línea por línea, es idéntico al anterior salvo la codificación.
- [ ] Todas las líneas de `requirements.txt` tienen `==`.
- [ ] Una búsqueda de `'PASSWORD': '` con un valor literal en `PedidosApp/settings.py` no encuentra coincidencias.
- [ ] `.env.example` lista cada variable que el código lee con `os.getenv` u `os.environ` (comparación hecha con una búsqueda en el código) y ninguna tiene valor.
- [ ] Con un `.env` local basado en `.env.example`, `python manage.py check` termina sin errores y `python manage.py runserver` arranca contra la réplica.
- [ ] `settings.py` no contiene la contraseña `'root'` ni ningún otro valor literal de contraseña (búsqueda en el archivo).
- [ ] Sin `ALLOWED_HOSTS` en el entorno, `runserver` responde en `127.0.0.1` y en `localhost` sin cambios manuales, y una petición con otro `Host` recibe 400.
- [ ] `.env.example` incluye `ALLOWED_HOSTS` y las cinco `DB_*`, sin valores.
- [ ] Después del despliegue, la aplicación publicada responde 200 en `manzagrafica.pythonanywhere.com` (evidencia del desarrollador).

## Fuera de alcance

- Rotar la clave secreta o limpiar el historial de Git (va en 04-03).
- Cambiar otros ajustes de producción (va en 04-02). Nota 2026-10-21: leer `ALLOWED_HOSTS` desde el entorno entró en esta iteración (tarea 7) por decisión del desarrollador; 04-02 conserva el resto de la configuración de producción.
- Cualquier cambio en la lógica de la aplicación.

## Datos requeridos del cliente

- Ninguno.
