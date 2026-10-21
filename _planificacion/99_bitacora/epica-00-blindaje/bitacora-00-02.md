# Bitácora 00-02 · Protocolo de respaldo verificado

- **Fecha:** 2026-10-20
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión (falta responder `evidencia-00-02.md`)

## Resumen

Se creó `scripts/verificar_respaldo.py`, que usa solo la biblioteca estándar. Revisa el tamaño, la línea de cierre, las 18 tablas esperadas y el SHA-256 sin mostrar contenido del volcado. Se probó con tres volcados sintéticos (códigos 0, 1 y 1). Se escribió `docs/operacion/respaldo.md` con comandos de PowerShell y se preparó `evidencia-00-02.md` para el respaldo real del 2026-10-20. Se registró la decisión de retener 5 volcados en el servidor y se resolvió el último `PENDIENTE_DESARROLLADOR` de la 00-01 (expiración). No se tocó código de la aplicación, esquema ni plantillas.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `scripts/verificar_respaldo.py` | Nuevo. Verificador de volcados, solo biblioteca estándar. |
| `docs/operacion/respaldo.md` | Nuevo. Rotación, generación, descarga, verificación, almacenamiento, cadencia, retención, qué hacer si falla y registro de respaldos. |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-02.md` | Nuevo. Cuatro pedidos al desarrollador. |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-02-respaldo-verificado.md` | Estado «En revisión»; decisión de 5 volcados en la tarea 3.5 y ajuste del último criterio, sin borrar el texto original. |
| `_planificacion/00_producto/linea-base-produccion.md` | Expiración del 2026-11-20 confirmada como resultado de la renovación del 2026-10-20. |
| `_planificacion/00_producto/registro-pendientes.md` | Estado de 00-02, decisiones resueltas y nuevas, pendiente asociado a 04-01 e historial. |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-02.md` | Esta bitácora. |

## Verificación

- **Tablas esperadas deducidas de las migraciones:** `pedidos` tiene 8 `CreateModel` (Cliente, Producto, Cotizacion, Pedido, ItemPedido en `0001`; ItemCotizacion en `0002`; HistorialBD en `0004`; Pago en `0005`), sin `ManyToManyField`, `db_table`, `DeleteModel` ni `RenameModel`. Las aplicaciones instaladas aportan 9 tablas (admin 1, auth 6, contenttypes 1, sessions 1); `widget_tweaks` no tiene modelos. Con `django_migrations` suman 18, las mismas 18 que dio el desarrollador y que mide la línea base. Sin diferencias.
- **Volcados sintéticos**, fabricados por `fabricar_volcados.py` en el scratchpad de la sesión, fuera del repositorio. Cada tabla tiene 1.499 filas de relleno con la marca `CONTENIDO_SINTETICO_NO_DEBE_APARECER`; no hay ningún dato real.
  - `integro.sql`, 1.390.224 bytes:

    ```text
    Informe de verificación de respaldo
    Archivo: integro.sql
    Tamaño: 1.390.224 bytes (mínimo 500.000): OK
    Línea de cierre «-- Dump completed»: presente
    Sentencias CREATE TABLE: 18
    Tablas esperadas encontradas: 18 de 18
    Tablas faltantes: ninguna
    Tablas adicionales (aviso, no invalida): ninguna
    SHA-256: 8b7902b266d5ff73dc0a66d97d61bd740461ed92d225383ff14bfc864e11ba52
    Resultado: VÁLIDO
    codigo=0
    ```

  - `truncado.sql`: el íntegro cortado a la mitad, 695.112 bytes. Supera el mínimo, así que falla por la falta de cierre y no por el tamaño:

    ```text
    Informe de verificación de respaldo
    Archivo: truncado.sql
    Tamaño: 695.112 bytes (mínimo 500.000): OK
    Línea de cierre «-- Dump completed»: AUSENTE
    Sentencias CREATE TABLE: 9
    Tablas esperadas encontradas: 9 de 18
    Tablas faltantes: django_session, pedidos_cliente, pedidos_cotizacion, pedidos_historialbd, pedidos_itemcotizacion, pedidos_itempedido, pedidos_pago, pedidos_pedido, pedidos_producto
    Tablas adicionales (aviso, no invalida): ninguna
    SHA-256: 4462542bed0aa308431512d194e5b617180380cccf83ace37873586a5743db2e
    Resultado: NO VÁLIDO (sin línea de cierre; 9 tabla(s) faltante(s))
    codigo=1
    ```

  - `tabla_faltante.sql`: sin `pedidos_pago` y con línea de cierre, 1.313.022 bytes:

    ```text
    Informe de verificación de respaldo
    Archivo: tabla_faltante.sql
    Tamaño: 1.313.022 bytes (mínimo 500.000): OK
    Línea de cierre «-- Dump completed»: presente
    Sentencias CREATE TABLE: 17
    Tablas esperadas encontradas: 17 de 18
    Tablas faltantes: pedidos_pago
    Tablas adicionales (aviso, no invalida): ninguna
    SHA-256: aedab15f67280e55c8b1e4cf80893005cb0fe68ac35f221ea64ce3e8b9e9d44e
    Resultado: NO VÁLIDO (1 tabla(s) faltante(s))
    codigo=1
    ```

- **El informe no muestra contenido:** `grep -c` de `CONTENIDO_SINTETICO`, `INSERT`, `LOCK TABLES` y `ENGINE=` en las tres salidas da 0, 0 y 0.
- **Pruebas adicionales:**
  - Archivo inexistente: «NO VÁLIDO», código 1.
  - `--min-bytes 5000000` sobre el íntegro: «NO VÁLIDO (tamaño bajo el mínimo)».
  - Con bloques de lectura de 97 bytes, para forzar que un `CREATE TABLE` quede partido entre dos bloques: 18 tablas y 18 sentencias, sin perder ni repetir ninguna.
- **PowerShell:** `Get-FileHash -Algorithm SHA256` del íntegro da el mismo hash que el script. `$LASTEXITCODE` vale 0 y las tildes del informe se ven bien en la consola.
- **Pruebas de la aplicación:** `python manage.py test pedidos` no se ejecutó. No se modificó código de la aplicación.
- **Revisión de pantallas:** no aplica, no se tocaron plantillas.

## Migraciones

- Ninguna. Cambio de esquema: Ninguno.

## Criterios de aceptación

- [x] Códigos 0, 1 y 1 para el íntegro, el truncado y el que tiene una tabla faltante (salidas arriba).
- [x] El informe no contiene ninguna línea del volcado: la marca sintética y las palabras clave de SQL dan 0 coincidencias en las tres salidas. El script solo imprime el nombre del archivo, sin la ruta, nombres de tabla que sean identificadores simples (`[A-Za-z0-9_$]`), conteos y el hash.
- [x] `docs/operacion/respaldo.md` cubre la generación (sección 2), la descarga (2), la verificación (3), qué hacer si falla (3), el almacenamiento (4), la cadencia y la retención (5) y el registro (6).
- [ ] Informe de un respaldo real con código 0 y su hash: pendiente de `evidencia-00-02.md`, punto 1.
- [ ] Carpeta cifrada fuera del repositorio: pendiente de `evidencia-00-02.md`, punto 2.
- [ ] `backups/` con a lo más 5 volcados: pendiente de `evidencia-00-02.md`, punto 3. La línea base del 2026-10-20 ya informaba 5.

## Decisiones tomadas

- **Retención en el servidor: 5 volcados**, por decisión del desarrollador del 2026-10-20. Reemplaza el «dos o tres» de la iteración, que se conserva en el texto. El último criterio se ajustó a 5 y no hay que borrar nada a mano.
  - La definición de la épica 00 («se reduce a mano en el servidor») y la acción recomendada de AUD-01-014 («retención de dos o tres en servidor») quedan desactualizadas. No se editaron: la auditoría no se reescribe, y el desarrollador decide si cambia la épica. AUD-01-014 sigue abierto para 06-03.
- **Retención local:** queda como propuesta (`PENDIENTE_DESARROLLADOR`): los 4 volcados semanales más recientes y el previo a cada despliegue, hasta que se cierre la fase siguiente.
- **Carpeta de respaldos:** en los documentos se llama «la carpeta de respaldos definida por el desarrollador»; su ruta no se escribe en el repositorio.
- **Hora del nombre del volcado.** Al planificar, el agente afirmó que `datetime.now()` entregaba la hora UTC. Era incorrecto: `TIME_ZONE = 'America/Santiago'` (`settings.py:148`) fija la zona horaria del proceso. El desarrollador lo corrigió con dos volcados de producción, que tienen 3 y 4 horas de diferencia con la hora UTC del servidor. Así quedó documentado en el procedimiento.
- **El enlace GET de «Generar Nuevo Respaldo BD»** ya está cubierto por **AUD-02-006** (04-01), así que no se creó un hallazgo nuevo. Se advirtió en el procedimiento y se agregó al registro como pendiente asociado a 04-01.
- **Tablas adicionales y repetidas** se informan como aviso y no invalidan el volcado: la iteración pide comparar contra las esperadas, y una tabla extra no indica un volcado roto.
- **Hueco de 120 días:** el mayor medido es de 119 días (2026-06-23 a 2026-10-20 en UTC). El procedimiento dice «hasta 120 días» y da la cifra exacta.

## Pendientes y riesgos

- Responder `evidencia-00-02.md` y consolidar en `bitacora-00-02-produccion.md`.
- Si el volcado real no trae `-- Dump completed`, el script lo da por no válido. El criterio no se relaja sin una decisión del desarrollador.
- Si una migración futura agrega una tabla, hay que actualizar `TABLAS_ESPERADAS` en el script en esa misma iteración. Si no, el volcado se informa con una tabla adicional, pero sigue siendo válido.

## Commit sugerido

`Épica 0 - Iteración 00-02: agrega verificar_respaldo.py, el procedimiento de respaldo y el pedido de evidencia; fija la retención en 5 volcados`
