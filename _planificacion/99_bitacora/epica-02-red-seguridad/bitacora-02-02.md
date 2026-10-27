# Bitácora 02-02 · Pruebas de la lógica de dinero

- **Fecha:** 2026-10-26
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** En revisión

## Resumen

Se creó `pedidos/tests/test_dinero.py` con 23 pruebas de caracterización: IVA y valor bruto de `Producto` con un oráculo de redondeo comercial, total pagado, saldo y porcentaje de `Pedido`, subtotales de ítems, abono inicial de `PedidoForm` y las cifras de `dashboard`, `estadisticas_pagos` y `estadisticas_pedidos` comparadas con un cálculo ingenuo sobre 12 pedidos conocidos. Se agregó la factoría `momento_chile` con 2 pruebas. Las pruebas pasaron de 86 a 111, en `OK` en tres ejecuciones seguidas. No se tocó código de la aplicación. Quedan 3 diferencias de $1 del IVA anotadas (D1) y 2 hallazgos propuestos.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/tests/test_dinero.py` | Nuevo: 23 pruebas en 7 clases (tareas 1 a 5) |
| `pedidos/tests/factorias.py` | Nueva función `momento_chile(anio, mes, dia, hora=12, minuto=0)` |
| `pedidos/tests/test_factorias.py` | 2 pruebas nuevas: `momento_chile` y pago con fecha dada |
| `docs/operacion/pruebas.md` | Fila de `test_dinero.py` en la sección 5, `momento_chile` en la sección 6 y sección 8 «Reglas de dinero fijadas» |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-02-logica-dinero.md` | Estado, decisiones D1 a D3 resueltas y criterios marcados |
| `_planificacion/00_producto/registro-pendientes.md` | Estado de la 02-02, nombres de prueba en la sección 2, decisiones en la sección 3, 2 hallazgos propuestos en la sección 4 e historial |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-02.md` | Esta bitácora |

## Punto de partida verificado contra el código

| Punto | Resultado |
| :---- | :-------- |
| `Producto.save()` | Coincide: `self.iva = int(round(self.valor_neto * 0.19))` y `valor_bruto = valor_neto + iva` (`models.py`). `valor_neto` es `IntegerField` sin validadores |
| `total_pagado_real`, `saldo_pendiente`, `porcentaje_pagado` | Coinciden. El porcentaje es `int((total / valor_venta) * 100)`: además de truncar, divide en `float` (ver hallazgo H1) |
| `Pago.monto` | Coincide: `PositiveIntegerField` |
| `subtotal` de ítems | Coincide en `ItemPedido` e `ItemCotizacion`; devuelve `Decimal` |
| Orden de limpieza en `PedidoForm` | `abono_inicial` es un campo declarado; el `ModelForm` lo pone **después** de los campos del modelo, así que es el último campo y `valor_venta` se limpia antes. La validación sí actúa cuando el total es mayor que 0. Solo deja de actuar si `valor_venta` es inválido (por ejemplo -1): entonces el formulario es inválido igual, por `valor_venta` |
| Vistas del panel | Solo `estadisticas_pagos` muestra dinero. `dashboard` y `estadisticas_pedidos` muestran conteos y porcentajes de pedidos, no montos (ver propuesta sobre D2) |
| `registrar_metricas_diarias()` en la base de pruebas | Funcionó sin `mock`: crea una fila en `HistorialBD` (efecto aceptado, AUD-01-006, fijado en `test_registra_metricas_diarias_una_vez`) |
| `TruncMonth` de `estadisticas_pedidos` en la base de pruebas | Funcionó: el gráfico anual devuelve los meses esperados |
| Línea base | 86 pruebas en `OK`, como se esperaba |

## Cómo se obtiene la hora (decisión D3)

- `dashboard`, `estadisticas_pedidos`, `estadisticas_pagos` y `registrar_metricas_diarias` (`utils.py`) usan solo `timezone.now()` sobre el módulo importado con `from django.utils import timezone`. Parchar `django.utils.timezone.now` alcanza a todas, porque el nombre se busca en el módulo en cada llamada.
- `datetime.now()` aparece solo en `utils.py:29` (`generar_respaldo_mysql`), fuera de estas rutas. `datetime.fromtimestamp` de `dashboard` lee la fecha de modificación de los `.sql` de `backups/`, no el reloj. **No fue necesario detenerse.**
- La prueba apunta `views.settings.BASE_DIR` a una carpeta temporal vacía con `mock.patch.object`, para que `dashboard` no liste la carpeta `backups/` del equipo.
- Hora fija: 2026-10-15 a las 12:00 de Chile (15:00 UTC). `test_la_hora_congelada_llega_a_la_vista` comprueba que `fecha_actual` del contexto es esa hora.

## Oráculo de IVA (decisión D1)

Oráculo: `Decimal(valor_neto) * Decimal('0.19')` con `ROUND_HALF_UP`.

| `valor_neto` | `× 0,19` | IVA del modelo | IVA del oráculo | Diferencia |
| -----------: | -------: | -------------: | --------------: | ---------: |
| 0 | 0 | 0 | 0 | 0 |
| 1 | 0,19 | 0 | 0 | 0 |
| 100 | 19 | 19 | 19 | 0 |
| 1.000 | 190 | 190 | 190 | 0 |
| 1.000.000 | 190.000 | 190.000 | 190.000 | 0 |
| -1.000 | -190 | -190 | -190 | 0 |
| 50 | 9,5 | 10 | 10 | 0 |
| 150 | 28,5 | 28 | 29 | **+1** |
| 250 | 47,5 | 48 | 48 | 0 |
| 350 | 66,5 | 66 | 67 | **+1** |
| 4.950 | 940,5 | 940 | 941 | **+1** |

- Tres diferencias de $1 en la tabla, todas en mitades que el redondeo al par baja. Ninguna supera $1.
- Barrido adicional, fuera de las pruebas: entre 0 y 100.000, **500 de 100.001** valores netos difieren en $1 (150, 350, 550, 750, …, es decir, los múltiplos de 50 cuyo IVA termina en ,5 y queda por debajo al redondear al par).
- Según D1, no se crean regresiones.

## Panel frente al cálculo ingenuo

Conjunto: 12 pedidos de 4 clientes, en estados `PENDIENTE` (3), `EN_PROCESO` (3), `TERMINADO` (4) y `ENTREGADO` (2), con pagos parciales, pagos completos, un sobrepago, pedidos sin pagos y fechas entre diciembre de 2025 y octubre de 2026. Cada cifra se comparó dos veces: contra el cálculo ingenuo (bucle en Python) y contra el valor fijo de la tabla.

| Vista | Variable | Vista | Cálculo ingenuo |
| :---- | :------- | ----: | --------------: |
| `estadisticas_pagos` | `deuda_critica_total` / `deuda_critica_cantidad` | $60.000 / 2 | $60.000 / 2 |
| | `riesgo_total_monto` / `riesgo_cantidad` | $35.000 / 1 | $35.000 / 1 |
| | `proyeccion_total` | $175.000 | $175.000 |
| | `ingresos_mes_actual` | $51.000 | $51.000 |
| | `count_pagados` / `count_parcial` / `count_sin_abono` | 3 / 3 / 4 | 3 / 3 / 4 |
| | `pct_pagados` / `pct_parcial` / `pct_sin_abono` | 30 / 30 / 40 | 30 / 30 / 40 |
| | `deudores_list` | 2 pedidos, por fecha de entrega | igual |
| `dashboard` | `criticos_count` / `urgentes_count` | 3 / 3 | 3 / 3 |
| | `total_pedidos` (mes) | 5 | 5 |
| | `pendientes` / `en_proceso` / `completados` | 1 / 3 / 1 | 1 / 3 / 1 |
| | `pct_pendientes` / `pct_proceso` / `pct_completados` | 20 / 60 / 20 | 20 / 60 / 20 |
| | `top_clientes` (pedidos) / `max_pedidos` | 4, 3, 3, 2 / 4 | 4, 3, 3, 2 / 4 |
| `estadisticas_pedidos` | `total_mes_actual` | 5 | 5 |
| | `crecimiento_pct` (5 frente a 3) | 66,7 | 66,7 |
| | `eficiencia_pct` | 20,0 | 20,0 |
| | `lista_puntos` (ene a dic 2026) | 0,0,1,0,0,0,0,2,3,5,0,0 | igual |
| | `max_y_label` | 6 | 6 |

Todas las cifras coinciden. El sobrepago (saldo -$2.000) no rompe la resta en MySQL (`valor_venta` es sin signo, pero `SUM` devuelve decimal con signo) y queda fuera de la deuda y de la proyección. El oráculo de `dashboard` reproduce el criterio actual: «crítico» incluye los `ENTREGADO` atrasados (2 de los 3 críticos; `PENDIENTE_CLIENTE`, AUD-02-013). El oráculo calcula «mes actual» en hora de Chile; con la hora fija al mediodía y fechas lejos de los bordes coincide con la vista, que corta el mes en UTC (AUD-02-003, para la 02-04).

## Hallazgos propuestos (sin corregir)

- **H1 · Error de `float` en `porcentaje_pagado`.** `int((29 / 100) * 100)` da 28, no 29, porque `29 / 100 * 100` es 28,999…; en los pagos de 1 a valor − 1 sobre valores de 100, 1.000 y 10.000 hay 9 casos (29, 57 y 58 % en cada escala). Efecto: una barra de progreso un punto más baja. Alternativa sin `float`: `pagado * 100 // valor`. Fijado en el caso «error de float al truncar». Severidad sugerida: Baja. Avanza AUD-02-015 (cantidades con `float`).
- **H2 · Pedido de $0 contado dos veces en `estadisticas_pagos`.** Un pedido activo de $0 sin pagos entra en «pagados» (saldo 0) y en «sin abono» (pagado 0); el remanente «parcial» baja en uno y, con varios pedidos así, puede quedar negativo. Producción no tiene pedidos de $0 (2026-10-20), así que hoy no se ve. Depende del dato `PENDIENTE_CLIENTE` del pedido de $0. Fijado en `test_pedido_de_valor_cero_cuenta_como_pagado_y_sin_abono`. Severidad sugerida: Baja.
- Ambos quedaron en la sección 4 de `registro-pendientes.md`. No se les asignó número de auditoría: lo decide el desarrollador.

