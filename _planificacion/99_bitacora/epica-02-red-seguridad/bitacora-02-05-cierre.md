# Bitácora 02-05-cierre · Control de acceso: decisiones tras la revisión y verificación de RDA-014

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** Terminada (la 02-05, con sus 9 criterios de aceptación marcados)

## Resumen

Registra las decisiones del desarrollador del 2026-10-27 tras revisar [bitacora-02-05](bitacora-02-05.md). Por la regla 5.4, `bitacora-02-05.md` y `bitacora-02-04-cierre.md` (ya entregadas en el commit `99a6157`) no se editan; lo que esta revisión corrige de ellas queda aquí.

- **Parte A:** verificación de RDA-014, sin cambiar ninguna numeración.
- **Parte B:** AUD-02-029 con la regresión R20, que sube el recuento de la 02-04 a 19; AUD-02-030 sin regresión; notas en AUD-01-025 y en la Épica 04.
- **Parte C:** `dashboard` y `estadisticas_bd` pasan de la 06-01 a la 06-02.

## Parte A · Verificación de RDA-014 (solo lectura)

### A1. RDA-014, transcripción literal de `decisiones.md`

> ## RDA-014 · Épicas numeradas según su orden de ejecución, de 00 a 14
>
> - **Fecha:** 2026-10-27
> - **Estado:** Aceptada
> - **Reemplaza a:** RDA-011
>
> **Contexto:** el desarrollador pidió, durante la Épica 02, sumar al plan trabajo que no existía en él: reorganizar el frontend, un módulo de usuarios con roles, mejoras del tablero «Trabajo Semanal», automatizaciones por correo, una proyección de pedidos y servicios de AWS. Además separó la antigua Fase 6 en dos (mantención y arquitectura) y sacó de la Fase 5 los estilos y recursos del navegador. Con eso, la regla «la Épica `NN` es la Fase `N`» de RDA-011 deja de ser posible.
> **Decisión:** las épicas se numeran según su **orden de ejecución**, de 00 a 14, y el número de cada épica coincide con su lugar en la secuencia. El origen en el plan queda escrito en la cabecera de cada definición («Fase del plan») y en el anexo de `plan-de-trabajo.md`. Las iteraciones nuevas toman el correlativo libre de su épica; los números que quedan sin uso no se reasignan, para que ninguna referencia antigua apunte a otra cosa. Las referencias a la numeración anterior en documentos escritos antes de esta fecha (bitácoras, iteraciones cerradas, evidencias, Auditorías 01 y 02, documentos de la Épica 02 y `docs/operacion/`) no se reescriben: se leen con la tabla de equivalencias de abajo.
>
> | Antes | Ahora | Contenido |
> | :---- | :---- | :-------- |
> | Épicas 00 a 04 | Épicas 00 a 04 | Sin cambio de número (la 03 ajusta su contrato de error; la 04 suma 04-07 a 04-09) |
> | 05-01, 05-02, 05-03 | 05-01, 05-02, 05-03 | Sin cambio |
> | 05-04 | 08-05 | Compilación local de Tailwind |
> | 05-05 | 08-06 y 08-07 | Tipografías e íconos; librerías JavaScript |
> | 05-06 | 05-00 y 05-06 (servidor); 08-01 y 08-09 (navegador) | Medición inicial y final |
> | 06-01, 06-02, 06-03 | 06-01, 06-02, 06-03 | Sin cambio (la 06-02 suma la tarea programada y el respaldo de los días 1 y 15) |
> | — | 06-04 | Rediseño del módulo de base de datos (nueva) |
> | 06-04 | 07-01 | Modularización de las vistas |
> | 06-05 | 07-02 | Capa de servicios (y selectores) |
> | — | 07-03 | Modelos por dominio (nueva) |
> | 06-06 | 07-04 | Deuda técnica menor |
> | — | Épicas 08 a 12 | Frontend; usuarios y roles; mejoras del negocio; automatizaciones; proyección de pedidos (nuevas) |
> | 07-01 a 07-06 (Épica 07) | 13-01 a 13-06 (Épica 13) | Operación continua |
> | — | Épica 14 | Tecnología en la nube (AWS) (nueva) |
>
> **Alternativas consideradas:** mantener RDA-011 y agregar las épicas nuevas como 08 en adelante con la operación continua en 07 (descartada por el desarrollador: la operación continua debe ir al final y el número debe decir el orden); renumerar también los documentos cerrados (descartado: las bitácoras no se editan y la tabla basta).
> **Consecuencias:** el commit sigue el formato `Épica N - Iteración NN-NN: …` con el número nuevo. Un número de iteración desde la Épica 05 en adelante ya no se traduce directo a una subfase del plan: la tabla de iteraciones de cada definición dice su origen. Quien lea un documento anterior al 2026-10-27 debe usar la tabla.

