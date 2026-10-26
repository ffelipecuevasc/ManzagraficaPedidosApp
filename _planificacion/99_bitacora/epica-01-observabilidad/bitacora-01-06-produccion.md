# Bitácora 01-06 · Producción: despliegue y validación de la observabilidad

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado:** en curso. Desplegada el 2026-10-25 como `v1.1-observabilidad` (`d6768d0`). Partes A, B y C validadas: 12 de 13 criterios cumplidos. Falta la parte D (siete días, hacia el domingo 2026-11-01). No pasa a `En revisión` ni a `Terminada` hasta entonces, porque el criterio de la semana depende de esa medición.

## Resumen de la ejecución (2026-10-25, 20:59 a 22:13, hora de Chile)

Fuente: [evidencia-01-06](../../10_epicas/epica-01-observabilidad/evidencia-01-06.md), con sus partes A, B y C completas y la respuesta del desarrollador. Solo se citan conteos, horas y códigos.

| Parte | Resultado |
| :---- | :-------- |
| A1 · Lista de comprobación | `Ran 79 tests` · `OK` (71,0 s); `check --deploy` con 5 avisos (`W004`, `W008`, `W009`, `W012`, `W016`); `No changes detected`; regresión de eliminar pago en `OK` |
| A2 · Respaldo previo | `respaldo_25-10-2026_21-02-34.sql`, 1.446.507 bytes, 18 de 18, `VÁLIDO`, código 0, SHA-256 `f3163addfce2…` |
| A3 · Restauración en la réplica | Código 0, 3,6 s, 18 tablas, `[X] 0006`, tabla de eventos `False` |
| A4 · Migración y reversión | Aplicar 1,46 s, revertir 1,07 s, aplicar de nuevo 1,78 s; plan de reversión con solo `Undo Create model RegistroEvento` |
| A5 · Pruebas y etiqueta | `Ran 79 tests` · `OK` (76,3 s) con la réplica migrada; etiqueta sobre `d6768d0`, `HEAD` igual a `origin/main`; objeto `45817771…` en el remoto |
| B2 · Antes del cambio | Sin 0007, `tabla_eventos: False`, `No planned migration operations.`; `check --deploy` con 4 códigos (sin `W009`: la clave de producción pasa) |
| B3 · `checkout` | `d6768d0`; sin cambios en `requirements.txt` ni en `pedidos/static`; en `pedidos/migrations`, solo la 0007 |
| B4 · Migración | Solo la 0007 en el plan; `Applying … OK` en 2,659 s a las 00:23 UTC; `check --deploy` igual a B2, `ERRORS`: 0 (tarea 5 cumplida) |
| B5 · Antes de recargar | Plantilla faltante (el caso sigue), pago 1056 existe, `eventos: 0` |
| B6 · Recarga | Anotada a las 00:27:15 UTC; reinicio en `server.log` a las 21:26:25 de Chile (00:26:25 UTC). `DESDE` se definió primero con el texto de la plantilla y se corrigió a las 00:31 UTC |
| B7 · Revisión | Acceso, panel, listado y detalle correctos, con la **sesión que el desarrollador ya tenía abierta** (confirmado): por eso no se registró un `acceso_exitoso`, y no es una falla |
| B8 · Verificador | Sintéticos del agente: 19 de 19 con código 0 y 18 de 19 con código 1. **En el PC del desarrollador**, el respaldo de A2 con el script nuevo dio 18 de 19, falta `pedidos_registroevento`, `NO VÁLIDO (1 tabla(s) faltante(s))`, código 1 y SHA-256 `f3163addfce276441938c03419d646770ffecd10ef48d96739c8b2fc89490aa9` (el mismo de A2). Es el resultado esperado |
| C1 · Página 500 | «Algo salió mal», correcta en escritorio y a 360 px, foco visible |
| C2 · Diagnóstico | Cabeceras con `❌` y todo el contexto en `server.log`; traza completa en ambos archivos; unos 2 minutos |
| C3 · Conteos | `server.log`: 2, 2, 0 y 0. `error.log`: 1, 1, 1, 1 y 0, con **14 líneas desde `DESDE`**, exactamente la composición esperada (mensaje, `Traceback`, 10 líneas de traza, excepción e `Internal Server Error`) |
| C4 · PDF | `GET /cotizaciones/27/pdf/ 200` a las 00:54:55 UTC; `fontTools` 0 en ambos archivos; `django.server` 0; solo 2 `nivel=ERROR` |
| C5 · Eventos | Tras la prueba directa (acceso fallido con contraseña inventada y acceso correcto), 2 eventos con hora `UTC-0300`; `purgar_registros`: 0 eliminados; sin `pago_eliminado` |

