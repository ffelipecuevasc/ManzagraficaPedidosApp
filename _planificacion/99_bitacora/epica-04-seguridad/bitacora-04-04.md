# Bitácora 04-04 · Endurecimiento de la restauración

- **Fecha:** 2026-11-19
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Implementada, pendiente de ensayo y despliegue. Etiqueta prevista `v4.6-restauracion`, sin fecha fija (RDA-021); retroceso `v4.5-credenciales`. El formato D2 sobre respaldos reales y el ensayo en la réplica están **pendientes de ejecutar por el desarrollador**.
- **Regla:** ningún valor de clave, ningún contenido de volcado y ningún nombre de persona en este documento.

## Resumen

D1 a D5 implementados; D6 respetada (AUD-05-004 sin tocar). La restauración valida extensión (sin mayúsculas), tamaño (20 MB) y estructura (ocho reglas de D2) antes del respaldo de emergencia; exige `RESTAURAR` en el servidor; no restaura si el respaldo de emergencia falla o sale incompleto; deja dos líneas en `server.log` y el evento con usuario nulo si el volcado no trae al usuario; borra siempre la subida. `generar_respaldo_mysql` ya no deja un `.sql` vacío ante ningún fallo, y el respaldo `emergencia_` queda fuera de la rotación, solo el último. Pruebas primero. Sin migraciones ni configuración.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/utils.py` | `TOPE_VOLCADO_BYTES`, `PREFIJO_EMERGENCIA`, `revisar_volcado()`, `volcado_valido()`, `generar_respaldo_mysql(prefijo=…)` con borrado ante cualquier fallo y «solo el último» de emergencia; rotación sin `emergencia_` (CRLF). |
| `pedidos/views.py` | `restaurar_bd` reordenado con `finally`; textos `TEXTO_VOLCADO_INVALIDO` y `TEXTO_CONFIRMACION`; `respaldar_bd` marca `emergencia_` (LF). |
| `pedidos/templates/pedidos/restaurar_bd.html` | Campo `RESTAURAR` con etiqueta y ayuda; `reportValidity()` antes del aviso (CRLF). |
| `pedidos/templates/pedidos/respaldar_bd.html` | Etiqueta «Emergencia» (CRLF). |
| `pedidos/tests/test_restauracion_endurecida.py` | Nuevo: 33 pruebas. |
| `pedidos/tests/ayudas.py` | `VOLCADO_VALIDO`, `volcado_subido`, `datos_restaurar`, `respaldo_de_emergencia`. |
| `pedidos/tests/test_capturas_amplias.py`, `test_contrato_error.py`, `test_eventos_negocio.py` | Envían un volcado válido y `RESTAURAR`; el respaldo previo simulado es un `emergencia_` válido. |
| `docs/operacion/despliegue.md` | Sección 3.11 (orden y paso a paso) y fila en la sección 5 (CRLF). |
| `docs/operacion/respaldo.md`, `retroceso.md` (caso 3), `replica-local.md` | Comportamiento desde `v4.6`, nombre del respaldo de emergencia y excepción nueva. |
| Iteración, `definicion-epica-04.md`, `registro-pendientes.md` (CRLF) | Estado. |

**Fuera del repo** (carpeta temporal de la sesión del agente; si se borra antes del ensayo, se piden de nuevo):

- `C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-04\revisar_volcado_d2.py`
- `C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-04\puente_ensayo_04_04.py`

## Correcciones a la redacción

- Referencias de línea obsoletas: `restaurar_bd` en `views.py:1286` (antes del cambio), protección de la base de pruebas hacia `settings.py:199`, `utils.py` cambiado por la 04-03.
- «El ensayo puede exigir el cliente de MySQL» queda superado por el puente.
- `RESTAURAR` repite el criterio de `ELIMINAR` (`views.py:396`) en línea; no se propone extraer una función (dos líneas).
- `respaldar_bd.html` no estaba en la lista de archivos, pero D5 pide que la pantalla marque el de emergencia.

## Verificación

- Línea base: 342 pruebas, `OK (expected failures=4)` (cierre de la 04-03).
- Pruebas nuevas antes del cambio: 33, `FAILED (failures=22, errors=21)` (los fallos cuentan subcasos). Pasaban de antemano las que protegen lo que ya funcionaba (`.txt` rechazado, evento con su usuario, `CalledProcessError` sin archivo, restauración correcta sin subida).
- Primera corrida completa con el cambio: 375 pruebas, 9 fallos, todos de la propia prueba: en los subcasos, los mensajes de la petición anterior se acumulan sin seguir la redirección; se comparó el último mensaje.
- Después: ver «Resultado final» al pie.
- `check` y `makemigrations --check --dry-run`: ver «Resultado final».
- **Revisión a 360 px de `restaurar_bd.html`: no hecha por el agente** (no abrió el navegador). El campo usa `w-full` y las mismas clases que el de la 04-10, ya revisado a 360 px; la revisión queda para el desarrollador antes del despliegue.
- El script de D2 se probó solo sobre un archivo sintético (sin datos): `CUMPLE D2`. El puente compila; **no se ejecutó**.

## Formato D2 (reglas que revisa el script, las mismas de la aplicación)

`no_vacio`, `dentro_del_tope` (≤ 20 MB), `texto_utf8`, `cabecera_mysql_dump` (primera línea con texto empieza con `-- MySQL dump`), `linea_de_cierre` (última con texto empieza con `-- Dump completed`), `tabla_pedidos_pedido` y `tabla_django_migrations` (línea que empieza con su `CREATE TABLE`), `sin_sentencias_prohibidas` (`CREATE DATABASE`, `DROP DATABASE`, `USE`, `GRANT`, `CREATE USER` al inicio de una línea, también dentro de `/*!NNNNN … */`). **Inferido, se confirma con el script:** que los respaldos reales de producción y de la réplica cumplen las ocho.

## Orden de despliegue de `v4.6-restauracion`

1. **Formato D2 con un respaldo real de producción** (paso 6): `RESULTADO: CUMPLE D2`. Si una regla da `False`, **no despliegues**: la aplicación rechazaría sus propios respaldos.
2. **Ensayo en la réplica** con `RESULTADO: CUMPLE`.
3. **Respaldo previo en producción** `VÁLIDO` (`respaldo.md`) y `revisar_volcado_d2.py` → `CUMPLE D2` sobre ese archivo.
4. Etiqueta anotada `v4.6-restauracion` y `git push` de la etiqueta.
5. Checkout en el servidor y `git describe` → `v4.6-restauracion`. Sin migraciones, `pip` ni `collectstatic`.
6. `check --deploy` **antes** del Reload: solo W005 y W021.
7. Reload y verificaciones del mismo día: campo `RESTAURAR` visible; `.sql` vacío rechazado con el mensaje fijo y sin `emergencia_` nuevo; respaldo desde la web `VÁLIDO`; `server.log` y `error.log` sin errores nuevos. Sin restauración real en producción.
8. Retroceso: `retroceso.md`, caso 1, a `v4.5-credenciales`.

## Ensayo en la réplica y formato D2, paso a paso (PowerShell 7)

Es el mismo texto de `despliegue.md`, sección 3.11. Todo en **una sola ventana**; si la cierras, vuelve al paso 1. **Nunca** `docker compose down -v` ni `docker volume rm`.

**Paso 1. Proyecto y entorno virtual.**

```powershell
cd "D:\Trabajo\Proyectos PYTHON\Proyectos Personales\Pedidos Manzagrafica\PedidosApp"
.\.venv\Scripts\Activate.ps1
```

Debe verse `(.venv)`. Si no, no sigas.

**Paso 2. Contenedor arriba.**

```powershell
docker compose up -d
docker inspect -f "{{.State.Running}}" manzagrafica-mysql
```

Debe responder `true`. Si no: Docker Desktop, «Engine running», repite; si sigue, `docker compose logs db --tail 30` y detente.

**Paso 3. Réplica y paridad.**

```powershell
$env:DB_NAME = "manzagrafica_replica"
python scripts\diagnostico\paridad_replica.py
$LASTEXITCODE
```

Debe dar `0`. Si da `1`, no sigas.

**Paso 4. Carpeta de volcados fuera del repo.**

```powershell
$carpeta = "<tu carpeta de respaldos descargados, fuera del repo>"
Test-Path $carpeta
```

Debe dar `True`.

**Paso 5 (paso 0 de la iteración). Respaldo de la réplica.**

```powershell
docker exec manzagrafica-mysql sh -c 'MYSQL_PWD="$MYSQL_ROOT_PASSWORD" mysqldump -uroot --no-tablespaces --set-gtid-purged=OFF manzagrafica_replica > /tmp/replica_paso0.sql'
docker cp manzagrafica-mysql:/tmp/replica_paso0.sql "$carpeta\replica_paso0_04-04.sql"
docker exec manzagrafica-mysql rm -f /tmp/replica_paso0.sql
python scripts\verificar_respaldo.py "$carpeta\replica_paso0_04-04.sql"
```

Debe terminar en `VÁLIDO` (19 de 19). Si no, no sigas.

**Paso 6. Formato D2 sobre respaldos reales.**

```powershell
$d2 = "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-04\revisar_volcado_d2.py"
python $d2 "$carpeta\replica_paso0_04-04.sql"
$LASTEXITCODE
python $d2 "<ruta de un respaldo de producción, por ejemplo respaldo_19-11-2026_14-13-28.sql>"
$LASTEXITCODE
```

Cada uno: ocho reglas en `True`, `RESULTADO: CUMPLE D2` y `0`. **Si alguna da `False`, detente y pega las ocho líneas.**

**Paso 7. Ensayo.**

```powershell
python "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-04\puente_ensayo_04_04.py" --carpeta $carpeta --respaldo-paso0 "$carpeta\replica_paso0_04-04.sql"
$LASTEXITCODE
```

**Paso 8. Conteos esperados.**

| Línea | Qué debe decir |
| :---- | :------------- |
| `[0] Respaldo del paso 0: existe y cumple D2` | Esa frase. |
| `Carpeta del ensayo: …` | **Anótala**. |
| `[1] Antes: N tablas, F filas` | Cualquier número. |
| `[2] Volcado A: … cumple D2: sí` | `sí`. |
| `[3] Volcado de seguridad nativo: … cumple D2: sí` | `sí`. |
| `[4] Volcado inválido rechazado sin respaldo ni restauración: sí` | `sí`. |
| `[5] Sin RESTAURAR, rechazado sin tocar nada: sí` | `sí`. |
| `[6] Restauración con RESTAURAR: correcta sí, X s` | `sí`; anota los segundos. |
| `Respaldo emergencia_: 1 archivo(s), cumple D2: sí; mensaje lo nombra: sí` | `1`, `sí`, `sí`. |
| `Subida borrada de backups/tmp: sí` | `sí`. |
| `[7] … «Restauración iniciada» 1, «resultado=correcta» 1` | `1` y `1`. |
| `[8] Después: … tablas con conteo distinto: 1 (esperado 1: eventos +1, esperado +1)` | `1` y `+1`. |
| `[9] … procesos del ensayo vistos: X; con contraseña en argumentos: equipo 0, contenedor 0` | X ≥ 1; `0` y `0`. |
| `Archivos de opciones residuales: equipo 0, contenedor 0` | `0` y `0`. |
| `RESULTADO: CUMPLE` y `$LASTEXITCODE` = `0` | **Éxito.** Pega las líneas. |

**Paso 9. Si falla.**

- `NO SE EJECUTA` (código 2): no tocó nada; corrige y repite el paso 7.
- Corte en `[2]` o `[3]`: la base no se restauró; pega la salida.
- `NO` en `[4]` o `[5]`: no despliegues; pega la salida.
- Error o `NO` en `[6]`: restaura `<Carpeta del ensayo>\seguridad_nativo.sql` con `replica-local.md`, sección 5, y repite el paso 3; si falla, usa `replica_paso0_04-04.sql`.
- Otro conteo distinto en `[8]` o algo distinto de 0 en `[9]`: no cumple; no despliegues.
- Residuales: `docker exec manzagrafica-mysql sh -c "rm -f /tmp/mysql_opciones_*"` o `Remove-Item "$env:TEMP\mysql_opciones_*"`.

**Paso 10. Limpieza (siempre).**

```powershell
Remove-Item Env:DB_NAME
Remove-Item -Recurse -Force "<Carpeta del ensayo que anotaste en el paso 8>"
Remove-Item -Force "$carpeta\replica_paso0_04-04.sql"
Remove-Item -Recurse -Force "C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\4b08cb32-a4fd-45ef-92e8-7e874083185f\scratchpad\ensayo-04-04"
docker compose stop
```

Borra la carpeta del ensayo y el respaldo del paso 0 **solo si salió `CUMPLE`**. Si sigue la carpeta del ensayo de la 04-03, bórrala también. `$env:DB_NAME` no debe mostrar nada.

## Riesgos y lo que no se vio

- **D2 más estricta que el formato real:** la confirma el paso 6 antes de desplegar.
- **La restauración sigue en la petición** (regla 8.10 de `AGENTS.md`); el paso 8 mide su duración en la réplica. Propuesta sin cambio: la de la redacción (06-03 o Épica 14).
- **Excepción a la rotación (D5):** la 06-03 debe conocerla.
- **El ensayo usa el cliente de pruebas de Django**, no el navegador: no prueba el JavaScript ni SweetAlert. La revisión manual de la pantalla (escritorio y 360 px) queda para el desarrollador.
- **El ensayo inicia sesión con el primer superusuario activo de la réplica** (no imprime cuál) y deja el evento de la restauración en la réplica (+1 fila).
- No se vio: ningún volcado real, ningún `.env`, el servidor ni la pantalla en un navegador.

## Resultado final

- `python manage.py test pedidos` → **375 pruebas, `OK (expected failures=4)`** (342 + 33).
- `python manage.py check` → sin problemas. `makemigrations --check --dry-run` → `No changes detected`.
- Finales de línea conservados (CRLF en `utils.py`, las dos plantillas y `test_contrato_error.py`; LF en el resto).
- Pendiente del desarrollador: formato D2 sobre respaldos reales, ensayo en la réplica, revisión manual de `restaurar_bd.html` en escritorio y a 360 px, y el despliegue.
