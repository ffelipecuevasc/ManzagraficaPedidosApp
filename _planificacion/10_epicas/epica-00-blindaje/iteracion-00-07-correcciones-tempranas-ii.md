# Iteración 00-07 · Correcciones tempranas II

- **Épica:** 00 · Blindaje y punto de retorno (reabierta el 2026-10-27 solo para esta iteración)
- **Estado:** En revisión (implementada en local el 2026-10-27; faltan `test pedidos` con el contenedor MySQL encendido y la revisión manual del desarrollador)
- **Subfase del plan:** 0.6 (continuación; nueva, por hallazgos de producción del 2026-10-27)
- **Depende de:** 00-05 (protocolo de despliegue). En producción, va después de validar `v1.2-capturas` (decisión 5).
- **RDA relacionadas:** RDA-007
- **Hallazgos que cierra:** ninguno por completo. Avanza AUD-04-001 (el lado del servidor queda en la 03-04).
- **Cambio de esquema:** Ninguno (sin migración). ~~Ninguno (solo plantilla o JavaScript; riesgo de Clase 1 en el sentido de que no toca datos ni estructura)~~ Reemplazado el 2026-10-27: las clases de `AGENTS.md` (sección 8, regla 1) solo clasifican migraciones.
- **Respaldo previo al despliegue:** No (no toca datos ni esquema), pero sí etiqueta y despliegue propios
- **Etiqueta:** `v0.3-doble-envio`
- **Partida y destino de retroceso:** `v1.2-capturas`
- **Ventana:** domingo 2026-11-01, después de validar `v1.2-capturas`
- **Evidencia:** [evidencia-00-07](evidencia-00-07.md)

## Objetivo

Que un doble clic en «Crear Pedido» no envíe dos veces el formulario de pedido, ni al crear ni al editar, con una corrección mínima del lado del cliente que se despliega sola, antes de que la Épica 03 pueda empezar.

`pedidos/templates/pedidos/pedido_form.html` es una plantilla compartida: la renderizan `crear_pedido` y `editar_pedido`. Las cotizaciones (`cotizacion_form.html`, que usa el mismo id `pedidoForm`) no se tocan.

> ~~Que un doble clic en «Confirmar» de «Nuevo pedido» no cree dos pedidos, con una corrección mínima del lado del cliente que se despliega sola, antes de que la Épica 03 pueda empezar.~~ Reemplazado el 2026-10-27 (decisión 1): el alcance es crear y editar, y el botón dice «Crear Pedido».

## Contexto

El 2026-10-27 a las 14:36:20, dos `POST /pedidos/nuevo/` en el mismo segundo crearon dos pedidos (AUD-04-001). El botón `id="btn-confirmar-pedido"` de `pedido_form.html` (cerca de la línea 416), con el texto **«Crear Pedido»** (también en modo edición), no se desactiva al enviar, y ningún manejador escucha el `submit` del formulario. La 00-06 resolvió lo mismo en el acceso y dejó «los demás formularios» para la 03-04. Esta iteración adelanta solo el formulario de pedido; la 00-06 no se reabre. `DESIGN.md` (sección 5.1) ya pide que un botón que envía un formulario se deshabilite tras el primer clic.

## Tareas

1. En `pedido_form.html`, agregar al botón `btn-confirmar-pedido` los elementos `data-texto-normal`, `data-texto-procesando` («Guardando…», válido para crear y editar), `data-icono-normal` y `data-icono-procesando` (ícono que gira), y las clases `disabled:` del botón de acceso.
2. Un script propio de la plantilla en `{% block scripts %}` (que `base.html` carga después de `index.js`), atado al `submit` del formulario `pedidoForm` y no al `click`: desactiva el botón, marca `aria-busy`, cancela un segundo `submit` y restaura el botón en `pageshow`. Patrón de la 00-06 en `login.html`. No se toca `index.js`.
3. Revisión manual en la réplica, en escritorio y a 360 px, modo claro y oscuro: crear, editar y «Nueva cotización» sin cambios.
4. Despliegue propio con la lista de comprobación de `docs/operacion/despliegue.md` y la etiqueta `v0.3-doble-envio` ([evidencia-00-07](evidencia-00-07.md)).

> Texto original de las tareas (reemplazado el 2026-10-27 por las decisiones 1 a 3):
> 1. ~~En «Nuevo pedido», desactivar `btn-confirmar-pedido` al primer envío del formulario `pedidoForm` y mostrar que se está procesando, siguiendo el patrón de la 00-06 en el acceso.~~
> 2. ~~Si el envío no ocurre (validación del navegador o del propio JavaScript que lo cancela), el botón vuelve a quedar disponible.~~ Se conserva como criterio.
> 3. ~~Revisión manual en la réplica, en escritorio y a 360 px.~~
> 4. ~~Despliegue propio con la lista de comprobación de `docs/operacion/despliegue.md` y etiqueta propia.~~

