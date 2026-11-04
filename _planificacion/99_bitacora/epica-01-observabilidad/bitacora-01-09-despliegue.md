# Bitácora 01-09 · Despliegue de `v1.2-capturas` y cierre de la Épica 01

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** 01-07, 01-08 y 01-09 **Terminadas** (2026-11-04) y **Épica 01 Terminada** (2026-11-04), por instrucción expresa del desarrollador y con sus tres condiciones cumplidas (ver «Cierre»). La 00-07 sigue En revisión, sin fecha de despliegue.

Es la bitácora nueva que pide la regla 5.4 de `_planificacion/README.md`: [bitacora-01-09](bitacora-01-09.md) y [bitacora-01-09-evidencia](bitacora-01-09-evidencia.md) ya están entregadas y no se editan. Solo se citan conteos, horas, tamaños y códigos; ningún dato de clientes y ninguna ruta de la carpeta de respaldos (solo nombres de archivo). Todas las horas son de Chile, salvo que diga UTC. Toda la medición viene de producción y la entregó el desarrollador; el agente no tiene acceso al servidor.

## Resumen

`v1.2-capturas` (etiqueta anotada, objeto `567db391d5d1bf818f63d7d33758be7898c8abcc`, sobre el commit `81005df`, partida `v1.1-observabilidad`, `d6768d0`) se desplegó el 2026-11-04 **sin migraciones, sin `pip` y sin `collectstatic`** y quedó validada sin retroceso. La **hora oficial de la recarga es 00:11:49** (decisión del desarrollador); la que se había informado, 00:14:00, queda como «informada». E1 (cuatro pantallas) salió sin problemas; el respaldo de E2 se hizo **después** del reinicio y salió `VÁLIDO` (19 de 19); E3 mostró 1 `ERROR` (el ruido conocido de `root`) y 1 `INFO`, con los emojis 🔴 y 🔵 de la 01-07. Antes del despliegue hubo un **incidente** en la consola del servidor (`git checkout main` por error), restaurado sin `git pull` ni reinicios; su ventana queda **registrada como no verificada**. Con esto se cierran la 01-07, la 01-08, la 01-09 y la Épica 01.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-01-observabilidad/evidencia-01-09.md` | Partes B a E completas, incidente, hora de la recarga (decisión 1), ventana no verificada (decisión 4) y respuesta del desarrollador |
| `docs/operacion/respaldo.md` | Sección 6: fila del respaldo de E2 y nota sobre las dos horas; sección 3: ruta dañada corregida a `$env:TEMP\verificar_respaldo_v02.py` (era un carácter de control, `0x0B`, en lugar de `\v`; el archivo ya no tiene ninguno) |
| `docs/operacion/despliegue.md` | Sección 5: fila de `v1.2-capturas` con la hora oficial. Sin tocar la fila de `v1.1-observabilidad` ni la sección 3 |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-07-marcas-visuales.md`, `iteracion-01-08-comentarios-registro.md`, `iteracion-01-09-capturas-amplias.md` | `Terminada (2026-11-04)` con su historial; cuatro criterios de la 01-09 marcados con su medición |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | Épica `Terminada (2026-11-04)`, filas de iteraciones y sección «Cierre de la épica» |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-07.md` e `iteracion-00-07-correcciones-tempranas-ii.md` | Fechas «2026-11-01» tachadas y 00-07 «sin fecha» (decisión 3); nota fechada |
| `_planificacion/00_producto/auditoria-tecnica.md` | Nota fechada de AUD-04-004 (decisión 2), sin reescribir el hallazgo |
| `_planificacion/00_producto/registro-pendientes.md` | Iteración activa y próximo hito, filas de iteraciones, las 7 líneas `root` clasificadas, decisiones de la sección 3 e historial |
| `_planificacion/99_bitacora/epica-01-observabilidad/bitacora-01-09-despliegue.md` | Esta bitácora |

Sin cambios de código, de `pedidos/tests/`, de documentos protegidos, de `.claude/`, de la fila de `v1.1` de `despliegue.md` ni de bitácoras ya entregadas.

## Cronología (hora de Chile)

| Hora | Hecho | Fuente |
| :--- | :---- | :----- |
| 2026-11-03 22:34:09 | Parte A: respaldo previo (`respaldo_03-11-2026_22-34-09.sql`, `600993c55d75…`, 19 de 19) | evidencia-01-09, parte A |
| 2026-11-03 22:37:58 | Parte D de la 01-06 | [bitacora-01-06-medicion](bitacora-01-06-medicion.md) |
| hacia las 23:41 (02:41 UTC) | **Incidente:** `git checkout main` por error en el servidor | Informe del desarrollador |
| 23:41 a 00:09 | Ninguna línea `Starting uWSGI` (consulta con filtro por fecha, archivos rotados incluidos, desde 23:30:00) | Registro de uWSGI |
| hacia las 00:09 (03:09 UTC) | Restauración: `git checkout v1.1-observabilidad` | Informe del desarrollador |
| hacia las 00:10 | D2: `fetch origin --tags`, `checkout v1.2-capturas` | Informe del desarrollador |
| **00:11:49** | **Hora oficial de la recarga:** `Starting uWSGI 2.0.28`, mensaje interno `[Wed Nov  4 03:11:48 2026]` (UTC) | Registro de uWSGI |
| 00:12:37 | Hora del **nombre** del respaldo de E2 | Nombre del archivo |
| 00:12:39 | `INFO` 🔵 de `pedidos.utils` y `ERROR` 🔴 de `root` en `server.log` | E3 |
| 00:14:00 | Hora de la recarga **informada** por el desarrollador | Informe del desarrollador |

## Las dos horas de la recarga (decisión 1)

El desarrollador informó la recarga a las 00:14:00, pero el respaldo de E2 lleva las 00:12:37 en su nombre y `Starting uWSGI` figura a las 00:11:49. **Decisión del desarrollador (2026-11-04):** la hora oficial en `despliegue.md` y en el registro es **00:11:49**; la informada, 00:14:00, queda anotada como «informada», 2 min 11 s posterior. Un detalle sin consecuencias: el prefijo del registro (00:11:49) y el mensaje interno de uWSGI (03:11:48 UTC, es decir 00:11:48 en Chile) difieren en un segundo; la hora oficial es la del prefijo, que al pasarla a UTC da 03:11:49.

**El respaldo de E2 fue posterior al reinicio:** 48 s según el nombre (00:12:37) y 50 s según el `INFO` (00:12:39). Además, ese `INFO` empieza con 🔵, el emoji de `v1.2` (en `v1.1-observabilidad` el `INFO` llevaba ❕), de modo que lo escribió el código nuevo. Entre el nombre y el registro hay 2 s; en el respaldo de las 22:34:09 coincidían al segundo. No se explica y no cambia la conclusión.

## Incidente del `git checkout main` en el servidor (decisión 4)

- **Qué pasó:** hacia las 23:41 del 2026-11-03 se ejecutó por error `git checkout main` en la consola del servidor; era un comando de la parte B, que va en el PC. El servidor quedó en la rama `main` **del servidor**, atrasada (`git describe` = `v0.0-inicial`; Git indicó 32 commits de atraso). Sin cambios en archivos versionados: solo líneas `??` de `media/` y `staticfiles/`. **No se hizo `git pull`.**
- **Resolución:** hacia las 00:09, `git checkout v1.1-observabilidad`: `describe` = `v1.1-observabilidad`, `rev-parse` = `d6768d0`, `git status --short` vacío. Unos 28 minutos de desfase (horas informadas «hacia»).
- **Reinicios:** ninguno entre las 23:41 y las 00:09. Una sola línea `Starting uWSGI` desde las 23:30:00: la de las 00:11:49.
- **Ventana 2026-11-03 23:41 a 2026-11-04 00:09: NO VERIFICADA.** No se comprobó si alguna petición leyó archivos del árbol atrasado ni si `server.log` tuvo líneas nuevas en ese tramo. Lo que sí se conoce: sin cambios en archivos versionados, sin `git pull`, restauración con `describe` y `rev-parse` correctos, y las cuatro pantallas de E1 funcionaron. **Inferencia, no comprobada:** la web app tenía cargado en memoria el código de `v1.1-observabilidad`. El desarrollador decide si revisa esa ventana (ver «Pendientes»).

## Resultado de la validación (E1 a E3)

| Revisión | Resultado |
| :------- | :-------- |
| E1 Acceso, panel, listado y detalle | Sin problemas |
| E2 Respaldo por el camino normal | `respaldo_04-11-2026_00-12-37.sql`, 1.481.788 bytes, 19 de 19, `VÁLIDO`, código 0, SHA-256 `348f44c3eb91…`; descargado y guardado en la carpeta cifrada. Si fue directo o desde Files: no informado |
| E3 desde 00:11:49 (definitiva) | `1 nivel=ERROR` y `1 nivel=INFO`. La primera ejecución, con `DESDE_CL` 00:14:00, salió vacía porque empezaba después de los eventos y no cuenta |
| E3 emojis | 🔵 en el `INFO` y 🔴 en el `ERROR`, ambos a las 00:12:39 |

## La octava línea `root` (2026-11-04 00:12:39)

El único `ERROR` de E3 es `mensaje="OSError: write error"`, `registrador=root`, sin método, ruta, usuario ni excepción: el ruido de AUD-04-004. Es la **octava** línea igual desde el reinicio del 2026-10-25: 7 antes de `v1.2` y 1 después (nota fechada en `auditoria-tecnica.md`, decisión 2).

- **Coincidencia:** tiene el mismo segundo (00:12:39) que el `INFO` del respaldo de E2, igual que la pista de la 00-05 (un `write error` 2 s después de generar un respaldo, el 2026-10-23).
- **No es sistemática:** en los nueve días de la medición solo hubo un `respaldo_generado` (el de las 22:34 del 2026-11-03) y a esa hora no hubo `OSError`. Ninguna de las 7 líneas anteriores coincide con él. Con tan pocos respaldos, no se puede decir más.
- **Hipótesis, no conclusión:** la recarga de la página a los 2 segundos (`location.reload()`, AUD-03-002) corta la descarga. Es consistente con lo observado, pero no se confirmó. Si la descarga de E2 fue desde Files (no informado), también sería compatible.
- **El archivo no se dañó:** salió `VÁLIDO` (19 de 19).
- **Sin acción.** La causa de las otras 7 tampoco se concluye.

## Cierre de las iteraciones y de la Épica 01

Condiciones del desarrollador para cerrar la 01-07, la 01-08 y la 01-09, todas cumplidas:

| Condición | Evidencia |
| :-------- | :-------- |
| E1 cumplida | Las cuatro pantallas sin problemas |
| Respaldo de E2 posterior al reinicio | Reinicio 00:11:49; nombre 00:12:37 (+48 s); `INFO` 00:12:39 (+50 s); el `INFO` lleva el emoji de `v1.2` |
| E3 sin `ERROR` nuevos, salvo el ruido conocido | 1 `ERROR`: `root`, `OSError: write error`, AUD-04-004 |

- **01-07 · Terminada.** Sus criterios ya estaban marcados; el 🔵 y el 🔴 de E3 son la primera comprobación de los emojis nuevos en producción (2 de los 5 niveles; `WARNING`, `CRITICAL` y `DEBUG` no aparecieron).
- **01-08 · Terminada.** Solo comentarios, sin despliegue propio; viajó dentro de `v1.2-capturas`, que quedó validada sin retroceso.
- **01-09 · Terminada.** Los cuatro criterios de producción quedan marcados: respaldo previo `VÁLIDO` (parte A), despliegue de `v1.2-capturas` sobre `81005df` sin migraciones, `pip` ni `collectstatic` (partes C y D), respaldo normal descargado (E2) y `server.log` sin errores nuevos y con emojis (E3). **Salvedad:** E3 tiene 1 `nivel=ERROR`; se da por cumplido porque es el ruido conocido, como pidió el desarrollador.
- **Épica 01 · Terminada.** Sus tres criterios de término (diagnóstico en unos 2 minutos desde `server.log`, `fontTools` en 0 y crecimiento de la tabla en el 47,5 % de la estimación) se midieron en la 01-06 y están en la sección «Cierre de la épica» de [definicion-epica-01](../../10_epicas/epica-01-observabilidad/definicion-epica-01.md). Sus nueve iteraciones están Terminadas. Nada de la evidencia escrita impide el cierre.
- **Excepción a `AGENTS.md`, sección 10, paso 8** (dejar la iteración en `En revisión`): hecha por instrucción expresa, como en la 01-06.
- **No cierra:** la 00-07 (sigue En revisión, sin fecha) ni la Épica 03 (sigue bloqueada hasta cerrar la 00-07, decisión del desarrollador).

## Migraciones

- Ninguna. `migrate --plan` del servidor: «No planned migration operations.» Esta iteración solo toca documentos `.md`.

## Verificación

- Evidencia de producción: tomada tal como la entregó el desarrollador; el agente no la pudo comprobar.
- Cálculos con las horas informadas: 00:14:00 − 00:11:49 = 2 min 11 s; 00:12:37 − 00:11:49 = 48 s; 00:12:39 − 00:11:49 = 50 s.
- Caracteres de control: `respaldo.md` tenía uno (`0x0B`, en la sección 3) y se corrigió. Revisados los 12 `.md` tocados (11 modificados y esta bitácora), byte a byte: 0 caracteres de control (salvo LF y TAB) y 0 CR.
- Enlaces: los 16 que apuntan a `bitacora-01-09-despliegue.md` resuelven, y no hay enlaces `.md` rotos en los archivos tocados.
- Rutas: ningún archivo tocado contiene una ruta con unidad de disco ni carpeta de usuario; la carpeta de respaldos solo se nombra, sin ruta.
- `git status --short`: 11 archivos `M` y 1 `??` (esta bitácora), todos `.md`. `git diff --stat`: 11 archivos, 129 inserciones y 56 eliminaciones.
- Pruebas: no se ejecutaron; no hay cambios de código ni de pruebas. Pantallas: no aplica.
- Lo que el agente **no** pudo comprobar: la ventana del incidente, la hora real del clic en Reload, la causa de las líneas `root`, y la forma de descarga de E2.

## Propuestas, sin aplicar (decide el desarrollador)

### 1. Advertencia para `despliegue.md`, sección 3 (después del paso 3.2)

```markdown
> **Advertencia (incidente del 2026-11-03).** En la consola del servidor solo se ejecutan `git fetch origin --tags` y `git checkout <etiqueta>`. **Nunca** el checkout de una rama (`main` u otra), `git pull`, `merge`, `rebase` ni `reset`. Los comandos de la lista de comprobación (`git checkout main`, pruebas, `check --deploy`) son del PC. Antes de cada comando de Git, mira el prompt de la consola: debe decir `(HEAD detached at <etiqueta>)`; si dice `main` u otra rama, detente. Si te equivocas, no hagas `git pull`: vuelve con `git checkout <etiqueta anterior>`, comprueba `git describe --tags`, `git rev-parse --short HEAD` y que `git status --short` quede vacío, y revisa en el registro de uWSGI que no hubo reinicios entre el error y la restauración.
```

Opcional, en el paso 3.1: `git branch --show-current` no imprime nada con `HEAD` suelto (si la versión de Git del servidor lo admite). En el servidor solo debería haber `HEAD` suelto sobre una etiqueta, así que una respuesta con el nombre de una rama es una alarma.

### 2. Comando de solo lectura para detectar reinicios de uWSGI con filtro por fecha

Imprime solo la fecha y una etiqueta fija, nunca la línea. Recorre el archivo vivo y los rotados por nombre explícito, **exige** que la línea empiece con fecha y sea de arranque, y filtra por la hora de Chile. Evita el glob `zcat -f $S*`, que recorre archivos que no son del registro y devuelve líneas antiguas. **El agente no lo probó** (no tiene acceso al servidor): conviene ejecutarlo primero con una fecha donde se conozca el resultado, por ejemplo `2026-11-03 23:30:00`, que debe imprimir solo la línea de las 00:11:49.

**[PA · Bash]**

```bash
S=/var/log/manzagrafica.pythonanywhere.com.server.log
DESDE_CL="2026-11-03 23:30:00"
echo "$DESDE_CL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE_CL válido"
for f in "$S" "$S".*; do [ -f "$f" ] && zcat -f "$f"; done \
  | awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9:]+ \*\*\* Starting uWSGI/ && substr($0,1,19) >= d { print substr($0,1,19), "Starting uWSGI" }' \
  | sort