## Propuesta sobre D2 (no aplicada)

- **Sobra en sentido estricto:** `dashboard` y `estadisticas_pedidos` no muestran dinero, solo conteos de pedidos. Igual conviene mantenerlas: sus pruebas fijan los criterios de «crítico», «urgente» y «mes actual» que la 02-04 y la 06-01 van a tocar.
- **No falta ninguna** con cifras de dinero agregadas: `lista_pedidos` agrega solo conteos, `lista_pagos` pagina sin totales y `estadisticas_bd` mide la base. Los saldos por pedido de `pedido_detail`, `pago_detail` y `pago_form` usan las propiedades del modelo, cubiertas en la tarea 2. La tabla de deudores de `estadisticas_pagos` muestra `pedido.saldo_pendiente` (una consulta por fila) en lugar del `saldo_db` ya anotado: es tema de la 05-02, no se probó aquí.

## Verificación

### `python manage.py test pedidos -v 2`, tres ejecuciones seguidas

| Ejecución | Recuento | Resultado |
| :-------- | :------- | :-------- |
| 1 | `Ran 111 tests in 73.059s` | `OK` |
| 2 | `Ran 111 tests in 91.131s` | `OK` |
| 3 | `Ran 111 tests in 80.936s` | `OK` |

Las tres crean y destruyen `test_manzagrafica` y muestran la advertencia esperada `mysql.W002`. Pruebas nuevas de la ejecución 1:

