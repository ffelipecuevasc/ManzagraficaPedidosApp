# Iteración 03-02 · Erradicación de la supresión silenciosa

- **Épica:** 03 · Integridad transaccional
- **Estado:** Terminada (2026-11-04). Ejecutada en local con el alcance B: solo `crear_pedido` ([bitacora-03-02](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-02.md)); cierre en [bitacora-03-02-cierre](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-02-cierre.md). Sin despliegue propio: viaja con la 03-05. Historial de estados: Pendiente (redactada el 2026-11-04) → En revisión (2026-11-04) → Terminada (2026-11-04).
- **Subfase del plan:** 3.2 «Erradicación de la supresión silenciosa» (`plan-de-trabajo.md:338-342`)
- **Depende de:** 03-01 (Terminada el 2026-11-04)
- **RDA relacionadas:** RDA-007 (un despliegue, un propósito), RDA-013 (errores con `logging` en `server.log`, sin identificador de correlación), RDA-015 (las transacciones vivirán en servicios en la 07-02), RDA-019 (la atomicidad se declara con `transaction.atomic` explícito y la captura fuera del bloque).
- **Hallazgos relacionados:** AUD-01-002 (avanza; **se cierra en la 03-03** junto con R1, R2 y R4, nota del 2026-11-04), AUD-02-008 (evidencia P3; R3 pasa a verde aquí; nota fechada del 2026-11-04 y el estado lo decide el desarrollador), AUD-02-006 (solo la parte de capturas, ya avanzada por la 01-09).
- **Cambio de esquema:** Ninguno.
- **Respaldo previo al despliegue:** No lo exige por sí misma (sin migraciones ni datos). Ver «Despliegue».
- **Etiqueta y ventana:** sin despliegue propio; viaja con la 03-05 (decisión 2 del 2026-11-04).

## Objetivo

Que ninguna captura amplia del código de la aplicación esconda un fallo o descarte datos sin que nadie se entere, según la regla 4 de `AGENTS.md`. Esta iteración trata el **fondo** de las cuatro capturas de ítems que la 01-09 solo dejó registradas. Cuánto de ese fondo se corrige aquí y cuánto queda para la 03-03 lo fijó la decisión 1 (alcance B, 2026-11-04): aquí solo `crear_pedido`.

## Regla 4 de `AGENTS.md`, en resumen

1. Prohibido `except Exception: pass` y equivalentes.
2. Se captura la excepción concreta que se sabe manejar.
3. Una captura amplia solo se permite cuando el código no puede fallar hacia el usuario sin protección (el servicio de registro, un decorador de vistas) y siempre registra con `logging`.
4. Nunca se muestra `str(e)` al usuario, ni se usa `print` para errores.

Regla 3 (atomicidad): una excepción capturada **dentro** del bloque `atomic` hace que la transacción se confirme igual; la captura va **fuera** del bloque o la excepción se propaga.

## Qué hace hoy (evidencia leída el 2026-11-04)

### Las cuatro capturas de ítems

La 01-09 las dejó con `logger.exception(..., extra={'request': request})` y un comentario que remite a esta iteración. Ninguna silencia ya sin rastro, pero las cuatro siguen incumpliendo los puntos 2 y 3 de la regla (captura amplia dentro de una vista) y las cuatro **descartan datos sin avisar al usuario**.

| Vista | Captura | Qué hace antes de la captura | Qué ve el usuario si un ítem falla |
| :---- | :------ | :--------------------------- | :--------------------------------- |
| `crear_pedido` | `views.py:191` (`except Exception as e`; `e` no se usa) | `transaction.atomic` abierto en `:166`: guarda el pedido (`:176`), luego los ítems (`:181-190`) | Redirección al detalle, como si todo hubiera salido bien. La transacción **se confirma** con el pedido y los ítems creados hasta el fallo (caso de estudio de la 03-01, AUD-02-008) |
| `editar_pedido` | `views.py:267` | **Sin** transacción: `form.save()` (`:252`), borra todos los ítems (`:257`) y recrea (`:258-266`) | Redirección al detalle. El pedido queda con los ítems creados hasta el fallo, o con ninguno |
| `crear_cotizacion` | `views.py:759` | **Sin** transacción: `form.save()` (`:742`), luego los ítems (`:748-758`) | Redirección al detalle con ítems parciales |
| `editar_cotizacion` | `views.py:803` | **Sin** transacción: `form.save()` (`:788`), borra los ítems (`:793`) y recrea (`:794-802`) | Redirección al detalle con ítems parciales o ninguno |

