# Registro de Decisiones Arquitectónicas (RDA)

Consolidado de las decisiones técnicas del proyecto. Formato y reglas en `_planificacion/README.md` (secciones 5.2 y 6.4).

Las RDA-002 a RDA-010 registran las nueve decisiones D1 a D9 que el plan de trabajo tomó antes de redactarse (`plan-de-trabajo.md`, sección 1.2). Se fechan el día en que se registraron aquí.

| RDA | Título | Estado |
| :-- | :----- | :----- |
| RDA-001 | Monolito Django con MySQL como arquitectura base | Aceptada |
| RDA-002 | Réplica local con volcado real de producción como entorno de pruebas (D1) | Aceptada |
| RDA-003 | Cambios de esquema autorizados: solo Clase 1 y Clase 2 (D2) | Aceptada |
| RDA-004 | PythonAnywhere en plan gratuito, con tarea diaria heredada (D3) | Aceptada |
| RDA-005 | Observabilidad local en tablas propias de MySQL con respaldo a salida estándar (D4) | Reemplazada en parte por RDA-013 |
| RDA-006 | Pruebas automatizadas contra MySQL en Docker idéntico a producción (D5) | Aceptada |
| RDA-007 | Rama única `main` con etiqueta anotada antes de cada despliegue (D6) | Aceptada |
| RDA-008 | Registro de eventos limitado a errores y eventos de negocio críticos (D7) | Aceptada |
| RDA-009 | Una sola orden de gestión de mantención diaria (D8) | Aceptada |
| RDA-010 | Tailwind CSS v3 compilado localmente con pnpm (D9) | Aceptada |
| RDA-011 | Épicas numeradas igual que las fases del plan | Reemplazada por RDA-014 |
| RDA-012 | Procedimientos operativos en `docs/operacion/` | Aceptada |
| RDA-013 | Errores en el registro del servidor con `logging`; eventos de negocio en MySQL | Aceptada |
| RDA-014 | Épicas numeradas según su orden de ejecución, de 00 a 14 | Aceptada |
| RDA-015 | Vistas delgadas con servicios y selectores; sin patrón repositorio sobre el ORM | Aceptada |
| RDA-016 | Interfaz renderizada en el servidor con plantillas de Django; sin migración a React | Aceptada |
| RDA-017 | Dos roles sobre la tabla nativa de usuarios y borrado físico con doble confirmación | Aceptada |
| RDA-018 | Proyección de pedidos con la biblioteca estándar de Python; sin aprendizaje automático | Aceptada |

---

## RDA-001 · Monolito Django con MySQL como arquitectura base

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** la aplicación ya está en producción como un monolito Django 6.0.1 sobre Python 3.13 y MySQL 8.0, con una sola aplicación (`pedidos`) y datos reales. El plan de trabajo es de mejora, no de reescritura.
**Decisión:** se mantiene el monolito con el patrón Modelo-Vista-Plantilla, plantillas renderizadas en el servidor, autenticación nativa de Django y MySQL 8.0. La reorganización interna (vistas por dominio, capa de servicios) ocurre dentro de la misma aplicación.
**Alternativas consideradas:** separar una API y un frontend independiente (descartado: duplica el despliegue en un plan con un solo worker y no resuelve ningún hallazgo); cambiar a PostgreSQL (descartado: migrar datos reales es un riesgo sin beneficio para los hallazgos actuales).
**Consecuencias:** el código depende de particularidades de MySQL (zonas horarias, `information_schema`, `mysqldump`), por lo que las pruebas deben correr contra MySQL (RDA-006).

## RDA-002 · Réplica local con volcado real de producción como entorno de pruebas (D1)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** varios defectos solo se manifiestan con historia acumulada (métricas duplicadas, saldos, estados financieros). Unos datos de prueba sintéticos no los reproducen.
**Decisión:** el entorno local se alimenta con un volcado real de producción restaurado en el MySQL local, y todo cambio de esquema se ensaya primero contra esa réplica.
**Alternativas consideradas:** datos sintéticos (descartado por baja fidelidad); entorno de preproducción en el servidor (descartado: el plan gratuito no lo permite y comparte el mismo disco).
**Consecuencias:** la máquina del desarrollador guarda datos personales de clientes reales: exige disco cifrado, ningún volcado en el repositorio ni en carpetas sincronizadas sin cifrar, y que los agentes no lean los volcados.

