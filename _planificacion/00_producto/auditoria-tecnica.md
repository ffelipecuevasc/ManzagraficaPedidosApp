# Auditoría técnica

Registro acumulativo de auditorías. Las auditorías se agregan al final y nunca se borran. Antes de agregar una, revisa el último número usado en este archivo y suma uno. Un hallazgo se marca como resuelto indicando la iteración o la RDA que lo cerró (por ejemplo, `Resuelto en 03-03` o `Resuelto en RDA-004`).

**Severidad:** Alta (bloquea la publicación o afecta al usuario o al negocio), Media (afecta calidad o rendimiento), Baja (mejora).

---

## Auditoría 01 · Hallazgos del plan de trabajo técnico

- **Fecha:** 2026-10-19 (fecha de registro; los hallazgos provienen de la auditoría que dio origen a `plan-de-trabajo.md`)
- **Auditor:** Francisco Felipe Cuevas Cerón, con asistencia de IA, según el plan de trabajo
- **Alcance:** código de la aplicación, configuración, plantillas y registro de uWSGI de producción

### Resumen

La aplicación funciona, pero no protege sus propios datos: el decorador que promete transacciones no abre ninguna, la edición de pedidos puede borrar ítems sin avisar, hay rutas que modifican datos con una petición GET y, cuando algo falla, no queda rastro para diagnosticar. A eso se suman problemas de rendimiento (consultas por fila, Tailwind compilado en el navegador, WeasyPrint cargado al arrancar) y de operación (respaldos en el mismo disco, riesgo de expiración silenciosa). La severidad «Crítico» y «Alto» del plan se registra como Alta; «Medio» como Media; «Bajo» y «Diferido» como Baja.

### Hallazgos

