# Evidencia 14-04 · RUT del cliente y folio de cotización

- **Fecha del pedido:** 2026-11-27
- **Pedido por:** Claude (chat de traspaso a la Épica 14), para que el desarrollador la complete y Claude Code la dé por registrada.
- **Iteración:** [14-04](iteracion-14-04-rut-del-cliente-y-folio-de-cotizacion.md). Etiqueta propuesta `v14.3-rut-y-folio`; partida y **destino de retroceso `v4.11-csp-observacion`** (decisión del desarrollador, 2026-11-27, dicha por él; `v4.11` queda en `37527b9`).
- **Criterios que dependen de esta evidencia:** los criterios 1 a 5 y 7 de la iteración que solo se pueden comprobar con datos reales (réplica y producción).
- **Estado (2026-11-28, tras el ensayo en la réplica):** **Parte A comprobada salvo A0 (filas 3, 3b, 4 y 5) y A3.** A1, A2 y A2b, comprobados en la consola del desarrollador el 2026-11-28. Faltan los avisos y la hora (A0), el respaldo de producción (A3) y las partes B a E.
- ~~**Estado (2026-11-27, tras el análisis):** **Pendiente.** Registrados el punto de partida informado y el resultado de A0.1 (prueba efímera). Nada de lo demás se ejecutó.~~
- ~~**Estado (2026-11-27):** **Pendiente. No se ejecutó nada.**~~ Este archivo solo deja los pasos y las tablas listos. Nada de lo que está en blanco se completa por inferencia: lo que no se informe queda como «No informado».

> Este archivo existe porque el agente no puede tocar producción, crear etiquetas ni abrir respaldos. Responde solo lo que se pide. **Sin datos de clientes:** nada de nombres, teléfonos ni **RUT reales** (usa solo los sintéticos `12.345.678-5` y `11.111.111-1`); solo conteos, horas, códigos y tipos de error. Nunca pegues el texto completo de una línea del registro (`despliegue.md`, 3.9).
>
> **Orden:** parte A (tu PC: condiciones previas, pruebas, réplica y respaldo) → parte B (etiqueta y servidor) → parte C (día 0, el mismo día) → parte D (retroceso, **solo si** se cumple su regla) → parte E (datos para la fila de `despliegue.md`, sección 5).
>
> **Terminales** (`docs/operacion/despliegue.md`, sección 0): **[PC · PowerShell 7]** en la raíz del repositorio con `.venv` activo; **[PA · Bash]** consola Bash de PythonAnywhere con el entorno virtual activo (`source "$VENV/bin/activate"`, prompt `(venv)`); **[PA · Panel]**; **[Navegador]**.
>
> **Horas:** `server.log` está en **hora de Chile**; `error.log` y la consola de PythonAnywhere, en **UTC** (en noviembre, Chile = UTC−3).

## Lo que debe completar Claude Code al implementar (no lo completa el desarrollador)

Estos datos no existen hasta que la iteración se implemente. Márcalos aquí cuando estén:

| # | Dato | Dónde queda | Estado |
| :- | :--- | :---------- | :----- |
| 1 | Nombres exactos de las migraciones `0010`, `0011` y `0012` | Parte A2 y B5 | **Hecho (2026-11-27, agente):** `0010_rut_y_folio`, `0011_folio_igual_id`, `0012_folio_unico`. `sqlmigrate` [código]: la `0010` emite `CREATE TABLE pedidos_secuenciafolio`, `ADD COLUMN folio integer UNSIGNED DEFAULT 0 NOT NULL CHECK (folio >= 0)` + `ALTER COLUMN folio DROP DEFAULT`, y `ADD COLUMN rut varchar(12) DEFAULT '00.000.000-0' NOT NULL` + `DROP DEFAULT` (Clase 2); la `0011` es `-- Raw Python operation` (datos, sin DDL); la `0012` emite solo `ADD CONSTRAINT pedidos_cotizacion_folio_36c672ad_uniq UNIQUE (folio)`, **sin `MODIFY`** (Clase 2). SQL completo en [bitacora-14-04-implementacion](../../99_bitacora/epica-14-mantenimiento/bitacora-14-04-implementacion.md) |
| 2 | Bloque de `python manage.py shell` del paso único del folio (ensayado en la réplica) | Parte B6 | **Escrito (2026-11-27, agente) y ensayado en la réplica (A2.9 y A2.10), comprobado en la consola del desarrollador el 2026-11-28.** ~~Escrito y ensayado solo en la base de prueba; falta el ensayo en la réplica, A2.9 y A2.10.~~ Bloque: `from pedidos.paso_unico_folio import fijar_inicio_folio` · `ok, texto = fijar_inicio_folio(1000)` · `print(texto)`. Respuesta esperada: `HECHO: contador de folios de cotización, antes: <N>; después: 999. La próxima cotización recibirá el folio 1000.` o `NEGADO: <k> cotización(es) ya tienen folio 1000 o mayor. Contador sin cambios (antes: <N>; después: <N>).` La guarda mira las cotizaciones, no el contador: se puede volver a correr (aviso 2, opción C) |
| 3 | Cantidad de pruebas finales (461 de hoy + las nuevas) con `OK (expected failures=3)` | Parte A1 | **Hecho (2026-11-27, agente):** `Ran 500 tests` (461 + 39 nuevas), `OK (expected failures=3)`, en la base `test_…`. `check`: sin problemas; `makemigrations --check --dry-run`: `No changes detected` |
| 4 | Texto exacto que imprime `verificar_respaldo.py` con un volcado de 19 tablas y con uno de 20 | Partes A3 y B8 | **Hecho (2026-11-27, agente, con volcados ficticios):** script nuevo, 20 tablas → `Tablas esperadas encontradas: 20 de 20`, `Tablas faltantes: ninguna`, `Resultado: VÁLIDO`, código 0. Script nuevo, 19 tablas → `Tablas esperadas encontradas: 19 de 20`, `Tablas faltantes: pedidos_secuenciafolio`, `Resultado: NO VÁLIDO (1 tabla(s) faltante(s))`, código 1. **Por eso el respaldo previo (A3, 19 tablas) se verifica con la versión de `v4.11`:** `git show v4.11-csp-observacion:scripts/verificar_respaldo.py > "$env:TEMP\verificar_respaldo_v411.py"` y `python "$env:TEMP\verificar_respaldo_v411.py" "<ruta>"` → `19 de 19`, `VÁLIDO` (`respaldo.md`; el mismo trato que tuvieron los de 18 tablas) |
| 5 | Lista de archivos que debe mostrar `git diff --stat v4.11-csp-observacion v14.3-rut-y-folio` | Parte B1 | **Hecho (2026-11-27, agente), según el árbol de trabajo:** código `pedidos/models.py`, `pedidos/validadores.py` (nuevo), `pedidos/paso_unico_folio.py` (nuevo), `pedidos/views.py`, `pedidos/migrations/0010_rut_y_folio.py`, `0011_folio_igual_id.py`, `0012_folio_unico.py` (nuevas), `pedidos/static/pedidos/js/index.js`, plantillas `cotizacion_confirm_delete.html`, `cotizacion_convertir.html`, `cotizacion_detail.html`, `cotizacion_form.html`, `cotizacion_list.html`, `cotizacion_pdf.html`, `pedido_form.html`, `scripts/verificar_respaldo.py`; pruebas `pedidos/tests/factorias.py`, `test_acceso.py`, `test_cotizaciones.py`, `test_eventos_negocio.py`, `test_rut_folio.py` y `test_verificar_respaldo.py` (nuevas); documentos `docs/operacion/despliegue.md`, `respaldo.md` y `_planificacion/`. **No** debe aparecer `requirements.txt`, `PedidosApp/settings.py` ni `pedidos/admin.py` (sin cambios) |

## Decisiones que fijan estos pasos

| Tema | Decisión | Dónde se aplica |
| :--- | :------- | :-------------- |
| RUT | Obligatorio; los clientes existentes reciben `00.000.000-0`, que se rechaza si alguien lo escribe (D1 y D2, 2026-11-20) | A2, C |
| Folio | Columna propia, distinta del `id`; las existentes reciben `folio = id`; el «1000» es un paso único y manual, no código (D3 a D5) | A2, B6, C |
| Migraciones | `0010` (estructura, Clase 2), `0011` (datos) y `0012` (solo el índice único, Clase 2), confirmadas con `sqlmigrate` (opción C, 2026-11-20) | A2, B5 |
| Orden de despliegue | Después de la 04-09 (**ya desplegada el 2026-11-27**, `v4.11-csp-observacion`) | B |
| Retroceso | `v4.11-csp-observacion`, **con restauración del respaldo previo** (hay migraciones con datos y una tabla nueva) | D |
| Respaldo | Previo verificado (19 tablas) y posterior verificado (20 tablas) | A3, B8 |
| Avisos al dueño y al cliente | Antes del despliegue: explicación del 2026-11-27 y confirmación de los dos puntos que pide (RUT obligatorio; clientes antiguos piden su RUT real al editarse) | A0 |

## Punto de partida (2026-11-27)

