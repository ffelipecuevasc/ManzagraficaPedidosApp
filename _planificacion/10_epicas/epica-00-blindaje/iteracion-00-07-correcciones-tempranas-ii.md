# Iteración 00-07 · Correcciones tempranas II

- **Épica:** 00 · Blindaje y punto de retorno (reabierta el 2026-10-27 solo para esta iteración)
- **Estado:** Pendiente
- **Subfase del plan:** 0.6 (continuación; nueva, por hallazgos de producción del 2026-10-27)
- **Depende de:** 00-05 (protocolo de despliegue)
- **RDA relacionadas:** RDA-007
- **Hallazgos que cierra:** ninguno por completo. Avanza AUD-04-001 (el lado del servidor queda en la 03-04).
- **Cambio de esquema:** Ninguno (solo plantilla o JavaScript; riesgo de Clase 1 en el sentido de que no toca datos ni estructura)
- **Respaldo previo al despliegue:** No (no toca datos), pero sí etiqueta y despliegue propios

## Objetivo

Que un doble clic en «Confirmar» de «Nuevo pedido» no cree dos pedidos, con una corrección mínima del lado del cliente que se despliega sola, antes de que la Épica 03 pueda empezar.

## Contexto

El 2026-10-27 a las 14:36:20, dos `POST /pedidos/nuevo/` en el mismo segundo crearon dos pedidos (AUD-04-001). El botón `btn-confirmar-pedido` de `pedido_form.html` no se desactiva al enviar. La 00-06 resolvió lo mismo en el acceso y dejó «los demás formularios» para la 03-04. Esta iteración adelanta solo el formulario donde el defecto está verificado; la 00-06 no se reabre.

## Tareas

1. En «Nuevo pedido», desactivar `btn-confirmar-pedido` al primer envío del formulario `pedidoForm` y mostrar que se está procesando, siguiendo el patrón de la 00-06 en el acceso.
2. Si el envío no ocurre (validación del navegador o del propio JavaScript que lo cancela), el botón vuelve a quedar disponible.
3. Revisión manual en la réplica, en escritorio y a 360 px.
4. Despliegue propio con la lista de comprobación de `docs/operacion/despliegue.md` y etiqueta propia.

## Criterios de aceptación

- [ ] En la réplica, un doble clic rápido en «Confirmar» de «Nuevo pedido» crea un solo pedido (conteo de pedidos antes y después en la bitácora).
- [ ] El botón queda desactivado y muestra que se está procesando tras el primer clic, con contraste y foco visibles (escritorio y 360 px).
- [ ] Si el formulario no se envía por un error de validación del navegador, el botón vuelve a estar disponible.
- [ ] `python manage.py test pedidos` sin cambios en el recuento (184 pruebas, 19 fallos esperados) y `check` sin errores.
- [ ] Desplegada con su propia etiqueta, distinta de `v1.2`.
- [ ] Una semana después del despliegue, `access.log` no muestra dos `POST /pedidos/nuevo/` en el mismo segundo (evidencia del desarrollador).

## Fuera de alcance

- **Protección del lado del servidor** (token de envío único o idempotencia) en pedido, cotización y pago: 03-04 (AUD-04-001).
- **Los demás formularios** (editar pedido, cotización, pago, conversión): 03-04.
- **Regresión R21** («dos POST idénticos crean un solo pedido»): 03-04. Esta iteración no la escribe, porque un bloqueo en el navegador no la hace pasar.
- Indicador de carga y confirmación visible en todos los envíos: Épica 08 (08-07).
- Detectar o limpiar duplicados históricos: 06-04.

## Datos requeridos del cliente

- Ninguno. Conviene avisar a Manza Gráfica de la ventana del despliegue.

## Notas

- **2026-10-27 (decisión del desarrollador):** se crea esta iteración y se reabre la Épica 00 solo para ella, en lugar de reabrir la 00-06 (terminada y desplegada como `v0.2-correcciones`). Origen: P4 de la Auditoría 04.
