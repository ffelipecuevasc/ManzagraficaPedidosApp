# Iteración 03-01 · Rediseño del decorador transaccional

- **Épica:** 03 · Integridad transaccional
- **Estado:** Pendiente (redactada el 2026-11-04; no se ha ejecutado)
- **Subfase del plan:** 3.1 «Rediseño conceptual del decorador» (`plan-de-trabajo.md:327`)
- **Depende de:** 01-06 (parte D) y Épica 02; 00-07 desplegada y validada (cumplido el 2026-11-04; nota del 2026-11-04 en `definicion-epica-03.md`)
- **RDA relacionadas:** RDA-003 (sin migraciones destructivas), RDA-007 (un despliegue, un propósito), RDA-013 (errores con `logging` en `server.log`, sin identificador de correlación), RDA-015 (las transacciones vivirán en servicios en la 07-02). RDA-019 si la decisión 1 lo requiere.
- **Hallazgos relacionados:** AUD-01-001 (avanza; su fila nombra «03-01 y 03-03»), AUD-02-029 (se cierra aquí, con R20), AUD-02-008 (solo caso de estudio; se cierra con R3 en la 03-03, nota del 2026-11-04).
- **Cambio de esquema:** Ninguno.
- **Respaldo previo al despliegue:** No lo exige por sí misma (sin migraciones ni datos). Ver «Despliegue».
- **Etiqueta y ventana:** `PENDIENTE_DESARROLLADOR` (ver «Despliegue»).

## Objetivo

Que el componente hoy llamado `@transaccion_segura` deje de prometer algo que no hace: que su nombre y su comportamiento digan la verdad, que separe atomicidad de manejo de errores, y que un `pk` inexistente responda 404 en vez de 500. Todo sin adelantar la corrección de ítems (03-02 y 03-03) ni el contrato de error (03-04).

## Qué hace hoy (evidencia leída el 2026-11-04)

### El decorador

`pedidos/decorators.py:9-33`:

- `:17-19`: ejecuta la vista dentro de un `try`.
- `:20`: `except Exception as e` captura **todo**, incluidas las respuestas HTTP que Django transmite como excepción (`Http404`, `PermissionDenied`).
- `:24-25`: registra con `logger.exception(..., extra={'request': request})` (desde la 01-03).
- `:28-31`: arma `mensaje_tecnico` con `str(e)` y responde la plantilla 500. La plantilla no lo muestra (`bitacora-01-03.md:59`), pero el texto viaja en el contexto. Eso contradice la regla 8.4 de `AGENTS.md`.
- **No abre ninguna transacción** (AUD-01-001, `auditoria-tecnica.md:23`). `settings.py` tampoco activa `ATOMIC_REQUESTS` (verificado con búsqueda: sin resultados). Cada `save()`, `delete()` y `create()` se confirma por separado.

### Las 17 vistas que lo usan

`pedidos/views.py` tiene 17 usos de `@transaccion_segura` (siempre debajo de `@login_required`). Las líneas indican dónde está el decorador:

| Dominio | Vistas (línea del decorador) |
| :------ | :--------------------------- |
| Pedidos | `crear_pedido` :158, `editar_pedido` :247, `eliminar_pedido` :301, `duplicar_pedido` :405 |
| Clientes | `crear_cliente` :589, `editar_cliente` :602, `eliminar_cliente` :616 |
| Cotizaciones | `crear_cotizacion` :741, `editar_cotizacion` :787, `eliminar_cotizacion` :847, `convertir_a_pedido` :856 |
| Productos | `crear_producto` :993, `editar_producto` :1006, `eliminar_producto` :1020 |
| Pagos | `ingresar_pago` :1380, `editar_pago` :1447, `eliminar_pago` :1478 |

**12 de ellas** reciben un `pk` y responden 500 si no existe (AUD-02-029, `auditoria-tecnica.md:94`; rutas en `test_acceso.py:296-304`). `eliminar_pago` queda fuera de esas 12 porque su GET ya responde 500 por otra causa: falta su plantilla (R7, AUD-02-002, `test_acceso.py:295`). Las 4 vistas restantes (`crear_*` e `ingresar_pago` sin pedido) no reciben `pk`.

### Caso de estudio: el orden de anidación (AUD-02-008)

