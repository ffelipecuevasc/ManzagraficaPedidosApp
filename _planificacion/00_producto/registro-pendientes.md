# Registro de pendientes

**Fuente única de verdad del trabajo pendiente.** Si discrepa con cualquier otro documento de planificación sobre el estado del trabajo, prevalece este archivo.

- **Última actualización:** 2026-10-20
- **Iteración activa:** 00-01 · Línea base de producción (En revisión, a la espera de la evidencia de producción)
- **Próximo hito:** Fase 0 completa: respaldo verificado fuera del servidor, réplica local fiel y retroceso ensayado
- **Entrega comprometida:** sin fecha comprometida; el plan es una secuencia de dependencias, no un cronograma
- **Flujo de ramas vigente:** rama única `main` y etiqueta anotada antes de cada despliegue (RDA-007)

---

## 1. Estado de épicas e iteraciones

Las épicas 02 a 07 tienen sus iteraciones nombradas en su definición; el archivo detallado de cada iteración se escribe cuando su épica se acerca.

| Iteración | Nombre | Épica | Estado | Depende de | Bitácoras |
| :-------- | :----- | :---- | :----- | :--------- | :-------- |
| 00-01 | Línea base de producción | 00 | En revisión | — | [bitacora-00-01](../99_bitacora/epica-00-blindaje/bitacora-00-01.md) |
| 00-02 | Protocolo de respaldo verificado | 00 | Pendiente | 00-01 | — |
| 00-03 | Réplica local fiel | 00 | Pendiente | 00-02 | — |
| 00-04 | Higiene del repositorio | 00 | Pendiente | — | — |
| 00-05 | Protocolo de versionado, despliegue y retroceso | 00 | Pendiente | 00-03, 00-04 | — |
| 00-06 | Correcciones tempranas de riesgo nulo | 00 | Pendiente | 00-05 | — |
| 01-01 | Modelo de registro de errores y eventos | 01 | Pendiente | Épica 00 | — |
| 01-02 | Servicio de registro | 01 | Pendiente | 01-01, 02-01 | — |
| 01-03 | Retiro del middleware de captura global | 01 | Pendiente | 01-02 | — |
| 01-04 | Instrumentación de eventos de negocio | 01 | Pendiente | 01-02 | — |
| 01-05 | Consulta de registros en el admin | 01 | Pendiente | 01-01 | — |
| 01-06 | Despliegue y validación de la observabilidad | 01 | Pendiente | 01-03, 01-04, 01-05 | — |
| 02-01 | Infraestructura de pruebas | 02 | Pendiente | Épica 00 | — |
| 02-02 | Pruebas de la lógica de dinero | 02 | Pendiente | 02-01 | — |
| 02-03 | Pruebas de flujos críticos | 02 | Pendiente | 02-01 | — |
| 02-04 | Pruebas de regresión de defectos conocidos | 02 | Pendiente | 02-01 | — |
| 02-05 | Pruebas de control de acceso | 02 | Pendiente | 02-01 | — |
| 03-01 | Rediseño del decorador transaccional | 03 | Pendiente | Épicas 01 y 02 | — |
| 03-02 | Erradicación de la supresión silenciosa | 03 | Pendiente | 03-01 | — |
| 03-03 | Fronteras transaccionales por vista | 03 | Pendiente | 03-02 | — |
| 03-04 | Contrato de error hacia el usuario | 03 | Pendiente | 03-03 | — |
| 03-05 | Validación y despliegue de la integridad | 03 | Pendiente | 03-04 | — |
| 04-01 | Mutaciones solo por POST | 04 | Pendiente | Épica 02 | — |
| 04-02 | Configuración de producción | 04 | Pendiente | Épica 02 | — |
| 04-03 | Credenciales y secretos | 04 | Pendiente | Épica 02 | — |
| 04-04 | Endurecimiento de la restauración | 04 | Pendiente | Épica 02, 01-04 | — |
| 04-05 | Correcciones de configuración | 04 | Pendiente | Épica 02 | — |
| 04-06 | Protección del historial ante borrados en cascada | 04 | Pendiente | Épica 02 | — |
| 05-01 | Reducción del arranque en frío | 05 | Pendiente | Épica 02, medición inicial de 05-06 | — |
| 05-02 | Consultas por fila en plantillas | 05 | Pendiente | Épica 02, medición inicial de 05-06 | — |
| 05-03 | Índices de base de datos | 05 | Pendiente | 05-02 | — |
| 05-04 | Compilación local de estilos | 05 | Pendiente | Épica 02, medición inicial de 05-06 | — |
| 05-05 | Consolidación de recursos externos | 05 | Pendiente | 05-04 | — |
| 05-06 | Medición de rendimiento | 05 | Pendiente | Épica 02 | — |
| 06-01 | Fechas locales y registro diario de métricas | 06 | Pendiente | Épicas 01, 02 y 03 | — |
| 06-02 | Orden de mantención diaria | 06 | Pendiente | 06-01 | — |
| 06-03 | Gestión del disco | 06 | Pendiente | 06-02 | — |
| 06-04 | Modularización de las vistas | 06 | Pendiente | Épicas 01, 02 y 03 | — |
| 06-05 | Capa de servicios | 06 | Pendiente | 06-04 | — |
| 06-06 | Deuda técnica menor | 06 | Pendiente | 06-04 | — |
| 07-01 | Vigilancia de la expiración de la web app | 07 | Pendiente | 00-01 | — |
| 07-02 | Ritual de despliegue consolidado | 07 | Pendiente | Épica 06 | — |
| 07-03 | Revisión periódica de registros | 07 | Pendiente | Épica 01 | — |
| 07-04 | Ensayo de recuperación ante desastres | 07 | Pendiente | 00-05 | — |
| 07-05 | Deuda diferida y evolución | 07 | Pendiente | Épica 06 | — |
| 07-06 | Criterios para evaluar el cambio de plan | 07 | Pendiente | 00-01 | — |

