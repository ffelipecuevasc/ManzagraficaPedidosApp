# Bitácora 02-01 · Infraestructura de pruebas

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión. No despliega nada por sí sola: el cambio de `settings.py` solo afecta la ejecución de pruebas y viaja con el próximo despliegue.

## Resumen

- **Base de pruebas fija:** `test_manzagrafica`, con `CHARSET` `utf8mb4` y `COLLATION` `utf8mb4_unicode_ci` en `TEST`. Si el nombre coincide con `manzagrafica_local`, `manzagrafica_replica` o la base activa, la carga se detiene con `ImproperlyConfigured`.
- **Paquete `pedidos/tests/` por dominio:** `pedidos/tests.py` se trasladó con `git mv` y se repartió en 4 archivos. Se agregaron `factorias.py`, `test_entorno.py` y `test_factorias.py`.
- **Datos de prueba:** 10 funciones propias, sin dependencias. Las pruebas de eventos y de pagos ya las usan.
- **Modo SQL:** opción A, sin modo estricto, igual que producción; `test_entorno.py` lo comprueba.
- **Fallos esperados:** `expectedFailure` con `@tag('regresion')`, documentado sin prueba de demostración.
- **Documentación:** nuevo `docs/operacion/pruebas.md` y punto 1 de la lista de `docs/operacion/despliegue.md` actualizado.
- **17 pruebas en `OK`** en tres ejecuciones seguidas: las 10 anteriores, 4 de entorno y 3 de factorías.

## Decisiones del desarrollador (2026-10-25)

| # | Tema | Decisión |
| :- | :--- | :------- |
| 1 | Nombre de la base de pruebas | `test_manzagrafica` en `TEST`, con bloqueo de nombres reales |
| 2 | Caracteres y colación | Fijados en `TEST` con los valores de la línea base de 00-01: `utf8mb4`, `utf8mb4_unicode_ci`. Coinciden con `compose.yaml`, sin diferencias que avisar |
| 3 | `sql_mode` | Opción A, paridad con producción |
| 4 | Datos de prueba | Funciones propias, sin dependencias |
| 5 | Fallos esperados | `expectedFailure` con etiqueta `regresion`, sin prueba de demostración |
| 6 | Documentación | `docs/operacion/pruebas.md` y punto 1 de `despliegue.md` |

Antes de actuar, el desarrollador aprobó el diff de `settings.py` y autorizó el traslado de `pedidos/tests.py`.

## Cambio en `PedidosApp/settings.py`

Bloque agregado después de la configuración de producción, tal como se aprobó:

```python
# 3. Base de pruebas (iteración 02-01, RDA-006). Nombre fijo para que no dependa de DB_NAME;
#    juego de caracteres y colación de la línea base de producción (00-01). Django destruye
#    esta base al terminar las pruebas: nunca puede llamarse como una base real.
TEST_DB_NAME = 'test_manzagrafica'
BASES_REALES = {'manzagrafica_local', 'manzagrafica_replica', DATABASES['default'].get('NAME')}
if TEST_DB_NAME in BASES_REALES:
    raise ImproperlyConfigured(
        f'La base de pruebas no puede llamarse {TEST_DB_NAME!r}: coincide con una base real.'
    )
DATABASES['default']['TEST'] = {
    'NAME': TEST_DB_NAME,
    'CHARSET': 'utf8mb4',
    'COLLATION': 'utf8mb4_unicode_ci',
}
```

No se tocaron `OPTIONS`, `compose.yaml` ni los privilegios de MySQL.

## Traslado de las pruebas

| Antes (`pedidos/tests.py`) | Después |
| :------------------------- | :------ |
| `RobotsTxtTests` (3) | `pedidos/tests/test_rutas_publicas.py` |
| `ListaPagosRutaTests` (2) | `pedidos/tests/test_pagos.py` |
| `CargaDiferidaWeasyprintTests` (1) | `pedidos/tests/test_arranque.py` |
| `RegistroEventoTests` (4) | `pedidos/tests/test_eventos.py` (archivo trasladado con `git mv`) |

- **Mismos nombres de método antes y después.** Antes: 10 pruebas en `OK`. Después: esas 10, con su nueva ruta de módulo, más 7 nuevas.
- `RegistroEventoTests` usa ahora `crear_evento` y `crear_usuario` de `factorias.py`, en lugar de su ayudante local.
- `ListaPagosRutaTests` usa `crear_usuario`.

## Verificación

Todo en PowerShell 7.

**Salida de `python manage.py test pedidos -v 2`** con `DB_NAME=manzagrafica_replica` (extracto):

