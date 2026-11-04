# Bitácora 03-03 · Fronteras transaccionales por vista

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión. Falta la revisión manual del desarrollador (pantallas a 360 px y en escritorio). Sin despliegue propio: viaja con la 03-05.

## Resumen

Se ejecutó la iteración 03-03 con las ocho decisiones del desarrollador del 2026-11-04 (todas la opción A). Siete vistas de escritura compuesta abren un único `transaction.atomic()` y la excepción sale del bloque: `editar_pedido`, `crear_cotizacion`, `editar_cotizacion`, `convertir_a_pedido`, `ingresar_pago`, `editar_pago` y `eliminar_pago` (`crear_pedido` ya lo tenía desde la 03-02). `estado_pago` se recalcula dentro de la misma transacción al crear con abono, al editar el pedido y al editar un pago (el pedido anterior y el nuevo). La conversión bloquea la cotización, rechaza una ya aceptada y valida fecha y abono con un formulario. Pasan a verde R1, R2, R4, R10, R11, R12, R13 y R18 y los fallos esperados bajan de 17 a **9**, igual que la predicción. Sin migraciones, sin `messages.*` nuevos y sin validar ni recalcular el precio del ítem.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/views.py` | `editar_pedido`, `crear_cotizacion`, `editar_cotizacion`, `ingresar_pago`, `editar_pago` y `eliminar_pago` con `transaction.atomic()` y sin `except Exception` (se quitaron las tres capturas y sus comentarios «se corrige en 03-02»). `crear_pedido` recalcula `estado_pago` tras el pago inicial. `convertir_a_pedido` reescrita: bloqueo con `select_for_update`, rechazo de una cotización `ACEPTADA` (GET y POST), `ConversionCotizacionForm`, un solo `atomic`. `actualizar_estado_pago_pedido` guarda solo `estado_pago` (`update_fields`). `ingresar_pago` deja de repetir la lógica en línea. |
| `pedidos/forms.py` | `ConversionCotizacionForm` (fecha de entrega requerida; abono entero ≥ 0, vacío = 0, no mayor que el total cuando este es > 0). |
| `pedidos/templates/pedidos/cotizacion_convertir.html` | Errores junto a la fecha y al abono (`text-red-600`, `role="alert"`, `aria-invalid`, `aria-describedby`), valores y método de pago conservados al volver con errores. |
| `pedidos/tests/test_fronteras_transaccionales.py` | **Nuevo:** 34 pruebas (ítems fallidos en tres vistas con cinco causas, atomicidad de pagos y conversión, `estado_pago`, conversión repetida y formulario). |
| `pedidos/tests/test_regresiones.py` | R1, R2, R4, R10, R11, R12, R13 y R18 sin `@expectedFailure` ni `@tag('regresion')`; `raise_request_exception = False` en `ItemsTodoONadaTests` y `absorber_errores` con `django.request`; encabezado y comentario de R19 (04-01). |
| `pedidos/tests/test_capturas_amplias.py` | Se retiró `CapturasItemsTests` (3 pruebas, ya no son ciertas: las vistas responden 500) y la constante y los imports que quedaron sin uso. |
| `pedidos/tests/test_cotizaciones.py` | `test_abono`: salen los casos «no numérico» y «negativo» (ahora se rechazan, `ConversionFormularioTests`) y cada caso devuelve la cotización a `ENVIADA`, porque antes dependía de poder convertir la misma cotización varias veces (R13). |
| `docs/operacion/pruebas.md` | Valor vigente 9; filas de R1, R2, R4, R10 a R13 y R18 retiradas; viñetas, con la nota fechada de R18; fila de R19 a la 04-01; sección 9 (conversión). |
| `docs/operacion/despliegue.md` | Sección 3.7: imágenes de referencia sin pedido (decisión 2-A). |
| `_planificacion/10_epicas/epica-03-integridad-transaccional/iteracion-03-03-fronteras-transaccionales-por-vista.md` | Estado «En revisión», decisiones con fecha, criterios marcados y «Resultado de la ejecución». |
| `_planificacion/00_producto/auditoria-tecnica.md` | Notas «Resuelto en 03-03» en AUD-01-001, AUD-01-002, AUD-02-004, AUD-02-005, AUD-02-008 y AUD-02-027; nota en AUD-02-028 (04-01) y en AUD-02-014 (sigue abierto). |
| `_planificacion/00_producto/registro-pendientes.md` | Cabecera, fila 03-03 «En revisión», decisiones resueltas, dos propuestas en la sección 4 (abono de la edición y `estado_pago` históricos con la cifra) e historial. |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-04-regresiones.md` | Notas del 2026-11-04: R18 pasó a la 03-03 (reemplaza la D5) y R19 a la 04-01. |
| `_planificacion/10_epicas/epica-04-seguridad/definicion-epica-04.md` | «Para la redacción de 04-01»: `creado_por` al duplicar (R19). |
| `_planificacion/10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md` | Nota fechada. El estado de la épica no cambia. |
| `_planificacion/99_bitacora/epica-03-integridad-transaccional/bitacora-03-03.md` | Esta bitácora (nueva). |

