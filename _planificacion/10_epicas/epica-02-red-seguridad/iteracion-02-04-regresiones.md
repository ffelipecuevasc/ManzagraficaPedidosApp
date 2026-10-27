# Iteración 02-04 · Pruebas de regresión de defectos conocidos

- **Épica:** 02 · Red de seguridad
- **Estado:** En revisión (ejecutada el 2026-10-27; [bitacora-02-04](../../99_bitacora/epica-02-red-seguridad/bitacora-02-04.md))
- **Subfase del plan:** 2.4
- **Depende de:** 02-01 y 02-03 (reutiliza sus ayudas y factorías)
- **RDA relacionadas:** RDA-006
- **Hallazgos que avanza:** AUD-01-002, AUD-01-006, AUD-02-001, AUD-02-002, AUD-02-003, AUD-02-004, AUD-02-005, AUD-02-006, AUD-02-008, AUD-02-025, AUD-02-027 y AUD-02-028. No cierra ninguno: cada prueba **documenta** el defecto y lo cerrará la iteración que lo corrija.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no despliega nada: solo agrega pruebas)

## Objetivo

Dejar una prueba por cada defecto conocido que **falla hoy a propósito** y pasará cuando se corrija. Es la parte de la épica que convierte la auditoría en una lista ejecutable: la prueba describe cómo debería comportarse el sistema, falla porque hoy no lo hace, y el día que la Épica 03, 04 o 06 lo corrija, pasa a verde y avisa que hay que quitar la marca.

La más importante de todo el plan es la pérdida silenciosa de ítems al editar.

## Cómo se escribe cada regresión (procedimiento obligatorio)

1. Escribir la prueba afirmando el **comportamiento correcto deseado**, no el síntoma del defecto.
2. Ejecutarla **sin** la marca y pegar en la bitácora el mensaje real del fallo. Comprobar que falla por el defecto y no por un error de montaje (datos mal armados, URL equivocada).
3. Agregar `@tag('regresion')` y `@unittest.expectedFailure`, con un comentario: `AUD-…`, qué falla hoy, qué iteración lo corrige.
4. Ejecutar tres veces seguidas y comprobar que el resultado es idéntico.

Detalle técnico útil: con `expectedFailure`, un error en `setUp` **no** cuenta como fallo esperado, sino como error; así un montaje roto no se disfraza de defecto detectado. Si un defecto hoy se corrige sin querer, el resumen informa `unexpected successes` y se quita la marca.

## Punto de partida (a verificar leyendo el código antes de escribir)

El mecanismo de fallos esperados está decidido en 02-01 y documentado en `docs/operacion/pruebas.md`, sección 7. Lo que sigue son los defectos con la evidencia disponible; el agente reconfirma cada uno antes de escribir su prueba.

## Regresiones a escribir (`pedidos/tests/test_regresiones.py`)

