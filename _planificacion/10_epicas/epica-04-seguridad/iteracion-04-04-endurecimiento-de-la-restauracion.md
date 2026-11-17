# Iteración 04-04 · Endurecimiento de la restauración

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones resueltas). Redactada el 2026-11-17 ([bitacora-04-04-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-04-redaccion.md)); D1 a D6 resueltas por el desarrollador el mismo día ([bitacora-04-04-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-04-cierre.md)).
- **Subfase del plan:** 4.4 «Restauración endurecida» (`definicion-epica-04.md`, alcance 4).
- **Depende de:** 04-03 (archivo temporal de opciones, D1, en `generar_respaldo_mysql` y `restaurar_bd_mysql`) y 04-01 (`generar_respaldo_bd` solo POST). Se desarrolla en local en paralelo a la vigilancia de la 03-05. **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → 04-02 (y su subida de HSTS) → 04-03 → **04-04**.
- **RDA relacionadas:** RDA-007, RDA-009 (tareas lentas fuera de la petición), RDA-013 (errores en `server.log`, eventos en MySQL), RDA-019 (captura fuera del `atomic`).
- **Hallazgos que cierra:** AUD-02-024 (D5) y el **`.sql` vacío** ante un fallo de `mysqldump`, hallazgo hermano de AUD-02-019 sin ID propio (nota del 2026-10-26 de la definición). **No cierra AUD-02-019** (rotación por cantidad, 06-03) **ni AUD-05-004** (pasa a la Épica 08 por D6).
- **Cambio de esquema:** ninguno con las opciones recomendadas.
- **Respaldo previo al despliegue:** **sí**, obligatorio: la iteración cambia la restauración y el respaldo de emergencia.
- **Archivos que tocará la ejecución:** `pedidos/utils.py`, `pedidos/views.py` (`restaurar_bd`), `pedidos/templates/pedidos/restaurar_bd.html`, `docs/operacion/respaldo.md` y `retroceso.md` (caso 3), y pruebas. Sin archivos de configuración: el tope de D1 es una constante en `utils.py`.

## Objetivo

