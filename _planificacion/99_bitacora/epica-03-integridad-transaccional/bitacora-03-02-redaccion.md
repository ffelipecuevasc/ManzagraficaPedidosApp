# Bitácora 03-02 · Redacción de la iteración

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (la redacción). La iteración 03-02 queda «Pendiente»: no se ejecutó.

## Resumen

Se redactó la iteración 03-02 · Erradicación de la supresión silenciosa a partir de evidencia leída en el código, las pruebas y la planificación. Incluye el inventario de capturas amplias y `print` de `pedidos/`, el análisis del solapamiento con la 03-03 (qué exige cada regresión y dos trampas de las pruebas), cuatro opciones de alcance sin decidir y el conteo de pedidos sin ítems como consulta de solo lectura que ejecuta el desarrollador, con su limitación declarada. Sin cambios de código, pruebas ni `docs/operacion/`.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-02-erradicacion-supresion-silenciosa.md` | Nuevo: iteración con estado «Pendiente». |
| `00_producto/registro-pendientes.md:44` | Fila 03-02: enlaces a la iteración y a esta bitácora; el estado sigue «Pendiente». |
| `00_producto/registro-pendientes.md:304` | Entrada de historial 2026-11-04. |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-02-redaccion.md` | Esta bitácora (nueva). |

## Verificación

Evidencia leída (solo lectura):

- **Inventario:** búsqueda de `except`, `pass` y `print(` en `pedidos/` sin `tests/` ni `migrations/`. 10 `except Exception`: `eventos.py:45` y `:54`, `registro.py:68` (permitidas por la regla 4) y `views.py:191`, `:267`, `:759`, `:803` (ítems), `:1118`, `:1162`, `:1187` (respaldo y restauración). 0 `print(` en `pedidos/` (el único en el repositorio está en `scripts/diagnostico/paridad_replica.py`, una herramienta de consola). 0 `except:` sin tipo y 0 `pass` dentro de un `except` en código de aplicación. Las siete de `views.py` ya las registró la 01-09 (o la 01-03, la de `:191`): ninguna queda sin registrar.
- **Código:** `views.py:156-242` (`crear_pedido`, con `atomic` en `:166` y la captura en `:181-195`), `:244-295` (`editar_pedido`), `:732-775` y `:777-829` (cotizaciones), `:844-918` (`convertir_a_pedido`, sin captura ni transacción; `except ValueError` en `:858`).
- **Pruebas:** `test_regresiones.py:57-74` (`absorber_errores`) y `:110-175` (R1 a R4), `test_capturas_amplias.py:42-75` (las 3 pruebas de ítems de la 01-09), `test_errores.py:19` y `test_registro.py:187` (`raise_request_exception = False`), `test_pedidos.py:147` (crear sin ítems es válido).
- **Planificación:** `definicion-epica-03.md` (alcance 2 y 3, «Para la redacción de 03-02», `:47`), `iteracion-03-01` (modelo), `iteracion-01-09` (opciones elegidas), `auditoria-tecnica.md` (AUD-01-002, AUD-02-006, AUD-02-008), `pruebas.md` sección 7, `decisiones.md` (RDA-015 y RDA-019), `plan-de-trabajo.md:338-342`, `replica-local.md` y las notas del registro sobre la réplica.

Además:

- Pruebas: no se ejecutaron (sin cambios de código). Los fallos esperados que da cada opción son **predicción por lectura**, no medición; la iteración los confirma al ejecutar.
- Las tres consultas de la sección «Evidencia P3» **no fueron ejecutadas por el agente** (no usa `docker` ni `mysql`). Los nombres de tabla son los que Django genera por defecto: `models.py` no define `db_table`.
- `git --no-pager status --short` y `git --no-pager diff --stat`: solo los `.md` de la tabla.

## Migraciones

- Ninguna.

## Hallazgos de la lectura que importan para decidir

