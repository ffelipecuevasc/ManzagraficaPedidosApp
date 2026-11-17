# Iteración 04-03 · Credenciales y secretos

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones abiertas). Redactada el 2026-11-17 ([bitacora-04-03-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-03-redaccion.md)). Cinco decisiones `PENDIENTE_DESARROLLADOR` (sección «Decisiones»), cada una con opción recomendada.
- **Subfase del plan:** 4.3 «Credenciales y secretos» (`plan-de-trabajo.md`, sección 4.3).
- **Depende de:** 04-02 (usa su variable de seguridad, D3, y su regla de arranque, D5). Se desarrolla en local en paralelo a la vigilancia de la 03-05. **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → 04-02 (con su subida de HSTS) → **04-03**.
- **RDA relacionadas:** RDA-004 (PythonAnywhere, servidor compartido), RDA-007, RDA-013 (errores con `logging`, nunca con la salida de los comandos al usuario).
- **Hallazgos que cierra:** AUD-02-010 (clave del commit inicial) en lo que corresponde a la aplicación; la contraseña en los argumentos de `mysqldump` y `mysql` (plan 4.3). AUD-04-002 solo en la parte de credenciales del panel; el procedimiento sigue en la 13-02.
- **Cambio de esquema:** ninguno.
- **Respaldo previo al despliegue:** sí, el normal: la iteración cambia cómo se generan y restauran los respaldos. Se prueba un respaldo y una restauración en la réplica antes de desplegar.
- **Archivos que tocará la ejecución:** `pedidos/utils.py`, `PedidosApp/settings.py` y `.env.example` (configuración: **consulta previa**), `docs/operacion/` (respaldo, despliegue, réplica) y pruebas. El `.env` del servidor y el panel de PythonAnywhere los maneja solo el desarrollador.

## Regla de esta iteración

Ningún documento, bitácora, prueba ni mensaje contiene valores de claves o contraseñas, actuales o del historial. Se escribe solo si **coinciden o no**, medido con un método que no muestre el valor (como el hash de la 00-01).

## Objetivo

Que la contraseña de la base no aparezca en los argumentos de ningún proceso, que la aplicación no arranque sin una clave secreta segura, que se sepa qué secretos quedaron en el historial público y si siguen en uso, y que quede escrito quién tiene acceso al panel de PythonAnywhere.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main` (`84fe300`), con archivo y línea o commit.
- **Dicho por el desarrollador / medido antes:** se cita la fuente.
- **Inferido:** sale de leer el código o del comportamiento documentado de Django o MySQL; se dice cómo se confirma.
- **No verificado (producción):** solo se ve en el servidor.

## Qué hay hoy

### Contraseña en la línea de órdenes (verificado)

- `generar_respaldo_mysql()` arma `mysqldump … --password={db_password} …` (`pedidos/utils.py:44-50`, la contraseña en `:48`) y lo ejecuta con `subprocess.run` (`:57`).
- `restaurar_bd_mysql()` arma `mysql … --password={db_password} …` (`:113-117`, la contraseña en `:117`) y lo ejecuta con `subprocess.run` (`:126`).
- **Inferido:** mientras dura el proceso, sus argumentos son visibles para otros usuarios del mismo servidor (`ps`), que en PythonAnywhere es compartido. El plan lo dice (4.3); no se midió en el servidor.
- En la réplica local, la 01-09 registró que `mysqldump` no estaba instalado (`definicion-epica-04.md`, nota del 2026-10-26): **el ensayo local de respaldo y restauración puede exigir instalar el cliente de MySQL** (no verificado hoy).

### Clave secreta (verificado)

- `SECRET_KEY = os.getenv('SECRET_KEY')` (`settings.py:37`), sin comprobación: si falta, Django falla después con un error genérico (inferido).
- **Historial:** la clave literal con prefijo `django-insecure-` está en el commit `713260c` y sale de `settings.py` en `c9d58cc` (`git log -S`, sin mostrar el valor). El repositorio tiene remoto en GitHub; la auditoría lo trata como **público** (AUD-02-010).
- **Medido en la 00-01:** la clave de producción **no coincide** con la del commit `713260c` y no empieza con `django-insecure-` (`auditoria-tecnica.md:105`). La rotación «deja de ser urgente».

### Otra credencial en el historial (verificado, nuevo en esta redacción)

- Entre los commits `08a1a44` (2026-02-01) y `da0cbcd` (00-04), `settings.py` tuvo una **contraseña literal de la base local** (`NAME` `manzagrafica_local`, `HOST` `127.0.0.1`). Se detectó por búsqueda de patrón, sin mostrar el valor.
- **No se sabe si coincide** con la contraseña de la base de producción ni con la local actual. Se compara con el método de la 00-01 (decisión D4).
- `08a1a44` también agregó `.idea/dataSources.xml` (retirado en `965227d`): solo trae URL de conexión, sin contraseña ni usuario (conteo de claves, sin valores).
- No se revisaron a fondo coincidencias del patrón `mysql://usuario:clave@` en commits de documentación de la 00-03 y la 00-04 (`cfe5e26`, `27f7ff9`, `da0cbcd`): probablemente ejemplos, **no verificado** (la revisión automática fue denegada por permisos). Se revisa en la ejecución.
- `compose.yaml` (versionado): 3 líneas con `PASSWORD`, una con `${…}`; no se mostraron sus valores. Se revisa en la ejecución si alguna es literal.

