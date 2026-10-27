# Bitácora 02-04 · Pruebas de regresión de defectos conocidos

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** En revisión

## Resumen

Se escribieron 18 regresiones en `pedidos/tests/test_regresiones.py`: R1 a R4, R6 (tres pruebas), R7 a R15, R18 y R19. Cada una afirma el comportamiento correcto y hoy falla por el defecto descrito. Antes de marcarlas, se ejecutaron sin `@expectedFailure` para confirmar el motivo de cada fallo. **R5 (AUD-01-006) no se confirmó** (`unexpected success`) y no se registró. La tarea 0 unificó `congelar_hora` y corrigió el comentario del precio del ítem. No se cambió código de la aplicación.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/tests/test_regresiones.py` | Nuevo: 18 regresiones, oráculo de `estado_pago` probado (`OraculoEstadoPagoTests`) y `absorber_errores` |
| `pedidos/tests/ayudas.py` | `estado_pago_esperado` (oráculo, tarea 2); nota de `congelar_hora` como definición única |
| `pedidos/tests/test_dinero.py` | Tarea 0a: importa `congelar_hora` y `MEDIODIA` desde `ayudas.py` (`AHORA = MEDIODIA`, el mismo instante) |
| `pedidos/tests/test_pedidos.py` | Tarea 0b: comentario de `test_el_precio_lo_envia_el_navegador`, ahora como regla de negocio confirmada |
| `docs/operacion/pruebas.md` | Sección 7.1: tabla de regresiones, N = 18, cómo se retiran |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-04-regresiones.md` | En revisión; decisiones D1 a D5; R5 no confirmada; criterios |
| `_planificacion/10_epicas/epica-02-red-seguridad/definicion-epica-02.md` | Estado y nota de la 02-04 |
| `_planificacion/00_producto/registro-pendientes.md` | 02-04 en revisión; decisiones; historial |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-02-027 asignado a la 03-04; notas de la 02-04 (hallazgo → prueba; AUD-01-006 sin regresión) |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-04.md` | Esta bitácora |

## Verificación

- **Línea base** (paso 0): `python manage.py test pedidos` → `Found 151 test(s)` … `OK`.
- **Después de la tarea 0, antes de escribir regresiones:** 151 pruebas, `OK`.
- **Tres ejecuciones seguidas** de `python manage.py test pedidos -v 2`:

```text
Ejecución 1: Found 170 test(s). Ran 170 tests in 149.225s  OK (expected failures=18)
Ejecución 2: Found 170 test(s). Ran 170 tests in 156.384s  OK (expected failures=18)
Ejecución 3: Found 170 test(s). Ran 170 tests in 164.146s  OK (expected failures=18)
```

  Sin `failures`, `errors` ni `unexpected successes`. 170 = 151 previas + 18 regresiones + 1 prueba del oráculo.
- `python manage.py test pedidos --exclude-tag regresion` → `Ran 152 tests` … `OK`.
- `python manage.py test pedidos --tag regresion -v 2` → `Ran 18 tests` … `OK (expected failures=18)`.
- `python manage.py check` → `System check identified no issues (0 silenced).`
- `python manage.py makemigrations --check --dry-run` → `No changes detected` (código de salida 0).
- `git status --short` y `git diff --stat`: solo `pedidos/tests/` y archivos `.md`.
- Pantallas: no aplica (no se tocaron plantillas ni estilos).

### Motivo real de cada fallo, sin la marca

Salida de la ejecución de las 18 pruebas sin `@expectedFailure` (copia temporal, borrada después): `FAILED (failures=18)`, **sin errores**.

| # | Mensaje real | ¿Es el defecto descrito? |
| :- | :----------- | :----------------------- |
| R1 | `Lists differ: [(4, Decimal('3.00'), 4000)] != [(3, Decimal('1.00'), 10000)]` | Sí: el ítem anterior se borró y quedó solo el nuevo creado antes del fallo |
| R2 | `Lists differ: [(6, Decimal('3.00'), 4000)] != [(5, Decimal('1.00'), 10000)]` | Sí, igual en cotizaciones |
| R3 | `Tuples differ: (1, 1) != (0, 0)` | Sí: pedido creado con un ítem de dos |
| R4 | `Tuples differ: (1, 1) != (0, 0)` | Sí: cotización con un ítem de dos |
| R6a | `Tuples differ: (302, 'EN_PROCESO') != (405, 'PENDIENTE')` | Sí: GET cambia el estado |
| R6b | `Tuples differ: (302, 2) != (405, 1)` | Sí: GET crea el duplicado |
| R6c | `Tuples differ: (200, True) != (405, False)` | Sí: GET genera el respaldo (función reemplazada; `mysqldump` no se ejecuta) |
| R7 | `500 != 200` | Sí: falta `pedidos/pago_confirm_delete.html` |
| R8 | `Tuples differ: (1, 0) != (0, 1)` | Sí: un pedido que se entrega hoy en Chile cuenta como crítico. La parte de base de datos, ejecutada por separado: `2 != 1` (el panel escribió una segunda fila de métricas el mismo día de Chile) |
| R9 | `0 != 10000` | Sí: «ingresos del mes» toma noviembre en UTC |
| R10 | `'PENDIENTE' != 'PARCIAL'` | Sí |
| R11 | `'PAGADO' != 'PARCIAL'` | Sí (la primera aserción, `valor_venta == 20_000`, pasa) |
| R12 | `'PAGADO' != 'PENDIENTE'` | Sí: el pedido destino sí se recalcula; el anterior no |
| R13 | `2 != 1` | Sí: dos pedidos |
| R14 | `ProtectedError not raised` | Sí: borra en cascada |
| R15 | `28 != 29` | Sí |
| R18 | `500 != 200` | Sí. La traza muestra `ValidationError: el valor tiene un formato de fecha inválido` en `Pedido.objects.create` (`views.py:875`), capturado por el decorador (`decorators.py:19`). La hipótesis de la 02-03 era correcta |
| R19 | `None != <User: usuario15>` | Sí: `creado_por` nulo |

**Detalle de R18:** en la primera versión, la prueba consultaba la base antes de comprobar el código de respuesta y dio `TransactionManagementError`. El `ValidationError` ocurre dentro del bloque atómico de `save_base` y deja marcada para revertir la transacción de `TestCase`. En producción no hay transacción externa, así que no ocurre. La prueba ahora comprueba la respuesta primero.

### Regresión no confirmada: R5 (AUD-01-006)

- **Prueba:** dos llamadas a `registrar_metricas_diarias()` con la hora fija a mediodía de Chile, esperando una fila de `HistorialBD`.
- **Resultado sin la marca:** `ok`. Habría sido `unexpected success`, así que no se registró como regresión.
- **Evidencia adicional** (prueba temporal, borrada): con la hora a las 22:00 de Chile, dos llamadas dejan `2 != 1`. Ese es el defecto del día en UTC (AUD-02-003): `hoy` sale de `timezone.now().date()` en UTC y `__date` compara en hora de Chile. La parte de base de datos de R8 ya lo comprueba.
- **Lectura:** en la base local la comprobación de duplicados funciona dentro del mismo día. Las 187 filas en 121 días de producción pueden explicarse por visitas al panel entre las 21:00 y las 24:00 de Chile y, quizá, por un MySQL de producción sin tablas de zona horaria, donde `__date` devuelve nulo y nunca encuentra la fila (`AGENTS.md`, regla 6). Esto no se puede comprobar en local. Decisión pendiente (sección «Decisiones»).

## Inventario D4 · Rutas que escriben con GET

Leído en `pedidos/urls.py`, `PedidosApp/urls.py` y `pedidos/views.py`. Sin pruebas nuevas fuera de R6.

| Ruta | Vista | Qué escribe con GET | Cubierta |
| :--- | :---- | :------------------ | :------- |
| `pedido/<pk>/cambiar/<nuevo_estado>/` | `cambiar_estado_pedido` | `Pedido.estado` y evento `pedido_estado_cambiado` | R6a |
| `pedido/duplicar/<pk>/` | `duplicar_pedido` | Pedido nuevo y evento `pedido_duplicado` | R6b |
| `base_datos/respaldar_bd/accion/` | `generar_respaldo_bd` | Archivo `.sql` en `backups/`, borra respaldos antiguos (deja 5) y evento `respaldo_generado` | R6c |
| `` (raíz, panel) | `dashboard` | Una fila de `HistorialBD` vía `registrar_metricas_diarias()` (si no hay del día) | No (R8 lo toca por la fecha, no por el método) |
| `base_datos/estadisticas_bd/` | `estadisticas_bd` | Lo mismo: `registrar_metricas_diarias()` | No |
| `pagos/eliminar/<pk>/` | `eliminar_pago` | Nada con GET: solo intenta mostrar la confirmación | R7 (500, no escritura) |

Revisadas sin escritura por GET: las demás eliminaciones (`eliminar_pedido`, `eliminar_cliente`, `eliminar_cotizacion`, `eliminar_producto`) y `restaurar_bd` escriben solo con POST; las API rápidas tienen `require_POST`; el cierre de sesión de Django acepta solo POST. Las señales de acceso escriben eventos solo al enviar el formulario de acceso. Las dos rutas no cubiertas son el efecto aceptado de AUD-01-006: el plan las saca de la petición con la orden de mantención diaria (06-01 y 06-02).

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Una regresión por cada fila (R1 a R15, R18 y R19), con `@tag('regresion')`, `@expectedFailure` y su comentario. **Salvo R5**, no confirmada (arriba).
- [x] Para cada una, el fallo real sin la marca y que su causa es el defecto descrito (tabla de motivos).
- [x] Tres ejecuciones seguidas: `OK (expected failures=18)`, sin `unexpected successes` ni errores.
- [x] `--exclude-tag regresion` en verde (152 pruebas).
- [x] `pruebas.md`, sección 7.1, lista las regresiones y N = 18; `despliegue.md`, paso 1, ya remite a ese número.
- [x] El diff no toca código de la aplicación.
- [x] Decisiones `PENDIENTE_DESARROLLADOR` resueltas y registradas (D1 a D5); la de AUD-02-028 queda abierta por decisión (D5).

## Decisiones tomadas

Decisiones del desarrollador del 2026-10-27, registradas en la iteración y en el registro:

- **D1:** R1 a R4 afirman «todo o nada». También se comprueba que no cambian los campos (`valor_venta`, `valor_total`) en R1 y R2.
- **D2:** AUD-02-021 no entra; R16 reservado.
- **D3:** numeración sin cambios; R17 libre.
- **D4:** inventario arriba, sin pruebas nuevas.
- **D5:** R18 (AUD-02-027) la corrige la 03-04; R19 (AUD-02-028) sigue `PENDIENTE_DESARROLLADOR`.

Decisiones técnicas del agente:

- **Ruido de registro:** `absorber_errores` envuelve `assertLogs` (`pedidos` y, donde hay 500, `django.request`) sin exigir que haya registros. Así, la prueba pasa cuando la corrección deje de registrar el error y no se queda roja por la forma de absorberlo.
- **Hora de R8 y R9:** el parche devuelve el instante en **UTC**. Con la zona de Chile, `.date()` daría el día de Chile y escondería el defecto.
- **R6c:** se reemplaza `pedidos.views.generar_respaldo_mysql` (el nombre donde lo busca la vista) por un archivo temporal; nunca corre `mysqldump`.
- **R15:** el comentario dice que la corrige la 07-02 (antes 06-05, RDA-014).

## Pendientes y riesgos

- **Decisión del desarrollador · R5:** reescribirla con otra hipótesis (tablas de zona horaria de producción, que no se pueden reproducir en local sin cambiar la configuración) o darla por cubierta con la parte de base de datos de R8. Queda en la sección 3 del registro.
- **Decisión del desarrollador · D4:** si `dashboard` y `estadisticas_bd` (escriben métricas con GET) se suman como regresión. Queda en la sección 3 del registro.
- **Hallazgo propuesto (para que lo decidas):** la causa de AUD-01-006 en producción no es la descrita en la auditoría. Dentro de un mismo día, la comprobación funciona en local. Los duplicados vienen del día en UTC (AUD-02-003) y, posiblemente, de la falta de tablas de zona horaria en el MySQL de producción. Verificarlo exige mirar producción. Pasos propuestos para el desarrollador: en una consola de MySQL de PythonAnywhere, `SELECT CONVERT_TZ('2026-10-15 12:00:00', 'UTC', 'America/Santiago');` (si devuelve `NULL`, faltan las tablas) y contar las filas de `HistorialBD` por hora UTC del día. Anotado también en `auditoria-tecnica.md` (notas de la 02-04), sin crear un ID.
- Ningún defecto nuevo de la aplicación.

## Commit sugerido

`Épica 2 - Iteración 02-04: agrega 18 regresiones que fallan a propósito (R5 no confirmada), unifica congelar_hora e inventaría las rutas que escriben con GET`
