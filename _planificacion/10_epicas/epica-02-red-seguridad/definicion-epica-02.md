# Épica 02 · Red de seguridad

- **Estado:** En curso (02-01 a 02-03 terminadas; 02-04 en revisión; 02-05 redactada, sin ejecutar)
- **Fase del plan:** 2 (`plan-de-trabajo.md`, «FASE 2»)
- **Objetivo:** construir las pruebas automatizadas que permiten refactorizar la lógica crítica sin miedo. La aplicación maneja dinero y, hasta la 02-01, tenía cero pruebas.
- **Precondición:** Épica 00 completa. Puede avanzar en paralelo con la Épica 01.
- **Qué NO es:** no busca cobertura total. Cubre la lógica de dinero y exactamente las rutas de código que las Épicas 03, 04 y 05 van a modificar. Todo lo demás queda fuera.

## Alcance

1. Infraestructura de pruebas contra MySQL en Docker (RDA-006), con funciones o factorías de datos y archivos organizados por dominio.
2. Pruebas de la lógica de dinero: IVA y redondeo, totales, saldos, porcentajes, abonos, sobrepagos y las agregaciones del panel financiero comparadas contra un cálculo ingenuo.
3. Pruebas de los flujos críticos: crear y editar pedidos con ítems, convertir cotizaciones, cambiar estados, duplicar pedidos.
4. Pruebas de regresión que **fallan hoy** a propósito y pasarán cuando se corrija cada defecto. Además de las del plan (pérdida de ítems, métricas duplicadas, escritura por GET), incluye las de la Auditoría 02: eliminación de pagos (AUD-02-002), fechas en UTC con la hora fijada a las 22:00 de Chile (AUD-02-003), `estado_pago` desincronizado (AUD-02-004), doble conversión de cotizaciones (AUD-02-005), borrado en cascada del historial de un cliente (AUD-02-001), el porcentaje pagado calculado con `float` (AUD-02-025, agregado tras la 02-02), la fecha de entrega vacía al convertir una cotización (AUD-02-027) y el pedido duplicado sin `creado_por` (AUD-02-028), agregados tras la 02-03. Recuento previsto: 19 regresiones.
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
| 02-04 | [Pruebas de regresión de defectos conocidos](iteracion-02-04-regresiones.md) | 2.4 | En revisión (2026-10-27; sin despliegue propio) | AUD-01-002, AUD-01-006, AUD-02-001 a AUD-02-006, AUD-02-008, AUD-02-025, AUD-02-027, AUD-02-028 |
| 02-05 | [Pruebas de control de acceso](iteracion-02-05-control-acceso.md) | 2.5 | Redactada, sin ejecutar | AUD-01-015, AUD-01-018 |

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

- Las pruebas de regresión de 02-04 fallan de forma reproducible en tres ejecuciones seguidas, demostrando que capturan los defectos reales; el resto del conjunto está en verde.
- La lógica de dinero (02-02), los flujos críticos (02-03) y el control de acceso (02-05) tienen pruebas en verde, con las reglas sin confirmar marcadas `PENDIENTE_CLIENTE`.
- El comando de pruebas forma parte de la lista de comprobación de `docs/operacion/despliegue.md` (hecho en 02-01).
- `docs/operacion/pruebas.md` lista cada regresión declarada con su hallazgo y la iteración que la hará pasar.

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