**Actualización 2026-10-21:** el cifrado obligatorio se cumple en D: (BitLocker al 100 %), donde están el repositorio, la carpeta de respaldos y el disco de Docker Desktop con la réplica (iteración 00-03). C: queda sin cifrar por decisión informada del desarrollador. El riesgo residual son restos de respaldos antiguos en C:; el desarrollador revisó y no encontró ninguno.

## RDA-003 · Cambios de esquema autorizados: solo Clase 1 y Clase 2 (D2)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** cada migración sobre datos reales es un riesgo; algunas mejoras (unificar `estado_pago`) exigirían cambios destructivos.
**Decisión:** se autorizan cambios de Clase 1 (metadatos, sin alteración de tabla) y de Clase 2 (aditivos: índices, tablas nuevas, columnas que admiten nulo), con respaldo previo. La Clase 3 (renombrar, eliminar, cambiar tipo, imponer obligatoriedad) está prohibida. La clase se determina mirando el SQL de `sqlmigrate`, no la intención del cambio.
**Alternativas consideradas:** permitir Clase 3 con respaldo (descartado: el riesgo de pérdida no se justifica con el beneficio).
**Consecuencias:** la doble fuente de verdad de `estado_pago` queda como deuda conocida y diferida; mientras tanto, se mantiene sincronizada.

## RDA-004 · PythonAnywhere en plan gratuito, con tarea diaria heredada (D3)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** la aplicación ya está publicada en el plan gratuito.
**Decisión:** se mantiene el plan gratuito y se diseña todo dentro de sus límites: 512 MiB de disco compartido, un worker de un núcleo, una tarea programada diaria, 100 segundos de CPU diarios para consolas y tareas, salida a lista blanca, hibernación y expiración por inactividad.
**Alternativas consideradas:** plan de pago (diferido; la sección 7.6 del plan define las señales que justificarían evaluarlo).
**Consecuencias:** sin servicios externos de monitoreo, sin entorno de preproducción y con arranque en frío inevitable.

**Actualización 2026-10-20:** medido en 00-01, la tarea programada diaria del plan está disponible, pero la cuenta no tiene ninguna creada (el formulario para crearla está habilitado). La orden de mantención de RDA-009 tendrá que crearla. Detalle en `99_bitacora/epica-00-blindaje/bitacora-00-01-produccion.md`.

## RDA-005 · Observabilidad local en tablas propias de MySQL con respaldo a salida estándar (D4)

- **Fecha:** 2026-10-19
- **Estado:** Reemplazada en parte por RDA-013

**Contexto:** hoy un error no deja rastro útil y la lista blanca de salida descarta Sentry y equivalentes.
**Decisión:** dos tablas propias, una de errores y otra de eventos, consultables desde el admin. Si la escritura en la base falla, el error se emite a la salida estándar, que PythonAnywhere recoge en su registro del servidor.
**Alternativas consideradas:** servicios externos (descartados por la lista blanca); solo archivos de registro (descartado: no se consultan sin acceso al servidor).
**Consecuencias:** las tablas compiten por el disco y necesitan retención y purga desde su diseño; la escritura del error debe quedar fuera de la transacción que falló.

**Actualización 2026-10-25:** reemplazada en parte por RDA-013. Se descarta la tabla de errores: los errores se registran con `logging` y se diagnostican en `server.log` (corregido el 2026-10-25 en la 01-06; ver RDA-013). Sigue vigente la tabla de eventos de negocio, con retención y purga desde su diseño, consultable en el admin.

## RDA-006 · Pruebas automatizadas contra MySQL en Docker idéntico a producción (D5)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** el código depende de particularidades de MySQL; SQLite no reproduce las conversiones de zona horaria ni las agregaciones tal como ocurren en producción.
**Decisión:** las pruebas corren contra un MySQL 8.0 en Docker, con la misma versión, conjunto de caracteres, colación y configuración de zona horaria que producción.
**Alternativas consideradas:** SQLite en memoria (descartado: más rápido pero engañoso).
**Consecuencias:** las pruebas son más lentas y requieren el contenedor encendido; el usuario de la base local necesita permiso para crear la base de pruebas.

## RDA-007 · Rama única `main` con etiqueta anotada antes de cada despliegue (D6)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** desarrollador individual; el riesgo principal no es la colaboración sino no poder volver atrás tras un despliegue.
**Decisión:** se trabaja en `main`. Antes de cada despliegue, el desarrollador crea una etiqueta anotada con el formato definido en `docs/operacion/despliegue.md`. Los agentes no crean ramas salvo pedido explícito y nunca hacen commits, etiquetas ni despliegues.
**Alternativas consideradas:** una rama por iteración con merge a `main` (descartado como flujo por defecto: agrega pasos sin aportar retroceso adicional para una sola persona).
**Consecuencias:** `main` puede contener trabajo aún no desplegado; la etiqueta, no la punta de `main`, marca lo que está en producción. Un despliegue lleva un solo propósito.