### A2. Tablas de iteraciones de las Épicas 06 y 07, tal como están hoy

En `_planificacion/10_epicas/` conviven **dos carpetas por número**: las vigentes (`epica-06-mantencion-respaldos`, `epica-07-arquitectura-codigo`) y las anteriores a RDA-014 (`epica-06-arquitectura-automatizacion`, `epica-07-operacion-continua`), que siguen en el repositorio con estado «Pendiente».

**`epica-06-mantencion-respaldos/definicion-epica-06.md` (vigente):**

| Iteración | Nombre | Origen |
| :-------- | :----- | :----- |
| 06-01 | Fechas locales y registro diario de métricas | 6.1 |
| 06-02 | Orden de mantención diaria y tarea programada | 6.2, con el respaldo de los días 1 y 15 |
| 06-03 | Gestión del disco | 6.3 |
| 06-04 | Rediseño del módulo de base de datos | Nueva (reorganización 2026-10-27, AUD-03-003) |

**`epica-07-arquitectura-codigo/definicion-epica-07.md` (vigente):**

| Iteración | Nombre | Origen |
| :-------- | :----- | :----- |
| 07-01 | Modularización de las vistas | 6.4 (antes 06-04) |
| 07-02 | Capa de servicios y selectores | 6.5 (antes 06-05), ampliada con selectores |
| 07-03 | Modelos por dominio | Nueva (reorganización 2026-10-27) |
| 07-04 | Deuda técnica menor | 6.6 (antes 06-06) |

**`epica-06-arquitectura-automatizacion/definicion-epica-06.md` (anterior a RDA-014):**

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 06-01 | Fechas locales y registro diario de métricas | 6.1 |
| 06-02 | Orden de mantención diaria | 6.2 |
| 06-03 | Gestión del disco | 6.3 |
| 06-04 | Modularización de las vistas | 6.4 |
| 06-05 | Capa de servicios | 6.5 |
| 06-06 | Deuda técnica menor | 6.6 |

**`epica-07-operacion-continua/definicion-epica-07.md` (anterior a RDA-014):**

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 07-01 | Vigilancia de la expiración de la web app | 7.1 |
| 07-02 | Ritual de despliegue consolidado | 7.2 |
| 07-03 | Revisión periódica de registros | 7.3 |
| 07-04 | Ensayo de recuperación ante desastres | 7.4 |
| 07-05 | Deuda diferida y evolución | 7.5 |
| 07-06 | Criterios para evaluar el cambio de plan | 7.6 |

### A3. Menciones de «06-05» y «07-02»

Búsqueda en `_planificacion/`, `docs/` y `pedidos/tests/`, antes de los cambios de esta revisión.