| # | Hallazgo | Comportamiento correcto que afirma la prueba | Qué pasa hoy | Lo corrige |
| :- | :------- | :------------------------------------------- | :----------- | :--------- |
| R1 | AUD-01-002 | Si falla un ítem al **editar un pedido**, los ítems anteriores siguen en la base | Se borran todos los ítems y se recrean hasta el fallo | 03-02 / 03-03 |
| R2 | AUD-01-002 | Lo mismo al **editar una cotización** | Igual que R1 | 03-02 / 03-03 |
| R3 | AUD-02-008 | Si falla un ítem al **crear un pedido**, no queda un pedido a medias | `transaction.atomic` existe, pero el `try/except` interno lo anula y el pedido queda con ítems parciales | 03-03 |
| R4 | AUD-01-002 | Lo mismo al **crear una cotización** | Cotización con ítems parciales | 03-03 |
| R5 | AUD-01-006 | Llamar dos veces `registrar_metricas_diarias()` el mismo día deja **una** fila de `HistorialBD` | Deja dos; la comprobación de duplicados no funciona (producción: 187 filas en 121 días). **No confirmada el 2026-10-27:** a mediodía deja una fila (`unexpected success`); no se escribió (ver bitácora) | 06-01 |
| R6 | AUD-02-006 y plan 4.1 | `cambiar_estado`, `duplicar_pedido` y `generar_respaldo_bd` rechazan GET (405) | Responden y escriben con GET | 04-01 |
| R7 | AUD-02-002 | La eliminación de un pago muestra una página de confirmación (200) | La plantilla `pedidos/pago_confirm_delete.html` no existe: error 500 (confirmado en producción) | 04-01 |
| R8 | AUD-02-003 | A las 22:00 de Chile, el panel y el chequeo diario usan el **día de Chile**, no el de UTC | Con 22:00 de Chile ya es el día siguiente en UTC | 06-01 |
| R9 | AUD-02-003 | El 31 a las 22:00 de Chile, «ingresos del mes» corresponden al **mes de Chile** | Usa el mes siguiente en UTC | 06-01 |
| R10 | AUD-02-004 | Un pedido creado con abono inicial queda con `estado_pago` coherente con sus pagos | Queda en `PENDIENTE` | 03-03 |
| R11 | AUD-02-004 | Editar el `valor_venta` de un pedido recalcula `estado_pago` | No lo recalcula | 03-03 |
| R12 | AUD-02-004 | Editar un pago que cambia de pedido recalcula **ambos** pedidos | No recalcula el pedido anterior | 03-03 |
| R13 | AUD-02-005 | Convertir dos veces la misma cotización crea **un** pedido y rechaza la segunda | Crea dos pedidos | 03-03 |
| R14 | AUD-02-001 | Eliminar un cliente con pedidos no borra su historial (se rechaza con `ProtectedError`) | Borra en cascada pedidos, ítems, pagos y cotizaciones | 04-06 |
| R15 | AUD-02-025 | Un pago de $29 sobre un pedido de $100 da `porcentaje_pagado == 29` (cálculo con enteros) | Da 28: divide con `float` y trunca (decisión del desarrollador, 2026-10-26, tras la 02-02) | 06-05 |
| R18 | AUD-02-027 | Convertir una cotización con `fecha_entrega` vacía **no** responde 500: rechaza la petición sin crear el pedido | Por lectura del código: el guardado del `DateField` falla y el decorador responde 500 (decisión del desarrollador, 2026-10-27, tras la 02-03) | 03-04 (decisión D5, 2026-10-27) |
| R19 | AUD-02-028 | El pedido duplicado queda con `creado_por` igual al usuario que lo duplicó | `creado_por` queda nulo (decisión del desarrollador, 2026-10-27, tras la 02-03) | `PENDIENTE_DESARROLLADOR` (04-01 o 03-03) |

R6 se escribe como tres pruebas (una por ruta); R10 a R12, R15, R18 y R19, una cada una. El total previsto era de **19**; el resultado es **18**, porque R5 no se confirmó (16 al redactar, más R15 agregada el 2026-10-26, más R18 y R19 agregadas el 2026-10-27). Los números R16 y R17 no tienen fila: R16 queda reservado para AUD-02-021 (decisión 2) y R17 sin asignar; R18 y R19 se numeraron así por decisión del desarrollador, sin renumerar las anteriores. La cifra exacta es la que queda en `pruebas.md` como `expected failures=N`.

**Condiciones propias de R18 y R19:**

- **R18:** al ejecutarla sin la marca, el fallo debe ser el motivo descrito (respuesta 500 o excepción por la fecha vacía), no un error de montaje. Si resulta `unexpected success`, la hipótesis era falsa: se reporta en la bitácora, no se registra como defecto y se propone retirar AUD-02-027.
- **R19:** debe fallar porque `creado_por` es nulo, no por otro motivo. No decide qué se copia al duplicar: esa pregunta del cliente (ítems y pagos) sigue abierta en `registro-pendientes.md`, sección 2.

## Tareas

