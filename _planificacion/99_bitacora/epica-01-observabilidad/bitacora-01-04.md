# Bitácora 01-04 · Instrumentación de eventos de negocio

- **Fecha:** 2026-10-25
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión. Se despliega con 01-01 a 01-05 en 01-06 (`v1.1-observabilidad`). **Sin migraciones.**

## Resumen

- **15 eventos instrumentados**, los mismos 15 tipos de `RegistroEvento`. Sin cambios en el modelo ni migraciones.
  - **13 vistas en `pedidos/views.py`:** se agregó solo la llamada a `registrar_evento`. En `cambiar_estado_pedido` además se guarda el estado anterior, para registrar solo los cambios reales.
  - **2 señales de acceso** en el archivo nuevo `pedidos/senales.py`, conectadas en `PedidosConfig.ready()` (`pedidos/apps.py`). Los dos cambios, aprobados.
- **Un evento por acción del usuario** (decisión del desarrollador): una operación compuesta deja una sola fila y el detalle va en el resumen.
- **19 pruebas nuevas** en `pedidos/tests/test_eventos_negocio.py`. En total son 61, en verde tres veces.
- **Estimación de 01-01:** sin cambios. Mismos tipos, y una fila por acción, igual que el supuesto de la estimación.

## Cierre de la 01-03 (2026-10-25)

- La 01-03 quedó `Terminada` y AUD-01-004 pasó a `Cerrado`.
- La revisión visual de la página 500 a 360 px pasó a la 01-06 (tarea 7), con constancia en el criterio de la 01-03.
- El fin de línea mezclado de `settings.py` queda como propuesta, sin cambios (sección 3 del registro).
- La regla 4 de `AGENTS.md` queda `PENDIENTE_DESARROLLADOR`: la revisa el desarrollador.

## Inventario de eventos

Líneas finales, después de instrumentar. Las líneas de `pedidos/views.py` corresponden a la llamada a `registrar_evento`.

| Tipo | Archivo | Función | Línea | Momento | Entidad | Resumen (solo identificadores) |
| :--- | :------ | :------ | :---- | :------ | :------ | :----------------------------- |
| `pedido_creado` | `pedidos/views.py` | `crear_pedido` | 223 | Dentro del `atomic()`, tras el pedido, los ítems y el abono; se escribe al confirmar | `pedido` | `Pedido #N creado` o `… creado con abono inicial` |
| `pedido_modificado` | `pedidos/views.py` | `editar_pedido` | 272 | Tras `form.save()` y los ítems | `pedido` | `Pedido #N modificado` |
| `pedido_eliminado` | `pedidos/views.py` | `eliminar_pedido` | 304 | Tras `delete()`, solo con POST | `pedido` | `Pedido #N eliminado` |
| `pedido_estado_cambiado` | `pedidos/views.py` | `cambiar_estado_pedido` | 325 | Tras `save()`, solo si el estado es válido y distinto (ruta GET, 04-01) | `pedido` | `Pedido #N: PENDIENTE -> EN_PROCESO` |
| `pedido_duplicado` | `pedidos/views.py` | `duplicar_pedido` | 421 | Tras guardar la copia (ruta GET, 04-01) | `pedido` (el nuevo) | `Pedido #N duplicado desde el pedido #M` |
| `pago_registrado` | `pedidos/views.py` | `ingresar_pago` | 1415 | Tras el pago y el estado del pedido | `pago` | `Pago #N registrado en el pedido #M` |
| `pago_modificado` | `pedidos/views.py` | `editar_pago` | 1445 | Tras recalcular el estado | `pago` | `Pago #N modificado en el pedido #M` |
| `pago_eliminado` | `pedidos/views.py` | `eliminar_pago` | 1475 | Tras `delete()` y el recálculo, solo con POST | `pago` | `Pago #N eliminado del pedido #M` |
| `cotizacion_convertida` | `pedidos/views.py` | `convertir_a_pedido` | 914 | Tras cerrar la cotización | `cotizacion` | `Cotización #N convertida en el pedido #M` |
| `cliente_eliminado` | `pedidos/views.py` | `eliminar_cliente` | 619 | Tras `delete()`, solo con POST | `cliente` | `Cliente #N eliminado` |
| `producto_eliminado` | `pedidos/views.py` | `eliminar_producto` | 1023 | Tras `delete()`, dentro del `try`; no se registra si salta `ProtectedError` | `producto` | `Producto #N eliminado` |
| `respaldo_generado` | `pedidos/views.py` | `generar_respaldo_bd` | 1121 | Tras `generar_respaldo_mysql()` (ruta GET, 04-01) | `respaldo` | `Respaldo <archivo>.sql generado` |
| `restauracion_ejecutada` | `pedidos/views.py` | `restaurar_bd` | 1181 | **Después** de `restaurar_bd_mysql()`, para que la restauración no borre el evento | `base_de_datos` | `Base de datos restaurada desde un archivo .sql, con respaldo previo` |
| `acceso_exitoso` | `pedidos/senales.py` | `acceso_exitoso` (`user_logged_in`) | 13 | Al iniciar sesión | `usuario` | `Acceso de usuario #N` |
| `acceso_fallido` | `pedidos/senales.py` | `acceso_fallido` (`user_login_failed`) | 20 | Al fallar el inicio de sesión | `usuario`, sin id | `Usuario intentado: <nombre>` (máximo 150 caracteres, sin contraseña) |

