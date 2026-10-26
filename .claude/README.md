# .claude · Permisos de Claude Code

`settings.json` define qué puede hacer Claude Code en este repositorio sin preguntar, qué debe consultar antes y qué tiene prohibido. Este README explica cada grupo de reglas. Ningún agente edita esta carpeta: la mantiene el desarrollador.

---

## 1. Cómo se resuelven las reglas

- Claude Code evalúa primero `deny`, luego `ask` y al final `allow`. La primera lista que calza decide, sin importar qué regla es más específica.
- Por eso una regla de `allow` nunca abre una excepción dentro de una de `ask` o `deny`. Ejemplo de este archivo: `Edit(/pedidos/**)` está en `allow`, pero `Edit(/pedidos/migrations/**)` está en `ask`, así que editar una migración siempre pregunta.
- Lo que no calza con ninguna regla queda en el comportamiento por defecto del modo de permisos activo (en el modo manual, Claude pregunta).
- Las rutas que empiezan con `/` se leen desde la raíz del proyecto. `**` cubre cualquier profundidad de carpetas.
- `Bash(comando *)` calza con el comando solo y con cualquier argumento detrás.
- `settings.local.json`, si existe, es personal: no se versiona y no debe usarse para relajar las reglas de `deny`.

## 2. `allow` · Sin consulta

| Regla | Por qué |
| :---- | :------ |
| `runserver`, `test`, `check`, `sqlmigrate`, `showmigrations` | Son los comandos de verificación de cada iteración y no modifican la base ni el repositorio. |
| `makemigrations --check --dry-run` | Detecta cambios de modelo sin migración y no crea archivos. |
| `python -m pip list` y `show` | Solo leen el entorno instalado. |
| `git status`, `diff`, `log`, `show`, `blame` | Lectura del historial, necesaria para entender el código. |
| Edición de `pedidos/`, `docs/`, `scripts/` y `_planificacion/` | Son las carpetas de trabajo de cada iteración. Las excepciones (`pedidos/migrations/` y `_planificacion/README.md`) las cubren `ask` y `deny`. |

## 3. `ask` · Requiere consulta

| Regla | Por qué |
| :---- | :------ |
| `makemigrations pedidos`, `migrate` | Crear o aplicar una migración es un cambio de esquema que debe clasificarse (Clase 1, 2 o 3) antes de existir. |
| `dbshell`, `shell`, `createsuperuser` | Abren acceso directo a los datos de la base local, que es una copia real de producción. |
| `collectstatic` | Escribe archivos estáticos generados en el disco. |
| `pip`, `pip install`, `pip uninstall` | Cada dependencia nueva pesa en el arranque en frío y en los 512 MiB del servidor. |
| `pnpm add`, `remove`, `update`, `install` | Igual que `pip`, y además cambia el archivo de bloqueo. |
| `docker` | Puede detener, borrar o recrear el contenedor con la réplica local de los datos. |
| `mysql`, `mysqldump` | Tocan la base directamente. La regla no puede distinguir entre la base local y la remota, así que siempre pregunta. |
| `git checkout`, `switch`, `branch`, `restore`, `stash` | El flujo es rama única `main`; además, `checkout` y `restore` pueden descartar cambios sin guardar. |
| `rm`, `mv` | Mover o borrar archivos requiere aprobación. |
| Edición de `pedidos/migrations/` | Una migración aplicada nunca se edita; una nueva se revisa con `sqlmigrate`. |
| Edición de `PedidosApp/`, `manage.py`, `requirements.txt`, `.gitignore`, `compose.yaml`, `package.json`, `pnpm-lock.yaml`, `tailwind.config.js` | Son archivos de configuración: un error en ellos rompe el arranque o el despliegue. `.env.example` ya no está aquí: su lectura y su edición están en `deny` (ver sección 4 y sección 5). |

## 4. `deny` · Prohibido

