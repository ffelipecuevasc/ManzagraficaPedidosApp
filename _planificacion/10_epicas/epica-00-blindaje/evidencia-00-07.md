# Evidencia 00-07 · Correcciones tempranas II

- **Fecha del pedido:** 2026-10-27
- **Pedido por:** Claude Code (Opus 5.5)
- **Criterios que dependen de esta evidencia:** lista de comprobación en el PC; `v1.2-capturas` sobre el último commit anterior a la 00-07 y `v0.3-doble-envio` sobre la punta de `main`; despliegue con etiqueta propia; «Nuevo pedido», «Editar pedido» y cotizaciones revisados en producción; sin pares de `POST /pedidos/nuevo/` en el mismo segundo durante la semana siguiente.

> Este archivo existe porque el agente no puede obtener estos datos por su cuenta. Responde solo lo que se pide.
>
> **Orden (decisión 5; fecha prevista ~~domingo 2026-11-01~~, ver la nota de abajo):** parte D de la 01-06 → [evidencia-01-09](../epica-01-observabilidad/evidencia-01-09.md) (incluye crear `v1.2-capturas`, equivalente a B1–B3) → despliegue y validación de `v1.2-capturas` → **B4** → **parte C** → una semana después del despliegue de esta iteración (~~2026-11-08~~), **parte D**. Si `v1.2-capturas` se retrocede, esta iteración se pospone y no se crea `v0.3-doble-envio`. (Corregido el 2026-10-27.)
>
> **Nota (2026-11-04):** la parte D de la 01-06 se midió el 2026-11-03 y `v1.2-capturas` se desplegó y validó el 2026-11-04 (reinicio efectivo de uWSGI a las 00:11:49, hora de Chile; [evidencia-01-09](../epica-01-observabilidad/evidencia-01-09.md)), no el 2026-11-01 previsto. **La condición para esta iteración quedó cumplida**, y la Épica 01 está terminada. ~~**B4 y la parte C esperan la indicación del desarrollador, sin fecha:** no se ejecutaron (la etiqueta `v0.3-doble-envio` no se crea hasta B4).~~ (Superado por la nota siguiente, del mismo día.) La fecha de la parte D será una semana después de ese despliegue, no el 2026-11-08. Conviene avisar a Manza Gráfica de la ventana. B1 a B3 ya no se repiten: `v1.2-capturas` existe sobre `81005df`.
>
> **Nota (2026-11-04, posterior): B4 y la parte C se ejecutaron esa noche.** `v0.3-doble-envio` (objeto `e68f87212245679d68ba8340db46cd9c3218419d`) se creó y publicó sobre `5dc82a8` y se desplegó con **reinicio efectivo a las 01:32:51** (hora de Chile, la oficial; decisión 5 del desarrollador). Validación sin retroceso. Las tablas de abajo tienen los datos; la **parte D (access.log) se mide el 2026-11-11, hacia las 01:32**. Consolidación en [bitacora-00-07-despliegue](../../99_bitacora/epica-00-blindaje/bitacora-00-07-despliegue.md).
>
> **Nota (2026-11-17): la 00-07 pasó a Terminada (decisión del desarrollador, dicha por él).** La medición de la parte D, hecha el 2026-11-16 hacia las 23:13, cumple: 12 de 13 días con registro y `segundos_repetidos=0` en todos. **Salvedad:** el 2026-11-08 (domingo) salió con `lineas=0` y no se sabe si fue falta de uso o de registro. Los datos son dichos por el desarrollador; el agente no vio la salida.
>
> **Nota (2026-11-16): la medición de la parte D no se hizo el 2026-11-11.** Lo dijo el desarrollador el 2026-11-16 (dato no verificado por el agente). La parte D **sigue siendo precondición de la 03-05** y se mide **antes del despliegue del martes 2026-11-17** (de 20:00 a 23:00, hora de Chile): hoy por la noche o mañana durante el día. Ya no son siete días: desde el reinicio efectivo del 2026-11-04 (01:32:51 de Chile, 04:32:51 UTC) pasan 12 días el 2026-11-16 y 13 el 2026-11-17. El guion se ajustó para cubrirlos (ver la parte D, «Ajuste del guion»). Verificado en GitHub el 2026-11-16: la etiqueta `v3.1-integridad` no existe y no hay commits posteriores a `a1653dd`; que producción siga en `v0.3-doble-envio` lo confirma el desarrollador en el servidor (`PENDIENTE_DESARROLLADOR`).
>
> ~~**Orden (domingo 2026-11-01, decisión 5):** parte D de la 01-06 → despliegue y validación de `v1.2-capturas` → **parte A** (si no se hizo antes) → **parte B** (etiquetas) → **parte C** (despliegue de `v0.3-doble-envio`) → una semana después, **parte D**.~~

