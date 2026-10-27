# Bitácora 00-07 · Correcciones tempranas II (revisión en local)

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión (criterios locales verificados; quedan los de producción del domingo 2026-11-01)

## Resumen

Verificación en local de la 00-07, ya con commit y push en `main`. Las pruebas pasaron (184 pruebas, 19 fallos esperados). Los seis pasos de revisión de `bitacora-00-07.md` los hizo el desarrollador en Chrome (ventana de incógnito) contra la réplica, guiado por el agente, porque la sesión no tenía herramienta de navegador (decisión del desarrollador: no se instala). El agente comprobó conteos y eventos después de cada paso que cambiaba datos. Durante la revisión el desarrollador decidió cambiar el texto del botón en modo edición a «Editar Pedido» (cambio aplicado y verificado). Los registros de prueba se borraron y los conteos volvieron a su valor inicial.

Convención: **observado por el desarrollador** es lo que el desarrollador vio en el navegador; **verificado por el agente** es lo que el agente midió con `manage.py shell -c` o con comandos.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/templates/pedidos/pedido_form.html` | Texto del botón: «Editar Pedido» al editar, «Crear Pedido» al crear (decisión del desarrollador, 2026-10-27) |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-07-correcciones-tempranas-ii.md` | Criterios locales marcados, criterio y decisión 7 del texto del botón |
| `_planificacion/00_producto/registro-pendientes.md` | Propuesta del texto del botón resuelta, fila 00-07 e historial |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-07-revision.md` | Esta bitácora |

## Verificación

### Pruebas (verificado por el agente)

- `docker compose ps`: `manzagrafica-mysql` (`mysql:8.0.46`) `Up`, `127.0.0.1:3306->3306/tcp`.
- `python manage.py test pedidos`, antes de la revisión: `Ran 184 tests in 237.793s` · `OK (expected failures=19)`.
- Después del cambio de texto: `Found 184 test(s)` · `OK (expected failures=19)`; `check`: `System check identified no issues (0 silenced).`; `makemigrations --check --dry-run`: `No changes detected`.

### Entorno

- `runserver 127.0.0.1:8000 --noreload` con `DB_NAME=manzagrafica_replica` en la sesión (`replica-local.md`, sección 6). Se reinició una vez para tomar el cambio de texto. Detenido al terminar.
- **La consola de `runserver` no muestra las líneas `POST`:** `LOGGING` deja el registrador `django` en `WARNING` (`PedidosApp/settings.py:237`), así que las peticiones correctas (200 y 302) no se escriben. No se cambió la configuración. Como evidencia de «un solo envío» se usó la tabla de eventos: cada envío confirmado deja exactamente un `pedido_creado` o `pedido_modificado` (decisión de la 01-04, un evento por acción).

### Conteos (verificado por el agente)

| Momento | Cliente | Pedido | ItemPedido | Pago | RegistroEvento |
| :------ | ------: | -----: | ---------: | ---: | -------------: |
| Inicio | 736 | 887 | 871 | 1.054 | 0 |
| Cliente de prueba creado (ID 742) | 737 | 887 | 871 | 1.054 | 1 (`acceso_exitoso` del inicio de sesión; crear un cliente no registra evento) |
| Paso 1, pedido 907 | 737 | 888 | 872 | 1.054 | 2 |
| Paso 2, edición del 907 | 737 | 888 | 872 | 1.054 | 3 |
| Paso 3, abono negativo | — | 888 | — | — | — |
| Paso 4, pedido 908 | 737 | 889 | 873 | 1.054 | 4 |
| Paso 5, revisión visual | 737 | 889 | 873 | 1.054 | 4 |
| Pedidos 907 y 908 eliminados | 737 | 887 | 871 | 1.054 | 6 |
| Cliente 742 eliminado (final) | **736** | **887** | **871** | **1.054** | **7** |

- Eventos agregados a la réplica (no se borran): `acceso_exitoso`, `pedido_creado` (907), `pedido_modificado` (907), `pedido_creado` (908), `pedido_eliminado` (907), `pedido_eliminado` (908), `cliente_eliminado` (742). **Siete en total.**
- IDs de prueba, todos borrados: cliente 742; pedidos 907 y 908. `Pago` no cambió en ningún momento (abono 0).

## Resultado de los seis pasos

| Paso | Observado por el desarrollador | Verificado por el agente | Resultado |
| :--- | :----------------------------- | :----------------------- | :-------- |
| 1. Crear con doble clic | Al primer clic, «Guardando…» con el ícono girando y el botón atenuado; el segundo clic no fue posible; llegó al detalle del pedido nuevo | `Pedido` 887 → 888 (+1); un solo `pedido_creado` (907); 1 ítem | Cumple |
| 2. Editar con doble clic | Igual que al crear: «Guardando…», botón desactivado, segundo clic imposible, detalle del pedido | Un solo `pedido_modificado` (907); el pedido sigue con 1 ítem; `Pedido` sin cambio | Cumple |
| 3. Abono negativo (-100) | El navegador marcó el campo y no envió; el botón siguió en «Crear Pedido» y activo | `Pedido` siguió en 888 | Cumple |
| 4. «Atrás» después de crear | Pedido 908 creado; con «atrás» volvió al formulario con «Crear Pedido» activo; Chrome no pidió reenviar | `Pedido` 888 → 889; un solo `pedido_creado` (908) | Cumple |
| 5. Escritorio y 360 px, claro y oscuro | Foco visible y «Guardando…» legible en las cuatro combinaciones (estado activado a mano desde la consola, sin enviar); «Editar Pedido» al editar y «Crear Pedido» en «Nuevo pedido» | Conteos sin cambio (889 y 4 eventos): no hubo envío | Cumple |
| 6. «Nueva cotización» | Pantalla igual que siempre; la consola respondió `[null, null]` a la búsqueda de `btn-confirmar-pedido` y `[data-texto-procesando]`; no se guardó | `cotizacion_form.html`: 0 coincidencias de esos selectores y sin cambios en el árbol de trabajo | Cumple |

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Crear con doble clic deja un solo pedido (887 → 888, un `pedido_creado`).
- [x] Editar con doble clic deja un solo guardado (un `pedido_modificado`).
- [x] «Guardando…» con su ícono, contraste y foco visibles (escritorio y 360 px, claro y oscuro; observado por el desarrollador).
- [x] La validación nativa impide el envío y el botón sigue disponible.
- [x] «Atrás» restaura el botón.
- [x] «Nueva cotización» sin cambios.
- [x] Pruebas, `check` y `makemigrations` sin cambios.
- [x] El botón dice «Editar Pedido» al editar y «Crear Pedido» al crear (criterio nuevo, decisión 7).
- [ ] Despliegue con `v0.3-doble-envio`, `v1.2-capturas` sobre el commit anterior a la 00-07 y la semana de `access.log`: producción, domingo 2026-11-01 ([evidencia-00-07](../../10_epicas/epica-00-blindaje/evidencia-00-07.md)).

## Decisiones tomadas

- **2026-10-27 (desarrollador):** revisión manual hecha por el desarrollador, guiada por el agente, sin instalar Claude in Chrome ni otras herramientas.
- **2026-10-27 (desarrollador), decisión 7 de la 00-07:** el botón dice «Editar Pedido» en modo edición. El agente recomendó «Guardar cambios» (`DESIGN.md:153`: los botones dicen lo que hacen). El desarrollador eligió «Editar Pedido» porque remite al cliente a lo que está haciendo: editar un pedido existente. Cambio de una línea con la misma condición del título (`{% if form.instance.pk %}`); viaja en `v0.3-doble-envio`. Resuelve la propuesta del registro del 2026-10-27.

### Diff del cambio de texto

```diff
-                                <span data-texto-normal>Crear Pedido</span>
+                                <span data-texto-normal>{% if form.instance.pk %}Editar Pedido{% else %}Crear Pedido{% endif %}</span>
```

## Pendientes y riesgos

- **El cambio de texto requiere un commit nuevo** antes del domingo. La parte B de la evidencia no cambia: `v1.2-capturas` va sobre el commit anterior al **primero** que cambia `pedido_form.html`, y B2 debe seguir mostrando solo ese archivo.
- La consola de `runserver` no sirve para contar peticiones mientras `django` esté en `WARNING`. Se anota como dato para futuras revisiones locales, sin propuesta de cambio.
- Siguen abiertos: `DESIGN.md` §8 frente al ícono que gira, y `btn-submit-pedido` inexistente en `index.js:302` (registro).

## Commit sugerido

`Épica 0 - Iteración 00-07: verifica en local el bloqueo del doble envío (6 pasos, 184 pruebas) y cambia el botón a Editar Pedido en la edición`
