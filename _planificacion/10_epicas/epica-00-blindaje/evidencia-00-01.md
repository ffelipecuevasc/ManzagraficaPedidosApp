# Evidencia 00-01 · Línea base de producción

- **Fecha del pedido:** 2026-10-20
- **Pedido por:** Claude Code (Sonnet 5.5)
- **Criterios que dependen de esta evidencia:** todas las cifras de `00_producto/linea-base-produccion.md` (iteración 00-01, criterio 3) y el resultado medido de AUD-01-006, AUD-02-004, AUD-02-007 y AUD-02-010 (criterio 5).

> Este archivo existe solo porque el agente no pudo obtener estos datos por su cuenta. Responde solo lo que se pide.

## Qué intentó el agente

| Dato | Qué intentó en local | Por qué se necesita producción |
| :--- | :------------------- | :----------------------------- |
| Filas de `HistorialBD`, peso de la base, filas por tabla, estados de pago, gráfico anual | Escribí `scripts/diagnostico/linea_base.sql` con los nombres de `pedidos/models.py`. No pude ejecutarlo: el MySQL local no está encendido (conexión rechazada en `127.0.0.1:3306`, error 2002 al correr `makemigrations --check --dry-run`) y la réplica local aún no existe (iteración 00-03). | Aunque hubiera una base local, tendría datos de desarrollo, no los de producción. |
| Versión de MySQL, conjunto de caracteres, colación, zona horaria, tablas de zona horaria cargadas | Lo mismo: sin MySQL local accesible. | Son parámetros del servidor MySQL de PythonAnywhere. |
| Disco de la cuenta, `backups/`, `media/`, Python del entorno, `pip freeze` | Escribí `scripts/diagnostico/linea_base.sh` y lo probé contra una carpeta simulada (rutas, un `requirements.txt` en UTF-16 LE y un `pip` de prueba). | El agente no accede a PythonAnywhere (`AGENTS.md`, sección 6) y no abre los respaldos. |
| Clave secreta de producción | Calculé con `git show 713260c:PedidosApp/settings.py` el hash SHA-256 de la clave de ese commit y probé el fragmento con claves de prueba. | Saber qué clave usa producción exige ver su configuración. |
| Tarea programada, expiración de la web app, uso de disco del panel | Revisé la documentación del proyecto: no registra estos datos. | Solo se ven en el panel de PythonAnywhere. |
| Desconexiones y peticiones a `/robots.txt` | Probé los comandos de conteo contra registros simulados. | Son los registros reales del servidor. |

## Qué necesito del desarrollador

Antes de empezar:

- **Cuota de CPU.** Cada consola que abres consume la cuota diaria de **100 segundos de CPU** compartida entre consolas y tareas programadas. El guion SQL es liviano. Lo más costoso es `du` sobre `$HOME` (el entorno virtual tiene muchos archivos) y la lectura de los registros. No medí el consumo en producción. Si te preocupa la cuota, haz los pasos 1 a 3 un día y el 5 otro, o mira el indicador de CPU del Dashboard antes y después. Cierra cada consola al terminar.
- **Datos personales.** Todos los comandos devuelven solo conteos, tamaños, fechas y nombres de archivo. No pegues líneas completas del registro de accesos (tienen direcciones IP) ni nada que no sea la salida de estos comandos.
- **No modifiques nada** en el servidor para esta medición. En particular, no pulses el botón que extiende la vigencia de la web app (paso 4) hasta haber anotado la fecha de expiración.

Orden recomendado: 1 → 2 → 3 → 5 (las tres últimas, en la misma consola Bash) → 4. Anota también el uso de CPU del Dashboard antes y después.

### 1. Guion SQL (consola MySQL de PythonAnywhere)

- **Para qué:** criterios de `HistorialBD` (días distintos, máximo por día), peso de la base, filas por tabla de negocio, parámetros de MySQL, tablas de zona horaria, gráfico anual y `estado_pago` inconsistente. Cierra con medición AUD-01-006, AUD-02-004 y AUD-02-007.
- **Cómo obtenerlo:**
  1. En PythonAnywhere, abre la pestaña **Databases** e inicia la consola MySQL de la base de la aplicación (enlace del tipo *Start a MySQL console*).
  2. En PyCharm abre `scripts/diagnostico/linea_base.sql`, selecciona todo y cópialo.
  3. Pégalo completo en la consola y pulsa Enter. Son 14 resultados; el primer campo de cada uno (`seccion`) los identifica: `0`, `1a`, `1b`, `2a`, `2b`, `2c`, `3`, `4`, `5`, `6a`, `6b`, `6c`, `7a`, `7b`.
  4. Si la consola corta el texto pegado, pega el archivo por bloques (cada bloque termina en `;`).
  5. Copia toda la salida y pégala abajo.