| ID | Severidad | Área | Hallazgo | Acción recomendada | Estado |
| :- | :-------- | :--- | :------- | :----------------- | :----- |
| AUD-01-001 | Alta | Integridad | El decorador `transaccion_segura` no abre transacción alguna: solo captura excepciones. | Separar atomicidad de manejo de errores y renombrar el componente con un nombre honesto. Iteraciones 03-01 y 03-03. | Abierto |
| AUD-01-002 | Alta | Integridad | Supresión silenciosa de excepciones (`except Exception: pass`) al guardar ítems; la edición de pedidos borra los ítems antes de recrearlos. | Propagar o capturar de forma específica y registrar. Iteración 03-02. Avance 01-09 (2026-10-26, sin desplegar): los fallos de ítems quedan registrados con `logger.exception`; la pérdida de datos sigue. | Abierto |
| AUD-01-003 | Alta | Seguridad | El cambio de estado y la duplicación de pedidos modifican datos con GET (CSRF, prelectura del navegador, rastreadores). | Convertir a POST con token y formularios en las plantillas. Iteración 04-01. | Abierto |
| AUD-01-004 | Alta | Observabilidad | `ErrorHandlingMiddleware` captura toda excepción, descarta la traza y desconecta el manejo de errores de Django. | Retirar el middleware y usar los manejadores 404/500 ya declarados. Iteración 01-03. | Cerrado (2026-10-25, 01-03: middleware retirado y eliminado, traza completa del decorador; en producción con 01-06) |
| AUD-01-005 | Alta | Observabilidad | Ausencia total de registro de errores y de eventos. | Según RDA-013 (2026-10-25): errores con `logging` a la salida de error, que PythonAnywhere guarda en `server.log` (opción A de la 01-06; la redacción original decía `error.log`), con traza completa y contexto de la petición; eventos de negocio en una tabla propia de MySQL con retención y purga, consultable en el admin. Iteraciones 01-01 a 01-06. | Abierto (avanzado en 01-01: modelo de eventos y purga; 2026-10-26: 01-01 a 01-05 y 01-07 desplegadas en `v1.1-observabilidad`, falta la parte D de la 01-06) |
| AUD-01-006 | Alta | Datos | El registro diario de métricas podría insertar una fila en cada visita al panel (`fecha_registro__date` con zona horaria). | Medir en producción (00-01) y corregir con rango de instantes (06-01). | Abierto (confirmado en producción el 2026-10-20, ver «Mediciones de producción») |
| AUD-01-007 | Alta | Arquitectura | Escritura de mantenimiento (métricas) dentro del ciclo de petición de dos vistas de lectura. | Orden de gestión de mantención diaria. Iteración 06-02. | Abierto |
| AUD-01-008 | Alta | Rendimiento | Propiedades del modelo que consultan la base por fila en plantillas (`total_pagado_real`, `saldo_pendiente`, `porcentaje_pagado`). | Anotaciones del conjunto de consulta. Iteración 05-02. | Abierto |
| AUD-01-009 | Alta | Configuración | `from PedidosApp import settings` en lugar de `django.conf.settings`. | Usar el objeto de configuración perezoso. Iteración 04-05. | Abierto |
| AUD-01-010 | Alta | Rendimiento | Compilador de Tailwind cargado desde CDN y ejecutado en el navegador en cada página. | Compilación local con pnpm. Iteración 05-04. | Abierto |
| AUD-01-011 | Alta | Rendimiento | WeasyPrint se importa al arrancar el proceso, aunque solo lo usa una vista. | Importación diferida (00-06) y revisión del resto de importaciones (05-01). | Avanzado en 00-06 (2026-10-25: WeasyPrint diferido; importar `pedidos.urls` de 1.029,0 a 26,3 ms en local); sigue abierto para 05-01 |
| AUD-01-012 | Media | Seguridad | Configuración de producción sin endurecer (cookies seguras, HTTPS, HSTS, orígenes CSRF de confianza). | Resolver `check --deploy` con criterio. Iteración 04-02. | Abierto |
| AUD-01-013 | Media | Seguridad | La contraseña de la base viaja como argumento de `mysqldump` y `mysql`, visible en la tabla de procesos del servidor compartido. | Pasarla por variable de entorno del subproceso o archivo de opciones con permisos restringidos. Iteración 04-03. | Abierto |
| AUD-01-014 | Media | Operación | Los respaldos viven en el mismo disco que la base que protegen; se retienen cinco volcados completos. | Extracción y verificación local; retención de dos o tres en servidor. Iteraciones 00-02 y 06-03. | Abierto |
| AUD-01-015 | Media | Calidad | Cero pruebas automatizadas en una aplicación que maneja dinero. | Red de pruebas sobre lógica de dinero, flujos críticos y regresiones. Iteraciones 02-01 a 02-05. | Abierto |
| AUD-01-016 | Media | Configuración | Conexiones reutilizadas 60 segundos sin verificación de salud; fallos intermitentes tras hibernación. | `CONN_HEALTH_CHECKS`. Iteración 04-05. | Abierto |
| AUD-01-017 | Media | Rendimiento | El listado de clientes no tiene paginación. | Paginación. Iteración 06-06. | Abierto |
| AUD-01-018 | Media | Seguridad | El módulo de restauración ejecuta un SQL arbitrario sin validar el archivo. | Validación de extensión, tamaño y estructura; confirmación explícita; registro del evento. Iteración 04-04. | Abierto |
| AUD-01-019 | Media | Operación | La web app del plan gratuito expira sin aviso si la cuenta no registra actividad. | Recordatorio externo y procedimiento de renovación. Iteración 07-01. | Abierto |
| AUD-01-020 | Baja | Operación | Rastreadores sin ruta para `robots.txt` generan 404 con renderizado completo. | Publicar `robots.txt`. Iteración 00-06. | Resuelto en 00-06 (2026-10-25, `v0.2-correcciones`: 0 404 desde el despliegue). Seguimiento: confirmar 200 a un rastreador real con C2 (2026-11-20) |
| AUD-01-021 | Baja | Interfaz | Doble envío del formulario de acceso. | Deshabilitar el botón tras el primer envío. Iteración 00-06. | Resuelto en 00-06 (2026-10-25, `v0.2-correcciones`) |
| AUD-01-022 | Baja | Arquitectura | Todas las vistas en un único archivo de más de 1.500 líneas. | Dividir por dominio como refactorización pura. Iteración 06-04. | Abierto |
| AUD-01-023 | Baja | Repositorio | Configuración del IDE (`.idea/`) versionada. | Excluirla del repositorio. Iteración 00-04. | Cerrado (00-04, 2026-10-21) |
| AUD-01-024 | Baja | Arquitectura | Nomenclatura de rutas inconsistente entre secciones (incluida `pagos/lista` sin barra final). | Barra final en 00-06; normalización en 06-06. | Avanzado en 00-06 (2026-10-25: `pagos/lista/` con barra final); sigue abierto para 06-06 |
| AUD-01-025 | Baja | Calidad | Importaciones duplicadas y código muerto. | Limpieza. Iteración 04-05. | Abierto |
| AUD-01-026 | Baja | Datos | `estado_pago` duplica información derivable de los pagos (doble fuente de verdad). Corregirlo exige un cambio de Clase 3. | Deuda diferida: mantener ambos valores sincronizados (ver AUD-02-004). Iteraciones 06-06 y 07-05. | Diferido |

---

## Auditoría 02 · Revisión de código previa a la planificación

- **Fecha:** 2026-10-19
- **Auditor:** Claude (Opus 5.5), revisión asistida para el desarrollador
- **Alcance:** repositorio `ManzagraficaPedidosApp`, rama `main`, commit `2442f3b` (68 commits): modelos, vistas, formularios, utilidades, configuración, plantillas, JavaScript propio e historial de Git. No incluye producción ni el registro del servidor.

### Resumen

La revisión confirma los hallazgos de la Auditoría 01 y agrega defectos que el plan no menciona. Los más graves son de datos: borrar un cliente borra en cascada sus pedidos, ítems y pagos; eliminar un pago termina en error 500; las fechas «de hoy» y «del mes» se calculan en UTC; `estado_pago` nace desincronizado y una cotización se puede convertir dos veces. También precisa una afirmación del plan: `transaction.atomic` sí se usa en `crear_pedido`, pero la captura interna anula su efecto sobre los ítems. Ningún hallazgo registra datos personales.

### Hallazgos

