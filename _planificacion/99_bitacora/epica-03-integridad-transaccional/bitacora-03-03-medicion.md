# Bitácora 03-03 · Medición de consultas (regla 12)

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (la 03-03 sigue En revisión: falta la revisión manual del desarrollador). Solo mediciones y documentos; sin cambios en el código de la aplicación.

## Resumen

Se midió el número de consultas SQL del camino feliz de las vistas que tocó la 03-03, antes y después, para cerrar la desviación del paso 0 de la iteración («registrar el número de consultas», regla 12 de `AGENTS.md`), que [bitacora-03-03](bitacora-03-03.md) dejó declarada como no medida. La decisión de medirla es del desarrollador (2026-11-04). Complementa esa bitácora, que no se edita (regla 5.4). Las cifras se informan sin juzgarlas.

## Método

- **Qué se contó:** todas las consultas SQL de una petición (`CaptureQueriesContext` sobre la conexión, con el cliente de pruebas de Django), incluida la sesión, el usuario, `BEGIN` y `COMMIT`. Una petición por vista, con los mismos datos sintéticos y las mismas peticiones en ambos árboles: cabecera con 2 ítems (cantidades `2` y `1,5`), un abono de $4.000 al crear el pedido y de $5.000 al convertir.
- **Modo de transacción:** `TransactionTestCase` (autocommit, como en producción). Con `TestCase` cada `transaction.atomic()` habría sumado `SAVEPOINT` y `RELEASE SAVEPOINT` que en producción no existen, y los eventos (`on_commit`) no se habrían escrito. Con `TransactionTestCase` el evento sí se escribe y se cuenta su `INSERT`.
- **Calentamiento:** un `GET /clientes/lista/` antes de medir, igual en ambas mediciones.
- **Repetición:** cada árbol midió **dos vueltas** completas con datos nuevos; las dos dieron las mismas cifras en las nueve peticiones.
- **Después:** árbol actual, commit `501c0b0` (la 03-03).
- **Antes:** commit `b553aa3` (el último previo a la ejecución de la 03-03; su código es el de la 03-02 terminada), en un `git worktree` desacoplado (`--detach`) dentro de la carpeta temporal de la sesión, **fuera del repositorio**, sin tocar el árbol de trabajo ni cambiar de rama. El archivo de medición se copió ahí tal cual.
- **Configuración:** el worktree no tiene `.env`; un lanzador temporal cargó el `.env` del árbol principal dentro del propio proceso de Python (como lo hace la aplicación) y fijó `DB_NAME=manzagrafica_replica`. El contenido del `.env` no se leyó ni se mostró.
- **Base:** solo la base de pruebas `test_manzagrafica`, con datos sintéticos. No se consultó la réplica.
- **Limpieza:** el worktree se eliminó (`git worktree remove --force` y `prune`), también el archivo temporal `test_medicion_consultas.py` y su `.pyc`. `git status --short` quedó vacío y `git worktree list` muestra solo el árbol principal.

## Resultado

Consultas por petición. «Sin BEGIN/COMMIT» descuenta las dos consultas de control de transacción que Django registra cuando una vista usa `transaction.atomic()` o un borrado en cascada. «S/I/U/D» es el desglose SELECT/INSERT/UPDATE/DELETE de cada medición.

| Vista | Antes | Después | Dif. | Antes sin BEGIN/COMMIT | Después sin BEGIN/COMMIT | Dif. | Antes S/I/U/D | Después S/I/U/D | Código HTTP antes→después |
| :---- | --: | --: | --: | --: | --: | --: | :-- | :-- | :-- |
| `crear_pedido` (con abono) | 13 | 16 | +3 | 11 | 14 | +3 | 6/5/0/0 | 8/5/1/0 | 302→302 |
| `editar_pedido` | 14 | 17 | +3 | 12 | 15 | +3 | 7/3/1/1 | 9/3/2/1 | 302→302 |
| `crear_cotizacion` | 9 | 11 | +2 | 9 | 9 | 0 | 6/3/0/0 | 6/3/0/0 | 302→302 |
| `editar_cotizacion` | 13 | 13 | 0 | 11 | 11 | 0 | 7/2/1/1 | 7/2/1/1 | 302→302 |
| `convertir_a_pedido` (GET) | 4 | 4 | 0 | 4 | 4 | 0 | 4/0/0/0 | 4/0/0/0 | 200→200 |
| `convertir_a_pedido` (POST, con abono) | 15 | 19 | +4 | 15 | 17 | +2 | 8/5/2/0 | 10/5/2/0 | 302→302 |
| `ingresar_pago` | 9 | 11 | +2 | 9 | 9 | 0 | 6/2/1/0 | 6/2/1/0 | 302→302 |
| `editar_pago` (a otro pedido) | 10 | 15 | +5 | 10 | 13 | +3 | 7/1/2/0 | 9/1/3/0 | 302→302 |
| `eliminar_pago` | 8 | 10 | +2 | 8 | 8 | 0 | 5/1/1/1 | 5/1/1/1 | 302→302 |
| **Suma de las 9 peticiones** | **95** | **116** | **+21** | **89** | **100** | **+11** | | | |