`crear_pedido` es **la única** vista que usa `transaction.atomic` (`views.py:168`). Dentro del bloque, el `try/except Exception` de los ítems (`views.py:183-197`) captura el fallo, lo registra y **sigue**. Como la excepción no sale del bloque `atomic`, Django confirma la transacción: el pedido queda guardado con los ítems parciales. Es lo que fija R3 (`test_regresiones.py:156`).

La regla que se enseña (`plan-de-trabajo.md:333`; `AGENTS.md`, regla 8.3):

```python
# MAL: la excepción se captura dentro; la transacción se confirma con datos a medias
with transaction.atomic():
    guardar_pedido()
    try:
        guardar_items()
    except Exception:
        registrar()

# BIEN: la excepción sale del bloque; la transacción se revierte entera y después se informa
try:
    with transaction.atomic():
        guardar_pedido()
        guardar_items()
except ErrorConocido:
    registrar_e_informar()
```

**Esta iteración no corrige `crear_pedido`.** R3 sigue como fallo esperado hasta la 03-03.

### Lo que ya hace Django sin el decorador (01-03)

`test_errores.py:32-44` comprueba que una excepción en una vista **sin** decorador responde 500 con la plantilla `pedidos/errors/500.html` y deja en el registro `django.request` el método, la ruta, el usuario, el tipo de excepción y la traza completa. `test_errores.py:27-30` comprueba que el 404 usa su plantilla. Por eso, en las vistas con decorador, cada error deja hoy **dos líneas** en el registro (`bitacora-01-03.md:105`, «se simplifica en 03-01»). Esto importa para la decisión 1.

### Eventos y transacciones

`registrar_evento` (`pedidos/eventos.py:28-44`) escribe con `transaction.on_commit`. Sin transacción abierta escribe de inmediato; dentro de una, escribe al confirmarse y no deja rastro si se revierte. Cualquier opción que agregue un bloque `atomic` alrededor de la vista cambia **cuándo** se escribe el evento, aunque no cambia si se escribe.

## Decisión 1 · Qué hacer con el decorador (`PENDIENTE_DESARROLLADOR`)

`definicion-epica-03.md` («Decisiones de la épica») la deja para esta iteración, con una RDA. Explicación para quien empieza:

> El decorador hace dos trabajos con un nombre que solo describe uno, y ese uno ni siquiera lo hace. **Atomicidad** significa «todo o nada»: si falla algo a mitad de camino, la base vuelve a como estaba. **Manejo de errores** significa qué ve el usuario y qué queda en el registro cuando algo falla. Son responsabilidades distintas: la primera protege los datos y la segunda protege la experiencia y el diagnóstico.

### Opción A · Dividir en dos

Dos piezas apiladas en cada vista: `transaction.atomic` de Django (atomicidad, ya existe y no hay que escribirla) por dentro, y un decorador propio de traducción de errores, con nombre honesto, por fuera. Este último deja pasar `Http404` y `PermissionDenied`.

```python
@login_required
@errores_a_pagina_500        # nombre PENDIENTE_DESARROLLADOR; por fuera: ve la excepción después del rollback
@transaction.atomic          # por dentro: si la excepción sale de aquí, se revierte todo
def editar_cliente(request, pk): ...
```

- **Ventajas:** cada pieza hace una cosa y se lee en la vista. Es la opción «más limpia» del plan (`plan-de-trabajo.md:334`). En la 07-02, la línea `@transaction.atomic` se quita de la vista y la transacción pasa al servicio (RDA-015).
- **Riesgos:** el orden de las dos líneas es determinante. Si alguien las invierte, se repite el error de AUD-02-008, así que hace falta una prueba que lo detecte. Envolver las 17 vistas completas en `atomic` **adelanta parte de la 03-03**: cambia el comportamiento cuando una excepción escapa (hoy confirma lo hecho; después lo revertiría). Tampoco arregla R1 a R4, porque las capturas internas siguen dentro del bloque. La traducción de errores duplica lo que Django ya hace (sección anterior).

### Opción B · Un solo decorador con el orden interno correcto

Se reescribe el decorador con un nombre honesto: `try` por fuera, `transaction.atomic()` por dentro, y deja pasar `Http404` y `PermissionDenied`.