| ID | Severidad | Área | Hallazgo | Acción recomendada | Estado |
| :- | :-------- | :--- | :------- | :----------------- | :----- |
| AUD-02-001 | Alta | Integridad | `Pedido.cliente` y `Cotizacion.cliente` usan `on_delete=CASCADE`: eliminar un cliente borra sus pedidos, ítems de pedido, pagos, cotizaciones e ítems de cotización. La pantalla de confirmación solo advierte que «podrías perder» el historial. | Cambiar a `PROTECT` (verificar con `sqlmigrate` que sea Clase 1), capturar `ProtectedError` en la vista como ya hace `eliminar_producto`, y prueba de regresión. Iteración 04-06. | Abierto |
| AUD-02-002 | Alta | Funcional | `eliminar_pago` renderiza `pedidos/pago_confirm_delete.html`, que no existe. Los enlaces de eliminar en el detalle del pedido y en el listado de pagos son GET, así que hoy eliminar un pago siempre termina en error 500. | Prueba de regresión (02-04); formulario POST con confirmación y plantilla correcta (04-01). | Abierto (confirmado en producción el 2026-10-20: 14 errores en el registro) |
| AUD-02-003 | Alta | Datos | «Hoy» y «inicio de mes» se calculan en UTC: `timezone.now().date()` en el panel, en trabajo semanal y en `registrar_metricas_diarias`; `timezone.now().replace(day=1, hour=0…)` en el panel y en las estadísticas. En las últimas tres o cuatro horas del día en Chile, críticos, urgentes, conteos del mes, ingresos del mes y el chequeo diario de métricas usan el día equivocado. | Pruebas con hora fijada (02-04); `timezone.localdate()` y límites con `timezone.localtime()` (06-01). | Abierto |
| AUD-02-004 | Alta | Datos | `estado_pago` se desincroniza de los pagos: `crear_pedido` con abono inicial lo deja en `PENDIENTE`; `editar_pedido` no lo recalcula si cambia `valor_venta`; `editar_pago` que cambia el pedido de un pago no recalcula el pedido anterior. Además, el formulario de edición muestra el campo de abono inicial y descarta en silencio lo que se ingrese. | Pruebas (02-02); recalcular dentro de la misma transacción en cada escritura de pago o de valor de venta (03-03). | Abierto (confirmado en producción el 2026-10-20: 610 de 870 pedidos) |
| AUD-02-005 | Alta | Integridad | `convertir_a_pedido` no verifica el estado de la cotización: un doble clic o un reenvío convierte la misma cotización en dos pedidos. Además lee la fecha y el abono desde `request.POST` sin formulario de Django: el abono no se valida contra el valor total. | Prueba de regresión (02-04); rechazar cotizaciones ya aceptadas, validar con un formulario y hacer la conversión atómica (03-03). | Abierto |
| AUD-02-006 | Media | Seguridad | `generar_respaldo_bd` ejecuta `mysqldump` y escribe en disco con un GET. Ante un fallo, devuelve al navegador el texto de la excepción, que puede incluir la salida de error de `mysqldump`. | POST con token (04-01); mensaje sin detalles técnicos y error registrado (03-04). Avance 01-09 (2026-10-26, sin desplegar): error registrado y mensaje fijo sin detalles técnicos; el GET sigue. | Abierto |
| AUD-02-007 | Baja | Datos | El gráfico anual de `estadisticas_pedidos` filtra con `fecha_solicitud__year` y agrupa con `TruncMonth` sobre un `DateTimeField`: el mismo mecanismo de conversión de zona horaria de AUD-01-006. Si producción no tiene cargadas las tablas de zona horaria de MySQL, el gráfico sale vacío. | Medir en producción (00-01); rangos de instantes y agrupación sin conversión en la base (06-01). | Abierto (no confirmado en producción el 2026-10-20; severidad bajada a Baja por el desarrollador el 2026-10-20) |
| AUD-02-008 | Baja | Documentación | Precisión a la Fase 3 del plan: `transaction.atomic` sí se usa en `crear_pedido`, pero el `try/except` dentro del bloque atómico captura el fallo de un ítem y la transacción se confirma igual. Es el ejemplo exacto del orden de anidación que la fase busca enseñar. | Usarlo como caso de estudio en 03-01. | Abierto |
| AUD-02-009 | Media | Repositorio | `requirements.txt` está codificado en UTF-16 LE con CRLF (salida de `pip freeze >` en PowerShell): GitHub lo trata como binario, los diffs no se leen y algunas herramientas no lo interpretan. | Recodificar en UTF-8 sin BOM con LF. Iteración 00-04. | Cerrado (00-04, 2026-10-21) |
| AUD-02-010 | Media | Seguridad | El commit inicial `713260c` incluye una `SECRET_KEY` con prefijo `django-insecure-` escrita en `settings.py`. Si producción usa esa misma clave, está expuesta públicamente. | Confirmar si la clave de producción es distinta sin copiarla en ningún documento (00-01); rotarla si coincide (04-03). | Abierto (mitigado en producción el 2026-10-20; la clave expuesta sigue en el historial) |
| AUD-02-011 | Media | Documentación | El README raíz afirmaba Django 5.0, Python 3.10+, «sintaxis Jinja2» y transacciones atómicas mediante `@transaccion_segura`. | README reescrito con el estado real. | Resuelto al crear la documentación (historial 2026-10-19) |
| AUD-02-012 | Baja | Administración | `Pago`, `ItemPedido`, `ItemCotizacion`, `Cotizacion` y `HistorialBD` no están registrados en el admin; `PedidoAdmin` permite editar `estado` desde el listado (`list_editable`), saltando la lógica de estados, y muestra `saldo_pendiente`, que consulta por fila. | Revisar el admin en 06-06. | Abierto |
| AUD-02-013 | Media | Negocio | El panel y el trabajo semanal excluyen solo los pedidos `TERMINADO`: un pedido `ENTREGADO` atrasado cuenta como crítico. Los pedidos sin fecha de entrega cuentan en el total de activos pero en ninguna categoría, lo que distorsiona el nivel de presión. | Confirmar la regla de negocio (`PENDIENTE_CLIENTE`) y fijarla con pruebas (02-03); corregir en 06-06. | Abierto |
| AUD-02-014 | Media | Negocio | `Cotizacion.valor_total` se describe como «precio neto propuesto» y se copia tal cual a `Pedido.valor_venta` («valor total»). Si la cotización es neta, el pedido pierde el IVA. `valor_venta` además lo calcula el navegador y el servidor no lo contrasta con la suma de los ítems. | Confirmar la regla (`PENDIENTE_CLIENTE`) y fijarla con pruebas (02-02); corregir en 03-03 o 06-05 según la respuesta. | Abierto |
| AUD-02-015 | Baja | Datos | Las cantidades de los ítems se convierten con `float()` antes de guardarse en un `DecimalField`. | Convertir con `Decimal` en la capa de servicios. Iteración 06-05. | Abierto |
| AUD-02-016 | Baja | Configuración | `TEMPLATES['DIRS']` apunta a una carpeta `templates/` que no existe y `BASE_DIR` se define dos veces. | Limpieza. Iteración 04-05. | Abierto |
| AUD-02-017 | Media | Accesibilidad | `text-primary` (`#FBBF24`) aparece 46 veces sin variante `dark:`; sobre fondos claros su contraste es 1,60:1, por debajo de cualquier umbral WCAG. | Decidir el color de texto amarillo para modo claro (`PENDIENTE_DESARROLLADOR`) y aplicarlo al compilar los estilos. Iteración 05-04. | Abierto |
| AUD-02-018 | Baja | Diseño | `index.css` declara `cursive` como respaldo de Bebas Neue. | Cambiar el respaldo a `sans-serif`. Iteración 05-04. | Abierto |
| AUD-02-019 | Media | Operación | La rotación de respaldos es por cantidad (`limpiar_backups_antiguos`, `mantener=5`, ordenada por fecha de modificación): cada restauración genera un respaldo de emergencia y cada clic repetido en «generar respaldo» crea otro volcado, y ambos desplazan copias sanas. Las cinco copias viven en el mismo disco que la base que protegen. | Rediseñar la política de rotación para que las restauraciones y los clics repetidos no desplacen copias sanas y para no depender de copias en el mismo disco (extracción local de 00-02). Iteración 06-03. | Abierto |
| AUD-02-020 | Media | Datos | Producción corre MySQL 8.0.46 con `sql_mode = NO_ENGINE_SUBSTITUTION`, sin modo estricto (`STRICT_TRANS_TABLES`): un valor demasiado largo o fuera de rango se trunca o se ajusta con una advertencia en lugar de rechazarse, y los datos pueden quedar alterados sin aviso. Medido en 00-01 (2026-10-20). | Decidir en 00-03 si la réplica local copia el modo de producción (paridad) o usa modo estricto, con la decisión escrita en la tabla de paridad; probar en 04-05 el comportamiento con modo estricto contra la réplica antes de proponer el cambio en producción. | Abierto |
| AUD-02-021 | Alta | Funcional | El registro del servidor (enero a octubre de 2026) tiene 13 errores capturados por el decorador al renderizar una plantilla: `crear_pedido` 7, `crear_cotizacion` 3 y `crear_cliente` 3. El mensaje empieza con «Template: …» y está truncado a 110 caracteres; la causa no se conoce. Son las pantallas de alta de las tres entidades principales. | Causa `PENDIENTE_DESARROLLADOR`: obtener el mensaje completo y la fecha de cada error en el registro del servidor (sin datos de clientes); reproducir en la réplica (00-03) y fijar con una prueba de regresión (02-04). | Abierto |
| AUD-02-022 | Baja | Configuración | `ALLOWED_HOSTS` en `settings.py` solo contiene `manzagrafica.pythonanywhere.com`: en local, la aplicación responde 400 en `127.0.0.1` y `localhost`, y para revisarla hay que editar `settings.py` a mano, con riesgo de commitear el cambio. Detectado en 00-03 (2026-10-21) al arrancar la réplica. | Leer `ALLOWED_HOSTS` desde el entorno con un valor por defecto local (`localhost`, `127.0.0.1`), en 00-04 por decisión del desarrollador. Definir la variable en el servidor antes de ese despliegue. | Resuelto en 00-04, desplegado en 00-05 el 2026-10-23 (`v0.1-higiene`, sitio correcto con `ALLOWED_HOSTS` definida) |
| AUD-02-023 | Media | Operación | Las imágenes que suben los usuarios (`media/pedidos/` y `media/referencias/` en el servidor; 10 archivos el 2026-10-23, después del despliegue de 00-04) no están en Git (`.gitignore` desde 00-04) ni en el respaldo de la base, que solo guarda la ruta. No tienen ninguna copia: si se pierde el disco o un `checkout` las borra, se pierden, y restaurar un respaldo (caso 3 de `retroceso.md`) deja pedidos que apuntan a archivos inexistentes. Detectado en 00-05 (2026-10-23). | Respaldo periódico de `media/` en la épica 07 (propuesta en las notas de la iteración 00-05). Mientras tanto, la protección es manual. | Abierto |
| AUD-02-024 | Media | Operación | El respaldo de emergencia que genera la restauración (`restaurar_bd`) se guarda en `backups/` del servidor, en el mismo disco de 512 MiB que la base de datos, sin enlace de descarga, y la rotación de cinco archivos (`limpiar_backups_antiguos`) puede borrarlo. Hallazgo hermano de AUD-02-019 y del `.sql` vacío anotado para la 04-04. Detectado el 2026-10-26. | Sin corrección propuesta. Iteración 04-04. | Abierto |
| AUD-02-025 | Baja | Datos | `Pedido.porcentaje_pagado` calcula `int((total_pagado / valor_venta) * 100)` con `float` y trunca: el error de representación baja un punto (un pago de $29 sobre $100 muestra 28 %, no 29 %; 9 casos en los pagos de 1 a valor − 1 sobre valores de 100, 1.000 y 10.000). Efecto: barras de progreso un punto más bajas. Detectado en 02-02 (2026-10-26), fijado en `test_dinero.SaldoPedidoTests.test_matriz_de_saldos`. | Calcular con enteros (`pagado * 100 // valor`). Regresión en 02-04 (R15). Iteración 06-05, junto con AUD-02-015 (decisión del desarrollador, 2026-10-26). | Abierto |
| AUD-02-026 | Baja | Negocio | En `estadisticas_pagos`, un pedido activo de $0 sin pagos cuenta a la vez como «pagado» (saldo 0) y como «sin abono» (pagado 0), y el remanente «parcial» baja en uno; con varios, puede quedar negativo. Producción no tiene pedidos de $0 (2026-10-20). Detectado en 02-02 (2026-10-26), fijado en `test_dinero.EstadisticasPagosOraculoTests.test_pedido_de_valor_cero_cuenta_como_pagado_y_sin_abono`. | Depende del dato `PENDIENTE_CLIENTE` «pedido de $0» (`registro-pendientes.md`, sección 2). Sin regresión en 02-04 hasta que el cliente responda. | Abierto |
| AUD-02-027 | Baja | Datos | `convertir_a_pedido` toma `fecha_entrega` de `request.POST` sin formulario ni validación; si llega vacía, el guardado del `DateField` lanza una excepción y el decorador responde 500. La plantilla marca el campo `required`, así que solo ocurre fuera del navegador (petición armada a mano o navegador sin validación HTML). Detectado por lectura en 02-03 (2026-10-26), sin prueba hasta la 02-04; registrado por decisión del desarrollador del 2026-10-27. | Validar la fecha con un formulario de Django y devolver el formulario con su error, sin 500. Regresión en 02-04 (R18), que debe confirmar que falla por la fecha vacía; si resulta `unexpected success`, la hipótesis era falsa y se retira el hallazgo. Iteración: 03-04 (contrato de error hacia el usuario; decisión del desarrollador, 2026-10-27). | Abierto |
| AUD-02-028 | Baja | Datos | `duplicar_pedido` crea el pedido nuevo con `creado_por` nulo: no copia el del original ni usa el usuario que duplica, así que el duplicado pierde la autoría. Detectado en 02-03 (2026-10-26), fijado en `test_pedidos.DuplicarPedidoTests.test_lo_que_no_se_copia`; registrado por decisión del desarrollador del 2026-10-27. Es distinto de la pregunta `PENDIENTE_CLIENTE` sobre qué se copia al duplicar (ítems y pagos), que sigue abierta. | Asignar `creado_por = request.user` al duplicar. Regresión en 02-04 (R19), que afirma que el duplicado queda con el usuario que lo duplicó. Iteración que lo corrige: `PENDIENTE_DESARROLLADOR` (candidatas 04-01 o 03-03). | Abierto |