| Dato | Valor | Origen |
| :--- | :---- | :----- |
| Versión en producción | `v4.11-csp-observacion`, `37527b9` | Consola del desarrollador, 2026-11-27 |
| Un solo arranque de uWSGI | 10:54:00 (hora de Chile) | Consola |
| Última migración aplicada | `0009_acceso_bloqueado` | Documentos (la 14-04 trae `0010` a `0012`) |
| Tablas del respaldo vigente | 19 | `verificar_respaldo.py` y `despliegue.md` |
| Pruebas | 461, `OK (expected failures=3)` | Consola del desarrollador, 2026-11-27 |
| Variables `.env` que se conservan | `ACCESO_PROXIES_CONFIABLES=1`, `ACCESO_FALLOS_POR_DIRECCION=20` | Consola |
| Modo estricto de MySQL en producción | **No está activado** (`mysql.W002`, AUD-02-020) | Consola; relevante para el aviso 1 de abajo |
| Web app vence | 2026-12-13 | Dicho |
| Procedimiento del despliegue de partida (04-09) | Sin desviaciones | Consola del desarrollador, 04-09 |
| Producción: clientes y cotizaciones | ~~870 clientes~~ (dicho, reemplazado) **872 clientes**; 33 cotizaciones, id 2 a 34, ninguna con id ≥ 1000; 1.051 pedidos, 22 sin fecha de entrega, 1 de ellos con edición registrada (cota superior de AUD-05-026) | Consola, 2026-11-27 ~21:41 (hora de Chile), consultas de solo lectura de la bitácora del análisis |
| Réplica: clientes y cotizaciones | ~~824 clientes; 33 cotizaciones; refrescada el 2026-11-18 (dicho)~~ **Refrescada el 2026-11-27** con `respaldo_27-11-2026_10-51-07.sql` (1.585.017 bytes, SHA-256 `2126d253bace…`, `VÁLIDO`, 19 de 19); restauración 5,5 s; paridad 0 diferencias; 19 tablas; última migración `0009`. 869 clientes; 33 cotizaciones (id 2 a 34), 0 con id ≥ 1000; 1.049 pedidos, 22 sin fecha, 1 con edición registrada | Consola, 2026-11-27. La diferencia con producción (3 clientes, 2 pedidos) sería actividad posterior al respaldo [inferido] |
| Cifrado de la réplica | Comprobado **después** de restaurar: D: con BitLocker 100,0 % y protección activada; disco de Docker en `D:\Docker\datos_nuevos_nov_2026\DockerDesktopWSL`; nada en C: ni en Descargas | Consola, 2026-11-27 |
| `MAX(id)` de las cotizaciones | 34 en réplica y producción: el paso único **no** se niega | Consola, 2026-11-27 |

## Avisos para la implementación y el despliegue (2026-11-27)

1. **Ventana entre `migrate` y el Reload** *(inferido; no comprobado)*. Con el esquema nuevo y el código viejo todavía cargado, una cotización o un cliente creados en esa ventana no traen `folio` ni `rut`. Como producción no tiene el modo estricto de MySQL, el motor no los rechazaría: guardaría `folio = 0` y `rut` vacío, y el segundo folio 0 chocaría con el índice único de la `0012`. ~~Qué hacer queda `PENDIENTE_DESARROLLADOR`~~ **Decidido el 2026-11-27 [dicho]: opción A**: hora de poco uso, aviso al dueño de no crear clientes ni cotizaciones durante la actualización, conteo en la parte C (filas 9 a 11) y plan de contingencia escrito en la iteración («Riesgos y avisos»), sin código.
2. **Los folios de prueba se consumen.** La validación del día 0 pide ver la primera cotización nueva con folio 1000; si es de prueba y se borra, el contador no la reutiliza y la primera real saldría 1001. ~~Qué cotización se usa para validar queda `PENDIENTE_DESARROLLADOR`~~ **Decidido el 2026-11-27 [dicho]: opción C**: cotización de prueba; se borra (antes que su cliente de prueba) y se vuelve a correr el paso único, cuya guarda mira las cotizaciones existentes con folio ≥ 1000 (no el contador) y anota el valor antes y después (parte C, filas 4b a 4d).
3. **El paso 2 de la iteración dice «`git pull` en el servidor».** Está **corregido en esta evidencia**: en el servidor solo se hace `git fetch origin --tags` y `git checkout <etiqueta>` (`despliegue.md`, 3.2). Corregir también la iteración al empezar.
4. **La numeración visible se muestra sin separador de miles** (`USE_THOUSAND_SEPARATOR = True`): 1000, no ~~1.000~~ `1 000` (con `es-cl` el separador es un espacio; H4 del análisis). Se mira en pantalla, PDF y nombre del archivo (parte C).
5. **Sin scripts ni estilos en línea nuevos:** desde `v4.11` cada pieza en línea suma trabajo a la 08-08.
6. **AUD-05-026 (fecha de entrega vacía al editar un pedido)** comparte `forms.py` con esta iteración. ~~Su resultado de comprobación decide el orden (parte A0).~~ **Decidido el 2026-11-27 [dicho]:** queda Media y se arregla **después** de la 14-04, en iteración propia (14-05, número al redactarla).

---

## Parte A · Tu PC: condiciones previas, pruebas, réplica y respaldo

### A0. Condiciones previas