**Coincide con los 15 tipos de `RegistroEvento.TIPO_CHOICES`:** ninguno sobra, ninguno falta, ninguno se renombró. No hace falta migración ni recalcular por cambio de tipos.

## Decisiones del desarrollador (2026-10-25)

1. **Un evento por acción del usuario.** Crear un pedido con abono registra solo `pedido_creado`, con el resumen «… con abono inicial». Convertir una cotización registra solo `cotizacion_convertida`, aunque cree un pedido, sus ítems y quizá un pago. Restaurar registra solo `restauracion_ejecutada`, aunque genere antes un respaldo de emergencia. **Consecuencia aceptada:** filtrar por `pago_registrado` no muestra los abonos iniciales. Registrada en «Decisiones de la épica».
2. **Señales de acceso:** archivo nuevo `pedidos/senales.py` y método `ready()` en `pedidos/apps.py`, tal como se propusieron.

## Reglas aplicadas

- **Después de confirmar:** todas las llamadas pasan por `transaction.on_commit`. Las vistas sin transacción (casi todas, hasta la Épica 03) escriben tras el guardado ya confirmado. `crear_pedido`, que sí tiene `atomic()`, escribe solo si se confirma.
- **Nunca en lecturas:** una prueba recorre 15 rutas de solo lectura (panel, listados, detalles, estadísticas, trabajo semanal y pantallas de base de datos) y no aparece ningún evento. La prueba de costo de 01-02 ahora intercepta `pedidos.views.registrar_evento` y sigue con 4 consultas en `/pagos/lista/`.
- **Rutas que escriben con GET** (cambio de estado, duplicación, respaldo): el evento se registra igual. Pasarlas a POST es de la 04-01.
- **Sin datos personales en el resumen:** solo identificadores (`#N`), estados y el nombre del archivo de respaldo. Sin montos, nombres ni teléfonos. La única excepción la pide el criterio: el nombre de usuario intentado en un acceso fallido.
- **Eventos del sistema:** hoy no hay ninguno; llegan con la orden de mantención de la 06-02. Convención escrita en `pedidos/eventos.py`: usuario nulo y resumen que empieza con «Origen: <orden o proceso> ·».

## Contraste con la estimación de 01-01

- **Tipos:** los mismos 15.
- **Filas por acción:** una, como suponía la estimación. Con «un evento por efecto» habrían aparecido filas extra de `pago_registrado` y `pedido_creado`.
- **Cambios de estado:** solo se registran los reales (estado distinto del anterior), así que la cifra queda igual o por debajo del supuesto de 3 por pedido.
- **Accesos:** `user_logged_in` también se dispara al entrar al admin de Django. Con un solo usuario, cabe en el supuesto de 5 accesos al día.
- **Conclusión:** la estimación se mantiene: ~1.200 filas y ~0,6 MB por mes; ~18 MB en régimen con los respaldos (5,4 % del disco libre). No se recalcula. La cifra real se mide en 01-06.

## Desviaciones y observaciones

- **Restauración y la tabla de eventos:** la restauración reemplaza todas las tablas con las del volcado, incluida `pedidos_registroevento`. Los eventos posteriores a ese volcado se pierden, y por eso el de la restauración se escribe después. Si el volcado no trae el usuario que restauró, la clave foránea rechaza la fila. El servicio absorbe el error y lo deja en `error.log` con traza: el evento se pierde, pero la restauración no falla. Es una limitación conocida, que conviene recordar en 04-04 (endurecimiento de la restauración).
- **Riesgo del acceso fallido:** si alguien escribe su contraseña en el campo de usuario, quedaría en el resumen. El criterio exige guardar el nombre intentado; se recorta a 150 caracteres.
- **Prueba del respaldo:** cerrar a mano el `FileResponse` dispara `request_finished`, y Django cierra la conexión en medio de la transacción de la prueba (error 2006). La prueba no lo cierra y usa `ignore_cleanup_errors` para la carpeta temporal en Windows. No afecta a la aplicación.
- **Pruebas de restauración** sin ejecutar `mysql`: se simulan `generar_respaldo_mysql` y `restaurar_bd_mysql`, y `BASE_DIR` apunta a una carpeta temporal, para no escribir en `backups/`.
- **Atomicidad:** las operaciones siguen sin `atomic()` (Épica 03). Si una vista falla después de guardar y antes de llamar al servicio, la operación queda hecha sin su evento. Pasa a ser imposible cuando 03-03 envuelva cada vista.

