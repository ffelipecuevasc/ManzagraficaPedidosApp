# Épica 02 · Red de seguridad

- **Estado:** Terminada (2026-10-27). Sin despliegue propio: sus pruebas llegan al servidor con la próxima etiqueta (`v1.2`) y allí no se ejecutan. Cierre en [bitacora-02-cierre-epica](../../99_bitacora/epica-02-red-seguridad/bitacora-02-cierre-epica.md)
- **Fase del plan:** 2 (`plan-de-trabajo.md`, «FASE 2»)
- **Objetivo:** construir las pruebas automatizadas que permiten refactorizar la lógica crítica sin miedo. La aplicación maneja dinero y, hasta la 02-01, tenía cero pruebas.
- **Precondición:** Épica 00 completa. Puede avanzar en paralelo con la Épica 01.
- **Qué NO es:** no busca cobertura total. Cubre la lógica de dinero y exactamente las rutas de código que las Épicas 03, 04 y 05 van a modificar. Todo lo demás queda fuera.

## Alcance

1. Infraestructura de pruebas contra MySQL en Docker (RDA-006), con funciones o factorías de datos y archivos organizados por dominio.
2. Pruebas de la lógica de dinero: IVA y redondeo, totales, saldos, porcentajes, abonos, sobrepagos y las agregaciones del panel financiero comparadas contra un cálculo ingenuo.
3. Pruebas de los flujos críticos: crear y editar pedidos con ítems, convertir cotizaciones, cambiar estados, duplicar pedidos.
4. Pruebas de regresión que **fallan hoy** a propósito y pasarán cuando se corrija cada defecto. Además de las del plan (pérdida de ítems, escritura por GET y métricas duplicadas; para esta última, la regresión prevista R5 no se confirmó y el defecto real, el duplicado que deja el día en UTC, lo cubre R8), incluye las de la Auditoría 02: eliminación de pagos (AUD-02-002), fechas en UTC con la hora fijada a las 22:00 de Chile (AUD-02-003), `estado_pago` desincronizado (AUD-02-004), doble conversión de cotizaciones (AUD-02-005), borrado en cascada del historial de un cliente (AUD-02-001), el porcentaje pagado calculado con `float` (AUD-02-025, agregado tras la 02-02), la fecha de entrega vacía al convertir una cotización (AUD-02-027) y el pedido duplicado sin `creado_por` (AUD-02-028), agregados tras la 02-03. Recuento: 19 regresiones (R1 a R4, R6 ×3, R7 a R15, R18 a R20). R5, de las métricas duplicadas, no se confirmó y queda cubierta por R8; R20 (AUD-02-029, el 404 que responde 500) se sumó tras la 02-05.
5. Pruebas de control de acceso: anónimos, usuarios sin superusuario en las vistas de base de datos y endpoints JSON sin sesión.

Las reglas de negocio sin confirmar (`registro-pendientes.md`, sección 2) se fijan con el comportamiento actual y un comentario `PENDIENTE_CLIENTE` en la prueba, para que cambiarlas sea una decisión visible y no un accidente.

## Tres tipos de prueba (vocabulario común de la épica)

| Tipo | Qué fija | Estado hoy | Cómo se marca | Iteración |
| :--- | :------- | :--------- | :------------ | :-------- |
| **Caracterización** | Lo que el código hace **hoy**, esté bien o mal | Verde | Sin marca. Si la regla de negocio no está confirmada: comentario `PENDIENTE_CLIENTE` | 02-02, 02-03 |
| **Regresión de defecto conocido** | Lo que el código **debería** hacer | Rojo a propósito | `@tag('regresion')` + `@unittest.expectedFailure` + comentario con el `AUD-…` y la iteración que lo corrige | 02-04 |
| **Control de acceso** | Lo que **no** se debe poder hacer | Verde (o regresión, si el sistema deja pasar de más) | Sin marca; si revela un defecto, pasa a 02-04 como regresión | 02-05 |

Una prueba de caracterización nunca afirma que el comportamiento actual sea correcto: afirma que es el actual. Cuando una épica posterior lo cambie a propósito, la prueba se edita en el mismo cambio y la diferencia queda visible en el diff.

