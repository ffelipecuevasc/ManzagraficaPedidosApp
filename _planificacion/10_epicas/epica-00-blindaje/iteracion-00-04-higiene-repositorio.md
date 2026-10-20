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
3. **Credenciales locales fuera de `settings.py`** (requiere consulta): el bloque de base de datos local toma nombre, usuario, contraseña, host y puerto desde variables de entorno, sin valores de contraseña escritos en el código. El bloque de producción con `DATABASE_URL` no cambia: producción sigue configurándose igual.
4. **`.env.example`** (requiere consulta): todas las variables que lee la aplicación (`SECRET_KEY`, `DEBUG`, `DATABASE_URL` y las de la base local), con un comentario por variable y **sin valores**.
5. **`requirements.txt`** (requiere consulta): recodificar de UTF-16 LE con CRLF a UTF-8 sin BOM con LF, sin cambiar ninguna versión. Confirmar que todas las líneas usan `==`.
6. **Revisión final** sobre el árbol de trabajo: buscar contraseñas, claves y cadenas `django-insecure-` en archivos versionados.

## Criterios de aceptación

- [ ] `git ls-files` no lista nada bajo `.idea/` (después de que el desarrollador ejecute el comando entregado) ni ningún archivo `.sql` o `.env`.
- [ ] `requirements.txt` se detecta como UTF-8 sin BOM con fin de línea LF (comprobado leyendo sus primeros bytes con Python) y su contenido, línea por línea, es idéntico al anterior salvo la codificación.
- [ ] Todas las líneas de `requirements.txt` tienen `==`.
- [ ] Una búsqueda de `'PASSWORD': '` con un valor literal en `PedidosApp/settings.py` no encuentra coincidencias.
- [ ] `.env.example` lista cada variable que el código lee con `os.getenv` u `os.environ` (comparación hecha con una búsqueda en el código) y ninguna tiene valor.
- [ ] Con un `.env` local basado en `.env.example`, `python manage.py check` termina sin errores y `python manage.py runserver` arranca contra la réplica.

## Fuera de alcance

- Rotar la clave secreta o limpiar el historial de Git (va en 04-03).
- Cambiar `ALLOWED_HOSTS` u otros ajustes de producción (va en 04-02).
- Cualquier cambio en la lógica de la aplicación.

## Datos requeridos del cliente

- Ninguno.
