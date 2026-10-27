# Bitácora 02-cierre-carpetas-antiguas · Informe de las carpetas anteriores a RDA-014

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** En revisión (informe de solo lectura; el desarrollador borra las carpetas con `git rm`)

## Resumen

Informe de solo lectura sobre `_planificacion/10_epicas/epica-06-arquitectura-automatizacion/` y `_planificacion/10_epicas/epica-07-operacion-continua/`, que quedaron en el repositorio después de la reorganización de RDA-014. Cada una tiene un solo archivo. Todo su contenido relevante está en las carpetas vigentes. Ningún documento las enlaza: solo las mencionan como texto. No se borró ni movió nada.

## 1. Archivos y su equivalente vigente

| Carpeta antigua / archivo | Último commit que lo tocó | Equivalente vigente | ¿Difiere de forma relevante? |
| :------------------------ | :------------------------ | :------------------ | :--------------------------- |
| `epica-06-arquitectura-automatizacion/definicion-epica-06.md` (3.317 bytes) | `3347c21` (00-01, nota de retención de volcados) | Iteraciones 06-01 a 06-03 → `epica-06-mantencion-respaldos/definicion-epica-06.md`. Iteraciones 06-04, 06-05 y 06-06 → `epica-07-arquitectura-codigo/definicion-epica-07.md` (07-01, 07-02, 07-04) | No: todo el contenido está en las vigentes (detalle abajo) |
| `epica-07-operacion-continua/definicion-epica-07.md` (2.261 bytes) | `fac89a8` (documentación inicial) | `epica-13-operacion-continua/definicion-epica-13.md` (13-01 a 13-06) | No: todo el contenido está en la vigente |

Comprobación del contenido, buscando en las vigentes cada elemento de las antiguas:

- **Antigua 06:**
  - En la 06 vigente: la nota de retención de volcados (6,19 MB, 1.438.471 bytes, AUD-02-019), la limpieza de filas duplicadas de `HistorialBD`, la orden de mantención que retira la invocación desde el panel, AUD-02-007, los siete días de tarea, «ninguna vista de lectura escribe» y la regresión de fechas en UTC.
  - En la 07 vigente: AUD-02-012, AUD-02-013, AUD-02-014, AUD-02-015, la capa de servicios y la deuda menor.
  - «Unificar `estado_pago` exige Clase 3»: está en la 06 vigente (`:57`, ahora 13-05, antes 07-05) y en la 07 vigente (`:42`).
- **Antigua 07:** en la 13 vigente están el recordatorio en el calendario personal, las bitácoras con sufijo, la deuda diferida (copia de ítems al duplicar, Clase 3), las señales para evaluar un plan de pago y «no tiene término».
- **Sin equivalente:** ninguno. Las vigentes agregan contenido (06-04 nueva, 07-03 nueva, respaldo de los días 1 y 15) que las antiguas no tienen.

## 2. Referencias entrantes

Búsqueda de `epica-06-arquitectura-automatizacion` y `epica-07-operacion-continua` en todo el repositorio, sin `.env`, `.env.*`, la carpeta de respaldos, `.git/` ni `.venv/`. Ningún comentario de código las menciona.

| Archivo:línea | Tipo | ¿Bitácora entregada? |
| :------------ | :--- | :------------------- |
| `_planificacion/10_epicas/epica-06-mantencion-respaldos/definicion-epica-06.md:56` | Mención en texto («La carpeta cambia de `epica-06-arquitectura-automatizacion` a …») | No (definición vigente) |
| `_planificacion/10_epicas/epica-13-operacion-continua/definicion-epica-13.md:46` | Mención en texto («La carpeta cambia de `epica-07-operacion-continua` a …») | No (definición vigente) |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-01-cierre.md:19` | Ruta en una tabla de archivos modificados, en código, sin enlace | **Sí** |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-05-cierre.md:50, 70, 81, 110, 114, 125, 128, 200` | Menciones en texto y rutas en código, sin enlace | **Sí** |

No hay enlaces Markdown (`[texto](ruta)`) hacia esas carpetas ni hacia sus archivos.

## 3. ¿Borrarlas rompe algún enlace?

- **No rompe ningún enlace:** todas las referencias son menciones de texto.
- Las dos definiciones vigentes las citan para explicar de dónde viene cada carpeta: siguen siendo correctas después del borrado, como historia.
- Dos bitácoras entregadas, `bitacora-00-01-cierre.md` y `bitacora-02-05-cierre.md`, citan sus rutas. No se editan: después del borrado, la ruta se encuentra en el historial de git (por ejemplo, `git show 3347c21 -- _planificacion/10_epicas/epica-06-arquitectura-automatizacion/`).

## 4. Carpetas vigentes (nombres exactos)

| Épica | Carpeta vigente | Archivo |
| :---- | :-------------- | :------ |
| 06 · Mantención automatizada y respaldos | `_planificacion/10_epicas/epica-06-mantencion-respaldos/` | `definicion-epica-06.md` |
| 07 · Arquitectura del código | `_planificacion/10_epicas/epica-07-arquitectura-codigo/` | `definicion-epica-07.md` |
| 13 · Operación continua | `_planificacion/10_epicas/epica-13-operacion-continua/` | `definicion-epica-13.md` |

Las que se borran: `epica-06-arquitectura-automatizacion/` y `epica-07-operacion-continua/`. Hay que cuidar no confundir `epica-07-operacion-continua` (antigua) con `epica-13-operacion-continua` (vigente).

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-cierre-carpetas-antiguas.md` | Este informe |

## Verificación

- `ls` de las cinco carpetas y `git log -1` de cada una; lectura completa de los dos archivos antiguos; búsqueda de referencias en todo el repositorio.
- Pruebas: la corrida del cierre de la épica está en [bitacora-02-cierre-epica](bitacora-02-cierre-epica.md).

## Migraciones

- Ninguna.

## Criterios de aceptación

- No aplica: es un informe.

## Decisiones tomadas

- Ninguna. El borrado lo hace el desarrollador.

## Pendientes y riesgos

- **Fuera de las carpetas, pero relacionado:** el criterio de término de la Épica 06 vigente (`epica-06-mantencion-respaldos/definicion-epica-06.md`) dice «Las pruebas de regresión de fechas en UTC y de **métricas duplicadas** pasan de fallo esperado a verde». No existe una regresión de métricas duplicadas: R5 no se confirmó y queda cubierta por R8. Conviene ajustar ese criterio (no se editó: no era parte del encargo).

## Recomendación

**Seguro borrar.** Ningún enlace se rompe, todo el contenido está en las carpetas vigentes y ningún comentario de código las cita. Comando sugerido para el desarrollador:

```bash
git rm -r _planificacion/10_epicas/epica-06-arquitectura-automatizacion _planificacion/10_epicas/epica-07-operacion-continua
```