```text
test_abono_negativo_se_rechaza (AbonoInicialTests.test_abono_negativo_se_rechaza) ... ok
test_matriz_de_abonos (AbonoInicialTests.test_matriz_de_abonos) ... ok
test_valor_venta_invalido_deja_pasar_cualquier_abono (AbonoInicialTests.test_valor_venta_invalido_deja_pasar_cualquier_abono) ... ok
test_valor_venta_se_limpia_antes_que_abono_inicial (AbonoInicialTests.test_valor_venta_se_limpia_antes_que_abono_inicial) ... ok
test_cifras_coinciden_con_el_calculo_ingenuo (DashboardOraculoTests.test_cifras_coinciden_con_el_calculo_ingenuo) ... ok
test_cifras_fijadas_del_conjunto (DashboardOraculoTests.test_cifras_fijadas_del_conjunto) ... ok
test_la_hora_congelada_llega_a_la_vista (DashboardOraculoTests.test_la_hora_congelada_llega_a_la_vista) ... ok
test_registra_metricas_diarias_una_vez (DashboardOraculoTests.test_registra_metricas_diarias_una_vez) ... ok
test_cifras_coinciden_con_el_calculo_ingenuo (EstadisticasPagosOraculoTests.test_cifras_coinciden_con_el_calculo_ingenuo) ... ok
test_cifras_fijadas_del_conjunto (EstadisticasPagosOraculoTests.test_cifras_fijadas_del_conjunto) ... ok
test_pedido_de_valor_cero_cuenta_como_pagado_y_sin_abono (EstadisticasPagosOraculoTests.test_pedido_de_valor_cero_cuenta_como_pagado_y_sin_abono) ... ok
test_cifras_coinciden_con_el_calculo_ingenuo (EstadisticasPedidosOraculoTests.test_cifras_coinciden_con_el_calculo_ingenuo) ... ok
test_cifras_fijadas_del_conjunto (EstadisticasPedidosOraculoTests.test_cifras_fijadas_del_conjunto) ... ok
test_invariante_bruto_igual_neto_mas_iva (IvaProductoTests.test_invariante_bruto_igual_neto_mas_iva) ... ok
test_iva_y_valor_bruto_guardados (IvaProductoTests.test_iva_y_valor_bruto_guardados) ... ok
test_oraculo_comercial_difiere_solo_en_las_mitades_al_par (IvaProductoTests.test_oraculo_comercial_difiere_solo_en_las_mitades_al_par) ... ok
test_recalcula_al_cambiar_valor_neto (IvaProductoTests.test_recalcula_al_cambiar_valor_neto) ... ok
test_matriz_de_saldos (SaldoPedidoTests.test_matriz_de_saldos) ... ok
test_monto_de_pago_no_admite_negativos_ni_decimales (SaldoPedidoTests.test_monto_de_pago_no_admite_negativos_ni_decimales) ... ok
test_pagos_de_otro_pedido_no_se_mezclan (SaldoPedidoTests.test_pagos_de_otro_pedido_no_se_mezclan) ... ok
test_subtotal_item_cotizacion (SubtotalItemsTests.test_subtotal_item_cotizacion) ... ok
test_subtotal_item_pedido (SubtotalItemsTests.test_subtotal_item_pedido) ... ok
test_valor_venta_distinto_de_la_suma_de_items_se_acepta (SubtotalItemsTests.test_valor_venta_distinto_de_la_suma_de_items_se_acepta) ... ok
test_momento_chile_es_mediodia_local_y_consciente (FactoriasTests.test_momento_chile_es_mediodia_local_y_consciente) ... ok
test_pago_con_fecha_dada (FactoriasTests.test_pago_con_fecha_dada) ... ok
```