- En las nueve peticiones el código HTTP es el mismo antes y después: ninguna vista se pudo comparar «a la fuerza»; no hubo caminos que fallaran ni que cambiaran de código de respuesta.
- Aun así, el trabajo que hace cada vista **no es idéntico** en tres casos, por diseño de la 03-03: `crear_pedido` y `editar_pedido` ahora recalculan `estado_pago`; `editar_pago` ahora también recalcula el pedido anterior; y `convertir_a_pedido` ahora lee la cotización con bloqueo y valida un formulario. En esos casos la cifra compara dos comportamientos distintos, no dos formas de hacer lo mismo.

### Origen de la diferencia (inferido por lectura del código, no medido por separado)

- `BEGIN` y `COMMIT` (2 consultas por vista): el nuevo `transaction.atomic()`. En `editar_pedido` y `editar_cotizacion` el «antes» ya los tenía, por el borrado de ítems.
- Recálculo de `estado_pago` (`actualizar_estado_pago_pedido`): 2 SELECT y 1 UPDATE. Aparece en `crear_pedido`, `editar_pedido` y, dos veces, en `editar_pago`. En `ingresar_pago` y `convertir_a_pedido` la lógica ya existía en línea, por eso allí no suma consultas de recálculo.
- `convertir_a_pedido` (POST): +2 SELECT. Uno corresponde a la relectura de la cotización con bloqueo dentro de la transacción. El otro, a que el ayudante de `estado_pago` hace dos agregados (saldo y total pagado) donde la lógica en línea anterior hacía uno. El formulario no consulta la base.

## Límites

- **Datos sintéticos** de la base de pruebas y de una sola forma (2 ítems por cabecera, un abono). Las consultas por ítem (un `Producto` y un `INSERT` por ítem en las vistas de ítems) crecen con la cantidad de ítems; no se midió ese crecimiento.
- **Solo el camino feliz.** No se midieron los caminos de error (formulario inválido, ítem fallido, cotización ya aceptada) ni la página 500.
- **Solo consultas, no tiempo.** No hay medición de milisegundos ni de CPU. Una consulta no pesa lo mismo que otra.
- **Sin tráfico real:** una sola petición por vista, con el cliente de pruebas de Django; no es producción (un solo worker, uWSGI, PythonAnywhere ni MySQL de producción). La cuenta de `BEGIN` y `COMMIT` depende de cómo el motor de MySQL de Django registra el control de transacción.
- **Comparación de comportamiento distinto** en `crear_pedido`, `editar_pedido`, `editar_pago` y `convertir_a_pedido` (ver arriba).
- El «antes» corre con el mismo `requirements.txt` y las mismas dependencias del entorno virtual principal.
- Las vistas de lectura (listados y detalles) no se tocaron en la 03-03 y no se midieron.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/99_bitacora/epica-03-integridad-transaccional/bitacora-03-03-medicion.md` | Esta bitácora (nueva). |
| `_planificacion/10_epicas/epica-03-integridad-transaccional/iteracion-03-03-fronteras-transaccionales-por-vista.md` | Nota fechada bajo «Decisiones del desarrollador». |
| `_planificacion/00_producto/registro-pendientes.md` | Una línea de historial. |

Archivos temporales (borrados): `pedidos/tests/test_medicion_consultas.py`, su copia en el worktree y el worktree mismo. No se tocó el código de la aplicación.

## Verificación

- Medición «después»: `OK` (1 prueba, 2 vueltas iguales). Medición «antes»: `OK` (1 prueba, 2 vueltas iguales).
- No se ejecutó la suite completa (no hay cambios de código). La de la 03-03 está en [bitacora-03-03](bitacora-03-03.md): 220 pruebas, `OK (expected failures=9)` en tres ejecuciones.
- `git status --short` al terminar: vacío antes de agregar estos documentos.

## Commit sugerido

`Épica 3 - Iteración 03-03: mide las consultas por vista antes y después (95 y 116 en las nueve peticiones) y cierra la desviación del paso 0`