### Mediciones de producción · 2026-10-20 (iteración 00-01)

Notas agregadas sin reescribir los hallazgos. Cifras en `linea-base-produccion.md`; análisis en `99_bitacora/epica-00-blindaje/bitacora-00-01-produccion.md`.

- **AUD-01-006 · confirmado.** `pedidos_historialbd` tiene 187 filas en 121 días distintos (UTC); máximo de 16 filas en un mismo día; 23 días con más de una fila y 66 filas sobrantes. En hora de Chile: 119 días, máximo 17, 24 días y 68 sobrantes. Además, la cobertura es del 47 % (121 de 256 días desde la primera fila), porque la métrica solo se registra cuando alguien abre la pantalla de estadísticas y no hay tarea programada.
- **AUD-02-002 · confirmado.** El registro del servidor tiene 14 errores «Error capturado por decorador en eliminar_pago» por la plantilla `pedidos/pago_confirm_delete.html` inexistente.
- **AUD-02-004 · confirmado a gran escala.** 610 de 870 pedidos (70,1 %) tienen `estado_pago` distinto del que dicen sus pagos. Casi todos quedaron en `PENDIENTE` con pagos registrados: 563 deberían estar en `PAGADO` y 47 en `PARCIAL`. No hay pedidos con valor de venta $0.
- **AUD-02-007 · no confirmado.** Las tablas de zona horaria están cargadas en producción y el gráfico anual tiene datos: 870 pedidos de 2026, 0 con conversión nula. Aclaración acordada: `fecha_solicitud__year` con un valor exacto se traduce a un rango de instantes y no convierte la zona horaria; solo `TruncMonth` convierte en la base. El riesgo queda condicionado a que la base cambie de configuración. Se propone al desarrollador bajar la severidad de Media a Baja; la acción de 06-01 se mantiene por regla técnica.
- **AUD-02-010 · mitigado en producción.** La clave de producción no empieza con `django-insecure-` y no coincide con la del commit `713260c`. La clave expuesta sigue en el historial público de Git: no debe reutilizarse en ningún entorno. La rotación de 04-03 deja de ser urgente.
- **AUD-02-019 · contexto.** Cinco volcados suman 6,19 MB (el más reciente pesa 1.438.471 bytes) frente a 180,8 MB usados de 512: la retención por cantidad no está limitada por el disco.
- **Otros errores del decorador en el registro.** `eliminar_producto` (4, `ProtectedError` por claves foráneas protegidas) y `eliminar_cotizacion` (2, plantilla `cotizacion_confirm_delete.html`): ambos defectos se corrigieron en el repositorio el 2026-02-03 (commits `73cc8e6` y `59801a4`) y producción corre `2442f3b`, posterior. Probablemente son errores anteriores a esa fecha; se confirman cuando se conozcan sus fechas. No se abre hallazgo nuevo.
- **AUD-02-007 · decisión del desarrollador (2026-10-20).** Severidad Baja. Sigue abierto por el desfase de un pedido entre julio y agosto según se agrupe el mes en UTC o en hora de Chile (julio 65 o 64, agosto 77 o 78); se corrige en 06-01.
- **AUD-02-021 · sigue abierto (2026-10-20).** La causa queda pendiente: falta el comando que entregue la fecha y el mensaje completo de cada error.

