# Bitácora 01-06 · Producción: despliegue y validación de la observabilidad

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado:** en curso. Partes A y B completadas por el desarrollador; B8 con la parte del agente lista; C y D en curso. La evidencia completa de la parte C se integra cuando el desarrollador la entregue.

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
