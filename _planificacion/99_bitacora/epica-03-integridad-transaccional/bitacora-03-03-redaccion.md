# Bitácora 03-03 · Redacción de la iteración

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (la redacción). La iteración 03-03 queda «Redactada»: no se ejecutó. La Épica 03 no cambia de estado.

## Resumen

Se redactó la iteración 03-03 · Fronteras transaccionales por vista con evidencia leída en `views.py`, las pruebas y la planificación. Cubre 8 vistas de escritura, el orden de nueve pasos, siete regresiones que pasan a verde (R1, R2, R4 y R10 a R13), criterios de aceptación, riesgos y revisión manual. Deja ocho decisiones `PENDIENTE_DESARROLLADOR`, cada una con opciones, ventajas, riesgos y una recomendada, sin decidir. Además, en el mismo tramo, se ajustó el cierre de la 03-02 (nombre propio del cliente, pedido #910 y asignación de AUD-05-003).

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-03-fronteras-transaccionales-por-vista.md` | Nuevo: iteración con estado «Redactada». |
| `00_producto/registro-pendientes.md` | Fila 03-03 «Redactada» con enlaces; cabecera y párrafo del próximo hito; fila de decisiones en la sección 3; observación sobre los mensajes en la sección 4; dos entradas de historial. |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-03-redaccion.md` | Esta bitácora (nueva). |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-02-cierre.md` | Parte A: nombre propio por «el cliente»; #910 con un ítem y fuera de los 126 y los 38; AUD-05-003 sin asignar. La 03-02 la entregó el mismo día; el desarrollador pidió el ajuste de forma expresa. |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-02-erradicacion-supresion-silenciosa.md` | Parte A: nombre propio por «el cliente»; el #910 como pedido de prueba. |
| `00_producto/auditoria-tecnica.md` | Parte A: AUD-05-003 «sin asignar, 08-06 candidata». |
| `10_epicas/epica-14-nube-aws/definicion-epica-14.md`, `epica-10-mejoras-negocio/definicion-epica-10.md`, `epica-09-usuarios-roles/definicion-epica-09.md`, `00_producto/producto.md` | Parte A: el nombre propio del cliente reemplazado por «el cliente» (1, 3, 2 y 1 apariciones). Solo texto. |

## Verificación

Evidencia leída (solo lectura): no se ejecutó nada, ni pruebas, ni `docker`, ni `mysql`.

- **Código:** `views.py:142-150` (ayudante de `estado_pago`), `:156-292` (`crear_pedido`, `editar_pedido`), `:397-419` (`duplicar_pedido`), `:729-826` (cotizaciones), `:841-915` (`convertir_a_pedido`), `:1361-1478` (pagos), `forms.py:22-56`, `models.py:42`, `:50-81` y `:150-161`, `cotizacion_convertir.html`, `cotizacion_detail.html`.
- **Pruebas:** `test_regresiones.py` completo, `test_capturas_amplias.py:42-75`, `test_cotizaciones.py:140-174`, `test_pedidos.py:450-490`, `pruebas.md` secciones 7.1, 8 y 9.
- **Planificación:** `definicion-epica-03.md`, `plan-de-trabajo.md:317-358`, `auditoria-tecnica.md` (AUD-01-001, 01-002, 02-004, 02-005, 02-006, 02-008, 02-014, 02-021, 02-027, 02-028), RDA-019, `iteracion-03-01`, `iteracion-03-02`, `bitacora-03-02` y `registro-pendientes.md`.
- **Búsquedas:** `estado_pago` en `pedidos/` (sin coincidencias en plantillas ni en el admin); `message` en `*.html` y `*.js` del repositorio (una sola plantilla, `restaurar_bd.html`); el nombre propio del cliente en el repositorio (cero apariciones al terminar, salvo el historial de git).
- **Predicciones** de fallos esperados (17 → 10, 9 u 8): por lectura, se confirman al ejecutar.
- `git --no-pager status --short`: solo `.md`.

## Hallazgos de la lectura que importan

1. **Alcance confirmado, con tres matices.** Todo lo que pide la definición está en la iteración. Los matices: la validación de la fecha en la conversión choca con R18 asignada a la 03-04 (decisión 3); la 03-02 citaba `views.py:858` y hoy es `:855`; el `estado_pago` de pedidos de valor $0 sigue la regla provisoria del oráculo.
2. **Nadie lee `estado_pago` (inferido).** Corregir R10 a R12 deja el dato correcto pero no cambia ninguna pantalla; las 610 filas desincronizadas del 2026-10-20 no se reparan solas (decisión 6).
3. **Los mensajes de Django casi no se muestran (inferido).** Solo `restaurar_bd.html` recorre `messages`. Cambia las opciones de las decisiones 1 y 4 y afecta al contrato de la 03-04. Se anotó como observación en el registro.
4. **El borrado de la imagen huérfana es peligroso:** `duplicar_pedido` copia la ruta del archivo (`views.py:410`) y `editar_pedido` sin imagen nueva conserva la anterior. Por eso se recomienda no borrar nada (decisión 2, opción A).
5. **La conversión no tiene vínculo entre cotización y pedido:** la relación solo queda en el texto del evento, así que no se puede redirigir al pedido ya creado (decisión 4).

## Decisiones abiertas (`PENDIENTE_DESARROLLADOR`)

| # | Tema | Recomendada |
| :- | :--- | :---------- |
| 1 | Qué ve el usuario si falla un ítem hasta la 03-04 | A. Propagar (500), como en la 03-02 |
| 2 | Imágenes de referencia huérfanas | A. Aceptar y documentar |
| 3 | Qué valida el formulario de la conversión (y dónde cae R18) | A. Fecha, abono y estado |
| 4 | Qué ve el usuario ante una conversión repetida | A. Redirigir al detalle de la cotización |
| 5 | Quién corrige AUD-02-028 (R19) | A. La 04-01 |
| 6 | Reparar los `estado_pago` históricos | A. No reparar ahora |
| 7 | Una iteración o dos | A. Una, con pasos ordenados |
| 8 | El abono inicial que la edición descarta | A. Fuera de alcance, como propuesta |

Todas figuran en la sección 3 de `registro-pendientes.md`.

## Contradicciones y puntos a revisar (sin corregir)

1. **R18 y la 03-04.** La definición pide validar la fecha con un formulario en la 03-03, pero AUD-02-027, R18 y `pruebas.md` la asignan a la 03-04 (decisión del 2026-10-27). La decisión 3 lo resuelve.
2. **Estado «Redactada».** `_planificacion/README.md` (documento protegido, §3) lista seis estados y no incluye «Redactada». Se usó porque lo pediste; hasta ahora una iteración redactada figuraba como «Pendiente». Propuesta para el desarrollador: agregar «Redactada» a esa lista, o seguir usando «Pendiente (redactada)».
3. **Las líneas de la 03-02 están desplazadas.** Cita `views.py:858`, `:191`, `:267`, `:759` y `:803`; las vigentes son `:855`, y las capturas de ítems de `:264`, `:756` y `:800`. No se editó la 03-02 por eso.
4. **Los avisos de la 01-09 podrían no verse.** `generar_respaldo_bd` redirige a `respaldar_bd` con `messages.error` (`views.py:1118`), y esa plantilla no recorre los mensajes (inferido). La 01-09 y la épica (alcance 4) los dan por buenos. No se probó en pantalla.
5. **Estado de la Épica 03.** `definicion-epica-03.md` sigue en «Pendiente» con dos iteraciones terminadas y una redactada. No se tocó, como pediste.
6. **`bitacora-03-02-cierre.md` editada tras entregarse.** La regla 5.4 pide correcciones en una bitácora nueva; aquí el desarrollador pidió editarla de forma expresa. Quedó constancia en la sección «Decisiones tomadas» de esa bitácora.
7. **Historial de git.** Los nombres reemplazados siguen en los commits anteriores; no se reescribió historial.

## Migraciones

- Ninguna.

## Commit sugerido

`Épica 3 - Iteración 03-03: redacta las fronteras transaccionales por vista con ocho decisiones abiertas y ajusta el cierre de la 03-02`