## Reglas comunes a todas las iteraciones de la épica

1. **No se cambia código de la aplicación.** Solo se agregan pruebas, factorías, ayudas de pruebas y documentación. Si al probar aparece un defecto, se anota en `registro-pendientes.md` (y, si corresponde, como regresión en 02-04); no se corrige aquí.
2. **Pruebas primero, y por la razón correcta.** Una regresión se escribe, se ejecuta sin la marca de fallo esperado, se pega en la bitácora el mensaje real del fallo y se comprueba que falla por el defecto y no por un error de montaje. Recién entonces se agrega la marca.
3. **Datos ficticios** (regla 7.4): nunca nombres, teléfonos ni montos copiados de la réplica ni de producción. Dinero en pesos enteros y cantidades con `Decimal` (regla 13).
4. **Tiempo controlado** (regla 6): toda prueba que dependa de «hoy» o del «mes» fija la hora. Por defecto, mediodía de Chile; las horas que cruzan la medianoche UTC se usan solo en las regresiones de AUD-02-003.
5. **Nada de escribir en el disco real:** toda prueba que toque `ImageField` o `media/` usa un `MEDIA_ROOT` temporal (`override_settings`), porque `media/` no tiene respaldo (AUD-02-023). Ninguna prueba ejecuta `mysql` ni `mysqldump` de verdad: se simulan con `mock`.
6. **Aislamiento:** cada prueba construye sus datos con las factorías y no depende del orden ni de otra prueba.
7. **Ruido de registro controlado:** las pruebas que provocan errores a propósito los absorben con `assertLogs`, para que la salida de `test` no se llene de trazas.
8. **Base de pruebas:** `test_manzagrafica`, con la paridad de `sql_mode` de producción (decidido en 02-01). Nunca una base real.
9. **Comando oficial:** `python manage.py test pedidos` (con `-v 2` para ver el nombre de la base). Para ver solo lo que debe estar en verde: `--exclude-tag regresion`.

## Iteraciones

| Iteración | Nombre | Subfase | Estado | Hallazgos que avanza |
| :-------- | :----- | :------ | :----- | :------------------- |
| 02-01 | [Infraestructura de pruebas](iteracion-02-01-infraestructura-pruebas.md) | 2.1 | Terminada (2026-10-25; desplegada en `v1.1-observabilidad`) | AUD-01-015, AUD-02-020 |
| 02-02 | [Pruebas de la lógica de dinero](iteracion-02-02-logica-dinero.md) | 2.2 | Terminada (2026-10-26; sin despliegue propio) | AUD-01-015, AUD-02-014, AUD-02-015 |
| 02-03 | [Pruebas de flujos críticos](iteracion-02-03-flujos-criticos.md) | 2.3 | Terminada (2026-10-27; sin despliegue propio) | AUD-01-015, AUD-02-013, AUD-02-014 |
| 02-04 | [Pruebas de regresión de defectos conocidos](iteracion-02-04-regresiones.md) | 2.4 | Terminada (2026-10-27; sin despliegue propio) | AUD-01-002, AUD-01-006, AUD-02-001 a AUD-02-006, AUD-02-008, AUD-02-025, AUD-02-027, AUD-02-028 |
| 02-05 | [Pruebas de control de acceso](iteracion-02-05-control-acceso.md) | 2.5 | Terminada (2026-10-27; sin despliegue propio) | AUD-01-015, AUD-01-018 |

**Orden recomendado:** 02-02 → 02-03 → 02-04 → 02-05. La 02-04 reutiliza las ayudas de la 02-03 (cómo enviar el formulario de ítems, cómo congelar la hora). La 02-05 es independiente y puede adelantarse si conviene.

Ninguna iteración de esta épica necesita migraciones, respaldo previo ni despliegue propio.

## Datos pendientes del cliente que esta épica necesita

Se usan como `PENDIENTE_CLIENTE` en las pruebas; ninguno bloquea la ejecución. Fuente: `registro-pendientes.md`, sección 2.

