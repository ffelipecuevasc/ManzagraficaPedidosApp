# Iteración 01-07 · Marcas visuales en el registro de errores

- **Épica:** 01 · Observabilidad
- **Estado:** En revisión (2026-10-25; se despliega dentro de la 01-06)
- **Subfase del plan:** 1.2 (amplía el formato de 01-02; iteración nueva, sin subfase propia en el plan)
- **Depende de:** 01-02
- **RDA relacionadas:** RDA-013
- **Hallazgos que cierra:** ninguno. Avanza AUD-01-005 (lectura de `error.log`).
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no toca datos ni esquema). Se despliega dentro de la 01-06, que sí lo exige por la 0007.
- **Orden:** se ejecuta **antes** de la 01-06 (decisión del desarrollador del 2026-10-25), para que haya un solo despliegue y una sola validación de `error.log`. Los números son identificadores, no un orden.

## Objetivo

Que el nivel de cada línea de `error.log` se reconozca a simple vista, con un emoji al inicio de la línea, sin cambiar los campos `clave=valor` ni su orden (`grep "nivel=ERROR"` sigue funcionando). En producción, PythonAnywhere antepone su fecha:

`2026-10-25 19:19:05,412: ❌ nivel=ERROR registrador=pedidos.decorators metodo=GET ruta=/pagos/eliminar/1056/ ...`

| Nivel | Emoji |
| :---- | :---- |
| ERROR | ❌ |
| WARNING | ⚠️ |
| INFO | ❕ |
| CRITICAL | ❗❌❗ |
| DEBUG | 🛠️ |

## Tareas

1. **Formateador propio** en `pedidos/registro.py`, junto al filtro de contexto: antepone el emoji del nivel a la primera línea del registro. La traza, debajo, no cambia.
2. **`LOGGING`** (requiere consulta): el formateador `clave_valor` usa la clase nueva, con el mismo formato de 01-02.
3. **Codificación de la salida:** comprobar en local qué pasa si el flujo no admite emojis (codificación `ascii`): si el registro falla con `UnicodeEncodeError`, documentar que `logging` informa el problema y sigue, y que **nunca rompe la petición**. La comprobación en el `error.log` real queda para la 01-06.
4. **Pruebas:** una por nivel (emoji correcto y resto de la línea igual), la regla de `DEBUG`, y actualización de las pruebas de 01-02 y 01-03 que comparan la línea.
5. **Verificación manual en local:** un PDF y un error forzado, con la salida en la terminal de PyCharm y en PowerShell 7 (pegada en la bitácora).

## Criterios de aceptación

- [x] Cada nivel lleva su emoji al inicio de la línea y el resto de la línea es idéntico al formato de 01-02 (pruebas). `EmojiPorNivelTests`.
- [x] La regla de `DEBUG` está cubierta por una prueba. Decisión del desarrollador: DEBUG lleva 🛠️; un nivel personalizado va sin emoji.
- [x] `grep "nivel=ERROR"` (o su equivalente en la prueba) sigue encontrando la línea.
- [x] Con un flujo `ascii`, el registro no rompe la petición; el comportamiento está documentado en la bitácora. Ojo: se pierde la línea completa, no solo el emoji (bitácora).
- [ ] La terminal de PyCharm y PowerShell 7 muestran bien los emojis (salida en la bitácora). PowerShell 7.6.8 verificado por el agente; falta la terminal de PyCharm (el desarrollador).
- [x] `python manage.py check` sin errores, `makemigrations --check` sin cambios y `python manage.py test pedidos` en verde. 79 pruebas, tres veces.

## Fuera de alcance

- Cambiar los campos, su orden o los niveles de los registradores (01-02).
- Colores ANSI u otros formatos (JSON).
- Verificar el emoji en el `error.log` real de PythonAnywhere (va en la 01-06).

## Datos requeridos del cliente

- Ninguno.