| # | Condición | Resultado | Estado |
| :- | :-------- | :-------- | :----- |
| 1 | Comprobación de AUD-05-026. ~~En la réplica (pedido nº, fecha antes, ¿vacía al editar?, resultado al guardar, fecha después)~~ **Método usado (2026-11-27, agente):** prueba efímera en la base de prueba (`test_…`, fuera del repositorio), que abre el formulario de edición, toma el `value` pintado, le aplica la regla del estándar HTML para `type="date"` (un valor que no es `aaaa-mm-dd` se envía vacío) y envía el formulario sin tocar la fecha | **Pedido:** el widget pinta `value="15/12/2026"`; el navegador envía `''`; respuesta 302 y `fecha_entrega` queda `None` (**se pierde**). **Cotización:** la plantilla escribe el campo a mano con `\|date:'Y-m-d'` (`cotizacion_form.html:334`, `type="text"`, `readonly`): se envía `2026-12-15` y la fecha se conserva. **Control «Reabrir»:** pinta `2026-12-15`. La parte del navegador está emulada, no observada; coincide con el aviso de consola dicho en la 04-09. Confirmación en la réplica con navegador: opcional, la hace el desarrollador | Hecho (prueba efímera) |
| 2 | ~~Si la fecha se pierde al guardar: arreglo urgente desplegado **antes** de esta iteración (etiqueta y fecha) y retroceso de la 14-04 ajustado~~ | No aplica: AUD-05-026 queda Media y va **después** (decisión del 2026-11-27, dicha); retroceso sigue en `v4.11-csp-observacion` | No aplica |
| 3 | El dueño fue avisado (canal, día y hora; sin su texto completo) | | No informado |
| 4 | El cliente respondió a la explicación del 2026-11-27 (RUT obligatorio; clientes antiguos piden su RUT real) | | No informado |
| 3b | El dueño fue avisado de **no crear clientes ni cotizaciones** durante la actualización (aviso 1, opción A) | | No informado |
| 5 | Hora o ventana de baja actividad elegida para el despliegue (aviso 1, opción A) | | No informado |
| 6 | Qué cotización se usará para validar el folio 1000 (aviso 2) | Opción C: una de prueba, que se borra antes que su cliente de prueba, y se re-corre el paso único (decisión del 2026-11-27, dicha) | Decidido |

### A1. Pruebas y comprobaciones

**[PC · PowerShell 7]** con la réplica arriba (`docker compose up -d`) y `$env:DB_NAME = "manzagrafica_replica"`:

```powershell
python manage.py test pedidos
python manage.py check
python manage.py makemigrations --check --dry-run
```

| # | Comando | Esperado | Resultado | Estado |
| :- | :------ | :------- | :-------- | :----- |
| 1 | `test pedidos` | `Ran N tests` (461 + nuevas) y `OK (expected failures=3)` | `Ran 500 tests` en 604 s, `OK (expected failures=3)` | Comprobado (consola del desarrollador, 2026-11-28) |
| 2 | `check` | `no issues` | Sin problemas | Comprobado (consola del desarrollador, 2026-11-28) |
| 3 | `makemigrations --check --dry-run` | `No changes detected` (con las tres migraciones ya en el repositorio) | `No changes detected` | Comprobado (consola del desarrollador, 2026-11-28) |
| 4 | `grep` del número 1000 en código y migraciones (criterio 6) | ~~Ninguna coincidencia~~ **Ninguna coincidencia que sea el folio** (ajustado el 2026-11-28: el código ya tenía usos del número ajenos al folio) | Solo coincidencias preexistentes: el lienzo SVG de 1000×400, la clase `duration-1000`, `data-desbloquear-ms="10000"` y los textos de ejemplo de `cotizacion_form.html:289` y `producto_form.html:44`. Ninguna en el diff de la 14-04 (`git diff 6815ef3 e82c9cf`) | Comprobado (consola del desarrollador, 2026-11-28) |

### A2. Réplica: respaldo, migraciones y ensayo

Todo en una sola ventana. **Nunca** `docker compose down -v` ni `docker volume rm`.