## Verificación

Todo con `DB_NAME=manzagrafica_replica` y el MySQL local de Docker. Las pruebas usan la base `test_manzagrafica`. No se consultaron datos de la réplica.

### Paso 0 · línea de partida

`python manage.py test pedidos` → 189 pruebas, `OK (expected failures=17)` (172,7 s).

### Pasos 1 y 6 · las pruebas fallaban por la razón correcta (antes de corregir)

Con las marcas ya quitadas y las vistas sin tocar:

| Prueba | Fallo observado | Motivo |
| :----- | :-------------- | :----- |
| R1 | `[(2, Decimal('3.00'), 4000)] != [(1, Decimal('1.00'), 10000)]` | Ítems anteriores perdidos (datos, no excepción) |
| R2 | `[(4, Decimal('3.00'), 4000)] != [(3, Decimal('1.00'), 10000)]` | Igual, en cotizaciones |
| R4 | `(1, 1) != (0, 0)` | Cotización con ítem parcial |
| R10 | `'PENDIENTE' != 'PARCIAL'` | `estado_pago` sin recalcular |
| R11 | `'PAGADO' != 'PARCIAL'` | Idem |
| R12 | `'PAGADO' != 'PENDIENTE'` | El pedido anterior no se recalcula |
| R13 | `2 != 1` | Dos pedidos |
| R18 | `ERROR` | `ValidationError` por la fecha vacía (excepción, como se había descrito) |

También fallaban las pruebas nuevas de atomicidad (el pago, el pedido o la cotización seguían tras un fallo), de las vistas (todavía tenían `except Exception`) y de la conversión repetida. Primera tanda: 14 pruebas, `failures=25`. Segunda: 29 pruebas, `failures=21, errors=7`.

### Después de corregir

- Pruebas de los dominios tocados: 101 pruebas, `OK (expected failures=9)`.
- Suite completa, `python manage.py test pedidos`, tres ejecuciones: **220 pruebas** (189 − 3 retiradas + 34 nuevas), `OK (expected failures=9)` en todas (223,8 s, 214,0 s y 211,3 s). Sin `unexpected successes`, `failures` ni `errors`.
- `python manage.py check` → `System check identified no issues (0 silenced).`
- `python manage.py makemigrations --check --dry-run` → `No changes detected`.
- **N real de fallos esperados: 9; predicción: 9.** Son R6a, R6b, R6c, R7, R8, R9, R14, R15 y R19.
- Un tropiezo: tras el primer cambio, `test_abono` (dos casos) falló con `Pedido.DoesNotExist`. No era un defecto: la prueba convertía la misma cotización en cada caso y el rechazo de la segunda conversión (R13) lo impide. Se corrigió la prueba (ver la tabla de archivos).
- **Consultas por vista (regla 12):** no se midieron. Por lectura, el recálculo de `estado_pago` agrega 2 o 3 agregados y un `UPDATE` por escritura. Son vistas de escritura, no listados ni detalles.

## Migraciones

- Ninguna (`makemigrations --check --dry-run`: `No changes detected`).

## Criterios de aceptación

Ver la iteración: todos marcados salvo la **revisión manual** (la hace el desarrollador, más abajo).

## Decisiones tomadas

