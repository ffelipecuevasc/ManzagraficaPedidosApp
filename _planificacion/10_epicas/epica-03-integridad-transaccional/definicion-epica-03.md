# Épica 03 · Integridad transaccional

- **Estado:** Pendiente
- **Fase del plan:** 3 (`plan-de-trabajo.md`, «FASE 3»)
- **Objetivo:** corregir el defecto más grave del proyecto: escrituras compuestas sin atomicidad combinadas con supresión silenciosa de excepciones.
- **Precondición real:** (1) la iteración **01-06 cerrada, incluida su parte D** (medición de siete días en producción, hacia el 2026-11-01), y (2) la **Épica 02 cerrada completa** (02-03, 02-04 y 02-05 terminadas, con las regresiones de la 02-04 fallando de forma reproducible). **No es negociable**: sin la observabilidad validada en producción no se sabe si la corrección introduce un fallo nuevo, y sin las pruebas no se puede verificar que se conservó el comportamiento correcto. Decisión del desarrollador del 2026-10-27.
- **Última revisión:** 2026-10-27 (contrato de error reescrito sobre lo que existe según RDA-013 y precondición explicitada).

## Alcance

1. Rediseñar `@transaccion_segura`: separar atomicidad de traducción de errores y darle un nombre honesto. Caso de estudio central: `crear_pedido` ya usa `transaction.atomic`, pero el `try/except` interno anula su efecto sobre los ítems (AUD-02-008).
2. Erradicar `except Exception: pass` y los `print` de diagnóstico que queden (la 01-09 ya registra las capturas de ítems; aquí se corrige el fondo).
3. Fijar la frontera transaccional de cada vista de escritura: creación y edición de pedidos y cotizaciones, conversión de cotización a pedido, registro, edición y eliminación de pagos. Se suman los hallazgos de la Auditoría 02 que son de esta naturaleza:
   - `estado_pago` se recalcula dentro de la misma transacción en toda escritura que cambie pagos o el valor de venta, incluido el pedido anterior cuando un pago cambia de pedido (AUD-02-004).
   - La conversión rechaza una cotización ya aceptada y valida fecha y abono con un formulario de Django (AUD-02-005).
4. **Contrato de error hacia el usuario**, construido sobre lo que existe desde la Épica 01 (RDA-013): **no hay tabla de errores ni identificador de correlación**, y no se agregan.
   - **Errores de validación:** la vista vuelve al formulario con los datos conservados y los mensajes junto a cada campo. El usuario nunca pierde lo que escribió por un dato mal ingresado.
   - **Errores del sistema:** la traza completa queda en `server.log` con `logger.exception` (método, ruta, usuario y hora, formato de la 01-02). El usuario ve un mensaje fijo, comprensible y sin detalles técnicos: en una acción con redirección, `messages.error` con texto aprobado (el patrón de la opción C de la 01-09); si la excepción escapa de la vista, la página 500 de la 01-03.
   - **Cómo se informa un error:** el usuario cuenta qué pantalla usaba y a qué hora; con eso, el desarrollador encuentra la traza en `server.log` filtrando por ruta y hora (`docs/operacion/`). Ningún mensaje muestra `str(e)`, rutas del servidor ni salidas de `mysql` o `mysqldump` (incluye respaldo y restauración, AUD-02-006).
   - **Peor caso a evitar:** que un formulario largo (pedido con muchos ítems) se pierda por un error del sistema. La iteración define cómo se conserva lo ingresado cuando sea posible.
5. Validación y despliegue con vigilancia intensiva la primera semana, leyendo `server.log`.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 03-01 | Rediseño del decorador transaccional | 3.1 |
| 03-02 | Erradicación de la supresión silenciosa | 3.2 |
| 03-03 | Fronteras transaccionales por vista | 3.3 |
| 03-04 | Contrato de error hacia el usuario | 3.4 |
| 03-05 | Validación y despliegue de la integridad | 3.5 |

## Decisiones de la épica

- Dividir el decorador en dos o mantenerlo unificado con el orden correcto: `PENDIENTE_DESARROLLADOR`, se decide en 03-01 con una RDA.
- Las imágenes de referencia que quedan en disco cuando una transacción se revierte: `PENDIENTE_DESARROLLADOR`, se decide en 03-03.
- **2026-10-27 · Sin identificador de correlación (decisión del desarrollador).** El contrato de error se apoya en `server.log` y en mensajes fijos. Mostrar un código al usuario exigiría reabrir RDA-013, y no se hace.

## Criterio de término

- Las pruebas de regresión de pérdida de ítems, `estado_pago` y doble conversión pasan de fallo esperado a verde.
- Una operación compuesta que falla a mitad de camino no deja rastro en la base, queda en `server.log` con traza completa y el usuario recibe un mensaje comprensible y sin detalles técnicos.
- Un error de validación en la creación o edición de un pedido devuelve el formulario con los datos ingresados (prueba automatizada).
- Una semana de producción sin errores nuevos asociados a las vistas modificadas, según la revisión de `server.log`.

## Notas

- **2026-10-27 (reorganización, RDA-014):** se reescribe el contrato de error (punto 4) y el criterio de término, que pedían un identificador de correlación y una «tabla de errores» que RDA-013 descartó. Se explicita la precondición real. La épica conserva su número y sus iteraciones.