| # | Paso | Esperado | Resultado | Estado |
| :- | :--- | :------- | :-------- | :----- |
| 1 | Paridad: `python scripts\diagnostico\paridad_replica.py` | `PARIDAD con diferencias aceptadas` | 0 diferencias no aceptadas y 1 aceptada (Python 3.13.0 frente a 3.13.1); 19 tablas; 22 de 22 comprobaciones | Comprobado (consola del desarrollador, 2026-11-28) |
| 2 | Respaldo de la réplica antes de migrar (como `despliegue.md`, 3.13 A, paso 2), con `verificar_respaldo.py` y `revisar_volcado_d2.py` | `VÁLIDO` y `CUMPLE D2` | `replica_antes_14-04.sql`, 1.585.767 bytes, SHA-256 `2ef41d7845ba…`; `VÁLIDO`, 19 de 19 con el verificador de `v4.11`; `CUMPLE D2` | Comprobado (consola del desarrollador, 2026-11-28) |
| 3 | `sqlmigrate` de la `0010` | `ALTER`/`CREATE` aditivos; las columnas nuevas nacen `NOT NULL` con relleno en el mismo paso | Plan: `0010`, `0011` y `0012`. Aditiva: `CREATE TABLE pedidos_secuenciafolio`; `ADD COLUMN` de `folio` y de `rut`, cada una seguida de su `DROP DEFAULT` | Comprobado (consola del desarrollador, 2026-11-28) |
| 4 | `sqlmigrate` de la `0011` | Sin DDL (solo datos) | Operación Python, sin DDL | Comprobado (consola del desarrollador, 2026-11-28) |
| 5 | `sqlmigrate` de la `0012` | **Solo** el índice único de `folio`; **ningún `MODIFY` de la columna** (si lo hay, es Clase 3: se detiene) | Solo `ADD CONSTRAINT … UNIQUE (folio)`, sin `MODIFY` | Comprobado (consola del desarrollador, 2026-11-28) |
| 6 | `migrate`; después `showmigrations pedidos` | `[X]` en `0010`, `0011` y `0012` | `migrate` OK; `[X]` en `0010` a `0012` | Comprobado (consola del desarrollador, 2026-11-28) |
| 7 | Conteos: clientes totales; clientes con `00.000.000-0`; cotizaciones totales; cotizaciones con `folio = id`; valor del contador | Los dos primeros iguales; los dos siguientes iguales; contador = mayor folio | 869 clientes, 869 con `00.000.000-0`; 33 cotizaciones, 33 con `folio = id`; mayor folio 34; contador 34 | Comprobado (consola del desarrollador, 2026-11-28) |
| 8 | Reversa de la `0011` ensayada (`migrate pedidos 0010` y de vuelta) | Sin errores; datos intactos | Ida y vuelta OK; después, 869 clientes, 33 cotizaciones y contador 34 | Comprobado (consola del desarrollador, 2026-11-28) |
| 9 | **Paso único del folio ensayado:** valor antes, valor después, folio de la primera cotización nueva | Antes: mayor folio; después: `999`; primera nueva: `1000` | `HECHO`, antes: 34; después: 999. Primera cotización nueva: folio 1000 | Comprobado (consola del desarrollador, 2026-11-28) |
| 10 | El paso único se **niega** si ya hay folios ≥ 1000 | Se ensaya contra una copia con un folio ≥ 1000 | Con una cotización de folio ≥ 1000: `NEGADO`. Después, limpieza de los datos de prueba (cotizaciones, pedido y clientes) y nueva corrida: `HECHO`, sin errores (opción C del aviso 2). Los valores exactos de las salidas (cantidad negada, antes y después de la nueva corrida): no informado | Comprobado (consola del desarrollador, 2026-11-28); valores exactos no informados |

### A2b. Revisión manual en la réplica (escritorio y 360 px)

Solo resultados; sin RUT reales ni nombres de clientes.

| # | Caso | Esperado | Resultado | Estado |
| :- | :--- | :------- | :-------- | :----- |
| 1 | Editar un cliente existente sin cambiar el RUT | Muestra `00.000.000-0` y **rechaza** guardar | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 2 | Escribir `00.000.000-0` a mano | Rechazado | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 3 | Escribir `12.345.678-5`, `12345678-5` y `123456785` | Aceptados y guardados como `12.345.678-5` | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 4 | Escribir `12.345.678-4` (dígito erróneo) y `12.345.67A-5` | Rechazados | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 5 | Crear cliente rápido (modal) sin RUT, y con `11.111.111-1` | Sin RUT: rechazado; con RUT: crea | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 6 | Crear una cotización: folio asignado | Siguiente correlativo, sin separador de miles | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 7 | Detalle y PDF de la cotización | Muestran el RUT del cliente y el folio; el nombre del archivo trae el folio | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 8 | Listado y búsqueda por folio | Lo encuentra | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 9 | Convertir una cotización a pedido y eliminar una cotización | Los mensajes dicen «folio N»; sin 500 | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 10 | Dos cotizaciones creadas casi a la vez (dos pestañas) | Folios distintos | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |
| 11 | Un error forzado al guardar una cotización | El folio **no** queda consumido | Como se esperaba. **Prueba débil:** desde el navegador no se puede forzar un fallo dentro del guardado; la garantía es la prueba automática de transacción revertida (`test_rut_folio.py`) [inferido] | Comprobado (escritorio y 360 px, 2026-11-28), con esa salvedad |
| 12 | Consola del navegador (`F12`) en las pantallas tocadas | Sin mensajes `[Report Only]` nuevos de scripts o estilos en línea | Sin mensajes `[Report Only]` nuevos | Comprobado (escritorio y 360 px, 2026-11-28) |
| 13 | A 360 px | Todo se lee completo, sin barra horizontal | Como se esperaba | Comprobado (escritorio y 360 px, 2026-11-28) |

Limpieza: `Ctrl+C` en `runserver`, `Remove-Item Env:DB_NAME`, `docker compose stop`.

### A3. Respaldo de producción ANTES (con `v4.11-csp-observacion` activo)