## Criterios de aceptación

- [ ] En la réplica, un doble clic rápido en «Crear Pedido» al crear deja un solo pedido nuevo (conteo de pedidos antes y después en la bitácora). ~~«Confirmar» de «Nuevo pedido»~~
- [ ] En la réplica, un doble clic rápido en «Crear Pedido» al editar deja un solo guardado (la edición tampoco se envía dos veces).
- [ ] El botón queda desactivado y muestra «Guardando…» con su ícono tras el primer clic, con contraste y foco visibles (escritorio y 360 px, modo claro y oscuro).
- [ ] Si la validación nativa del navegador impide el envío, el botón sigue disponible.
- [ ] Al volver con «atrás» después de enviar, el botón vuelve a su estado normal (`pageshow`).
- [ ] «Nueva cotización» se comporta igual que antes.
- [ ] `python manage.py test pedidos` sin cambios en el recuento (`Ran 184 tests`, `OK (expected failures=19)`), `check` sin errores y `makemigrations --check --dry-run` sin cambios. **2026-10-27:** `check` sin problemas y `makemigrations` sin cambios; las pruebas no corrieron porque el contenedor MySQL estaba apagado (bitácora).
- [ ] Desplegada con su propia etiqueta, `v0.3-doble-envio`, distinta de `v1.2-capturas`.
- [ ] `v1.2-capturas` apunta al último commit anterior a la 00-07, y `git diff --stat <ese commit>..v0.3-doble-envio` muestra solo `pedido_form.html` y documentos (evidencia, parte B).
- [ ] Una semana después del despliegue, `access.log` no muestra dos `POST /pedidos/nuevo/` en el mismo segundo (evidencia, parte D).

## Fuera de alcance

- **Protección del lado del servidor** (token de envío único o idempotencia) en pedido, cotización y pago: 03-04 (AUD-04-001).
- **Los demás formularios** (cotización, pago, conversión): 03-04. ~~(editar pedido, cotización, pago, conversión)~~ La edición de pedido entra por la decisión 1.
- **Regresión R21** («dos POST idénticos crean un solo pedido»): 03-04. Esta iteración no la escribe, porque un bloqueo en el navegador no la hace pasar.
- Indicador de carga y confirmación visible en todos los envíos: Épica 08 (08-07).
- Detectar o limpiar duplicados históricos: 06-04.
- `index.js`, incluida la validación de montos que busca `btn-submit-pedido` (inexistente): solo se registra como propuesta.
- El texto «Crear Pedido» en modo edición: solo se registra como propuesta.
- La compatibilidad del ícono que gira con `DESIGN.md` (sección 8): pendiente registrado, no se resuelve aquí.

## Datos requeridos del cliente

- Ninguno. Conviene avisar a Manza Gráfica de la ventana del despliegue.

## Decisiones del desarrollador (2026-10-27)

1. **Alcance:** crear y editar pedido (`crear_pedido` y `editar_pedido` renderizan `pedido_form.html`). Las cotizaciones quedan fuera (03-04).
2. **Ubicación del código:** un script propio en `pedido_form.html`, dentro de `{% block scripts %}`, que `base.html` carga después de `index.js` (`base.html:317` y `:319`). No se toca `index.js`: su manejador del id `pedidoForm` alcanza también a `cotizacion_form.html`, y no tocar estáticos evita `collectstatic`.
3. **Indicador:** texto de procesando e ícono que gira, igual que la 00-06 en `login.html` (`disabled`, `aria-busy`, los cuatro elementos `data-*`, cancelar el segundo `submit` y restaurar en `pageshow`). La posible contradicción con `DESIGN.md` (sección 8) queda como pendiente en el registro.
4. **Etiqueta:** `v0.3-doble-envio`. **Destino de retroceso:** `v1.2-capturas`.
5. **Orden en producción (domingo 2026-11-01):** parte D de la 01-06 → `v1.2-capturas` → validación de `v1.2` → `v0.3-doble-envio` → validación. Si `v1.2` se retrocede, la 00-07 se pospone.
6. **Commits y etiquetas:** el desarrollador hace el commit de la 00-07 en `main` esta semana. El domingo, `v1.2-capturas` se crea sobre el último commit anterior a la 00-07 (`git tag -a v1.2-capturas <hash>`) y `v0.3-doble-envio` sobre la punta de `main`.

## Notas

- **2026-10-27 (decisión del desarrollador):** se crea esta iteración y se reabre la Épica 00 solo para ella, en lugar de reabrir la 00-06 (terminada y desplegada como `v0.2-correcciones`). Origen: P4 de la Auditoría 04.
- **2026-10-27 (decisiones 1 a 6):** se ajustan objetivo, tareas, criterios, cabecera y fuera de alcance; el texto anterior queda tachado ([bitacora-00-07](../../99_bitacora/epica-00-blindaje/bitacora-00-07.md)).