- **Respuesta:**

```text
(pega aquí la salida completa del guion SQL)
```

### 2. Guion Bash (consola Bash de PythonAnywhere)

- **Para qué:** disco de la cuenta frente a los 512 MiB, número, tamaño y antigüedad de los volcados de `backups/`, tamaño de `media/`, versión de Python del entorno y diferencias entre `pip freeze` y `requirements.txt`.
- **Cómo obtenerlo:**
  1. Abre una consola **Bash** nueva (pestaña **Consoles**).
  2. Averigua dos rutas. La del proyecto es la carpeta que contiene `manage.py`. La del entorno virtual está en la pestaña **Web**, campo *Virtualenv*.
  3. Abre `scripts/diagnostico/linea_base.sh` en PyCharm y reemplaza `PENDIENTE_DESARROLLADOR` en las dos líneas `PROYECTO=` y `VENV=` (solo en lo que vas a pegar, no en el repositorio).
  4. Copia todo y pégalo en la consola. Si las rutas están mal, el guion lo dice y no hace nada más.
  5. Copia la salida completa y pégala abajo.
  6. Si la consola corta el texto pegado, crea el archivo desde la pestaña **Files** con el mismo contenido, ejecútalo con `bash linea_base.sh` y bórralo al terminar.
- **Respuesta:**

```text
(pega aquí la salida completa del guion Bash)
```

### 3. Clave secreta sin revelarla (AUD-02-010)

- **Para qué:** responder dos preguntas con `True` o `False`: si la clave de producción empieza con `django-insecure-` y si coincide con la clave escrita en el commit inicial `713260c`. No imprime la clave.
- **Hash SHA-256 de la clave del commit `713260c`:** `9f959802c17ec6798c581b354b11b3244aa0b7aed5e6f9178d64d015a22f745a` (calculado por el agente con `git show`; la clave no está copiada en ningún archivo).
- **Cómo obtenerlo:** en la **misma consola Bash del paso 2** (las variables `PROYECTO` y `VENV` siguen definidas), pega:

```bash
cd "$PROYECTO" && source "$VENV/bin/activate" && python - <<'PY'
import hashlib
import os

HASH_713260C = "9f959802c17ec6798c581b354b11b3244aa0b7aed5e6f9178d64d015a22f745a"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PedidosApp.settings")
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

try:
    clave = settings.SECRET_KEY
except ImproperlyConfigured:
    print("SIN CLAVE: esta consola no ve la variable SECRET_KEY")
else:
    print("empieza con django-insecure-:", clave.startswith("django-insecure-"))
    print("coincide con la del commit 713260c:", hashlib.sha256(clave.encode("utf-8")).hexdigest() == HASH_713260C)
PY
deactivate
```

  Notas: no agregues un `print(clave)`. Si responde `SIN CLAVE`, la clave de producción no llega por el `.env` del proyecto (quizá la entrega la configuración de la web app). En ese caso no hay respuesta válida con este método: anótalo y dime dónde se define, sin copiar su valor.
- **Respuesta:**

```text
(pega aquí las dos líneas True/False, o SIN CLAVE)
```

### 4. Panel de PythonAnywhere: tarea programada, expiración y disco

- **Para qué:** «tarea programada disponible», «fecha de expiración de la web app y procedimiento de renovación» y el uso de disco que informa el panel. La tarea programada decide dónde corre la orden de mantención diaria de la épica 06. La expiración alimenta 07-01.
- **Cómo obtenerlo (el panel está en inglés; si un texto difiere, copia el que veas):**
  1. **Tasks:** anota si la cuenta tiene una tarea programada configurada (hora y, sin copiar comandos, si es de un solo día o diaria) y si el panel permite crear una. El plan gratuito incluye una tarea diaria.
  2. **Web:** busca el aviso de expiración de la web app y anota la fecha exacta. Copia el texto exacto del botón o enlace de extensión y escribe los pasos que sigues para renovarla (qué pulsar y cada cuánto). **No lo pulses antes de anotar la fecha.**
  3. **Dashboard:** anota el indicador de uso de disco del panel (valor y límite) y, si aparece, el uso de CPU del día.