Qué puede fallar dentro de cada bloque (leído en el código, sin ejecutarlo): `json.loads` (JSON inválido), `item['producto_id']` y `item['cantidad']` (clave ausente), `Producto.objects.get` (producto inexistente), `float(...)` e `int(...)` (valor no numérico) y el `create` (error de la base). La lista concreta de excepciones es parte de la decisión 1 (opción D).

### Efectos laterales que importan

- **Evento «modificado» aunque falle:** `editar_pedido` registra `pedido_modificado` (`views.py:271`) después de la captura, así que el evento dice que el pedido se modificó aunque los ítems se hayan perdido.
- **`convertir_a_pedido` (`views.py:852-912`) no tiene captura ni transacción:** si falla en la copia de ítems (`:874-880`) o en el pago, deja el pedido a medias y responde 500. No es supresión, es falta de frontera: es de la 03-03.
- **Imagen de referencia:** `form.save()` escribe el archivo en disco antes de los ítems. Si la transacción se revierte, el archivo queda huérfano. La épica deja esa decisión para la 03-03 (`definicion-epica-03.md:47`).
- **Cantidades con `float`:** `float(item['cantidad'])` (`:188`, `:264`, `:756`, `:800`) contradice la regla 13 (`Decimal`). La 01-09 lo dejó fuera por no ser de la regla 4 (`iteracion-01-09`, «Fuera de alcance»). Ver decisión 4.

## Inventario de capturas amplias y `print` en `pedidos/` (leído el 2026-11-04)

Búsqueda sobre `pedidos/*.py` sin `tests/` ni `migrations/`: `except Exception`, `except:`, `except BaseException`, `pass`, `print(` y `sys.stdout`.

- `print(`: **0** en `pedidos/`. El único uso en el repositorio es `scripts/diagnostico/paridad_replica.py:108-139`, una herramienta de consola que imprime su informe a propósito. No es código de la aplicación (regla 8) y queda fuera.
- `except:` sin tipo, `except BaseException` y `pass` dentro de un `except`: **0** en código de aplicación.
- `except Exception`: **10**.

| # | Lugar | Qué protege | Registra | Qué ve el usuario | Estado frente a la regla 4 |
| :- | :---- | :---------- | :------- | :---------------- | :------------------------- |
| 1 | `eventos.py:45` | Programar el evento con `on_commit` | `logger.exception` | Nada (el servicio nunca falla hacia el usuario) | **Permitida**: servicio de registro |
| 2 | `eventos.py:54` | Escribir el evento tras confirmar | `logger.exception` | Nada | **Permitida**: servicio de registro |
| 3 | `registro.py:68` | Filtro de contexto del registro | `sys.stderr` | Nada | **Permitida**: el propio servicio de registro |
| 4 | `views.py:191` (`crear_pedido`) | Ítems del pedido | Sí, desde la 01-03 | Nada: parece éxito | **Incumple 2 y 3.** Ya registrada. Se corrige aquí |
| 5 | `views.py:267` (`editar_pedido`) | Ítems del pedido | Sí, desde la 01-09 | Nada: parece éxito | **Incumple 2 y 3.** Ya registrada por la 01-09. Se corrige aquí |
| 6 | `views.py:759` (`crear_cotizacion`) | Ítems de la cotización | Sí, desde la 01-09 | Nada: parece éxito | **Incumple 2 y 3.** Ya registrada por la 01-09. Se corrige aquí |
| 7 | `views.py:803` (`editar_cotizacion`) | Ítems de la cotización | Sí, desde la 01-09 | Nada: parece éxito | **Incumple 2 y 3.** Ya registrada por la 01-09. Se corrige aquí |
| 8 | `views.py:1118` (`generar_respaldo_bd`) | Respaldo con `mysqldump` | Sí, desde la 01-09 | Texto fijo aprobado | **Amplia pero registrada y sin `str(e)`** (opción C de la 01-09). Decisión 2 |
| 9 | `views.py:1162` (`restaurar_bd`, respaldo previo) | Respaldo de emergencia | Sí, desde la 01-09 | Texto fijo aprobado; no restaura | Igual que la #8. Decisión 2 |
| 10 | `views.py:1187` (`restaurar_bd`, la restauración) | Guardar, restaurar y limpiar | Sí, desde la 01-09 | Texto fijo aprobado, con el estado de la base | Igual que la #8. Decisión 2 |

