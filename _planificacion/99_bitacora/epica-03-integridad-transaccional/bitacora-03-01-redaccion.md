# Bitácora 03-01 · Redacción de la iteración

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión (la redacción). La iteración 03-01 queda «Pendiente»: no se ejecutó.

## Resumen

Se redactó la iteración 03-01 · Rediseño del decorador transaccional a partir de evidencia leída en el código y en la planificación. Se describe qué hace hoy `@transaccion_segura`, sus 17 vistas (12 con `pk`, AUD-02-029), el caso de estudio de AUD-02-008 y R20 como prueba de aceptación (fallos esperados de 19 a 18). La decisión del decorador queda abierta con tres opciones y una recomendación. Sin cambios de código, pruebas ni `docs/operacion/`.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-01-rediseno-decorador-transaccional.md` | Nuevo: iteración con estado «Pendiente». |
| `00_producto/registro-pendientes.md:43` | Fila 03-01: enlaces a la iteración y a esta bitácora; el estado sigue «Pendiente». |
| `00_producto/registro-pendientes.md:297` | Entrada de historial 2026-11-04. |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-01-redaccion.md` | Esta bitácora (nueva). |

## Verificación

Evidencia leída (solo lectura):

- `pedidos/decorators.py:9-33`: `try/except Exception` sin transacción; `mensaje_tecnico` con `str(e)` en `:29`.
- `pedidos/views.py`: 17 líneas `@transaccion_segura` (contadas con `grep -c`); `transaction.atomic` solo en `:168` (`crear_pedido`), con la captura interna en `:183-197`.
- `settings.py`: sin `ATOMIC_REQUESTS` (búsqueda sin resultados).
- `pedidos/eventos.py:28-44`: los eventos se escriben con `transaction.on_commit`.
- `test_regresiones.py:416-433` (R20) y `test_acceso.py:284-320` (caracterización de las 12 rutas; `eliminar_pago` queda fuera por R7).
- `test_errores.py:27-73`: Django ya responde 404 y 500 con traza sin el decorador.
- `auditoria-tecnica.md:23`, `:73` y `:94`; `decisiones.md` (RDA-003, 007, 013 y 015); `plan-de-trabajo.md:327-337`; `definicion-epica-07.md:16-19`; `bitacora-01-03.md:59` y `:105`.

Además:

- Pruebas: no se ejecutaron (sin cambios de código).
- `git --no-pager status --short` y `git --no-pager diff --stat`: solo los `.md` de la tabla.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Iteración creada con cabecera, objetivo, tareas, criterios, fuera de alcance y decisiones, y con estado «Pendiente».
- [x] Afirmaciones apoyadas en archivo:línea.
- [x] Pruebas primero (regla 8.15) y compatibilidad con RDA-015 explícitas en las tareas y las opciones.
- [x] Lo no decidido queda marcado `PENDIENTE_DESARROLLADOR`, sin alcance nuevo para la 03-02 ni la 03-03.

## Decisiones tomadas

- Ninguna. Las decisiones abiertas son del desarrollador.

## Pendientes y riesgos

Decisiones abiertas (`PENDIENTE_DESARROLLADOR`), detalladas en la iteración:

1. **Qué hacer con el decorador:**
   - A: dividir en `transaction.atomic` más un decorador de errores con nombre honesto.
   - B: un solo decorador con el orden correcto.
   - C: retirarlo y dejar los errores al manejo nativo de Django (recomendada, con RDA-019).
2. Nombre del componente nuevo (solo en A o B).
3. Cierre de AUD-01-001 en la 03-01 o en la 03-03.
4. Despliegue propio o junto con la 03-05.

Diferencias con el pedido:

- El pedido hablaba de «las 12 vistas que lo usan». En realidad lo usan 17; 12 son las que reciben `pk` y responden 500 (AUD-02-029). La iteración lista las 17.
- La opción C no está entre las dos que nombran `plan-de-trabajo.md:334` y `definicion-epica-03.md:11`. Se propone por la evidencia de `test_errores.py:32-44`, y elegirla exige registrarlo en una RDA.

## Commit sugerido

`Épica 3 - Iteración 03-01: redacta el rediseño del decorador transaccional con evidencia, R20 como aceptación y tres opciones abiertas`