| Dato | Hallazgo | Iteración que lo fija con una prueba |
| :--- | :------- | :----------------------------------- |
| ¿El valor de una cotización es neto o incluye IVA? ¿El valor de venta del pedido debe ser igual a la suma de sus ítems? | AUD-02-014 | 02-02, 02-03 |
| Un pedido con valor de venta $0, ¿cuenta como pagado al 100 %? | — | 02-02 |
| ¿Se permite registrar pagos que superan el saldo (sobrepago)? | — | 02-02 |
| Al reabrir (duplicar) un pedido, ¿se copian sus ítems? | — | 02-03 |
| ¿Un pedido `ENTREGADO` atrasado debe contar como crítico? ¿Cómo se tratan los pedidos sin fecha de entrega en el trabajo semanal? | AUD-02-013 | 02-03 |

## Decisiones de la épica

- Las pruebas de regresión que fallan a propósito se marcan de forma que el conjunto se pueda ejecutar completo y el resultado distinga «fallo esperado» de «fallo nuevo». **Decidido en 02-01 (2026-10-25):** `unittest.expectedFailure` con `@tag('regresion')` y comentario con el hallazgo; procedimiento en `docs/operacion/pruebas.md`, sección 7.
- Esta épica no despliega nada por sí misma: solo agrega pruebas al repositorio. Las pruebas llegan al servidor con la siguiente etiqueta que se despliegue por otra razón, y allí no se ejecutan.
- Herramientas de prueba: `unittest`/`django.test` y `unittest.mock`, sin dependencias nuevas. Congelar la hora con `mock.patch` de `django.utils.timezone.now`; agregar una librería (por ejemplo `freezegun`) requeriría consulta y una RDA.
- La lista de regresiones declaradas (`expected failures=N`) vive en `docs/operacion/pruebas.md` y es el número que `despliegue.md` acepta en el resumen de `test`.

## Criterio de término

Cumplido el 2026-10-27 (decisión del desarrollador de cerrar la épica).

- [x] Las pruebas de regresión de 02-04 fallan de forma reproducible en tres ejecuciones seguidas, demostrando que capturan los defectos reales; el resto del conjunto está en verde. **Evidencia** ([bitacora-02-05-cierre](../../99_bitacora/epica-02-red-seguridad/bitacora-02-05-cierre.md)): tres ejecuciones de `python manage.py test pedidos -v 2` con `Ran 184 tests` y `OK (expected failures=19)`; `--exclude-tag regresion`: 165 en `OK`; `--tag regresion`: 19 fallos esperados. Cada regresión se ejecutó antes sin la marca para confirmar el motivo real del fallo ([bitacora-02-04](../../99_bitacora/epica-02-red-seguridad/bitacora-02-04.md)). Corrida de control del cierre de la épica en [bitacora-02-cierre-epica](../../99_bitacora/epica-02-red-seguridad/bitacora-02-cierre-epica.md).
- [x] La lógica de dinero (02-02), los flujos críticos (02-03) y el control de acceso (02-05) tienen pruebas en verde, con las reglas sin confirmar marcadas `PENDIENTE_CLIENTE`. **Evidencia:** `test_dinero.py` (02-02), `test_pedidos.py` y `test_cotizaciones.py` (02-03), `test_acceso.py` (02-05), todas dentro de las 165 en verde; las reglas sin confirmar, con su prueba, en «Resultados de la épica».
- [x] El comando de pruebas forma parte de la lista de comprobación de `docs/operacion/despliegue.md` (hecho en 02-01). **Evidencia:** paso 1 de `despliegue.md`, que acepta `OK (expected failures=N)` solo si N coincide con las regresiones declaradas.
- [x] `docs/operacion/pruebas.md` lista cada regresión declarada con su hallazgo y la iteración que la hará pasar. **Evidencia:** sección 7.1, 19 filas (R1 a R4, R6a a R6c, R7 a R15, R18 a R20) y «Valor vigente: `expected failures=19`».

## Resultados de la épica

Resumen al cierre (2026-10-27). Detalle y lecciones en [bitacora-02-cierre-epica](../../99_bitacora/epica-02-red-seguridad/bitacora-02-cierre-epica.md).

### Pruebas