```text
Creating test database for alias 'default' ('test_manzagrafica')...
test_vistas_no_importan_weasyprint_al_cargar (pedidos.tests.test_arranque.CargaDiferidaWeasyprintTests...) ... ok
test_juego_de_caracteres_y_colacion (pedidos.tests.test_entorno.EntornoBaseDePruebasTests...) ... ok
test_modo_sql_igual_a_produccion (pedidos.tests.test_entorno.EntornoBaseDePruebasTests...) ... ok
test_nombre_de_la_base_de_pruebas (pedidos.tests.test_entorno.EntornoBaseDePruebasTests...) ... ok
test_zona_horaria_utc (pedidos.tests.test_entorno.EntornoBaseDePruebasTests...) ... ok
test_eliminar_usuario_conserva_sus_eventos (pedidos.tests.test_eventos.RegistroEventoTests...) ... ok
test_orden_purgar_registros_informa_las_filas_eliminadas (pedidos.tests.test_eventos.RegistroEventoTests...) ... ok
test_purga_elimina_solo_los_antiguos (pedidos.tests.test_eventos.RegistroEventoTests...) ... ok
test_purga_rechaza_retencion_menor_a_un_dia (pedidos.tests.test_eventos.RegistroEventoTests...) ... ok
test_cotizacion_con_items (pedidos.tests.test_factorias.FactoriasTests...) ... ok
test_pedido_con_items_y_pago (pedidos.tests.test_factorias.FactoriasTests...) ... ok
test_valores_unicos_por_llamada (pedidos.tests.test_factorias.FactoriasTests...) ... ok
test_ruta_con_barra_responde (pedidos.tests.test_pagos.ListaPagosRutaTests...) ... ok
test_ruta_sin_barra_redirige (pedidos.tests.test_pagos.ListaPagosRutaTests...) ... ok
test_acepta_head (pedidos.tests.test_rutas_publicas.RobotsTxtTests...) ... ok
test_rechaza_post (pedidos.tests.test_rutas_publicas.RobotsTxtTests...) ... ok
test_responde_sin_sesion_en_texto_plano (pedidos.tests.test_rutas_publicas.RobotsTxtTests...) ... ok
Ran 17 tests in 5.965s
OK
Destroying test database for alias 'default' ('test_manzagrafica')...
```

- **Tres ejecuciones seguidas:** 5,97 s, 6,08 s y 5,63 s, todas con 17 pruebas en `OK`.
- **Nombre fijo:** con `DB_NAME=manzagrafica_local` la base de pruebas también es `test_manzagrafica` (6,08 s, `OK`).
- **Bloqueo:** con `DB_NAME=test_manzagrafica`, `check` se detiene con `ImproperlyConfigured: La base de pruebas no puede llamarse 'test_manzagrafica': coincide con una base real.`
- **La base se crea y se destruye sola:** tras las ejecuciones, `SHOW DATABASES LIKE 'test%'` devuelve vacío. También desapareció `test_manzagrafica_replica`, que usaban las ejecuciones anteriores.
- **Bases reales intactas.** Conteos por tabla antes y después, idénticos:

| Tabla | Réplica | Local |
| :---- | :------ | :---- |
| `auth_user` | 1 | 1 |
| `pedidos_cliente` | 718 | 2 |
| `pedidos_pedido` | 866 | 13 |
| `pedidos_itempedido` | 844 | 16 |
| `pedidos_pago` | 1.029 | 13 |
| `pedidos_cotizacion` | 25 | 5 |
| `pedidos_itemcotizacion` | 52 | 8 |
| `pedidos_producto` | 55 | 7 |
| `pedidos_historialbd` | 189 | 16 |
| `pedidos_registroevento` | 0 | sin tabla (0007 solo está aplicada en la réplica) |

- `python manage.py check`: sin problemas.
- `python manage.py makemigrations --check --dry-run`: `No changes detected`.
- **Cambio de esquema:** ninguno.
- **Pantallas:** ninguna tocada.

## Desviaciones y observaciones

- **Ejecución interrumpida:** no se simuló. Queda documentado en `pruebas.md`: Django pregunta si puede borrar la base que quedó creada, y con `--noinput` la borra sin preguntar. El criterio de la iteración aceptaba documentarlo.
- **Advertencia `mysql.W002`:** sigue apareciendo, como se espera con la opción A. No se silenció: `SILENCED_SYSTEM_CHECKS` la ocultaría también en `check --deploy`.
- **Las factorías no aplican reglas de negocio** (no recalculan `valor_venta` ni `estado_pago`), para no decidir reglas `PENDIENTE_CLIENTE`. Los precios por defecto ($10.000 de precio unitario y $5.000 de pago) son valores ficticios.
- **`unexpected successes`:** con Django, una prueba marcada con `expectedFailure` que empieza a pasar hace fallar el conjunto. Así lo describe `pruebas.md`, y obliga a quitar la marca en la iteración que corrige el defecto.
- La base local sigue sin la migración 0007. No es parte de esta iteración: se aplicó solo en la réplica en la 01-01.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `PedidosApp/settings.py` | Bloque 3: base de pruebas (aprobado) |
| `pedidos/tests.py` → `pedidos/tests/test_eventos.py` | Trasladado (autorizado) y reducido a las pruebas de eventos |
| `pedidos/tests/__init__.py`, `factorias.py`, `test_entorno.py`, `test_factorias.py`, `test_rutas_publicas.py`, `test_pagos.py`, `test_arranque.py` | Nuevos |
| `docs/operacion/pruebas.md` | Nuevo |
| `docs/operacion/despliegue.md` | Punto 1 de la lista previa (RDA-012) |
| `_planificacion/00_producto/auditoria-tecnica.md` | Nota de AUD-02-020 con la decisión de 02-01 |
| `_planificacion/00_producto/registro-pendientes.md` | Estado, 6 decisiones resueltas e historial |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-01-infraestructura-pruebas.md` | Decisiones, estado y criterios |
| `_planificacion/10_epicas/epica-02-red-seguridad/definicion-epica-02.md` | Estado de la épica y nota del mecanismo |

## Despliegue

- **No requiere respaldo previo:** no hay migraciones ni cambios de datos. El bloque de `settings.py` no cambia el comportamiento en producción (`TEST` solo lo usa `manage.py test`), pero el bloqueo se evalúa al cargar la configuración: con `DATABASE_URL`, el nombre de producción no coincide con `test_manzagrafica`. Conviene que la lista de comprobación del próximo despliegue confirme que el `check` del servidor sigue limpio.

## Pendientes

- Revisión del desarrollador.
