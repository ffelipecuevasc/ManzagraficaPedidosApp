# Bitácora 01-02 · Configuración del registro y servicio de eventos

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada (2026-10-25, revisada por el desarrollador); sin desplegar; en 01-06 se comprueba que `error.log` no reciba líneas duplicadas por un manejador propio de PythonAnywhere. Sin migraciones. **Actualización 2026-10-26:** desplegada el 2026-10-25 en `v1.1-observabilidad` (commit `d6768d0`).

## Resumen

- **`LOGGING`** en `settings.py`, aprobado por el desarrollador:
  - Un único manejador `stderr` en la raíz, con formato `clave=valor`.
  - Niveles: `django` en `WARNING` sin sus manejadores por defecto, `django.request` en `ERROR`, `django.security` en `WARNING`, `pedidos` en `INFO`.
  - `fontTools` en `WARNING` con su propio manejador y `propagate=False`; `weasyprint` en `WARNING`.
- **Filtro de contexto** en `pedidos/registro.py` (archivo nuevo, aprobado): agrega método, ruta sin la cadena de consulta, usuario (id, `anonimo` o `-`), tipo de excepción y el mensaje entre comillas. No toca el `MIDDLEWARE`.
- **Servicio de eventos** `registrar_evento()` en `pedidos/eventos.py`: escribe con `transaction.on_commit` y nunca lanza una excepción hacia quien lo llama. Sin cambios en `models.py` ni migraciones.
- **Ruido de `fontTools` eliminado:** un PDF real pasó de **540 líneas** (292 DEBUG y 248 INFO) a **0**. La causa la explica la observación 1.
- **Pruebas:** de 17 a **34**, en verde tres veces seguidas: 8 en `test_registro.py`, 9 del servicio en `test_eventos.py`.

## A1 · Estado actual (antes de 01-02)

- **`settings.py` no tenía `LOGGING`.** Regía la configuración por defecto de Django:
  - `django` con un manejador de consola que solo actúa con `DEBUG=True` y otro de correo que no hace nada sin `ADMINS`;
  - `django.server` con su propio manejador;
  - la raíz en `WARNING`, sin manejadores;
  - `fontTools`, `weasyprint` y `pedidos` sin manejadores propios.
- **Medido en local con `DEBUG=False`:** un `ERROR` de `django.request` **no** llega a stderr, y un INFO de `fontTools` tampoco. Solo pasan los `WARNING` y superiores, por el manejador de último recurso de Python.
- **En producción sí aparecen ambos en `error.log`** (Épica 00: `Internal Server Error: /pagos/eliminar/1056/` y cientos de líneas de `fontTools`). Hipótesis: el cargador WSGI de PythonAnywhere instala un manejador en la raíz con nivel INFO. Un `DEBUG=True` en producción explicaría la línea de `django.request`, pero no los INFO de `fontTools`. Queda como pista en `definicion-epica-01.md`, para comprobar en 01-06 que no haya líneas duplicadas.
- **`error.log`:** recibe la salida de error del proceso. PythonAnywhere antepone su fecha en UTC, por eso el formato no la repite.
- **`server.log`:** recibe los `print` (salida estándar), en hora de Chile: los del middleware (`🔴 Error capturado por Middleware`) y del decorador (`⚠️ Error capturado por decorador`), sin traza. En `utils.py` y `views.py` hay otros 6 `print`. Los del middleware y el decorador se tratan en 01-03; el resto, en la épica 03 o la 06.
- **Mientras exista el middleware (hasta 01-03):** una excepción en una vista se convierte en una respuesta 500 sin pasar por `django.request` con su traza. Django registra igual `Internal Server Error: <ruta>` (por el código 500), pero sin `exc_info`.

