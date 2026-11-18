# Bitácora 14-01 · Ejecución en local

- **Fecha:** 2026-11-18
- **Iteración:** [14-01 · Arreglo urgente de pagos](../../10_epicas/epica-14-mantenimiento/iteracion-14-01-arreglo-urgente-de-pagos.md)
- **Estado resultante:** Implementada, pendiente de despliegue. Se cierra con la verificación del día 0 en producción.
- **Hallazgos:** AUD-05-010 y AUD-05-011, corregidos en código y pendientes de verificar en producción. AUD-05-009 no se tocó (D3 A).

## Causa

Confirmada por prueba. Con `LANGUAGE_CODE = 'es-cl'` y `USE_THOUSAND_SEPARATOR = True`, `{{ pedido_obj.id }}` escribe el id con el separador de miles del formato de Django para «es», que es un espacio duro (`"\xa0"`), no un punto. El pedido 1002 salía «1 002» en el campo oculto, `PagoForm` lo rechazaba como opción no válida y esa rama de la plantilla no pintaba el error.

## Archivos modificados

| Archivo | Cambio | Fin de línea |
| :------ | :----- | :----------- |
| `pedidos/templates/pedidos/pago_form.html` | `{% load l10n %}`; `\|unlocalize` en «Pedido #…» y en el campo oculto; aviso `id="error-pedido"` `role="alert"` en la rama del campo oculto | CRLF, conservado |
| `pedidos/forms.py` | `PagoForm`: `select_related('cliente')`; `error_messages` con `invalid_choice` de D4 | CRLF, conservado |
| `pedidos/templates/pedidos/pedido_form.html` | `{% load l10n %}`; `producto.id\|unlocalize` | LF, conservado |
| `pedidos/templates/pedidos/cotizacion_form.html` | `{% load l10n %}`; `producto.id\|unlocalize` | CRLF, conservado |
| `pedidos/tests/test_pagos_ids.py` | Nuevo: T1, T2, T3 (pedido y cotización), T4, T5 | LF |
| Documentos | Iteración, registro, auditoría y esta bitácora | conservados |

Sin migraciones, dependencias, configuración ni estáticos.

## Pruebas

| Momento | Comando | Resultado |
| :------ | :------ | :-------- |
| Antes del arreglo | `python manage.py test pedidos.tests.test_pagos_ids` | `Ran 6 tests` · `FAILED (failures=6)`. T1: `'1\xa0002' != '1002'`; T2: no encuentra `id="error-pedido"`; T3: no encuentra `<option value="1002"`; T4: `9 != 36`; T5: `10 != 37` |
| Después | mismo | `Ran 6 tests` · `OK` |
| Suite completa | `python manage.py test pedidos` | `Found 273 test(s)` · `OK (expected failures=9)` |
| Configuración | `python manage.py check` | `System check identified no issues (0 silenced).` |
| Migraciones | `python manage.py makemigrations --check --dry-run` | `No changes detected` |

El primer intento de T1 después del arreglo falló solo en la prueba: el evento `pago_registrado` se escribe en `on_commit` y `TestCase` no lo ejecuta. Se ajustó con `captureOnCommitCallbacks(execute=True)`, igual que `test_eventos_negocio.py`.

## Medición de consultas (regla 12)

| Pantalla | Antes (3 → 30 pedidos) | Después |
| :------- | :--------------------- | :------ |
| `GET /pagos/ingresar/` | 9 → 36 | igual con 3 y con 30 |
| `GET /pagos/editar/<pk>/` | 10 → 37 | igual con 3 y con 30 |

La réplica (994 pedidos) no se midió.

## No hecho

- Revisión manual en la réplica, en escritorio y a 360 px (paso 6 de la iteración): la hace el desarrollador.
- Nada en producción: despliegue, día 0 ni tiempos de `/pagos/ingresar/`.

## Despliegue

Pasos, verificación del día 0 y retroceso a `v3.1-integridad`: en la iteración. Sin respaldo previo obligatorio.
