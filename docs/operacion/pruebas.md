# Pruebas automatizadas

Cómo se ejecutan y se escriben las pruebas de Manza Gráfica App. Infraestructura creada en la iteración 02-01 (RDA-006). Comandos en PowerShell 7.

## 1. Requisitos

- El contenedor MySQL local encendido (`docker compose up -d`, ver `replica-local.md`).
- El entorno virtual activo y el `.env` con las variables `DB_*`.

## 2. Comandos

```powershell
# Todas las pruebas (comando oficial de la lista de despliegue)
python manage.py test pedidos

# Con el detalle de cada prueba y el nombre de la base de pruebas
python manage.py test pedidos -v 2

# Solo las pruebas que deben pasar (excluye las regresiones que fallan a propósito)
python manage.py test pedidos --exclude-tag regresion

# Un dominio o una clase
python manage.py test pedidos.tests.test_eventos
python manage.py test pedidos.tests.test_eventos.RegistroEventoTests
```

Resultado esperado: `OK`. Si hay regresiones declaradas, `OK (expected failures=N)`, donde N es el número de pruebas marcadas con `regresion`.

## 3. La base de pruebas

- **Nombre fijo: `test_manzagrafica`** (`DATABASES['default']['TEST']` en `settings.py`). No depende de `DB_NAME`: da lo mismo si apuntas a la réplica o a la base local.
- **Nunca puede ser `manzagrafica_replica` ni `manzagrafica_local`.** Django destruye la base de pruebas al terminar. `settings.py` detiene la carga con `ImproperlyConfigured` si el nombre de la base de pruebas coincide con una base real o con la base activa.
- Django la **crea al empezar y la destruye al terminar** (líneas `Creating test database` y `Destroying test database` de `-v 2`). Las bases reales no se tocan.
- Si una ejecución se interrumpe y la base queda creada, la siguiente pregunta si se puede borrar: responde `yes`. En una ejecución sin atención, usa `--noinput`, que la borra y la vuelve a crear.
- **Juego de caracteres y colación** fijados en `TEST`: `utf8mb4` y `utf8mb4_unicode_ci`, los de producción (`linea-base-produccion.md`, sección 5). La zona horaria viene del servidor (UTC, `compose.yaml`).
- `test_entorno.py` comprueba en cada ejecución el nombre, el juego de caracteres, la colación, la zona horaria y el modo SQL.

## 4. Modo SQL

Las pruebas corren **sin modo estricto** (`NO_ENGINE_SUBSTITUTION`), igual que producción (decisión 02-01, opción A, AUD-02-020). Por eso `test` muestra la advertencia `mysql.W002`: es esperada y no se silencia, porque silenciarla la ocultaría también en `check --deploy`.

Una prueba que dependa del truncado o el ajuste silencioso de MySQL (un texto más largo que la columna, un número fuera de rango) lo declara con un comentario `# Depende del truncado silencioso (AUD-02-020)`, para revisarla cuando 04-05 evalúe el modo estricto.

## 5. Organización

Paquete `pedidos/tests/`, un archivo por dominio:

| Archivo | Contenido |
| :------ | :-------- |
| `factorias.py` | Funciones que construyen datos de prueba |
| `test_entorno.py` | Configuración de la base de pruebas |
| `test_factorias.py` | Coherencia de las funciones de datos |
| `test_arranque.py` | Carga diferida de bibliotecas pesadas |
| `test_rutas_publicas.py` | Rutas sin sesión (`robots.txt`) |
| `test_pagos.py` | Pagos |
| `test_eventos.py` | Registro de eventos, su purga y el servicio `registrar_evento` |
| `test_registro.py` | Formato, emoji por nivel y niveles del registro de la aplicación (`LOGGING`) |
| `test_errores.py` | Páginas 404 y 500 y trazas completas |
| `test_eventos_negocio.py` | Un evento por operación del inventario y lecturas sin eventos |
| `test_admin_eventos.py` | Admin de eventos: solo lectura, solo superusuarios, filtros, búsqueda y consultas |
| `test_dinero.py` | Lógica de dinero: IVA, saldos, ítems, abono inicial y cifras del panel con oráculo (02-02) |
| `ayudas.py` | Ayudas de los flujos: `items_json`, `cambiar_estado` y `duplicar` (método HTTP actual) y `congelar_hora` (02-03) |
| `test_pedidos.py` | Flujos de pedidos y pagos: crear, editar, cambiar estado, duplicar, clasificación, detalle, ingresar y editar pago (02-03) |
| `test_cotizaciones.py` | Flujos de cotizaciones: crear, editar y convertir en pedido (02-03) |