## Configuración elegida

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {'contexto_peticion': {'()': 'pedidos.registro.FiltroContextoPeticion'}},
    'formatters': {'clave_valor': {'format': (
        'nivel=%(levelname)s registrador=%(name)s metodo=%(metodo)s '
        'ruta=%(ruta)s usuario=%(usuario)s excepcion=%(excepcion)s mensaje=%(mensaje_cv)s')}},
    'handlers': {'stderr': {'class': 'logging.StreamHandler', 'stream': 'ext://sys.stderr',
                            'filters': ['contexto_peticion'], 'formatter': 'clave_valor'}},
    'root': {'handlers': ['stderr'], 'level': 'WARNING'},
    'loggers': {
        'django': {'handlers': [], 'level': 'WARNING', 'propagate': True},
        'django.request': {'level': 'ERROR'},
        'django.security': {'level': 'WARNING'},
        'pedidos': {'level': 'INFO'},
        'fontTools': {'handlers': ['stderr'], 'level': 'WARNING', 'propagate': False},
        'weasyprint': {'level': 'WARNING'},
    },
}
```

Ejemplo de línea en `error.log`, con la fecha que antepone PythonAnywhere:

```text
2026-10-22 19:19:04,512: nivel=ERROR registrador=django.request metodo=GET ruta=/pagos/eliminar/1056/ usuario=1 excepcion=TemplateDoesNotExist mensaje="Internal Server Error: /pagos/eliminar/1056/"
2026-10-22 19:19:04,512: Traceback (most recent call last):
...
```

- **Convención del proyecto** (docstring de `pedidos/registro.py`): `logger = logging.getLogger(__name__)` en cada módulo y, dentro de una vista, `logger.exception('…', extra={'request': request})`.
- **Datos sensibles:** el filtro solo lee `request.method`, `request.path` y `request.user.pk`. No lee el cuerpo, las cookies ni la cadena de consulta. Las trazas pueden incluir el mensaje de la excepción, que escribe el código; las vistas de 01-03 en adelante no deben poner datos de clientes en esos mensajes.

## B · Diseño del servicio de eventos

1. **Fallo en cascada:** `registrar_evento` tiene dos capturas amplias, una al programar el evento y otra al escribirlo. Cada una registra el problema con `logger.exception` (con traza, en `error.log`) y retorna. Son las capturas permitidas por `AGENTS.md`, regla 4, y el código lo dice en un comentario. Con el filtro de contexto pasa lo mismo: si falla, escribe un aviso a stderr y deja pasar el registro.
2. **Costo por petición:** el servicio solo se llamará desde los puntos del inventario de 01-04. Una prueba fija en 4 las consultas de `/pagos/lista/` y comprueba que la vista no llama al servicio.
3. **Registro después de confirmar:** `transaction.on_commit`. Sin una transacción abierta (modo autocommit, como en las vistas de hoy), escribe de inmediato tras el guardado, que ya está confirmado. Dentro de `atomic()`, escribe solo si la transacción se confirma.
4. **Usuario:** nulo para los eventos del sistema y para los anónimos (`AnonymousUser`). El resumen se recorta a 255 caracteres.

## Desviaciones y observaciones

1. **El nivel `WARNING` no bastaba para `fontTools`.** Al recortar las fuentes, WeasyPrint usa `capture_logs('fontTools')` (`weasyprint/pdf/fonts.py:283`, `weasyprint/logger.py`): baja `fontTools` a `DEBUG`, reemplaza sus manejadores y deja `propagate=True`, así que todo sube al manejador de la raíz. Es la causa del ruido de producción. Con la primera versión aprobada, el PDF seguía mostrando líneas DEBUG e INFO. Se consultó y el desarrollador aprobó `propagate=False` con manejador propio. Una prueba reproduce `capture_logs`.
2. **`runserver` muestra los 4xx de `django.server` con el formato del proyecto.** Al reconfigurar, `django.server` queda sin manejador propio y propaga a la raíz. Los 2xx no se ven (`django` en `WARNING`). Solo afecta a `runserver`: en PythonAnywhere, uWSGI escribe los accesos en `access.log`.
3. **Los 404 dejan de llegar a `error.log`** porque `django.request` queda en `ERROR`. Incluye la línea `Not Found` de `favicon.ico` (propuesta fuera de alcance del 2026-10-25).
4. **Verificación manual de un error 500 con traza en `runserver`:** no se hizo. Con el middleware activo, el 500 de una vista no trae traza hasta 01-03, y provocarlo exige iniciar sesión, lo que escribe `last_login` y una sesión en la réplica. El formato con traza completa está cubierto por `test_error_en_peticion_lleva_contexto_y_traza_completa`. El error forzado en `runserver` fue un POST sin CSRF.
5. **El PDF de la verificación** se generó llamando a la vista en el mismo proceso, con el superusuario cargado de la réplica y sin iniciar sesión, para no escribir en ella. Conteos de la réplica idénticos antes y después.

## Verificación

Todo en PowerShell 7 o Bash, con `DB_NAME=manzagrafica_replica`.

**Error forzado contra `runserver`** (POST sin CSRF a `/accounts/login/` con usuario y contraseña ficticios; respuesta 403). Salida de error de `runserver`:

```text
nivel=WARNING registrador=django.security.csrf metodo=POST ruta=/accounts/login/ usuario=anonimo excepcion=- mensaje="Forbidden (CSRF cookie not set.): /accounts/login/"
nivel=WARNING registrador=django.server metodo=- ruta=- usuario=- excepcion=- mensaje="\"POST /accounts/login/ HTTP/1.1\" 403 2907"
nivel=WARNING registrador=django.server metodo=- ruta=- usuario=- excepcion=- mensaje="\"GET /ruta-inexistente/ HTTP/1.1\" 404 13860"
```

La contraseña ficticia no aparece. El servidor se detuvo al terminar.

**PDF real** (primera cotización de la réplica):

| | Líneas de `fontTools` en stderr | Resultado |
| :- | :------------------------------ | :-------- |
| Antes (`propagate=True` repuesto solo para medir) | 540 (292 DEBUG, 248 INFO) | `200`, `application/pdf`, `%PDF` |
| Después | 0 | `200`, `application/pdf`, `%PDF`, 27.957 bytes |

**Pruebas nuevas** (`python manage.py test pedidos`: 34 pruebas en `OK` en tres ejecuciones, 12,5 s, 12,6 s y 12,3 s):

| Criterio | Prueba |
| :------- | :----- |
| Línea con nivel, método, ruta, usuario, excepción y traza | `test_registro.FormatoRegistroTests.test_error_en_peticion_lleva_contexto_y_traza_completa` |
| Anónimo, sin contraseña ni cuerpo del formulario | `test_anonimo_y_sin_datos_del_formulario` |
| Sin petición, guiones; comillas y saltos de línea escapados | `test_sin_peticion_usa_guiones` |
| El filtro no falla con un usuario dañado | `test_filtro_no_falla_con_usuario_roto` |
| `fontTools` INFO no, WARNING sí | `NivelesRegistradoresTests.test_fonttools_y_weasyprint_solo_desde_warning`, `test_recorte_de_fuentes_de_weasyprint_no_llega_a_la_raiz` |
| Niveles y un solo manejador | `test_niveles_de_django_y_de_la_aplicacion`, `test_un_solo_manejador_en_la_raiz` |
| Fallo en cascada | `test_eventos.ServicioEventosTests.test_fallo_al_escribir_no_lanza_y_queda_en_el_registro`, `test_fallo_al_programar_no_lanza`, `ServicioEventosTransaccionTests.test_error_real_de_la_base_no_corta_la_peticion` (`IntegrityError` real y la app responde 200 después) |
| Costo | `test_listado_no_usa_el_servicio_ni_suma_consultas` (4 consultas) |
| Confirmación | `test_registra_despues_de_confirmar`, `test_transaccion_revertida_no_deja_evento`, `test_transaccion_confirmada_deja_evento` |
| Usuario nulo y resumen | `test_anonimo_y_sistema_quedan_sin_usuario`, `test_resumen_largo_se_recorta` |

- `python manage.py check`: sin problemas.
- `makemigrations --check --dry-run`: `No changes detected`. **Sin migraciones.**
- Conteos de la réplica iguales a los de la 02-01 (`pedidos_registroevento` = 0).

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `PedidosApp/settings.py` | `LOGGING` (aprobado, con el ajuste de `fontTools` también aprobado) |
| `pedidos/registro.py` | Nuevo (aprobado): filtro de contexto y convención |
| `pedidos/eventos.py` | `registrar_evento` y `_escribir_evento` |
| `pedidos/tests/test_registro.py` | Nuevo: 8 pruebas |
| `pedidos/tests/test_eventos.py` | 9 pruebas del servicio |
| `docs/operacion/pruebas.md` | Tabla de archivos de prueba |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-02-servicio-registro.md` | Estado y criterios |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-06-despliegue-validacion.md` | Tarea 5: configuración de pruebas de 02-01 y `check --deploy` |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | Estado, pista de `fontTools` actualizada y nueva pista del manejador de PythonAnywhere |
| `_planificacion/10_epicas/epica-02-red-seguridad/*`, `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-01.md` | Cierre de la 02-01 |
| `_planificacion/00_producto/registro-pendientes.md` | Cierre de 02-01, estado de 01-02 e historial |

## Despliegue

- **Sin migraciones.** Viaja en 01-06, que ya exige respaldo previo por la 0007.
- **En 01-06, comprobar en `error.log`:**
  - que no haya líneas duplicadas (hipótesis del manejador de PythonAnywhere);
  - que los PDF no dejen líneas de `fontTools`;
  - que la fecha de PythonAnywhere siga apareciendo al inicio de cada línea.

## Pendientes

- Revisión del desarrollador.