**Ya registradas:** las #4 a #10 (siete): la #4 desde la 01-03 y de la #5 a la #10 por la 01-09. **Sin registrar:** ninguna. Las #1 a #3 son anteriores y la regla las permite.

**Después de la 03-02:** la #4 desaparece (`crear_pedido` ya no tiene captura). Las #5 a #7 siguen hasta la 03-03 y las #8 a #10 hasta la 04-04 (decisión 3). Quedan 9 `except Exception`, 3 de ellas permitidas.

Capturas con excepción concreta que conviene tener a la vista:

| Lugar | Qué hace | Observación |
| :---- | :------- | :---------- |
| `views.py:858` (`convertir_a_pedido`) | `except ValueError` al leer el abono: si no es un número, **usa 0 sin avisar** | Excepción concreta, pero el efecto es de supresión: el abono que el usuario escribió se pierde y no queda registro. `definicion-epica-03.md:15` asigna la validación del abono con un formulario a la 03-03 (AUD-02-005). Decisión 3 |
| `views.py:1015` (`eliminar_producto`) | `except ProtectedError` | Correcta: informa al usuario por qué no se puede borrar |
| `utils.py:91` | `except OSError` al borrar un respaldo antiguo | Correcta: `logger.warning(..., exc_info=True)` y sigue |
| `utils.py:58-62`, `:128-137` | Convierten `CalledProcessError` y `FileNotFoundError` en `Exception` con texto | No suprimen: relanzan. El texto técnico solo llega a `server.log` desde la 01-09. Una excepción propia es de la 04-04 |

**Comentarios `noqa: BLE001`:** `eventos.py:45`, `:54` y `registro.py:68` ya declaran que son capturas permitidas.

## Solapamiento con la 03-03

Hay un orden de hechos que condiciona el alcance. Es **lectura del código y de las pruebas, no medición**: las predicciones de pruebas se confirman al ejecutar.

### Qué exige cada regresión

| Regresión | Qué afirma | Qué necesita para pasar a verde |
| :-------- | :--------- | :------------------------------ |
| R3 (`test_regresiones.py:156-164`) | Crear pedido con un ítem que falla deja 0 pedidos y 0 ítems | Que la excepción **salga** del `atomic` que ya existe en `crear_pedido` (`views.py:166`). No necesita bloque nuevo |
| R4 (`:166-175`) | Crear cotización con un ítem que falla deja 0 cotizaciones y 0 ítems | Un `atomic` nuevo alrededor de `form.save()` y los ítems |
| R1 (`:122-136`) | Editar pedido con un ítem que falla conserva los ítems anteriores **y** el `valor_venta` anterior | Un `atomic` nuevo que incluya `form.save()`, el borrado y la recreación |
| R2 (`:138-154`) | Igual que R1, en cotizaciones | Igual que R1 |

Por eso: **R3 es la única que puede pasar a verde solo propagando la excepción.** R1, R2 y R4 exigen `transaction.atomic` nuevo, que es el trabajo de la 03-03 (`definicion-epica-03.md:13`, «fijar la frontera transaccional de cada vista de escritura»).

### Dos trampas de las pruebas (por lectura)

1. **Una excepción que sale de la vista sale también por el cliente de pruebas.** `Client` vuelve a lanzarla salvo que se ponga `raise_request_exception = False` (patrón ya usado en `test_errores.py:19` y `test_registro.py:187`). R1 a R4 no lo ponen y solo absorben los registros del registrador `pedidos` (`absorber_errores`, `test_regresiones.py:57-74`).
   - **R3** pasaría de «aserción falla» a «la prueba lanza `Producto.DoesNotExist`»: como `@expectedFailure` también cuenta los errores, seguiría figurando como fallo esperado y **no daría `unexpected success`** aunque la corrección funcione. Para que pase a verde, la iteración debe ajustar la prueba (`raise_request_exception = False`) como parte de las pruebas primero.
   - **R1, R2 y R4** seguirían como fallo esperado, pero **por otra razón** (el error, no los datos que quedan). Conviene ajustarlas igual, para que su fallo siga diciendo lo que deben decir hasta la 03-03.
   - Los errores que escapan se registran en `django.request`, no en `pedidos`: `absorber_errores` tendría que incluirlo para que la salida de las pruebas no se llene de trazas.