- **Respuesta:**

```text
Tarea programada disponible (sí/no):
Detalle (hay una configurada, hora, si el panel deja crear otra):
Fecha de expiración de la web app (AAAA-MM-DD):
Texto exacto del botón o enlace de extensión:
Procedimiento de renovación (pasos y frecuencia):
Uso de disco que muestra el panel (valor y límite):
Uso de CPU del Dashboard antes y después de los pasos (si aparece):
```

### 5. Registro del servidor: desconexiones y `/robots.txt` de los últimos siete días

- **Para qué:** línea base de desconexiones y de peticiones a `/robots.txt`, que 00-06 compara después del despliegue con el mismo método.
- **Cómo obtenerlo:** en la **misma consola Bash**, pega la función y luego escribe `contar_logs`. Cuenta por archivo de registro: el servidor guarda copias rotadas y cada una trae su fecha de modificación. Así no hay que interpretar el formato de fecha de cada línea.

```bash
contar_logs() {
    local dominio="manzagrafica.pythonanywhere.com" dir="${DIR_LOGS:-/var/log}" f m
    echo "--- Registro de accesos: peticiones a /robots.txt por archivo ---"
    for f in $(ls -1t "$dir/$dominio".access.log* 2>/dev/null); do
        m=$(stat -c '%y' "$f" | cut -c1-16)
        zcat -f "$f" | awk -v a="$(basename "$f")" -v m="$m" '
            /GET \/robots\.txt/ { r++ }
            { n++ }
            END { printf "%s | modificado %s | lineas=%d | robots_txt=%d\n", a, m, n, r }'
    done
    echo "--- Registro del servidor: desconexiones por archivo ---"
    for f in $(ls -1t "$dir/$dominio".server.log* 2>/dev/null); do
        m=$(stat -c '%y' "$f" | cut -c1-16)
        zcat -f "$f" | awk -v a="$(basename "$f")" -v m="$m" '
            /Broken pipe/ { bp++ }
            /write error/ { we++ }
            /SIGPIPE|closed (pipe|socket|fd)/ { sp++ }
            { n++ }
            END { printf "%s | modificado %s | lineas=%d | broken_pipe=%d | write_error=%d | sigpipe_o_cerrado=%d\n", a, m, n, bp, we, sp }'
    done
    echo "--- Mensajes mas repetidos del registro del servidor (digitos reemplazados por N) ---"
    zcat -f "$dir/$dominio".server.log* 2>/dev/null \
        | grep -iE 'error|broken|pipe|timeout|disconnect|closed' \
        | sed -E 's/[0-9]+/N/g' | cut -c1-90 | sort | uniq -c | sort -rn | head -10
}
contar_logs
```

  Notas:
  - La ruta `/var/log/<dominio>.access.log` y `.server.log` es la habitual de PythonAnywhere; confírmala con los enlaces de registro de la pestaña **Web** (*Access log*, *Server log*). Si son otras, cambia `dir` y `dominio`.
  - Tres cosas del método **no están verificadas** contra producción: que el registro del servidor rote a diario (cada archivo sea un día), que una «desconexión» se escriba como `Broken pipe`, `write error` o `SIGPIPE`, y que no existan otras variantes. La última sección del comando (los mensajes más repetidos) sirve para comprobarlo: si la desconexión que viste en el registro no aparece ahí, dímelo y ajusto el patrón en la bitácora de producción.
  - Los siete días se arman con las filas cuya fecha de modificación esté dentro del periodo. Pega todas las filas; yo calculo la suma.
- **Respuesta:**

```text
(pega aquí la salida completa de contar_logs: solo contiene conteos y nombres de archivo)
```

## Lo que no se pudo verificar

- Que `linea_base.sql` se ejecute sin errores: el MySQL local no está encendido (conexión rechazada). Queda «sin ejecutar» hasta que lo enciendas y me autorices a correrlo.
- El método de conteo de desconexiones (nota del paso 5).
- Qué clave usa realmente producción si resulta que la consola no la ve (paso 3).
- Las rutas del proyecto y del entorno virtual en PythonAnywhere (`PENDIENTE_DESARROLLADOR`): el guion las toma de las dos variables del inicio.

