# Iteración 01-09 · Capturas amplias que incumplen la regla 4

- **Épica:** 01 · Observabilidad
- **Estado:** Redactada, sin ejecutar. Ninguna corrección está decidida: cada captura tiene opciones para que elija el desarrollador (sección «Decisiones del desarrollador»).
- **Subfase del plan:** ninguna propia. Es deuda detectada en la revisión de la 01-06 (2026-10-25) y adelanta parte de 3.2 (supresión silenciosa) y de 3.4 (contrato de error) **solo en lo que pide la regla 4**: registrar y no mostrar `str(e)`.
- **Depende de:** 01-06 (detección de las capturas y opción A: el diagnóstico se lee en `server.log`).
- **RDA relacionadas:** RDA-007 (un despliegue, un propósito), RDA-008 (inventario de eventos), RDA-013 (errores con `logging`).
- **Hallazgos relacionados:** AUD-01-002 (`:270`, `:766`, `:810`), AUD-02-006 (`:1128`) y las dos entradas nuevas de la sección 3 de `registro-pendientes.md` (`:1168`, `:1191`). Según la opción elegida, la iteración **avanza** esos hallazgos sin cerrarlos: AUD-01-002 se cierra en 03-02 y AUD-02-006 en 04-01 y 03-04.
- **Cambio de esquema:** Ninguno.
- **Respaldo previo al despliegue:** ver «Despliegue». La iteración no toca esquema ni datos.

## Objetivo

Que ninguna de las seis capturas amplias de `pedidos/views.py` deje un fallo sin rastro en `server.log` ni muestre al usuario el texto técnico de una excepción, sin adelantar el rediseño transaccional de la Épica 03 ni el endurecimiento de la Épica 04.

## Regla 4 (AGENTS.md), en resumen

1. Prohibido `except Exception: pass` y sus equivalentes.
2. Se captura la excepción concreta que se sabe manejar.
3. Una captura amplia solo se permite cuando el código no puede fallar hacia el usuario sin protección, y siempre registra con `logger.exception(...)` (en una vista, con `extra={'request': request}`).
4. Nunca se muestra `str(e)` al usuario.

**Precedente:** `views.py:194` (`crear_pedido`) mantiene su captura amplia, pero desde la 01-03 registra con `logger.exception` y el comentario la deja para 03-02. Es la misma solución de transición que la opción A de los ítems.

## Contexto técnico común

- `@transaccion_segura` (`pedidos/decorators.py`) **no** abre una transacción: es un `try/except` que registra y muestra la página 500. Además, `settings.py` no activa `ATOMIC_REQUESTS`. Cada `save()`, `delete()` y `create()` se confirma por separado. Por eso hoy, si falla un ítem, lo ya escrito queda en la base y, en las ediciones, los ítems anteriores ya están borrados.
- `generar_respaldo_mysql()` (`pedidos/utils.py:62`) lanza `Exception` genérica con la salida de error de `mysqldump` en el mensaje. Una captura específica en la vista exige cambiar antes esa función para que lance una excepción propia.
- `restaurar_bd_mysql()` (`pedidos/utils.py:94`) ejecuta `mysql` en un subproceso, fuera de cualquier transacción de Django. Si falla a mitad de camino, la base puede quedar restaurada en parte.

## Alcance · las seis capturas

### 1. `views.py:270` · `editar_pedido` (AUD-01-002)

- **Qué hace hoy:** guarda el pedido, **borra todos sus ítems** y los recrea desde `items_json`. Si falla cualquier ítem (JSON inválido, producto inexistente, cantidad no numérica), `except Exception: pass` lo silencia: el pedido queda con los ítems creados hasta el fallo (o sin ninguno), se registra `pedido_modificado` y el usuario ve el detalle como si todo hubiera salido bien.
- **Qué incumple:** puntos 1 y 3 (silencia y no registra). Además se pierden datos sin aviso, que es lo que corrige 03-02.

### 2. `views.py:766` · `crear_cotizacion` (AUD-01-002)

- **Qué hace hoy:** crea la cotización y después los ítems. Si falla uno, `except Exception as e: pass` (con el comentario «En producción podrías loguear esto»): la cotización queda con ítems parciales y el usuario no se entera.
- **Qué incumple:** puntos 1 y 3.

