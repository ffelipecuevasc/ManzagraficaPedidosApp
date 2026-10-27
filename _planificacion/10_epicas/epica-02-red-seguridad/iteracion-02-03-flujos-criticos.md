# Iteración 02-03 · Pruebas de flujos críticos

- **Épica:** 02 · Red de seguridad
- **Estado:** Redactada, sin ejecutar
- **Subfase del plan:** 2.3
- **Depende de:** 02-01 (la 02-02 no es requisito, pero conviene haberla hecho para reutilizar sus factorías)
- **RDA relacionadas:** RDA-006
- **Hallazgos que avanza:** AUD-01-015 (cero pruebas), AUD-02-013 (clasificación de pedidos atrasados y sin fecha) y AUD-02-014 (valor de la cotización al convertirla). No cierra ninguno.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no despliega nada: solo agrega pruebas)

## Objetivo

Probar de punta a punta los flujos que el equipo usa a diario, **tal como funcionan hoy**: una petición HTTP entra por la URL, atraviesa la vista, el formulario, el ORM y MySQL, y se comprueba el estado final de la base. Son pruebas de integración con el cliente de pruebas de Django (`self.client`) y de **caracterización**: congelan el comportamiento actual para que las Épicas 03 y 04 puedan cambiarlo a propósito y con el cambio visible.

Los fallos de estos flujos (ítems perdidos, doble conversión, escrituras por GET) **no** se prueban aquí: son regresiones y van en 02-04.

## Punto de partida (a verificar leyendo el código antes de escribir)

- Rutas en `pedidos/urls.py`: `crear_pedido` (`pedidos/nuevo/`), `editar_pedido` (`pedido/editar/<pk>/`), `cambiar_estado` (`pedido/<pk>/cambiar/<nuevo_estado>/`), `duplicar_pedido` (`pedido/duplicar/<pk>/`), `crear_cotizacion`, `editar_cotizacion` y `convertir_a_pedido` (`cotizaciones/convertir/<pk>/`).
- Hoy `cambiar_estado` y `duplicar_pedido` modifican datos con una petición **GET** (AUD-02-006 y el plan, subfase 4.1). Las pruebas de esta iteración usan el método actual, pero lo concentran en una ayuda de pruebas (tarea 1), para que 04-01 cambie una sola línea.
- Los ítems viajan en el campo `items_json` del formulario. `crear_pedido` y las vistas de edición los procesan dentro de un `try/except` amplio que, desde la 01-03 y la 01-09, registra el error con `logger.exception`.
- `duplicar_pedido` crea un pedido nuevo copiando cliente, resumen, detalles, valor, fecha de entrega e imagen de referencia; deja el estado en `PENDIENTE`. Según el plan, **no copia ítems**. El agente confirma qué más copia o deja de copiar (pagos, `creado_por`, `estado_pago`).
- `convertir_a_pedido` lee la fecha y el abono desde `request.POST` sin formulario de Django y copia `valor_total` de la cotización a `valor_venta` del pedido (AUD-02-014).
- Los eventos de negocio (`RegistroEvento`, 15 tipos) se escriben desde estas vistas; el agente verifica en `pedidos/eventos.py` el nombre de cada tipo.

## Tareas

1. **Ayudas de pruebas.** Un módulo `pedidos/tests/ayudas.py` con: enviar el formulario de ítems (`items_json`) con datos válidos, cambiar el estado de un pedido (aquí vive el método HTTP actual) y congelar la hora (la solución elegida en 02-02). Cada ayuda lleva su prueba.
2. **Crear pedido** (`test_pedidos.py`): el formulario responde 200; un POST válido con dos ítems redirige y crea el pedido con `creado_por` y estado `PENDIENTE`; los ítems quedan asociados con su cantidad (`Decimal`) y su **precio histórico congelado**: si después se cambia `valor_neto` del producto, el `precio_unitario` del ítem no cambia. Un abono inicial crea un `Pago` con su método (por defecto `EFECTIVO`), su nota y quién lo registró; sin abono, no hay pagos. Queda escrito el evento de negocio que corresponda.
3. **Editar pedido:** cambiar campos y `valor_venta`; reemplazar los ítems (los anteriores desaparecen y los nuevos quedan); el evento de modificación. El camino de fallo a mitad del guardado es la regresión de 02-04.
4. **Cotizaciones** (`test_cotizaciones.py`): crear y editar con ítems, igual que en los pedidos; el estado inicial y la fecha de vencimiento.
5. **Convertir cotización en pedido:** el camino feliz. Se comprueba qué pasa con el cliente, el resumen, los detalles, el valor (`valor_total` pasa a `valor_venta`, `PENDIENTE_CLIENTE` por AUD-02-014), los ítems (todos, con cantidad y precio), el estado de la cotización, y el abono y la fecha que llegan por POST. La doble conversión es regresión de 02-04.
   - **Valor neto o con IVA (AUD-02-014, decidido el 2026-10-26):** una prueba fija que `valor_venta` del pedido es igual a `valor_total` de la cotización, sin sumar IVA, con el comentario `PENDIENTE_CLIENTE` (¿el valor de la cotización es neto o incluye IVA?). La 02-02 no lo cubrió porque el modelo no calcula nada con `valor_total`.