Genera desde la app («Respaldar BD», **un solo clic**) y descarga a tu carpeta de respaldos, fuera del repositorio. **[PC · PowerShell 7]**:

```powershell
python scripts\verificar_respaldo.py "<ruta del respaldo descargado>"
python scripts\diagnostico\revisar_volcado_d2.py "<ruta del respaldo descargado>"
$LASTEXITCODE
Get-FileHash "<ruta del respaldo descargado>" -Algorithm SHA256
```

| Dato | Esperado | Resultado | Estado |
| :--- | :------- | :-------- | :----- |
| Nombre del archivo | | | No informado |
| Tamaño (bytes) | | | No informado |
| SHA-256 | | | No informado |
| `verificar_respaldo.py` | `VÁLIDO` (19 tablas; texto exacto lo fija el dato 4 de la tabla inicial) | | No informado |
| `revisar_volcado_d2.py` | `RESULTADO: CUMPLE D2` | | No informado |
| Código de salida | `0` | | No informado |
| Hora (rotación en `error.log`, UTC) | Anterior al checkout | | No informado |

**Con migraciones y una tabla nueva, este respaldo es obligatorio.** Si algo no cumple, no sigas.

---

## Parte B · Etiqueta y servidor

### B1. Etiqueta (PC)

**[PC · PowerShell 7]** (`despliegue.md`, sección 1; el día del despliegue):

```powershell
git status --short
git fetch origin --tags
git rev-parse --short HEAD
git rev-parse --short origin/main
git diff --stat v4.11-csp-observacion HEAD
$hoy = Get-Date -Format "yyyy-MM-dd"
git tag -a v14.3-rut-y-folio -m "Iteración 14-04 · desplegada el $hoy"
git tag -n v14.3-rut-y-folio
git push origin v14.3-rut-y-folio
```

| # | Comprobación | Esperado | Resultado | Estado |
| :- | :----------- | :------- | :-------- | :----- |
| 1 | `git status --short` | Sin salida | | No informado |
| 2 | `HEAD` y `origin/main` | El mismo hash | | No informado |
| 3 | `git diff --stat` | Solo los archivos de la iteración (dato 5 de la tabla inicial) y documentos; **no** `requirements.txt` (inferido) ni `pedidos/static/` salvo `index.js` | | No informado |
| 4 | `git tag -n` | `Iteración 14-04 · desplegada el <fecha de hoy>` | | No informado |
| 5 | `push` | `[new tag]`; si dice `already exists` o `rejected`, **no fuerces**: usa el correlativo siguiente | | No informado |

### B2. Servidor antes

**[PA · Bash]**

```bash
cd "$PROYECTO"
source "$VENV/bin/activate"
which python
git status --short
git rev-parse --short HEAD
git describe --tags
grep -E '^ACCESO_' .env
grep -c '^CSP_OBSERVACION' .env
```

| # | Comprobación | Esperado | Resultado | Estado |
| :- | :----------- | :------- | :-------- | :----- |
| 1 | Prompt `(venv)` y `which python` | El entorno virtual | | No informado |
| 2 | `git status --short` | Sin salida | | No informado |
| 3 | `git describe --tags` | `v4.11-csp-observacion` (`37527b9`) | | No informado |
| 4 | `ACCESO_` | Las dos líneas (`...POR_DIRECCION=20`, `...PROXIES_CONFIABLES=1`) | | No informado |
| 5 | `CSP_OBSERVACION` | `0` | | No informado |

### B3. Checkout

**[PA · Bash]** (**no** `git pull`):

```bash
git fetch origin --tags
git checkout v14.3-rut-y-folio
git describe --tags
git rev-parse --short HEAD
git status --short
```

| # | Comprobación | Esperado | Resultado | Estado |
| :- | :----------- | :------- | :-------- | :----- |
| 1 | `describe` | `v14.3-rut-y-folio`; prompt `(HEAD detached at v14.3-rut-y-folio)` | | No informado |
| 2 | `rev-parse` | El hash de la etiqueta | | No informado |
| 3 | `git status --short` | Sin salida | | No informado |

### B3b. Estáticos (después del checkout, antes de migrar; H2, 2026-11-27)

**[PA · Bash]** (cambia `index.js`):

```bash
python manage.py collectstatic --noinput
```

| # | Comprobación | Esperado | Resultado | Estado |
| :- | :----------- | :------- | :-------- | :----- |
| 1 | `collectstatic` | `1 static file copied` (o el número que fije el dato 5), sin errores | | No informado |

Después del Reload (B7), **[Navegador]** `Ctrl+F5` en el formulario de pedidos y en el de cotizaciones antes de usar el modal.

### B4. Revisión antes de migrar

**[PA · Bash]**

```bash
python manage.py migrate --plan
python manage.py check --deploy
```

| # | Comprobación | Esperado | Resultado | Estado |
| :- | :----------- | :------- | :-------- | :----- |
| 1 | `migrate --plan` | **Solo** `0010`, `0011` y `0012` | | No informado |
| 2 | `check --deploy` | Solo W005 y W021 | | No informado |

