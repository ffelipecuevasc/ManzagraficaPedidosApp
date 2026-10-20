# Épica 03 · Integridad transaccional

- **Estado:** Pendiente
- **Fase del plan:** 3 (`plan-de-trabajo.md`, «FASE 3»)
- **Objetivo:** corregir el defecto más grave del proyecto: escrituras compuestas sin atomicidad combinadas con supresión silenciosa de excepciones.
- **Precondición:** Épicas 01 y 02 completas. **No es negociable**: sin observabilidad no se sabe si la corrección introduce un fallo nuevo, y sin pruebas no se puede verificar que se conservó el comportamiento correcto.

## Alcance

1. Rediseñar `@transaccion_segura`: separar atomicidad de traducción de errores y darle un nombre honesto. Caso de estudio central: `crear_pedido` ya usa `transaction.atomic`, pero el `try/except` interno anula su efecto sobre los ítems (AUD-02-008).
2. Erradicar `except Exception: pass` y los `print` de diagnóstico.
3. Fijar la frontera transaccional de cada vista de escritura: creación y edición de pedidos y cotizaciones, conversión de cotización a pedido, registro, edición y eliminación de pagos. Se suman los hallazgos de la Auditoría 02 que son de esta naturaleza:
   - `estado_pago` se recalcula dentro de la misma transacción en toda escritura que cambie pagos o el valor de venta, incluido el pedido anterior cuando un pago cambia de pedido (AUD-02-004).
   - La conversión rechaza una cotización ya aceptada y valida fecha y abono con un formulario de Django (AUD-02-005).
4. Contrato de error hacia el usuario: errores de validación vuelven al formulario con los datos conservados; errores del sistema van a la página de error con el identificador de correlación; ningún mensaje muestra detalles técnicos (incluye los mensajes de respaldo y restauración, AUD-02-006).
5. Validación y despliegue con vigilancia intensiva la primera semana.

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

## Criterio de término

- Las pruebas de regresión de pérdida de ítems, `estado_pago` y doble conversión pasan de fallo esperado a verde.
- Una operación compuesta que falla a mitad de camino no deja rastro en la base, queda registrada con traza completa y el usuario recibe un mensaje comprensible con su identificador.
- Una semana de producción sin errores nuevos asociados a las vistas modificadas, según la tabla de errores.