### 3. `views.py:810` · `editar_cotizacion` (AUD-01-002)

- **Qué hace hoy:** igual que `editar_pedido`: borra los ítems, los recrea y silencia el fallo con `pass`.
- **Qué incumple:** puntos 1 y 3.

### Opciones para las capturas 1, 2 y 3 (se eligen juntas o por separado)

| Opción | Qué cambia | Riesgo |
| :----- | :--------- | :----- |
| **A. Registrar sin cambiar el flujo** (como `:194`) | `pass` → `logger.exception('Error procesando ítems de …', pk, extra={'request': request})` y comentario que remite a 03-02. El usuario ve lo mismo que hoy. | **Bajo** en código. La pérdida de ítems sigue igual, pero deja traza. La captura sigue siendo amplia dentro de una vista, una excepción tolerada como transición, igual que `:194`. |
| **B. Capturar lo concreto y avisar al usuario** | Capturar `json.JSONDecodeError`, `KeyError`, `ValueError`, `TypeError` y `Producto.DoesNotExist`; registrar y mostrar un `messages.error` sin detalles técnicos («Algunos ítems no se guardaron; revisa el pedido»). Lo demás se propaga al decorador (página 500 y traza). | **Medio.** Cambia lo que ve el usuario y, sin transacción, los datos parciales siguen en la base. Adelanta parte de 3.4 sin el contrato completo. Hay que elegir la lista de excepciones y el texto (`PENDIENTE_DESARROLLADOR`). |
| **C. No tocarlas en la 01-09** | Se dejan para 03-02, que ya las cubre. La 01-09 solo deja registradas las líneas. | **Sin riesgo de código**, pero los fallos siguen sin rastro hasta la Épica 03 y la deuda de la regla 4 sigue abierta. |
| **D. Corrección completa** | `transaction.atomic()` alrededor del pedido o la cotización y sus ítems, y propagar el error. | **Alto para esta iteración.** Es el trabajo de 03-02 y 03-03, cambia el comportamiento ante fallos y mezcla fases (contra «un despliegue, un propósito», RDA-007). Se anota solo para descartarla de forma consciente. |

### 4. `views.py:1128` · `generar_respaldo_bd` (AUD-02-006)

- **Qué hace hoy:** genera el volcado con `mysqldump`, registra `respaldo_generado` y lo descarga. Si algo falla, `except Exception as e` devuelve `HttpResponse(f"Error crítico: {str(e)}")`: una página en blanco, fuera de `base.html`, con el texto de la excepción, que puede incluir la salida de error de `mysqldump` y rutas del servidor. No registra nada.
- **Qué incumple:** puntos 3 y 4. Que sea un GET (también AUD-02-006) es de 04-01 y queda fuera.

### 5. `views.py:1168` · `restaurar_bd`, respaldo de emergencia previo (entrada nueva)

- **Qué hace hoy:** si falla el respaldo previo a restaurar, borra el archivo subido, muestra «Operación abortada: No se pudo crear el respaldo de seguridad previo (`str(e)`)» y redirige. **Aborta bien** (no restaura), pero no registra el fallo y muestra el texto técnico.
- **Qué incumple:** puntos 3 y 4.

### 6. `views.py:1191` · `restaurar_bd`, la restauración (entrada nueva)

- **Qué hace hoy:** cualquier fallo al guardar el archivo, al restaurar o al limpiar termina en «Error crítico al restaurar: `str(e)`». No registra nada, no dice en qué estado quedó la base y el archivo subido puede quedar en `backups/tmp/`. Es la operación más destructiva de la aplicación.
- **Qué incumple:** puntos 3 y 4.

### Opciones para las capturas 4, 5 y 6