## RDA-008 · Registro de eventos limitado a errores y eventos de negocio críticos (D7)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** con un worker, cada escritura suma latencia; con 512 MiB, cada fila suma disco.
**Decisión:** se registran errores y un inventario cerrado de eventos de negocio (pedidos, pagos, estados, conversiones, eliminaciones, accesos, respaldos y restauraciones). Nunca peticiones de lectura ordinarias ni el contenido completo de los objetos.
**Alternativas consideradas:** registro de todas las peticiones (descartado por costo de latencia y disco).
**Consecuencias:** el inventario de eventos se define en 01-04 y cambiarlo requiere estimar de nuevo el crecimiento.

## RDA-009 · Una sola orden de gestión de mantención diaria (D8)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** la plataforma concede una sola tarea programada diaria y 100 segundos de CPU.
**Decisión:** una orden de gestión de Django orquesta tres pasos independientes (métricas, purga de registros y respaldo), cada uno con su propio manejo de errores, y registra su propia ejecución en la tabla de eventos.
**Alternativas consideradas:** tres tareas separadas (imposible en el plan); mantener las métricas dentro de las vistas (descartado: escritura impredecible en el ciclo de petición).
**Consecuencias:** hay que medir el consumo de CPU de la orden y vigilar los días en que no se ejecuta.

**Actualización 2026-10-27 (decisión del desarrollador, reorganización RDA-014):** el paso de respaldo se ejecuta solo los días 1 y 15 de cada mes, en hora de Chile; métricas y purga siguen siendo diarias. Las automatizaciones de la Épica 11 se suman como un paso más, con su propio manejo de errores. Verificado en el panel (PDF de la pestaña **Tasks** del 2026-10-27) y en la ayuda de PythonAnywhere: la cuenta conserva una tarea diaria por ser anterior al 2026-01-15, y la tarea gratuita se detiene cada cuatro semanas si no se renueva (rutina de la 13-01). La orden se implementa en la 06-02.

## RDA-010 · Tailwind CSS v3 compilado localmente con pnpm (D9)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** el compilador de Tailwind se descarga desde CDN y se ejecuta en el navegador en cada carga de página (unos 400 KB de JavaScript), y la configuración del tema está duplicada en `base.html` y `login.html`.
**Decisión:** Tailwind CSS v3 se compila en local con pnpm, con versiones exactas y archivo de bloqueo versionado; el CSS compilado se versiona y se sirve como estático.
**Alternativas consideradas:** seguir con el CDN (descartado); npm (descartado: pnpm verifica la integridad por paquete y reduce la superficie ante ataques de cadena de suministro); Tailwind v4 (no elegido en el plan).
**Consecuencias:** compilar antes de desplegar pasa a ser un paso obligatorio de la lista de comprobación; si se olvida, los estilos nuevos no llegan a producción.

**Actualización 2026-10-27 (reorganización RDA-014):** la implementación pasa de la 05-04 a la 08-05 (Épica 08, frontend). Node.js y pnpm se usan solo en la máquina del desarrollador; PythonAnywhere sirve el CSS compilado y no necesita Node.

## RDA-011 · Épicas numeradas igual que las fases del plan

- **Fecha:** 2026-10-19
- **Estado:** Reemplazada por RDA-014

**Contexto:** el plan de trabajo numera sus fases de 0 a 7 y sus subfases como 0.1, 0.2…
**Decisión:** la Épica `NN` es la Fase `N` y la iteración `NN-MM` es la subfase `N.M` (la iteración `00-03` es la subfase 0.3). Las iteraciones que no existían en el plan toman el siguiente correlativo libre de su épica.
**Alternativas consideradas:** numerar las épicas desde 01 (descartado: obliga a traducir cada número entre el plan y la planificación).
**Consecuencias:** existe una Épica 00, y los commits de la primera fase se escriben como `Épica 0 - Iteración 00-NN: …`.

**Reemplazada por RDA-014 (2026-10-27):** la reorganización agrega épicas que no existen en el plan y separa fases; desde la Épica 05 el número de iteración ya no coincide siempre con la subfase.