De **86** (línea base al redactar las iteraciones 02-02 a 02-05, que ya incluía las 7 nuevas de la 02-01: de 10 a 17) a **184**: **98 nuevas**.

| Iteración | Pruebas al terminar | Nuevas | Archivos |
| :-------- | :------------------ | :----- | :------- |
| Línea base (incluye la 02-01) | 86 | — | `test_entorno.py`, `test_factorias.py` y las de la Épica 01 |
| 02-02 | 111 | 25 | `test_dinero.py` (23) y 2 de `momento_chile` en las factorías |
| 02-03 | 151 | 40 | `ayudas.py`, `test_pedidos.py`, `test_cotizaciones.py` |
| 02-04 | 170 | 19 | `test_regresiones.py`: 18 regresiones y la prueba del oráculo de `estado_pago` |
| 02-05 | 183 | 13 | `test_acceso.py` |
| Cierre de la 02-05 | 184 | 1 | R20 en `test_regresiones.py` |
| **Total** | **184** | **98** | 165 en verde y 19 fallos esperados |

### Regresiones (19)

La columna «La vuelve verde» usa la numeración vigente, con la anterior entre paréntesis cuando cambió (RDA-014). En `test_regresiones.py` y `pruebas.md`, R15 conserva «06-05» porque se escribió antes de esa regla.

| # | Hallazgo | Motivo real del fallo (sin la marca) | La vuelve verde |
| :- | :------- | :----------------------------------- | :-------------- |
| R1 | AUD-01-002 | Editar un pedido con un ítem que falla borra el ítem anterior y deja solo el nuevo | 03-03 |
| R2 | AUD-01-002 | Lo mismo al editar una cotización | 03-03 |
| R3 | AUD-02-008 | Crear un pedido con un ítem que falla deja el pedido con 1 ítem de 2 | 03-03 |
| R4 | AUD-01-002 | Crear una cotización con un ítem que falla deja la cotización con 1 ítem de 2 | 03-03 |
| R6a | AUD-02-006 | GET a `cambiar_estado` responde 302 y cambia el estado | 04-01 |
| R6b | AUD-02-006 | GET a `duplicar_pedido` responde 302 y crea el duplicado | 04-01 |
| R6c | AUD-02-006 | GET a `generar_respaldo_bd` responde 200 y genera el respaldo (simulado) | 04-01 |
| R7 | AUD-02-002 | Confirmar la eliminación de un pago responde 500: falta la plantilla | 04-01 |
| R8 | AUD-02-003 | A las 22:00 de Chile, un pedido de hoy cuenta como crítico y el panel escribe una 2.ª fila de métricas | 06-01 |
| R9 | AUD-02-003 | El 31 a las 22:00 de Chile, «ingresos del mes» da 0 (usa noviembre en UTC) | 06-01 |
| R10 | AUD-02-004 | Crear con abono deja `estado_pago` en `PENDIENTE` | 03-03 |
| R11 | AUD-02-004 | Subir `valor_venta` deja `estado_pago` en `PAGADO` | 03-03 |
| R12 | AUD-02-004 | Mover un pago de pedido deja el anterior en `PAGADO` | 03-03 |
| R13 | AUD-02-005 | Convertir dos veces la misma cotización crea 2 pedidos | 03-03 |
| R14 | AUD-02-001 | Eliminar un cliente con pedidos no lanza `ProtectedError` (borra en cascada) | 04-06 |
| R15 | AUD-02-025 | `porcentaje_pagado` da 28 en vez de 29 (`float`) | 07-02 (antes 06-05), junto con AUD-02-015 |
| R18 | AUD-02-027 | Convertir sin fecha de entrega responde 500 (`ValidationError`) | 03-04 |
| R19 | AUD-02-028 | El duplicado queda con `creado_por` nulo | `PENDIENTE_DESARROLLADOR` |
| R20 | AUD-02-029 | Con un `pk` inexistente, 12 vistas responden 500 en vez de 404 | 03-01 |

- **R5 (AUD-01-006): no confirmada, sin prueba.** Dos llamadas a `registrar_metricas_diarias()` a mediodía dejan una fila. Queda cubierta por R8 (decisión del desarrollador, 2026-10-27). El número R5 sigue sin asignar.
- **R16** reservado para AUD-02-021; **R17** libre.