2. **Las tres pruebas de la 01-09 sobre ítems** (`test_capturas_amplias.py:42-75`) afirman hoy «redirección y un `ERROR` de `pedidos.views`». Cambian con cualquier opción que modifique lo que ve el usuario.

### Opciones de alcance (`PENDIENTE_DESARROLLADOR`, sin recomendación)

| Opción | Qué cambia | Fallos esperados (por lectura) | Ventajas | Riesgos |
| :----- | :--------- | :----------------------------- | :------- | :------ |
| **A. Propagar en las cuatro** | Se quitan los cuatro `try/except Exception` y la excepción sube. Django responde 500 con la página de la 01-03 y deja una línea `django.request` con traza | 18 → **17** (R3). R1, R2 y R4 siguen | Es el cambio más chico. Cumple la regla 4 en las cuatro. `crear_pedido` ya revierte por su `atomic` (R3). La 03-03 queda con todo el trabajo transaccional | En `editar_pedido`, `crear_cotizacion` y `editar_cotizacion` **no hay transacción**: el pedido se guarda, los ítems se borran y el usuario ve un **500** en vez de un éxito falso. La pérdida de datos es la misma; cambia que ahora se nota, pero **antes de la 03-04** pierde además lo que escribió en el formulario. Hasta la 03-03, ese estado intermedio es peor para el usuario que el de hoy en la experiencia y no mejor en los datos. Deja la imagen huérfana de `crear_pedido` (decisión de la 03-03) |
| **B. Propagar solo en `crear_pedido`** | Solo se quita la captura de `views.py:191`. Las otras tres quedan registradas, con su comentario | 18 → **17** (R3) | Es la única de las cuatro que hoy tiene transacción, así que propagar ahí no deja datos a medias. Las otras tres no empeoran para el usuario | La subfase se llama «erradicación» y quedarían tres capturas amplias hasta la 03-03. Misma imagen huérfana que A en `crear_pedido` |
| **C. Cuatro `atomic` mínimos (adelantar la parte de ítems de la 03-03)** | En las cuatro vistas, `try: with transaction.atomic(): …guardar cabecera e ítems… except <concretas>:` registra y vuelve al formulario con aviso. Captura **fuera** del bloque (regla 3) | 18 → **14** (R1 a R4) | Ninguna vista queda en un estado intermedio. Es el patrón correcto de la regla 3 desde el primer día. La 03-03 se concentra en pago, `estado_pago` y conversión | **Contradice la decisión del 2026-11-04** de cerrar AUD-01-002 con R1, R2 y R4 en la 03-03 (habría que revisar esas notas). Mezcla con 03-03 y con 03-04: hay que decidir qué ve el usuario y si se conserva el formulario. Cambia lo que ve el usuario ante un fallo. Más grande de revisar. Imagen huérfana (decisión de la 03-03) |
| **D. Excepciones concretas, registro y aviso, sin transacción** | `except (json.JSONDecodeError, KeyError, TypeError, ValueError, Producto.DoesNotExist)` (lista por confirmar) con `logger.exception` y `messages.error` de texto fijo. Lo no listado sube y da 500 | 18 → **18** (R3 sigue: captura dentro del `atomic`) | Cumple los puntos 2, 3 y 4 sin tocar transacciones. El usuario **se entera** de que los ítems no se guardaron | No arregla los datos: siguen parciales (R1 a R4 siguen). Adelanta parte del contrato de error de la 03-04 (texto aprobado, qué ve el usuario). Se parece a la opción B de la 01-09, que el desarrollador no eligió. Necesita fijar la lista de excepciones y el texto |

**Elegida: B** (decisión 1, 2026-11-04). Notas que valían para todas:

- Ninguna opción cierra AUD-01-002: se cierra en la 03-03 (decisión del 2026-11-04). Con A o B, **R3 pasaría a verde en la 03-02** y AUD-02-008 (cuyo cierre dice «con R3 en la 03-03») habría que anotarlo; con C, también R1, R2 y R4.
- **RDA-015:** ninguna opción cambia dónde viven las transacciones a futuro. En C, los `atomic` quedan en la vista y la 07-02 los mueve a los servicios, igual que los de la 03-03.
- Con A o B, el 500 no es el mensaje final: la 03-04 define el mensaje y la conservación del formulario (`definicion-epica-03.md:16-20`).

## Evidencia P3 · pedidos sin ítems