### Panel de PythonAnywhere (AUD-04-002)

- Registrado: el cliente tiene acceso al panel y recargó la aplicación dos veces el 2026-10-27. Quién más tiene las credenciales y si se comparten: **no consta en el repo**.
- El procedimiento (quién recarga o despliega, «la app no responde») es de la 13-02.

## Alcance

1. **Contraseña fuera de los argumentos** de `mysqldump` y `mysql` (decisión D1), con la misma salida y el mismo manejo de errores de la 01-09.
2. **Clave secreta obligatoria** (D2): la aplicación no arranca sin `SECRET_KEY`; con la variable de seguridad de la 04-02 activa, tampoco con una clave con prefijo `django-insecure-` o demasiado corta. Mensaje claro con `ImproperlyConfigured`. Se coordina con D5 de la 04-02: ambas reglas viven juntas en el bloque de seguridad.
3. **Revisión del historial de Git** y decisión de rotar (D3 y D4), sin reescribir el historial.
4. **Credenciales del panel** (D5): registro de quién las tiene, sin valores.
5. **Documentación:** `.env.example` y `replica-local.md` dicen que `SECRET_KEY` es obligatoria; `despliegue.md` deja de esperar W009.

## Decisiones (`PENDIENTE_DESARROLLADOR`)

**D1 · Cómo recibe la contraseña el cliente de MySQL.**
- **A (recomendada):** archivo temporal de opciones (`--defaults-extra-file`) con permisos solo para el dueño, creado en una carpeta temporal y borrado en un `finally`. Es la vía que documenta MySQL; el archivo no queda en `backups/`.
- **B:** variable de entorno `MYSQL_PWD` en el entorno del subproceso. Más simple, pero MySQL 8.0 la marca como insegura y obsoleta (documentación de MySQL; no verificado aquí en la versión instalada).

**D2 · Cuándo se exige la clave.**
- **A (recomendada):** `SECRET_KEY` obligatoria siempre (local, pruebas, producción); con la variable de seguridad activa, además se rechazan prefijo `django-insecure-` y largo menor a 50.
- **B:** obligatoria solo con la variable de seguridad activa, con una clave fija de desarrollo en local. Más cómodo, pero vuelve a poner una clave en el código.

**D3 · Rotar la clave secreta de producción.**
- **A (recomendada):** no rotar ahora: no coincide con la expuesta (00-01). Se anota que la del commit `713260c` está quemada y no se usa en ningún entorno.
- **B:** rotar igual, con `SECRET_KEY_FALLBACKS` para la anterior durante unos días. **Inferido:** cambiar la clave sin respaldo cierra las sesiones abiertas y anula enlaces firmados (recuperación de contraseña); con la anterior en `SECRET_KEY_FALLBACKS` las sesiones siguen. Se confirma en la réplica antes.

**D4 · Contraseña de la base local que quedó en el historial.**
- **A (recomendada):** el desarrollador compara, sin escribir valores, si coincide con la de producción (y con la local actual) usando el método de hash de la 00-01. Si coincide con producción, se cambia la de producción desde el panel de PythonAnywhere y se actualiza `DATABASE_URL` en el `.env` del servidor; si solo coincide con la local, se cambia la local.
- **B:** cambiar la de producción sin comparar.
- En ambos casos **no se reescribe el historial** (prohibido a los agentes y el repo es público: lo publicado se da por expuesto).

