# Bitácora 04-cierre-epica · Cierre de la Épica 04 · Seguridad y endurecimiento

- **Fecha:** 2026-11-27
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada (cierre documental; criterio de término marcado con su evidencia, una casilla sin marcar por no constar en producción)

## Resumen

La Épica 04 se cierra por decisión del desarrollador del 2026-11-27. Las diez iteraciones (04-01 a 04-10) están Terminadas y verificadas en producción, de `v4.1-mutaciones-post` (2026-11-18) a `v4.11-csp-observacion` (2026-11-27), que es la versión estable vigente y el destino de retroceso del despliegue siguiente (la 14-04).

Antes de cerrar se comprobó en los documentos que la 04-09 está Terminada · verificada en producción el 2026-11-27 (iteración, bitácora, registro y `despliegue.md`, sección 5).

Este cierre solo cambia archivos `.md`. No hay código, pruebas, commit, etiqueta ni despliegue.

## Archivos creados o modificados

| Archivo | Cambio |
| :-- | :-- |
| `_planificacion/10_epicas/epica-04-seguridad/definicion-epica-04.md` | Estado «Terminada (2026-11-27)», fila de la 04-09, criterio de término marcado con su fuente, «Resumen de cierre», «Resultados de la épica», «Siguiente: revisión final» tachado (2 lugares) y nota de los hallazgos revisados |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-02-010 y AUD-04-002, cerrados por decisión; destino de AUD-05-025 a 030; notas del cierre de la épica |
| `_planificacion/00_producto/registro-pendientes.md` | Épica 04 Terminada; épicas terminadas 00 a 04; próximo hito; historial |
| `_planificacion/99_bitacora/epica-04-seguridad/bitacora-04-cierre-epica.md` | Esta bitácora |

## Verificación

- **Estado de las diez iteraciones:** en la tabla de la definición y en el registro, sección 1, todas Terminadas o «Completadas y verificadas en producción» (04-02 a 04-06, el nombre de entonces).
- **Etiquetas y fechas:** `despliegue.md`, sección 5. Once despliegues de la épica (la 04-02 tuvo dos escalones).
- **Pruebas finales (local, antes de la 04-09):** 461, `OK (expected failures=3)`: R8, R9 y R15.
- **Notas «documentado»:** `docs/operacion/riesgos-aceptados.md` (AUD-04-003, AUD-02-030, eliminar cotización sin evento) y `docs/operacion/respaldo.md`, sección 7 (AUD-02-023).
- **Enlaces:** los nuevos apuntan a archivos que existen (`definicion-epica-04.md`, `bitacora-04-cierre-epica.md`, `bitacora-04-09.md`, `bitacora-04-01.md`, `riesgos-aceptados.md`, `respaldo.md`).
- **Fin de línea:** `registro-pendientes.md` con CRLF en todas las líneas; `definicion-epica-04.md` y `auditoria-tecnica.md` siguen en LF.

## Migraciones

- Ninguna en este cierre. En la épica: `0008` (04-06) y `0009_acceso_bloqueado` (04-08), ambas Clase 1.

## Criterios de aceptación

| Criterio | Estado | Fuente |
| :-- | :-- | :-- |
| `check --deploy` solo W005 y W021 | Cumplido | Documentos (consola en cada despliegue) |
| R6a-c, R7, R19 y R14 a verde | Cumplido | Documentos |
| Ningún proceso muestra la contraseña | **Sin marcar** | Réplica: documentos; producción: no consta |
| Respaldo desde la web se descarga | Cumplido | Dicho (2026-11-18) |
| `<script>` guardado no se ejecuta | Cumplido | Prueba automatizada |
| Bloqueo tras N intentos con evento | Cumplido | Pruebas y pantalla (2026-11-21) |
| Imagen de más de 5 MB y cuerpo grande rechazados | Cumplido | Pruebas; imagen en producción, dicho |
| Restauración endurecida | Cumplido | Pruebas y ensayo; `vacio.sql` en producción, dicho |
| 04-05 sin cambios visibles | Cumplido | Suite; revisión manual dicha |
| Política de contenido en observación en producción | Cumplido | Captura (2026-11-27) |
| Pedido con pagos con confirmación y evento | Cumplido | Pruebas; día 0 dicho |
| Decisiones escritas en `docs/operacion/` | Cumplido | Documentos |

## Decisiones tomadas

- **Cierre de la épica** (desarrollador, 2026-11-27).
- **AUD-02-010 y AUD-04-002:** cerrados por decisión, sin acción nueva (desarrollador, 2026-11-27, dicho).
- **Destinos:** AUD-03-005 (08-07 y 08-08); AUD-05-004 y la página de error de CSRF (Épica 08); AUD-02-020 (Épica 06); AUD-02-023 y AUD-02-024 (Épica 14); AUD-05-025, 027, 028, 029 y 030 (Épica 14, agrupados por tema, 2026-11-27); AUD-05-026 Media (propuesta), pendiente de comprobación en la réplica; si la fecha se pierde al guardar, pasa a Crítica (RDA-022).
- **Política de contenido:** queda en observación; la endurece la 08-08.
- **Orden siguiente:** la 14-04, excepcional, antes de la Épica 05 (desarrollador, 2026-11-27, dicho; sin RDA), con retroceso a `v4.11-csp-observacion`.

## Pendientes y riesgos

| Pendiente | Fecha o destino |
| :-- | :-- |
| Renovar la web app de PythonAnywhere | Antes del 2026-12-13 |
| D5 de la 04-03 | `PENDIENTE_DESARROLLADOR` |
| AUD-01-016, punto 3 (observación tras una hibernación) | Abierto |
| AUD-04-004 (desconexiones registradas como error) | Abierto |
| Copia de las imágenes de los pedidos 46 y 56 | No consta (04-07, 2026-11-20) |
| Protección de `media/` (sin copia automática) | Épica 14 (AUD-02-023) |
| Restauración real en producción | Nunca probada (por diseño; la cubre el ensayo en la réplica) |
| AUD-05-026 | Comprobar en la réplica |

**Riesgos:**

- La contraseña fuera de los argumentos de los procesos solo está verificada en la réplica.
- La política de contenido no bloquea nada: la defensa contra el HTML peligroso sigue siendo la sanitización de la 04-07.
- El HSTS de una semana ya se emitió: un retroceso a antes de `v4.3-configuracion-produccion` no lo borra de los navegadores durante 7 días.

## Qué no se pudo verificar

- **Producción:** nada lo vio el agente. Todo sale de las bitácoras, de `despliegue.md` y de lo dicho por el desarrollador.
- **Commit de `v4.1-mutaciones-post`:** no se informó.
- **`Strict-Transport-Security` y `X-Frame-Options` en producción después de la 04-09:** no constan.

## Commit sugerido

`Épica 4 - cierre documental: Épica 04 Terminada, criterio marcado con evidencia, resumen y resultados; destinos de hallazgos y próximo hito 14-04`
