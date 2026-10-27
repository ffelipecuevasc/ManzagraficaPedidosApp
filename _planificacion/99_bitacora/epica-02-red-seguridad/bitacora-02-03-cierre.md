# Bitácora 02-03-cierre · Pruebas de flujos críticos: decisiones tras la revisión

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** Terminada (la 02-03, con sus 8 criterios de aceptación marcados)

## Resumen

Registra las decisiones del desarrollador del 2026-10-27 tras revisar [bitacora-02-03](bitacora-02-03.md) y sus tres hallazgos propuestos. Por la regla 5.4 de `_planificacion/README.md`, `bitacora-02-03.md` es una bitácora entregada y no se edita: las decisiones van aquí. Solo cambia documentación; no se tocan el código de la aplicación ni `pedidos/tests/`.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-03-cierre.md` | Esta bitácora |
| `_planificacion/00_producto/registro-pendientes.md` | 02-03 terminada; H1 a H3 fuera de la sección 4; `creado_por` separado de la pregunta del cliente sobre duplicar; decisión pendiente sobre la iteración de AUD-02-028; una línea de historial |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-02-027 y AUD-02-028 en la tabla de la Auditoría 02; notas de la iteración 02-03 |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-03-flujos-criticos.md` | Estado terminada; decisiones 4 a 6 |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-04-regresiones.md` | R18 y R19, recuento de 19, condiciones de R18 y R19, tarea 0 (`congelar_hora`), hallazgos que avanza, criterio de aceptación |
| `_planificacion/10_epicas/epica-02-red-seguridad/definicion-epica-02.md` | Estado de la épica y de la 02-03; alcance y recuento de 19; hallazgos de la 02-04; nota del cierre |
| `docs/operacion/pruebas.md` | Sección 9: regla de negocio confirmada del precio del ítem y advertencia para las Épicas 03 a 06 |

## Verificación

- `git status --short` y `git diff --stat`: solo archivos `.md`.
- `bitacora-02-03.md` sin cambios.
- Pruebas: no aplica, solo documentación.

## Migraciones

- Ninguna.

## Criterios de aceptación

- No aplica: es un cierre documental. Los 8 criterios de la 02-03 están marcados en su iteración, por eso pasa a «Terminada».

## Decisiones tomadas

Decisiones del desarrollador del 2026-10-27.

- **H1 · El precio de cada ítem lo fija el vendedor: regla de negocio confirmada.** El vendedor (hoy, el dueño, único usuario y superusuario) ajusta a mano el precio de cada ítem para dar trato diferenciado a distintos clientes. No es defecto: sin hallazgo, sin regresión y sin ampliar AUD-02-014. **Advertencia:** ningún cambio de las Épicas 03 a 06 debe validar el precio contra el catálogo sin consultar al desarrollador. Documentada en `docs/operacion/pruebas.md`, sección 9.
- **H2 → AUD-02-027** (severidad propuesta: Baja; solo ocurre fuera del navegador). `convertir_a_pedido` con la fecha de entrega vacía responde 500. Regresión **R18** en la 02-04, que debe confirmar que falla por la fecha vacía (500 o excepción); si da `unexpected success`, la hipótesis era falsa y no se registra como defecto. Iteración propuesta: **03-04** (contrato de error hacia el usuario).
- **H3 → AUD-02-028** (severidad propuesta: Baja). El pedido duplicado queda con `creado_por` nulo. Regresión **R19** en la 02-04, que afirma que el duplicado queda con el usuario que lo duplicó y debe fallar porque `creado_por` es nulo. Iteración que lo corrige: `PENDIENTE_DESARROLLADOR` (candidatas 04-01, que ya reescribe `duplicar_pedido`, o 03-03), registrada en la sección 3 del registro. Se relaciona con la pregunta del cliente sobre qué se copia al duplicar, pero no se mezcla: esa pregunta sigue abierta solo para ítems y pagos.
- **Recuento de la 02-04:** de 17 a **19** regresiones, sin renumerar las existentes.
- **Tarea 0 de la 02-04:** unificar `congelar_hora` (hoy en `test_dinero.py` y `ayudas.py`) en un solo lugar, sin cambiar el comportamiento de ninguna prueba. No se ejecuta ahora.
- H1, H2 y H3 salen de la sección 4 de `registro-pendientes.md`; el historial lo registra en una línea.

## Pendientes y riesgos

- **Comentario de prueba para que decida el desarrollador** (no se edita en este cierre): `pedidos/tests/test_pedidos.py:118-119`, en `CrearPedidoTests.test_el_precio_lo_envia_el_navegador`, dice «El servidor guarda el precio que llega en items_json, sin compararlo con el catálogo (hallazgo propuesto en bitacora-02-03).» No usa las palabras `PENDIENTE_CLIENTE` ni «defecto», pero sigue llamándolo «hallazgo propuesto», que ya no es cierto. Ningún otro comentario de las pruebas de la 02-03 trata este comportamiento.
- **Numeración R16 y R17:** la tabla de la 02-04 tenía filas R1 a R15 (17 pruebas, porque R6 son tres). R16 estaba reservado para AUD-02-021 (decisión 2 de la 02-04) y R17 no existía. Las nuevas quedan como R18 y R19, como se pidió; R17 queda sin asignar.
- Iteración que corrige AUD-02-028: `PENDIENTE_DESARROLLADOR`.

## Commit sugerido

`Épica 2 - Iteración 02-03: cierra la iteración, confirma el precio manual del ítem como regla de negocio y suma AUD-02-027 y AUD-02-028 a la 02-04 como R18 y R19 (19 regresiones)`