### Hallazgos nuevos de la épica

| ID | Severidad | Hallazgo | Estado |
| :- | :-------- | :------- | :----- |
| AUD-02-025 | Baja | Porcentaje pagado con `float` | Abierto; R15; 07-02 (antes 06-05) |
| AUD-02-026 | Baja | Pedido de $0 en `estadisticas_pagos` cuenta como pagado y sin abono | Abierto; sin regresión hasta que el cliente responda |
| AUD-02-027 | Baja | Fecha de entrega vacía al convertir: 500 | Abierto; R18; 03-04 |
| AUD-02-028 | Baja | Duplicado con `creado_por` nulo | Abierto; R19; iteración `PENDIENTE_DESARROLLADOR` |
| AUD-02-029 | Baja | `@transaccion_segura` convierte el 404 en 500 | Abierto; R20; 03-01 |
| AUD-02-030 | Baja | Recuperación de contraseña y acceso del panel de administración sin sesión | Abierto; sin regresión; Épica 04 |

Además: notas sin ID nuevo en AUD-01-006 (causa más consistente, no verificada en producción), AUD-01-025 (`@login_required` sobre `es_superusuario`) y la definición de la Épica 04 (302 en vez de 401 y 403). Regla de negocio confirmada: el precio de cada ítem lo fija el vendedor (no es defecto).

### Datos del cliente fijados como `PENDIENTE_CLIENTE`

| Dato | Prueba que lo fija |
| :--- | :----------------- |
| ¿El valor de la cotización es neto o incluye IVA? (AUD-02-014) | `test_cotizaciones.ConvertirCotizacionTests.test_valor_venta_es_el_valor_total_sin_iva` |
| ¿El valor de venta del pedido debe ser igual a la suma de sus ítems? (AUD-02-014) | `test_dinero.SubtotalItemsTests.test_valor_venta_distinto_de_la_suma_de_items_se_acepta` |
| Un pedido de $0, ¿cuenta como pagado al 100 %? | `test_dinero.SaldoPedidoTests.test_matriz_de_saldos`, `AbonoInicialTests.test_matriz_de_abonos`, `EstadisticasPagosOraculoTests.test_pedido_de_valor_cero_cuenta_como_pagado_y_sin_abono` |
| ¿Se permite el sobrepago? | `test_dinero.SaldoPedidoTests.test_matriz_de_saldos` y el conjunto de `EstadisticasPagosOraculoTests` |
| Al duplicar un pedido, ¿se copian ítems y pagos? | `test_pedidos.DuplicarPedidoTests.test_lo_que_no_se_copia` |
| ¿Un pedido `ENTREGADO` atrasado es crítico? ¿Cómo se tratan los pedidos sin fecha? (AUD-02-013) | `test_dinero.DashboardOraculoTests`, `test_pedidos.ClasificacionTests.test_trabajo_semanal` y `test_panel` |

## Fuera de alcance de la épica

- Corregir cualquier defecto (Épicas 03, 04 y 06).
- Cobertura total, medición de cobertura o ejecución automática en GitHub.
- Probar el modo estricto de `sql_mode` (04-05).
- Probar plantillas, estilos o JavaScript del navegador.

## Notas