## Qué intentó el agente

| Dato | Qué hizo en local | Por qué se necesita al desarrollador |
| :--- | :---------------- | :----------------------------------- |
| Lista de comprobación | `test pedidos`, `check` y `makemigrations --check` en la bitácora | El desarrollador la repite sobre el commit que etiqueta |
| Revisión en el navegador | Preparó los pasos en la bitácora | El agente no abre un navegador contra la réplica |
| Etiquetas, despliegue y conteo | Preparó los comandos | Etiquetas, `push`, PythonAnywhere y sus registros los maneja solo el desarrollador (`AGENTS.md`, sección 6) |

---

## Parte A · Lista de comprobación **[PC · PowerShell 7]**

Desde la raíz del repositorio, con `.venv` activo y `docker compose up -d`, sobre la punta de `main` con la 00-07 ya en commit.

```powershell
python manage.py test pedidos
$env:DEBUG = "False"; python manage.py check --deploy; Remove-Item Env:DEBUG
python manage.py check
python manage.py makemigrations --check --dry-run
```

| # | Comprobación | Esperado | Resultado |
| :- | :----------- | :------- | :-------- |
| 1 | Pruebas | `Ran 184 tests` y `OK (expected failures=19)` | **No repetidas el 2026-11-04, a propósito:** el código es idéntico al de `bd07f21`, sobre el que corrieron las dos ejecuciones del mismo día de la [evidencia-01-09](../epica-01-observabilidad/evidencia-01-09.md) (parte B): `Ran 184 tests`, `OK (expected failures=19)` en ambas (174,975 s y 283,578 s). El `diff` de `bd07f21` contra `main`, sin `_planificacion` ni `docs`, salió vacío |
| 2 | `check --deploy` | Solo las advertencias conocidas de `despliegue.md` (para 04-02 y 04-03); ningún `ERRORS` | **No repetido**, por el mismo motivo. Sobre `bd07f21` (evidencia-01-09, parte B): exactamente `W004`, `W008`, `W009`, `W012` y `W016`, sin `ERRORS` |
| 3 | `check` | `System check identified no issues (0 silenced).` | No informado en esta ejecución |
| 4 | Migraciones | `No changes detected` (la 00-07 no tiene migraciones) | No informado en esta ejecución (`makemigrations --check`); sobre `bd07f21`, `No changes detected`. La ausencia de migraciones se comprobó en el servidor: `migrate --plan` sin operaciones y `diff` de `pedidos/migrations` entre `v1.2-capturas` y `v0.3-doble-envio` vacío |
| 5 | Respaldo | No aplica: no toca datos ni esquema y no es el primer despliegue de una fase | No se hizo un respaldo nuevo por ese motivo; el último verificado es `respaldo_04-11-2026_00-12-37.sql` (19 de 19, `VÁLIDO`) |
| 6 | Estilos compilados | No aplica | No aplica |

## Parte B · Etiquetas (el domingo, después de validar `v1.2-capturas`) **[PC · PowerShell 7]**

> **B1 a B3 se hacen en la [evidencia-01-09](../epica-01-observabilidad/evidencia-01-09.md) (parte C), antes de desplegar `v1.2-capturas`:** `v1.2-capturas` va sobre `81005df`, el commit anterior a `4560874` (el primero que cambia `pedido_form.html`). El día del despliegue de la 00-07 solo se ejecuta **B4**. B1 a B3 quedan aquí como referencia. (Corregido el 2026-10-27.)
>
> ~~Si `v1.2-capturas` ya se creó y desplegó antes (procedimiento de la 01-09), salta B3 y comprueba en B2 que `v1.2-capturas` es el commit anterior a la 00-07.~~

### B1. Ubicar el último commit anterior a la 00-07

```powershell
git status --short
git fetch origin
git status -sb
git log --oneline -n 15
git log --oneline -n 3 -- pedidos/templates/pedidos/pedido_form.html
```