## Comprobaciones del agente

**SQL de la 0007: idéntico carácter por carácter.** Comparé el bloque `sql` pegado en A1 con el de [bitacora-01-06](bitacora-01-06.md) y con el de [bitacora-01-01](bitacora-01-01.md): los tres son iguales (674 caracteres, sin diferencias en espacios ni en saltos de línea). Clase 2, como se aprobó en 01-01.

**Contenido de la etiqueta.** `git diff --stat v0.2-correcciones v1.1-observabilidad`: 59 archivos, 3.790 inserciones y 283 eliminaciones.
- Hashes resueltos en el repositorio local:
  - `v0.2-correcciones` → `7944943`;
  - `v1.1-observabilidad` → objeto `45817771de0a…` sobre `d6768d00274a…`, igual que en A5 y B3.
- **Código:**
  - `settings.py`: sale `ErrorHandlingMiddleware`, más el bloque 3 de `TEST` y `LOGGING`;
  - `admin.py`, `apps.py`, `decorators.py`, `eventos.py`, `registro.py`, `senales.py`, `models.py`, `utils.py`, `views.py` y la plantilla 500;
  - la orden `purgar_registros`, la migración 0007, `middleware.py` eliminado y `tests.py` reemplazado por el paquete `pedidos/tests/`.
- **Documentos:** `_planificacion/` y `docs/operacion/` (`despliegue.md` y `pruebas.md`).
- **Fuera de lo esperado:** nada.
  - En `views.py`, las líneas que no son de eventos ni de registro son la condición `estado_anterior != nuevo_estado` del evento de cambio de estado (01-04) y la limpieza de `print`.
  - No hay cambios en `requirements.txt`, `pedidos/static` ni `scripts/`: el cambio de `verificar_respaldo.py` (B8) va en un commit posterior a la etiqueta, como estaba previsto.

**Lo que no pude comprobar yo:** los datos del servidor (B2 a C5) y del PC del desarrollador (A1 a A5, la verificación de B8). Se toman de la evidencia tal como los entregó el desarrollador. El hash de la etiqueta sí lo comprobé contra el repositorio local.

## Criterios de la 01-06

| Criterio | Estado | Respaldo |
| :------- | :----- | :------- |
| Lista de comprobación y respaldo | Cumplido | A1, filas 1 a 5, y A2; comparación literal del SQL hecha por el agente |
| Ensayo en la réplica | Cumplido | A3 y A4 |
| 0007 no aplicada antes; plan con solo la 0007 | Cumplido | B2 y B4 |
| Etiqueta, migración y `check --deploy` | Cumplido | A5, B3 y B4 |
| Error con tipo, traza, método, ruta, usuario y hora | Cumplido (redacción corregida por la opción A: en `server.log`) | C2 |
| Diagnóstico en menos de cinco minutos | Cumplido | C2: unos 2 minutos |
| Una sola vez por archivo | Cumplido (redacción corregida por la opción A) | C3 |
| Página 500 en escritorio y a 360 px | Cumplido | C1 |
| Sin `fontTools` ni `django.server` | Cumplido | C4. En `error.log` no hay un conteo directo de `django.server`, pero sus 14 líneas son todas del error controlado (C3) |
| Evento en el admin y purga | Cumplido | C5 |
| Emoji en `server.log`; sin `Logging error` ni `UnicodeEncodeError` en ambos | Cumplido | C2 y C3 |
| `verificar_respaldo.py` con la tabla de eventos | Cumplido | B8: sintéticos del agente y respaldo de A2 en el PC |
| **Crecimiento de una semana** | **Pendiente** | Parte D, hacia el domingo 2026-11-01: filas, MB y contraste con la estimación de 01-01 |

## Documentación de operación completada

- **`docs/operacion/respaldo.md`, sección 6:** fila del respaldo previo a `v1.1-observabilidad` (tamaño, SHA-256 y los dos resultados según la versión del script).
- **`docs/operacion/replica-local.md`, sección 9:** fila del refresco de A3. La comprobación completa de paridad (sección 7) **no se repitió**: la fila lo dice, en lugar de dar por cumplida una paridad que no se midió.
- **`docs/operacion/despliegue.md`, sección 5:**
  - la fila de `v0.2-correcciones` que faltaba: 2026-10-23 18:35, `7944943`, sin respaldo previo porque no tocaba datos;
  - la fila de `v1.1-observabilidad`: 2026-10-25 21:26, `d6768d0`, respaldo `f3163addfce2`.