Que la restauración solo acepte un volcado válido de esta aplicación, que nunca restaure sin un respaldo de emergencia comprobado, que pida una confirmación que el servidor verifique, que deje constancia que sobreviva al reemplazo de la tabla de eventos y que no deje archivos vacíos ni huérfanos en el disco de 512 MiB.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main`, con archivo y línea.
- **Inferido:** sale de leer el código o del comportamiento documentado de MySQL; se dice cómo se confirma.
- **No verificado (producción):** solo se ve en el servidor.

## Qué hay hoy (verificado)

### La vista `restaurar_bd` (`views.py:1240-1316`)

- Solo superusuario (`@user_passes_test`), escribe solo con POST (`:1248`).
- **Extensión:** `archivo.name.endswith('.sql')` (`:1256`), sensible a mayúsculas y sin mirar el contenido. **Tamaño y estructura: sin validar.**
- Guarda la subida en `backups/tmp/` con `FileSystemStorage` (`:1263-1269`).
- **Respaldo de emergencia:** `generar_respaldo_mysql()` (`:1276`); si lanza una excepción, aborta, borra la subida y avisa (`:1277-1285`). **No comprueba que el archivo generado tenga contenido:** si `mysqldump` termina con código 0 y una salida incompleta, se restauraría igual (inferido).
- Restaura (`:1290`) y **después** registra `restauracion_ejecutada` (`:1292-1293`).
- **Archivo subido huérfano:** si la restauración falla, el `except` (`:1302-1310`) registra y avisa, pero no borra la subida de `backups/tmp/` (solo se borra en el camino feliz, `:1299-1300`).

### `utils.py`

- `generar_respaldo_mysql()` abre el `.sql` antes de `mysqldump` (`:56`) y solo lo borra ante `CalledProcessError` (`:58-63`). Ante `FileNotFoundError` (sin `mysqldump`) u otra excepción **queda un `.sql` vacío** en `backups/`, que la rotación cuenta entre los cinco (`:67`). Visto en la réplica en la 01-09 (nota de la definición).
- `limpiar_backups_antiguos(mantener=5)` rota por fecha de modificación todos los `*.sql` de `backups/`, incluidos los de emergencia (`:70-92`).
- `restaurar_bd_mysql()` pasa el archivo por la entrada estándar de `mysql` (`:121-126`), abierto en modo texto con la codificación por defecto del sistema (inferido: UTF-8 en el servidor, distinta en Windows).

### La pantalla (`restaurar_bd.html`)

- Formulario POST con `accept=".sql"` (`:36-40`) y una confirmación SweetAlert solo en el navegador (`:59-89`): **el servidor no verifica ninguna confirmación.**
- AUD-05-004 (la tarjeta de `:106-107` pinta todo `success`) existe, pero **queda fuera** de esta iteración por D6: pasa a la Épica 08. Esta iteración no toca ese recorrido de mensajes.

### Respaldos en disco

- `respaldar_bd.html` lista los respaldos (nombre, fecha, tamaño; `:95-102`) **sin enlace de descarga**: el de emergencia solo se puede recuperar desde el servidor (AUD-02-024).
- Tamaño de un respaldo medido el 2026-11-03: 1.481.608 bytes (AUD-03-002, caso 1). Seis archivos de ese tamaño son menos del 2 % de 512 MiB (cálculo propio, sobre una sola medición).

## Contradicciones con la planificación

- **El `.sql` vacío no es AUD-02-019.** En `auditoria-tecnica.md:84`, AUD-02-019 es la rotación por cantidad, con destino **06-03**. La nota del 2026-10-26 de la definición asocia el `.sql` vacío a ese ID. Resuelto el 2026-11-17: el `.sql` vacío es un **hallazgo hermano** sin ID propio, se corrige aquí con una prueba que falla primero, y la rotación sigue en la 06-03. La definición, el registro y la auditoría usan ya esta lectura.
- **D5 roza la 06-03:** sacar el respaldo `emergencia_` de la rotación por cantidad es una **excepción mínima** a la política vigente; la 06-03 la hereda y decide si la conserva al rediseñar la rotación.
- **AUD-05-004 sale de esta iteración (D6):** pasa a la Épica 08, junto con AUD-05-005 a AUD-05-008.

## Alcance

1. **Validación del volcado subido:** extensión (sin distinguir mayúsculas), tamaño (D1) y estructura (D2), **antes** del respaldo de emergencia, con mensaje fijo y sin detalles técnicos.
2. **Aborto sin excepciones:** no se restaura si el respaldo de emergencia falla **o** sale vacío o incompleto (misma comprobación de estructura que D2 aplicada a lo que se generó).
3. **Confirmación explícita verificada por el servidor** (D3).
4. **Constancia que sobreviva** al reemplazo de la tabla de eventos (D4).
5. **`.sql` vacío:** `generar_respaldo_mysql()` borra el archivo ante **cualquier** fallo de `mysqldump` y vuelve a lanzar la excepción.
6. **Subida huérfana:** el archivo de `backups/tmp/` se borra siempre (`finally`), también si la restauración falla.
7. **Respaldo de emergencia en el mismo disco** (AUD-02-024, D5).
8. **Coordinación:** usa el ayudante del archivo temporal de opciones de la 04-03 (D1); no cambia el POST de `generar_respaldo_bd` de la 04-01.
9. **Fuera:** AUD-05-004 (Épica 08, D6); rotación por cantidad y política de retención (AUD-02-019, 06-03); respaldo externo (Épica 14); límites globales de subida (`DATA_UPLOAD_MAX_MEMORY_SIZE`, 04-08).

## Decisiones (resueltas por el desarrollador, 2026-11-17)

| # | Decisión | Resuelta como |
| :- | :------- | :------------ |
| D1 | Tope de tamaño | **20 MB**, constante con comentario en `utils.py` (más de diez veces el respaldo medido). Se revisa si la base crece. |
| D2 | Volcado válido | Por **estructura y sentencias peligrosas**: texto UTF-8; cabecera `-- MySQL dump` y final `-- Dump completed` (inferido, se confirma con un respaldo real de la réplica); creación de `pedidos_pedido` y `django_migrations`; rechaza `CREATE DATABASE`, `DROP DATABASE`, `USE`, `GRANT` y `CREATE USER`. La **misma función valida el respaldo de emergencia**. |
| D3 | Confirmación | Campo donde se escribe **`RESTAURAR`**, exigido por el servidor, **además** del aviso SweetAlert actual. Sin él no se toca nada. |
| D4 | Constancia | Una línea en `server.log` **antes** (usuario, archivo, respaldo de emergencia) y otra **después** (resultado); el evento `restauracion_ejecutada` se registra después, **con usuario nulo** si el volcado no trae al usuario (`models.py:271-272`). Sin tabla nueva. |
| D5 | Respaldo de emergencia | Prefijo **`emergencia_`**, **fuera de la rotación por cantidad**, se conserva **solo el último**; la pantalla de respaldos lo marca y los mensajes dicen su nombre. **Excepción mínima que roza la 06-03.** La descarga queda como propuesta (funcionalidad nueva). |
| D6 | AUD-05-004 | **No se corrige aquí.** Pasa a la Épica 08 (iteración por definir). Se retiran de esta iteración el punto de alcance, la prueba y el cambio de mensajes de `restaurar_bd.html`. |

## Pasos

0. Respaldo de la réplica antes de cualquier ensayo.
1. Línea base: `test pedidos` (se anota el número tras la 04-03).
2. Pruebas primero (tabla siguiente); ver fallar las de los puntos 1 a 7.
3. `utils.py`: constante de 20 MB (D1), validación de estructura (D2), borrado ante cualquier fallo, respaldo `emergencia_` y su exclusión de la rotación (D5).
4. `restaurar_bd`: orden validar → confirmar → respaldo de emergencia → comprobar respaldo → registrar antes → restaurar → registrar después, con `finally` para la subida.
5. `restaurar_bd.html`: solo el campo de D3, según `DESIGN.md`; el recorrido de mensajes (`:100-112`) no se toca (D6).
6. Ensayo en la réplica (ver «Riesgo de ensayar»).
7. `respaldo.md` y `retroceso.md` (caso 3: nombre del respaldo de emergencia).
8. Bitácora, registro, estado «En revisión».

## Pruebas

Todas reemplazan `generar_respaldo_mysql`, `restaurar_bd_mysql` o `subprocess.run` donde los busca el código: **ninguna ejecuta `mysqldump` ni `mysql`**.

| Punto del alcance | Prueba |
| :---------------- | :----- |
| 1 · Extensión, tamaño, estructura | Un `.SQL` válido pasa; un `.txt`, un archivo de 20 MB más un byte, uno sin cabecera, uno sin final y uno con `DROP DATABASE` se rechazan sin llamar al respaldo ni a la restauración. |
| 2 · Aborto | Respaldo de emergencia que lanza excepción (ya existe: `test_capturas_amplias.py:65`) y respaldo que devuelve un archivo vacío o sin final: no se restaura. |
| 3 · Confirmación | POST sin el campo, vacío, con `restaurar` en minúsculas o con otro texto: no se llama al respaldo ni a la restauración. Con espacios al inicio o al final de `RESTAURAR` pasa (se aplica `strip()`): mismo criterio que la 04-10 (`ELIMINAR`): coincidencia exacta, sensible a mayúsculas. |
| 4 · Constancia | `assertLogs` con las líneas antes y después; el evento se registra aunque el usuario no exista tras restaurar. |
| 5 · `.sql` vacío | `subprocess.run` lanza `FileNotFoundError`: el `.sql` no queda en `backups/`. **Falla hoy** (`utils.py:58-63` solo cubre `CalledProcessError`). |
| 6 · Subida huérfana | La restauración falla: `backups/tmp/` queda vacío. **Falla hoy.** |
| 7 · Emergencia | El de emergencia lleva el prefijo y no lo borra `limpiar_backups_antiguos` aunque haya cinco respaldos más nuevos; al crear otro, el `emergencia_` anterior se borra. |
| Existentes | `test_capturas_amplias.py:65-91`, `test_acceso.BaseDeDatosPermisosTests` (el POST de usuario común sigue en 302) y `test_contrato_error.py` siguen en verde; las que hacen POST a `restaurar_bd` agregan el campo de D3. `test_un_pago_registrado_no_aparece_como_restauracion_exitosa` (03-04) sigue sin cambios: AUD-05-004 no se toca. |

Suite con los mismos fallos esperados que deje la 04-01 (4).

## Riesgo de ensayar restauraciones en la réplica

- **Restaurar reemplaza la base de la réplica**, que es una copia de producción con datos reales. Un volcado de prueba mal armado deja la réplica inservible hasta refrescarla (`docs/operacion/replica-local.md`), y ese refresco depende de un respaldo descargado por el desarrollador.
- Por eso el ensayo usa **un respaldo generado por la propia réplica** (restaurar sobre sí misma) y, antes, un respaldo de la réplica guardado por el desarrollador.
- **Nunca contra producción.** `settings.py:142-145` solo protege la base de **pruebas**; la vista no sabe a qué base apunta. El ensayo se hace con el `.env` local (sin `DATABASE_URL`).
- El ensayo puede exigir el cliente de MySQL instalado en el equipo (la 01-09 no tenía `mysqldump`).
- Los volcados son datos personales: no se abren ni se copian a la documentación (`AGENTS.md`, sección 6); la bitácora anota solo tamaños, tiempos y conteos.

## Verificación en producción (la hace el desarrollador; **no verificado** hasta entonces)

1. Respaldo previo al despliegue, descargado y verificado (`respaldo.md`).
2. Tras el Reload, `restaurar_bd` carga y muestra el campo de confirmación; un archivo no válido (por ejemplo, un `.sql` vacío creado en el equipo) se rechaza con el mensaje fijo **sin** crear respaldo de emergencia.
3. **No se ejecuta una restauración real en producción** para validar la iteración: el camino completo se valida en la réplica.
4. `server.log` sin errores nuevos.

## Plan de retroceso

- `retroceso.md`, caso 1 (sin migraciones): volver a la etiqueta anterior. Los archivos `emergencia_…` que hayan quedado no estorban al código anterior: la rotación anterior los trata como cualquier `.sql` (inferido de `utils.py:70-92`).
- Si una restauración real falla después del despliegue: caso 3, con el nombre del respaldo de emergencia que da el mensaje.

## Criterio de término

- Las pruebas de la tabla en verde, con las de los puntos 5 y 6 escritas antes de la corrección y vistas fallar.
- Ensayo en la réplica: un volcado propio se restaura; uno inválido se rechaza sin tocar la base; queda la línea de `server.log` y el respaldo de emergencia.
- `respaldo.md` y `retroceso.md` actualizados.
- Verificación de producción hecha (puntos 1, 2 y 4).

## Riesgos

- **Rechazar un volcado bueno:** si la validación de D2 es más estricta que el formato real, la restauración queda bloqueada justo cuando hace falta; mitigado con un respaldo real de la réplica como caso de prueba y con el procedimiento manual de `retroceso.md`, caso 3.
- **Choque con `AGENTS.md`, regla 8.10 (restauración dentro de la petición):** el respaldo de emergencia y la restauración corren en el ciclo de la petición con un solo worker; mientras duran, la aplicación no atiende a nadie y una petición larga puede cortarse. Esta iteración **no lo cambia** (sería otra arquitectura y otro propósito, RDA-007). **Propuesta** (registro, sección 4): evaluar en la 06-03 o en la Épica 14 una restauración fuera de la petición (desde consola, que ya es el caso 3 de `retroceso.md`) y dejar la pantalla para volcados pequeños; mientras tanto se mide el tiempo del ensayo en la réplica y se anota en la bitácora.
- **D2 sobre el respaldo de emergencia:** si la validación rechaza un respaldo de emergencia bueno, ninguna restauración avanza; se mitiga con el mismo caso de prueba real de la réplica.
- **Excepción a la rotación (D5):** la 06-03 debe conocerla para no anularla sin querer al rediseñar la rotación.
- **Disco:** el respaldo de emergencia fuera de la rotación agrega como máximo un archivo; despreciable según la medición, sin verificar el uso actual del disco.
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-03.
