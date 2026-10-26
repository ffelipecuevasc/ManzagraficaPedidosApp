# Iteración 01-07 · Marcas visuales en el registro de errores

- **Épica:** 01 · Observabilidad
- **Estado:** En revisión (reabierta el 2026-10-26 por decisión del desarrollador para cambiar los emojis, cambio estético; la versión original se desplegó en `v1.1-observabilidad` el 2026-10-25; los emojis nuevos viajan en el próximo despliegue, `v1.2`, junto con la 01-08 y la 01-09)
- **Subfase del plan:** 1.2 (amplía el formato de 01-02; iteración nueva, sin subfase propia en el plan)
- **Depende de:** 01-02
- **RDA relacionadas:** RDA-013
- **Hallazgos que cierra:** ninguno. Avanza AUD-01-005 (lectura de `error.log`).
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no toca datos ni esquema). Se despliega dentro de la 01-06, que sí lo exige por la 0007.
- **Orden:** se ejecuta **antes** de la 01-06 (decisión del desarrollador del 2026-10-25), para que haya un solo despliegue y una sola validación de `error.log`. Los números son identificadores, no un orden.

## Objetivo

Que el nivel de cada línea de `error.log` se reconozca a simple vista, con un emoji al inicio de la línea, sin cambiar los campos `clave=valor` ni su orden (`grep "nivel=ERROR"` sigue funcionando). En producción, PythonAnywhere antepone su fecha:

`2026-10-25 19:19:05,412: 🔴 nivel=ERROR registrador=pedidos.decorators metodo=GET ruta=/pagos/eliminar/1056/ ...`

| Nivel | Emoji |
| :---- | :---- |
| ERROR | 🔴 |
| WARNING | 🟡 |
| INFO | 🔵 |
| CRITICAL | 🔴🔴 |
| DEBUG | 🟢 |

Un nivel personalizado va sin emoji. **Tabla vigente desde el 2026-10-26** (01-07 reabierta, decisión del desarrollador). La tabla original (❌ ERROR, ⚠️ WARNING, ❕ INFO, ❗❌❗ CRITICAL, 🛠️ DEBUG) es la que se desplegó en `v1.1-observabilidad` y la que muestran las evidencias de la 01-06.

**Para filtrar se busca `nivel=ERROR`, no el emoji:** «🔴🔴 nivel=CRITICAL» contiene «🔴 nivel=», así que buscar por el emoji mezclaría los dos niveles.

## Tareas

1. **Formateador propio** en `pedidos/registro.py`, junto al filtro de contexto: antepone el emoji del nivel a la primera línea del registro. La traza, debajo, no cambia.
2. **`LOGGING`** (requiere consulta): el formateador `clave_valor` usa la clase nueva, con el mismo formato de 01-02.
3. **Codificación de la salida:** comprobar en local qué pasa si el flujo no admite emojis (codificación `ascii`): si el registro falla con `UnicodeEncodeError`, documentar que `logging` informa el problema y sigue, y que **nunca rompe la petición**. La comprobación en el `error.log` real queda para la 01-06.
4. **Pruebas:** una por nivel (emoji correcto y resto de la línea igual), la regla de `DEBUG`, y actualización de las pruebas de 01-02 y 01-03 que comparan la línea.
5. **Verificación manual en local:** un PDF y un error forzado, con la salida en la terminal de PyCharm y en PowerShell 7 (pegada en la bitácora).

## Criterios de aceptación

- [x] Cada nivel lleva su emoji al inicio de la línea y el resto de la línea es idéntico al formato de 01-02 (pruebas). `EmojiPorNivelTests`.
- [x] La regla de `DEBUG` está cubierta por una prueba. Decisión del desarrollador: DEBUG lleva su emoji (🛠️ hasta el 2026-10-26, 🟢 desde entonces); un nivel personalizado va sin emoji.
- [x] `grep "nivel=ERROR"` (o su equivalente en la prueba) sigue encontrando la línea.
- [x] Con un flujo `ascii`, el registro no rompe la petición; el comportamiento está documentado en la bitácora. Ojo: se pierde la línea completa, no solo el emoji (bitácora).
- [x] La terminal de PyCharm y PowerShell 7 muestran bien los emojis (salida en la bitácora). PowerShell 7.6.8 verificado por el agente. El desarrollador cerró la iteración el 2026-10-25; la revisión de la terminal de PyCharm no se reportó por escrito. **Cubierto el 2026-10-26** con el reporte por escrito del desarrollador: los emojis nuevos se ven bien en PyCharm y en PythonAnywhere ([bitacora-01-07](../../99_bitacora/epica-01-observabilidad/bitacora-01-07.md), «Reapertura del 2026-10-26»).
- [x] `python manage.py check` sin errores, `makemigrations --check` sin cambios y `python manage.py test pedidos` en verde. 79 pruebas, tres veces. Reapertura del 2026-10-26: suite completa en verde tras actualizar los valores esperados (bitácora).

## Fuera de alcance

- Cambiar los campos, su orden o los niveles de los registradores (01-02).
- Colores ANSI u otros formatos (JSON).
- Verificar el emoji en el registro real de PythonAnywhere (va en la 01-06). Corrección del 2026-10-25: en producción, el emoji se ve en `server.log`; `error.log` conserva el formato de PythonAnywhere, sin emoji (opción A, [bitacora-01-06-produccion](../../99_bitacora/epica-01-observabilidad/bitacora-01-06-produccion.md)).

## Datos requeridos del cliente

- Ninguno.
