# Bitácora 01-06 · Preparación del despliegue de la observabilidad

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** (de esta bitácora, que cubre solo la etapa de redacción) iteración redactada, sin ejecutar; sin decisiones abiertas (ajuste del 2026-10-25, al final). La ejecución, la evidencia de producción y el contraste de la semana van en `bitacora-01-06-produccion.md`. **Aclaración 2026-10-26:** la iteración ya se ejecutó y desplegó (`v1.1-observabilidad`, 2026-10-25) y sigue En curso hasta la parte D; su estado vigente está en `registro-pendientes.md`.

## Resumen

- **Cierre de la 01-05:** los resultados del desarrollador quedaron integrados en `evidencia-01-05.md`, sección «Respuesta del desarrollador». La 01-05 está `Terminada`. La observación de los 360 px quedó en bitacora-01-05.
- **`iteracion-01-06-despliegue-validacion.md` reescrita:**
  - qué se despliega, iteración por iteración;
  - 14 tareas, entre ellas las que se fueron sumando: `check --deploy` del servidor por el bloque de 02-01, líneas duplicadas, página 500 a 360 px y `django.server`;
  - el error controlado decidido;
  - 12 criterios.
- **`evidencia-01-06.md` nueva**, en cuatro partes:
  - **A**, en el PC: lista de comprobación, respaldo, restauración en la réplica como ensayo de retroceso, migración y reversión de la 0007, y etiqueta;
  - **B**, en el servidor: prueba de que la 0007 no estaba aplicada, `checkout`, migración, `check --deploy` antes y después, y recarga;
  - **C**, validación: error controlado, diagnóstico, duplicados, `fontTools`, `django.server`, admin y purga;
  - **D**, la semana.
- No se escribió código ni se cambió configuración. No se ejecutó nada contra Django ni contra git en esta etapa.

## Decisión del desarrollador: error controlado (2026-10-25)

- **Método:** abrir la página de eliminar un pago, `/pagos/eliminar/<id>/` (AUD-02-002). Solo se abre, nunca se confirma.
- **Por qué no escribe nada:** con GET, `eliminar_pago` solo intenta mostrar `pedidos/pago_confirm_delete.html`, que no existe. El decorador registra la traza y responde 500. El evento `pago_eliminado` solo se registra con POST (01-04), así que tampoco crea un evento.
- **`id`:** el `1056` (caso real del 2026-10-22) si existe; si no, el último pago. El comando que lo decide está en B5.
- **Confirmación previa de que el caso sigue:**
  - en el PC, la prueba `test_regresion_eliminar_pago_deja_tipo_y_traza` en la lista de comprobación (A1);
  - en el servidor, después del `checkout`, que la plantilla no exista y que el pago exista (B5). Si la plantilla existiera, se detiene el despliegue de la validación.
- Cierra el `PENDIENTE_DESARROLLADOR` «Método para provocar el error controlado en producción» en la iteración y en la sección 3 del registro.

## SQL de la migración 0007 y su clase

SQL de `python manage.py sqlmigrate pedidos 0007`, registrado en [bitacora-01-01](bitacora-01-01.md) el 2026-10-25:

```sql
--
-- Create model RegistroEvento
--
CREATE TABLE `pedidos_registroevento` (`id` bigint AUTO_INCREMENT NOT NULL PRIMARY KEY, `momento` datetime(6) NOT NULL, `tipo` varchar(40) NOT NULL, `entidad` varchar(30) NOT NULL, `entidad_id` integer UNSIGNED NULL CHECK (`entidad_id` >= 0), `resumen` varchar(255) NOT NULL, `usuario_id` integer NULL);
ALTER TABLE `pedidos_registroevento` ADD CONSTRAINT `pedidos_registroevento_usuario_id_b991a708_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`);
CREATE INDEX `evento_momento_idx` ON `pedidos_registroevento` (`momento`);
CREATE INDEX `evento_tipo_momento_idx` ON `pedidos_registroevento` (`tipo`, `momento`);
```

