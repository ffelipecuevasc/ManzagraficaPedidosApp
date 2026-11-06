# Bitácora 03-04 · Corrección del abono al devolver el formulario

- **Fecha:** 2026-11-06
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (la 03-04 sigue En revisión: faltan los pasos [Visual] y la revisión manual del desarrollador).

## Resumen

La revisión de servidor ([bitacora-03-04-revision-servidor](bitacora-03-04-revision-servidor.md), hallazgo 1) mostró que, cuando `crear_pedido` devuelve el formulario con error (dato inválido, ítem que no se puede guardar o formulario vencido), el campo del abono vuelve vacío y el `<select>` del método de pago vuelve marcado pero **deshabilitado**. Un `<select>` deshabilitado no se envía: si el usuario no reescribía el abono, `metodo_pago` no llegaba al servidor y el pago inicial se creaba con el método por defecto (Efectivo) o no se creaba. Se corrigió con la prueba primero (regla 15), sin migraciones, sin dependencias y sin tocar el token ni las decisiones 1 a 10 de la 03-04.

## Causa

- `pedido_form.html` escribe el campo `abono_inicial` a mano, sin `value`. El formulario de Django está ligado al envío, pero la plantilla nunca lo usaba para este campo.
- El `<select name="metodo_pago">` se escribía siempre con `disabled`. `index.js` (`initConversionLogic`, `toggleMetodo`) lo habilita al cargar solo si el campo del abono tiene un valor mayor que 0; como el campo volvía vacío, el select seguía deshabilitado.
- Las pruebas de la 03-04 comprobaban los ítems y que la opción del método estuviera marcada, no el abono ni el atributo `disabled`.

## Cambio

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/views.py` | Función nueva `_abono_devuelto(request)`: devuelve el `abono_inicial` del envío solo si es un número finito mayor que 0 (con `Decimal`, regla 13), y vacío en cualquier otro caso. `crear_pedido` lo agrega al contexto como `abono_devuelto`. Importa `Decimal` e `InvalidOperation` |
| `pedidos/templates/pedidos/pedido_form.html` | El campo del abono lleva `value="{{ abono_devuelto }}"` cuando hay abono devuelto. El `<select>` y su contenedor salen habilitados (sin `disabled`, sin `opacity-50`, con `bg-white dark:bg-neutral-800`) cuando hay abono devuelto, y como antes cuando no lo hay. El valor se escapa con el autoescape de Django |
| `pedidos/tests/test_contrato_error.py` | Cuatro pruebas nuevas en `FormulariosConservanLoEscritoTests` y el `import re` |
| `docs/operacion/pruebas.md` | La fila de `test_contrato_error.py` menciona el abono |

`index.js` **no se tocó**: la lógica que deshabilita el select ya respeta el valor del campo al cargar, así que con el abono devuelto por el servidor el select queda habilitado también en el navegador. `editar_pedido` no se tocó (no crea el pago inicial; el hallazgo era de crear pedido).

## Prueba

En `FormulariosConservanLoEscritoTests` (`test_contrato_error.py`):

1. `test_crear_pedido_invalido_devuelve_el_abono_y_deja_habilitado_el_metodo_de_pago`: POST con resumen vacío, abono 5.000 y Transferencia → 200, `value="5000"` en el input, select sin `disabled`, Transferencia marcada, contenedor sin `opacity-50`.
2. `test_crear_pedido_con_item_fallido_devuelve_el_abono_y_deja_habilitado_el_metodo_de_pago`: ítem inexistente (200 con el aviso fijo y una línea `ERROR`) con las mismas comprobaciones.
3. `test_crear_pedido_vencido_devuelve_el_abono_y_deja_habilitado_el_metodo_de_pago`: token vacío (200 con el aviso de formulario vencido) con las mismas comprobaciones.
4. `test_crear_pedido_sin_abono_deja_deshabilitado_el_metodo_de_pago`: guarda el comportamiento anterior. GET, error sin abono y error con abono 0 siguen con el select deshabilitado y el input sin `value`.

**Antes de corregir** se ejecutó la clase: 11 pruebas, `FAILED (failures=3)`. Las tres fallaron por la razón correcta: `Regex didn't match: 'value="5000"' not found` en el `<input name="abono_inicial">` (sin `value`). La cuarta pasó, como corresponde a una prueba que fija lo que no debe cambiar. Se escribió como prueba normal: no hay `@expectedFailure` ni `@tag('regresion')` (no es una de las regresiones R de la auditoría).

## Verificación

- Clase `FormulariosConservanLoEscritoTests` tras la corrección: 11 pruebas, `OK`. Módulo `test_contrato_error`: 21 pruebas, `OK`.
- `python manage.py test pedidos` (tres ejecuciones, contra MySQL): **267 pruebas** (263 antes + 4 nuevas), `OK (expected failures=9)` en las tres. Las 9 fallas esperadas se mantienen (R6a, R6b, R6c, R7, R8, R9, R14, R15 y R19).
- `python manage.py check`: sin problemas.
- `python manage.py makemigrations --check --dry-run`: `No changes detected`.
- No se levantó el servidor ni se revisó en el navegador: la revisión visual (abono visible y método habilitado a 360 px, claro y oscuro) la hace el desarrollador junto con los pasos [Visual] pendientes.
- Consultas: no cambia el número de consultas de ninguna vista (solo se lee `request.POST` y se formatea un valor).

## Resultado de los comandos

- `python manage.py check` → `System check identified no issues (0 silenced).`
- `python manage.py makemigrations --check --dry-run` → `No changes detected`.
- `python manage.py test pedidos`, tres ejecuciones seguidas → `Ran 267 tests`, `OK (expected failures=9)` las tres veces (240 s, 256 s y 350 s).

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] La respuesta 200 de crear pedido (dato inválido, ítem fallido y formulario vencido) contiene el abono escrito en el input y el select de método sin `disabled` (cuatro pruebas, tres de ellas verificadas primero en rojo).
- [x] Sin abono mayor que 0, el comportamiento anterior no cambia (cuarta prueba).
- [x] Sin dependencias, sin migraciones, sin validación de precios, sin cambios en el token ni en las decisiones 1 a 10.
- [ ] Revisión visual en el navegador: pendiente del desarrollador.

## Decisiones tomadas

- El abono se devuelve desde la vista (`abono_devuelto`) y no desde `form.abono_inicial.value` en la plantilla: así la condición «mayor que 0» es la misma que usa `index.js` y el select no queda habilitado por un valor como `0` o `-5` que el JavaScript volvería a deshabilitar.
- No se tocó `index.js`: la lógica ya es correcta con el valor presente.

## Pendientes y riesgos

- **AUD-05-004** (hallazgo 2 de la revisión de servidor, confirmación pendiente en `restaurar_bd`): registrado en la Auditoría 05 como hallazgo menor, sin corregir; `restaurar_bd` no se tocó.
- Si el abono devuelto es mayor que el valor del pedido, el formulario vuelve con el error del abono junto al campo y el método habilitado: es el comportamiento esperado.
- `editar_pedido` comparte la plantilla, pero no usa `abono_devuelto` (no crea pagos): su campo de abono sigue sin `value`. Si el desarrollador lo considera un defecto, se propone aparte.

## Commit sugerido

`Épica 3 - Iteración 03-04: el formulario de crear pedido devuelve el abono y deja habilitado el método de pago; registra AUD-05-004 sin corregir`