La Auditoría 04 (P3) recoge que el cliente dice que «a veces al guardar sale error y no se guarda» (`definicion-epica-03.md:26`). La épica pide que esta iteración revise si existen pedidos sin ítems. Se hace en la **réplica local**, con consultas de solo lectura que ejecuta el desarrollador (los agentes no usan `docker` ni `mysql`, `AGENTS.md`, sección 6).

**Decisión 4 (2026-11-04):** el desarrollador ejecuta las tres consultas durante la 03-02 y las **repite tras el refresco de la réplica** (al cerrar la Épica 03, AUD-05-002). Cada cifra se registra con la fecha del último refresco de la réplica.

### Limitaciones que se declaran en la bitácora

- La réplica tiene su **último refresco registrado en `replica-local.md`** (volcado del 2026-10-25 21:02:34). El refresco con el respaldo del 2026-11-04 00:12:37 está pendiente hasta el cierre de la Épica 03 (AUD-05-002). Por eso la cifra **no es el estado actual de producción**.
- La réplica tiene además **una conversión de cotización de prueba hecha el 2026-11-04**: suma un pedido con ítems y marca una cotización como aceptada.
- «Sin ítems» **no prueba un fallo**: el formulario permite guardar sin ítems (`test_pedidos.py:147`) y los pedidos anteriores a la tabla de ítems no los tienen. Por eso la consulta separa los pedidos posteriores al primero que sí tiene ítems. Aun así, es un **indicio**, no una medida de fallos.
- **No detecta** pedidos con ítems parciales (el caso de R3) ni ediciones que perdieron ítems: solo cuenta los que quedaron sin ninguno.
- Las consultas son agregados: sin nombres, teléfonos, correos ni montos de clientes concretos.

### Consultas (solo `SELECT`, una línea cada una)

Los nombres de tabla son los que Django genera por defecto (`models.py` no define `db_table`); si alguno no existe, el mensaje de error lo dirá y no se modifica nada. Mismo patrón que `replica-local.md`, sección 2.

1. Pedidos totales, sin ítems, sin ítems posteriores al primer pedido con ítems y sin ítems con valor de venta mayor que 0:

```powershell
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" manzagrafica_replica -e "SELECT COUNT(*) AS pedidos, SUM(i.pedido_id IS NULL) AS sin_items, SUM(i.pedido_id IS NULL AND p.id > (SELECT MIN(pedido_id) FROM pedidos_itempedido)) AS sin_items_desde_el_primero_con_items, SUM(i.pedido_id IS NULL AND p.valor_venta > 0) AS sin_items_con_valor FROM pedidos_pedido p LEFT JOIN (SELECT DISTINCT pedido_id FROM pedidos_itempedido) i ON i.pedido_id = p.id;"'
```

2. Lo mismo para cotizaciones:

```powershell
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" manzagrafica_replica -e "SELECT COUNT(*) AS cotizaciones, SUM(i.cotizacion_id IS NULL) AS sin_items, SUM(i.cotizacion_id IS NULL AND c.id > (SELECT MIN(cotizacion_id) FROM pedidos_itemcotizacion)) AS sin_items_desde_la_primera_con_items FROM pedidos_cotizacion c LEFT JOIN (SELECT DISTINCT cotizacion_id FROM pedidos_itemcotizacion) i ON i.cotizacion_id = c.id;"'
```

3. Pedidos sin ítems posteriores al primero con ítems, por mes (mes en UTC, solo para ubicarlos en el tiempo):

```powershell
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" manzagrafica_replica -e "SELECT LEFT(p.fecha_solicitud, 7) AS mes_utc, COUNT(*) AS sin_items FROM pedidos_pedido p LEFT JOIN (SELECT DISTINCT pedido_id FROM pedidos_itempedido) i ON i.pedido_id = p.id WHERE i.pedido_id IS NULL AND p.id > (SELECT MIN(pedido_id) FROM pedidos_itempedido) GROUP BY mes_utc ORDER BY mes_utc;"'
```

### Formato de la respuesta

Se responde en la bitácora de ejecución (no hace falta archivo de evidencia, porque no es producción), copiando solo los números:

| Consulta | Resultado |
| :------- | :-------- |
| 1 | pedidos = N · sin_items = N · desde_el_primero_con_items = N · con_valor = N |
| 2 | cotizaciones = N · sin_items = N · desde_la_primera_con_items = N |
| 3 | una línea `mes_utc = N` por mes (o «sin filas») |