| Regla | Por qué |
| :---- | :------ |
| `git commit`, `push`, `merge`, `pull`, `rebase`, `reset`, `tag`, `cherry-pick`, `revert`, `filter-branch`, `filter-repo` | Publicar, etiquetar o reescribir el historial lo hace solo el desarrollador. Las etiquetas son el botón de retroceso de cada despliegue. |
| Las mismas reglas de Git con `PowerShell(...)` | En Windows, Claude Code puede usar PowerShell en vez de Bash; sin estas reglas, el mismo comando pasaría por la otra herramienta. |
| `ssh`, `scp`, `sftp`, `rsync`, `pa` | Son las vías de acceso a PythonAnywhere. El agente nunca toca producción. |
| `flush`, `sqlflush` | Vacían la base de datos. No hay caso de uso legítimo para un agente. |
| `npm`, `npx`, `yarn`, `pnpm dlx` | El único gestor de Node es pnpm con dependencias fijadas; los otros generan archivos de bloqueo distintos, y `npx` y `pnpm dlx` ejecutan paquetes descargados en el momento, sin versión fija. |
| Edición de `AGENTS.md`, `DESIGN.md`, `README.md` y `_planificacion/README.md` | Son los documentos inmutables: el agente propone cambios y el desarrollador los aplica. |
| Edición de `.claude/` y `.git/` | El agente no cambia sus propios permisos ni el repositorio interno de Git. |
| Lectura y edición de `.env` y de cualquier `.env.*`, incluido `.env.example`, en cualquier carpeta (`Read(**/.env)`, `Read(**/.env.*)`, `Edit(**/.env.*)`) | `.env` contiene la clave secreta y las credenciales. `.env.example` queda bloqueado con el mismo patrón: el agente propone su texto y el desarrollador lo edita. |
| Lectura de `backups/` en cualquier carpeta (`Read(**/backups/**)`) y edición de `backups/` en la raíz; lectura de `../respaldos/` (la carpeta de respaldos descargados, junto al proyecto) y de cualquier `respaldo_*.sql` | Los volcados contienen nombres, teléfonos y montos de clientes reales. La carpeta de respaldos se indica con una ruta relativa, no absoluta, para no depender del equipo. El patrón `respaldo_*.sql` usa el prefijo con que la aplicación nombra sus volcados, para no bloquear los guiones SQL de diagnóstico de `scripts/`. Si descargas un volcado con otro nombre, guárdalo fuera del repositorio. |
| WebFetch a `pythonanywhere.com`, `www.pythonanywhere.com` y `manzagrafica.pythonanywhere.com` | El panel y la API de PythonAnywhere son producción. La aplicación publicada tiene rutas que modifican datos con una simple visita, así que ni siquiera se lee desde el agente. La documentación de ayuda está en otro dominio y sigue disponible. |

## 5. `.env.example` y los límites de la protección

- **`.env.example` también queda bloqueado para lectura.** La regla `Read(./.env.*)` (y `Read(**/.env.*)`) calza con `.env.example`, así que el agente no puede leerlo; `Edit(**/.env.*)` también impide editarlo. Si una iteración necesita cambiarlo, el agente entrega el texto propuesto y el desarrollador lo aplica. Archivos nuevos como `.env.local` o `.env.production` quedan cubiertos por los mismos patrones.
- **La protección es parcial.** Las reglas `Read` y `Edit` solo gobiernan las herramientas de lectura y edición de Claude Code. No cubren un `grep -r` (ni `rg`, `findstr` o `Select-String`) que recorra el repositorio, ni un guion de Python o de shell que abra el archivo. Por eso el agente excluye siempre `.env`, `.env.*`, `backups/` y la carpeta de respaldos en sus búsquedas.
- **Sin sandbox en Windows nativo.** El sandbox de Claude Code, que limitaría a nivel de sistema los archivos que leen los comandos, no existe en Windows nativo. Aquí la única barrera para Bash y PowerShell es la disciplina del agente y la revisión del desarrollador.