Del desarrollador, 2026-11-04 (todas la opción A): 1 propagar el error; 2 aceptar huérfanas y documentarlo; 3 formulario con fecha, abono y estado (reemplaza la D5 del 2026-10-27, que dejaba R18 y AUD-02-027 en la 03-04); 4 redirigir al detalle de la cotización, sin mensaje; 5 R19 a la 04-01; 6 no reparar los `estado_pago` históricos (610 de 870, medición del 2026-10-20); 7 una sola iteración; 8 el abono de la edición, fuera de alcance. Estado «Pendiente (redactada)» mientras no se ejecuta, sin editar el README protegido.

Del agente, dentro del alcance:

- **`update_fields=['estado_pago']`** en el ayudante: `editar_pago` recalcula con el pedido anterior leído antes de armar el formulario, y un `save()` completo podría pisar otros campos con valores viejos.
- **`crear_pedido` recalcula solo si hay abono,** para no cambiar el estado de un pedido sin pagos. `editar_pedido` recalcula siempre (es idempotente); un pedido de $0 queda `PAGADO` según la regla provisoria del oráculo (`PENDIENTE_CLIENTE`).
- **`select_for_update`** en la conversión: con un solo worker las peticiones van en serie y la comprobación de estado bastaría (inferido), pero el bloqueo no depende de esa configuración.
- **El método de pago de la conversión** se sigue leyendo de la petición sin validar, como antes: la decisión 3-A pide fecha, abono y estado.
- **Rechazo de una cotización aceptada también por GET,** como ya hacía `editar_cotizacion`.
- **El `messages.success` de la conversión exitosa se conserva** (ya existía); no se agregó ningún `messages.*`.
- **Texto de errores del formulario** en español de Chile y con `red-600` (4,83:1 sobre blanco según `DESIGN.md`) en lugar del `red-500` de otras plantillas.

## Pendientes y riesgos

- **Revisión manual del desarrollador** (más abajo). Los pedidos y cotizaciones de prueba quedan en la réplica y se limpian al refrescarla al cierre de la Épica 03 (AUD-05-002).
- **Hasta la 03-04,** un ítem fallido al crear o editar un pedido o una cotización muestra la página 500 y el formulario se pierde. Los datos quedan íntegros. Viaja con la 03-05, junto con la 03-04.
- **Imagen de referencia:** si se revierte un pedido con imagen, el archivo queda en `media/referencias/` (decisión 2-A; guía en `despliegue.md`).
- **`estado_pago`:** el código nuevo no repara las filas históricas. Hoy ninguna plantilla ni el admin lo leen (por búsqueda), así que no se ve en pantalla.
- **Observación sin tocar:** el `<input>` del abono lleva `max="{{ cotizacion.valor_total }}"`, y con un total de $0 el navegador bloquea cualquier abono mientras el servidor lo acepta (misma regla que el pedido; `PENDIENTE_CLIENTE`).
- **AUD-02-014** sigue abierto: la conversión copia `valor_total` sin IVA.
- **La 03-04 no se redactó.** Debe saber que R18 ya está resuelta y que los mensajes de Django solo se muestran en `restaurar_bd.html`.

## Revisión manual (pendiente, la hace el desarrollador)

Contra la réplica local, con `DEBUG=False`. En cada paso con error mira escritorio y 360 px (DevTools: Ctrl+Mayús+M y ancho 360). Los datos de prueba se limpian al refrescar la réplica.

**0. Preparar (PowerShell 7).**

```powershell
cd "D:\Trabajo\Proyectos PYTHON\Proyectos Personales\Pedidos Manzagrafica\PedidosApp"
docker compose up -d
.\.venv\Scripts\Activate.ps1
$env:DB_NAME = 'manzagrafica_replica'
$env:DEBUG = 'False'
python manage.py runserver --insecure
```

Deja esa terminal abierta: los errores aparecen ahí como `nivel=ERROR registrador=django.request`. Abre `http://127.0.0.1:8000/` e inicia sesión.

**Fragmento para forzar un ítem fallido** (consola del navegador, F12). Úsalo con la tabla de ítems ya cargada y **no toques la tabla después**, porque la página reescribe el campo:

```js
const c = document.getElementById('input-items-json');
const primero = JSON.parse(c.value)[0];
c.value = JSON.stringify([primero, {producto_id: '999999', cantidad: '1', precio_unitario: 1000}]);
```