### Notas de la iteración 00-03 · 2026-10-21

Notas agregadas sin reescribir los hallazgos.

- **AUD-02-020 · decisión de paridad.** El desarrollador eligió que la réplica local copie el modo de producción: `compose.yaml` fija `--sql-mode=NO_ENGINE_SUBSTITUTION`. Usar el modo estricto solo en la base de pruebas, por conexión, se evalúa en 02-01. La prueba del modo estricto antes de proponerlo para producción sigue en 04-05. El hallazgo sigue abierto.
- **AUD-02-020 · decisión de 02-01 (2026-10-25).** El desarrollador eligió la opción A: la base de pruebas también corre sin modo estricto (`NO_ENGINE_SUBSTITUTION`), igual que producción; `test_entorno.py` lo comprueba. Las pruebas que dependan del truncado silencioso lo declaran con un comentario. La advertencia `mysql.W002` no se silencia. La evaluación del modo estricto sigue en 04-05. El hallazgo sigue abierto.
- **AUD-02-022 · nuevo.** Se agrega en la tabla de la Auditoría 02 con el correlativo siguiente. Lo detectó el desarrollador en la revisión de pantallas de la réplica.

### Notas de la iteración 00-05 · 2026-10-23

Notas agregadas sin reescribir los hallazgos.