- `git status --short` vacío y `git status -sb` con `## main...origin/main` sin `[ahead N]` ni `[behind N]`.
- El segundo `log` muestra el commit de la 00-07 que cambia `pedido_form.html` (el más reciente). **El hash que se busca es el commit inmediatamente anterior a ese, en el primer `log`.** Los commits solo de documentos marcados «00-07» (por ejemplo, el registro de la Auditoría 04) no cambian código: da igual que queden dentro o fuera de `v1.2-capturas`, y B2 lo confirma.
- Anota el hash: `$BASE_V12 = "<hash>"` (solo el hash, sin `<` ni `>`).

### B2. Comprobar que entre ese commit y la punta solo cambia la 00-07

```powershell
git diff --stat $BASE_V12..main
git diff --stat $BASE_V12..main -- . ":(exclude)_planificacion" ":(exclude)docs"
```

- **Esperado:** el segundo comando lista **solo** `pedidos/templates/pedidos/pedido_form.html`. El primero suma archivos de `_planificacion/` (y `docs/` si se aplicaron las propuestas de la bitácora).
- Si aparece otro archivo ejecutable (código, plantillas, estáticos, `settings.py`, `requirements.txt`), **detente**: ese cambio no es de la 00-07 y viajaría en `v0.3-doble-envio`.

### B3. Crear `v1.2-capturas` sobre ese commit

```powershell
$hoy = Get-Date -Format "yyyy-MM-dd"
git tag -a v1.2-capturas $BASE_V12 -m "Iteraciones 01-09, 01-08 y 01-07 · desplegada el $hoy"
git tag -n v1.2-capturas
git push origin v1.2-capturas
git ls-remote --tags origin v1.2-capturas
```

- El mensaje toma la fecha del día de `$hoy`; no se escribe a mano. Revisa `git tag -n` **antes** del `push`: si está mal, `git tag -d v1.2-capturas` y créala otra vez (todavía no está publicada).
- `ls-remote` devuelve una línea.

### B4. Crear `v0.3-doble-envio` en la punta de `main`

```powershell
$hoy = Get-Date -Format "yyyy-MM-dd"
git tag -a v0.3-doble-envio main -m "Iteración 00-07 · desplegada el $hoy"
git tag -n v0.3-doble-envio
git rev-parse --short "v0.3-doble-envio^{commit}"
git rev-parse --short main
git push origin v0.3-doble-envio
git ls-remote --tags origin v0.3-doble-envio
```

- Los dos `rev-parse` dan el mismo hash. Mismo control de `git tag -n` antes del `push`.

| Dato | Valor |
| :--- | :---- |
| `$BASE_V12` (hash corto) | `81005df`, de la parte C de la evidencia-01-09 (B1 a B3 no se repitieron) |
| Salida de B2 (segundo comando) | `diff` de `v1.2-capturas..main` sin `_planificacion` ni `docs`: solo `pedido_form.html` (1 archivo, 41 inserciones, 3 eliminaciones) |
| `v1.2-capturas` → commit | `81005df` |
| `v0.3-doble-envio` → commit | `5dc82a8`, igual que `main` y `origin/main` (`5dc82a8976c0012e90cac8103ec444949edbe999`); objeto de la etiqueta anotada `e68f87212245679d68ba8340db46cd9c3218419d` |
| Mensajes de `git tag -n` | Mensaje informado: «Iteración 00-07 · desplegada el 2026-11-04». `ls-remote` devolvió una línea (publicada) |

Comprobaciones previas en el PC, informadas: `git status --short` vacío y `main` igual a `origin/main`. La salida literal de `git tag -n` y la de los dos `rev-parse` no se informaron; el desarrollador resumió que la etiqueta quedó sobre `5dc82a8`.

## Parte C · Despliegue y validación (después de validar `v1.2-capturas`)

### C1. Traer la etiqueta **[PA · Bash]**

```bash
cd "$PROYECTO"; source "$VENV/bin/activate"
git status --short
git describe --tags
git fetch origin --tags
git checkout v0.3-doble-envio
git describe --tags
git diff --stat v1.2-capturas v0.3-doble-envio -- . ":(exclude)_planificacion" ":(exclude)docs"
```

- Antes del `checkout`: `git status --short` vacío y `git describe --tags` responde `v1.2-capturas`.
- Después: `git describe --tags` responde `v0.3-doble-envio` y el último `diff` lista solo `pedido_form.html`.
- Nunca `git pull`.

### C2. Sin migraciones ni estáticos **[PA · Bash]**