Recuento: 86 de la línea base + 23 de `test_dinero.py` + 2 de `test_factorias.py` = 111.

### Otros comandos

```text
> python manage.py test pedidos --exclude-tag regresion
Found 111 test(s).
OK

> python manage.py check
System check identified no issues (0 silenced).

> python manage.py makemigrations --check --dry-run
No changes detected

> git status --short
 M _planificacion/00_producto/registro-pendientes.md
 M _planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-02-logica-dinero.md
 M docs/operacion/pruebas.md
 M pedidos/tests/factorias.py
 M pedidos/tests/test_factorias.py
?? _planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-02.md
?? pedidos/tests/test_dinero.py
```

`git diff --stat` (archivos ya versionados; los dos nuevos no aparecen):

```text
 _planificacion/00_producto/registro-pendientes.md  | 17 ++++++++----
 .../iteracion-02-02-logica-dinero.md               | 26 +++++++++---------
 docs/operacion/pruebas.md                          | 31 ++++++++++++++++++++--
 pedidos/tests/factorias.py                         |  9 +++++++
 pedidos/tests/test_factorias.py                    | 14 ++++++++++
```

El diff no toca `models.py`, `views.py`, `forms.py`, `utils.py` ni ningún otro código de la aplicación: solo `pedidos/tests/` y documentación.

