# Bitácora 00-05 · Despliegue de 00-04 como `v0.1-higiene` y cierre

- **Fecha:** 2026-10-23
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada

## Resumen

- El desarrollador desplegó la 00-04 como `v0.1-higiene` siguiendo la parte B de `evidencia-00-05.md`, entre el 2026-10-22 a las 23:56 y el 2026-10-23 a las 00:30 (hora de Chile). La recarga fue a las 00:26 y no hubo retroceso.
- El agente revisó las salidas y aprueba la parte B.
- **Con esto se cierra la 00-05** y también el último criterio de la 00-04. La iteración activa pasa a ser la 00-06.
- Se registra AUD-02-023 (las imágenes de `media/` no tienen ninguna copia) y se anotan dos pistas para la épica 01.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `docs/operacion/despliegue.md` | Fila del despliegue en la sección 5. |
| `docs/operacion/respaldo.md` | Fila del respaldo previo en la sección 6. |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-05.md` | Las dos líneas «Revisión del agente» de la parte B. Las respuestas del desarrollador no se tocaron. |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-05-protocolo-despliegue.md` | Estado Terminada y último criterio marcado. |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-04-higiene-repositorio.md` | Criterio «responde 200» marcado, con la fecha del despliegue. |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-02-022 resuelto, AUD-02-023 nuevo y notas de la 00-05 con la propuesta. |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | Nueva sección «Pistas registradas para la épica». |
| `_planificacion/00_producto/registro-pendientes.md` | Estados, iteración activa, decisiones e historial. |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-05-produccion.md` | Esta bitácora. |

## Verificación (salidas del desarrollador en `evidencia-00-05.md`, parte B)

| Punto | Resultado |
| :---- | :-------- |
| Respaldo previo (B1) | `respaldo_22-10-2026_23-56-36.sql`, 1.444.819 bytes, 18 de 18 tablas, línea de cierre presente, código 0 |
| Lista de comprobación (B2) | 8 de 8 puntos, más la etiqueta de partida. `check --deploy` muestra solo las 5 advertencias conocidas y `makemigrations` da `No changes detected` |
| Etiquetas (B3 y B5) | `v0.1-higiene` (`64655f8`) y `v0.0-inicial` (`2442f3b`) publicadas. `v0.0-inicial` se publicó antes del `checkout` del servidor. `fase0-linea-base-2026-10-20` apunta al mismo commit y se deja como está (decisión del desarrollador) |
| Servidor antes (B4) | Sin líneas ` M` (solo `??` de `media/` y `staticfiles/`), commit `2442f3b`, migraciones `0001` a `0006` |
| `media/` y captura (B6) | 11 archivos en `media/`, 9 en `media/pedidos/`. `captura: 0`, así que ningún pedido usa la imagen que borra el `checkout`. 7 pedidos apuntan a `pedidos/` |
| `.env` (B7) | `DATABASE_URL`: 1 línea. Se agregó `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com` antes de recargar |
| `checkout` (B8) | `v0.1-higiene`, `git status` vacío y la captura eliminada como se previó. `check` limpio y `No planned migration operations.` |
| Después de recargar (B10) | Inicio de sesión, panel, listado y detalle de pedido (uno con imagen de referencia) correctos. Ninguna línea en el registro de errores después de las 03:26 UTC |

## Migraciones

- Ninguna.

## Criterios de aceptación de la 00-05

- [x] `despliegue.md` con la convención, la lista y los pasos (bitácora 00-05).
- [x] `retroceso.md` con los tres casos (bitácora 00-05).
- [x] Ensayo en menos de 15 minutos con `showmigrations` igual antes y después: 1,31 minutos (bitácora 00-05-ensayo).
- [x] Migración temporal ausente de `git status` y de `pedidos/migrations/` (bitácora 00-05-ensayo).
- [x] Etiqueta del despliegue de 00-04 en `git tag -n` y lista completada: B3, B5 y B2.

**Criterio de la 00-04 «el sitio publicado responde 200»:** cumplido; las tres pantallas cargaron con `v0.1-higiene`.

## Decisiones tomadas

- **El servidor queda en `detached HEAD`** sobre `v0.1-higiene`, como prevé el protocolo. Los próximos despliegues usan `git fetch origin --tags` y `git checkout <etiqueta>`, nunca `git pull`. El paso 3.2 de `despliegue.md` ya lo dice así.
- **El mensaje de `v0.1-higiene` dice 2026-10-22**, pero la recarga fue el 2026-10-23 a las 00:26. Una etiqueta publicada no se reescribe: la fecha real queda en el registro de despliegues y en la evidencia.
- **AUD-02-022 queda resuelto** con el despliegue (`ALLOWED_HOSTS` definida y sitio correcto).
- **AUD-02-023, severidad Media** (asignada por el desarrollador): la propuesta para la épica 07 está en las notas de la 00-05 de `auditoria-tecnica.md`. No se implementa ahora.

## Pendientes y riesgos

- **AUD-02-023:**
  - Hasta que exista un respaldo de `media/`, la protección es manual: descargar las imágenes nuevas a la carpeta cifrada.
  - Restaurar un respaldo de la base (caso 3) no recupera las imágenes.
  - El desarrollador define qué iteración de la épica 07 lo implementa.
- **Pistas para la épica 01**, anotadas en `definicion-epica-01.md`:
  - El `OSError: write error` de las 02:56:38 UTC ocurrió 2 segundos después de generar el respaldo, lo que apunta a que los cortes de conexión podrían estar relacionados con la descarga de respaldos. Es una hipótesis.
  - Los mensajes de `fontTools` llenan el registro de errores.
- **El retroceso real en producción no se ha medido:** el ensayo cubrió solo la réplica.

## Commit sugerido

`Épica 0 - Iteración 00-05: cierra la iteración con v0.1-higiene desplegada sin retroceso, registra AUD-02-023 (media/ sin copia) y pistas para la épica 01`
