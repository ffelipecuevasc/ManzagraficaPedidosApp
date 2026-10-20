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
| AUD-01-002 | Alta | Integridad | Supresión silenciosa de excepciones (`except Exception: pass`) al guardar ítems; la edición de pedidos borra los ítems antes de recrearlos. | Propagar o capturar de forma específica y registrar. Iteración 03-02. | Abierto |
| AUD-01-003 | Alta | Seguridad | El cambio de estado y la duplicación de pedidos modifican datos con GET (CSRF, prelectura del navegador, rastreadores). | Convertir a POST con token y formularios en las plantillas. Iteración 04-01. | Abierto |
| AUD-01-004 | Alta | Observabilidad | `ErrorHandlingMiddleware` captura toda excepción, descarta la traza y desconecta el manejo de errores de Django. | Retirar el middleware y usar los manejadores 404/500 ya declarados. Iteración 01-03. | Abierto |
| AUD-01-005 | Alta | Observabilidad | Ausencia total de registro de errores y de eventos. | Tablas propias de errores y eventos con respaldo a salida estándar. Iteraciones 01-01 a 01-06. | Abierto |
| AUD-01-006 | Alta | Datos | El registro diario de métricas podría insertar una fila en cada visita al panel (`fecha_registro__date` con zona horaria). | Medir en producción (00-01) y corregir con rango de instantes (06-01). | Abierto |
| AUD-01-007 | Alta | Arquitectura | Escritura de mantenimiento (métricas) dentro del ciclo de petición de dos vistas de lectura. | Orden de gestión de mantención diaria. Iteración 06-02. | Abierto |
| AUD-01-008 | Alta | Rendimiento | Propiedades del modelo que consultan la base por fila en plantillas (`total_pagado_real`, `saldo_pendiente`, `porcentaje_pagado`). | Anotaciones del conjunto de consulta. Iteración 05-02. | Abierto |
| AUD-01-009 | Alta | Configuración | `from PedidosApp import settings` en lugar de `django.conf.settings`. | Usar el objeto de configuración perezoso. Iteración 04-05. | Abierto |
| AUD-01-010 | Alta | Rendimiento | Compilador de Tailwind cargado desde CDN y ejecutado en el navegador en cada página. | Compilación local con pnpm. Iteración 05-04. | Abierto |
| AUD-01-011 | Alta | Rendimiento | WeasyPrint se importa al arrancar el proceso, aunque solo lo usa una vista. | Importación diferida (00-06) y revisión del resto de importaciones (05-01). | Abierto |
| AUD-01-012 | Media | Seguridad | Configuración de producción sin endurecer (cookies seguras, HTTPS, HSTS, orígenes CSRF de confianza). | Resolver `check --deploy` con criterio. Iteración 04-02. | Abierto |
| AUD-01-013 | Media | Seguridad | La contraseña de la base viaja como argumento de `mysqldump` y `mysql`, visible en la tabla de procesos del servidor compartido. | Pasarla por variable de entorno del subproceso o archivo de opciones con permisos restringidos. Iteración 04-03. | Abierto |
| AUD-01-014 | Media | Operación | Los respaldos viven en el mismo disco que la base que protegen; se retienen cinco volcados completos. | Extracción y verificación local; retención de dos o tres en servidor. Iteraciones 00-02 y 06-03. | Abierto |
| AUD-01-015 | Media | Calidad | Cero pruebas automatizadas en una aplicación que maneja dinero. | Red de pruebas sobre lógica de dinero, flujos críticos y regresiones. Iteraciones 02-01 a 02-05. | Abierto |
| AUD-01-016 | Media | Configuración | Conexiones reutilizadas 60 segundos sin verificación de salud; fallos intermitentes tras hibernación. | `CONN_HEALTH_CHECKS`. Iteración 04-05. | Abierto |
| AUD-01-017 | Media | Rendimiento | El listado de clientes no tiene paginación. | Paginación. Iteración 06-06. | Abierto |
| AUD-01-018 | Media | Seguridad | El módulo de restauración ejecuta un SQL arbitrario sin validar el archivo. | Validación de extensión, tamaño y estructura; confirmación explícita; registro del evento. Iteración 04-04. | Abierto |
| AUD-01-019 | Media | Operación | La web app del plan gratuito expira sin aviso si la cuenta no registra actividad. | Recordatorio externo y procedimiento de renovación. Iteración 07-01. | Abierto |
| AUD-01-020 | Baja | Operación | Rastreadores sin ruta para `robots.txt` generan 404 con renderizado completo. | Publicar `robots.txt`. Iteración 00-06. | Abierto |
| AUD-01-021 | Baja | Interfaz | Doble envío del formulario de acceso. | Deshabilitar el botón tras el primer envío. Iteración 00-06. | Abierto |
| AUD-01-022 | Baja | Arquitectura | Todas las vistas en un único archivo de más de 1.500 líneas. | Dividir por dominio como refactorización pura. Iteración 06-04. | Abierto |
| AUD-01-023 | Baja | Repositorio | Configuración del IDE (`.idea/`) versionada. | Excluirla del repositorio. Iteración 00-04. | Abierto |
| AUD-01-024 | Baja | Arquitectura | Nomenclatura de rutas inconsistente entre secciones (incluida `pagos/lista` sin barra final). | Barra final en 00-06; normalización en 06-06. | Abierto |
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
| AUD-02-002 | Alta | Funcional | `eliminar_pago` renderiza `pedidos/pago_confirm_delete.html`, que no existe. Los enlaces de eliminar en el detalle del pedido y en el listado de pagos son GET, así que hoy eliminar un pago siempre termina en error 500. | Prueba de regresión (02-04); formulario POST con confirmación y plantilla correcta (04-01). | Abierto |
| AUD-02-003 | Alta | Datos | «Hoy» y «inicio de mes» se calculan en UTC: `timezone.now().date()` en el panel, en trabajo semanal y en `registrar_metricas_diarias`; `timezone.now().replace(day=1, hour=0…)` en el panel y en las estadísticas. En las últimas tres o cuatro horas del día en Chile, críticos, urgentes, conteos del mes, ingresos del mes y el chequeo diario de métricas usan el día equivocado. | Pruebas con hora fijada (02-04); `timezone.localdate()` y límites con `timezone.localtime()` (06-01). | Abierto |
| AUD-02-004 | Alta | Datos | `estado_pago` se desincroniza de los pagos: `crear_pedido` con abono inicial lo deja en `PENDIENTE`; `editar_pedido` no lo recalcula si cambia `valor_venta`; `editar_pago` que cambia el pedido de un pago no recalcula el pedido anterior. Además, el formulario de edición muestra el campo de abono inicial y descarta en silencio lo que se ingrese. | Pruebas (02-02); recalcular dentro de la misma transacción en cada escritura de pago o de valor de venta (03-03). | Abierto |
| AUD-02-005 | Alta | Integridad | `convertir_a_pedido` no verifica el estado de la cotización: un doble clic o un reenvío convierte la misma cotización en dos pedidos. Además lee la fecha y el abono desde `request.POST` sin formulario de Django: el abono no se valida contra el valor total. | Prueba de regresión (02-04); rechazar cotizaciones ya aceptadas, validar con un formulario y hacer la conversión atómica (03-03). | Abierto |
| AUD-02-006 | Media | Seguridad | `generar_respaldo_bd` ejecuta `mysqldump` y escribe en disco con un GET. Ante un fallo, devuelve al navegador el texto de la excepción, que puede incluir la salida de error de `mysqldump`. | POST con token (04-01); mensaje sin detalles técnicos y error registrado (03-04). | Abierto |
| AUD-02-007 | Media | Datos | El gráfico anual de `estadisticas_pedidos` filtra con `fecha_solicitud__year` y agrupa con `TruncMonth` sobre un `DateTimeField`: el mismo mecanismo de conversión de zona horaria de AUD-01-006. Si producción no tiene cargadas las tablas de zona horaria de MySQL, el gráfico sale vacío. | Medir en producción (00-01); rangos de instantes y agrupación sin conversión en la base (06-01). | Abierto |
| AUD-02-008 | Baja | Documentación | Precisión a la Fase 3 del plan: `transaction.atomic` sí se usa en `crear_pedido`, pero el `try/except` dentro del bloque atómico captura el fallo de un ítem y la transacción se confirma igual. Es el ejemplo exacto del orden de anidación que la fase busca enseñar. | Usarlo como caso de estudio en 03-01. | Abierto |
| AUD-02-009 | Media | Repositorio | `requirements.txt` está codificado en UTF-16 LE con CRLF (salida de `pip freeze >` en PowerShell): GitHub lo trata como binario, los diffs no se leen y algunas herramientas no lo interpretan. | Recodificar en UTF-8 sin BOM con LF. Iteración 00-04. | Abierto |
| AUD-02-010 | Media | Seguridad | El commit inicial `713260c` incluye una `SECRET_KEY` con prefijo `django-insecure-` escrita en `settings.py`. Si producción usa esa misma clave, está expuesta públicamente. | Confirmar si la clave de producción es distinta sin copiarla en ningún documento (00-01); rotarla si coincide (04-03). | Abierto |
| AUD-02-011 | Media | Documentación | El README raíz afirmaba Django 5.0, Python 3.10+, «sintaxis Jinja2» y transacciones atómicas mediante `@transaccion_segura`. | README reescrito con el estado real. | Resuelto al crear la documentación (historial 2026-10-19) |
| AUD-02-012 | Baja | Administración | `Pago`, `ItemPedido`, `ItemCotizacion`, `Cotizacion` y `HistorialBD` no están registrados en el admin; `PedidoAdmin` permite editar `estado` desde el listado (`list_editable`), saltando la lógica de estados, y muestra `saldo_pendiente`, que consulta por fila. | Revisar el admin en 06-06. | Abierto |
| AUD-02-013 | Media | Negocio | El panel y el trabajo semanal excluyen solo los pedidos `TERMINADO`: un pedido `ENTREGADO` atrasado cuenta como crítico. Los pedidos sin fecha de entrega cuentan en el total de activos pero en ninguna categoría, lo que distorsiona el nivel de presión. | Confirmar la regla de negocio (`PENDIENTE_CLIENTE`) y fijarla con pruebas (02-03); corregir en 06-06. | Abierto |
| AUD-02-014 | Media | Negocio | `Cotizacion.valor_total` se describe como «precio neto propuesto» y se copia tal cual a `Pedido.valor_venta` («valor total»). Si la cotización es neta, el pedido pierde el IVA. `valor_venta` además lo calcula el navegador y el servidor no lo contrasta con la suma de los ítems. | Confirmar la regla (`PENDIENTE_CLIENTE`) y fijarla con pruebas (02-02); corregir en 03-03 o 06-05 según la respuesta. | Abierto |
| AUD-02-015 | Baja | Datos | Las cantidades de los ítems se convierten con `float()` antes de guardarse en un `DecimalField`. | Convertir con `Decimal` en la capa de servicios. Iteración 06-05. | Abierto |
| AUD-02-016 | Baja | Configuración | `TEMPLATES['DIRS']` apunta a una carpeta `templates/` que no existe y `BASE_DIR` se define dos veces. | Limpieza. Iteración 04-05. | Abierto |
| AUD-02-017 | Media | Accesibilidad | `text-primary` (`#FBBF24`) aparece 46 veces sin variante `dark:`; sobre fondos claros su contraste es 1,60:1, por debajo de cualquier umbral WCAG. | Decidir el color de texto amarillo para modo claro (`PENDIENTE_DESARROLLADOR`) y aplicarlo al compilar los estilos. Iteración 05-04. | Abierto |
| AUD-02-018 | Baja | Diseño | `index.css` declara `cursive` como respaldo de Bebas Neue. | Cambiar el respaldo a `sans-serif`. Iteración 05-04. | Abierto |