- **2026-10-21 (00-03, AUD-02-020):** la réplica local usa `sql_mode = NO_ENGINE_SUBSTITUTION`, igual que producción. En 02-01 se decide si la base de pruebas activa el modo estricto por conexión (`OPTIONS["init_command"]` en la configuración de pruebas). Eso cambia la configuración y requiere consulta. Las pruebas que dependen del truncado silencioso de producción deben declararlo.
- **2026-10-25 (01-01, antes de la 02-01 por decisión del desarrollador):** las pruebas de 01-01 corrieron con la infraestructura existente, sin cambiar configuración ni privilegios: Django crea y destruye `test_<DB_NAME>` (con `DB_NAME=manzagrafica_replica`, la base es `test_manzagrafica_replica`) y el usuario local tiene permiso para hacerlo. Las pruebas siguen en `pedidos/tests.py` (10 en total). Queda para la 02-01: paquete de pruebas por dominio, factorías, modo estricto en la base de pruebas (la advertencia `mysql.W002` sigue apareciendo), un nombre de base de pruebas fijo en `TEST` que no dependa de `DB_NAME`, y el mecanismo de fallos esperados. Detalle en la sección «Para la 02-01» de [bitacora-01-01](../../99_bitacora/epica-01-observabilidad/bitacora-01-01.md).
- **2026-10-25 (02-01):** decidido el mecanismo de fallos esperados: `unittest.expectedFailure` con `@tag('regresion')` y comentario con el hallazgo; procedimiento en `docs/operacion/pruebas.md`. Las regresiones de 02-04 lo usan.
- **2026-10-26:** redactadas las iteraciones 02-02 a 02-05 y actualizada esta definición (estado, vocabulario de tipos de prueba, reglas comunes, datos del cliente por iteración). Línea base de pruebas al redactar: 86 en `main` (79 de la etiqueta `v1.1-observabilidad` más 7 de la 01-09, aún sin desplegar); cada iteración mide la cifra real al empezar.
- **2026-10-26 (cierre de la 02-02):** 02-02 terminada con 111 pruebas. AUD-02-025 (porcentaje pagado con `float`) se suma a la 02-04 como R15: recuento previsto de 17 regresiones (antes, alrededor de 16). AUD-02-026 (pedido de $0 en `estadisticas_pagos`) queda solo en la auditoría. AUD-02-014 (valor de la cotización) lo fija la 02-03.
- **2026-10-27 (cierre de la 02-03):** 02-03 terminada. El precio del ítem que ajusta a mano el vendedor es regla de negocio confirmada (sin hallazgo). AUD-02-027 (fecha de entrega vacía al convertir) y AUD-02-028 (duplicado sin `creado_por`) se suman a la 02-04 como R18 y R19: recuento previsto de 19 regresiones. La 02-04 suma una tarea 0 para unificar `congelar_hora`.
- **2026-10-27 (02-04):** 18 regresiones en `test_regresiones.py`, `OK (expected failures=18)` en tres ejecuciones. R5 (AUD-01-006) no se confirmó y no se escribió: el previsto de 19 queda en 18. Decisiones D1 a D5 en la iteración.
- **2026-10-27 (cierre de la 02-04):** 02-04 terminada. R5 queda cubierta por R8; `dashboard` y `estadisticas_bd` no se suman como regresión (los resuelve la 06-02; corregido el 2026-10-27, antes decía 06-01).
- **2026-10-27 (02-05):** control de acceso fijado en `test_acceso.py` (13 pruebas). Mecanismo: decoradores vista por vista. Sin rutas públicas nuevas en `pedidos/urls.py`; recuento de la 02-04 sin cambios (18). Hallazgo propuesto principal: `@transaccion_segura` convierte el 404 en 500.
- **2026-10-27 (cierre de la 02-05):** 02-05 terminada. AUD-02-029 (el 404 que responde 500) con regresión R20 en la 02-04: recuento de 19. AUD-02-030 (recuperación de contraseña y acceso del panel de administración sin sesión) sin regresión, para la Épica 04. Nota en AUD-01-025 (`@login_required` sobre `es_superusuario`) y en la definición de la Épica 04 (302 en vez de 401 y 403).
- **2026-10-27 (cierre de la épica):** decisiones del desarrollador. (1) La épica se cierra ahora: su criterio de término está cumplido; no despliega nada por sí misma y sus pruebas llegan al servidor con `v1.2`, donde no se ejecutan. (2) Numeración: lo escrito antes de RDA-014 no se reescribe; toda referencia nueva usa la numeración vigente con la anterior entre paréntesis, por ejemplo «07-02 (antes 06-05)»; R15 queda con «06-05» en los documentos ya escritos. (3) AUD-02-028 (R19) sigue `PENDIENTE_DESARROLLADOR`. Detalle en [bitacora-02-cierre-epica](../../99_bitacora/epica-02-red-seguridad/bitacora-02-cierre-epica.md).