6. **Cambiar estado:** cada transición válida entre `PENDIENTE`, `EN_PROCESO`, `TERMINADO` y `ENTREGADO`; un estado inexistente (la respuesta real, sea un rechazo, un 404 o un error, se fija tal cual); si la vista permite retroceder un estado, también se fija. El agente informa qué hace hoy la vista antes de escribir la prueba.
7. **Duplicar pedido:** qué se copia y qué no (cliente, resumen, detalles, valor, fecha de entrega e imagen se copian; ítems y pagos, según lo que se observe), el estado `PENDIENTE`, que el pedido nuevo tiene otro `pk` y fecha de solicitud actual, y a dónde redirige. `PENDIENTE_CLIENTE`: ¿deberían copiarse los ítems? Toda prueba con imagen usa un `MEDIA_ROOT` temporal.
8. **Clasificación del panel y del trabajo semanal** (AUD-02-013): con la hora fijada a mediodía de Chile, la combinación de estado (`PENDIENTE`, `EN_PROCESO`, `TERMINADO`, `ENTREGADO`) con fecha de entrega (atrasada, de esta semana, futura, sin fecha) y en qué categoría cae cada pedido. Un `ENTREGADO` atrasado y un pedido sin fecha quedan `PENDIENTE_CLIENTE`.
9. **Documentación.** En `docs/operacion/pruebas.md`, una sección «Flujos fijados» con la tabla de flujos, qué comprueba cada prueba y cuáles dependen del método GET actual (para 04-01). En `registro-pendientes.md`, sección 2, el nombre de la prueba que fija cada dato del cliente.
10. **Bitácora** `bitacora-02-03.md` con la salida de `test pedidos -v 2` y el recuento.

## Criterios de aceptación

- [ ] Existen `test_pedidos.py` y `test_cotizaciones.py` en `pedidos/tests/`, más el módulo de ayudas, con pruebas por cada tarea 2 a 8.
- [ ] El precio histórico del ítem se comprueba como congelado.
- [ ] Cada regla sin confirmar (ítems al duplicar, `ENTREGADO` atrasado, pedidos sin fecha, valor de la cotización) tiene su comentario `PENDIENTE_CLIENTE` y figura en `registro-pendientes.md`.
- [ ] Las pruebas que dependen de que `cambiar_estado` o `duplicar_pedido` usen GET lo declaran en un comentario y pasan por la ayuda de la tarea 1.
- [ ] Ninguna prueba escribe fuera de la base de pruebas ni en el `media/` real; ninguna ejecuta `mysql` ni `mysqldump`.
- [ ] `python manage.py test pedidos` en verde (más las nuevas) en tres ejecuciones seguidas; `check` sin errores; `makemigrations --check --dry-run` sin cambios.
- [ ] El diff no toca código de la aplicación.
- [ ] Las decisiones `PENDIENTE_DESARROLLADOR` quedaron resueltas y registradas.

## Fuera de alcance

- Los caminos de fallo y los defectos conocidos (pérdida de ítems, `estado_pago`, doble conversión, escritura por GET, eliminar pago): 02-04.
- Cálculos de dinero: 02-02. Control de acceso: 02-05.
- Pruebas de plantillas, JavaScript o PDF (la generación de PDF ya tiene su prueba de arranque).

## Decisiones del desarrollador

1. **Flujos de pagos** (`ingresar_pago`, `editar_pago`): el plan no los lista, pero mueven dinero. Propuesta: incluir el camino feliz de registrar y editar un pago, sin tocar `eliminar_pago` (regresión en 02-04). `PENDIENTE_DESARROLLADOR`.
2. **Pantallas de lectura** (detalle y listado de pedidos con filtros y paginación): propuesta, solo el detalle, porque lo usan las redirecciones. `PENDIENTE_DESARROLLADOR`.
3. **Transiciones de estado:** si la vista hoy permite cualquier cambio, se fija así y se anota; no se decide aquí qué transiciones deberían existir. `PENDIENTE_DESARROLLADOR` solo si el agente encuentra reglas que contradigan el plan.

## Datos requeridos del cliente

- Ninguno para ejecutar. Se usan como `PENDIENTE_CLIENTE`: si al duplicar se copian los ítems; si un pedido `ENTREGADO` atrasado es crítico y cómo se tratan los pedidos sin fecha de entrega (AUD-02-013); y si el valor de la cotización es neto o incluye IVA (AUD-02-014).