| Opción | Qué cambia | Riesgo |
| :----- | :--------- | :----- |
| **A. Registrar y mensaje sin detalles técnicos** | `logger.exception(..., extra={'request': request})` en cada una. `str(e)` se reemplaza por un texto fijo. En `:1128`, `messages.error` y redirección a `respaldar_bd` en lugar del `HttpResponse` en blanco (o, si lo prefieres, un `HttpResponse` con texto fijo). Las capturas siguen amplias. | **Bajo.** El administrador pierde el detalle en pantalla y tiene que ir a `server.log` a leerlo, que es lo que pide la opción A de la 01-06. Los textos fijos son una decisión (`PENDIENTE_DESARROLLADOR`). |
| **B. Como A, más excepciones concretas** | Además, `utils.py` lanza una excepción propia (por ejemplo `ErrorRespaldo`) y las vistas capturan esa y `OSError`. Lo inesperado se propaga a la página 500. | **Medio.** Toca `utils.py`, que hoy tiene pruebas indirectas, y cambia lo que ve el usuario ante errores inesperados (página 500 en lugar del mensaje). |
| **C. A, más el estado de la base en `:1191`** | Además, el mensaje de `:1191` dice que la base puede haber quedado restaurada en parte y nombra el respaldo de emergencia que se generó en `:1168` (hoy se descarta el valor que devuelve `generar_respaldo_mysql()`). | **Medio.** Cambia el texto y guarda una variable, sin tocar la lógica de aborto. El nombre del archivo no es un dato técnico sensible, pero la decisión es del desarrollador. Se solapa con 04-04 («verificar que el respaldo previo se generó»). |
| **D. No tocarlas en la 01-09** | Se dejan para 03-04 (mensajes), 04-01 (`:1128` por POST) y 04-04 (restauración). | **Sin riesgo de código**, pero `str(e)` sigue expuesto hasta la Épica 03 o 04, y un fallo de la restauración sigue sin traza. |

## Fuera de alcance

- Transacciones en pedidos y cotizaciones (03-02, 03-03) y el rediseño de `@transaccion_segura` (Épica 03).
- `float(item['cantidad'])` en lugar de `Decimal` (regla 13): es de 03-02 o de la épica que corresponda, no de la regla 4.
- `generar_respaldo_bd` por GET (04-01), y la validación, la confirmación y el registro de eventos de la restauración (04-04).
- Registrar un evento de negocio para los fallos (por ejemplo `respaldo_fallido`): RDA-008 limita el inventario y agregar un tipo sería una decisión aparte.
- La captura del propio decorador (`decorators.py`) y la de `registro.py:69`, que la regla 4 permite.
- Cualquier otra captura amplia fuera de estas seis.

## Tareas (una vez elegidas las opciones)

1. **Pruebas primero (regla 8.15).** Por cada captura que se corrija, una prueba que falla hoy y pasa con la corrección, simulando el fallo con `mock` (sin ejecutar `mysql` ni `mysqldump`, como `test_restauracion_fallida_no_deja_evento`). Cada prueba comprueba lo que corresponda a la opción: hay un registro `ERROR` de `pedidos.views` con traza, el mensaje que ve el usuario no contiene el texto de la excepción y no aparece `Traceback` en la respuesta.
2. Aplicar las opciones elegidas en `pedidos/views.py` (y en `pedidos/utils.py` solo con la opción B de respaldo).
3. Verificar: `python manage.py test pedidos` (79 más las nuevas, en `OK`), `check` y `makemigrations --check --dry-run`.
4. Revisión manual en la réplica local, en escritorio y a 360 px: generar un respaldo (camino normal) y ver los mensajes de error con un fallo simulado. La restauración real contra la réplica solo si el desarrollador la autoriza (decisión 5).
5. Bitácora `bitacora-01-09.md` con el diff, las pruebas y los resultados. Actualizar `registro-pendientes.md` (entradas de `:270` a `:1191`) y, si corresponde, `auditoria-tecnica.md` (avance de AUD-01-002 y AUD-02-006, sin cerrarlos).

## Criterios de aceptación

- [ ] Cada una de las seis capturas tiene la opción elegida por el desarrollador, o queda anotada como «sin cambios, se corrige en <iteración>».
- [ ] Ninguna de las capturas corregidas silencia el error: cada una deja en el registro un `ERROR` con traza y, en vistas, con método, ruta y usuario.
- [ ] Ninguna de las capturas corregidas muestra `str(e)` ni texto técnico al usuario.
- [ ] Hay una prueba por captura corregida que falla antes de la corrección y pasa con ella.
- [ ] `python manage.py test pedidos` en `OK`, `check` sin errores, `makemigrations --check`: `No changes detected`.
- [ ] El diff no toca transacciones, métodos HTTP, plantillas ni el inventario de eventos.

