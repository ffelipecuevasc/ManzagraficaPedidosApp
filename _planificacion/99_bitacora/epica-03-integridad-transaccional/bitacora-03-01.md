# Bitácora 03-01 · Rediseño del decorador transaccional

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión

## Resumen

Se aplicó la opción C (RDA-019): se retiró `@transaccion_segura` de las 17 vistas y se eliminó `pedidos/decorators.py`. Los errores de vista quedan en el manejo nativo de Django: una sola línea `django.request` con traza y la página 500 de la 01-03. Un `pk` inexistente responde 404. R20 pasó a verde y se retiró como regresión, así que los fallos esperados bajan de 19 a 18. AUD-02-029 queda resuelto y AUD-01-001 avanza; su cierre es en la 03-03. No se tocaron las capturas internas de ítems ni R1 a R4. Sin despliegue propio: viaja con la 03-05.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/decorators.py` | Eliminado (33 líneas). |
| `pedidos/views.py` | 18 líneas menos: `from .decorators import transaccion_segura` (`:15`) y las 17 líneas `@transaccion_segura`. Sin otro cambio. |
| `pedidos/tests/test_errores.py:27-46` | Pruebas nuevas, escritas antes de corregir: `test_decorador_transaccion_segura_retirado` y `test_error_en_vista_que_usaba_el_decorador_deja_una_sola_linea_con_traza`. |
| `pedidos/tests/test_errores.py:66-79` | La prueba del decorador pasa a `test_excepcion_en_vista_que_tenia_el_decorador_registra_vista_y_traza`: registrador `django.request` y la vista leída en la traza. |
| `pedidos/tests/test_errores.py:85-86` | `test_regresion_eliminar_pago_deja_tipo_y_traza`: la línea se lee en `django.request`. |
| `pedidos/tests/test_acceso.py:268-304` | `CON_500` pasa a `DECORADOR_RETIRADO`. La caracterización pasa a `test_vistas_que_tenian_transaccion_segura_responden_404`. Se quitan `absorber_errores` y el import de `contextmanager`, que quedaron sin uso. |
| `pedidos/tests/test_regresiones.py:8-9` y `:417-430` | R20 sin `@expectedFailure` ni `@tag('regresion')`, como prueba normal y sin absorber errores; nota en la numeración del encabezado. |
| `docs/operacion/pruebas.md:99`, `:120-122` y `:192-193` | Valor vigente 18; fila de R20 retirada de la tabla y explicada en una viñeta; las 12 rutas responden 404. |
| `docs/operacion/despliegue.md:38-39` | Guía de `server.log`: registrador `django.request`, una línea por error. |
| `_planificacion/00_producto/decisiones.md:27` y `:247-256` | RDA-019 y su fila en el índice. |
| `_planificacion/00_producto/auditoria-tecnica.md:23` | AUD-01-001: nota de avance; se cierra en la 03-03. |
| `_planificacion/00_producto/auditoria-tecnica.md:94` | AUD-02-029: «Resuelto en 03-01». |
| `_planificacion/10_epicas/epica-03-integridad-transaccional/iteracion-03-01-rediseno-decorador-transaccional.md` | Estado «En revisión», decisiones resueltas y criterios marcados (salvo la revisión a 360 px). |
| `_planificacion/00_producto/registro-pendientes.md:6`, `:7`, `:16`, `:43` y `:298` | Estado, siguiente paso (03-02), fila 03-01 e historial. |

## Verificación

Todo con `DB_NAME=manzagrafica_replica` en la sesión. Las pruebas usan la base `test_manzagrafica` en el MySQL local de Docker.

- **Antes de corregir** (solo con las pruebas nuevas escritas): `python manage.py test pedidos` → 186 pruebas, `FAILED (failures=2, expected failures=19)`. Las 2 que fallaron fueron las nuevas, por la razón esperada:
  - `ImportError not raised`: el módulo del decorador seguía existiendo.
  - La lista de registradores daba `['pedidos.decorators', 'django.request']` en vez de `['django.request']`.
  - R20 seguía como fallo esperado.
- **Después de corregir:** `python manage.py test pedidos` → 186 pruebas, `OK (expected failures=18)` en tres ejecuciones (304 s, 285 s y 293 s). Sin `unexpected successes`.
- `python manage.py check` → sin problemas.
- `python manage.py makemigrations --check --dry-run` → `No changes detected`.
- **Revisión de pantallas** en escritorio y a 360 px contra la réplica: no hecha. La hace el desarrollador (criterio sin marcar).

## Migraciones

- Ninguna.

## Caso de estudio · AUD-02-008 (sin corregir)

`crear_pedido` (`pedidos/views.py`, ahora unas líneas más arriba por el decorador retirado) es la única vista con `transaction.atomic`. Dentro del bloque, un `try/except Exception` envuelve la creación de los ítems. Si un ítem falla, la excepción se captura **dentro** del bloque atómico: para la base no ocurrió nada y la transacción se **confirma** con el pedido y los ítems creados hasta el fallo. La reversión solo ocurre si la excepción **sale** del bloque.

```python
# Hoy (mal): se confirma con datos a medias
with transaction.atomic():
    pedido.save()
    try:
        crear_items()
    except Exception:
        logger.exception(...)

