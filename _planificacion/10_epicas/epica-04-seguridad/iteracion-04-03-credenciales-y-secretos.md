# Iteración 04-03 · Credenciales y secretos

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones resueltas). Redactada el 2026-11-17 ([bitacora-04-03-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-03-redaccion.md)); D1 a D5 **resueltas el 2026-11-17** por el desarrollador (dicho por él; [bitacora-04-03-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-03-cierre.md)).
- **Subfase del plan:** 4.3 «Credenciales y secretos» (`plan-de-trabajo.md`, sección 4.3).
- **Depende de:** 04-02 (usa su variable `SEGURIDAD_PRODUCCION`, D3, y su regla de arranque, D5). Se desarrolla en local en paralelo a la vigilancia de la 03-05. **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → 04-02 (con su subida de HSTS) → **04-03**.
- **RDA relacionadas:** RDA-004 (PythonAnywhere, servidor compartido), RDA-007, RDA-013 (errores con `logging`, nunca con la salida de los comandos al usuario).
- **Hallazgos que cierra:** AUD-02-010 (clave del commit inicial) en lo que corresponde a la aplicación, con riesgo aceptado para lo publicado; la contraseña en los argumentos de `mysqldump` y `mysql` (plan 4.3). AUD-04-002: solo se registra por rol quién tiene acceso al panel; contraseñas, verificación en dos pasos y procedimiento van a la 13-02.
- **Cambio de esquema:** ninguno.
- **Respaldo previo al despliegue:** sí, el normal: la iteración cambia cómo se generan y restauran los respaldos. Se prueba un respaldo y una restauración en la réplica antes de desplegar.
- **Archivos que tocará la ejecución:** `pedidos/utils.py`, `PedidosApp/settings.py` y `.env.example` (configuración: **consulta previa**), `docs/operacion/` (respaldo, despliegue, réplica) y pruebas. El `.env` del servidor y el panel de PythonAnywhere los maneja solo el desarrollador.

## Regla de esta iteración

Ningún documento, bitácora, prueba ni mensaje contiene valores de claves o contraseñas, actuales o del historial. Se escribe solo si **coinciden o no**, medido con un método que no muestre el valor (como el hash de la 00-01).

## Objetivo

Que la contraseña de la base no aparezca en los argumentos de ningún proceso, que la aplicación no arranque sin una clave secreta segura, que se sepa qué secretos quedaron en el historial público y si siguen en uso (riesgo aceptado y documentado) y que quede escrito, por rol, quién tiene acceso al panel de PythonAnywhere.

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
- **Dicho por el desarrollador (2026-11-17), no verificado por el agente:** comparó producción y desarrollo y **no coinciden**. Riesgo aceptado (D4).
- `08a1a44` también agregó `.idea/dataSources.xml` (retirado en `965227d`): solo trae URL de conexión, sin contraseña ni usuario (conteo de claves, sin valores).
- No se revisaron a fondo coincidencias del patrón `mysql://usuario:clave@` en commits de documentación de la 00-03 y la 00-04 (`cfe5e26`, `27f7ff9`, `da0cbcd`): probablemente ejemplos, **no verificado** (la revisión automática fue denegada por permisos). Se revisa en la ejecución.
- `compose.yaml` (versionado): 3 líneas con `PASSWORD`, una con `${…}`; no se mostraron sus valores. Se revisa en la ejecución si alguna es literal.

### Panel de PythonAnywhere (AUD-04-002)

- Registrado: el cliente tiene acceso al panel y recargó la aplicación dos veces el 2026-10-27. Quién más tiene las credenciales y si se comparten: **no consta en el repo**.
- El procedimiento (quién recarga o despliega, «la app no responde») es de la 13-02.

## Alcance

1. **Contraseña fuera de los argumentos** de `mysqldump` y `mysql` con un archivo temporal de opciones (D1), con la misma salida y el mismo manejo de errores de la 01-09.
2. **Clave secreta obligatoria** (D2): la aplicación no arranca sin `SECRET_KEY`; con `SEGURIDAD_PRODUCCION` activa, tampoco con una clave con prefijo `django-insecure-` o corta (largo mínimo propuesto: 50, el de la comprobación W009 de Django; se confirma al ejecutar). Mensaje claro con `ImproperlyConfigured`, junto a la regla D5 de la 04-02 en el mismo bloque.
3. **Historial de Git** (D3 y D4): sin rotación ni reescritura; la bitácora registra qué secretos aparecieron, en qué commits y si coinciden, sin valores, y el riesgo aceptado.
4. **Acceso al panel** (D5): solo un registro por rol en la bitácora. Cambiar contraseñas y activar la verificación en dos pasos **quedan fuera** (13-02).
5. **Documentación:** `.env.example` y `replica-local.md` dicen que `SECRET_KEY` es obligatoria; `despliegue.md` deja de esperar W009.

## Decisiones (resueltas el 2026-11-17, dichas por el desarrollador)