## Riesgos

| Riesgo | Mitigación |
| :----- | :--------- |
| Que registrar en los ítems haga creer que la pérdida de datos está resuelta | El comentario remite a 03-02 y AUD-01-002 sigue abierto |
| Que el administrador, sin `str(e)` en pantalla, no sepa por qué falló un respaldo | El mensaje dice dónde mirar; el detalle queda en `server.log` con su traza (opción A de la 01-06) |
| Que una prueba ejecute `mysql` o `mysqldump` de verdad contra la réplica | Las pruebas simulan las dos funciones con `mock`, como las de 01-04 |
| Que la opción B cambie un mensaje controlado por la página 500 | Probar los dos caminos: excepción conocida (mensaje) y desconocida (500 con traza) |
| Mezclar propósitos con la Épica 03 o 04 | Las opciones D de los ítems y los cambios de método HTTP quedan fuera de alcance |
| Una línea registrada con datos personales | `logger.exception` lleva el `pk` y el contexto de la petición, nunca el contenido de `items_json` ni del archivo |

## Despliegue

- **Cambia código, así que necesita despliegue con etiqueta** (RDA-007). Propuesta: `v1.2-capturas` (o el propósito que elija el desarrollador), con partida en `v1.1-observabilidad`.
- **La 01-08 viaja en el mismo despliegue:** sus comentarios están en `main` y no tienen despliegue propio. La etiqueta de la 01-09 los incluye. El registro de despliegue de `despliegue.md` debe nombrar las dos iteraciones.
- **Cuándo:** después de cerrar la parte D de la 01-06 (medición hasta el 2026-11-01), para que la medición no mezcle versiones. Es una decisión del desarrollador (decisión 6).
- **Respaldo previo:** no hay migraciones ni cambios de datos, así que la iteración no lo exige por sí misma. Las vistas que se tocan son las de respaldo y restauración: si el despliegue sale mal, el botón de respaldo de la aplicación puede ser justo lo que no funcione. Conviene un respaldo descargado antes, según el protocolo de `docs/operacion/despliegue.md` (decisión 5).
- **Pruebas con la réplica:** pruebas automáticas con `mock` en todos los casos. Contra la réplica local, el camino normal de generar respaldo. La restauración real en local reemplaza los datos de la réplica: solo si el desarrollador la autoriza, y después se refresca la réplica según `docs/operacion/replica-local.md`.
- **Validación en producción:** pasos para el desarrollador. Generar un respaldo desde la aplicación (camino normal) y comprobar que se descarga. **No** se provoca a propósito un fallo de respaldo ni de restauración en producción.

## Decisiones del desarrollador

1. **Capturas de ítems (`:270`, `:766`, `:810`):** opción A, B o C (D queda descartada por alcance). `PENDIENTE_DESARROLLADOR`.
2. **Capturas de respaldo y restauración (`:1128`, `:1168`, `:1191`):** opción A, B, C o D, juntas o por separado. `PENDIENTE_DESARROLLADOR`.
3. **Textos que ve el usuario** con las opciones que los cambian (B de ítems; A, B o C de respaldo). Propuesta para revisar: `:1128` «No se pudo generar el respaldo. El detalle quedó en el registro del servidor.»; `:1168` «Operación cancelada: no se pudo crear el respaldo de seguridad previo, así que la base no se tocó.»; `:1191` «La restauración falló. La base puede haber quedado restaurada en parte: revisa el registro del servidor antes de seguir.» `PENDIENTE_DESARROLLADOR`.
4. **`:1128`:** mensaje y redirección a `respaldar_bd`, o `HttpResponse` con texto fijo. `PENDIENTE_DESARROLLADOR`.
5. **Respaldo previo al despliegue y restauración real en la réplica local:** sí o no. `PENDIENTE_DESARROLLADOR`.
6. **Cuándo ejecutar y desplegar:** antes o después de cerrar la parte D de la 01-06, y nombre de la etiqueta. `PENDIENTE_DESARROLLADOR`.

## Datos requeridos del cliente

- Ninguno.
