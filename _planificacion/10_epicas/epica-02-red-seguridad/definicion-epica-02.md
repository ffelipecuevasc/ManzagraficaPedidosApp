# Épica 02 · Red de seguridad

- **Estado:** Pendiente
- **Fase del plan:** 2 (`plan-de-trabajo.md`, «FASE 2»)
- **Objetivo:** construir las pruebas automatizadas que permiten refactorizar la lógica crítica sin miedo. La aplicación maneja dinero y hoy tiene cero pruebas.
- **Precondición:** Épica 00 completa. Puede avanzar en paralelo con la Épica 01.

## Alcance

1. Infraestructura de pruebas contra MySQL en Docker (RDA-006), con funciones o factorías de datos y archivos organizados por dominio.
2. Pruebas de la lógica de dinero: IVA y redondeo, totales, saldos, porcentajes, abonos, sobrepagos y las agregaciones del panel financiero comparadas contra un cálculo ingenuo.
3. Pruebas de los flujos críticos: crear y editar pedidos con ítems, convertir cotizaciones, cambiar estados, duplicar pedidos.
4. Pruebas de regresión que **fallan hoy** a propósito y pasarán cuando se corrija cada defecto. Además de las del plan (pérdida de ítems, métricas duplicadas, escritura por GET), incluye las de la Auditoría 02: eliminación de pagos (AUD-02-002), fechas en UTC con la hora fijada a las 22:00 de Chile (AUD-02-003), `estado_pago` desincronizado (AUD-02-004), doble conversión de cotizaciones (AUD-02-005) y borrado en cascada del historial de un cliente (AUD-02-001).
5. Pruebas de control de acceso: anónimos, usuarios sin superusuario en las vistas de base de datos y endpoints JSON sin sesión.

Las reglas de negocio sin confirmar (`registro-pendientes.md`, sección 2) se fijan con el comportamiento actual y un comentario `PENDIENTE_CLIENTE` en la prueba, para que cambiarlas sea una decisión visible y no un accidente.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 02-01 | Infraestructura de pruebas | 2.1 |
| 02-02 | Pruebas de la lógica de dinero | 2.2 |
| 02-03 | Pruebas de flujos críticos | 2.3 |
| 02-04 | Pruebas de regresión de defectos conocidos | 2.4 |
| 02-05 | Pruebas de control de acceso | 2.5 |

## Decisiones de la épica

- Las pruebas de regresión que fallan a propósito se marcan de forma que el conjunto se pueda ejecutar completo y el resultado distinga «fallo esperado» de «fallo nuevo» (por ejemplo, con `unittest.expectedFailure`). El mecanismo se decide en 02-01.
- Esta épica no despliega nada: solo agrega pruebas al repositorio.

## Criterio de término

- Las pruebas de regresión de 02-04 fallan de forma reproducible en tres ejecuciones seguidas, demostrando que capturan los defectos reales; el resto del conjunto está en verde.
- El comando de pruebas forma parte de la lista de comprobación de `docs/operacion/despliegue.md`.

## Notas

- **2026-10-21 (00-03, AUD-02-020):** la réplica local usa `sql_mode = NO_ENGINE_SUBSTITUTION`, igual que producción. En 02-01 se decide si la base de pruebas activa el modo estricto por conexión (`OPTIONS["init_command"]` en la configuración de pruebas). Eso cambia la configuración y requiere consulta. Las pruebas que dependen del truncado silencioso de producción deben declararlo.
- **2026-10-25 (01-01, antes de la 02-01 por decisión del desarrollador):** las pruebas de 01-01 corrieron con la infraestructura existente, sin cambiar configuración ni privilegios: Django crea y destruye `test_<DB_NAME>` (con `DB_NAME=manzagrafica_replica`, la base es `test_manzagrafica_replica`) y el usuario local tiene permiso para hacerlo. Las pruebas siguen en `pedidos/tests.py` (10 en total). Queda para la 02-01: paquete de pruebas por dominio, factorías, modo estricto en la base de pruebas (la advertencia `mysql.W002` sigue apareciendo), un nombre de base de pruebas fijo en `TEST` que no dependa de `DB_NAME`, y el mecanismo de fallos esperados. Detalle en la sección «Para la 02-01» de [bitacora-01-01](../../99_bitacora/epica-01-observabilidad/bitacora-01-01.md).
