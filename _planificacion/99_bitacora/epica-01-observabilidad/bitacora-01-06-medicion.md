# Bitácora 01-06 · Medición de la parte D y cierre

- **Fecha:** 2026-11-03
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión → Terminada (2026-11-03, por instrucción expresa del desarrollador; ver «Decisiones tomadas»)

Es la bitácora nueva que pide la regla 5.4 de `_planificacion/README.md`: [bitacora-01-06-produccion](bitacora-01-06-produccion.md) ya está entregada y no se edita. Solo se citan conteos, horas, tamaños y códigos; ningún dato de clientes.

## Resumen

La parte D de la 01-06 se ejecutó el **2026-11-03 a las 22:37:58 (hora de Chile)**, y no el domingo 2026-11-01 previsto, con producción todavía en `v1.1-observabilidad`. Midió 172 eventos de negocio desde el reinicio del 2026-10-25 21:26:25, en una ventana de 9,0497 días (no de 7). El ritmo real es el **47,5 %** de la estimación de la 01-01 (19,0 filas por día frente a ~40), así que **no hace falta ajustar el inventario**. `fontTools` quedó en 0 y las 10 líneas de `server.log` desde la recarga están clasificadas: 3 explicadas y 7 con `registrador=root` por clasificar. Con esto, los 13 criterios de la 01-06 están marcados y la iteración queda terminada. La parte A de la 01-09 (respaldo previo) se ejecutó el mismo día, 3 minutos y 49 segundos antes.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-01-observabilidad/evidencia-01-06.md` | Tabla de la parte D completa, nota fechada 2026-11-03 y respuesta del desarrollador. No se tocó el plan ni el orden |
| `_planificacion/10_epicas/epica-01-observabilidad/evidencia-01-09.md` | Tabla de la parte A completa y nota fechada 2026-11-03. No se tocó el plan ni el orden |
| `docs/operacion/respaldo.md` | Sección 6: fila del respaldo del 2026-11-03 22:34:09 |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-06-despliegue-validacion.md` | Criterio de la semana marcado (13 de 13); estado `En revisión` → `Terminada` |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | Fila de la 01-06 en la tabla de iteraciones |
| `_planificacion/00_producto/auditoria-tecnica.md` | Estado de AUD-01-004 y AUD-01-005 |
| `_planificacion/00_producto/registro-pendientes.md` | Iteración activa, próximo hito, fila de la 01-06, propuesta de la sección 4 e historial |
| `_planificacion/99_bitacora/epica-01-observabilidad/bitacora-01-06-medicion.md` | Esta bitácora |

Sin cambios de código, de pruebas, de `docs/operacion/despliegue.md` ni de documentos protegidos.

## Datos de la parte D (medición en producción, 2026-11-03)

Fuente: [evidencia-01-06](../../10_epicas/epica-01-observabilidad/evidencia-01-06.md), parte D. Los entregó el desarrollador; el agente no tiene acceso a producción.

| Dato | Valor |
| :--- | :---- |
| Hora de la medición | 2026-11-03 22:37:58 (Chile); el servidor imprimió `2026-11-04 01:37:58`, que es UTC |
| Filas totales | 172 |
| Por tipo | `acceso_exitoso` 3, `acceso_fallido` 1, `pago_registrado` 25, `pedido_creado` 35, `pedido_eliminado` 1, `pedido_estado_cambiado` 103, `pedido_modificado` 3, `respaldo_generado` 1 |
| Por día (Chile) | 10-25: 2; 10-26: 18; 10-27: 22; 10-28: 9; 10-29: 16; 10-30: 10; 10-31: 64; 11-01: 2; 11-02: 7; 11-03: 22 |
| `information_schema` | `table_rows` 103, `data_length` 16.384, `index_length` 49.152 |
| Resumen promedio | 35,8372 caracteres |
| `server.log` desde la recarga | `ERROR` 9, `INFO` 1; registradores: `django.request` 1, `pedidos.decorators` 1, `pedidos.utils` 1, `root` 7 |
| `fontTools` | 0 en `error.log` y 0 en `server.log` |
| Panel | Disco 183,2 MB (36 %) de 512 MB; CPU 2,37 s de 100 s (2 %) |

