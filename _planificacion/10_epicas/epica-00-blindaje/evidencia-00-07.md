# Evidencia 00-07 · Correcciones tempranas II

- **Fecha del pedido:** 2026-10-27
- **Pedido por:** Claude Code (Opus 5.5)
- **Criterios que dependen de esta evidencia:** lista de comprobación en el PC; `v1.2-capturas` sobre el último commit anterior a la 00-07 y `v0.3-doble-envio` sobre la punta de `main`; despliegue con etiqueta propia; «Nuevo pedido», «Editar pedido» y cotizaciones revisados en producción; sin pares de `POST /pedidos/nuevo/` en el mismo segundo durante la semana siguiente.

> Este archivo existe porque el agente no puede obtener estos datos por su cuenta. Responde solo lo que se pide.
>
> **Orden (domingo 2026-11-01, decisión 5):** parte D de la 01-06 → [evidencia-01-09](../epica-01-observabilidad/evidencia-01-09.md) (incluye crear `v1.2-capturas`, equivalente a B1–B3) → despliegue y validación de `v1.2-capturas` → **B4** → **parte C** → una semana después (2026-11-08), **parte D**. Si `v1.2-capturas` se retrocede, esta iteración se pospone y no se crea `v0.3-doble-envio`. (Corregido el 2026-10-27.)
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
| 1 | Pruebas | `Ran 184 tests` y `OK (expected failures=19)` | |
| 2 | `check --deploy` | Solo las advertencias conocidas de `despliegue.md` (para 04-02 y 04-03); ningún `ERRORS` | |
| 3 | `check` | `System check identified no issues (0 silenced).` | |
| 4 | Migraciones | `No changes detected` (la 00-07 no tiene migraciones) | |
| 5 | Respaldo | No aplica: no toca datos ni esquema y no es el primer despliegue de una fase | |
| 6 | Estilos compilados | No aplica | |

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
| `$BASE_V12` (hash corto) | |
| Salida de B2 (segundo comando) | |
| `v1.2-capturas` → commit | |
| `v0.3-doble-envio` → commit | |
| Mensajes de `git tag -n` | |

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
| C1 (`describe` y `diff`) | |
| C2 (`migrate --plan` y `diff`) | |
| C3 hora de recarga (Chile) | |
| C4.1 Nuevo pedido | |
| C4.2 Editar pedido | |
| C4.3 Nueva cotización | |
| C4.4 `server.log` | |

## Parte D · Una semana después **[PA · Bash]**

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
- El día de la recarga mezcla antes y después: indícalo. **Esperado** después del despliegue: `segundos_repetidos=0`.
- Un `segundos_repetidos` mayor que 0 no prueba un duplicado (dos personas pueden crear pedidos en el mismo segundo), pero con un solo usuario es la señal que se busca: anótalo y no copies la línea del registro.

| Salida (pegar tal cual) |
| :---------------------- |
| |

## Lo que no se pudo verificar

- La revisión en el navegador contra la réplica: queda para el desarrollador (pasos en la bitácora).

## Respuesta del desarrollador

_(Pendiente.)_