**El `ALTER TABLE` sigue siendo Clase 2.** El `ALTER` modifica solo `pedidos_registroevento`, la tabla que crea la sentencia anterior y que en ese momento está vacía: le agrega la clave foránea hacia `auth_user`. `auth_user` no se altera (solo queda referenciada) y ninguna tabla existente cambia de columnas, tipos ni obligatoriedad. Es la forma estándar en que Django crea en MySQL una clave foránea al crear una tabla. El desarrollador la aprobó como Clase 2 en 01-01.

- **Por qué el SQL es el de 01-01:** en esta etapa no se ejecutaron comandos (la consulta de `sqlmigrate` y la de git no se aprobaron durante la redacción). Desde 01-01 no se tocó `pedidos/migrations/` en ninguna iteración (01-02 a 01-05 terminaron con `makemigrations --check` en `No changes detected` y sin migraciones).
- **Control en la ejecución:** el punto 4 de la lista de comprobación (A1) vuelve a ejecutar `sqlmigrate pedidos 0007` y exige que coincida con este SQL; si difiere, el despliegue se detiene.

## Tareas que se fueron sumando, incorporadas

| Tarea en la 01-06 | Origen |
| :---------------- | :----- |
| 5 · `check --deploy` del servidor antes y después del `checkout` (bloque 3 de `settings.py`) | Cierre de 02-01 |
| 6 · Sin líneas duplicadas ni formato antiguo en `error.log` | Hipótesis del manejador de PythonAnywhere (01-02) |
| 7 · Página 500 en escritorio y a 360 px | Trasladada desde 01-03 |
| 11 · `django.server` solo existe en `runserver` (0 líneas en `error.log`) | Hallazgo de 01-02 y 01-05 |
| 13 · `pedidos_registroevento` en `TABLAS_ESPERADAS` de `verificar_respaldo.py` después de migrar | Detectado en esta redacción (ver abajo) |
| 4 · Prueba de que la 0007 no se aplicó antes de tiempo | Pedido del desarrollador |
| 3 · Restauración del respaldo en la réplica como ensayo de retroceso, más migración y reversión de la 0007 | Pedido del desarrollador |
| 12 · Una semana de crecimiento contra la estimación de 01-01 | Criterio de término de la épica |

## Hallazgo de la redacción: `verificar_respaldo.py` y la tabla nueva

- `scripts/verificar_respaldo.py` exige las 18 tablas actuales. Una tabla adicional solo genera un aviso («Tablas adicionales (aviso, no invalida)»), sin invalidar el volcado.
- **Antes del despliegue**, el respaldo previo tiene 18 tablas y pasa, como debe.
- **Después**, los volcados tendrán 19 tablas y seguirán pasando, con el aviso. Pero un volcado al que le faltara `pedidos_registroevento` también pasaría.
- **Propuesta:** agregar la tabla a la lista justo después de confirmar la migración en producción (tarea 13). No antes, porque el respaldo previo fallaría. Cuándo hacerlo queda como decisión abierta.

## Decisiones abiertas (`PENDIENTE_DESARROLLADOR`)

1. **Ventana del despliegue** (día y hora en Chile). La etiqueta se crea ese día, con el mensaje calculado con la fecha real.
2. **Cuándo actualizar `verificar_respaldo.py`:** en esta iteración, tras migrar (propuesta), o en 06-03.

Ambas quedaron registradas en `registro-pendientes.md`, sección 3.

## Observaciones