## RDA-012 · Procedimientos operativos en `docs/operacion/`

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** la Fase 0 produce procedimientos que se usan en cada despliegue (respaldo verificado, réplica local, despliegue, retroceso) y que la Fase 7 consolida como documentos vivos del repositorio. No son planificación ni bitácoras: son instrucciones de operación.
**Decisión:** viven en `docs/operacion/`, un archivo por procedimiento: `respaldo.md`, `replica-local.md`, `despliegue.md` y `retroceso.md`. Los agentes pueden editarlos; cada cambio queda descrito en la bitácora de la iteración que lo hizo.
**Alternativas consideradas:** dentro de `_planificacion/` (descartado: mezcla instrucciones permanentes con el registro del trabajo); en el README raíz (descartado: el README no lleva comandos).
**Consecuencias:** `AGENTS.md` y el README raíz remiten a esa carpeta.

**Actualización 2026-10-20:** aceptada por el desarrollador.

## RDA-013 · Errores en el registro del servidor con `logging`; eventos de negocio en MySQL

- **Fecha:** 2026-10-25
- **Estado:** Aceptada

**Contexto:** RDA-005 preveía dos tablas propias, una de errores y otra de eventos. Al detallar la Épica 01 se vio que la tabla de errores obliga a resolver dos trampas caras (escribir el error fuera de la transacción que falló y registrar en MySQL un fallo del propio MySQL) para un público que no la necesita: quien diagnostica errores es el desarrollador, no el usuario final. Los eventos de negocio («quién hizo qué y cuándo») sí son información del negocio y deben respaldarse con la base.
**Decisión:** los errores se emiten con `logging` de Python a la salida de error, que PythonAnywhere guarda en `server.log` (actualización del 2026-10-25, abajo), con traza completa, método, ruta, usuario y hora (The Twelve-Factor App, factor XI: la aplicación emite sus registros como flujo y el entorno los guarda). Los eventos de negocio se guardan en una tabla propia de MySQL (Clase 2), con índices, retención y purga desde su creación, y se consultan en el admin de Django. No hay código de error visible para el usuario ni identificador de petición.
**Alternativas consideradas:** tabla de errores en MySQL (descartada por YAGNI: el usuario final no diagnostica errores, y exige escritura fuera de la transacción y un camino de respaldo propio); servicios externos de monitoreo como Sentry (descartados: la lista blanca de salida de PythonAnywhere lo impide, RDA-004).
**Consecuencias:** los errores dependen de la rotación de registros de PythonAnywhere y se pierden si nadie los mira a tiempo; su revisión periódica es la iteración 07-03. Diagnosticar un error exige entrar al panel de PythonAnywhere. La tabla de eventos sigue compitiendo por el disco (estimación en 01-01) y su inventario lo cierra RDA-008. Desaparecen el aislamiento transaccional y la dependencia circular del registro de errores.

**Actualización 2026-10-25 (01-06, medido en producción):** la salida de error del proceso web termina en **`server.log`**, en hora de Chile, con la traza en la misma línea y los saltos escritos como `#012`. Ahí queda la línea completa con emoji y `clave=valor`. `error.log`, en UTC, recibe los mismos errores en el formato de PythonAnywhere (`fecha,ms: mensaje` y la traza debajo), sin método, ruta ni usuario. Decisión del desarrollador (opción A): **el diagnóstico se hace en `server.log`** y `error.log` se deja como lo escribe PythonAnywhere, sin cambiar código ni configuración. Que `error.log` lo alimente un manejador propio de PythonAnywhere en el registrador raíz es una deducción no confirmada ([bitacora-01-06-produccion](../99_bitacora/epica-01-observabilidad/bitacora-01-06-produccion.md)).

**Actualización 2026-10-26 (01-07 reabierta, decisión del desarrollador):** cambian los emojis del nivel, sin cambiar los campos: 🔴 ERROR, 🟡 WARNING, 🔵 INFO, 🔴🔴 CRITICAL, 🟢 DEBUG; un nivel personalizado sigue sin emoji. Viaja en `v1.2`. Para filtrar se busca `nivel=ERROR`, no el emoji, porque «🔴🔴 nivel=CRITICAL» contiene «🔴 nivel=».

## RDA-014 · Épicas numeradas según su orden de ejecución, de 00 a 14

- **Fecha:** 2026-10-27
- **Estado:** Aceptada
- **Reemplaza a:** RDA-011