Las iteraciones siguientes agregan los archivos que necesiten (por ejemplo `test_regresiones.py`, `test_acceso.py`). No se crean archivos vacíos.

## 6. Datos de prueba

- Se construyen con las funciones de `pedidos/tests/factorias.py` (`crear_usuario`, `crear_superusuario`, `crear_cliente`, `crear_producto`, `crear_pedido`, `crear_item_pedido`, `crear_pago`, `crear_cotizacion`, `crear_item_cotizacion`, `crear_evento` y `momento_chile`, que entrega un instante en hora de Chile, por defecto el mediodía). Nunca accesorios estáticos (`fixtures` JSON).
- Cada función tiene valores por defecto válidos; la prueba pasa solo lo que le importa: `crear_pedido(items=[{'cantidad': '2.5', 'precio_unitario': 4_000}])`.
- Datos ficticios, montos enteros en pesos, cantidades con `Decimal` y fechas con `timezone`.
- Las funciones **no aplican reglas de negocio** de las vistas (no recalculan `valor_venta` ni `estado_pago`): esas reglas son lo que se prueba.
- Sin dependencias externas (decisión 02-01).

## 7. Regresiones que fallan a propósito

Una prueba que demuestra un defecto todavía sin corregir se marca así:

```python
from unittest import expectedFailure

from django.test import TestCase, tag


class EliminarPagoTests(TestCase):
    @tag('regresion')
    @expectedFailure  # AUD-02-002: se corrige en 03-0X. Quitar la marca al corregir.
    def test_eliminar_pago_responde_200(self):
        ...
```

- El resumen de `test` las cuenta aparte: `expected failures=N`. Un `failures` es siempre un fallo nuevo.
- Si el defecto se corrige y la prueba pasa, aparece como `unexpected successes` y el conjunto **falla**: hay que quitar `@expectedFailure` (y la etiqueta) en la misma iteración que corrige.
- No se usa `skip`: no ejecuta la prueba y no avisa cuando el defecto se corrige.

## 8. Reglas de dinero fijadas

Pruebas de caracterización de la iteración 02-02, en `pedidos/tests/test_dinero.py`: fijan cómo calcula **hoy** la aplicación, sea correcto o no. Cambiar una de estas reglas obliga a cambiar su prueba en la misma iteración, con la decisión que lo respalda.

