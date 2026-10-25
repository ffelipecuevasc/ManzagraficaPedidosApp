# Bitácora 01-07 · Marcas visuales en el registro de errores

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión. Falta que el desarrollador mire la terminal de PyCharm. Se despliega dentro de la 01-06 (`v1.1-observabilidad`). **Sin migraciones; no requiere respaldo propio** (la 01-06 lo exige por la 0007).

## Resumen

- **`FormateadorConEmoji`** en `pedidos/registro.py`: antepone el emoji del nivel a la primera línea (❌ ERROR, ⚠️ WARNING, ❕ INFO, ❗❌❗ CRITICAL, 🛠️ DEBUG). Los campos `clave=valor` y su orden no cambian; la traza de debajo, tampoco.
- **`LOGGING`:** una línea nueva en el formateador `clave_valor` (`'class': 'pedidos.registro.FormateadorConEmoji'`), diff aprobado.
- **Codificación:** con una salida que no admite emojis, la petición **no se rompe**, pero **la línea completa se pierde**, no solo el emoji. La comprobación en el `error.log` real quedó como tarea de la 01-06.
- **Pruebas:** 7 nuevas y 3 ajustadas en `test_registro.py`. En total son 79, en verde tres veces.
- **Planificación:**
  - 01-07 creada y registrada;
  - la 01-06 depende de la 01-07, queda «redactada, sin ejecutar» y su validación comprueba el emoji en el `error.log` real;
  - el número de pruebas de la 01-06 pasó de 72 a 79.

## Decisiones del desarrollador (2026-10-25)

1. **Emoji por nivel**, según la tabla de la iteración, y la 01-07 antes de la 01-06.
2. **Diff de `LOGGING`** aprobado.
3. **`DEBUG` lleva 🛠️.** La tarea 6 pedía probar que `DEBUG` no llevaba emoji, en contradicción con la tabla. Se consultó y vale la tabla. La prueba comprueba 🛠️ para `DEBUG`, y otra comprueba que un nivel personalizado (sin entrada en la tabla) sale sin emoji. Hoy ningún registrador está en `DEBUG`, así que esas líneas no llegan a `error.log`.

## Formato resultante

En `error.log`, después de la fecha de PythonAnywhere:

```text
2026-10-25 19:19:05,412: ❌ nivel=ERROR registrador=pedidos.decorators metodo=GET ruta=/pagos/eliminar/1056/ usuario=1 excepcion=TemplateDoesNotExist mensaje="Error capturado por decorador en eliminar_pago"
2026-10-25 19:19:05,412: Traceback (most recent call last):
...
```

- Solo la primera línea lleva el emoji, y la traza queda igual. Una prueba verifica que en una línea con traza hay exactamente un `❌`.
- **`grep "nivel=ERROR"`** sigue encontrando la línea: el emoji es un prefijo separado por un espacio.
- **Caracteres:** `⚠️` y `🛠️` incluyen el selector de variación U+FE0F, para que se vean como emoji y no como símbolo de texto.

## Codificación de la salida (tarea 3)

**Comprobado en local** (`SalidaSinEmojisTests`) con un flujo `ascii` en el manejador real:

1. Al escribir, `StreamHandler.emit` lanza `UnicodeEncodeError` por el emoji.
2. `logging` lo captura en `Handler.handleError`, que escribe en stderr `--- Logging error ---` con la traza del `UnicodeEncodeError`, y **no relanza** (`logging.raiseExceptions` vale `True` por defecto: informa y sigue).
3. Una petición con error forzado responde `500` con la página «Algo salió mal» aunque el manejador no pueda escribir: **el registro nunca rompe la petición**.
4. **Pero la línea completa se pierde**, no solo el emoji: `emit` falla al escribir el texto entero. En una salida sin UTF-8, `error.log` recibiría el aviso `--- Logging error ---` en lugar del error.

**Riesgo en producción:** depende de la codificación de stderr del proceso uWSGI de PythonAnywhere (Python 3.13 en Linux, normalmente UTF-8). No se puede comprobar en local, así que va como verificación de la 01-06:

- C2 debe encontrar la línea que empieza con `❌`;
- si no aparece, se cuenta `Logging error` en `error.log`;
- se mira el emoji también en el visor de registros del panel.

Si fallara, la corrección propuesta (sin aplicar) es abrir el flujo con `errors='backslashreplace'`. Sería un cambio de `LOGGING` y requeriría consulta.

## Verificación manual en local (tarea 7)

PowerShell 7.6.8 (`[Console]::OutputEncoding` = `utf-8`), `DB_NAME=manzagrafica_replica`. Un PDF y un error forzado en el mismo proceso, con el superusuario de la réplica cargado y sin iniciar sesión (no escribe en la réplica): abrir con GET la eliminación del último pago de la réplica (`1038`), que falla por la plantilla faltante (AUD-02-002). Después, una línea de muestra de cada nivel restante. Salida de error (traza abreviada):