- **AUD-02-022 · resuelto.** `ALLOWED_HOSTS` se definió en el `.env` del servidor antes de recargar, y el sitio respondió con `v0.1-higiene` (evidencia-00-05, B7 y B10).
- **AUD-02-023 · nuevo.** Se agrega en la tabla de la Auditoría 02 con el correlativo siguiente. Lo detectó el desarrollador al revisar `media/` en el despliegue de 00-04. Severidad Media, asignada por el desarrollador.
  - **Propuesta (épica 07, sin implementar).** Respaldo de `media/` con la misma cadencia que el de la base (semanal y antes de cada despliegue), acotado al disco de 512 MB. En la consola Bash se empaqueta `media/` en un `.tar.gz` fuera del proyecto, se anota su SHA-256, se descarga con la pestaña **Files** a la carpeta cifrada y **se borra del servidor** en la misma sesión. Así el servidor no guarda copias y el uso de disco solo sube durante unos minutos (hoy son unos pocos MB; antes de adoptarlo hay que medir `du -sm media`). Se documenta en `docs/operacion/respaldo.md` y se ensaya la restauración en la réplica (07-04). Más adelante se puede evaluar moverlo a la orden de mantención diaria (06-02), cuidando los 100 segundos de CPU y el límite de disco (06-03). La iteración que lo implemente la define el desarrollador.
  - **Mientras tanto, la protección es manual:** el desarrollador descarga las imágenes nuevas desde la pestaña **Files** a la carpeta cifrada cuando las haya. No hay copia automática.

### Notas de la iteración 00-06 · 2026-10-25

Notas agregadas sin reescribir los hallazgos.

