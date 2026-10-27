# Épica 04 · Seguridad y endurecimiento

- **Estado:** Pendiente
- **Fase del plan:** 4 (`plan-de-trabajo.md`, «FASE 4»), ampliada el 2026-10-27 (anexo del plan, RDA-014)
- **Objetivo:** cerrar las vulnerabilidades identificadas, defender las entradas de la aplicación (HTML enriquecido, acceso y archivos) y aplicar el estándar de configuración de producción de Django.
- **Precondición:** Épica 02 completa. **Orden de ejecución:** después de la Épica 03 (decisión del desarrollador del 2026-10-27), incluida la 04-06.
- **Última revisión:** 2026-10-27 (iteraciones 04-07, 04-08 y 04-09 agregadas; AUD-03-002 sumado a 04-01).

## Alcance

1. **Mutaciones solo por POST**: cambio de estado y duplicación de pedidos (plan), y además la generación de respaldos (AUD-02-006) y la eliminación de pagos, que hoy termina en error 500 por una plantilla inexistente (AUD-02-002). Las plantillas pasan de enlaces a formularios con confirmación. Se revisan todas las rutas buscando el mismo patrón. Al convertir «Generar Nuevo Respaldo BD» en formulario se retira la recarga de la página a los 2 segundos, que aborta la descarga del respaldo en el navegador (AUD-03-002), y se comprueba que el archivo llega al equipo del usuario.
2. **Configuración de producción**: `check --deploy` sin advertencias resueltas a ciegas; cookies seguras, HTTPS, HSTS con periodo de prueba corto antes de un valor alto, orígenes CSRF de confianza, `ALLOWED_HOSTS` que no estorbe en local y arranque que falla si la configuración es insegura.
3. **Credenciales y secretos**: contraseña de la base fuera de la línea de órdenes de `mysqldump` y `mysql`; clave secreta obligatoria desde el entorno; revisión del historial de Git y rotación de la clave si coincide con la del commit inicial (AUD-02-010, medido en 00-01).
4. **Restauración endurecida**: validación de extensión, tamaño y estructura del volcado; aborto infalible si el respaldo de emergencia falla; confirmación explícita; evento registrado.
5. **Correcciones de configuración**: `django.conf.settings`, `CONN_HEALTH_CHECKS`, importaciones duplicadas, código muerto, `TEMPLATES['DIRS']` inexistente y `BASE_DIR` duplicado (AUD-02-016). La carpeta global `templates/` que crea la Épica 08 parte de lo que deje esta iteración.
6. **Protección del historial ante borrados en cascada** (AUD-02-001): `Pedido.cliente` y `Cotizacion.cliente` pasan de `CASCADE` a `PROTECT`, y la vista de eliminar cliente informa por qué no se puede borrar, como ya hace la de productos.
7. **Defensa contra inyección** (nuevo, AUD-03-001): el HTML que guarda Summernote en `pedido.detalles_pedido`, `cotizacion.detalles` y `producto.descripcion` se imprime con `|safe` sin limpiar (XSS almacenado). Se sanitiza con una lista blanca de etiquetas y atributos. Hoy solo escribe un usuario de confianza, pero la Épica 09 agrega operadores y un operador no debe poder ejecutar código en la sesión de un superusuario: **esta iteración es requisito de la 09**. Se documenta además la revisión de inyección SQL: la única consulta directa (`pedidos/utils.py`, `connection.cursor()`) usa parámetros y el resto pasa por el ORM; la iteración deja una prueba o una regla que impida introducir SQL armado con texto.
8. **Protección del acceso y límites de entrada** (nuevo, AUD-03-004): límite de intentos fallidos de acceso por usuario y por dirección (fuerza bruta), con evento registrado, en las dos entradas que existen hoy: `accounts/login/` y el acceso del admin de Django; límites de tamaño para las subidas (`DATA_UPLOAD_MAX_MEMORY_SIZE`, `FILE_UPLOAD_MAX_MEMORY_SIZE` y validación del tamaño de las imágenes de referencia).
9. **Política de seguridad de contenido en observación** (nuevo): `ContentSecurityPolicyMiddleware` de Django 6.0 en modo `SECURE_CSP_REPORT_ONLY`, para conocer qué recursos carga la aplicación sin bloquear nada mientras existan los CDN. El modo estricto (`SECURE_CSP`) se activa en la Épica 08, cuando ya no haya recursos externos.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 04-01 | Mutaciones solo por POST | 4.1 |
| 04-02 | Configuración de producción | 4.2 |
| 04-03 | Credenciales y secretos | 4.3 |
| 04-04 | Endurecimiento de la restauración | 4.4 |
| 04-05 | Correcciones de configuración | 4.5 |
| 04-06 | Protección del historial ante borrados en cascada | Nueva (Auditoría 02) |
| 04-07 | Sanitización del HTML enriquecido y revisión de inyección SQL | Nueva (Auditoría 03) |
| 04-08 | Protección del acceso y límites de entrada | Nueva (Auditoría 03) |
| 04-09 | Política de seguridad de contenido en observación | Nueva (reorganización 2026-10-27) |

## Decisiones de la épica