Cómo se lee: si «sin ítems desde el primero con ítems» es 0, la réplica no muestra el síntoma (sin descartar fallos que solo dejan ítems parciales). Si es mayor que 0, no se concluye que fueron fallos: se registra la cifra y se pregunta al cliente si crea pedidos sin ítems a propósito (`PENDIENTE_CLIENTE`, solo si la cifra es mayor que 0).

## Tareas (ejecutadas el 2026-11-04 con el alcance B)

1. **Pruebas primero (regla 8.15)**, con `DB_NAME=manzagrafica_replica` y Docker encendido:
   - R3 ajustada: `raise_request_exception = False` y `absorber_errores` con `pedidos` y `django.request`; sin `@expectedFailure` ni `@tag('regresion')`. R1, R2 y R4 no se tocaron.
   - Pruebas nuevas en `test_pedidos.py` (`CrearPedidoItemFallidoTests`): un ítem fallido (cinco causas) no deja pedido, ítems, pago ni evento y responde 500 con la plantilla de la 01-03; deja una sola línea `django.request` con traza; `crear_pedido` ya no contiene `except Exception`.
   - Antes de corregir: 4 pruebas fallaban (8 fallos contando los cinco casos), R1, R2 y R4 como fallo esperado.
2. **Corregir `crear_pedido`** (`views.py`): se quita el `try/except Exception` de los ítems; la excepción sale del `transaction.atomic` de `:166` y el bloque revierte pedido, ítems y pago. Sin cambios en mensajes al usuario (03-04).
3. **Retirar R3** como regresión y actualizar `docs/operacion/pruebas.md` (valor vigente 17, fila de R3 fuera, viñeta que explica la retirada).
4. **Verificación:** `python manage.py test pedidos` → `OK (expected failures=17)` en tres ejecuciones; `check`; `makemigrations --check --dry-run`.
5. **Conteo P3:** las tres consultas quedan listas para que el desarrollador las ejecute. Criterio sin marcar.
6. **Cierre documental:** bitácora, registro y notas fechadas en AUD-02-008 y AUD-01-002.

## Criterios de aceptación

- [x] La decisión 1 está registrada antes de implementar (alcance B, 2026-11-04). No exige RDA: no contradice RDA-019, que ya fija «captura fuera del bloque» y atomicidad explícita.
- [x] Las pruebas se escribieron antes de la corrección y fallaban: 4 pruebas (8 fallos con los cinco casos), según la bitácora.
- [x] `crear_pedido` no contiene `except Exception`; la prueba lo comprueba.
- [x] Un ítem fallido en `crear_pedido` no deja pedido, ítems, pago ni evento, y responde 500 con `pedidos/errors/500.html`.
- [x] Cada fallo deja **una** línea `django.request` con traza, método, ruta y usuario, y la respuesta no lleva `str(e)` ni `Traceback`.
- [x] R3 está en verde y sin marcas; R1, R2 y R4 siguen como fallo esperado por la aserción de los datos.
- [x] `pruebas.md` y la bitácora dicen `expected failures=17`.
- [x] `python manage.py test pedidos` → `OK (expected failures=17)` en tres ejecuciones, `check` limpio y `makemigrations --check`: `No changes detected`.
- [x] El conteo P3 está en la bitácora con sus limitaciones declaradas (réplica con su último refresco registrado y la conversión de prueba del 2026-11-04). Ejecutado por el desarrollador el 2026-11-04: 888 pedidos, 126 sin ítems, 38 sin ítems posteriores al primero con ítems, 126 con valor mayor que 0; 27 cotizaciones, 0 sin ítems ([bitacora-03-02-cierre](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-02-cierre.md)). Se repite tras el refresco de la réplica (decisión 4), sin bloquear el cierre.
- [x] Revisión manual a 360 px y en escritorio de la página 500 al fallar un ítem al crear un pedido. Hecha por el desarrollador el 2026-11-04 en la réplica (`DEBUG=False`, `--insecure`): con `items_json` alterado a un `producto_id` inexistente, `POST /pedidos/nuevo/` devolvió 500 y se vio la página 500 de la aplicación en escritorio y a 360 px; traza `DoesNotExist` en `views.py:186` en `django.request`; el último pedido siguió siendo el #910 ([bitacora-03-02-cierre](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-02-cierre.md)).

## Fuera de alcance