- **AUD-01-020 · resuelto con seguimiento.** Del 19 al 22 de octubre, 9 de 9 peticiones de `/robots.txt` dieron 404; desde el despliegue del 2026-10-23, ninguna. La única petición posterior fue la verificación manual y dio 200. El 24 y el 25 ningún rastreador la pidió: al repetir el conteo con C2 (2026-11-20) se confirma que un rastreador real recibe 200 (evidencia-00-06, C1).
- **AUD-01-021 · resuelto.** Botón de acceso revisado en local (escritorio y 360 px) y en producción (evidencia-00-06, A8 y B3).
- **AUD-01-011 y AUD-01-024 · avanzados.** Siguen abiertos para 05-01 y 06-06.
- **`favicon.ico` · observación menor, sin número de hallazgo.** 404 en producción porque la app no define favicon. Registrado como propuesta en `registro-pendientes.md`, sección 4.

### Notas del 2026-10-26

Notas agregadas sin reescribir los hallazgos.

- **AUD-02-024 · nuevo.** Se agrega en la tabla de la Auditoría 02 con el correlativo siguiente, por decisión del desarrollador. Asignado a la 04-04; solo se registra el hallazgo, sin corrección. La severidad queda `PENDIENTE_DESARROLLADOR`. **Actualización 2026-10-26:** severidad Media, igual que AUD-02-019 (decisión del desarrollador).

### Notas de la iteración 02-02 · 2026-10-26

Notas agregadas sin reescribir los hallazgos ([bitacora-02-02](../99_bitacora/epica-02-red-seguridad/bitacora-02-02.md)).

- **AUD-02-015 · avanzado, nota sobre el IVA.** `Producto.save()` también calcula con `float`: `int(round(valor_neto * 0.19))`, que redondea las mitades al par. Frente al redondeo comercial (`Decimal`, mitad hacia arriba) difiere en $1 en 150, 350 y 4.950 de la tabla de la 02-02, y en 500 de los 100.001 valores netos entre 0 y 100.000; nunca más de $1. Por decisión del desarrollador (D1, 2026-10-26) queda solo anotado: sin hallazgo nuevo y sin regresión.
- **AUD-02-025 y AUD-02-026 · nuevos** (hallazgos H1 y H2 de la 02-02), por decisión del desarrollador del 2026-10-26. AUD-02-025 pasa a regresión en la 02-04 (R15); AUD-02-026 queda solo en la auditoría hasta que el cliente responda sobre los pedidos de $0.

### Notas de la iteración 02-03 · 2026-10-27

Notas agregadas sin reescribir los hallazgos ([bitacora-02-03](../99_bitacora/epica-02-red-seguridad/bitacora-02-03.md), [bitacora-02-03-cierre](../99_bitacora/epica-02-red-seguridad/bitacora-02-03-cierre.md)).

- **AUD-02-027 y AUD-02-028 · nuevos** (hallazgos H2 y H3 de la 02-03), por decisión del desarrollador del 2026-10-27, con regresiones R18 y R19 en la 02-04.
- **Precio del ítem enviado por el navegador (H1 de la 02-03) · no es hallazgo.** El vendedor ajusta a mano el precio de cada ítem para dar trato diferenciado a cada cliente: regla de negocio confirmada por el desarrollador el 2026-10-27. No se crea hallazgo ni se amplía AUD-02-014. Ningún cambio de las Épicas 03 a 06 valida el precio contra el catálogo sin consultar al desarrollador. Detalle en `docs/operacion/pruebas.md`, sección 9.

### Notas de la iteración 02-04 · 2026-10-27

Notas agregadas sin reescribir los hallazgos ([bitacora-02-04](../99_bitacora/epica-02-red-seguridad/bitacora-02-04.md)). Cada hallazgo apunta a su prueba en `pedidos/tests/test_regresiones.py`; la tabla completa está en `docs/operacion/pruebas.md`, sección 7.1.

- **AUD-01-002:** R1, R2 y R4 (`ItemsTodoONadaTests`). **AUD-02-008:** R3.
- **AUD-02-006:** R6a, R6b y R6c (`EscrituraPorGetTests`). **AUD-02-002:** R7.
- **AUD-02-003:** R8 (panel y chequeo diario, también en la base) y R9 (ingresos del mes).
- **AUD-02-004:** R10, R11 y R12. **AUD-02-005:** R13. **AUD-02-001:** R14. **AUD-02-025:** R15.
- **AUD-02-027:** R18, confirmada: la vista lanza `ValidationError` por la fecha vacía y responde 500. **AUD-02-028:** R19, confirmada: `creado_por` queda nulo.
- **AUD-01-006 · sin regresión.** R5 no se confirmó: en la base local, dos llamadas a `registrar_metricas_diarias()` en el mismo instante a mediodía dejan una fila. A las 22:00 de Chile sí dejan dos, por el día en UTC (AUD-02-003), que ya comprueba R8. Lo revisa la 06-01.
- **AUD-01-006 · causa más consistente (decisión del desarrollador, 2026-10-27; [bitacora-02-04-cierre](../99_bitacora/epica-02-red-seguridad/bitacora-02-04-cierre.md)).** El día de la comprobación se calcula en UTC (`timezone.now().date()`) y Django convierte `fecha_registro` a día de Chile para `__date`. En las últimas 3 o 4 horas del día de Chile (cuando en UTC ya es el día siguiente), el chequeo no encuentra la fila e inserta una por visita. Evidencia en la base de pruebas: R8 (`BordesDeHoraChileTests`) deja 2 filas el mismo día de Chile. **Hipótesis consistente, no verificada en producción.** La de tablas de zona horaria sin cargar ya estaba descartada por la medición de la 00-01 (AUD-02-007: tablas cargadas, 0 conversiones nulas, 119 días distintos en hora de Chile). R5 queda cubierta por R8, sin prueba propia.

