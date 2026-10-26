# Iteración 01-08 · Comentarios del registro alineados con la opción A

- **Épica:** 01 · Observabilidad
- **Estado:** Redactada, sin ejecutar
- **Subfase del plan:** 1.2 (ajuste de texto de 01-02 y 01-03; iteración nueva, sin subfase propia en el plan)
- **Depende de:** 01-06 (hallazgo «dos destinos de registro» y decisión A del desarrollador, 2026-10-25)
- **RDA relacionadas:** RDA-013 (con su actualización del 2026-10-25)
- **Hallazgos que cierra:** ninguno. Corrige comentarios desmentidos por la medición de la 01-06 ([bitacora-01-06-produccion](../../99_bitacora/epica-01-observabilidad/bitacora-01-06-produccion.md)).
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no toca datos, esquema ni comportamiento)

## Objetivo

Que los comentarios y docstrings del código digan lo que se midió en producción el 2026-10-25:
- nuestro manejador escribe en la salida de error, que en PythonAnywhere termina en **`server.log`**, el archivo de diagnóstico (opción A);
- **`error.log`** recibe los mismos errores en el formato de PythonAnywhere;
- configurar la raíz en `LOGGING` **no** evita la línea doble.

Solo cambia texto: ni una instrucción ni un valor de configuración.

## Alcance

Los cuatro lugares decididos por el desarrollador, más uno que encontró la revisión.

| # | Archivo y línea | Texto actual | Texto propuesto |
| :- | :-------------- | :----------- | :-------------- |
| 1 | `PedidosApp/settings.py:206-209` (bloque `LOGGING`) | Ver el diff de abajo | Ver el diff de abajo |
| 2 | `pedidos/decorators.py:22-23` | `# Traza completa a error.log con el contexto de la petición (01-03). El rediseño` / `# del decorador es de la Épica 03.` | `# Traza completa con el contexto de la petición (01-03); en producción se lee en` / `# server.log (opción A, 01-06). El rediseño del decorador es de la Épica 03.` |
| 3 | `pedidos/views.py:194` | `# Supresión que descarta ítems: se corrige en 03-02. Mientras, queda en error.log.` | `# Supresión que descarta ítems: se corrige en 03-02. Mientras, queda en server.log.` |
| 4 | `pedidos/eventos.py:47` | `# hacer fallar una petición. El problema queda en error.log con su traza.` | `# hacer fallar una petición. El problema queda en server.log con su traza.` |
| 5 | `pedidos/registro.py:69` (encontrado en la revisión) | `# Única captura amplia permitida (AGENTS.md, regla 4): el registrador nunca puede` | `# Captura amplia permitida (AGENTS.md, regla 4), como las de eventos.py: el registrador nunca puede` |

- **Sobre el punto 5:** no menciona `error.log`, pero comparte el problema: el comentario es inexacto. Dice «única» y `eventos.py:45` y `:54` tienen otras dos capturas permitidas por la misma regla. Se incluye solo si el desarrollador lo aprueba (decisión 2).
- **Si el punto 5 deja la línea muy larga:** el texto se reparte en dos líneas de comentario, sin tocar el código.

### Diff exacto de `settings.py` (solo comentarios; requiere aprobación antes de aplicarlo)

```diff
 # REGISTRO (iteración 01-02, RDA-013)
-# Todo va a stderr, que PythonAnywhere guarda en error.log (con su fecha UTC al inicio de
-# cada línea: por eso el formato no repite la fecha). Sin archivos de registro propios.
-# Configurar la raíz reemplaza cualquier manejador previo del entorno y evita líneas dobles.
+# Todo va a stderr. En PythonAnywhere, stderr termina en server.log (hora de Chile, con la
+# traza en una línea y los saltos como #012): es el archivo de diagnóstico (opción A, 01-06).
+# error.log recibe además los mismos errores en el formato de PythonAnywhere, por un manejador
+# del entorno que esta configuración no reemplaza (deducción no confirmada). El formato no
+# lleva fecha porque el recolector la antepone. Sin archivos de registro propios.
 LOGGING = {
```

- Las líneas del bloque `LOGGING` usan fin de línea LF, mientras el resto del archivo mezcla CRLF y LF (pendiente registrado en 01-03). El reemplazo **conserva LF** en esas líneas, para que el diff muestre solo el texto.
- La línea «evita líneas dobles» **se elimina**: producción la desmintió en la 01-06, porque el error queda en `server.log` y en `error.log`.

### Revisión de otros comentarios con la misma suposición

Busqué `error.log`, `server.log`, `stderr`, «salida estándar», «salida de error», «líneas dobles» y `PythonAnywhere` en `pedidos/`, `PedidosApp/` y `scripts/`.