Si sale otra cosa, **no migres**: `git checkout v4.11-csp-observacion`.

### B5. Migración

**[PA · Bash]** (aviso 1: la ventana empieza aquí y termina con el Reload; hazla corta)

```bash
python manage.py migrate
python manage.py showmigrations pedidos
```

| # | Comprobación | Esperado | Resultado | Estado |
| :- | :----------- | :------- | :-------- | :----- |
| 1 | `migrate` | `Applying ...0010... OK`, `0011` y `0012` | | No informado |
| 2 | `showmigrations pedidos` | `[X]` en las tres | | No informado |
| 3 | Hora del `migrate` (Chile) | Anotar | | No informado |

Si `migrate` falla a medias, detente y sigue `retroceso.md` (caso 2). Anota cuál quedó aplicada.

### B6. Paso único del folio

El bloque de `python manage.py shell` lo escribe y ensaya Claude Code en la réplica (dato 2 de la tabla inicial). **Antes de crear la primera cotización nueva.**

| # | Dato | Esperado | Resultado | Estado |
| :- | :--- | :------- | :-------- | :----- |
| 1 | Valor del contador **antes** | El mayor folio existente | | No informado |
| 2 | ¿El bloque se negó (había folios ≥ 1000)? | No | | No informado |
| 3 | Valor del contador **después** | `999` | | No informado |

### B7. Un solo Reload

Calcula y valida `DESDE_CL` justo antes de pulsar Reload, en la misma consola:

```bash
DESDE_CL="$(TZ=America/Santiago date -d '1 minute ago' '+%Y-%m-%d %H:%M:%S')"
echo "DESDE_CL=$DESDE_CL"
echo "$DESDE_CL" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$' && echo "DESDE_CL válido"
```

**[PA · Panel]** Reload **una vez**. Después, **[PA · Bash]**:

```bash
S=/var/log/manzagrafica.pythonanywhere.com.server.log
for f in "$S" "$S".*; do [ -f "$f" ] && zcat -f "$f"; done \
  | awk -v d="$DESDE_CL" '/^20[0-9][0-9]-[0-9][0-9]-[0-9][0-9] [0-9:]+ \*\*\* Starting uWSGI/ && substr($0,1,19) >= d { print substr($0,1,19), "Starting uWSGI" }' \
  | sort
```

| # | Dato | Esperado | Resultado | Estado |
| :- | :--- | :------- | :-------- | :----- |
| 1 | `DESDE_CL` y «válido» | Hora de Chile de un minuto antes y `DESDE_CL válido` | | No informado |
| 2 | «Starting uWSGI» | **Una** línea; anota su hora (es `R`, la hora oficial del Reload) | | No informado |

### B8. Respaldo posterior (PC)

Genera otro respaldo desde la app y verifícalo como en A3.

| Dato | Esperado | Resultado | Estado |
| :--- | :------- | :-------- | :----- |
| Nombre, tamaño y SHA-256 | | | No informado |
| `verificar_respaldo.py` | `VÁLIDO` con **20** tablas (texto exacto: dato 4 de la tabla inicial) | | No informado |
| `revisar_volcado_d2.py` | `CUMPLE D2` | | No informado |

---

## Parte C · Día 0 (el mismo día, RDA-021)

Sin esperas de 3, 5 ni 7 días: el despliegue se valida hoy y se respalda con el plan de retroceso. Sin RUT reales: para escribir un RUT usa los sintéticos.

**[Navegador]** en ventana privada. No guardes cambios en clientes reales.

| # | Caso | Esperado | Resultado | Estado |
| :- | :--- | :------- | :-------- | :----- |
| 1 | Acceso y panel | Sin 500 | | No informado |
| 2 | Editar un cliente existente **sin cambiar el RUT** | Muestra `00.000.000-0` y rechaza guardar (no guardes nada) | | No informado |
| 3 | Crear un cliente de prueba con `12.345.678-5` y borrarlo | Se crea con ese RUT normalizado y se borra | | No informado |
| 4 | Cotización de validación (aviso 2): folio en pantalla | `1000` (sin punto de miles) | | No informado |
| 5 | Mismo folio en el PDF y en el nombre del archivo | `1000` | | No informado |
| 4b | Borrar la cotización de prueba y **después** su cliente de prueba (`PROTECT` impide el orden inverso) | Ambos borrados | | No informado |
| 4c | Re-correr el paso único (aviso 2, opción C): valor antes y después | Antes `1000`; después `999`; no se niega (ninguna cotización existente con folio ≥ 1000) | | No informado |
| 4d | Modal de cliente rápido tras `Ctrl+F5`: pide RUT y rechaza vacío (sin guardar o con el sintético, borrado después) | Rechazo sin RUT | | No informado |
| 6 | RUT del cliente en el PDF y en el detalle | Se ve | | No informado |
| 7 | Listado y búsqueda por folio | Lo encuentra | | No informado |
| 8 | Consola del navegador (`F12`) | Sin mensajes `[Report Only]` nuevos de piezas en línea | | No informado |