- **Ventajas:** es la opción menos invasiva (`plan-de-trabajo.md:334`): cambia una línea por vista y el orden correcto queda fijado en un solo lugar.
- **Riesgos:** sigue juntando dos responsabilidades, que es justo lo que el principio de la subfase pide separar (`plan-de-trabajo.md:329`). Comparte los riesgos de la opción A: adelanta la 03-03 en las 17 vistas y duplica a Django. En la 07-02 choca con RDA-015: la transacción quedaría en el decorador de la vista **y** en el servicio, y habría que deshacer el decorador de nuevo.

### Opción C · Retirar el decorador y dejar los errores a Django (recomendada)

Se quitan las 17 líneas `@transaccion_segura` y el archivo `decorators.py`. Los errores pasan por el manejo nativo de Django, que ya cumple lo que pide la Épica 01 (`test_errores.py:32-44`). La atomicidad no se agrega aquí: la pone la 03-03 donde haga falta, con `transaction.atomic` explícito y con el orden correcto. En la 07-02 se mueve a los servicios.

- **Ventajas:**
  - Elimina el nombre que miente sin crear otro.
  - Corrige R20 por construcción: Django convierte `Http404` en 404 por su cuenta.
  - Quita `mensaje_tecnico` y la doble línea de registro.
  - No adelanta la 03-03 ni deja nada que deshacer en la 07-02 (RDA-015).
  - Es el cambio más chico y fácil de probar.
- **Riesgos:**
  - Es una tercera opción que el plan (`plan-de-trabajo.md:334`) y la épica (`definicion-epica-03.md:11`, «darle un nombre honesto») no nombran, así que necesita la RDA-019 para dejar constancia.
  - La línea del registro cambia de `registrador=pedidos.decorators` a `registrador=django.request`. La guía para leer `server.log` debe decirlo y dos pruebas cambian (`test_errores.py:46` y `:60`).
  - Esta iteración no deja ninguna vista más protegida que hoy: la protección llega en la 03-03.

**Recomendación: C.** La evidencia muestra que la mitad «errores» ya la hace Django y que la mitad «atomicidad» nunca existió. Lo que queda es retirar el componente y poner la atomicidad donde corresponde en la 03-03, que la 07-02 trasladará a servicios. Si se prefiere no salirse de las dos opciones del plan, la siguiente es **A**, por su compatibilidad con RDA-015. La decisión es del desarrollador.

## Tareas (una vez tomada la decisión 1)

1. **RDA-019** en `decisiones.md` si la decisión lo requiere (en C, sí). Se agrega a la tabla índice.
2. **Pruebas primero** (regla 8.15). Antes de tocar el decorador:
   - R20 (`test_regresiones.py:416-433`) ya existe y falla. Se comprueba que hoy figura como fallo esperado.
   - Se escriben las pruebas nuevas que fallen hoy:
     - Opciones A y B: el orden de anidación (una vista de prueba que escribe y después lanza una excepción no deja rastro en la base) y el paso de `Http404` y `PermissionDenied`.
     - Opción C: ninguna vista de `pedidos/views.py` usa `transaccion_segura`, y una excepción en una de las vistas que lo usaban deja **una sola** línea de error, con traza, en `django.request`.
   - Se registra en la bitácora cuántas fallan antes de la corrección.
3. **Implementar la opción elegida** en `pedidos/decorators.py` y en las 17 vistas (tabla de arriba). No se tocan las capturas internas de ítems (`views.py:193`, `:270`, `:768`, `:813`): son de la 03-02 y la 03-03.
4. **Retirar R20 como regresión** en el mismo cambio, como indica `docs/operacion/pruebas.md` («Cómo se retira una regresión»):
   - Quitar `@expectedFailure` y `@tag('regresion')` de `test_r20_pk_inexistente_responde_404`.
   - Cambiar la caracterización `test_acceso.PkInexistenteTests.test_vistas_con_transaccion_segura_responden_500` (`test_acceso.py:314-320`) para que afirme 404, con un nombre acorde, según el comentario de `test_regresiones.py:419-421`.
   - Valor vigente: de `expected failures=19` a **18**.
5. **Ajustar las pruebas del decorador** según la opción: `test_errores.py:46-58` (vista con decorador) y `:60-73` (`eliminar_pago`, que en GET sigue respondiendo 500 hasta la 04-01).
6. **Documentación de operación:**
   - `docs/operacion/pruebas.md`: valor vigente (`:99`), fila de R20 (`:121`) y filas de las rutas con `pk` inexistente (`:192-193`).
   - Si cambia el registrador (opción C), la guía para leer `server.log` en `docs/operacion/`.