```text
codificacion_stderr=utf-8
pdf=200 application/pdf b'%PDF'
❌ nivel=ERROR registrador=pedidos.decorators metodo=GET ruta=/pagos/eliminar/1038/ usuario=1 excepcion=TemplateDoesNotExist mensaje="Error capturado por decorador en eliminar_pago"
Traceback (most recent call last):
django.template.exceptions.TemplateDoesNotExist: pedidos/pago_confirm_delete.html
eliminar_pago_get=500
⚠️ nivel=WARNING registrador=pedidos.views metodo=- ruta=- usuario=- excepcion=- mensaje="Linea de muestra 01-07"
❕ nivel=INFO registrador=pedidos.views metodo=- ruta=- usuario=- excepcion=- mensaje="Linea de muestra 01-07"
❗❌❗ nivel=CRITICAL registrador=pedidos.views metodo=- ruta=- usuario=- excepcion=- mensaje="Linea de muestra 01-07"
```

- Los cuatro emojis se ven correctamente en PowerShell 7. 🛠️ (`DEBUG`) está cubierto por la prueba, porque ningún registrador emite `DEBUG`.
- El PDF no dejó **ninguna** línea de `fontTools`: el ajuste de 01-02 sigue vigente.
- **Terminal de PyCharm:** el agente no la puede ver. Para comprobarla, el desarrollador ejecuta en la terminal de PyCharm el mismo guion: `$env:DB_NAME='manzagrafica_replica'; python manage.py shell -c "import logging; [logging.getLogger('pedidos.views').log(n, 'muestra') for n in (50, 40, 30, 20)]"` y mira que se vean ❗❌❗, ❌, ⚠️ y ❕. Mientras tanto, ese criterio queda sin marcar.
- **Dato para la 01-06:** la réplica (volcado del 2026-10-20) no tiene el pago `1056`; su último pago es el `1038`. En producción, B5 decide el `id`.

## Pruebas

| Prueba (`test_registro.py`) | Qué comprueba |
| :-------------------------- | :------------ |
| `EmojiPorNivelTests.test_cada_nivel_lleva_su_emoji_y_el_resto_no_cambia` | Los 5 niveles: emoji y la línea completa idéntica al formato de 01-02 |
| `test_debug_lleva_su_emoji` | `DEBUG` → 🛠️ (decisión del desarrollador) |
| `test_nivel_personalizado_sin_emoji` | Un nivel sin entrada en la tabla sale sin emoji |
| `test_grep_por_nivel_sigue_funcionando` | `nivel=ERROR` es el primer campo después del emoji |
| `test_la_traza_no_lleva_emoji` | Un solo `❌`, en la primera línea; `Traceback` intacto |
| `SalidaSinEmojisTests.test_flujo_ascii_no_rompe_y_logging_informa_el_problema` | `UnicodeEncodeError` informado como `--- Logging error ---`, sin excepción hacia quien registra |
| `test_peticion_responde_aunque_la_salida_no_admita_emojis` | Una petición con error forzado responde 500 con la página nueva aunque el registro no se pueda escribir |
| Ajustadas: `test_error_en_peticion_lleva_contexto_y_traza_completa`, `test_sin_peticion_usa_guiones`, `test_filtro_no_falla_con_usuario_roto` | Ahora esperan el emoji al inicio |

- Las pruebas de 01-03 (`test_errores.py`) usan `assertIn` sobre los campos y no necesitaron cambios.
- `python manage.py test pedidos`: **79 pruebas en `OK`** en tres ejecuciones (61,1 s, 60,3 s y 59,1 s).
- `check`: sin problemas. `makemigrations --check --dry-run`: `No changes detected`. **Sin migraciones.**

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `PedidosApp/settings.py` | `LOGGING`: clase del formateador (aprobado) |
| `pedidos/registro.py` | `EMOJI_POR_NIVEL` y `FormateadorConEmoji` |
| `pedidos/tests/test_registro.py` | 7 pruebas nuevas, 3 ajustadas |
| `docs/operacion/pruebas.md` | Descripción de `test_registro.py` |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-07-marcas-visuales.md` | Nuevo |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-06-despliegue-validacion.md` | Depende de 01-07, sin ejecutar, emoji y codificación en la validación, 79 pruebas |
| `_planificacion/10_epicas/epica-01-observabilidad/evidencia-01-06.md` | C2 comprueba el emoji y la ausencia de `Logging error`; 79 pruebas |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | 01-07 en la tabla y decisión del emoji |
| `_planificacion/00_producto/registro-pendientes.md` | 01-07 en la tabla, 01-06 dependiente, iteración activa e historial |

## Pendientes

- Que el desarrollador mire la terminal de PyCharm (comando arriba).
- Revisión del desarrollador. Después, ejecutar la 01-06 cuando lo indique.