## Verificación

PowerShell 7, `DB_NAME=manzagrafica_replica`.

**Pruebas por evento** (`test_eventos_negocio.py`; cada una ejecuta la operación y comprueba **exactamente una fila** con tipo, usuario, entidad e id):

| Evento | Prueba |
| :----- | :----- |
| `pedido_creado` (con abono: un solo evento, aunque crea un pago) | `test_pedido_creado_con_abono_deja_un_solo_evento` |
| `pedido_modificado` | `test_pedido_modificado` |
| `pedido_eliminado` | `test_pedido_eliminado` |
| `pedido_estado_cambiado` (GET) | `test_pedido_estado_cambiado_por_get`; además `test_estado_igual_o_invalido_no_deja_evento` |
| `pedido_duplicado` | `test_pedido_duplicado` |
| `pago_registrado` (sin monto en el resumen) | `test_pago_registrado` |
| `pago_modificado` | `test_pago_modificado` |
| `pago_eliminado` | `test_pago_eliminado` |
| `cotizacion_convertida` (un solo evento) | `test_cotizacion_convertida_deja_un_solo_evento` |
| `cliente_eliminado` | `test_cliente_eliminado` |
| `producto_eliminado` | `test_producto_eliminado`; además `test_producto_protegido_no_deja_evento` |
| `respaldo_generado` (con su usuario) | `test_respaldo_generado_con_su_usuario` |
| `restauracion_ejecutada` (simulada, con su usuario) | `test_restauracion_simulada_con_su_usuario`; además `test_restauracion_fallida_no_deja_evento` |
| `acceso_exitoso` | `test_acceso_exitoso` |
| `acceso_fallido` (nombre sin contraseña) | `test_acceso_fallido_registra_el_nombre_sin_la_contrasena` |
| Lecturas sin eventos (15 rutas, todas en 200) | `test_listados_detalles_y_estadisticas_no_crean_eventos` |

- `python manage.py test pedidos`: **61 pruebas en `OK`** en tres ejecuciones (40,0 s, 40,7 s y 53,9 s), sin líneas de registro sueltas.
- `python manage.py check`: sin problemas.
- `makemigrations --check --dry-run`: `No changes detected`. **Sin migraciones.**
- Conteos de la réplica sin cambios (`pedidos_registroevento` = 0).

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/views.py` | Importa `registrar_evento`; 13 llamadas |
| `pedidos/senales.py` | Nuevo (aprobado): señales de acceso |
| `pedidos/apps.py` | `ready()` conecta las señales (aprobado) |
| `pedidos/eventos.py` | Docstring: un evento por acción y convención de eventos del sistema |
| `pedidos/tests/test_eventos_negocio.py` | Nuevo: 19 pruebas |
| `pedidos/tests/test_eventos.py` | La prueba de costo intercepta `pedidos.views.registrar_evento` |
| `docs/operacion/pruebas.md` | Tabla de archivos de prueba |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-01-004 cerrado |
| `_planificacion/00_producto/registro-pendientes.md` | Cierre de 01-03, estado de 01-04, sección 3 e historial |
| `_planificacion/10_epicas/epica-01-observabilidad/definicion-epica-01.md` | Estados y decisión «un evento por acción» |
| `_planificacion/10_epicas/epica-01-observabilidad/iteracion-01-03-retiro-middleware.md`, `iteracion-01-04-eventos-negocio.md`, `iteracion-01-06-despliegue-validacion.md` | Cierre de 01-03, estado de 01-04 y tarea 7 de 01-06 |
| `_planificacion/99_bitacora/epica-01-observabilidad/bitacora-01-03.md` | Estado final |

## Despliegue

- **Sin migraciones.** Viaja en 01-06, que exige respaldo previo por la 0007 de la 01-01.
- En 01-06, la acción de prueba de la evidencia (por ejemplo, un acceso o un cambio de estado de un pedido de prueba) debe aparecer en el admin de eventos (01-05) con su usuario.

## Pendientes

- Revisión del desarrollador.