**Contexto:** el desarrollador pidió, durante la Épica 02, sumar al plan trabajo que no existía en él: reorganizar el frontend, un módulo de usuarios con roles, mejoras del tablero «Trabajo Semanal», automatizaciones por correo, una proyección de pedidos y servicios de AWS. Además separó la antigua Fase 6 en dos (mantención y arquitectura) y sacó de la Fase 5 los estilos y recursos del navegador. Con eso, la regla «la Épica `NN` es la Fase `N`» de RDA-011 deja de ser posible.
**Decisión:** las épicas se numeran según su **orden de ejecución**, de 00 a 14, y el número de cada épica coincide con su lugar en la secuencia. El origen en el plan queda escrito en la cabecera de cada definición («Fase del plan») y en el anexo de `plan-de-trabajo.md`. Las iteraciones nuevas toman el correlativo libre de su épica; los números que quedan sin uso no se reasignan, para que ninguna referencia antigua apunte a otra cosa. Las referencias a la numeración anterior en documentos escritos antes de esta fecha (bitácoras, iteraciones cerradas, evidencias, Auditorías 01 y 02, documentos de la Épica 02 y `docs/operacion/`) no se reescriben: se leen con la tabla de equivalencias de abajo.

| Antes | Ahora | Contenido |
| :---- | :---- | :-------- |
| Épicas 00 a 04 | Épicas 00 a 04 | Sin cambio de número (la 03 ajusta su contrato de error; la 04 suma 04-07 a 04-09) |
| 05-01, 05-02, 05-03 | 05-01, 05-02, 05-03 | Sin cambio |
| 05-04 | 08-05 | Compilación local de Tailwind |
| 05-05 | 08-06 y 08-07 | Tipografías e íconos; librerías JavaScript |
| 05-06 | 05-00 y 05-06 (servidor); 08-01 y 08-09 (navegador) | Medición inicial y final |
| 06-01, 06-02, 06-03 | 06-01, 06-02, 06-03 | Sin cambio (la 06-02 suma la tarea programada y el respaldo de los días 1 y 15) |
| — | 06-04 | Rediseño del módulo de base de datos (nueva) |
| 06-04 | 07-01 | Modularización de las vistas |
| 06-05 | 07-02 | Capa de servicios (y selectores) |
| — | 07-03 | Modelos por dominio (nueva) |
| 06-06 | 07-04 | Deuda técnica menor |
| — | Épicas 08 a 12 | Frontend; usuarios y roles; mejoras del negocio; automatizaciones; proyección de pedidos (nuevas) |
| 07-01 a 07-06 (Épica 07) | 13-01 a 13-06 (Épica 13) | Operación continua |
| — | Épica 14 | Tecnología en la nube (AWS) (nueva) |

**Alternativas consideradas:** mantener RDA-011 y agregar las épicas nuevas como 08 en adelante con la operación continua en 07 (descartada por el desarrollador: la operación continua debe ir al final y el número debe decir el orden); renumerar también los documentos cerrados (descartado: las bitácoras no se editan y la tabla basta).
**Consecuencias:** el commit sigue el formato `Épica N - Iteración NN-NN: …` con el número nuevo. Un número de iteración desde la Épica 05 en adelante ya no se traduce directo a una subfase del plan: la tabla de iteraciones de cada definición dice su origen. Quien lea un documento anterior al 2026-10-27 debe usar la tabla.

## RDA-015 · Vistas delgadas con servicios y selectores; sin patrón repositorio sobre el ORM

- **Fecha:** 2026-10-27
- **Estado:** Aceptada (aprobada por el desarrollador junto con la reorganización del 2026-10-27)

**Contexto:** `pedidos/views.py` tiene 1.624 líneas con la lógica de negocio dentro de las vistas. El desarrollador pidió aplicar SOLID y evaluar los patrones repository y service, controladores por dominio y DTOs para los modelos.
**Decisión:** (1) vistas por dominio en `pedidos/views/`, que hacen de controlador y delegan; (2) `services` por dominio para los casos de uso que escriben, donde viven las transacciones; (3) `selectors` por dominio para las lecturas reutilizables; (4) modelos por dominio en `pedidos/models/`; (5) `dataclasses` solo para resultados compuestos de un servicio. Se implementa en la Épica 07.
**Alternativas consideradas:** patrón repositorio sobre el ORM (descartado: el `QuerySet` ya es un repositorio componible y perezoso, y envolverlo agrega código de paso y quita capacidades); DTOs como copia de cada modelo (descartado: duplican los campos sin aportar validación, que ya hacen los formularios de Django); dejar todo en las vistas (descartado: la lógica de negocio solo se prueba vía HTTP).
**Consecuencias:** la lógica de negocio se prueba directamente; cada iteración de la Épica 07 es una refactorización pura con su propio despliegue. Las funciones nuevas (Épicas 09 a 12) nacen en esta estructura.

