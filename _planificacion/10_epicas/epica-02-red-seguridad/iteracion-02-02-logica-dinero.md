# Iteración 02-02 · Pruebas de la lógica de dinero

- **Épica:** 02 · Red de seguridad
- **Estado:** Terminada (2026-10-26; [bitacora-02-02](../../99_bitacora/epica-02-red-seguridad/bitacora-02-02.md))
- **Subfase del plan:** 2.2
- **Depende de:** 02-01
- **RDA relacionadas:** RDA-006
- **Hallazgos que avanza:** AUD-01-015 (cero pruebas), AUD-02-014 (valor de cotización neto o con IVA; valor de venta frente a la suma de ítems) y AUD-02-015 (cantidades con `float`). No cierra ninguno.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no despliega nada: solo agrega pruebas)

## Objetivo

Fijar con pruebas, antes de que cualquier épica toque la lógica de dinero, **cómo calcula hoy** la aplicación el IVA y el valor bruto de un producto, el total pagado, el saldo y el porcentaje pagado de un pedido, la validación del abono inicial y las cifras del panel financiero. Es la iteración de mayor prioridad de la épica: un error silencioso aquí tiene consecuencias comerciales directas.

Son pruebas de **caracterización**: congelan el comportamiento actual, sea correcto o no. Lo que no está confirmado por el cliente se marca `PENDIENTE_CLIENTE`.

## Punto de partida (a verificar leyendo el código antes de escribir)

El agente confirma cada punto en el archivo indicado; si algo difiere, lo anota en la bitácora y sigue con lo que encuentre.

- `pedidos/models.py`, `Producto.save()`: `iva = int(round(valor_neto * 0.19))` y `valor_bruto = valor_neto + iva`. El cálculo usa `float` y el `round` de Python (que redondea las mitades al par más cercano), no un redondeo comercial. `valor_neto` es un `IntegerField` sin validadores.
- `Pedido.total_pagado_real`: suma de `pagos.monto` o `0`. `saldo_pendiente`: `valor_venta - total_pagado_real` (puede ser negativo). `porcentaje_pagado`: `100` si `valor_venta == 0`; si no, `int(total / valor_venta * 100)`, que **trunca** y puede pasar de 100.
- `Pago.monto` es un `PositiveIntegerField` (no admite negativos ni decimales).
- `ItemPedido.subtotal` y `ItemCotizacion.subtotal`: `cantidad * precio_unitario` con `cantidad` `Decimal` y precio entero.
- `pedidos/forms.py`: el formulario de pedido valida que el abono inicial no supere el valor total **solo si el total es mayor que 0**. Depende del orden de limpieza de los campos: si `valor_venta` no se limpia antes que `abono_inicial`, el total llega como 0 y la validación no actúa. El agente verifica el orden real.
- `pedidos/views.py`: el panel y las estadísticas calculan sus cifras con `aggregate` y objetos `Q`. El agente identifica cuáles muestran dinero (por ejemplo `dashboard`, `estadisticas_pagos` y `estadisticas_pedidos`) y qué variables del contexto contienen cada cifra.
- Línea base de pruebas: la medida al empezar (86 en `main` al redactar esta iteración).

## Tareas

1. **IVA y valor bruto de `Producto`.** En `pedidos/tests/test_dinero.py`:
   - Tabla de casos con `subTest`: `valor_neto` 0, 1, 100, 1.000, 1.000.000 y un negativo (el modelo no lo impide; se fija lo que ocurre).
   - Casos donde `valor_neto × 0,19` termina en `,5` (por ejemplo `valor_neto` 50, 150 y 250): se ejecutan, se observa el resultado y se fija ese valor.
   - Invariante: `valor_bruto == valor_neto + iva` en todos los casos; recalcular al cambiar `valor_neto` y guardar de nuevo.
   - **Oráculo independiente:** para cada caso, calcular el IVA con `Decimal` y redondeo comercial (mitad hacia arriba) y comparar con el valor guardado. Las diferencias de un peso **se anotan en la bitácora y no se corrigen**; el desarrollador decide después si pasan a regresión (decisión 1).
2. **Pedido: total pagado, saldo y porcentaje.** Matriz con `subTest`:
   - sin pagos; un pago parcial; varios pagos acumulados; pago exacto del total;
   - sobrepago: saldo negativo y porcentaje mayor que 100 (`PENDIENTE_CLIENTE`: ¿se permite?);
   - `valor_venta = 0` sin pagos y con un pago: porcentaje 100 (`PENDIENTE_CLIENTE`);
   - truncamiento: 1/3 → 33, 2/3 → 66 y 99,9 % → 99;
   - aislamiento: los pagos de otro pedido no se mezclan.
