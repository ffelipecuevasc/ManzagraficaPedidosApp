# Registro de Decisiones Arquitectónicas (RDA)

Consolidado de las decisiones técnicas del proyecto. Formato y reglas en `_planificacion/README.md` (secciones 5.2 y 6.4).

Las RDA-002 a RDA-010 registran las nueve decisiones D1 a D9 que el plan de trabajo tomó antes de redactarse (`plan-de-trabajo.md`, sección 1.2). Se fechan el día en que se registraron aquí.

| RDA | Título | Estado |
| :-- | :----- | :----- |
| RDA-001 | Monolito Django con MySQL como arquitectura base | Aceptada |
| RDA-002 | Réplica local con volcado real de producción como entorno de pruebas (D1) | Aceptada |
| RDA-003 | Cambios de esquema autorizados: solo Clase 1 y Clase 2 (D2) | Aceptada |
| RDA-004 | PythonAnywhere en plan gratuito, con tarea diaria heredada (D3) | Aceptada |
| RDA-005 | Observabilidad local en tablas propias de MySQL con respaldo a salida estándar (D4) | Aceptada |
| RDA-006 | Pruebas automatizadas contra MySQL en Docker idéntico a producción (D5) | Aceptada |
| RDA-007 | Rama única `main` con etiqueta anotada antes de cada despliegue (D6) | Aceptada |
| RDA-008 | Registro de eventos limitado a errores y eventos de negocio críticos (D7) | Aceptada |
| RDA-009 | Una sola orden de gestión de mantención diaria (D8) | Aceptada |
| RDA-010 | Tailwind CSS v3 compilado localmente con pnpm (D9) | Aceptada |
| RDA-011 | Épicas numeradas igual que las fases del plan | Aceptada |
| RDA-012 | Procedimientos operativos en `docs/operacion/` | Aceptada |

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

## RDA-005 · Observabilidad local en tablas propias de MySQL con respaldo a salida estándar (D4)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** hoy un error no deja rastro útil y la lista blanca de salida descarta Sentry y equivalentes.
**Decisión:** dos tablas propias, una de errores y otra de eventos, consultables desde el admin. Si la escritura en la base falla, el error se emite a la salida estándar, que PythonAnywhere recoge en su registro del servidor.
**Alternativas consideradas:** servicios externos (descartados por la lista blanca); solo archivos de registro (descartado: no se consultan sin acceso al servidor).
**Consecuencias:** las tablas compiten por el disco y necesitan retención y purga desde su diseño; la escritura del error debe quedar fuera de la transacción que falló.

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

## RDA-010 · Tailwind CSS v3 compilado localmente con pnpm (D9)

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** el compilador de Tailwind se descarga desde CDN y se ejecuta en el navegador en cada carga de página (unos 400 KB de JavaScript), y la configuración del tema está duplicada en `base.html` y `login.html`.
**Decisión:** Tailwind CSS v3 se compila en local con pnpm, con versiones exactas y archivo de bloqueo versionado; el CSS compilado se versiona y se sirve como estático.
**Alternativas consideradas:** seguir con el CDN (descartado); npm (descartado: pnpm verifica la integridad por paquete y reduce la superficie ante ataques de cadena de suministro); Tailwind v4 (no elegido en el plan).
**Consecuencias:** compilar antes de desplegar pasa a ser un paso obligatorio de la lista de comprobación; si se olvida, los estilos nuevos no llegan a producción.

## RDA-011 · Épicas numeradas igual que las fases del plan

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** el plan de trabajo numera sus fases de 0 a 7 y sus subfases como 0.1, 0.2…
**Decisión:** la Épica `NN` es la Fase `N` y la iteración `NN-MM` es la subfase `N.M` (la iteración `00-03` es la subfase 0.3). Las iteraciones que no existían en el plan toman el siguiente correlativo libre de su épica.
**Alternativas consideradas:** numerar las épicas desde 01 (descartado: obliga a traducir cada número entre el plan y la planificación).
**Consecuencias:** existe una Épica 00, y los commits de la primera fase se escriben como `Épica 0 - Iteración 00-NN: …`.

## RDA-012 · Procedimientos operativos en `docs/operacion/`

- **Fecha:** 2026-10-19
- **Estado:** Aceptada

**Contexto:** la Fase 0 produce procedimientos que se usan en cada despliegue (respaldo verificado, réplica local, despliegue, retroceso) y que la Fase 7 consolida como documentos vivos del repositorio. No son planificación ni bitácoras: son instrucciones de operación.
**Decisión:** viven en `docs/operacion/`, un archivo por procedimiento: `respaldo.md`, `replica-local.md`, `despliegue.md` y `retroceso.md`. Los agentes pueden editarlos; cada cambio queda descrito en la bitácora de la iteración que lo hizo.
**Alternativas consideradas:** dentro de `_planificacion/` (descartado: mezcla instrucciones permanentes con el registro del trabajo); en el README raíz (descartado: el README no lleva comandos).
**Consecuencias:** `AGENTS.md` y el README raíz remiten a esa carpeta.

**Actualización 2026-10-20:** aceptada por el desarrollador.