- 04-06 cambia el comportamiento de borrado gestionado por Django. Se espera Clase 1; la iteración se detiene si `sqlmigrate` muestra cualquier `ALTER`. **Decisión del desarrollador del 2026-10-27:** se ejecuta en el orden de la épica, después de la Épica 03 (deja sin efecto la sugerencia anterior de adelantarla).
- Cada iteración es un despliegue con su propio propósito; 04-02 se despliega con una ventana de observación porque HSTS no se puede deshacer en los navegadores que ya lo recibieron.
- 04-07 · Cómo se sanitiza: al guardar, al mostrar o en ambos momentos, y con qué herramienta (`nh3` es la opción recomendada: dependencia nueva, requiere consulta y RDA). `PENDIENTE_DESARROLLADOR`. El HTML ya guardado en producción se revisa en la réplica antes de decidir si hace falta limpiarlo (operación sobre datos, con respaldo previo).
- 04-08 · Mecanismo contra fuerza bruta: contador propio en la caché local (válida porque hay un solo proceso) o una librería como `django-axes` (dependencia nueva y tabla nueva de Clase 2). `PENDIENTE_DESARROLLADOR`.
- 04-09 · Dónde se leen los reportes de la política en modo observación (la consola del navegador en la réplica es suficiente; no se agrega un punto de recepción de reportes). Se confirma en la iteración.

## Fuera de alcance

- **Protección contra DoS o DDoS dentro de Django.** Con un solo proceso uWSGI, cuando una petición maliciosa llega a un middleware ya ocupó al único trabajador: un limitador en la aplicación no frena una inundación y da una falsa sensación de seguridad. Ese ataque se contiene en la red, que en el plan gratuito es responsabilidad de PythonAnywhere. Lo que sí está al alcance de la aplicación es la fuerza bruta en el acceso y el tamaño de las subidas (04-08).
- Corregir el respaldo de emergencia en el mismo disco (AUD-02-024) más allá de lo que decida la 04-04; el respaldo externo es la Épica 14.

## Criterio de término

- `python manage.py check --deploy` sin advertencias en producción.
- Las pruebas de regresión de escritura por GET, eliminación de pagos y borrado en cascada pasan de fallo esperado a verde.
- Ningún proceso del servidor muestra la contraseña de la base en sus argumentos.
- Un respaldo generado desde la web se descarga en el equipo del usuario (verificado en producción después del despliegue de la 04-01).
- Un `<script>` guardado en cualquiera de los tres campos enriquecidos no se ejecuta al mostrar el detalle (prueba automatizada).
- Después de N intentos fallidos el acceso queda bloqueado por un tiempo definido y queda un evento (prueba automatizada).
- La política de seguridad de contenido está activa en modo observación en producción.

## Notas

- **2026-10-21 (00-03, AUD-02-022):** leer `ALLOWED_HOSTS` desde el entorno, con un valor por defecto local, se adelantó a 00-04 por decisión del desarrollador. 04-02 parte de ese estado y no lo repite.
- **2026-10-25 (01-04), para 04-04 · Restauración y tabla de eventos:** restaurar un volcado reemplaza todas las tablas, incluida `pedidos_registroevento`, así que se pierden los eventos posteriores a ese volcado (la auditoría de lo ocurrido entre el volcado y la restauración). El evento `restauracion_ejecutada` se escribe después de restaurar para que sobreviva. Si el volcado no contiene al usuario que restauró, la clave foránea rechaza la fila: el servicio lo deja en `error.log` y el evento se pierde. 04-04 debe evaluar cómo conservar esa constancia (por ejemplo, registrarla también en `error.log` con `logger.warning` o preservar los eventos recientes). (Corrección del 2026-10-26: con la opción A de la 01-06, el registro de diagnóstico es `server.log`.)
- **2026-10-26 (01-09), asignado a 04-04 por decisión del desarrollador · `.sql` vacío al fallar `mysqldump`:** `generar_respaldo_mysql()` (`pedidos/utils.py`) abre el `.sql` antes de llamar a `mysqldump` y solo lo borra ante `CalledProcessError`. Si `mysqldump` no existe (`FileNotFoundError`), queda un `.sql` vacío en `backups/` que la rotación cuenta entre los cinco. Visto en la réplica local (01-09). 04-04 debe borrar el archivo ante cualquier fallo de `mysqldump`, con una prueba que falle antes de la corrección (AUD-02-019).
- **2026-10-26, asignado a 04-04 por decisión del desarrollador · AUD-02-024:** el respaldo de emergencia que genera la restauración se guarda en `backups/` del servidor, en el mismo disco de 512 MiB que la base, sin enlace de descarga, y la rotación de cinco archivos puede borrarlo. Hallazgo hermano de AUD-02-019 y del `.sql` vacío. Solo registrado, sin corrección propuesta.
- **2026-10-27 (reorganización, RDA-014):** se suman las iteraciones 04-07 (AUD-03-001), 04-08 (AUD-03-004) y 04-09, y AUD-03-002 a la 04-01, a pedido del desarrollador de atender la seguridad (inyección, XSS, ataques de acceso). La épica conserva su número y su lugar, después de la 03.
- **2026-10-27 (02-05, decisión del desarrollador, sin ID nuevo) · Respuestas de rechazo:** sin sesión, los puntos JSON `api/cliente/nuevo/` y `api/producto/nuevo/` responden 302 al acceso en HTML, no un JSON de error ni 401; un usuario autenticado que no es superusuario recibe 302 al acceso, no 403, en las cuatro vistas de la base de datos (`user_passes_test`). Comportamiento fijado en `test_acceso.PuntosJsonTests` y `test_acceso.BaseDeDatosPermisosTests`: si la Épica 04 lo cambia, actualiza esas pruebas en la misma iteración y el contrato de `index.js` (`AGENTS.md`, sección 9). Además, AUD-02-030: decidir si se desactivan la recuperación de contraseña y el acceso propio del panel de administración.
