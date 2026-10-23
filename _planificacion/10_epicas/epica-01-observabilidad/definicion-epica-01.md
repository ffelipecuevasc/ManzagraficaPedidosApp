# Épica 01 · Observabilidad

- **Estado:** Pendiente
- **Fase del plan:** 1 (`plan-de-trabajo.md`, «FASE 1»)
- **Objetivo:** dejar de estar ciego. Que todo error de producción quede registrado con su traza y con un identificador que el usuario ve en pantalla, y que las acciones de negocio críticas dejen constancia de quién hizo qué y cuándo.
- **Precondición:** Épica 00 completa. Puede avanzar en paralelo con la Épica 02; la iteración 01-02 necesita la infraestructura de pruebas de 02-01.

## Alcance

1. Dos tablas nuevas (Clase 2): registro de errores y registro de eventos, con índices, retención y purga desde el inicio.
2. Un servicio de registro que resuelve por diseño las cuatro trampas del plan: aislamiento transaccional, dependencia circular, fallo en cascada y costo por petición.
3. El retiro de `ErrorHandlingMiddleware` y la conexión del sistema de registro de Django con el servicio.
4. La instrumentación del inventario de eventos de negocio.
5. La consulta de ambas tablas en el admin de Django, solo lectura y solo superusuarios.
6. El despliegue y una validación activa en producción.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 01-01 | Modelo de registro de errores y eventos | 1.1 |
| 01-02 | Servicio de registro | 1.2 |
| 01-03 | Retiro del middleware de captura global | 1.3 |
| 01-04 | Instrumentación de eventos de negocio | 1.4 |
| 01-05 | Consulta de registros en el admin | 1.5 |
| 01-06 | Despliegue y validación de la observabilidad | 1.6 |

## Decisiones de la épica

- Las iteraciones 01-01 a 01-05 se trabajan en local y se despliegan **juntas** en 01-06: es un solo propósito (observabilidad) y la migración de las tablas nuevas va en un único despliegue con respaldo previo.
- La forma de aislar la escritura del error de la transacción que falló (conexión independiente, otra técnica) se decide en 01-02 y queda como RDA nueva.
- Mientras exista `@transaccion_segura` (hasta la Épica 03), el decorador captura las excepciones antes de que lleguen a Django. Por eso 01-03 cambia su `print` por una llamada al servicio de registro, sin tocar todavía su lógica.

## Pistas registradas para la épica

Observaciones de otras iteraciones que la épica debe revisar. Son hipótesis, no hallazgos confirmados.

- **2026-10-23 (00-05):** el `OSError: write error` del 2026-10-23 a las 02:56:38 UTC ocurrió 2 segundos después de generar un respaldo (`respaldo_22-10-2026_23-56-36.sql`, hora de Chile) y coincide con su descarga. Es de la misma familia que los `Broken pipe` y `SIGPIPE` medidos en 00-01. Hay que comprobar si esos cortes se relacionan con la descarga de respaldos (evidencia-00-05, B10).
- **2026-10-23 (00-05):** los mensajes informativos de `fontTools` al generar PDFs con WeasyPrint (`subsetted`, `pruned`, `Took …s`) llegan al registro de errores del servidor y lo ensucian. Al medir errores en la épica hay que filtrarlos o bajar el nivel de registro de `fontTools`.

## Criterio de término

- Un error real en producción se diagnostica en menos de cinco minutos sin acceso al servidor: desde el identificador que ve el usuario hasta la traza en el admin, medido en 01-06.
- Una semana después del despliegue, el crecimiento real de ambas tablas está medido y dentro de la estimación de 01-01 (o el alcance se ajustó).
