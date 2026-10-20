# Épica 04 · Seguridad y endurecimiento

- **Estado:** Pendiente
- **Fase del plan:** 4 (`plan-de-trabajo.md`, «FASE 4»)
- **Objetivo:** cerrar las vulnerabilidades identificadas y aplicar el estándar de configuración de producción de Django.
- **Precondición:** Épica 02 completa.

## Alcance

1. **Mutaciones solo por POST**: cambio de estado y duplicación de pedidos (plan), y además la generación de respaldos (AUD-02-006) y la eliminación de pagos, que hoy termina en error 500 por una plantilla inexistente (AUD-02-002). Las plantillas pasan de enlaces a formularios con confirmación. Se revisan todas las rutas buscando el mismo patrón.
2. **Configuración de producción**: `check --deploy` sin advertencias resueltas a ciegas; cookies seguras, HTTPS, HSTS con periodo de prueba corto antes de un valor alto, orígenes CSRF de confianza, `ALLOWED_HOSTS` que no estorbe en local y arranque que falla si la configuración es insegura.
3. **Credenciales y secretos**: contraseña de la base fuera de la línea de órdenes de `mysqldump` y `mysql`; clave secreta obligatoria desde el entorno; revisión del historial de Git y rotación de la clave si coincide con la del commit inicial (AUD-02-010, medido en 00-01).
4. **Restauración endurecida**: validación de extensión, tamaño y estructura del volcado; aborto infalible si el respaldo de emergencia falla; confirmación explícita; evento registrado.
5. **Correcciones de configuración**: `django.conf.settings`, `CONN_HEALTH_CHECKS`, importaciones duplicadas, código muerto, `TEMPLATES['DIRS']` inexistente y `BASE_DIR` duplicado (AUD-02-016).
6. **Protección del historial ante borrados en cascada** (AUD-02-001): `Pedido.cliente` y `Cotizacion.cliente` pasan de `CASCADE` a `PROTECT`, y la vista de eliminar cliente informa por qué no se puede borrar, como ya hace la de productos.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 04-01 | Mutaciones solo por POST | 4.1 |
| 04-02 | Configuración de producción | 4.2 |
| 04-03 | Credenciales y secretos | 4.3 |
| 04-04 | Endurecimiento de la restauración | 4.4 |
| 04-05 | Correcciones de configuración | 4.5 |
| 04-06 | Protección del historial ante borrados en cascada | Nueva (Auditoría 02) |

## Decisiones de la épica

- 04-06 cambia el comportamiento de borrado gestionado por Django. Se espera Clase 1; la iteración se detiene si `sqlmigrate` muestra cualquier `ALTER`. Por su riesgo para los datos, conviene ejecutarla apenas termine la Épica 02, aunque el resto de la épica espere.
- Cada iteración es un despliegue con su propio propósito; 04-02 se despliega con una ventana de observación porque HSTS no se puede deshacer en los navegadores que ya lo recibieron.

## Criterio de término

- `python manage.py check --deploy` sin advertencias en producción.
- Las pruebas de regresión de escritura por GET, eliminación de pagos y borrado en cascada pasan de fallo esperado a verde.
- Ningún proceso del servidor muestra la contraseña de la base en sus argumentos.