| # | Decisión | Qué se hace |
| :- | :------- | :---------- |
| D1 | Archivo temporal de opciones | `mysqldump` y `mysql` reciben `--defaults-extra-file=<archivo temporal>` (debe ir **primero** en la lista de argumentos; inferido de la documentación de MySQL, se confirma en la réplica). El archivo se crea con permisos solo para el dueño, fuera de `backups/`, y **se borra siempre en un `finally`**, también si el comando falla. |
| D2 | Clave obligatoria | Sin `SECRET_KEY`, `ImproperlyConfigured` en todo entorno. Con `SEGURIDAD_PRODUCCION` activa, además se rechazan prefijo `django-insecure-` y claves cortas. |
| D3 | No se rota ahora | La 00-01 midió que la clave de producción no coincide con la de `713260c`. La de `713260c` se da por quemada: no se usa en ningún entorno. |
| D4 | Riesgo aceptado | La contraseña local de `08a1a44` a `da0cbcd` queda publicada; según el desarrollador no coincide con la de producción (no verificado por el agente). **Nunca se reescribe el historial.** |
| D5 | Solo registro | Se anota por rol quién tiene acceso al panel. Sin cambiar contraseñas ni activar verificación en dos pasos: van a la 13-02. |

## Pasos

0. Consulta previa para editar `settings.py` y `.env.example` (`AGENTS.md`, sección 6).
1. Línea base: `test pedidos` y `check --deploy` con `DEBUG=False` y `SEGURIDAD_PRODUCCION` activa (tras la 04-02, esperado solo W009).
2. Pruebas primero (sección siguiente).
3. `utils.py` según D1, en las dos funciones, con un único ayudante que crea y borra el archivo.
4. `settings.py` según D2, junto al bloque de la 04-02.
5. Ensayo en la réplica: un respaldo desde la web (descarga completa) y una restauración del mismo archivo; durante el respaldo, la lista de procesos local no muestra la contraseña; al terminar no queda ningún archivo de opciones.
6. Bitácora con el historial revisado (commits y coincidencias, sin valores), el riesgo aceptado de D4 y el registro por rol de D5; revisión de los puntos no verificados de «Otra credencial en el historial».
7. Documentación, registro, estado «En revisión».

## Pruebas

- La lista de argumentos que recibe `subprocess.run` en el respaldo y en la restauración no contiene la contraseña ni `--password`, y empieza con `--defaults-extra-file` (reemplazando `subprocess.run` donde lo busca `utils.py`; nunca se ejecuta `mysqldump` en la prueba).
- El archivo de opciones existe durante la llamada y **no existe después**, tanto si el comando termina bien como si lanza `CalledProcessError` o `FileNotFoundError`.
- Arranque sin `SECRET_KEY` falla con `ImproperlyConfigured`; con `SEGURIDAD_PRODUCCION` activa y una clave `django-insecure-…` o corta, también; con una clave válida, arranca (proceso hijo, como en la 04-02).
- Las pruebas existentes de respaldo y restauración (`test_capturas_amplias.py`, `test_acceso.BaseDeDatosPermisosTests`, `test_contrato_error.py`) siguen en verde.
- Suite con los mismos fallos esperados que deje la 04-01 (4).

## Verificación en producción (la hace el desarrollador; **no verificado** hasta entonces)

1. `.env` del servidor con `SECRET_KEY` válida para la regla de D2 **antes** del Reload (el agente no ve el `.env`).
2. Tras el Reload, la aplicación arranca; `check --deploy` sin advertencias.
3. Un respaldo desde la web se descarga completo; `server.log` sin errores de `mysqldump`; no queda ningún archivo de opciones.

## Plan de retroceso

- `retroceso.md`, caso 1 (sin migraciones). No hay rotación de secretos que deshacer (D3, D4).
- Si el respaldo o la restauración dejan de funcionar tras el despliegue, se vuelve a la etiqueta anterior: el respaldo con contraseña en argumentos funciona y el riesgo es menor que quedarse sin respaldos.
- Si la aplicación no arranca por D2, se corrige `SECRET_KEY` en el `.env` del servidor y se recarga; si no se puede de inmediato, caso 1.

## Criterio de término

- Ningún comando de la aplicación lleva la contraseña en sus argumentos (prueba automatizada y lista de procesos en la réplica), y el archivo temporal se borra siempre (prueba automatizada).
- La aplicación no arranca sin una clave válida (prueba automatizada).
- Bitácora con el historial revisado y el riesgo aceptado de D4, **sin valores**.
- Acceso al panel registrado por rol.
- Respaldo desde la web verificado en producción.

## Riesgos

- **Quedarse sin respaldo:** un error en D1 rompe el respaldo y la restauración; mitigado con el ensayo en la réplica y el respaldo previo al despliegue.
- **Archivo de opciones huérfano:** si el proceso muere entre crear y borrar (por ejemplo, el worker se reinicia), el archivo queda en la carpeta temporal; mitigado con permisos solo del dueño. Riesgo residual anotado.
- **Arranque bloqueado:** D2 tumba el sitio si el `.env` del servidor no trae una clave válida; mitigado con el paso 1 de la verificación (`.env` antes del Reload).
- **Riesgo aceptado del historial (D3, D4):** lo publicado no se puede retirar; queda documentado.
- **Ensayo local sin cliente de MySQL:** puede exigir instalarlo en el equipo (no es dependencia de Python; se consulta).
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-02.
