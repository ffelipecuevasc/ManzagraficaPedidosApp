# Bitácora 04-02 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-02 queda **Pendiente (redactada, decisiones abiertas D1 a D6)**. Solo documentos; sin código, pruebas ni `manage.py`.

## Resumen

Se redactó [iteracion-04-02](../../10_epicas/epica-04-seguridad/iteracion-04-02-configuracion-de-produccion.md): cookies seguras, HTTPS, HSTS escalonado, orígenes CSRF, arranque que falla con configuración insegura, ventana de observación, retroceso y verificación en producción. No repite `ALLOWED_HOSTS` (00-04) ni la clave secreta (04-03).

## Verificación (solo lectura)

- `PedidosApp/settings.py` completo por búsqueda y lectura de `:30-60`, `:60-106` y `:107-160`: no hay ninguna opción `SECURE_*`, de cookies seguras ni `CSRF_TRUSTED_ORIGINS`; ya existe el patrón `ImproperlyConfigured`.
- `docs/operacion/despliegue.md` (`:88-118`, `:216-250`), `retroceso.md` (`:10-48`), `plan-de-trabajo.md:400-408`, `evidencia-03-05.md` (advertencias locales y «No informado» en producción), `linea-base-produccion.md:141` («Force HTTPS activado», 2026-10-20), `auditoria-tecnica.md` (AUD-01-012, AUD-02-010, AUD-02-022), `decisiones.md` (RDA-007).
- No se leyó `.env` ni `.env.example` (una lectura de este último fue denegada por permisos); la iteración pide consulta previa antes de editarlo.

## Distinción de fuentes

- **Dicho por el desarrollador:** producción muestra W004, W008, W012 y W016. El repo no tiene esa salida (`evidencia-03-05.md:284` y `:341`: «No informado»).
- **Medido antes, no verificado hoy:** «Force HTTPS» activo en PythonAnywhere.
- **Inferido:** que Django ya ve las peticiones de producción como `https` (los POST pasan la comprobación de origen de CSRF sin `CSRF_TRUSTED_ORIGINS`); que `settings.py` toma `DEBUG` del entorno antes de que el ejecutor de pruebas lo fuerce a falso.

## Decisiones abiertas

D1 escalones de HSTS, D2 redirección a HTTPS, D3 activación, D4 `CSRF_TRUSTED_ORIGINS`, D5 qué hace fallar el arranque, D6 ventana y orden. Cada una con opción recomendada en la iteración y una fila en la sección 3 del registro.

## Archivos

Nuevo `10_epicas/epica-04-seguridad/iteracion-04-02-configuracion-de-produccion.md`; `definicion-epica-04.md` (tabla y nota); `00_producto/registro-pendientes.md` (fila 04-02, decisiones, próximo hito 04-03, historial); esta bitácora.