## Auditoría 03 · Revisión de código para la reorganización de épicas

- **Fecha:** 2026-10-27
- **Auditor:** Claude (Opus 5.5), revisión asistida para el desarrollador
- **Alcance:** repositorio `ManzagraficaPedidosApp`, rama `main`, commit `ac70401`: plantillas, `pedidos/views.py`, `pedidos/utils.py` y `PedidosApp/settings.py`, enfocada en lo que pidió el desarrollador al reorganizar las épicas (inyección SQL, XSS, ataques de acceso, módulo de base de datos). No incluye producción.

### Resumen

No hay inyección SQL: la única consulta directa (`pedidos/utils.py`, `connection.cursor()`) usa parámetros y el resto pasa por el ORM. Sí hay un XSS almacenado: tres plantillas imprimen con `|safe` el HTML del editor enriquecido sin limpiarlo; hoy solo lo puede explotar un usuario de confianza, pero el módulo de usuarios (Épica 09) lo vuelve relevante. Dos defectos del módulo de base de datos que el desarrollador reportó tienen causas distintas de las que parecían: la descarga del respaldo se aborta por una recarga de la página a los 2 segundos (hipótesis a confirmar), y el gráfico de estadísticas no usa ninguna librería rota, sino que dibuja datos pobres. El acceso no limita intentos fallidos y las librerías por CDN no llevan verificación de integridad. Ningún hallazgo registra datos personales.

### Hallazgos

| ID | Severidad | Área | Hallazgo | Acción recomendada | Estado |
| :- | :-------- | :--- | :------- | :----------------- | :----- |
| AUD-03-001 | Media | Seguridad | XSS almacenado: `pedido_detail.html:115` (`detalles_pedido`), `cotizacion_detail.html:150` (`detalles`) y `producto_detail.html:53` (`descripcion`) imprimen con `\|safe` el HTML de Summernote sin sanitizar. Quien puede escribir en esos campos puede ejecutar JavaScript en la sesión de quien abre el detalle. Hoy solo escribe un superusuario; con operadores (Épica 09), un operador podría actuar en la sesión de un superusuario. La severidad se propone Media y pasa a Alta antes de la Épica 09. | Sanitizar con lista blanca de etiquetas y atributos (04-07), requisito de la Épica 09. | Abierto |
| AUD-03-002 | Media | Operación | El enlace «Generar Nuevo Respaldo BD» (`respaldar_bd.html:18-19`) ejecuta `setTimeout(function(){ location.reload(); }, 2000)` al hacer clic. La vista `generar_respaldo_bd` sí responde con `FileResponse` y `Content-Disposition: attachment`, pero si `mysqldump` tarda más de 2 segundos la recarga reemplaza la navegación pendiente y la descarga no llega al navegador; el `.sql` queda solo en `backups/` del servidor. Coincide con lo que reporta el desarrollador. Hipótesis por confirmar en la réplica. | Al convertir el enlace en formulario POST (04-01, AUD-02-006), retirar la recarga y verificar que el archivo llega al equipo del usuario. | Abierto |
| AUD-03-003 | Baja | Datos | `estadisticas_bd` dibuja un SVG calculado en el servidor (no usa librerías de JavaScript) con las últimas 6 filas de `HistorialBD`. Esas filas tienen duplicados y huecos (187 filas en 121 días, cobertura del 47 %, línea base sección 1) porque solo se registran al abrir la pantalla, y la base pesa unos 2 MB, así que el gráfico muestra una línea casi plana con fechas salteadas. El KPI de crecimiento compara con «30 registros atrás», que supone una fila por día. | Datos confiables con la orden diaria (06-01, 06-02) y rediseño de lo que muestra la pantalla (06-04). | Abierto |
| AUD-03-004 | Media | Seguridad | El acceso no limita los intentos fallidos: la 01-04 registra `acceso_fallido`, pero nada bloquea un ataque de fuerza bruta contra la contraseña. No hay configuración de límites de subida (`DATA_UPLOAD_MAX_MEMORY_SIZE`, `FILE_UPLOAD_MAX_MEMORY_SIZE`) más allá de los valores por defecto de Django, ni validación del tamaño de las imágenes de referencia. | Límite de intentos con bloqueo temporal y evento, y límites de tamaño de subida (04-08). | Abierto |
| AUD-03-005 | Baja | Seguridad | Las librerías cargadas desde jsDelivr (Select2, Summernote, SweetAlert2) no llevan atributo `integrity` (SRI): si el CDN sirviera un archivo alterado, el navegador lo ejecutaría. | Autoalojar las librerías (08-07) y activar la política de seguridad de contenido estricta (08-08). | Abierto |