**Verificación de las sumas** (hecha por el agente): por tipo, 3 + 1 + 25 + 35 + 1 + 103 + 3 + 1 = **172**; por día, 2 + 18 + 22 + 9 + 16 + 10 + 64 + 2 + 7 + 22 = **172**; por registrador, 1 + 1 + 1 + 7 = **10** = 9 `ERROR` + 1 `INFO`. Las tres coinciden con los totales.

## Contraste con la estimación de la 01-01

La estimación ([bitacora-01-01](bitacora-01-01.md), «Estimación de crecimiento»): **~1.135 filas al mes, redondeadas a 1.200** (~40 por día, ~280 en siete días) con el mes de mayor movimiento medido (febrero, 121 pedidos), y **~0,6 MB al mes** con 500 bytes por fila, incluidos los índices.

### 1. Ventana exacta

Desde el reinicio del 2026-10-25 21:26:25 hasta la medición del 2026-11-03 22:37:58: **9 días 1 h 11 min 33 s = 781.893 s = 9,0497 días**.

### 2. Ritmo real y proyección mensual

| Cálculo | Resultado | Estimación | Real / estimación |
| :------ | :-------- | :--------- | :---------------- |
| Filas por día: 172 ÷ 9,0497 | **19,0** | ~40 | 47,5 % |
| Primeros siete días calendario (25 al 31-oct): 2 + 18 + 22 + 9 + 16 + 10 + 64 | **141** | ~280 | 50,4 % |
| Proyección a 30 días: 19,006 × 30 | **~570 filas al mes** (579 con 30,4375 días) | ~1.200 | 47,5 % |
| Sin el evento de respaldo de la parte A: 171 ÷ 9,0497 = 18,90 por día; × 30 | **~567 filas al mes** | ~1.200 | 47,2 % |

- Los «siete días calendario» del 25 al 31 de octubre no son 7 × 24 h: el día 25 cuenta solo desde las 21:26:25. El tramo dura 6 días 2 h 33 min 35 s (6,1067 días), es decir, **23,1 filas por día**; sigue por debajo de las 40.
- La proyección a 30 días extrapola 9 días de datos: es un orden de magnitud, no una predicción.
- El evento de respaldo (1 fila) no cambia la conclusión: 570 frente a 567.

### 3. Por tipo (proyección a 30 días = filas × 30 ÷ 9,0497)

| Tipo (estimación 01-01) | Filas reales | Proyección a 30 días | Estimadas al mes |
| :---------------------- | -----------: | -------------------: | ---------------: |
| Pedido creado | 35 | 116 | 121 |
| Cambio de estado | 103 | 341 | 363 |
| Pago registrado | 25 | 83 | 149 |
| Pedido modificado | 3 | 10 | 242 |
| Accesos exitosos y fallidos | 3 + 1 = 4 | 13 | 180 |
| Pedido duplicado y eliminado | 0 + 1 = 1 | 3 | 24 |
| Respaldo y restauración | 1 | 3 | 11 |
| Pago modificado y eliminado; cotización convertida; cliente o producto eliminado | 0 | 0 | 45 (30 + 15) |
| **Total** | **172** | **570** (la suma de los valores redondeados de la columna da 569) | **1.135** |

- Dos tipos están cerca de lo estimado (pedidos creados y cambios de estado); el resto queda muy por debajo. La diferencia total sale sobre todo de los accesos (13 frente a 180), las modificaciones de pedido (10 frente a 242) y los pagos (83 frente a 149).
- Con 9 días de datos, los tipos con 1 a 3 filas son poco estables: no se les puede sacar una tasa.
- La estimación supuso 5 accesos por día. En B7 y C5 de la evidencia se vio que las sesiones de Django continúan sin registrar un nuevo acceso, pero eso no se midió aquí como causa de la diferencia.

### 4. Peso