**1. Editar un pedido con un ítem fallido** (usa el pedido de prueba #910, que tiene un ítem).
1. Abre `http://127.0.0.1:8000/910/` y anota el valor de venta y el ítem.
2. Abre `http://127.0.0.1:8000/pedido/editar/910/`, cambia el valor de venta a `99999`, pega el fragmento y pulsa «Editar Pedido».
3. Esperado: la página 500 de la aplicación.
4. Vuelve a `http://127.0.0.1:8000/910/`: el valor de venta y el ítem siguen como en el punto 1.
5. En la terminal del servidor: **una** línea `django.request` con `ruta=/pedido/editar/910/` y `DoesNotExist`.

**2. Crear una cotización con un ítem fallido.**
1. Abre `http://127.0.0.1:8000/cotizaciones/lista/` y anota cuántas hay.
2. Abre `http://127.0.0.1:8000/cotizaciones/nueva/`, llena los datos, agrega un ítem con el botón de la página, pega el fragmento y envía.
3. Esperado: página 500, una línea `django.request` con `ruta=/cotizaciones/nueva/` y ninguna cotización nueva en la lista.

**3. Crear una cotización válida** para los pasos 4 a 6: el mismo formulario, sin el fragmento. Anota su número `N` (URL `…/cotizaciones/detalle/N/`).

**4. Editar esa cotización con un ítem fallido.**
1. Abre `http://127.0.0.1:8000/cotizaciones/editar/N/`, cambia el resumen, pega el fragmento y envía.
2. Esperado: página 500; en `…/cotizaciones/detalle/N/` siguen el resumen y el ítem anteriores.

**5. Convertir con datos inválidos** (la cotización de `N`, que sigue sin convertir).
1. Abre `http://127.0.0.1:8000/cotizaciones/convertir/N/`.
2. Abono mayor que el total: en la consola pega y pulsa «Confirmar»:

```js
document.querySelector('form').noValidate = true;
const a = document.getElementById('valor_abonado');
a.removeAttribute('max');
a.value = '99999999';
```

   Esperado: vuelve la página con «El abono no puede ser mayor al valor total de la cotización.» bajo el campo, el valor escrito conservado y nada creado.
3. Fecha vacía: recarga la página y pega esto, luego «Confirmar»:

```js
document.querySelector('form').noValidate = true;
document.getElementById('fecha_entrega').value = '';
```

   Esperado: «Indica para cuándo es el trabajo.» bajo la fecha.
4. Comprueba en `http://127.0.0.1:8000/pedidos/lista/` que no apareció ningún pedido y que `…/cotizaciones/detalle/N/` no dice ACEPTADA.

**6. Convertir bien y repetir.**
1. En `…/cotizaciones/convertir/N/` deja la fecha sugerida, pon un abono (por ejemplo `10000`, menor que el total) y pulsa «Confirmar». Anota el número `P` del pedido nuevo.
2. Pulsa «Atrás» del navegador y «Confirmar» otra vez (o abre de nuevo la URL de convertir).
3. Esperado: vuelves a `…/cotizaciones/detalle/N/` con la etiqueta ACEPTADA y sin botón «Convertir», sin mensaje; en `…/pedidos/lista/` hay **un solo** pedido nuevo.

**7. Mover un pago de pedido.**
1. En `http://127.0.0.1:8000/pagos/lista/` abre el pago del pedido `P` y edítalo para pasarlo al pedido #910.
2. Esperado: en `…/910/` y en `…/P/` el saldo y el porcentaje pagado cambian como corresponde.
3. Opcional, solo lectura, para ver `estado_pago` (no se muestra en ninguna pantalla):

```powershell
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" manzagrafica_replica -e "SELECT id, valor_venta, estado_pago FROM pedidos_pedido WHERE id IN (910, P);"'
```

   (cambia `P` por el número). Esperado: `PAGADO` si el saldo es 0 o menos, `PARCIAL` si hay pagos y saldo, `PENDIENTE` si no hay pagos.

**8. Crear un pedido con abono.** En `http://127.0.0.1:8000/pedidos/nuevo/` crea uno con valor `10000` y abono `4000`; la consulta anterior con su número debe dar `PARCIAL`.

**9. Cerrar.** Ctrl+C en la terminal del servidor y `docker compose stop`. Avísame el resultado de cada paso; si todos salen bien, marco el último criterio de la iteración.

## Commit sugerido

`Épica 3 - Iteración 03-03: fronteras transaccionales por vista; R1, R2, R4, R10-R13 y R18 pasan a verde y los fallos esperados bajan de 17 a 9`