7. **Caso de estudio AUD-02-008** en la bitácora: el ejemplo de `views.py:168-197` con el orden correcto y el incorrecto, sin corregirlo.
8. **Verificación** (`AGENTS.md`, sección 10):
   - `python manage.py test pedidos` → `OK (expected failures=18)` en tres ejecuciones.
   - `check` sin errores y `makemigrations --check --dry-run` sin cambios.
   - Revisión manual contra la réplica local: un `pk` inexistente en editar cliente y en convertir cotización responde con la página 404, en escritorio y a 360 px.
9. **Bitácora** `bitacora-03-01.md`, registro, auditoría (AUD-02-029 «Resuelto en 03-01»; AUD-01-001 con nota de avance) y estado «En revisión».

## Criterios de aceptación

- [ ] La decisión 1 está registrada (RDA-019 si corresponde) antes de implementar.
- [ ] Las pruebas nuevas se escribieron antes de la corrección y fallaban; el número consta en la bitácora.
- [ ] Ningún componente del proyecto se llama `transaccion_segura` ni promete una transacción que no abre.
- [ ] Ninguna respuesta lleva `str(e)` en su contexto (`mensaje_tecnico` desaparece).
- [ ] R20 está en verde, sin `@expectedFailure` ni `@tag('regresion')`, y la caracterización de `test_acceso` afirma 404 en las 12 rutas.
- [ ] `python manage.py test pedidos` → `OK (expected failures=18)`; ninguna otra regresión cambia de estado (R1 a R4 siguen como fallo esperado).
- [ ] Un error en una de las 17 vistas sigue respondiendo 500 con `pedidos/errors/500.html` y deja en el registro la traza completa con método, ruta y usuario.
- [ ] `docs/operacion/pruebas.md` dice 18 y describe las rutas con `pk` inexistente como 404.
- [ ] El caso de estudio de AUD-02-008 está en la bitácora.

## Fuera de alcance

- Corregir la pérdida de ítems y la supresión silenciosa en `crear_pedido`, `editar_pedido`, `crear_cotizacion` y `editar_cotizacion`: 03-02 (avance) y 03-03 (cierre de AUD-01-002 con R1, R2 y R4, y de AUD-02-008 con R3).
- Fijar las fronteras transaccionales de cada vista y `estado_pago` (AUD-02-004): 03-03.
- Mensajes al usuario, conservación de formularios y envío único (R21): 03-04.
- La plantilla que falta en `eliminar_pago` (R7) y las escrituras por GET (R6): 04-01.
- Mover transacciones a servicios: 07-02 (RDA-015).

## Despliegue

- La tabla de la épica asigna el despliegue a la 03-05 («Validación y despliegue de la integridad», `definicion-epica-03.md:42`). Si la 03-01 viaja en ese despliegue o tiene uno propio (RDA-007): `PENDIENTE_DESARROLLADOR`.
- Sin migraciones ni cambios de datos.

## Riesgos

| Riesgo | Mitigación |
| :----- | :--------- |
| Opciones A o B: un error que hoy confirma a medias pasa a revertirse en 17 vistas, sin que la 03-03 lo haya revisado vista por vista | Pruebas por vista en la 03-03, o elegir C |
| Opción C: quien lee `server.log` busca `pedidos.decorators` y no lo encuentra | Actualizar la guía de `docs/operacion/` en la misma iteración |
| El número de fallos esperados no baja a 18 y `despliegue.md` (paso 1) rechaza la versión | Retirar R20 en el mismo cambio y actualizar `pruebas.md` |

## Decisiones del desarrollador

1. Qué hacer con el decorador (A, B o C) y si se registra como RDA-019: `PENDIENTE_DESARROLLADOR`.
2. Nombre del componente nuevo, solo en A o B: `PENDIENTE_DESARROLLADOR`.
3. Si AUD-01-001 se cierra en la 03-01 (opción C: el componente desaparece) o en la 03-03, como dice su fila: `PENDIENTE_DESARROLLADOR`.
4. Despliegue propio o junto con la 03-05: `PENDIENTE_DESARROLLADOR`.

## Datos requeridos del cliente

- Ninguno.