1. **R3 es la única regresión que puede pasar a verde solo propagando la excepción** (ya vive en un `atomic`). R1, R2 y R4 exigen `transaction.atomic` nuevo: es el trabajo de la 03-03.
2. **Trampa de las pruebas:** si la excepción sale de la vista, el cliente de pruebas la vuelve a lanzar y R3 seguiría figurando como fallo esperado (no daría `unexpected success`) hasta ajustar `raise_request_exception`. R1, R2 y R4 seguirían como fallo esperado, pero por otra razón.
3. **Propagar sin transacción empeora la experiencia en tres vistas:** en `editar_pedido`, `crear_cotizacion` y `editar_cotizacion` el éxito falso pasaría a un 500 con el formulario perdido (antes de la 03-04) y los datos quedarían igual de parciales.
4. **`views.py:858`:** `except ValueError` convierte un abono no numérico en 0 sin avisar. Es supresión por efecto, aunque la excepción sea concreta.
5. **Imagen de referencia:** revertir `crear_pedido` deja el archivo huérfano; la épica ya dejó esa decisión para la 03-03.

## Decisiones tomadas

- Ninguna. Las decisiones abiertas son del desarrollador.

## Pendientes y riesgos

Decisiones abiertas (`PENDIENTE_DESARROLLADOR`), detalladas en la iteración:

1. **Alcance**, sin recomendación:
   - A: propagar en las cuatro vistas (fallos esperados 18 → 17, por R3).
   - B: propagar solo en `crear_pedido` (18 → 17).
   - C: cuatro `atomic` mínimos, con captura fuera (18 → 14; contradice la decisión del 2026-11-04 sobre R1, R2 y R4).
   - D: excepciones concretas, registro y aviso sin transacción (18 → 18).
2. Capturas de respaldo y restauración (`views.py:1118`, `:1162`, `:1187`): dejarlas hasta la 04-04 o estrecharlas aquí con una excepción propia.
3. `views.py:858` (abono que se vuelve 0): aquí o en la 03-03.
4. `float` en las cantidades (regla 13): aquí, en otra épica o en una iteración propia.
5. Qué ve el usuario mientras tanto (solo A y B).
6. Lista de excepciones concretas y texto del aviso (solo C y D).
7. Despliegue propio o con la 03-05.
8. Cuándo ejecuta el desarrollador el conteo P3.

Riesgos y límites:

- **El conteo P3 no es el estado de producción.** Se hará sobre la réplica con su último refresco registrado (volcado del 2026-10-25 21:02:34, según `replica-local.md`) y una conversión de prueba del 2026-11-04. El refresco está pendiente hasta el cierre de la Épica 03 (AUD-05-002). «Sin ítems» es un indicio, no una prueba de fallo.
- **Cierre de AUD-02-008:** su nota dice que se cierra con R3 en la 03-03. Con A o B, R3 pasaría a verde en la 03-02 y habría que anotarlo.
- **Estado del registro:** las líneas `:6`, `:7` y `:16` de `registro-pendientes.md` siguen diciendo que el siguiente paso es redactar la 03-02. No se tocaron porque el pedido solo incluía la fila y el historial; quedan para el cierre de la redacción.

## Criterios de aceptación

- [x] Iteración creada con cabecera, objetivo, evidencia, tareas, criterios, fuera de alcance, riesgos y decisiones, con estado «Pendiente».
- [x] Afirmaciones apoyadas en archivo:línea.
- [x] Inventario completo de capturas amplias y `print`, con las ya registradas por la 01-09 separadas de las que no.
- [x] Solapamiento con la 03-03 analizado, con opciones, ventajas y riesgos, sin decidir.
- [x] Conteo P3 como consulta de solo lectura, con solo agregados y la limitación declarada.
- [x] Pruebas primero (regla 8.15) y RDA-015 explícitas.
- [x] Lo no decidido queda marcado `PENDIENTE_DESARROLLADOR`, sin alcance nuevo para la 03-03 ni la 03-04.

## Commit sugerido

`Épica 3 - Iteración 03-02: redacta la erradicación de la supresión silenciosa con inventario, cuatro opciones de alcance y el conteo de pedidos sin ítems`