| Medida | Resultado |
| :----- | :-------- |
| Con el mismo supuesto de 500 bytes por fila: 570 × 500 B | **0,285 MB al mes** (frente a ~0,6 MB) |
| `information_schema`: 16.384 + 49.152 | **65.536 bytes (64 KiB)** |
| Las 172 filas con el supuesto de 500 B | 86.000 bytes |
| Resumen promedio | 35,8372 caracteres (la estimación supuso ~80 bytes) |
| Disco del panel | 183,2 MB, contra 180,8 MB del 2026-10-20 (+2,4 MB) |

- El peso de `information_schema` es **referencial**: puede tener hasta 24 horas de atraso (`linea-base-produccion.md`, sección 2). Aquí el atraso es visible: `table_rows` dice 103 y la tabla tiene 172 filas.
- Aun así, 65.536 bytes no superan los 86.000 que da la estimación. Con el tamaño de página predeterminado de InnoDB (16 KiB), los valores equivalen a 1 página de datos y 3 de índices; por eso **no se puede deducir un peso por fila** de esta medición. El supuesto de 500 B/fila sigue sin comprobarse y la tabla es demasiado pequeña para hacerlo.
- Los +2,4 MB del panel **no se atribuyen a la tabla**: el disco incluye también el código, los registros y los respaldos del servidor. Con una tabla de 64 KiB, la tabla no puede explicarlos.

### 5. Resultado

**Lo real no supera lo estimado** (47,5 % en filas por día y por mes, 50,4 % en los primeros siete días, peso por debajo del supuesto). **No hace falta ajustar el inventario ni la retención de 365 días.** Cumple el tercer criterio de término de la Épica 01 en lo que mide: «dentro de la estimación de 01-01».

### 6. El día 2026-10-31 (64 filas)

Lo que muestran los datos:

- Es el día con más eventos: 64 de las 172 filas (37,2 %).
- Es 2,9 veces el segundo día más alto (22 filas, el 10-27 y el 11-03) y 5,3 veces el promedio de los otros siete días completos (84 filas ÷ 7 = 12,0 por día: 10-26 a 10-30, 11-01 y 11-02).
- Es el único día que supera las ~40 filas por día de la estimación.
- Los datos entregan el conteo por tipo para toda la ventana y el conteo por día, **pero no el cruce de ambos ni la hora**: no se sabe qué tipos ni a qué hora produjeron las 64 filas.

**No se infiere una causa.** El día 10-31 queda como un dato sin explicar; no cambia el resultado porque un solo día alto no mueve el promedio por debajo de la estimación (172 filas en total, con ese día incluido).

Otro dato del conteo por día: los 2 eventos del 2026-10-25 coinciden en número con los 2 eventos de la prueba de acceso de C5 (acceso fallido a las 22:12:58 y acceso exitoso a las 22:13:10, hora de Chile) y con la tabla vacía de antes de esa prueba (B7, C5). Es una coincidencia con la evidencia ya registrada, no una medición del tipo por día.

## Clasificación de las líneas de `server.log` desde la recarga

Ventana: desde el reinicio del 2026-10-25 21:26:25 (Chile). `server.log` está en hora de Chile.

| # | Hora (Chile) | Nivel | Registrador | Método, ruta y excepción | Clasificación |
| -: | :----------- | :---- | :---------- | :----------------------- | :------------ |
| 1 | 2026-10-25 21:40:36 | `ERROR` | `pedidos.decorators` | `GET /pagos/eliminar/1056/`, `TemplateDoesNotExist` | **Explicada:** el error controlado de la 01-06 (C1 y C2) |
| 2 | 2026-10-25 21:40:36 | `ERROR` | `django.request` | `GET /pagos/eliminar/1056/`, sin excepción | **Explicada:** el mismo error controlado (C2 y C3: eran 2 líneas) |
| 3 | 2026-10-26 12:01:10 | `ERROR` | `root` | sin método, ruta ni excepción | **Por clasificar** |
| 4 | 2026-10-26 16:53:18 | `ERROR` | `root` | ídem | **Por clasificar** |
| 5 | 2026-10-27 14:35:49 | `ERROR` | `root` | ídem | **Por clasificar** (coincidencia horaria, ver abajo) |
| 6 | 2026-10-29 13:46:48 | `ERROR` | `root` | ídem | **Por clasificar** |
| 7 | 2026-10-31 13:08:48 | `ERROR` | `root` | ídem | **Por clasificar** |
| 8 | 2026-11-03 11:22:59 | `ERROR` | `root` | ídem | **Por clasificar** |
| 9 | 2026-11-03 18:58:48 | `ERROR` | `root` | ídem | **Por clasificar** |
| 10 | 2026-11-03 22:34:09 | `INFO` | `pedidos.utils` | sin método, ruta ni excepción | **Explicada:** el respaldo de la parte A de la 01-09 (único clic, 22:34:09) |