```

- Sin líneas impresas: no hubo reinicios desde esa hora. Cada línea es un reinicio efectivo, con la hora de Chile del prefijo.
- Para saber si un tramo tuvo reinicios, `DESDE_CL` es el inicio del tramo y se miran las horas impresas.

## Criterios de aceptación

Criterios de la [iteración 01-09](../../10_epicas/epica-01-observabilidad/iteracion-01-09-capturas-amplias.md), todos marcados:

- [x] Respaldo previo descargado y verificado: 19 de 19, `VÁLIDO`, código 0, con su fila en `respaldo.md` §6.
- [x] Desplegada con `v1.2-capturas` sobre `81005df`, sin migraciones, `pip` ni `collectstatic`.
- [x] Respaldo por el camino normal descargado, sin provocar fallos.
- [x] `server.log` sin `ERROR` nuevos (salvo el ruido conocido) y con los emojis de la 01-07.

## Decisiones tomadas (2026-11-04, todas del desarrollador)

1. **Hora oficial de la recarga:** 00:11:49, la de `Starting uWSGI`; la informada, 00:14:00, queda como «informada».
2. **AUD-04-004:** nota fechada en `auditoria-tecnica.md` con las 8 líneas `root` (7 antes de `v1.2` y 1 después), sin acción ni causa.
3. **Fechas «2026-11-01»:** solo se corrigió la de `iteracion-00-07` (más `evidencia-00-07` y el registro); la 00-07 queda «sin fecha». No se tocó la fila de `v1.1` de `despliegue.md`.
4. **Ventana del incidente:** registrada como no verificada.
5. **Cierre:** 01-07, 01-08, 01-09 y Épica 01, con las condiciones de arriba. La 00-07 no se cierra ni se prepara; conviene avisar a Manza Gráfica de su ventana.

## Pendientes y riesgos

- **Ventana del incidente sin verificar.** Si el desarrollador quiere cerrarla: revisar `server.log` entre las 23:41 y las 00:09 (solo conteos por `nivel=` y tipos de excepción).
- **Propuestas de `despliegue.md` sin aplicar** (advertencia de la sección 3 y comando de reinicios).
- **El servidor conserva su rama `main` atrasada** (`v0.0-inicial`): queda a un `git checkout main` de repetir el incidente. La advertencia propuesta lo cubre en el procedimiento; no se tocó el servidor.
- **Líneas `root` (AUD-04-004):** 8 desde el 2026-10-25; seguimiento en la revisión periódica (13-03).
- **00-07:** lista para B4 y C de `evidencia-00-07` cuando el desarrollador lo indique; sin fecha.
- **Otras menciones de «2026-11-01» que no se tocaron** por ser históricas o de bitácoras entregadas: la fila de `v1.1` de `despliegue.md`, `definicion-epica-00.md` (decisión del 2026-10-27), `definicion-epica-03.md` y `evidencia-01-06.md`.

## Commit sugerido

`Épica 1 - Iteración 01-09: registra el despliegue de v1.2-capturas y su validación, cierra las iteraciones 01-07, 01-08 y 01-09 y la Épica 01, y deja el incidente del servidor documentado`