**Integridad (aviso 1):** número de clientes con `rut` vacío y de cotizaciones con `folio = 0` o repetido, contados con el bloque que fije Claude Code (solo conteos).

| # | Dato | Esperado | Resultado | Estado |
| :- | :--- | :------- | :-------- | :----- |
| 9 | Clientes con `rut` vacío | 0 | | No informado |
| 10 | Cotizaciones con `folio = 0` o repetido | 0 | | No informado |
| 11 | Clientes con `00.000.000-0` | Igual al total de clientes anteriores | | No informado |

**Registros desde el último «Starting uWSGI»**, contados **después** de usar las pantallas (anota la hora del conteo, en Chile). **[PA · Bash]**:

```bash
S=/var/log/manzagrafica.pythonanywhere.com.server.log
E=/var/log/manzagrafica.pythonanywhere.com.error.log
TZ=America/Santiago date "+%F %T (hora de Chile)"
awk 'FNR==NR { if (/\*\*\* Starting uWSGI/) n=FNR; next } FNR==n { print substr($0,1,19), "último Starting uWSGI" } FNR>n && /Traceback|OperationalError|IntegrityError|gone away|TemplateDoesNotExist/ { c++ } END { print "coincidencias desde el arranque:", c+0 }' "$S" "$S"
tail -n 80 "$E"
```

| # | Dato | Esperado | Resultado | Estado |
| :- | :--- | :------- | :-------- | :----- |
| 12 | Hora del conteo (Chile) | Anotar | | No informado |
| 13 | `coincidencias desde el arranque` | `0` | | No informado |
| 14 | `error.log` desde la hora UTC del arranque | Sin entradas nuevas | | No informado |

---

## Parte D · Retroceso (solo si se cumple la regla)

**Regla propuesta** *(`PENDIENTE_DESARROLLADOR`: confirmar o ajustar antes del despliegue)*: se retrocede si hay datos incorrectos (folio repetido o en cero, RUT perdido, cotizaciones sin folio), o dos o más `5xx` en la misma ruta tocada por la iteración sin causa explicada. Un `5xx` suelto se investiga.

- Destino: `v4.11-csp-observacion`, **con restauración del respaldo previo** (`retroceso.md`: casos 2 y 3).
- Antes de volver el código: decidir si se revierten las migraciones (`migrate pedidos 0009`; la `0011` tiene reversa definida) o se restaura el respaldo de A3.

| # | Dato | Resultado | Estado |
| :- | :--- | :-------- | :----- |
| 1 | ¿Se retrocedió? (sí/no y por qué) | | No informado |
| 2 | Caso de `retroceso.md` aplicado y hora (Chile) | | No informado |
| 3 | Etiqueta de destino y `git describe` posterior | | No informado |
| 4 | Resultado de la verificación posterior | | No informado |

---

## Parte E · Datos para la fila de `despliegue.md`, sección 5

| Campo | Valor | Estado |
| :---- | :---- | :----- |
| Fecha y hora del Reload (`Starting uWSGI`, Chile) | | No informado |
| Etiqueta | `v14.3-rut-y-folio` | |
| Commit de la etiqueta | | No informado |
| Iteración | 14-04 (RUT del cliente y folio de cotización; partida y retroceso `v4.11-csp-observacion`); con migraciones `0010` a `0012` (`sqlmigrate`: clases confirmadas), sin `pip`; ~~`collectstatic` solo si cambió `index.js`~~ **con `collectstatic`** (cambia `index.js`, H2) y `Ctrl+F5` | |
| Respaldo previo (nombre, tamaño, SHA-256, resultado) | | No informado |
| Respaldo posterior (nombre, tamaño, SHA-256, 20 tablas) | | No informado |
| Resultado general | | No informado |
| Pruebas previas | | No informado |
| Retroceso del despliegue siguiente | `v14.3-rut-y-folio` (previo `v4.11-csp-observacion`) | |

## Desviaciones de la ejecución

Se llena durante la ejecución: qué estaba previsto, qué pasó y qué efecto tuvo. Nada se completa por inferencia.

| # | Estaba previsto | Pasó | Efecto |
| :- | :-------------- | :--- | :----- |
| | | | |

## Hallazgos nuevos

| ID | Qué | Gravedad (propuesta) | Origen |
| :- | :-- | :------------------- | :----- |
| | | | |

## Qué no consta (se completa al cerrar)

- Lo que el desarrollador no informe queda aquí, con su motivo.
- **A2.10 (2026-11-28):** las salidas exactas de la negativa y de la nueva corrida (cuántas cotizaciones tenían folio ≥ 1000, y los valores antes y después) no se pegaron. Consta el resultado («NEGADO», limpieza y «HECHO» sin errores), no los números.
