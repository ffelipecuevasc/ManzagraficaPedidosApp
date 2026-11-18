# Bitácora 14-01 · Decisiones resueltas

- **Fecha:** 2026-11-18
- **Iteración:** [14-01 · Arreglo urgente de pagos](../../10_epicas/epica-14-mantenimiento/iteracion-14-01-arreglo-urgente-de-pagos.md)
- **Tipo:** solo documentos. Sin código, sin pruebas, sin `manage.py`.
- **Estado resultante:** Pendiente (redactada, decisiones resueltas).

## Decisiones (del desarrollador, dichas por él, 2026-11-18)

| # | Elegida | Resumen |
| :- | :------ | :------ |
| D1 | A | `unlocalize` en el id del campo oculto de `pago_form.html`, mismo patrón que `dashboard.html`. |
| D2 | A | `select_related('cliente')` en el selector de `PagoForm`. |
| D3 | A | AUD-05-009 no entra. |
| D4 | A | Texto propio con tuteo para `invalid_choice`. |
| D5 | B | Sin aviso provisional al cliente. |
| Etiqueta | — | `v14.1-pagos`; retroceso a `v3.1-integridad`. |

## Datos nuevos

- **Pago no guardado del #1004:** audio del cliente del 2026-11-18, dicho por el desarrollador. No verificado por el agente. Coincide con la causa inferida (id ≥ 1000). Se registra de nuevo después del despliegue.
- **#1015:** antes de borrarlo, el desarrollador revisa duplicados en producción con una consulta de solo lectura. En la documentación se anotan solo conteos.

## Archivos tocados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-14-nube-aws/iteracion-14-01-arreglo-urgente-de-pagos.md` | Estado, tabla de resolución, alcance de `forms.py`, avisos, #1004, revisión de duplicados antes del #1015. |
| `_planificacion/00_producto/registro-pendientes.md` | Próximo hito, fila 14-01, #1015, #1004, D1 a D5 y etiqueta resueltas, historial. |
| Esta bitácora | Nueva. |

## Qué sigue abierto

- Fecha y ventana del despliegue, texto literal del aviso antes y después del despliegue, y vigencia del protocolo de pedido y pago de prueba (parte C de `evidencia-03-05.md`): `PENDIENTE_DESARROLLADOR`.
- Si hubo otros pagos no guardados además del #1004: `PENDIENTE_CLIENTE`.