```bash
python manage.py migrate --plan
git diff --stat v1.2-capturas v0.3-doble-envio -- pedidos/static requirements.txt
```

- `migrate --plan` → `No planned migration operations.`. El `diff` no muestra nada: **sin `collectstatic`, sin `pip install` y sin `migrate`**.

### C3. Recargar **[PA · Panel]**

Pestaña **Web** → **Reload**. Anota la hora (Chile). Recuerda que la recarga deja unos 10 s de 502 (AUD-04-002).

### C4. Revisión **[Navegador]**

En una ventana privada, con sesión iniciada. **No crees pedidos de prueba en producción** salvo que lo decidas; esta revisión solo mira.

1. «Nuevo pedido» (`/pedidos/nuevo/`): el botón «Crear Pedido» se ve igual que antes.
2. «Editar pedido» (abre uno desde el listado y entra a editar, sin guardar): el botón se ve igual.
3. «Nueva cotización»: sin cambios.
4. Registro de `server.log` después de la recarga con el bloque de `despliegue.md`, sección 3.7: ninguna línea `nivel=ERROR` nueva.

| Revisión | Resultado |
| :------- | :-------- |
| C1 (`describe` y `diff`) | Antes: prompt «(HEAD detached at v1.2-capturas)», `git status --short` vacío, `describe` = `v1.2-capturas`. `fetch --tags` trajo `bd07f21..5dc82a8` y la etiqueta. Después: HEAD en `5dc82a8`, `describe` = `v0.3-doble-envio`. El `diff` de `pedidos/templates` entre `v1.2-capturas` y `v0.3-doble-envio` lista solo `pedido_form.html` |
| C2 (`migrate --plan` y `diff`) | `migrate --plan`: «No planned migration operations.» (con la advertencia conocida `mysql.W002`). Los `diff --stat` de `requirements.txt`, `pedidos/static` y `pedidos/migrations`: vacíos. Sin `pip`, sin `collectstatic` y sin `migrate` |
| C3 hora de recarga (Chile) | **Oficial: 01:32:51**, la del reinicio efectivo (`Starting uWSGI`, prefijo en hora de Chile; decisión 5 del desarrollador). Orden de Reload recibida a las 01:32:45 («received message 0 from emperor»). El mensaje interno de uWSGI dice 04:32:50 UTC (01:32:50 en Chile). El reloj de la consola de PythonAnywhere marca UTC, Chile + 3 h |
| C4.1 Nuevo pedido | Abre y muestra el cambio, en ventana privada. No se envió ningún formulario |
| C4.2 Editar pedido | Abre y muestra el cambio, en ventana privada. No se envió ningún formulario |
| C4.3 Nueva cotización | No informado |
| C4.4 `server.log` | Conteo por `nivel=` desde el reinicio (01:32:51): 0 líneas |

También se abrieron acceso, panel, listado de pedidos y detalle de un pedido, sin problemas; no se usó «Estadísticas». **Retroceso no necesario.**

> **Observación (2026-11-04):** los textos de C4.1 y C4.2 dicen que el botón «se ve igual que antes», anteriores a la decisión 7 de la iteración (el botón dice «Editar Pedido» al editar). Lo informado es «muestran el cambio»; no se detalló qué botón ni qué texto se vio.

## Parte D · Una semana después **[PA · Bash]**

> **Reprogramada el 2026-11-16.** ~~Se medía el 2026-11-11, hacia las 01:32.~~ No se hizo (dicho por el desarrollador). Se mide **antes del despliegue de la 03-05** (martes 2026-11-17, de 20:00 a 23:00 de Chile): hoy 2026-11-16 por la noche o el 2026-11-17 durante el día, y se anota **antes de empezar cualquier paso de la 03-05** (parte A1 de la [evidencia-03-05](../epica-03-integridad-transaccional/evidencia-03-05.md); la 03-05 está bloqueada hasta entonces). El límite duro es el Reload (B6): si se midiera después de él, el día UTC del 2026-11-17 mezclaría la 03-05 (con ella, un envío repetido también responde 302): no se hace así. Medir con más días no debilita el criterio: lo hace más exigente.

### Ajuste del guion (2026-11-16)

El guion original (más abajo) recorre `for i in 7 6 5 4 3 2 1 0`: mira solo los 8 últimos días UTC contados desde hoy. Medido el 2026-11-16 o el 11-17, dejaría fuera los primeros días después del despliegue (del 2026-11-04 al 11-08 o al 11-09). El guion nuevo:

