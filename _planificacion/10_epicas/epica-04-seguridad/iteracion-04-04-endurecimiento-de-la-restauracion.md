# Iteración 04-04 · Endurecimiento de la restauración

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones abiertas). Redactada el 2026-11-17 ([bitacora-04-04-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-04-redaccion.md)). Seis decisiones `PENDIENTE_DESARROLLADOR` (sección «Decisiones»), cada una con opción recomendada.
- **Subfase del plan:** 4.4 «Restauración endurecida» (`definicion-epica-04.md`, alcance 4).
- **Depende de:** 04-03 (archivo temporal de opciones, D1, en `generar_respaldo_mysql` y `restaurar_bd_mysql`) y 04-01 (`generar_respaldo_bd` solo POST). Se desarrolla en local en paralelo a la vigilancia de la 03-05. **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → 04-02 (y su subida de HSTS) → 04-03 → **04-04**.
- **RDA relacionadas:** RDA-007, RDA-009 (tareas lentas fuera de la petición), RDA-013 (errores en `server.log`, eventos en MySQL), RDA-019 (captura fuera del `atomic`).
- **Hallazgos que cierra:** AUD-02-024 (según D5), AUD-05-004 (según D6) y el `.sql` vacío ante un fallo de `mysqldump` (nota del 2026-10-26 de la definición). **AUD-02-019 no se cierra:** es la rotación por cantidad, asignada a la 06-03 (ver «Contradicciones»).
- **Cambio de esquema:** ninguno con las opciones recomendadas.
- **Respaldo previo al despliegue:** **sí**, obligatorio: la iteración cambia la restauración y el respaldo de emergencia.
- **Archivos que tocará la ejecución:** `pedidos/utils.py`, `pedidos/views.py` (`restaurar_bd`), `pedidos/templates/pedidos/restaurar_bd.html`, `docs/operacion/respaldo.md` y `retroceso.md` (caso 3), y pruebas. Sin archivos de configuración salvo que D1 lleve el tope a `settings.py` (consulta previa).

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
- **AUD-05-004:** la plantilla recorre sus propios mensajes y pinta todo `success` como la tarjeta «¡Base de Datos Restaurada Exitosamente!» (`:106-107`), aunque venga de otra pantalla.

### Respaldos en disco

- `respaldar_bd.html` lista los respaldos (nombre, fecha, tamaño; `:95-102`) **sin enlace de descarga**: el de emergencia solo se puede recuperar desde el servidor (AUD-02-024).
- Tamaño de un respaldo medido el 2026-11-03: 1.481.608 bytes (AUD-03-002, caso 1). Seis archivos de ese tamaño son menos del 2 % de 512 MiB (cálculo propio, sobre una sola medición).

## Contradicciones con la planificación

- **AUD-02-019 no es el `.sql` vacío.** En `auditoria-tecnica.md:84`, AUD-02-019 es la rotación por cantidad, con destino **06-03**. La nota del 2026-10-26 de la definición pide «una prueba que falle antes de la corrección (AUD-02-019)», asociando el `.sql` vacío a ese hallazgo. Esta iteración corrige el `.sql` vacío y lo trata como **hallazgo hermano**; no cambia la política de rotación (06-03).
- **D5 roza la 06-03:** excluir el respaldo de emergencia de la rotación es un cambio en la rotación. Se propone el mínimo (ver D5) y se avisa a la 06-03.

## Alcance

1. **Validación del volcado subido:** extensión (sin distinguir mayúsculas), tamaño (D1) y estructura (D2), **antes** del respaldo de emergencia, con mensaje fijo y sin detalles técnicos.
2. **Aborto sin excepciones:** no se restaura si el respaldo de emergencia falla **o** sale vacío o incompleto (misma comprobación de estructura que D2 aplicada a lo que se generó).
3. **Confirmación explícita verificada por el servidor** (D3).
4. **Constancia que sobreviva** al reemplazo de la tabla de eventos (D4).
5. **`.sql` vacío:** `generar_respaldo_mysql()` borra el archivo ante **cualquier** fallo de `mysqldump` y vuelve a lanzar la excepción.
6. **Subida huérfana:** el archivo de `backups/tmp/` se borra siempre (`finally`), también si la restauración falla.
7. **Respaldo de emergencia en el mismo disco** (AUD-02-024, D5).
8. **AUD-05-004** (D6).
9. **Coordinación:** usa el ayudante del archivo temporal de opciones de la 04-03 (D1); no cambia el POST de `generar_respaldo_bd` de la 04-01.
10. **Fuera:** rotación por cantidad y política de retención (AUD-02-019, 06-03); respaldo externo (Épica 14); límites globales de subida (`DATA_UPLOAD_MAX_MEMORY_SIZE`, 04-08).

## Decisiones (`PENDIENTE_DESARROLLADOR`)

**D1 · Tope de tamaño del volcado.**
- **A (recomendada):** 20 MB, fijo en el código como constante con comentario (más de diez veces el respaldo medido). Se revisa si la base crece.
- **B:** tope relativo (por ejemplo, tres veces el respaldo más reciente). Se adapta solo, pero falla si no hay respaldos previos.

**D2 · Qué es un volcado válido.**
- **A (recomendada):** texto UTF-8; primera línea de cabecera de `mysqldump` (`-- MySQL dump`) y línea final `-- Dump completed` (inferido del formato de `mysqldump`; se confirma con un respaldo real de la réplica); contiene la creación de `pedidos_pedido` y de `django_migrations`; **rechaza** `CREATE DATABASE`, `DROP DATABASE`, `USE`, `GRANT` y `CREATE USER` (un volcado de esta aplicación no los trae porque `mysqldump` se llama sin `--databases`, `utils.py:44-51`). La misma función valida el respaldo de emergencia.
- **B:** solo cabecera y final. Más simple; deja pasar un volcado de otra base.