## Hallazgo: dos destinos de registro

**Solo análisis.** No se cambió código, configuración ni `evidencia-01-06.md`.

### Lo observado (2026-10-25, 21:40:36 en Chile, 00:40:36 UTC)

El error controlado (`/pagos/eliminar/1056/`) quedó escrito **en dos archivos con dos formatos**:

| Archivo | Hora | Formato | Primera línea |
| :------ | :--- | :------ | :------------ |
| `error.log` | UTC, con milisegundos | `AAAA-MM-DD HH:MM:SS,mmm: mensaje`, traza en varias líneas | Solo el mensaje. Sin `nivel=`, sin emoji, sin método, ruta ni usuario. |
| `server.log` | Chile, sin milisegundos | El nuestro: emoji y `clave=valor`, con la traza en la misma línea (saltos escritos como `#012`) | Completa: `❌ nivel=ERROR registrador=pedidos.decorators metodo=GET ruta=… usuario=… excepcion=…` |

En cada archivo hay dos registros: el del decorador y el `Internal Server Error` de `django.request`. `grep -c "nivel=" server.log` da 2; `grep "nivel=" error.log` da 0. No hay `Logging error`: los emojis se escriben bien (UTF-8).

### Configuración vigente (`settings.py`, `LOGGING`)

- **Un manejador propio**, `stderr`: `logging.StreamHandler` con `'stream': 'ext://sys.stderr'`, nuestro filtro y `FormateadorConEmoji`. Está **solo en la raíz** (`root`, nivel `WARNING`).
- **`disable_existing_loggers: False`**.
- **`pedidos`** (`INFO`) y **`django.request`** (`ERROR`) no tienen manejadores propios y **propagan a la raíz**. `django` tiene `handlers: []` y `propagate: True`.
- **`fontTools`** tiene el manejador `stderr` propio, nivel `WARNING` y **`propagate: False`**.

### Causa

**Lo comprobado:**
1. **Nuestro formato sale por la salida de error del proceso, y esa salida termina en `server.log`.** Es el único manejador que produce `nivel=` y emoji, y esas líneas están en `server.log`. El `#012` es el escape octal del salto de línea que aplican los recolectores de registros tipo syslog cuando reciben un flujo línea a línea. Por eso la traza queda en una sola línea, con la hora de Chile del recolector antepuesta.
2. **`error.log` no recibe la salida de error en bruto.** Si la recibiera, sus líneas tendrían nuestro formato. Tiene otro (`%(asctime)s: %(message)s` con la traza debajo), así que **otro manejador de `logging` recibe los mismos registros** y los escribe con su propio formateador.
3. **Ese otro manejador está en la raíz o recibe lo que propaga a ella.** Recibe tanto `pedidos.decorators` como `django.request`, que no tienen nada en común salvo la propagación a la raíz.
4. **Las líneas antiguas de `fontTools` en `error.log`** (2026-10-23) tienen el mismo formato. Antes de la 01-02, `fontTools` propagaba a la raíz. Desde la 01-02 tiene `propagate: False`, así que sus avisos solo pasan por nuestro manejador y hoy irían a `server.log`.

**Lo inferido, sin confirmar:**
- PythonAnywhere instala su propio manejador de `logging` en el registrador raíz, que escribe en `error.log` con formato `%(asctime)s: %(message)s` en UTC.
- La configuración de `logging` que hace Django con `LOGGING` reemplaza los manejadores que la raíz tenga en ese momento, porque configura `root`. Que el manejador de PythonAnywhere siga ahí indica que se agrega **después** de cargar la aplicación WSGI.
- No se pudo confirmar con la documentación ni con una consola: en la consola Bash no corre el proceso web, así que `logging.getLogger().handlers` mostraría otra cosa.