- **Las líneas 1 y 2** coinciden con C3 de la evidencia de la 01-06 (2 líneas del error controlado) y son las únicas del 25 de octubre; ninguna otra línea `ERROR` o `WARNING` de esa noche, como ya constaba.
- **La línea 10** coincide con la hora del clic y con la del nombre del archivo `respaldo_03-11-2026_22-34-09.sql` (parte A de la 01-09). Es el `INFO` que escribe `pedidos.utils` al generar el respaldo normal.
- **Las 7 líneas con `registrador=root`** quedan **por clasificar**, sin número de hallazgo y sin proponer causa. Se registran en la sección 4 del registro de pendientes. No forman parte de los criterios de la 01-06.

### Coincidencia horaria (sin conclusión)

La línea 5, **2026-10-27 14:35:49**, cae en el mismo minuto que la recarga manual de la aplicación que el cliente hizo desde el panel de PythonAnywhere ([AUD-04-002](../../00_producto/auditoria-tecnica.md): 14:35 y 14:42 del 2026-10-27).

- **Misma zona horaria, verificada:** la Auditoría 04 declara que sus horas están en hora de Chile y que `server.log` está en hora de Chile; las dos están en la misma zona.
- **Precisión:** la auditoría da la hora de la recarga al minuto, de modo que la coincidencia es al minuto, no al segundo.
- **Para la otra recarga (14:42) no hay ninguna línea `root`** entre las 7.
- No se concluye nada: es una coincidencia de hora entre dos datos.

### Paso opcional: ver el campo `mensaje=` de las 7 líneas (solo lectura)

Para decidir si merecen un hallazgo. **[PA · Bash]**, no modifica nada. **Revisa la salida antes de pegarla en ningún documento ni en el chat:** el campo `mensaje=` es texto libre y podría traer datos de clientes (nombres, teléfonos, montos). Si hay duda, pega solo la hora y el tipo.

```bash
S=/var/log/manzagrafica.pythonanywhere.com.server.log
DESDE_CL="2026-10-25 21:26:25"
zcat -f $S* | awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] / && substr($0,1,19) >= d' | grep 'nivel=ERROR registrador=root' | awk '{ i = index($0, "mensaje="); print substr($0, 1, 19), (i ? substr($0, i, 160) : "(sin campo mensaje=)") }'
```

- **Esperado:** 7 líneas, cada una con su fecha y el comienzo del campo `mensaje=` (160 caracteres como máximo). Si salen otras cantidades, anótalo.
- Usa el mismo método de lectura de la parte D (`zcat -f` incluye los archivos rotados). No imprime la línea completa, así que no muestra la ruta de las trazas ni otros campos.

## Migraciones

- Ninguna. Esta iteración solo toca documentos `.md`.

## Verificación

- Sumas por tipo, por día y por registrador: 172, 172 y 10, iguales a los totales (cálculo del agente).
- Duración de la ventana: 781.893 s = 9,0497 días (cálculo con la biblioteca estándar de Python; coincide con el cálculo a mano de 9 días 1 h 11 min 33 s).
- Proyecciones y porcentajes: calculados con los datos de la tabla; la fórmula está en cada fila.
- Horas de la auditoría y de `server.log`: verificadas en `auditoria-tecnica.md` (alcance de la Auditoría 04).
- Pruebas: no se ejecutaron; no hay cambios de código ni de pruebas.
- Pantallas: no aplica, solo documentos.
- Lo que el agente **no** pudo comprobar: toda la medición viene de producción y se toma de la evidencia tal como la entregó el desarrollador. El contenido de las 7 líneas `root` y la descarga del respaldo (directa o desde Files: «no informado») quedaron sin comprobar.

