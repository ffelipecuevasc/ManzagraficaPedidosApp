# Bitácora 02-04-cierre · Pruebas de regresión: decisiones tras la revisión

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** Terminada (la 02-04, con sus 7 criterios de aceptación marcados)

## Resumen

Registra las decisiones del desarrollador del 2026-10-27 tras revisar [bitacora-02-04](bitacora-02-04.md). Por la regla 5.4, `bitacora-02-04.md` no se edita: lo que esta revisión corrige de ella queda aquí. Solo cambia documentación y un comentario de prueba; no se toca el código de la aplicación.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-04-cierre.md` | Esta bitácora |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-04-regresiones.md` | Terminada; R5 «no confirmada, sin prueba», cubierta por R8; decisiones 6 a 8 |
| `_planificacion/10_epicas/epica-02-red-seguridad/definicion-epica-02.md` | Recuento de 18 en el alcance (decía 19); 02-04 terminada |
| `_planificacion/00_producto/registro-pendientes.md` | 02-04 terminada; decisiones de R5 y de D4 resueltas; historial |
| `_planificacion/00_producto/auditoria-tecnica.md` | Nota de AUD-01-006 con la causa más consistente; se quita la hipótesis de tablas de zona horaria de la nota de la 02-04 |
| `docs/operacion/pruebas.md` | R15 → 06-05; R5 cubierta por R8; `dashboard` y `estadisticas_bd` sin regresión |
| `pedidos/tests/test_regresiones.py` | Solo comentarios: R15 → 06-05; R5 cubierta por R8 |

## Verificación

- Recuento de 18 regresiones: iteración 02-04 («el resultado es **18**»), definición de la épica («Recuento: 18 regresiones»), registro (historial: «18 regresiones») y `pruebas.md` (`expected failures=18`). No queda un 17 ni un 19 como recuento vigente; el 19 aparece solo como «previsto».
- **Prueba 152 de `--exclude-tag regresion`:** es `test_regresiones.OraculoEstadoPagoTests.test_reglas_del_oraculo`, la prueba del oráculo de `estado_pago` (tarea 2 de la 02-04), sin la etiqueta `regresion`. **No** es una prueba de `congelar_hora`: la unificación no agregó pruebas (la de la ayuda ya existía en `AyudasTests` desde la 02-03). Está documentada en `pruebas.md`, sección 7.1, y en `bitacora-02-04.md` (170 = 151 + 18 + 1).
- Pruebas: no se volvieron a ejecutar en este paso (solo comentarios en pruebas); las ejecuta la 02-05.

## Migraciones

- Ninguna.

## Criterios de aceptación

- No aplica: es un cierre documental. Los 7 criterios de la 02-04 están marcados en su iteración, por eso pasa a «Terminada».

## Decisiones tomadas

Decisiones del desarrollador del 2026-10-27.

- **a) R5 queda cubierta por R8.** «No confirmada, sin prueba»: dos llamadas a `registrar_metricas_diarias()` a mediodía de Chile dejan una fila. El número R5 sigue sin asignar. En AUD-01-006 queda una nota con la causa más consistente: el día de la comprobación se calcula en UTC y Django convierte el campo a día de Chile, así que en las últimas 3 o 4 horas del día de Chile el chequeo no encuentra fila e inserta una por visita. Evidencia: R8 en la base de pruebas. Es una hipótesis consistente, no verificada en producción.
- **b) Hipótesis de tablas de zona horaria descartada.** La medición de la 00-01 (AUD-02-007) ya mostró las tablas cargadas, 0 conversiones nulas y 119 días distintos en hora de Chile. **El comando `CONVERT_TZ` propuesto en `bitacora-02-04.md` («Pendientes y riesgos») es innecesario y no se ejecuta.** El «hallazgo propuesto» de esa bitácora queda reemplazado por la nota de AUD-01-006.
- **c) `dashboard` y `estadisticas_bd`** escriben `HistorialBD` con GET: no se suman como regresión. Quedan en el inventario D4 y se resuelven en la 06-01.
- **d) AUD-02-028 (R19)** sigue `PENDIENTE_DESARROLLADOR`.

Correcciones de esta revisión:

- **R15:** `bitacora-02-04.md`, `pruebas.md` y el comentario de la prueba decían «07-02». La decisión del desarrollador (2026-10-26) fue la **06-05, junto con AUD-02-015**. Corregido en `pruebas.md` y en el comentario. La tabla de la iteración 02-04 y el registro ya decían 06-05; no hubo que cambiarlos. Nota: la equivalencia de RDA-014 (la antigua 06-05 es la 07-02) sigue en el registro, sección 3.
- **Recuento:** la definición de la épica todavía decía «Recuento previsto: 19 regresiones»; ahora dice 18.

## Pendientes y riesgos

- **Numeración 06-05 frente a 07-02:** RDA-014 renumeró la 06-05 como 07-02, y `auditoria-tecnica.md` (AUD-02-015 y AUD-02-025) también dice 06-05. Conviene decidir si los documentos de la Épica 02 citan la numeración anterior o la nueva, para no mezclarlas.
- AUD-02-028: iteración que lo corrige, `PENDIENTE_DESARROLLADOR`.

## Commit sugerido

`Épica 2 - Iteración 02-04: cierra la iteración, cubre R5 con R8, anota la causa de AUD-01-006 y corrige R15 a la 06-05`