0. **Limpieza previa:** unificar `congelar_hora` (hoy duplicada en `test_dinero.py` y `ayudas.py`) en un solo lugar, sin cambiar el comportamiento de ninguna prueba. Agregada el 2026-10-27; se ejecuta al empezar la 02-04, no antes.
1. **Orden de trabajo:** R15, R19, R13 y R14 (simples) → R18 → R7 y R6 → R10 a R12 → R5 → R8 y R9 → R1 a R4. Cada regresión sigue el procedimiento de arriba.
2. **Cálculo de referencia de `estado_pago`:** una función de pruebas que devuelve `PAGADO`, `PARCIAL` o `PENDIENTE` según la regla de `scripts/diagnostico/linea_base.sql` (`PAGADO` si `valor_venta - pagos <= 0`; `PARCIAL` si hay pagos; `PENDIENTE` si no). Sirve de oráculo para R10 a R12 y se prueba por separado.
3. **Hora fija de R8 y R9:** 22:00 de Chile en octubre es 01:00 UTC del día siguiente (Chile está en UTC−3). El agente verifica `TIME_ZONE` y `USE_TZ` en `settings.py` y parchea `django.utils.timezone.now` para que el reloj de las vistas devuelva ese instante. Los modelos con `default=timezone.now` no se ven afectados por el parche.
4. **Ruido de registro:** R1 a R4, R7 y R14 provocan errores que se registran; se absorben con `assertLogs`.
5. **Documentación.** En `docs/operacion/pruebas.md`, la tabla de regresiones declaradas (prueba, hallazgo, iteración que la hará pasar) y el valor de `expected failures=N`. En la auditoría, cada hallazgo apunta a su prueba.
6. **Bitácora** `bitacora-02-04.md`: por cada regresión, el mensaje real del fallo sin la marca y la confirmación de que es la razón correcta; la salida de tres ejecuciones seguidas.

## Criterios de aceptación

- [x] Existe una regresión por cada fila de la tabla (R1 a R15, R18 y R19, salvo R5, que no se confirmó y queda explicada en la bitácora), con `@tag('regresion')`, `@unittest.expectedFailure` y su comentario.
- [x] La bitácora muestra, para cada una, el fallo real sin la marca y que su causa es el defecto descrito.
- [x] **Tres ejecuciones seguidas** de `python manage.py test pedidos` dan el mismo resultado: todo en verde salvo `expected failures=N`, sin `unexpected successes` y sin errores.
- [x] `python manage.py test pedidos --exclude-tag regresion` queda en verde.
- [x] `docs/operacion/pruebas.md` lista las regresiones y el valor de `N` (sección 7.1, N = 18); `despliegue.md` acepta ese número (paso 1, sin cambios: remite a `pruebas.md`).
- [x] El diff no toca código de la aplicación.
- [x] Las decisiones `PENDIENTE_DESARROLLADOR` quedaron resueltas y registradas (salvo la iteración que corrige AUD-02-028, que el desarrollador dejó abierta a propósito, D5).

## Fuera de alcance

- Corregir cualquiera de los defectos.
- Regresiones de hallazgos de severidad baja o de rendimiento.
- Pruebas de control de acceso: 02-05.

## Decisiones del desarrollador

Resueltas por el desarrollador el 2026-10-27:

1. **D1 · Contrato de R1 a R4:** «todo o nada». Si falla un ítem, no queda rastro en la base: ni pedido o cotización a medias, ni ítems anteriores borrados.
2. **D2 · AUD-02-021:** no entra en la 02-04. R16 queda reservado; no se escribe esa prueba.
3. **D3 · Numeración:** se deja como está (R1 a R15, R16 reservado, R17 libre, R18 y R19). No se renumera.
4. **D4 · Inventario de rutas que escriben por GET:** el agente lo lista en la bitácora (ruta, vista, qué escribe, si lo cubre R6 o R7). No se escriben pruebas fuera de R6; el desarrollador decide cuáles se suman.
5. **D5 · Iteraciones:** AUD-02-028 (R19) sigue `PENDIENTE_DESARROLLADOR`; AUD-02-027 (R18) la corrige la 03-04.

## Datos requeridos del cliente

- Ninguno.