- **Comandos de la evidencia:**
  - Los de PowerShell reutilizan formas ya probadas: `Select-Object -Last 1`, la restauración con `cmd /c` de `replica-local.md` y `curl.exe` en lugar de `-MaximumRedirection 0`.
  - De los de Bash, el bloque de B1 y el método `zcat -f` vienen de 00-05 y 00-06.
  - Los filtros nuevos de `error.log` (`awk 'substr($0,1,19) >= d'`) suponen que cada línea empieza con la fecha `AAAA-MM-DD HH:MM:SS` que antepone PythonAnywhere (observado en la Épica 00). **No se pudieron probar contra un `error.log` real.** Si no devuelven nada, la evidencia pide pegar 2 líneas recientes para ajustarlos.
- **La tabla de despliegues** de `docs/operacion/despliegue.md`, sección 5, no tiene la fila de `v0.2-correcciones` (2026-10-23 18:35). La tarea 14 pide agregarla junto con la nueva.
- **La restauración de la réplica (A3) borra los 8 eventos** de la revisión de 01-05. Es esperado: quedan descritos en `evidencia-01-05.md`.
- **El `print` del bloque de la parte D** está dentro de una consulta en la consola del servidor, no en código de la aplicación (regla 8).

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-01-observabilidad/evidencia-01-05.md` | Resultados del desarrollador integrados |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-05-admin-registros.md` | Terminada; criterio de la revisión manual marcado |
| `_planificacion/99_bitacora/epica-01-observabilidad/bitacora-01-05.md` | Estado final, revisión manual y observación de los 360 px |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-06-despliegue-validacion.md` | Reescrita |
| `_planificacion/10_epicas/epica-01-observabilidad/evidencia-01-06.md` | Nuevo |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | Estados y decisión del error controlado |
| `_planificacion/00_producto/registro-pendientes.md` | Cierre de 01-05, decisión cerrada, 2 abiertas e historial |

## Pendientes

- Revisión del desarrollador y respuesta a las 2 decisiones abiertas.
- Ejecutar la 01-06 cuando el desarrollador lo indique.

## Ajuste tras la 01-07 y decisiones del despliegue (2026-10-25)

- **Decisiones del desarrollador**, cerradas en la iteración y en la sección 3 del registro:
  1. **Ventana:** hoy, domingo 2026-10-25. El negocio cierra el sábado en la tarde y no hay uso hasta el lunes.
  2. **`verificar_respaldo.py`:** `pedidos_registroevento` se agrega en la 01-06, **justo después de migrar** (tarea 13, parte B8 de la evidencia), con prueba en volcados sintéticos con la tabla (código 0) y sin ella (código 1). El respaldo previo real dará código 1 con el script nuevo, lo que confirma que es anterior al despliegue.
- **`respaldo.md` y `bitacora-00-02`:** no se tocaron ahora. `respaldo.md` (sección 3, «18 tablas») se actualiza en B8, cuando cambie el script, con una nota para verificar los volcados anteriores con la versión de `v0.2-correcciones`. `bitacora-00-02` es histórica: no se reescribe.
- **Dependencia de la 01-07:** la 01-07 quedó cerrada por el desarrollador, y la 01-06 depende de ella y despliega su formato.
- **Filtros de las partes C y D:** buscan `nivel=…` dentro de la línea (fecha de PythonAnywhere, emoji y después `nivel=`) y nunca asumen que la línea empieza con el texto del nivel. Se revisaron todos los `grep` y `awk` de la evidencia.
- **Parte C3:** suma la comprobación de los emojis en el `error.log` real (las 2 líneas del error con `❌`, ninguna línea con `nivel=` sin emoji) y la ausencia de `Logging error` y `UnicodeEncodeError`. La iteración suma el criterio correspondiente.
- **Parte A:** las pruebas se **contaron** (79 métodos `test_` en `pedidos/tests/`, con `Grep`, sin ejecutar), y coinciden con la última ejecución de la 01-07. La etiqueta se crea solo con `git status` vacío, `main` sin `ahead` ni `behind` respecto de `origin/main` y el mismo hash en `HEAD` y `origin/main`. Su mensaje menciona la 01-07.
- **Parte D:** suma la verificación del respaldo semanal con el script nuevo (19 de 19).