- parte de la fecha UTC del despliegue (`INI=2026-11-04`) y llega hasta la fecha UTC de hoy, sea cual sea (desde las 21:00 de Chile la fecha UTC ya es la del día siguiente);
- agrega `lineas=` (todas las peticiones del día), para distinguir un día sin `POST` de un día sin registro;
- lee los archivos **una vez por día** en lugar de dos filtros encadenados (cada `zcat` recorre el archivo actual y los rotados);
- sigue sin imprimir IP, cadena de consulta ni datos de clientes: solo fechas y conteos.

**D0 y D1 [PA · Bash]:**

```bash
cd /var/log; D=manzagrafica.pythonanywhere.com
ls -l --time-style=long-iso $D.access.log*

INI=2026-11-04
N=$(( ( $(date -u +%s) - $(date -u -d "$INI" +%s) ) / 86400 ))
for k in $(seq 0 $N); do
  f=$(date -u -d "$INI +$k day" +%F); d=$(LC_ALL=C date -u -d "$INI +$k day" +%d/%b/%Y)
  L=$(zcat -f $D.access.log* | grep "\[$d:")
  lineas=$(printf '%s\n' "$L" | grep -c .)
  printf '%s\n' "$L" | grep '"POST /pedidos/nuevo/ ' \
    | sed -E 's/^[^[]*\[([^ ]+) .*/\1/' \
    | sort | uniq -c \
    | awk -v d="$f" -v l="$lineas" '{t+=$1; if ($1>1) {p++; e+=$1-1}} END {printf "%s lineas=%d post_nuevo=%d segundos_repetidos=%d envios_extra=%d\n", d, l, t, p, e}'
done
```

**D2 [PA · Bash], solo si el 2026-11-04 sale con `segundos_repetidos` mayor que 0:** imprime las horas UTC (sin IP) de esos segundos, para ver si caen antes o después del reinicio efectivo (04:32:51 UTC).

```bash
zcat -f $D.access.log* | grep '\[04/Nov/2026:' | grep '"POST /pedidos/nuevo/ ' | sed -E 's/^[^[]*\[[^:]+:([^ ]+) .*/\1/' | sort | uniq -c | awk '$1>1'
```

**Cómo se lee:**

- Una línea por día UTC, del 2026-11-04 a hoy. **Esperado:** `segundos_repetidos=0` en todas. El primer día mezcla unas 4,5 h anteriores al despliegue (las anteriores a 04:32:51 UTC no cuentan: D2 las separa) y el último llega solo hasta la hora de la medición.
- `lineas=0` en un día es sospechoso (registro faltante por la rotación, o sin tráfico): compara con D0 (nombre, tamaño y fecha de cada archivo). Si D0 no muestra archivos que cubran un día, anota cuáles días quedan sin medir y no concluyas nada de ellos. Cuántos días conserva la rotación no está documentado (`PENDIENTE_DESARROLLADOR`: D0 lo muestra).
- El guion nuevo hace 14 lecturas de los archivos (el original, 8). El consumo de CPU no se midió: si la consola se acerca a su cuota diaria de 100 s, corta el bucle y córrelo por tramos cambiando `INI` y `N`.
- Se probó solo con registros sintéticos (un archivo actual, uno rotado sin comprimir y uno `.gz`, 14 días, con GNU `date`, `grep`, `sed` y `awk` de Git Bash): no contra el servidor ni contra el formato real de `access.log`.

### Guion original (2026-10-27; referencia, no usar: solo cubre 8 días)

Cuenta, por día en UTC, los `POST /pedidos/nuevo/` y los segundos con dos o más de ellos. Solo imprime fechas y conteos: ninguna IP, cadena de consulta ni dato de cliente.

```bash
cd /var/log; D=manzagrafica.pythonanywhere.com
for i in 7 6 5 4 3 2 1 0; do
  d=$(LC_ALL=C date -u -d "-$i day" +%d/%b/%Y)
  zcat -f $D.access.log* | grep '"POST /pedidos/nuevo/ ' | grep "\[$d:" \
    | sed -E 's/^[^[]*\[([^ ]+) .*/\1/' \
    | sort | uniq -c \
    | awk -v d="$d" '{t+=$1; if ($1>1) {p++; e+=$1-1}} END {printf "%s post_nuevo=%d segundos_repetidos=%d envios_extra=%d\n", d, t, p, e}'
done
```