# Orden correcto: la captura va fuera; si algo falla, se revierte todo
try:
    with transaction.atomic():
        pedido.save()
        crear_items()
except ErrorConocido:
    logger.exception(...)
    # informar al usuario
```

Retirar el decorador no cambia este comportamiento, porque el decorador nunca abrió una transacción. R3 sigue como fallo esperado y la corrección es de la 03-03 (nota del 2026-11-04 en AUD-02-008).

## Criterios de aceptación

- [x] Decisión registrada antes de implementar: RDA-019.
- [x] Pruebas nuevas escritas antes de la corrección; 2 fallaban (ver «Verificación»).
- [x] Ningún componente se llama `transaccion_segura`: el módulo ya no existe y `views.py` no lo nombra (la prueba lo comprueba).
- [x] `mensaje_tecnico` y `str(e)` desaparecen con el decorador.
- [x] R20 en verde y sin marcas; la caracterización de `test_acceso` afirma 404 en las 12 rutas.
- [x] `OK (expected failures=18)` en tres ejecuciones; R1 a R4 siguen como fallo esperado.
- [x] Un error en una vista que tenía el decorador responde 500 con `pedidos/errors/500.html` y deja una sola línea `django.request` con traza, método, ruta y usuario.
- [x] `pruebas.md` dice 18 y describe las rutas con `pk` inexistente como 404.
- [x] Caso de estudio de AUD-02-008 en esta bitácora.
- [ ] Revisión manual a 360 px y en escritorio (la hace el desarrollador).

## Decisiones tomadas

Decisiones del desarrollador del 2026-11-04:

1. Opción C: retirar `@transaccion_segura` y eliminar `decorators.py`; se registra como RDA-019.
2. Nombre del componente: no aplica.
3. AUD-01-001 queda con nota de avance y se cierra en la 03-03.
4. La 03-01 viaja con la 03-05, sin despliegue propio.

Decisiones del agente dentro del alcance:

- Se quitaron `absorber_errores` de `test_acceso.py` y su import de `contextmanager`, que quedaron sin uso al pasar la caracterización a 404.
- La fila de R20 sale de la tabla de regresiones declaradas de `pruebas.md` y queda explicada en una viñeta, como indica la regla «Cómo se retira una regresión».

## Pendientes y riesgos

- **Revisión manual a 360 px:** abrir, con la réplica, un `pk` inexistente en editar cliente y en convertir cotización, y comprobar que se ve la página 404.
- **En producción, cuando se despliegue con la 03-05:** quien lea `server.log` ya no verá `registrador=pedidos.decorators`. La guía de `despliegue.md` lo explica.
- **Hasta la 03-03:** ninguna vista queda más protegida que antes; la atomicidad llega en esa iteración.
- **Para la 03-02:** las capturas internas de ítems siguen en `views.py` (antes `:193`, `:270`, `:768` y `:813`; ahora `:191`, `:267`, `:759` y `:803`).

## Commit sugerido

`Épica 3 - Iteración 03-01: retira @transaccion_segura de 17 vistas (RDA-019), R20 pasa a verde y los fallos esperados bajan de 19 a 18`