| Lugar | ¿Suposición inexacta? |
| :---- | :-------------------- |
| `pedidos/registro.py:44` (docstring de `FormateadorConEmoji`: «`logging` informa el problema en stderr») | No: es exacto, porque `Handler.handleError` escribe en stderr |
| `pedidos/registro.py:70` («Se emite el problema a stderr») | No: exacto |
| `pedidos/tests/test_registro.py:13` (docstring: «el de la raíz, a stderr») | No: exacto |
| `pedidos/utils.py:42`, `:57` y `:62` | No: hablan de `mysqldump`, no del registro |
| `PedidosApp/settings.py:39`, `:46` y `:128` | No: hablan de `DEBUG`, `ALLOWED_HOSTS` y la base de producción |
| Plantillas y `docs/operacion/` | Sin menciones pendientes: `despliegue.md` y RDA-013 ya se corrigieron en la 01-06 |

## Fuera de alcance

- Cambiar `LOGGING`, el formateador, el filtro, los niveles o el destino. La opción A no cambia código.
- Corregir las capturas amplias de la regla 4 (iteración 01-09).
- Normalizar el fin de línea de `settings.py` (propuesta registrada en 01-03).
- Confirmar el manejador de PythonAnywhere.

## Tareas

1. Aplicar los cambios 2, 3 y 4, y el 5 si se aprueba, exactamente como en la tabla.
2. Aplicar el diff de `settings.py` **solo después de la aprobación del desarrollador**, que antes lo ve tal cual.
3. Comprobar que el diff completo de la iteración contiene **solo líneas de comentario**. Revisarlo con `git diff --stat`, y con `git diff` filtrado: cada línea `+` o `-` empieza con `#` después de la sangría.
4. Verificar: `python manage.py test pedidos`, `check` y `makemigrations --check --dry-run`.
5. Bitácora `bitacora-01-08.md` con el diff y los resultados.

## Criterios de aceptación

- [ ] Los cuatro lugares decididos (y el quinto, si se aprueba) tienen el texto propuesto u otro aprobado por el desarrollador.
- [ ] El diff de `settings.py` lo aprobó el desarrollador antes de aplicarlo, y coincide con el de esta iteración.
- [ ] El diff total cambia solo comentarios: ninguna línea de código, configuración, plantilla ni prueba. El resto del diff es nulo.
- [ ] `python manage.py test pedidos`: **79 pruebas en `OK`**. `check` sin errores. `makemigrations --check`: `No changes detected`.
- [ ] Ningún comentario del código afirma que los errores se leen en `error.log` ni que `LOGGING` evita líneas dobles. Lo comprueba un `grep` que se pega en la bitácora.

## Despliegue

- **No requiere un despliegue ni una etiqueta propios.** No cambia el comportamiento: producción, con `v1.1-observabilidad`, se comporta igual con o sin estos comentarios.
- **Cuándo conviene desplegarla:** junto con el siguiente despliegue que cambie código, por ejemplo la 01-09 o la próxima iteración de la Épica 02 o 03. Así viaja dentro de esa etiqueta y el servidor vuelve a coincidir con `main`.
- **Mientras tanto,** el servidor queda con los comentarios antiguos. No tiene efecto, porque los comentarios no se ejecutan.

## Riesgos

| Riesgo | Mitigación |
| :----- | :--------- |
| Tocar por error una instrucción de `settings.py` (por ejemplo, una coma del diccionario `LOGGING`) | Diff aprobado antes de aplicarlo; tarea 3 (solo líneas `#`); las 79 pruebas, que cargan `LOGGING`, y `check` |
| Cambiar el fin de línea del bloque `LOGGING` y que el diff muestre todo el bloque | Conservar LF en esas líneas; revisar `git diff --stat` (deben ser pocas líneas) |
| Que el comentario nuevo afirme como hecho lo que es deducción (el manejador de PythonAnywhere) | El texto propuesto dice «deducción no confirmada» |
| Que alguien lea el comentario de `server.log` y lo dé por cierto fuera de PythonAnywhere (en local, stderr es la terminal) | El comentario dice «En PythonAnywhere» |

## Decisiones del desarrollador

1. **Diff de `settings.py`:** aprobarlo tal cual o ajustar el texto (`PENDIENTE_DESARROLLADOR`).
2. **Punto 5 (`registro.py:69`, «Única captura amplia»):** incluirlo en esta iteración o dejarlo fuera (`PENDIENTE_DESARROLLADOR`).
3. **Cuándo ejecutarla**, considerando que viaja en el siguiente despliegue con cambios de código.

## Datos requeridos del cliente

- Ninguno.