**D3 · Confirmación explícita.**
- **A (recomendada):** además del SweetAlert, un campo donde el superusuario escribe `RESTAURAR`; el servidor lo exige y, si falta, no toca nada. Funciona con JavaScript desactivado y se puede probar.
- **B:** escribir el nombre del archivo subido.
- **C:** dejar solo el SweetAlert (no verificable en el servidor).

**D4 · Constancia que sobreviva.**
- **A (recomendada):** una línea `logger.warning` en `server.log` **antes** de restaurar (usuario, nombre del archivo, respaldo de emergencia) y otra **después** con el resultado; el evento `restauracion_ejecutada` se mantiene después de restaurar, y si el volcado no trae al usuario se registra con usuario nulo (`RegistroEvento.usuario` admite nulo, `models.py:271-272`). Sin tabla nueva.
- **B:** exportar los eventos posteriores al volcado y reinsertarlos tras restaurar. Más completo, pero más código y riesgo en el momento más delicado.

**D5 · Respaldo de emergencia en el mismo disco (AUD-02-024).**
- **A (recomendada):** nombre con prefijo `emergencia_`, **fuera de la rotación por cantidad**, conservando solo el último de emergencia (el anterior se borra al crear uno nuevo); la pantalla de respaldos lo marca; el mensaje de éxito y el de error dicen su nombre. El disco no es el problema hoy (ver «Respaldos en disco»). La descarga de un respaldo existente es funcionalidad nueva: queda como propuesta.
- **B:** solo documentarlo en `respaldo.md` y dejarlo todo a la 06-03 y la Épica 14.

**D6 · AUD-05-004.**
- **A (recomendada):** la vista marca su mensaje con una etiqueta propia (`extra_tags='restauracion'`) y `restaurar_bd.html` solo pinta la tarjeta para esa etiqueta; los demás mensajes los pinta `base.html` como hasta hoy.
- **B:** la pantalla de resultado deja de usar mensajes y recibe el resultado en la redirección.

## Pasos

0. Respaldo de la réplica antes de cualquier ensayo; consulta previa si D1 va a `settings.py`.
1. Línea base: `test pedidos` (se anota el número tras la 04-03).
2. Pruebas primero (tabla siguiente); ver fallar las de los puntos 2, 3, 5, 6 y 8.
3. `utils.py`: validación de estructura (D2), borrado ante cualquier fallo, respaldo de emergencia (D5).
4. `restaurar_bd`: orden validar → confirmar → respaldo de emergencia → comprobar respaldo → registrar antes → restaurar → registrar después, con `finally` para la subida.
5. `restaurar_bd.html`: campo de D3 y mensajes de D6, según `DESIGN.md`.
6. Ensayo en la réplica (ver «Riesgo de ensayar»).
7. `respaldo.md` y `retroceso.md` (caso 3: nombre del respaldo de emergencia).
8. Bitácora, registro, estado «En revisión».

## Pruebas

Todas reemplazan `generar_respaldo_mysql`, `restaurar_bd_mysql` o `subprocess.run` donde los busca el código: **ninguna ejecuta `mysqldump` ni `mysql`**.

| Punto del alcance | Prueba |
| :---------------- | :----- |
| 1 · Extensión, tamaño, estructura | Un `.SQL` válido pasa; un `.txt`, un archivo mayor que el tope, uno sin cabecera, uno sin final y uno con `DROP DATABASE` se rechazan sin llamar al respaldo ni a la restauración. |
| 2 · Aborto | Respaldo de emergencia que lanza excepción (ya existe: `test_capturas_amplias.py:65`) y respaldo que devuelve un archivo vacío o sin final: no se restaura. |
| 3 · Confirmación | POST sin el campo de D3 o con otro texto: no se llama al respaldo ni a la restauración. |
| 4 · Constancia | `assertLogs` con las líneas antes y después; el evento se registra aunque el usuario no exista tras restaurar. |
| 5 · `.sql` vacío | `subprocess.run` lanza `FileNotFoundError`: el `.sql` no queda en `backups/`. **Falla hoy** (`utils.py:58-63` solo cubre `CalledProcessError`). |
| 6 · Subida huérfana | La restauración falla: `backups/tmp/` queda vacío. **Falla hoy.** |
| 7 · Emergencia | El de emergencia lleva el prefijo y no lo borra `limpiar_backups_antiguos` aunque haya cinco respaldos más nuevos; solo se conserva el último de emergencia. |
| 8 · AUD-05-004 | Un `messages.success` de otra pantalla no se pinta como restauración en `restaurar_bd` (la prueba de la 03-04 que lo cubre, citada en AUD-05-004, se revisa y se ajusta). |
| Existentes | `test_capturas_amplias.py:65-91`, `test_acceso.BaseDeDatosPermisosTests` (el POST de usuario común sigue en 302) y `test_contrato_error.py` siguen en verde; las que hacen POST a `restaurar_bd` agregan el campo de D3. |

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
- **Restauración larga en un solo worker:** sigue corriendo dentro de la petición, en tensión con `AGENTS.md`, regla 8.10. Esta iteración no lo cambia (sería otra arquitectura); se anota como propuesta.
- **Disco:** el respaldo de emergencia fuera de la rotación agrega un archivo; despreciable según la medición, sin verificar el uso actual del disco.
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-03.