| Regla | Valor actual | Prueba que la fija | `PENDIENTE_CLIENTE` |
| :---- | :----------- | :----------------- | :------------------ |
| IVA de un producto | `int(round(valor_neto * 0.19))`: `float` y redondeo de las mitades al par (150 → 28, 350 → 66, 4.950 → 940) | `IvaProductoTests.test_iva_y_valor_bruto_guardados` | No |
| Diferencia con el redondeo comercial (mitad hacia arriba) | A lo más $1, solo en las mitades que el redondeo al par baja; se anota, no es regresión (decisión D1) | `IvaProductoTests.test_oraculo_comercial_difiere_solo_en_las_mitades_al_par` | No |
| Valor bruto | `valor_neto + iva`, recalculado en cada `save()` | `IvaProductoTests.test_invariante_bruto_igual_neto_mas_iva`, `test_recalcula_al_cambiar_valor_neto` | No |
| Valor neto negativo | Se acepta: -1.000 da IVA -190 | `IvaProductoTests.test_iva_y_valor_bruto_guardados` | No |
| Total pagado y saldo | Suma de los pagos del pedido o 0; saldo = valor de venta − pagado | `SaldoPedidoTests.test_matriz_de_saldos`, `test_pagos_de_otro_pedido_no_se_mezclan` | No |
| Sobrepago | Se acepta: saldo negativo y porcentaje mayor que 100 | `SaldoPedidoTests.test_matriz_de_saldos` (caso «sobrepago») | Sí |
| Pedido de $0 | Porcentaje pagado 100, con o sin pagos | `SaldoPedidoTests.test_matriz_de_saldos` (casos «valor 0») | Sí |
| Porcentaje pagado | `int(pagado / valor * 100)`: trunca (1/3 → 33, 99,9 % → 99) y arrastra el error del `float` (29 de 100 → 28) | `SaldoPedidoTests.test_matriz_de_saldos` | No |
| Monto de un pago | Entero no negativo (`PositiveIntegerField`) | `SaldoPedidoTests.test_monto_de_pago_no_admite_negativos_ni_decimales` | No |
| Subtotal de un ítem | `cantidad × precio_unitario`, tipo `Decimal`, sin redondear al peso | `SubtotalItemsTests.test_subtotal_item_pedido`, `test_subtotal_item_cotizacion` | No |
| Valor de venta frente a la suma de los ítems | No se contrastan; el saldo usa el valor de venta | `SubtotalItemsTests.test_valor_venta_distinto_de_la_suma_de_items_se_acepta` | Sí |
| Abono inicial | Se rechaza si supera el valor total, solo cuando el total es mayor que 0; vacío equivale a 0 | `AbonoInicialTests.test_matriz_de_abonos` | No |
| Abono con valor de venta $0 | Se acepta cualquier abono | `AbonoInicialTests.test_matriz_de_abonos` (caso «valor 0 con abono») | Sí |
| Orden de limpieza | `valor_venta` se limpia antes que `abono_inicial` (último campo del formulario) | `AbonoInicialTests.test_valor_venta_se_limpia_antes_que_abono_inicial` | No |
| Panel financiero (`estadisticas_pagos`) | Coincide con el cálculo ingenuo en un conjunto de 12 pedidos; un pedido activo de $0 sin pagos cuenta como pagado y como sin abono a la vez | `EstadisticasPagosOraculoTests` | Sí (pedido de $0) |
| Panel principal (`dashboard`) | Coincide con el cálculo ingenuo; «crítico» incluye los pedidos `ENTREGADO` atrasados | `DashboardOraculoTests` | Sí (AUD-02-013) |
| Estadísticas de pedidos | Coinciden con el cálculo ingenuo | `EstadisticasPedidosOraculoTests` | No |

Las pruebas del panel congelan la hora con `mock.patch('django.utils.timezone.now')` al mediodía de Chile del 2026-10-15 (decisión D3) y apuntan `BASE_DIR` a una carpeta temporal vacía, porque `dashboard` lista los `.sql` de `backups/`. Los bordes de día y de mes en UTC (AUD-02-003) quedan para la 02-04.

## 9. Flujos fijados

Pruebas de caracterización de la iteración 02-03, en `test_pedidos.py` y `test_cotizaciones.py`: recorren la URL, la vista, el formulario y la base, y fijan lo que pasa **hoy**. Los caminos de fallo y los defectos conocidos son regresiones de la 02-04.

**Columna «GET»:** la prueba depende de que la ruta escriba con GET. Pasa por `ayudas.cambiar_estado` o `ayudas.duplicar`; la 04-01 cambia esas dos funciones a POST y revisa las pruebas marcadas.

