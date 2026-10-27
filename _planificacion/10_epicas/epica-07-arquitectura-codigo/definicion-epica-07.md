# Épica 07 · Arquitectura del código

- **Estado:** Pendiente
- **Fase del plan:** 6, subfases 6.4 a 6.6 (`plan-de-trabajo.md`, «FASE 6»), separada el 2026-10-27 (anexo del plan, RDA-014)
- **Objetivo:** que el código sea fácil de navegar, de probar y de cambiar: vistas delgadas por dominio que delegan en servicios (escritura) y selectores (lectura), aplicando los principios SOLID de forma práctica y sin capas que no aporten (RDA-015).
- **Precondición:** Épicas 01, 02 y 03 completas. Se ejecuta después de la Épica 06 y **antes** de las épicas que agregan funciones (08 a 12), para que lo nuevo nazca en la estructura nueva y no dentro de `views.py`.
- **Última revisión:** 2026-10-27 (creada a partir de la antigua Épica 06).

## Por qué esta épica (contexto para quien llega)

`pedidos/views.py` tiene 1.624 líneas (medido el 2026-10-27 en `main`, commit `ac70401`): todas las vistas conviven con la lógica de negocio (interpretar el formulario dinámico de ítems, calcular totales, convertir cotizaciones, aplicar pagos). No es un defecto funcional, pero es fricción permanente: cada cambio obliga a recorrer un archivo enorme, y la lógica de negocio solo se puede probar a través de peticiones HTTP.

## Alcance

1. **Modularización de las vistas (07-01):** `pedidos/views/` como paquete con un módulo por dominio (pedidos, clientes, cotizaciones, productos, pagos, base de datos, estadísticas, trabajo semanal y acceso). Es una **refactorización pura**: cero cambios de comportamiento, los mismos nombres de rutas y un despliegue dedicado, validado por la suite de pruebas. En Django la vista cumple el papel de «controlador»: recibe la petición, valida con un formulario, llama a un servicio o a un selector y elige la respuesta.
2. **Capa de servicios y selectores (07-02):** la lógica de negocio sale de las vistas.
   - `services` por dominio: casos de uso que **escriben** (crear o editar pedido con sus ítems, convertir cotización, registrar pago). Reciben datos ya validados y devuelven resultados, sin depender del objeto `request`. **Las fronteras transaccionales que fijó la Épica 03 se trasladan aquí**, sin cambiarlas.
   - `selectors` por dominio: consultas de **lectura** reutilizables, con las anotaciones de la 05-02 (saldos, totales, filtros del panel).
   - Se empieza por la conversión de cotización a pedido, la operación más compleja. Incluye convertir cantidades con `Decimal` (AUD-02-015), el porcentaje pagado con `float` (AUD-02-025, regresión R15 de la 02-04; asignado por el desarrollador el 2026-10-26 a la antigua 06-05, hoy 07-02) y, según la respuesta del cliente, la regla de neto o total en la conversión (AUD-02-014).
   - Las `dataclasses` se usan solo donde un servicio devuelve un resultado compuesto (por ejemplo, un resumen financiero), no como copia de los modelos.
3. **Modelos por dominio (07-03):** `pedidos/models.py` (288 líneas) pasa a un paquete `pedidos/models/` con un módulo por dominio, reexportados desde `__init__.py`. Django lo admite **sin migraciones**: la iteración lo comprueba con `makemigrations --check --dry-run` sin cambios. Se hace en esta épica porque la estructura de servicios y selectores sigue la misma división por dominio.
4. **Deuda técnica menor (07-04):** paginación de clientes, sincronía de `estado_pago` mientras siga siendo doble fuente de verdad, nomenclatura de rutas, captura de rutas numéricas en la raíz, criterio de idioma del código, el admin de los modelos de negocio (AUD-02-012) y la regla de pedidos entregados y sin fecha en el panel y en el trabajo semanal (AUD-02-013, con la respuesta del cliente o la decisión del desarrollador).

## Iteraciones

| Iteración | Nombre | Origen |
| :-------- | :----- | :----- |
| 07-01 | Modularización de las vistas | 6.4 (antes 06-04) |
| 07-02 | Capa de servicios y selectores | 6.5 (antes 06-05), ampliada con selectores |
| 07-03 | Modelos por dominio | Nueva (reorganización 2026-10-27) |
| 07-04 | Deuda técnica menor | 6.6 (antes 06-06) |

## Decisiones de la épica

- **2026-10-27 · Sin patrón repositorio ni DTOs para los modelos (RDA-015).** El ORM de Django ya cumple el papel de repositorio: un `QuerySet` es una consulta componible y perezosa. Envolverlo en clases `…Repository` agrega código de paso y quita esa capacidad. Los principios SOLID se aplican así: responsabilidad única (vista, servicio y selector hacen una cosa cada uno), dependencias explícitas (los servicios reciben datos, no la petición) y abierto a extensión (servicios pequeños que se componen).
- Cada iteración de esta épica es un despliegue propio, sin mezclar cambios funcionales: si algo falla, la causa es inequívoca.
- Criterio único de idioma del código (castellano o inglés): `PENDIENTE_DESARROLLADOR` (registro, sección 3), se decide en 07-04 y se aplica de forma gradual.

## Fuera de alcance

- Reorganizar las plantillas en carpetas semánticas: Épica 08 (los nombres de plantilla que usan las vistas se actualizan allí).
- Unificar `estado_pago` (Clase 3): deuda diferida, 13-05.
- Vistas basadas en clases como norma: se evalúan caso a caso, no se migra todo.

## Criterio de término

- `pedidos/views.py` ya no existe como archivo único; cada módulo de `pedidos/views/` tiene menos de 400 líneas.
- Ninguna vista contiene lógica de negocio: crear, editar, convertir y pagar pasan por servicios con pruebas directas (sin cliente HTTP).
- `makemigrations --check --dry-run` no detecta cambios después de 07-03.
- La suite completa en verde después de cada iteración, con el mismo número de regresiones declaradas.

## Notas

- **2026-10-27 (reorganización, RDA-014):** creada con las subfases 6.4 a 6.6 de la antigua Épica 06 y ampliada a pedido del desarrollador (servicios y selectores por dominio, modelos por dominio, SOLID). La propuesta de usar el patrón repositorio y DTOs para los modelos se descartó en RDA-015.
