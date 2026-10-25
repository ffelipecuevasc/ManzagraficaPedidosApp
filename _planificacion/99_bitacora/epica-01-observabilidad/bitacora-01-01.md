# Bitácora 01-01 · Modelo de registro de eventos

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada (2026-10-25, revisada por el desarrollador). Se despliega junto con 01-02 a 01-05 en 01-06 (`v1.1-observabilidad`), con respaldo previo.

## Resumen

- **Tarea 1, decisión documentada:** RDA-013 escrita en `decisiones.md`: errores con `logging` a `error.log` y eventos de negocio en MySQL. RDA-005 queda «Reemplazada en parte por RDA-013», en su ficha y en el índice. AUD-01-005 tiene la solución actualizada. En `registro-pendientes.md`, la decisión de retención queda solo para la tabla de eventos y los nombres de 01-01, 01-02, 01-03 y 01-05 siguen a los archivos de iteración.
- **Tarea 2, estimación:** ~1.200 filas y ~0,6 MB por mes; ~18 MB al cabo de un año contando los respaldos (5,4 % del disco libre). Detalle abajo.
- **Tareas 3 y 4, modelo e índices:** `RegistroEvento` en `pedidos/models.py`, con `momento`, `tipo` (15 opciones cerradas), `usuario` (admite nulo, `SET_NULL`), `entidad`, `entidad_id` y `resumen` (255 caracteres, solo identificadores). Índices sobre `momento`, sobre `tipo` y `momento` juntos, y sobre `usuario_id` (el que MySQL crea con la clave foránea).
- **Tarea 5, retención y purga:** `pedidos/eventos.py` con `RETENCION_EVENTOS_DIAS = 365`, `limite_retencion()` y `purgar_eventos()`, que devuelve las filas eliminadas. La orden `python manage.py purgar_registros [--dias N]` la ejecuta e informa el resultado.
- **Tarea 6, migración:** `0007_registroevento`, Clase 2, aplicada en la réplica en 1,25 s.
- **Pruebas:** 4 nuevas en `pedidos/tests.py`, `RegistroEventoTests`: purga que conserva solo los recientes (incluye un evento 1 segundo pasado el límite), rechazo de retención menor a 1 día, salida de la orden y eventos que sobreviven al borrar su usuario.

## Decisiones del desarrollador (2026-10-25)

- Tomar la 01-01 antes que la 02-01, y montar solo el mínimo de pruebas indispensable.
- **Retención: 365 días**, confirmados tras la estimación. Se quitó el `PENDIENTE_DESARROLLADOR`.
- Autorizada la creación de la migración 0007 y su aplicación en la réplica como Clase 2, con la observación del `ALTER TABLE` (abajo).

## Estimación de crecimiento (tarea 2)

Fuente: `linea-base-produccion.md` (medida el 2026-10-20). Supuestos pesimistas: se toma el mes con más pedidos (febrero, 121; el promedio es ~87).

| Evento | Filas por mes | Supuesto |
| :----- | :------------ | :------- |
| Pedido creado | 121 | Mes más alto medido |
| Pedido modificado | 242 | 2 modificaciones por pedido |
| Cambio de estado | 363 | 3 transiciones por pedido (pendiente, en proceso, terminado, entregado) |
| Pedido duplicado y eliminado | 24 | 10 % de los pedidos, cada uno |
| Pago registrado | 149 | 1.033 pagos en ~9,7 meses (~107), escalado al mes más alto |
| Pago modificado y eliminado | 30 | 10 % de los pagos, cada uno |
| Cotización convertida; cliente o producto eliminado | 15 | 25 cotizaciones en ~10 meses, más margen |
| Acceso exitoso y fallido | 180 | 5 accesos y 1 fallido por día |
| Respaldo y restauración | 11 | — |
| **Total** | **~1.135, redondeado a 1.200** | |

- **Tamaño de fila supuesto: 500 bytes con índices.** Los datos de la fila suman ~140 bytes: 8 de `id`, 8 de `momento`, ~22 de `tipo`, ~10 de `entidad`, 4 de `entidad_id`, 4 de `usuario_id` y ~80 de `resumen`. Ese valor se multiplica por ~2 por la sobrecarga de InnoDB (cabecera de fila y páginas que no se llenan) y se le suman 3 índices secundarios de ~30 a 50 bytes cada uno, también con sobrecarga.
- **Resultado:** 1.200 × 500 B ≈ **0,6 MB por mes**, que llegan a **~7,2 MB** en régimen con 365 días de retención.
- **Efecto en los respaldos:** un evento ocupa unos 150 bytes en el volcado SQL. Al año, cada volcado crece ~2,2 MB; con los 5 volcados del servidor, son ~11 MB.
- **Total en régimen: ~18 MB.** El disco libre es de 331,2 MB (180,8 MB usados de 512 MB al 2026-10-20): la tabla sola usa el 2,2 % y la tabla con los respaldos, el **5,4 %**. No hace falta reducir el inventario.
- La cifra real se mide una semana después del despliegue (criterio de término de la épica, 01-06).

## SQL de la migración 0007 (`sqlmigrate pedidos 0007`)

```sql
--
-- Create model RegistroEvento
--
CREATE TABLE `pedidos_registroevento` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `momento` datetime(6) NOT NULL, `tipo` varchar(40) NOT NULL, `entidad` varchar(30) NOT NULL, `entidad_id` integer UNSIGNED NULL CHECK (`entidad_id` >= 0), `resumen` varchar(255) NOT NULL, `usuario_id` integer NULL);
ALTER TABLE `pedidos_registroevento` ADD CONSTRAINT `pedidos_registroevento_usuario_id_b991a708_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`);
CREATE INDEX `evento_momento_idx` ON `pedidos_registroevento` (`momento`);
CREATE INDEX `evento_tipo_momento_idx` ON `pedidos_registroevento` (`tipo`, `momento`);
```