**La documentación de PythonAnywhere no lo explica, y lo que se encontró contradice lo observado.**
- En los foros, el personal de PythonAnywhere dice que lo que va a la salida estándar termina en el registro del servidor, y lo que va a la salida de error, en el registro de errores.
- También recomienda `StreamHandler` a la salida de error para que los registros aparezcan.
- Son respuestas de foro de entre 2013 y 2024, no páginas de ayuda. No se encontró una página oficial vigente sobre los registros de la aplicación web. La página de registro de la ayuda (`/pages/LoggingFromWebApps/`) responde 404.
- Fuentes:
  - [foro 32184](https://www.pythonanywhere.com/forums/topic/32184/);
  - [foro 671](https://www.pythonanywhere.com/forums/topic/671/);
  - [foro 12503](https://www.pythonanywhere.com/forums/topic/12503/).
  El sitio de foros bloqueó la lectura directa y se citan los resúmenes del buscador.
- **Conclusión:** el comportamiento actual de PythonAnywhere con Python 3.13 no coincide con esas respuestas. RDA-013 se apoyó en esa suposición («salida de error, que PythonAnywhere guarda en `error.log`») sin haberla medido en producción, y 01-02 lo dejó como hipótesis (tarea 6 de la 01-06).

**Para confirmarlo** (opcional; requiere código, así que es decisión del desarrollador): una línea de diagnóstico temporal que registre una vez los manejadores de la raíz (clase, formateador y flujo) dentro del proceso web. Bastaría con la opción C de abajo, que necesita conocerlos de todos modos.

### Opciones

Lo que pediste: el emoji y el formato `clave=valor` visibles en el archivo donde ya revisas los errores (`error.log`).

| | Opción | Qué cambia | Riesgo | Qué se pierde | ¿`v1.2-…`? | ¿Migración? | Parecido a lo pedido |
| :-- | :----- | :--------- | :----- | :------------ | :--------- | :---------- | :------------------- |
| **A** | **Aceptar y revisar en `server.log`** (recomendada) | Solo documentos y comandos. El diagnóstico se hace en `server.log`; los saltos se recuperan con `sed 's/#012/\n/g'`. `error.log` queda como copia en el formato de PythonAnywhere. | Bajo. Ninguno técnico. | Nada: la línea completa está en `server.log`. Se pierde la costumbre de mirar solo `error.log`, y cada error queda dos veces en disco (en dos archivos, no duplicado dentro de uno). | No | No | **Alto en contenido**, porque emoji y `clave=valor` están completos. **Bajo en ubicación**, porque es otro archivo. |
| **B** | **Aceptar y no cambiar nada** | Nada, ni siquiera la costumbre. Se sigue diagnosticando en `error.log`. | Bajo. | El contexto de la primera línea (método, ruta, usuario, nivel, emoji). Queda la traza y, en el registro de `django.request`, la ruta. | No | No | **Bajo.** |
| **C** | **Que nuestro formateador también se aplique al manejador de PythonAnywhere** | Código de arranque que, al llegar la primera petición, busca en la raíz el manejador que no es el nuestro y le asigna nuestro filtro y formateador. Opcionalmente quita el nuestro para no escribir dos veces. | **Alto.** Depende de un detalle interno y no documentado de PythonAnywhere (cuándo y cómo instala su manejador), que puede cambiar sin aviso. Exige código en el ciclo de la petición (regla 10) y es difícil de probar en local, donde ese manejador no existe. Si falla, se puede quedar sin registro. | Nada, si funciona. | **Sí** | No | **Alto**, con fecha UTC de PythonAnywhere delante. |
| **D** | **Contexto dentro del mensaje** | El decorador (y una sola entrada para `django.request`) arma el mensaje con `metodo=… ruta=… usuario=…`. Así, cualquier manejador, incluido el de PythonAnywhere, lo muestra. | Medio. Duplica el contexto en `server.log` y no cubre a `django.request` sin tocar cómo Django arma su mensaje. | Nada. | **Sí** | No | **Medio**: contexto sí, emoji y `nivel=` no. |

**Descartada: escribir directamente en `error.log` o `server.log`** (un `FileHandler` hacia `/var/log/…`).
- Esos archivos los crea, rota y escribe el sistema de PythonAnywhere: el personal de los foros dice que no son configurables por el usuario.
- Escribir en ellos desde la aplicación competiría con el recolector y podría corromper líneas o desaparecer en la rotación diaria. Además, puede que la cuenta no tenga permiso de escritura.
- No hay una forma documentada y segura de hacerlo.

**También descartada: un archivo propio en `/home/…`.** No es el archivo donde revisas, suma una rotación y un consumo de disco que hay que administrar (regla 11) y cambiaría RDA-013.

**Recomendación: A.** Sin despliegue ni riesgo, deja visibles el emoji y la línea completa (método, ruta, usuario y traza). La opción C es la única que cumple al pie de la letra «en `error.log`», pero depende de algo no documentado. Si igual la quieres, conviene hacerla en una iteración propia (`v1.2-…`), después de confirmar los manejadores con la línea de diagnóstico.

### Efectos en lo ya decidido (inexactos con lo observado; no se editaron)

| Documento | Qué queda inexacto |
| :-------- | :----------------- |
| RDA-013 (`decisiones.md`) | «salida de error, que PythonAnywhere guarda en `error.log`». En PythonAnywhere, nuestra salida de error va a `server.log`, y `error.log` recibe los mismos registros en el formato de PythonAnywhere. Requiere una actualización fechada, con el texto según la opción que elijas. |
| RDA-005 (`decisiones.md`), actualización 2026-10-25 | «los errores van a `error.log`»: mismo ajuste. |
| RDA-008 | Sigue exacta: solo limita qué se registra, no dónde. |
| Criterios de 01-02 | La hipótesis del manejador propio de PythonAnywhere queda **confirmada en parte**: existe otro manejador, pero escribe en `error.log` y el nuestro termina en `server.log`. «Formato `clave=valor` en `error.log`» no se cumple en `error.log`. |
| Criterios de 01-03 | Página 500 y retiro del middleware: sin cambios. La parte de «el error queda en `error.log` con su contexto» vale solo para `server.log`. |
| Criterios de 01-06 | Tarea 6, «sin líneas duplicadas ni formato antiguo en `error.log`»: dentro de cada archivo no hay duplicados, pero `error.log` tiene **solo** el formato antiguo y el error queda en dos archivos. Tareas 2 y 11 (diagnóstico, `django.server`) y criterio del emoji en `error.log`: se cumplen en `server.log`, no en `error.log`. |
| Criterios de 01-07 | «Comprobación del emoji en el `error.log` real»: el emoji se ve en `server.log`; en `error.log` no aparece. La codificación está bien: no hay `Logging error`. |
| Propuesta de regla 4 (bitacora-01-03) | Dice que lo que va a la salida estándar termina en `server.log` y que la salida de error deja el registro en `error.log`. Ambas cosas están sin verificar o desmentidas. Hay que reescribir la propuesta antes de que la revises. |
| `docs/operacion/despliegue.md` | Sección del registro de errores y variable `L=/var/log/…error.log` de los comandos: apuntan solo a `error.log`. Con la opción A, se suma `server.log` como archivo de diagnóstico, con su hora en Chile y el `#012`. |
| `fontTools` (01-02) | Sus avisos ya no llegan a `error.log`, sino a `server.log`. No es un problema; solo cambia dónde se buscan. |

### Cómo leer C2, C3 y C5 de `evidencia-01-06.md`

**El filtro por fecha.**
- `awk 'substr($0,1,19) >= d'` deja pasar cualquier línea que empiece con letra (`Traceback`, `django.…`, `  File …`), porque una letra es «mayor» que un dígito en la comparación de textos. Así se cuelan trazas antiguas.
- **Para `error.log`**, lo correcto es cortar desde la primera línea con fecha ≥ `DESDE` (UTC) y dejar pasar todo lo que sigue, que es lo que ya estás haciendo:
  ```bash
  awk -v d="$DESDE" '!f && /^[0-9]{4}-[0-9]{2}-[0-9]{2} / && substr($0,1,19) >= d {f=1} f' $L
  ```
- **Para `server.log`**, cada registro es una sola línea que empieza con fecha, así que el filtro original sirve, pero **`DESDE` va en hora de Chile** y sin coma ni milisegundos.

**C2 (diagnóstico).**
- La línea con todo el contexto está en **`server.log`**.
- Para ver la traza:
  ```bash
  grep "ruta=/pagos/eliminar/$ID/" server.log | sed 's/#012/\n/g'
  ```
- El tiempo de diagnóstico se mide hasta tener esa línea.
- En `error.log`, la misma traza está completa, pero sin método ni usuario.

**C3 (formato, duplicados y codificación).**
- **En `server.log`:**
  - las 2 líneas del error con `❌`;
  - ninguna línea con `nivel=` sin emoji;
  - cada registro una sola vez.
- **En `error.log`:**
  - 0 líneas con `nivel=`, esperado con este comportamiento;
  - el error en el formato de PythonAnywhere, una sola vez por registro.
- **En los dos archivos:** 0 `Logging error` y 0 `UnicodeEncodeError`.
- El criterio de la tarea 6 se anota como «cumplido en `server.log`; `error.log` conserva el formato de PythonAnywhere (hallazgo)».

**C5 (eventos en el admin).**
- No cambia: los eventos van a MySQL, no a los archivos.
- Si C5 incluye contar líneas de `fontTools` o `django.server`, se cuentan en los dos archivos. `fontTools` iría a `server.log`.

### Decisión del desarrollador (2026-10-25): opción A

- **El diagnóstico se hace en `server.log`** (hora de Chile; la traza se lee con `sed 's/#012/\n/g'`). `error.log` (UTC) queda como lo escribe PythonAnywhere.
- No se cambia código ni configuración, y no hay `v1.2`.
- Resuelto en la sección 3 de `registro-pendientes.md`.

**Documentos corregidos:**
- **RDA-013:** texto de la decisión y actualización fechada.
- **RDA-005:** la actualización del 2026-10-25.
- **`iteracion-01-02`:** resultado de la hipótesis, en el estado.
- **`iteracion-01-06`:** fila de la 01-07 en la tabla de lo que se despliega, resultado de la tarea 6 y criterio del emoji.
- **`iteracion-01-07`:** «Fuera de alcance».
- **`docs/operacion/despliegue.md`:**
  - tabla de los dos archivos al inicio;
  - `L` apunta a `server.log`;
  - comandos con `TZ=America/Santiago`;
  - recuperación de saltos con `sed`;
  - aviso sobre el filtro por fecha de `error.log`.
- **Propuesta de regla 4 en `bitacora-01-03`:** reescrita. `AGENTS.md` no se tocó.

Los criterios que mencionan `error.log` y aún no se marcan (diagnóstico, duplicados, `fontTools` y `django.server`) se evalúan al integrar la parte C, con la lectura de arriba. `evidencia-01-06.md` no se editó.

### Lo que sigue sin confirmar

**Que `error.log` lo alimenta un manejador de `logging` propio de PythonAnywhere, instalado en el registrador raíz después de cargar la aplicación, sigue siendo una deducción.**
- Se apoya en el formato distinto de `error.log` y en que recibe registros de `pedidos.decorators` y de `django.request`.
- No se comprobó dentro del proceso web, y la documentación encontrada no lo describe.
- Con la opción A no hace falta confirmarlo: el diagnóstico no depende de ese manejador.
- Si PythonAnywhere lo quitara o lo cambiara, `error.log` dejaría de recibir los errores, pero `server.log` seguiría teniéndolos.

## Capturas amplias y regla 4 (registradas, sin asignar)

- **Revisión del 2026-10-25:** hay 8 `except Exception` fuera de `registro.py` y `eventos.py`, y ningún `except:` sin tipo ni `except BaseException`.
  - `decorators.py:20` y `views.py:193` registran el error con `logging` y cumplen la regla 4 vigente.
  - Las otras 6 no la cumplen.
- **Ya registradas, se enlazan:**
  - `views.py:270`, `:766` y `:810` (`pass` al guardar ítems): AUD-01-002.
  - `views.py:1128` (`generar_respaldo_bd`, `str(e)` al navegador): AUD-02-006.
- **Nuevas:** `views.py:1168` y `:1191` (`restaurar_bd`). No registran el error y muestran `str(e)` al usuario.
- Las seis quedaron en la sección 3 del registro como `PENDIENTE_DESARROLLADOR`, sin proponer corrección ni iteración.

## Decisiones abiertas del desarrollador

1. **Comentarios de código que siguen diciendo «error.log».** El comentario del bloque `LOGGING` en `settings.py` dice:
   - «Todo va a stderr, que PythonAnywhere guarda en error.log»;
   - «Configurar la raíz reemplaza cualquier manejador previo del entorno y evita líneas dobles».

   Lo segundo quedó desmentido en producción. `decorators.py`, `views.py:194` y `eventos.py` también dicen «queda en error.log». El código funciona, pero los comentarios ya no describen la opción A. Cambiarlos toca `settings.py`, que requiere consulta. ¿Se corrigen, y en qué iteración?
2. **Usuario escrito en la evidencia.** C5 de `evidencia-01-06.md` nombra al usuario con el que se hizo la prueba de acceso (en la tabla y en la descripción de la prueba). Si es el nombre de una persona, choca con la regla 7.4 de `AGENTS.md` (sin datos personales en la documentación). No edité la evidencia: ¿lo reemplazas por «usuario #1» o lo dejas porque es tu propio usuario técnico?
3. **Asignación de las 6 capturas amplias** (sección 3 del registro).
4. **Parte D:** medición del domingo 2026-11-01. Con ella se marca el último criterio y la 01-06 pasa a `En revisión`.