## 2. Datos pendientes del cliente

Reglas de negocio que solo puede confirmar Manza Gráfica. Mientras falten, se usa `PENDIENTE_CLIENTE` y las pruebas fijan el comportamiento actual marcándolo como provisorio.

| Dato | Hallazgo | Necesario para | Estado |
| :--- | :------- | :------------- | :----- |
| ¿El valor de una cotización es neto o incluye IVA? ¿El valor de venta del pedido debe ser igual a la suma de sus ítems? | AUD-02-014 | 02-02, 03-03 | Pendiente |
| Un pedido con valor de venta $0, ¿cuenta como pagado al 100 %? | — | 02-02 | Pendiente |
| ¿Se permite registrar pagos que superan el saldo (sobrepago)? | — | 02-02 | Pendiente |
| Al reabrir (duplicar) un pedido, ¿se copian sus ítems? | — | 02-03 | Pendiente |
| ¿Un pedido `ENTREGADO` atrasado debe contar como crítico? ¿Cómo se tratan los pedidos sin fecha de entrega en el trabajo semanal? | AUD-02-013 | 02-03, 06-06 | Pendiente |
| Número de usuarios, sus roles y los dispositivos que usan | — | `producto.md` | Pendiente |

## 3. Decisiones por tomar

Decisiones del desarrollador que bloquean o condicionan trabajo. Mientras falten, se usa `PENDIENTE_DESARROLLADOR`.

| Tema | RDA o hallazgo | Responsable |
| :--- | :------------- | :---------- |
| Comando o archivo compose del contenedor MySQL local (`AGENTS.md`, sección 5) | RDA-006 | Desarrollador |
| Retención de volcados en el servidor: dos o tres | AUD-01-014 | Desarrollador |
| Carpeta local cifrada donde se guardan los respaldos descargados | RDA-002 | Desarrollador |
| Formato de las etiquetas de despliegue | RDA-007 | Desarrollador |
| Aceptar RDA-012 (procedimientos en `docs/operacion/`) | RDA-012 | Desarrollador |
| Licencia del repositorio (`README.md`, sección 8) | — | Desarrollador |
| Fechas de los hitos (`producto.md`, sección 7) | — | Desarrollador |
| Retención de las tablas de errores y de eventos | RDA-005 | Desarrollador |
| Método para provocar el error controlado en producción (01-06) | AUD-01-005 | Desarrollador |
| Dividir el decorador en dos o mantenerlo unificado con el orden correcto | AUD-01-001 | Desarrollador |
| Tratamiento de las imágenes de referencia huérfanas cuando una transacción se revierte | AUD-01-001 | Desarrollador |
| ¿La orden de mantención avisa si no se ejecutó varios días seguidos? | RDA-009 | Desarrollador |
| Criterio único de nomenclatura del código (castellano o inglés) | AUD-01-024 | Desarrollador |
| `DESIGN.md`: concepto visual, escala tipográfica, contenedor, retícula, radios por componente, sombras, estilo de foco, colores por estado, formatos y tamaño de imágenes, movimiento no permitido y comportamiento con movimiento reducido | — | Desarrollador |
| `DESIGN.md`: color del texto amarillo en modo claro | AUD-02-017 | Desarrollador |
| `DESIGN.md`: origen de tipografías e íconos (autoalojados o servicio externo) | AUD-01-010 | Desarrollador |
| Ejecutar en producción los pasos de [evidencia-00-01](../10_epicas/epica-00-blindaje/evidencia-00-01.md) y responder el archivo; incluye las rutas del proyecto y del entorno virtual en PythonAnywhere (`PENDIENTE_DESARROLLADOR`) | AUD-01-006, AUD-02-004, AUD-02-007, AUD-02-010 | Desarrollador |
| Encender el MySQL local y autorizar la ejecución de `scripts/diagnostico/linea_base.sql` (criterio 2 de 00-01, hoy «sin ejecutar») | 00-01 | Desarrollador |
| Ajustar el texto de `AGENTS.md` (sección 8, regla 6) sobre `__year`: propuesta entregada en el resumen de 00-01 | AUD-02-007 | Desarrollador |

## 4. Propuestas fuera de alcance

Ideas detectadas durante el trabajo que no forman parte del plan. Se evalúan aparte.

| Propuesta | Origen | Fecha |
| :-------- | :----- | :---- |
| Implementar la métrica «clientes nuevos» del listado de clientes, que hoy siempre muestra 0 porque la vista envía un valor fijo | Auditoría 02 | 2026-10-19 |

## 5. Historial

Una fila por cambio, en una sola línea, con enlace a la bitácora que tiene el detalle. Nada se borra: si un cambio queda sin efecto, se agrega una fila que lo dice.

| Fecha | Cambio |
| :---- | :----- |
| 2026-10-19 | Creación de la documentación del proyecto a partir de `plan-de-trabajo.md` y de la Auditoría 02: 8 épicas y 46 iteraciones previstas. |
| 2026-10-20 | Iteración 00-01 en revisión: guiones de solo lectura, plantilla de línea base y pedido de evidencia listos; faltan la ejecución en producción y la del SQL en local. Detalle en [bitacora-00-01](../99_bitacora/epica-00-blindaje/bitacora-00-01.md). |