| Archivo:línea | Texto | Significa |
| :------------ | :---- | :-------- |
| `00_producto/decisiones.md:197` | `\| 06-05 \| 07-02 \| Capa de servicios (y selectores) \|` | Tabla de RDA-014: equivalencia |
| `00_producto/registro-pendientes.md:63` | `\| 07-02 \| Capa de servicios y selectores \| 07 \| Pendiente …` | Capa de servicios (numeración nueva) |
| `00_producto/registro-pendientes.md:161` | «Resuelto el 2026-10-26: la 06-05, junto con AUD-02-015 … **Actualización 2026-10-27 (RDA-014):** la antigua 06-05 es la 07-02» | Capa de servicios, con las dos numeraciones |
| `00_producto/registro-pendientes.md:260` | «AUD-02-025 lo corrige la 06-05» (historial del 2026-10-26) | Capa de servicios (numeración anterior) |
| `00_producto/registro-pendientes.md:265` | «R15 corregida a la 06-05» (historial del cierre de la 02-04) | Capa de servicios (numeración anterior) |
| `00_producto/auditoria-tecnica.md:79` | AUD-02-014: «corregir en 03-03 o 06-05 según la respuesta» | Capa de servicios (numeración anterior, Auditoría 02) |
| `00_producto/auditoria-tecnica.md:80` | AUD-02-015: «Convertir con `Decimal` en la capa de servicios. Iteración 06-05.» | Capa de servicios (numeración anterior) |
| `00_producto/auditoria-tecnica.md:90` | AUD-02-025: «Iteración 06-05, junto con AUD-02-015» | Capa de servicios (numeración anterior) |
| `docs/operacion/pruebas.md:118` | R15: «06-05, junto con AUD-02-015 (decisión del 2026-10-26; numeración anterior a RDA-014)» | Capa de servicios (numeración anterior) |
| `pedidos/tests/test_regresiones.py:391` | «R15 · AUD-02-025 … Lo corrige la 06-05, junto con AUD-02-015.» | Capa de servicios (numeración anterior) |
| `10_epicas/epica-02-red-seguridad/iteracion-02-04-regresiones.md:49` | Fila R15, columna «Lo corrige»: `06-05` | Capa de servicios (numeración anterior) |
| `10_epicas/epica-06-mantencion-respaldos/definicion-epica-06.md:56` | «La modularización, la capa de servicios y la deuda menor pasan a la Épica 07 (antes 06-04, 06-05 y 06-06)» | Capa de servicios (numeración anterior, citada como «antes») |
| `10_epicas/epica-06-arquitectura-automatizacion/definicion-epica-06.md:25` | `\| 06-05 \| Capa de servicios \| 6.5 \|` | Capa de servicios (carpeta anterior) |
| `10_epicas/epica-07-arquitectura-codigo/definicion-epica-07.md:16` | «**Capa de servicios y selectores (07-02):**» | Capa de servicios (numeración nueva) |
| `10_epicas/epica-07-arquitectura-codigo/definicion-epica-07.md:19` | «… (AUD-02-025, regresión R15 de la 02-04; asignado por el desarrollador el 2026-10-26 a la antigua 06-05, hoy 07-02) …» | Capa de servicios, con las dos numeraciones |
| `10_epicas/epica-07-arquitectura-codigo/definicion-epica-07.md:29` | `\| 07-02 \| Capa de servicios y selectores \| 6.5 (antes 06-05) …` | Capa de servicios (numeración nueva) |
| `10_epicas/epica-07-operacion-continua/definicion-epica-07.md:22` | `\| 07-02 \| Ritual de despliegue consolidado \| 7.2 \|` | **Otra iteración:** ritual de despliegue (carpeta anterior; hoy 13-02) |
| `10_epicas/epica-13-operacion-continua/definicion-epica-13.md:28` | `\| 13-02 \| Ritual de despliegue consolidado \| 7.2 \| 07-02 \|` | **Otra iteración:** ritual de despliegue, número anterior |
| `10_epicas/epica-11-automatizaciones/definicion-epica-11.md:19` | «Usa los selectores de saldo de la 07-02.» | Capa de servicios (numeración nueva) |
| `10_epicas/epica-00-blindaje/iteracion-00-05-protocolo-despliegue.md:50` | «Consolidar la lista con los pasos de las fases posteriores (va en 07-02).» | **Otra iteración:** ritual de despliegue (numeración anterior; hoy 13-02) |
| `99_bitacora/…/bitacora-02-02-cierre.md:18, 19, 40, 54` | AUD-02-025 y R15: «la 06-05» | Capa de servicios (numeración anterior) |
| `99_bitacora/…/bitacora-02-04.md:124` | «el comentario dice que la corrige la 07-02 (antes 06-05, RDA-014)» | Capa de servicios, con las dos numeraciones |
| `99_bitacora/…/bitacora-02-04-cierre.md:20, 21, 48, 53, 58` | «R15 → 06-05» y la nota sobre la numeración | Capa de servicios (numeración anterior) |