## Criterios de aceptación

Criterios de la [iteración 01-06](../../10_epicas/epica-01-observabilidad/iteracion-01-06-despliegue-validacion.md):

- [x] 12 de 13 estaban cumplidos desde el 2026-10-25 ([bitacora-01-06-produccion](bitacora-01-06-produccion.md)).
- [x] **El crecimiento de una semana de la tabla de eventos está medido en filas y MB y comparado con la estimación.** Medido el 2026-11-03 en 9,0497 días: 172 filas (19,0 por día; 141 en los primeros siete días calendario) y 65.536 bytes en `information_schema` (referencial); proyección de ~570 filas al mes contra ~1.200 estimadas, sin ajuste del inventario. Cálculo arriba.
- **Total: 13 de 13 criterios marcados.**

## Decisiones tomadas

- **Cierre de la 01-06.** El desarrollador pidió pasar la iteración a `En revisión` y luego a `Terminada` el 2026-11-03, con las dos transiciones en el historial. Es una excepción a `AGENTS.md`, sección 10, paso 8 (que deja la iteración en `En revisión`), hecha por instrucción expresa. No se cierran la 01-07, la 01-08 ni la 01-09 (se cierran después de desplegar `v1.2-capturas`) ni la Épica 01.
- **AUD-01-004 y AUD-01-005 en `auditoria-tecnica.md`.** AUD-01-004 pasa a «confirmado en producción» y AUD-01-005 a `Cerrado`, con la evidencia de la 01-06 (C2, C3, C5 y D). Detalle en la tabla de hallazgos.
- **Sin ajuste del inventario** de eventos ni de la retención de 365 días: la medición queda bajo la estimación.
- **Las 7 líneas `root`** quedan en la sección 4 del registro, por clasificar, sin número AUD y sin causa propuesta (instrucción del desarrollador).
- **Iteración activa del registro:** «desplegar `v1.2-capturas` con las partes B a E de `evidencia-01-09`, y después la 00-07». No se edita `despliegue.md`: su fila se agrega después del despliegue.

## Pendientes y riesgos

- **El peso real por fila sigue sin comprobarse:** la tabla es demasiado pequeña (64 KiB) y `information_schema` va atrasado. El supuesto de 500 B por fila solo se pondrá a prueba con una tabla de más de unas pocas páginas; la revisión periódica de registros (13-03) es un momento natural para repetir la medición.
- **El día 2026-10-31 (64 filas) queda sin explicar.** No hay conteo por tipo y día ni por hora.
- **7 líneas `root` por clasificar** (sección 4 del registro); el paso opcional de arriba da el campo `mensaje=`.
- **La parte D midió 9 días, no 7**, porque se ejecutó el 2026-11-03. No cambia el resultado; las cifras por día lo normalizan.
- **Fechas del 2026-11-01 en otros documentos** (por ejemplo, la fila de la 00-07 del registro y los textos de `evidencia-00-07.md` y de la evidencia 01-09) siguen diciendo «2026-11-01» para el despliegue; hoy ya no es la fecha prevista. No se editaron: el despliegue de `v1.2-capturas` y la 00-07 quedan sin fecha fija hasta que el desarrollador la defina.
- **`docs/operacion/respaldo.md`, sección 3:** el comando de la versión anterior del verificador tiene una ruta dañada (`"$env:TEMPerificar_respaldo_v02.py"`, le falta `\v`). La evidencia 01-06 ya corrigió el mismo error en su B8; el documento de operación no. No se tocó (fuera de esta tarea).

## Commit sugerido

`Épica 1 - Iteración 01-06: mide la semana de eventos (172 filas, 47 % de la estimación), registra el respaldo previo a v1.2 y cierra la iteración y AUD-01-004 y 005.`