| Flujo | Prueba (clase) | Qué comprueba | GET | `PENDIENTE_CLIENTE` |
| :---- | :------------- | :------------ | :-: | :------------------ |
| Ayudas | `AyudasTests` | Formato de `items_json`, rutas de cambiar estado y duplicar, hora congelada | Sí (2 de 4) | — |
| Crear pedido | `CrearPedidoTests` | Formulario 200; POST válido redirige al detalle; `creado_por`, estado `PENDIENTE`, ítems con cantidad `Decimal`; precio del ítem congelado al cambiar el producto; el precio lo envía el navegador; abono crea un `Pago` (método enviado o `EFECTIVO`, nota, quién lo registró); sin abono, sin pagos; sin `items_json`, sin ítems; formulario inválido no crea nada; evento `pedido_creado` | No | — |
| Editar pedido | `EditarPedidoTests` | Ítems precargados; cambia campos y `valor_venta`; reemplaza los ítems; sin `items_json` conserva los ítems; evento `pedido_modificado` | No | — |
| Cambiar estado | `CambiarEstadoTests` | Las 16 combinaciones de estado se aceptan (avanzar, retroceder, saltar); estado inexistente redirige sin cambio ni evento; pedido inexistente 404; no toca `estado_pago` | Sí (3 de 4) | — |
| Duplicar pedido | `DuplicarPedidoTests` | Copia cliente, resumen, detalles, valor, fecha de entrega y la ruta de la imagen; redirige al nuevo; estado y `estado_pago` `PENDIENTE`; no copia `creado_por`, pagos ni ítems; fecha de solicitud actual; evento `pedido_duplicado`. `MEDIA_ROOT` temporal | Sí | Sí (ítems al duplicar) |
| Clasificación | `ClasificacionTests` | Trabajo semanal y panel con 16 pedidos (4 estados × 4 fechas) a mediodía de Chile: activos = no `TERMINADO`; crítico, urgente, normal; sin fecha fuera de las categorías pero dentro del total (presión 50 %) | No | Sí (`ENTREGADO` atrasado, sin fecha; AUD-02-013) |
| Detalle de pedido | `DetallePedidoTests` | 200 con el pedido y sin eventos; 404 si no existe | No | — |
| Pagos | `PagosTests` | Ingresar desde el pedido sugiere el saldo; ingresar redirige a la lista y deja `PARCIAL` o `PAGADO`; editar recalcula `estado_pago` y redirige al detalle; eventos `pago_registrado` y `pago_modificado` | No | — |
| Crear cotización | `CrearCotizacionTests` | Formulario 200 con la fecha de hoy; POST válido crea en `BORRADOR` con sus ítems; vencimiento = emisión + validez; sin evento | No | — |
| Editar cotización | `EditarCotizacionTests` | Cambia campos y reemplaza ítems; una `ACEPTADA` redirige al detalle sin cambios, por GET y por POST | No | — |
| Convertir cotización | `ConvertirCotizacionTests` | Entrega sugerida a 7 días; copia cliente, resumen, detalles, ítems; fecha de entrega del POST; `creado_por`; cotización `ACEPTADA`; `valor_venta` = `valor_total` sin IVA; abono: sin abono, parcial (método `TRANSFERENCIA` por defecto), total, no numérico y negativo (sin pago) y su `estado_pago`; evento `cotizacion_convertida` | No | Sí (valor neto o con IVA; AUD-02-014) |

Ninguna prueba escribe en el `media/` real ni ejecuta `mysql` o `mysqldump`.

**Regla de negocio confirmada: el precio de cada ítem lo fija el vendedor** (decisión del desarrollador, 2026-10-27). `CrearPedidoTests.test_el_precio_lo_envia_el_navegador` fija que el servidor guarda el precio unitario que llega en `items_json` sin compararlo con el catálogo. No es un defecto: el vendedor (hoy, el dueño, único usuario y superusuario) ajusta a mano el precio de cada ítem para dar trato diferenciado a distintos clientes. Por eso no hay hallazgo ni regresión. **Advertencia:** ningún cambio de las Épicas 03 a 06 debe validar el precio del ítem contra el catálogo, ni recalcularlo en el servidor, sin consultar antes al desarrollador.