## RDA-016 · Interfaz renderizada en el servidor con plantillas de Django; sin migración a React

- **Fecha:** 2026-10-27
- **Estado:** Aceptada (aprobada por el desarrollador junto con la reorganización del 2026-10-27)

**Contexto:** el desarrollador consultó si convenía migrar funciones del frontend a librerías de React para ganar fluidez y profesionalismo. La aplicación es un monolito Django que renderiza HTML con DTL, en un plan con un solo proceso y 512 MiB de disco, y la Épica 08 busca quitar JavaScript del navegador.
**Decisión:** la interfaz sigue renderizada en el servidor con DTL, parciales y estáticos propios. La fluidez se busca con librerías livianas que se evalúan en la 08-07, cada una con consulta y RDA propia (candidatas: HTMX para actualizar partes de una página, Alpine.js para interacciones pequeñas y Chart.js para gráficos).
**Alternativas consideradas:** aplicación de una sola página en React (descartada: exige una API, duplicar autenticación y CSRF, un segundo proyecto con su propia compilación y más JavaScript en el navegador; además no reemplaza la generación de PDF, que ocurre en el servidor con WeasyPrint).
**Consecuencias:** no se agrega Django REST Framework ni un proyecto de frontend separado. Si en el futuro apareciera un cliente distinto del navegador (por ejemplo, una aplicación móvil), se evalúa con una RDA nueva.

## RDA-017 · Dos roles sobre la tabla nativa de usuarios y borrado físico con doble confirmación

- **Fecha:** 2026-10-27
- **Estado:** Aceptada (decisión del desarrollador)

**Contexto:** hoy existe un solo usuario, superusuario. El dueño necesita crear cuentas para su equipo con un rol que pueda hacer todo el trabajo diario, salvo el módulo de base de datos y la gestión de usuarios.
**Decisión:** dos roles sobre `auth_user`: **superusuario** (`is_superuser=True`, `is_staff=True`) y **operador** (activo, `is_superuser=False`, `is_staff=False`), sin grupos ni permisos por modelo. Un usuario se elimina con **borrado físico** (no se desactiva), detrás de una página de confirmación con las consecuencias y una segunda confirmación que exige escribir el nombre de usuario. La vista impide borrarse a sí mismo y dejar el sistema sin superusuario. Se implementa en la Épica 09.
**Alternativas consideradas:** `Group` de Django «Operador» (descartado por el desarrollador: con dos roles basta el indicador); desactivar en vez de borrar (descartado por el desarrollador).
**Consecuencias:** al borrar un usuario, `Pedido.creado_por`, `Pago.registrado_por` y `RegistroEvento.usuario` quedan en nulo (`SET_NULL`) y la autoría solo sobrevive en el resumen de los eventos; si se quiere conservarla en todos, hace falta una columna de Clase 2 (pendiente en la 09-03). Un tercer rol obligaría a revisar esta RDA. La sanitización del HTML (04-07) es requisito previo, porque un operador no debe poder inyectar código que se ejecute en la sesión de un superusuario.

## RDA-018 · Proyección de pedidos con la biblioteca estándar de Python; sin aprendizaje automático

- **Fecha:** 2026-10-27
- **Estado:** Aceptada (decisión del desarrollador)

**Contexto:** el negocio quiere ver cuántos pedidos vienen en los próximos meses. La historia disponible son diez meses de 2026 (línea base, sección 5), y el disco es de 512 MiB.
**Decisión:** la proyección se calcula con la biblioteca estándar de Python 3.13 (`statistics`, `datetime`, `calendar`): carga comprometida real, ritmo del mes en curso, promedio móvil, tendencia lineal (`statistics.linear_regression`) y un margen, validados contra los meses pasados. No se usa aprendizaje automático, ni en el servidor ni en la nube. Se implementa en la Épica 12.
**Alternativas consideradas:** modelo supervisado con scikit-learn (descartado: diez puntos no permiten aprender estacionalidad ni generalizar, y numpy, scipy y scikit-learn ocupan una parte importante del disco); servicios de aprendizaje automático de AWS (descartados: costo y complejidad desproporcionados para el volumen).
**Consecuencias:** sin dependencias nuevas; la pantalla debe decir con cuántos meses de historia se calcula la estimación.