- Las capturas de ítems de `editar_pedido` (`views.py:267`), `crear_cotizacion` (`:759`) y `editar_cotizacion` (`:803`), con R1, R2 y R4: 03-03. Sus comentarios «se corrige en 03-02» quedan como están y se actualizan allí.
- Atomicidad nueva en esas vistas, frontera de `convertir_a_pedido`, `estado_pago` (AUD-02-004), rechazo de la doble conversión y validación del abono con formulario (AUD-02-005): 03-03.
- `views.py:858` (el abono que se vuelve 0 sin aviso): 03-03 (decisión 3).
- Cierre de AUD-01-002 y de AUD-01-001: 03-03.
- La imagen de referencia que queda en disco al revertir `crear_pedido`: 03-03 (`definicion-epica-03.md:47`).
- Mensajes al usuario, conservación del formulario y envío único (R21): 03-04. Hasta entonces, un ítem fallido al crear un pedido muestra la página 500 y el formulario se pierde.
- Las capturas de respaldo y restauración (`views.py:1118`, `:1162`, `:1187`), la excepción propia de `utils.py` y el registro de eventos de la restauración: 04-04 (decisión 3).
- `float(item['cantidad'])` en lugar de `Decimal` (regla 13): 07-02 (decisión 3).
- `scripts/diagnostico/paridad_replica.py` (herramienta de consola, no código de la aplicación).
- Mover transacciones a servicios: 07-02 (RDA-015).

## Despliegue

- Cambia código, así que necesita despliegue con etiqueta (RDA-007). **Viaja con la 03-05** (decisión 2 del 2026-11-04), igual que la 03-01. Sin migraciones ni cambios de datos. Respaldo previo: lo decide el desarrollador al planificar el despliegue de la 03-05.
- Hasta ese despliegue, producción sigue con las capturas registradas de `v1.2-capturas`.
- Cuando se despliegue: un ítem fallido al crear un pedido deja una línea de `django.request` (no de `pedidos.views`) y el usuario ve la página 500.

## Riesgos

| Riesgo | Mitigación |
| :----- | :--------- |
| Con B, el éxito falso de `crear_pedido` pasa a un 500 y el formulario se pierde hasta la 03-04 | Viaja con la 03-05, junto con la 03-03 y la 03-04. Los datos quedan íntegros: se revierte todo |
| La prueba de R3 sigue como fallo esperado por una razón equivocada (el error sube al cliente de pruebas) | Ajustar `raise_request_exception` y el absorbedor primero, y registrar en la bitácora el motivo de cada fallo |
| Una regresión pasa a verde sin que la 03-03 lo sepa (R3) | Notas en AUD-02-008 y en el registro; `pruebas.md` con el valor vigente |
| El conteo de la réplica se toma como medida de producción | La limitación va en la bitácora y en cualquier cita de la cifra |
| Se mezcla con la 03-03 sin querer (atomicidad, pago, conversión) | La decisión 1 fija el límite; el resto queda en «Fuera de alcance» |
| Quien lee `server.log` ya no ve `pedidos.views` en los errores de ítems | Actualizar la guía de `despliegue.md` si cambia el registrador |

## Decisiones del desarrollador

Todas resueltas el 2026-11-04.

1. **Alcance B:** propagar el error solo en `crear_pedido`, que ya tiene `transaction.atomic`.
2. **Despliegue:** la 03-02 viaja con la 03-05.
3. **Otros temas:** respaldo y restauración, hasta la 04-04; el abono de `views.py:858`, en la 03-03; `float`/`Decimal`, en la 07-02.
4. **Conteo de pedidos sin ítems:** lo ejecuta el desarrollador durante la 03-02 y lo repite tras el refresco de la réplica.

Las decisiones 5 y 6 de la redacción (qué ve el usuario mientras tanto y lista de excepciones) no aplican con el alcance B: el usuario ve la página 500 de la 01-03 hasta la 03-04.

## Datos requeridos del cliente

- Ninguno. El `PENDIENTE_CLIENTE` (¿se crean pedidos sin ítems a propósito?) se abrió porque el conteo dio más de 0 y se **cerró el 2026-11-04**: el cliente (Ignacio, dicha por él) siempre guarda pedidos con al menos 1 ítem y nunca sin ítems. No cambia el alcance ni agrega validación ([bitacora-03-02-cierre](../../99_bitacora/epica-03-integridad-transaccional/bitacora-03-02-cierre.md)).