**D5 · Credenciales del panel de PythonAnywhere.**
- **A (recomendada):** registrar en la bitácora quién tiene acceso (por rol: el desarrollador, el cliente), si la cuenta se comparte, y cambiar la contraseña del panel si se compartió por un medio inseguro. Activar la verificación en dos pasos si PythonAnywhere la ofrece (no verificado aquí). El procedimiento de uso va a la 13-02.
- **B:** solo registrar, sin cambios.

## Pasos

0. Consulta previa para `settings.py` y `.env.example`; D1 a D5 resueltas.
1. Línea base: `test pedidos` y `check --deploy` con `DEBUG=False` (tras la 04-02, esperado solo W009).
2. Pruebas primero (sección siguiente).
3. `utils.py` según D1, en las dos funciones.
4. `settings.py` según D2, junto al bloque de la 04-02.
5. Ensayo en la réplica: un respaldo desde la web (descarga completa) y una restauración del mismo archivo; durante el respaldo, `ps` en local no muestra la contraseña.
6. Revisión del historial (D4) y de los puntos no verificados de «Otra credencial en el historial», sin escribir valores.
7. Documentación, bitácora, registro, estado «En revisión».

## Pruebas

- La lista de argumentos que recibe `subprocess.run` en el respaldo y en la restauración no contiene la contraseña ni `--password` (reemplazando `subprocess.run` donde lo busca `utils.py`; nunca se ejecuta `mysqldump` en la prueba).
- El archivo temporal de opciones (D1-A) se borra también cuando el comando falla.
- Arranque sin `SECRET_KEY` falla con `ImproperlyConfigured`; con la variable de seguridad activa y una clave `django-insecure-…` o corta, también (proceso hijo, como en la 04-02).
- Las pruebas existentes de respaldo y restauración (`test_capturas_amplias.py`, `test_acceso.BaseDeDatosPermisosTests`, `test_contrato_error.py`) siguen en verde.
- Suite con los mismos fallos esperados que deje la 04-01 (4).

## Verificación en producción (la hace el desarrollador; **no verificado** hasta entonces)

1. `.env` del servidor con `SECRET_KEY` válida (la regla de D2 no la rechaza) **antes** del Reload.
2. Tras el Reload, la aplicación arranca; `check --deploy` sin advertencias.
3. Un respaldo desde la web se descarga completo; `server.log` sin errores de `mysqldump`.
4. Si se rotó algo (D3-B o D4): las sesiones siguen o se cierran según lo previsto, y la base responde.

## Plan de retroceso

- `retroceso.md`, caso 1 (sin migraciones). Si se rotó la contraseña de la base y algo falla, el `DATABASE_URL` del `.env` y la contraseña del panel deben quedar coherentes: se anota el orden exacto en la bitácora de ejecución, sin valores.
- Si el respaldo deja de funcionar tras el despliegue, se vuelve a la etiqueta anterior: el respaldo con contraseña en argumentos funciona y el riesgo es menor que quedarse sin respaldos.

## Criterio de término

- Ningún comando de la aplicación lleva la contraseña en sus argumentos (prueba automatizada y `ps` en la réplica).
- La aplicación no arranca sin una clave válida (prueba automatizada).
- Historial revisado: la bitácora dice qué secretos aparecieron, en qué commits y si coinciden con los vigentes, **sin valores**.
- Credenciales del panel registradas por rol.
- Respaldo desde la web verificado en producción.

## Riesgos

- **Quedarse sin respaldo:** un error en D1 rompe el respaldo y la restauración; mitigado con el ensayo en la réplica y el respaldo previo.
- **Arranque bloqueado:** D2 tumba el sitio si el `.env` del servidor no trae una clave válida; mitigado con el paso 1 de la verificación (`.env` antes del Reload).
- **Cierre de sesiones al rotar (inferido):** solo con D3-B; mitigado con `SECRET_KEY_FALLBACKS`.
- **Ensayo local sin cliente de MySQL:** puede exigir instalarlo en el equipo (no es dependencia de Python; se consulta).
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-02.