- Revisión de pantallas en escritorio y a 360 px: no aplica, la iteración no toca plantillas ni estilos.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] `test_dinero.py` existe con pruebas de las tareas 1 a 5 y sin accesorios estáticos (todo con factorías).
- [x] Cada regla sin confirmar tiene su comentario `PENDIENTE_CLIENTE` (sobrepago, pedido de $0, valor de venta frente a ítems, crítico con `ENTREGADO`) y figura en la sección 2 del registro.
- [x] Diferencias del oráculo de IVA en esta bitácora: 3 en la tabla, todas de $1.
- [x] Las cifras del panel coinciden con el cálculo ingenuo en las tres vistas.
- [x] Ninguna prueba depende del reloj real (hora congelada y comprobada en `test_la_hora_congelada_llega_a_la_vista`; las fechas se pasan explícitas) ni del orden (`setUpTestData` y datos por prueba; tres ejecuciones en verde).
- [x] `test pedidos` en verde en tres ejecuciones; `check` sin errores; `makemigrations --check --dry-run` sin cambios.
- [x] El diff no toca código de la aplicación.
- [x] D1, D2 y D3 resueltas por el desarrollador y registradas.

## Decisiones tomadas

- D1, D2 y D3 del desarrollador (2026-10-26), registradas en la iteración y en la sección 3 del registro.
- `mock` sobre `registrar_metricas_diarias()`: no hizo falta.
- No hubo errores provocados a propósito que absorber con `assertLogs`: ninguna prueba nueva genera registros de error.
- La primera pregunta de AUD-02-014 (valor de cotización neto o con IVA) no tiene prueba: el modelo no calcula nada con `valor_total`; queda para cuando 02-03 pruebe la conversión de cotizaciones.

## Pendientes y riesgos

- Para el desarrollador: decidir si H1 y H2 pasan a la auditoría y a qué iteración, y si acepta la propuesta sobre D2.
- Si el cliente responde los datos `PENDIENTE_CLIENTE`, las pruebas que los fijan (sección 2 del registro) se actualizan en la iteración que cambie la regla.
- Las pruebas de panel usan fechas lejos de los bordes de mes; los bordes en UTC (AUD-02-003) siguen sin prueba hasta la 02-04.

## Commit sugerido

`Épica 2 - Iteración 02-02: fija con 23 pruebas de caracterización el IVA, los saldos, el abono inicial y las cifras del panel frente a un oráculo, sin tocar el código de la aplicación` (183 caracteres)

## Decisiones tomadas tras la revisión

Decisiones del desarrollador del 2026-10-26, después de entregar esta bitácora.

- **H1 → AUD-02-025** (Baja). Se suma a la 02-04 como regresión R15, que afirma 29 %; recuento previsto de la 02-04: 17. Iteración que lo corrige: `PENDIENTE_DESARROLLADOR`, propuesta 06-05.
- **H2 → AUD-02-026** (Baja). Solo auditoría, ligado al dato `PENDIENTE_CLIENTE` del pedido de $0; sin regresión hasta que el cliente responda.
- **D2:** `dashboard` y `estadisticas_pedidos` se mantienen en la 02-02.
- **AUD-02-014** (valor de la cotización neto o con IVA): lo fija la 02-03 en la conversión de cotización, con `PENDIENTE_CLIENTE`.
- **IVA con diferencias de $1** (150, 350 y 4.950; 500 valores entre 0 y 100.000): solo anotado (D1), como nota de AUD-02-015 en `auditoria-tecnica.md`.
- Las notas H1 y H2 salen de la sección 4 de `registro-pendientes.md`; el historial lo registra.
- Con todos los criterios marcados, la 02-02 queda **Terminada**.
