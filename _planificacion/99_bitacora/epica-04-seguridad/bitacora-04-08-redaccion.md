# Bitácora 04-08 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** la 04-08 queda **Pendiente (redactada, decisiones abiertas D1 a D5)**. Solo documentos; sin código, pruebas, `manage.py` ni consultas a la base.

## Resumen

Se redactó [iteracion-04-08](../../10_epicas/epica-04-seguridad/iteracion-04-08-proteccion-del-acceso-y-limites-de-entrada.md): límite de intentos fallidos por usuario y por dirección en `accounts/login/` y en el admin, con un evento por bloqueo; límites de tamaño de subida; redirección con sesión iniciada. Compara el contador propio en la caché local con `django-axes` y deja recomendada la primera.

## Verificación (solo lectura; Django 6.0.1 de `.venv`)

- Dos entradas: `urls.py:24` (admin, ruta `acceso-manzagrafica-admin/`) y `urls.py:25` (`accounts/`). Ambas usan formularios que derivan de `AuthenticationForm`; `admin.site.login_form` existe y el admin ya redirige con sesión.
- `authenticate()` emite `user_login_failed` **incluso** si un backend lanza `PermissionDenied`: bloquear en un backend duplicaría eventos; se bloquea en el `clean()` del formulario, antes de autenticar.
- Hoy un ataque de fuerza bruta escribe una fila de evento por intento (`senales.py:17-26`), sin tope: llena la tabla además de adivinar.
- Sin `CACHES` en `settings.py`: rige la caché local por proceso, 300 entradas por defecto (`base.py:71`, `:77`), con `add` e `incr` atómicos.
- Django no interpreta `X-Forwarded-For`; ningún código de la aplicación lee la dirección del cliente.
- `DATA_UPLOAD_MAX_MEMORY_SIZE` y `FILE_UPLOAD_MAX_MEMORY_SIZE` valen 2,5 MB por defecto; el primero cuenta solo campos de texto (no archivos) y el segundo **no es un tope** (elige memoria o archivo temporal). La imagen de referencia no tiene tope (`models.py:42`).
- `media/` de producción: 3 MB en 11 archivos (línea base, 2026-10-20); el máximo no se midió.
- Colación de producción `utf8mb4_unicode_ci` (línea base, línea 98): el nombre de usuario se normaliza para no esquivar el contador con mayúsculas.

## Contradicciones

1. La definición llama «límite de tamaño» a `FILE_UPLOAD_MAX_MEMORY_SIZE`; en Django es un umbral, no un tope.
2. La definición pide «evento registrado»; un bloqueo mal ubicado dejaría dos eventos por intento.
3. «Dirección» no dice cómo se obtiene tras el proxy: no consta en el repo.

## Qué no se pudo ver

- Qué cabecera trae la dirección real en PythonAnywhere y cuántos proxies hay (se mide en producción; verificación 3).
- Cuántos usuarios tiene producción, cuántos fallos hace una persona legítima y la frecuencia de reinicio del proceso.
- Peso, tablas y órdenes de `django-axes` (de mi conocimiento, no verificado), y el límite de cuerpo del proxy.

## Decisiones abiertas

D1 mecanismo (recomendada: contador propio en la caché local), D2 qué se cuenta y cuánto (5 por usuario y 20 por dirección en 15 minutos, bloqueo de 15; propuesta sin medición), D3 dirección real (cantidad de proxies de confianza por variable de entorno), D4 evento (tipo nuevo `acceso_bloqueado`, migración de Clase 1) y D5 límites de tamaño (imagen de 5 MB y chequeo temprano de `CONTENT_LENGTH`). Fila en la sección 3 del registro.

## Archivos

Nuevo `iteracion-04-08-proteccion-del-acceso-y-limites-de-entrada.md`; `definicion-epica-04.md`; `00_producto/registro-pendientes.md` (fila, decisiones, propuesta de redirección, próximo hito 04-09, historial); esta bitácora.