### A4. ¿Qué renumera RDA-014?

- RDA-014 renumera **la misma iteración** «Capa de servicios»: 06-05 pasa a 07-02, ampliada con selectores. Es la iteración que hoy corrige AUD-02-015 (`Decimal`) y AUD-02-025 (R15), según la definición vigente de la Épica 07 (líneas 16 y 19). No asigna ese trabajo a una iteración distinta: «06-05» (antes) y «07-02» (ahora) nombran lo mismo.
- El «07-02» de **otra** iteración es el ritual de despliegue consolidado de la antigua Épica 07, que RDA-014 pasa a 13-02. Aparece en la carpeta anterior `epica-07-operacion-continua`, en `epica-13` (columna de origen) y en `iteracion-00-05`.
- RDA-014 dice que los documentos anteriores a esa fecha y los de la Épica 02 no se reescriben y se leen con la tabla.
- No resuelvo la discrepancia. Por decisión del desarrollador, R15 queda como está («06-05»).
- Observación sin cambios: las carpetas `epica-06-arquitectura-automatizacion` y `epica-07-operacion-continua` siguen en el repositorio junto a las vigentes y pueden confundir. Moverlas o eliminarlas requiere consulta (`AGENTS.md`, sección 6).

## Parte B · Decisiones del desarrollador (2026-10-27)

- **H1 → AUD-02-029** (Baja, Errores; la corrige la 03-01). Regresión **R20** en `test_regresiones.PkInexistenteTests.test_r20_pk_inexistente_responde_404`: afirma 404 en las 12 rutas, tomadas de `test_acceso.PkInexistenteTests.CON_500`, sin duplicar la lista.
  - Verificación sin la marca: `AssertionError: {'/pe[17 chars]9/': 500, '/pedido/eliminar/999999/': 500, … 500} != {… 404, '/pedido/eliminar/999999/': 404, … 404}`, `FAILED (failures=1)`. Falla porque responde 500, no por un error de montaje.
  - La caracterización de la 02-05 se mantiene, y cada prueba lleva un comentario que la relaciona con la otra.
  - Recuento de la 02-04: **19**, actualizado en la iteración, la definición, el registro y `pruebas.md`, sin renumerar R1 a R19.
- **H2 → AUD-02-030** (Baja, Seguridad; se decide en la Épica 04, sin regresión). La lista de rutas públicas no cambia.
  - **Cómo la trata hoy la prueba de inventario:** las rutas de recuperación de contraseña y el acceso del panel de administración están **fuera** de las 40. El inventario recorre solo `pedidos.urls.urlpatterns`; estas rutas vienen de `django.contrib.auth.urls` y de `admin.site.urls`, incluidas en `PedidosApp/urls.py`. La prueba no las ve, así que no falla por ellas ni las protege.
  - Si se quisiera vigilarlas, habría que ampliar el inventario al resolvedor del proyecto. Queda para la Épica 04.
- **H3 → nota en AUD-01-025** (limpieza, 04-05), sin ID nuevo.
- **H4 → nota en la definición de la Épica 04**, sin ID nuevo. Incluye el aviso de actualizar `test_acceso` y el contrato de `index.js` si se cambia.
- **D5:** AUD-02-028 (R19) sigue `PENDIENTE_DESARROLLADOR`.
- Los cuatro hallazgos propuestos de la 02-05 salen de la sección 4 del registro; el historial lo registra.

## Parte C · Corrección de una referencia

La 06-01 corrige las fechas en UTC. La 06-02 (orden de mantención diaria) retira la invocación desde el panel y desde las estadísticas de la base; así lo dice `definicion-epica-06.md:18`. Cambios:

| Archivo | Antes | Ahora |
| :------ | :---- | :---- |
| `docs/operacion/pruebas.md` (7.1) | «se resuelven en la 06-01» | «La 06-02 … retira la invocación …; la 06-01 corrige las fechas en UTC» |
| `iteracion-02-04-regresiones.md` (decisión 7) | «se resuelven en la 06-01» | «se resuelven en la 06-02 (corregido el 2026-10-27; ver decisión 10)», más la decisión 10 |
| `definicion-epica-02.md` (nota del cierre de la 02-04) | «(06-01)» | «(los resuelve la 06-02; corregido el 2026-10-27, antes decía 06-01)» |
| `registro-pendientes.md` (sección 3) | «se resuelven en la 06-01» | «se resuelven en la 06-02, que retira la invocación … (corregido el 2026-10-27 …)» |

Sin cambiar, porque son bitácoras entregadas: `bitacora-02-04-cierre.md:43` («se resuelven en la 06-01») queda corregida por esta bitácora. `bitacora-02-04.md:93` ya decía «06-01 y 06-02».

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/tests/test_regresiones.py` | R20; la numeración del encabezado incluye R20 |
| `pedidos/tests/test_acceso.py` | Solo el comentario de `CON_500`: AUD-02-029 y su correspondencia con R20 |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-02-029 y AUD-02-030; notas de la 02-05 (incluida la de AUD-01-025) |
| `_planificacion/00_producto/registro-pendientes.md` | 02-05 terminada; 4 propuestas fuera de la sección 4; referencia 06-02; historial |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-04-regresiones.md` | R20, recuento 19, decisiones 9 y 10, referencia 06-02 |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-05-control-acceso.md` | Terminada; decisiones 3 a 7 |
| `_planificacion/10_epicas/epica-02-red-seguridad/definicion-epica-02.md` | Recuento 19; 02-05 terminada; referencia 06-02; nota del cierre |
| `_planificacion/10_epicas/epica-04-seguridad/definicion-epica-04.md` | Nota H4 (302 en vez de 401 y 403) y AUD-02-030 |
| `docs/operacion/pruebas.md` | N = 19, fila R20, referencias a AUD-02-029 y AUD-02-030, referencia 06-02 |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-05-cierre.md` | Esta bitácora |

## Verificación

- **Tres ejecuciones seguidas** de `python manage.py test pedidos -v 2`:

```text
Ejecución 1: Found 184 test(s). Ran 184 tests in 217.774s  OK (expected failures=19)
Ejecución 2: Found 184 test(s). Ran 184 tests in 238.678s  OK (expected failures=19)
Ejecución 3: Found 184 test(s). Ran 184 tests in 268.959s  OK (expected failures=19)
```

  Sin `failures`, `errors` ni `unexpected successes`. 184 = 183 + R20.
- `python manage.py test pedidos --exclude-tag regresion` → `Ran 165 tests` … `OK`.
- `python manage.py test pedidos --tag regresion` → `Ran 19 tests` … `OK (expected failures=19)`.
- `python manage.py check` → `System check identified no issues (0 silenced).`
- `python manage.py makemigrations --check --dry-run` → `No changes detected` (código de salida 0).
- `git status --short` y `git diff --stat`: solo `pedidos/tests/` y archivos `.md`.

## Migraciones

- Ninguna.

## Criterios de aceptación

- No aplica: es un cierre documental. Los 9 criterios de la 02-05 están marcados en su iteración, por eso pasa a «Terminada».

## Pendientes y riesgos

- **Numeración 06-05 / 07-02:** ver A4; decide el desarrollador. R15 queda como está.
- **Carpetas anteriores a RDA-014** (`epica-06-arquitectura-automatizacion`, `epica-07-operacion-continua`): siguen en el repositorio; moverlas o eliminarlas requiere consulta.
- **AUD-02-028:** iteración que lo corrige, `PENDIENTE_DESARROLLADOR`.
- **AUD-02-030:** el inventario no vigila las rutas de fuera de `pedidos/urls.py`.

## Commit sugerido

`Épica 2 - Iteración 02-05: cierra la iteración, suma AUD-02-029 a la 02-04 como R20 (19 regresiones), registra AUD-02-030 y verifica RDA-014 sin renumerar`