## Respuesta del desarrollador (registrada el 2026-10-20)

El desarrollador ejecutó los pasos 1 a 5 el 2026-10-20 (UTC) y pegó en la conversación con el agente la salida ya procesada de las consolas y del panel de PythonAnywhere. Por la regla de datos personales **no se copian aquí registros crudos**: ni líneas del registro de accesos (tienen IP y agente), ni la clave, ni rutas con datos de clientes. Las cifras quedaron en `00_producto/linea-base-produccion.md` y el análisis en `99_bitacora/epica-00-blindaje/bitacora-00-01-produccion.md`.

| Paso | Respondido | Observación |
| :--- | :--------- | :---------- |
| 1. Guion SQL | Sí | 14 secciones. |
| 2. Guion Bash | Sí | La salida contó `.gitkeep` como volcado (6 en vez de 5, antigüedad del más antiguo mal calculada). El desarrollador corrigió los valores a mano y el guion ya excluye `.gitkeep`. |
| 3. Clave | Sí | `False` / `False`. |
| 4. Panel | Sí | Sin tarea programada creada; expiración 2026-11-20 (`PENDIENTE_DESARROLLADOR`: confirmar si viene de una renovación del mismo día). El uso de CPU antes y después no se informó. |
| 5. Registros | Sí, con un ajuste | El conteo por archivo no sirve para «7 días» porque los archivos rotan de forma irregular. Se contó por fecha de cada línea (método siguiente). |

Pendiente de la evidencia: el tamaño de `backups/` completo con subcarpetas y el desglose de datos e índices por tabla no vinieron en la respuesta; quedan como `PENDIENTE_DESARROLLADOR` en la línea base.

## Método reutilizable para 00-06: conteo por fecha

**Por qué:** los registros rotados de PythonAnywhere no cubren un día cada uno (`server.log` cubría 89 días; `access.log` empezaba el 2026-10-15 a las 09:03). Contar por archivo mezcla periodos. Se cuenta por la fecha escrita en cada línea, sobre todos los archivos (planos y `.gz`).

**Ventana:** siete días completos en UTC, más una ventana larga (todos los días que cubra el registro) para calcular la tasa diaria. En 00-06 se usa la misma ventana después del despliegue y se compara la tasa diaria, no el total.

**Registro de accesos** (formato verificado: `IP - - [dd/Mon/aaaa:hh:mm:ss +0000] "GET /robots.txt HTTP/1.1" 404 ...`). Pega en una consola Bash; imprime solo la fecha, el código de respuesta y el conteo:

```bash
contar_robots_por_dia() {
    local dir="${DIR_LOGS:-/var/log}" dominio="manzagrafica.pythonanywhere.com"
    zcat -f "$dir/$dominio".access.log* 2>/dev/null \
        | awk '/"GET \/robots\.txt/ {
                 split($0, a, "[][]"); split(a[2], f, ":");   # f[1] = dd/Mon/aaaa
                 split($0, b, "\""); split(b[3], c, " ");      # c[1] = codigo de respuesta
                 n[f[1] " " c[1]]++ }
               END { for (k in n) print k, n[k] }' \
        | sort -t/ -k3,3 -k2,2M -k1,1n
}
contar_robots_por_dia
```

**Registro del servidor:** la misma idea con los patrones verificados en 00-01, `Broken pipe` y `SIGPIPE|closed (pipe|socket|fd)`, agrupando por la fecha de cada línea. El formato de fecha de las líneas del registro del servidor **no quedó registrado** en la evidencia: `PENDIENTE_DESARROLLADOR`, guardar en `evidencia-00-06.md` el bloque exacto que se usó el 2026-10-20 para que la comparación use el mismo método.

**Línea base contra la que compara 00-06** (detalle en `linea-base-produccion.md`, sección 8):

| Señal | Últimos 7 días (2026-10-15 a 2026-10-21 UTC) | Tasa en la ventana larga |
| :---- | :------------------------------------------- | :----------------------- |
| 404 de `/robots.txt` | 7 | unas 1,1 por día |
| `Broken pipe` | 4 | 0,44 por día (39 en 89 días) |
| `SIGPIPE` o cerrado | 12 | 152 en 89 días |