- `segundos_repetidos`: segundos con dos o más `POST /pedidos/nuevo/`. `envios_extra`: cuántos sobran en esos segundos.
- El día de la recarga mezcla antes y después: indícalo. **Esperado** después del despliegue: `segundos_repetidos=0`. ~~**Fecha de medición: 2026-11-11, hacia las 01:32** (hora de Chile; una semana después del reinicio efectivo, 01:32:51 del 2026-11-04). Esa hora es 04:32 UTC, y el reinicio fue a las 04:32:51 UTC del 2026-11-04: el día UTC del 2026-11-04 mezcla unas 4,5 h anteriores al despliegue, y el del 2026-11-11 llega solo hasta las 04:32 UTC.~~ **Fecha de medición (2026-11-16): antes del despliegue de la 03-05** (ver el recuadro de arriba). Sigue valiendo que el reinicio fue a las 04:32:51 UTC del 2026-11-04 y que el día UTC del 2026-11-04 mezcla unas 4,5 h anteriores al despliegue.
- Un `segundos_repetidos` mayor que 0 no prueba un duplicado (dos personas pueden crear pedidos en el mismo segundo), pero con un solo usuario es la señal que se busca: anótalo y no copies la línea del registro.

| Salida (pegar tal cual) |
| :---------------------- |
| ~~Pendiente: se mide el 2026-11-11, hacia las 01:32~~ Pendiente (2026-11-16): se mide antes del despliegue de la 03-05 (2026-11-16 por la noche o 2026-11-17 durante el día). Pega aquí la salida de D0 (nombres, tamaños y fechas) y la de D1 |
| **Medida el 2026-11-16 hacia las 23:13 (hora de Chile; dicho por el desarrollador el 2026-11-17, no vi la salida).** 12 días con registro (2026-11-04 a 2026-11-16), todos con `segundos_repetidos=0`. El 2026-11-08 y el 2026-11-17 (UTC) salieron con `lineas=0`: **sin medir** (no se sabe si fue falta de uso o de registro; el 2026-11-17 UTC llegaba solo hasta las 02:13 UTC de la medición). D2 no hizo falta: el 2026-11-04 salió con 0. **Cumple.** No se informaron la salida de D0 (nombres, tamaños y fechas de los archivos, o sea cuántos días conserva la rotación) ni `post_nuevo` y `envios_extra` por día. |

## Lo que no se pudo verificar

- La revisión en el navegador contra la réplica: queda para el desarrollador (pasos en la bitácora).
- **Añadido el 2026-11-04:** el efecto del cambio en producción no se probó con un doble clic ni con un formulario enviado (la revisión solo miró, a propósito); lo mide la parte D. «Nueva cotización» (C4.3), `check` y `makemigrations` de esta ejecución, la salida literal de `git tag -n` y qué texto exacto mostraron los botones: no informados.

## Respuesta del desarrollador

Partes A a C respondidas el 2026-11-04 y consolidadas en las tablas de arriba. Puntos propios del despliegue:

- **Etiqueta:** `v0.3-doble-envio` anotada (objeto `e68f87212245679d68ba8340db46cd9c3218419d`) sobre `5dc82a8`, publicada; partida y destino de retroceso `v1.2-capturas`. Sin migraciones, sin `pip`, sin `collectstatic` y sin respaldo previo nuevo.
- **Pruebas y `check --deploy` no repetidos:** el código es idéntico al de `bd07f21`, sobre el que corrieron el 2026-11-04.
- **Recarga:** reinicio efectivo a las 01:32:51 (hora oficial); orden de Reload a las 01:32:45.
- **Validación:** seis pantallas abren y muestran el cambio, sin enviar formularios; 0 líneas con `nivel=` desde el reinicio; sin retroceso.
- **Falta (hasta el 2026-11-16; hecha ese día, ver la tabla de la parte D):** la parte D (solo `POST /pedidos/nuevo/` sin dos en el mismo segundo). ~~El 2026-11-11 hacia las 01:32.~~ No se hizo ese día; se mide antes del despliegue de la 03-05 del 2026-11-17, con el guion ajustado el 2026-11-16.
- **Cierre (2026-11-17, decisión del desarrollador, dicha por él):** la iteración pasa a **Terminada**. Medición del 2026-11-16: 12 de 13 días con registro y `segundos_repetidos=0` en todos; el 2026-11-08 (domingo) salió con `lineas=0` y no se sabe si fue falta de uso o de registro.