**Clase 2 (aditiva).** Crea una tabla nueva con sus índices y no altera ninguna tabla existente.

## Desviaciones y observaciones

- **`ALTER TABLE` en el SQL.** El criterio pedía «solo `CREATE TABLE` y `CREATE INDEX`». Django agrega la clave foránea hacia `auth_user` con un `ALTER TABLE` sobre la **tabla nueva**, que está vacía. `auth_user` no se modifica. Se consultó antes de aplicar y el desarrollador la aprobó como Clase 2.
- **Borrado de usuarios:** `on_delete=SET_NULL` lo gestiona Django; la restricción de MySQL no lleva `ON DELETE`. Un borrado hecho fuera de Django (SQL directo) sería rechazado por la clave foránea, no dejaría eventos huérfanos.
- **Eventos del sistema:** el modelo no tiene un campo de origen. La 01-04 identifica el origen con usuario nulo y el resumen. Si la 01-04 necesita un campo propio, es una columna que admite nulo (Clase 2).
- **Duración de la migración:** 1,25 s medidos con `Measure-Command` sobre el comando completo, incluido el arranque de Python y Django. La sentencia SQL tarda bastante menos.
- **Pruebas en `pedidos/tests.py`** y no en un paquete por dominio, igual que en la 00-06: convertir el archivo en paquete significa moverlo, y eso requiere consulta. Queda para la 02-01.
- **Los tipos de evento** siguen la propuesta de partida del plan para la 01-04. Si la 01-04 cierra un inventario distinto, cambiar las opciones es Clase 1 y obliga a recalcular la estimación (RDA-008).

## Para la 02-01

**Qué se hizo:** nada de configuración. Bastó la infraestructura existente:

- **Base de pruebas:** Django crea y destruye `test_<DB_NAME>`. Con `$env:DB_NAME = 'manzagrafica_replica'` la base es **`test_manzagrafica_replica`**, confirmado en la salida de `test -v 2`: `Creating test database for alias 'default' ('test_manzagrafica_replica')` y `Destroying test database ...`. Nunca es `manzagrafica_replica` ni `manzagrafica_local`.
- **Privilegios:** el usuario local ya puede crear y destruir esa base. No se cambiaron `settings.py`, `OPTIONS`, `TEST`, privilegios de MySQL ni `compose.yaml`.

**Qué queda por formalizar en la 02-01:**

1. El nombre de la base de pruebas depende de `DB_NAME`: con `manzagrafica_local` sería `test_manzagrafica_local`. Conviene fijarlo en `DATABASES['default']['TEST']['NAME']` (cambio de configuración, con consulta).
2. El modo estricto de `sql_mode` solo para la base de pruebas (AUD-02-020, opción C). La advertencia `mysql.W002` sigue apareciendo en `test`.
3. Un paquete de pruebas por dominio: mover `pedidos/tests.py`, que hoy tiene 10 pruebas en 4 clases.
4. Las factorías de datos. `RegistroEventoTests.crear_evento` es un ayudante local, no una factoría.
5. El mecanismo de fallos esperados para las pruebas de regresión.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/models.py` | Modelo `RegistroEvento` |
| `pedidos/eventos.py` | Nuevo: retención y purga |
| `pedidos/management/__init__.py`, `pedidos/management/commands/__init__.py` | Nuevos (vacíos) |
| `pedidos/management/commands/purgar_registros.py` | Nueva orden de gestión |
| `pedidos/migrations/0007_registroevento.py` | Nueva migración, Clase 2 (autorizada) |
| `pedidos/tests.py` | 4 pruebas nuevas |
| `_planificacion/00_producto/decisiones.md` | RDA-013; RDA-005 reemplazada en parte |
| `_planificacion/00_producto/auditoria-tecnica.md` | Solución y avance de AUD-01-005 |
| `_planificacion/00_producto/registro-pendientes.md` | Iteración activa, estado, nombres, retención resuelta, historial |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | Estado de la épica: En curso |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-01-modelo-registro.md` | Estado, retención y criterios |
| `_planificacion/10_epicas/epica-02-red-seguridad/definicion-epica-02.md` | Nota para la 02-01 |

## Verificación

Todo en PowerShell 7 con `$env:DB_NAME = 'manzagrafica_replica'`.

- `python manage.py test pedidos`: **10 pruebas, `OK`** (3,8 s), contra `test_manzagrafica_replica`.
- `python manage.py check`: sin problemas.
- `python manage.py makemigrations --check --dry-run`: `No changes detected`.
- `python manage.py migrate pedidos 0007`: `Applying pedidos.0007_registroevento... OK`, 1,25 s; `showmigrations` muestra `[X] 0007_registroevento`.
- `python manage.py purgar_registros`: `Eventos eliminados: 0 (anteriores al 25-10-2025 15:52, hora de Chile; retención de 365 días).`
- La tabla queda con 0 filas en la réplica.
- Pantallas: ninguna tocada.

## Despliegue

- Va en 01-06, junto con 01-02 a 01-05. **Requiere respaldo previo:** la migración 0007 es de Clase 2.
- Después de la migración en producción, conviene correr `purgar_registros` una vez para comprobar que la orden funciona allá (01-06).

## Pendientes

- Revisión del desarrollador. La iteración pasa a `Terminada` cuando se despliegue en 01-06.