3. **Ítems.** `subtotal` con cantidad entera y con decimales (por ejemplo 2,50 × 1.000), y el tipo del resultado (`Decimal`). La suma de los subtotales **no** se contrasta con `valor_venta` en el modelo: se fija con un pedido cuyo `valor_venta` difiere de la suma (`PENDIENTE_CLIENTE`, AUD-02-014).
4. **Abono inicial.** Con el formulario de pedido: abono menor, igual y mayor que el total (el último, con su mensaje de error); abono vacío y 0; `valor_venta = 0` con abono mayor que 0 (hoy no se rechaza; se fija); el orden de los campos como condición del caso.
5. **Panel financiero con oráculo.** Para cada vista elegida en la decisión 2:
   - construir un conjunto conocido (por ejemplo 8 a 12 pedidos con estados, valores, pagos y fechas distintas) con las factorías;
   - calcular el resultado esperado con un **cálculo ingenuo** (un bucle en Python sobre los objetos);
   - comparar contra el contexto de la respuesta del cliente de pruebas;
   - fijar la hora a mediodía de Chile para no entrar en AUD-02-003, que va en 02-04.
   - Nota: `dashboard` llama a `registrar_metricas_diarias()`, que escribe en `HistorialBD` con una petición de lectura (AUD-01-006). La prueba acepta ese efecto; si el cálculo del tamaño de la base falla en la base de pruebas, se anota y se simula esa llamada con `mock`.
6. **Factorías.** Ampliar `pedidos/tests/factorias.py` solo con lo que las pruebas necesiten (por ejemplo, pagos con fecha). Las nuevas funciones llevan su prueba, como en 02-01.
7. **Documentación.** En `docs/operacion/pruebas.md`, una sección «Reglas de dinero fijadas» con una tabla (regla, valor actual, prueba que la fija, `PENDIENTE_CLIENTE` sí/no). En `registro-pendientes.md`, sección 2, el nombre de la prueba que fija cada dato del cliente.
8. **Bitácora** `bitacora-02-02.md` con la salida de `test pedidos -v 2`, el recuento de pruebas y las diferencias del oráculo de IVA.

## Criterios de aceptación

- [x] `pedidos/tests/test_dinero.py` existe, con pruebas por cada punto de las tareas 1 a 5, y no hay accesorios estáticos.
- [x] Cada regla sin confirmar tiene su comentario `PENDIENTE_CLIENTE` y figura en `registro-pendientes.md`.
- [x] Las diferencias del oráculo de IVA frente al cálculo del modelo están en la bitácora, aunque sean cero.
- [x] Las cifras del panel coinciden con el cálculo ingenuo en el conjunto conocido, o la diferencia está explicada y registrada como hallazgo.
- [x] Ninguna prueba depende del reloj real ni del orden de ejecución.
- [x] `python manage.py test pedidos` en verde (más las pruebas nuevas) en tres ejecuciones seguidas; `check` sin errores; `makemigrations --check --dry-run` sin cambios.
- [x] El diff no toca `pedidos/models.py`, `views.py`, `forms.py` ni ningún otro código de la aplicación.
- [x] Las decisiones `PENDIENTE_DESARROLLADOR` quedaron resueltas y registradas.

## Fuera de alcance

- Corregir el redondeo, el `float`, el sobrepago o cualquier regla (queda como hallazgo o pasa a 02-04).
- Pruebas de las vistas de escritura (pedidos, cotizaciones, pagos): 02-03.
- Regresión de `estado_pago` desincronizado (AUD-02-004) y de fechas en UTC (AUD-02-003): 02-04.
- Probar el formato de números chilenos en plantillas.

## Decisiones del desarrollador

Resueltas por el desarrollador el 2026-10-26:

1. **D1 · Diferencias de IVA de un peso** entre el modelo y el oráculo (`Decimal`, `ROUND_HALF_UP`): solo se anotan en la bitácora, con la tabla de casos. No se crean regresiones.
2. **D2 · Vistas del panel con oráculo:** `dashboard`, `estadisticas_pagos` y `estadisticas_pedidos`. Si el agente cree que falta o sobra alguna, lo propone en la bitácora sin aplicarlo.
3. **D3 · Congelar la hora** con `unittest.mock.patch`, sin dependencias nuevas, parchando el nombre donde se busca, al mediodía de Chile. Si alguna ruta usa `date.today()` o `datetime.now()` y no se puede parchar sin tocar la aplicación, el agente se detiene y lo reporta. Resultado: las tres vistas usan solo `timezone.now()` del módulo, así que basta parchar `django.utils.timezone.now`.

## Datos requeridos del cliente

- Ninguno para ejecutar. Los cuatro datos de la sección 2 de `registro-pendientes.md` ligados a esta iteración (valor de cotización neto o con IVA; valor de venta frente a la suma de ítems; pedido de $0; sobrepago) se fijan como `PENDIENTE_CLIENTE` hasta que el cliente responda.

### Decisiones tras la revisión (2026-10-26)

- **D2 confirmada:** `dashboard` y `estadisticas_pedidos` se mantienen en la 02-02, aunque no muestran dinero, porque fijan los criterios de «crítico», «urgente» y «mes actual».
- **H1 → AUD-02-025:** regresión R15 en la 02-04. **H2 → AUD-02-026:** solo auditoría, sin regresión hasta que el cliente responda sobre los pedidos de $0.
- **AUD-02-014 (valor de la cotización neto o con IVA):** no se cubre aquí; lo fija la 02-03 en la conversión de cotización.
- **IVA con diferencias de $1:** solo anotado (D1), como nota de AUD-02-015.
