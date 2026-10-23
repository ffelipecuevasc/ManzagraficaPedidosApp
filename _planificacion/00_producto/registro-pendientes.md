# Registro de pendientes

**Fuente única de verdad del trabajo pendiente.** Si discrepa con cualquier otro documento de planificación sobre el estado del trabajo, prevalece este archivo.

- **Última actualización:** 2026-10-21
- **Iteración activa:** 00-06 · Correcciones tempranas de riesgo nulo
- **Próximo hito:** Fase 0 completa: respaldo verificado fuera del servidor, réplica local fiel y retroceso ensayado
- **Entrega comprometida:** sin fecha comprometida; el plan es una secuencia de dependencias, no un cronograma
- **Flujo de ramas vigente:** rama única `main` y etiqueta anotada antes de cada despliegue (RDA-007)

---

## 1. Estado de épicas e iteraciones

Las épicas 02 a 07 tienen sus iteraciones nombradas en su definición; el archivo detallado de cada iteración se escribe cuando su épica se acerca.

| Iteración | Nombre | Épica | Estado | Depende de | Bitácoras |
| :-------- | :----- | :---- | :----- | :--------- | :-------- |
| 00-01 | Línea base de producción | 00 | Terminada | — | [bitacora-00-01](../99_bitacora/epica-00-blindaje/bitacora-00-01.md), [bitacora-00-01-sql-local](../99_bitacora/epica-00-blindaje/bitacora-00-01-sql-local.md), [bitacora-00-01-produccion](../99_bitacora/epica-00-blindaje/bitacora-00-01-produccion.md), [bitacora-00-01-cierre](../99_bitacora/epica-00-blindaje/bitacora-00-01-cierre.md) |
| 00-02 | Protocolo de respaldo verificado | 00 | Terminada | 00-01 | [bitacora-00-02](../99_bitacora/epica-00-blindaje/bitacora-00-02.md) |
| 00-03 | Réplica local fiel | 00 | Terminada | 00-02 | [bitacora-00-03](../99_bitacora/epica-00-blindaje/bitacora-00-03.md) |
| 00-04 | Higiene del repositorio | 00 | Terminada (desplegada el 2026-10-23 como `v0.1-higiene`) | — | [bitacora-00-04](../99_bitacora/epica-00-blindaje/bitacora-00-04.md) |
| 00-05 | Protocolo de versionado, despliegue y retroceso | 00 | Terminada | 00-03, 00-04 | [bitacora-00-05](../99_bitacora/epica-00-blindaje/bitacora-00-05.md), [bitacora-00-05-ensayo](../99_bitacora/epica-00-blindaje/bitacora-00-05-ensayo.md), [bitacora-00-05-produccion](../99_bitacora/epica-00-blindaje/bitacora-00-05-produccion.md) |
| 00-06 | Correcciones tempranas de riesgo nulo | 00 | En revisión | 00-05 | [bitacora-00-06](../99_bitacora/epica-00-blindaje/bitacora-00-06.md) |
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
| Un pedido con valor de venta $0, ¿cuenta como pagado al 100 %? | — | 02-02 | Pendiente (prioridad baja: producción no tiene pedidos con valor $0, medido el 2026-10-20) |
| ¿Se permite registrar pagos que superan el saldo (sobrepago)? | — | 02-02 | Pendiente |
| Al reabrir (duplicar) un pedido, ¿se copian sus ítems? | — | 02-03 | Pendiente |
| ¿Un pedido `ENTREGADO` atrasado debe contar como crítico? ¿Cómo se tratan los pedidos sin fecha de entrega en el trabajo semanal? | AUD-02-013 | 02-03, 06-06 | Pendiente |
| Número de usuarios, sus roles y los dispositivos que usan | — | `producto.md` | Pendiente (dato medido en la réplica: 1 usuario, superusuario, en el volcado del 2026-10-20; faltan roles y dispositivos) |

## 3. Decisiones por tomar

Decisiones del desarrollador que bloquean o condicionan trabajo. Mientras falten, se usa `PENDIENTE_DESARROLLADOR`.

| Tema | RDA o hallazgo | Responsable |
| :--- | :------------- | :---------- |
| Comando o archivo compose del contenedor MySQL local (`AGENTS.md`, sección 5): `compose.yaml` creado el 2026-10-21; falta que el desarrollador edite la sección 5 de `AGENTS.md` con la propuesta de [bitacora-00-03](../99_bitacora/epica-00-blindaje/bitacora-00-03.md) | RDA-006 | Desarrollador |
| ~~Confirmar con el peso medido en 00-01 que la retención provisoria de 5 volcados en el servidor cabe en el disco~~ Resuelto el 2026-10-20: 5 volcados (6,19 MB) | AUD-01-014, AUD-02-019 | Desarrollador |
| ~~Carpeta local cifrada donde se guardan los respaldos descargados~~ Resuelto el 2026-10-20: carpeta cifrada fuera del repositorio, sin escribir su ruta; confirmada el 2026-10-21 (BitLocker, sin sincronización en la nube) | RDA-002 | Desarrollador |
| ~~Retención local de volcados~~ Resuelto el 2026-10-21: los 4 semanales más recientes y el previo a cada despliegue hasta cerrar la fase siguiente | AUD-01-014 | Desarrollador, en [evidencia-00-02](../10_epicas/epica-00-blindaje/evidencia-00-02.md) |
| ~~Responder [evidencia-00-02](../10_epicas/epica-00-blindaje/evidencia-00-02.md)~~ Resuelto el 2026-10-21 | 00-02 | Desarrollador |
| «Generar Nuevo Respaldo BD» es un enlace GET: cada visita crea un volcado y desplaza al más antiguo. Advertido en `docs/operacion/respaldo.md`; se corrige en 04-01 | AUD-02-006 | Agente, en 04-01 |
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
| ~~Ejecutar en producción los pasos de [evidencia-00-01](../10_epicas/epica-00-blindaje/evidencia-00-01.md)~~ Resuelto el 2026-10-20 | AUD-01-006, AUD-02-004, AUD-02-007, AUD-02-010 | Desarrollador |
| ~~Confirmar si la expiración de la web app del 2026-11-20 viene de una renovación hecha el día de la medición~~ Resuelto el 2026-10-20: sí, renovación del 2026-10-20 | 07-01 | Desarrollador |
| ~~Bajar la severidad de AUD-02-007 de Media a Baja~~ Resuelto el 2026-10-20: Baja, sigue abierto para 06-01 | AUD-02-007 | Desarrollador |
| Obtener el mensaje completo y la fecha de los 13 errores de plantilla de `crear_pedido`, `crear_cotizacion` y `crear_cliente`, y las fechas de los errores de `eliminar_producto` y `eliminar_cotizacion` | AUD-02-021 | Desarrollador |
| ~~Datos de la línea base que no vinieron en la evidencia~~ Resuelto el 2026-10-20 | — | Desarrollador |
| Informe de desconexiones a 28 días de 00-06 (en paralelo, sin bloquear la Épica 01) | 00-06 | Desarrollador |
| ~~Paridad del modo SQL en la réplica local~~ Resuelto el 2026-10-21: opción A, `NO_ENGINE_SUBSTITUTION` igual que producción; el modo estricto solo para la base de pruebas (opción C) se evalúa en 02-01 | AUD-02-020 | Desarrollador |
| ~~Responder [evidencia-00-03](../10_epicas/epica-00-blindaje/evidencia-00-03.md)~~ Resuelto el 2026-10-21 | 00-03 | Desarrollador |
| ~~Desplegar la 00-04 como primer uso de la lista de la 00-05 (punto 8): revisar `media/` y la referencia a la captura, confirmar `DATABASE_URL` y definir `ALLOWED_HOSTS=manzagrafica.pythonanywhere.com` en el `.env` del servidor antes de recargar. Paso a paso en [evidencia-00-05](../10_epicas/epica-00-blindaje/evidencia-00-05.md), parte B, después del ensayo (parte A)~~ Resuelto el 2026-10-23: desplegada como `v0.1-higiene` | 00-04, AUD-02-022 | Desarrollador, en 00-05 |
| ~~Formato de etiquetas de despliegue (00-05, tarea 1)~~ Resuelto el 2026-10-21: `v<fase>.<correlativo>-<propósito>`, reemplaza al del 2026-10-20 | RDA-007 | Desarrollador |
| ~~Numeración del correlativo de etiquetas~~ Resuelto el 2026-10-22: cada fase parte en `.1` (`v0.1`, `v1.1`); `v0.0-inicial` es la etiqueta del estado de partida | RDA-007 | Desarrollador |
| ~~Ventana del despliegue de 00-04 (`v0.1-higiene`), parte B de [evidencia-00-05](../10_epicas/epica-00-blindaje/evidencia-00-05.md)~~ Resuelto el 2026-10-23: recarga a las 00:26 | 00-05 | Desarrollador |
| Imágenes de `media/` sin ninguna copia: definir la iteración de la épica 07 que implementa el respaldo propuesto en `auditoria-tecnica.md` (notas de 00-05). Mientras tanto, la protección es manual | AUD-02-023 | Desarrollador |

## 4. Propuestas fuera de alcance

Ideas detectadas durante el trabajo que no forman parte del plan. Se evalúan aparte.

| Propuesta | Origen | Fecha |
| :-------- | :----- | :---- |
| Implementar la métrica «clientes nuevos» del listado de clientes, que hoy siempre muestra 0 porque la vista envía un valor fijo | Auditoría 02 | 2026-10-19 |
| Prioridad baja, para la Épica 04: la página de acceso debe redirigir al panel cuando ya hay sesión (`LoginView` con `redirect_authenticated_user=True`). Hoy, al volver con «atrás» después de entrar, aparece el formulario de acceso vacío | 00-06, parte A8 de la evidencia | 2026-10-23 |

## 5. Historial

Una fila por cambio, en una sola línea, con enlace a la bitácora que tiene el detalle. Nada se borra: si un cambio queda sin efecto, se agrega una fila que lo dice.

| Fecha | Cambio |
| :---- | :----- |
| 2026-10-19 | Creación de la documentación del proyecto a partir de `plan-de-trabajo.md` y de la Auditoría 02: 8 épicas y 46 iteraciones previstas. |
| 2026-10-20 | Iteración 00-01 en revisión: guiones de solo lectura, plantilla de línea base y pedido de evidencia listos; faltan la ejecución en producción y la del SQL en local. Detalle en [bitacora-00-01](../99_bitacora/epica-00-blindaje/bitacora-00-01.md). |
| 2026-10-20 | Resueltas por el desarrollador: RDA-012 aceptada, formato de etiquetas `fase<N>-<propósito>-AAAA-MM-DD` (RDA-007), retención de 5 volcados (provisoria, a confirmar con el peso medido en 00-01) y licencia MIT; se agrega AUD-02-019 (rotación de respaldos), asignado a 06-03. |
| 2026-10-20 | Guion SQL de 00-01 ejecutado en local sin errores (14 sentencias, solo lectura); el desarrollador aplicó la corrección de la regla 6 de `AGENTS.md`. Detalle en [bitacora-00-01-sql-local](../99_bitacora/epica-00-blindaje/bitacora-00-01-sql-local.md). |
| 2026-10-20 | Evidencia de producción de 00-01 consolidada en la línea base; confirmados AUD-01-006, AUD-02-002 y AUD-02-004, no confirmado AUD-02-007, mitigado AUD-02-010; nuevos AUD-02-020 y AUD-02-021; nota en RDA-004; `linea_base.sh` excluye `.gitkeep`. Detalle en [bitacora-00-01-produccion](../99_bitacora/epica-00-blindaje/bitacora-00-01-produccion.md). |
| 2026-10-20 | Iteración 00-01 terminada: línea base completa (`backups/`, desglose por tabla, CPU y método de conteo por fecha); AUD-02-007 baja a Baja; criterio de 00-06 y término de la épica 00 ajustados; nota de retención en la épica 06; iteración activa 00-02. Detalle en [bitacora-00-01-cierre](../99_bitacora/epica-00-blindaje/bitacora-00-01-cierre.md). |
| 2026-10-20 | Iteración 00-02 en revisión: `verificar_respaldo.py` (pruebas sintéticas 0, 1 y 1), `docs/operacion/respaldo.md` y pedido de evidencia; retención de 5 en el servidor; expiración del 2026-11-20 confirmada. Detalle en [bitacora-00-02](../99_bitacora/epica-00-blindaje/bitacora-00-02.md). |
| 2026-10-21 | Iteración 00-02 terminada: respaldo real verificado (código 0, 18 de 18 tablas), carpeta cifrada con BitLocker, 5 volcados en el servidor, retención local confirmada y nota en la épica 00; iteración activa 00-03. Detalle en [bitacora-00-02](../99_bitacora/epica-00-blindaje/bitacora-00-02.md). |
| 2026-10-21 | Iteración 00-03 en revisión: `compose.yaml` (MySQL 8.0.46, volumen `mysql_data` externo, `sql_mode` de producción), `paridad_replica.py`, `docs/operacion/replica-local.md` y pedido de evidencia. Detalle en [bitacora-00-03](../99_bitacora/epica-00-blindaje/bitacora-00-03.md). |
| 2026-10-21 | Iteración 00-03 terminada: restauración en 4,17 s, paridad sin diferencias no aceptadas, migraciones 0001 a 0006, `check` limpio, conteos explicados y pantallas coherentes; nuevo AUD-02-022 y 00-04 ampliada; iteración activa 00-04. Detalle en [bitacora-00-03](../99_bitacora/epica-00-blindaje/bitacora-00-03.md). |
| 2026-10-21 | Iteración 00-04 en revisión: `.gitignore`, `.gitattributes`, `.env.example`, `requirements.txt` en UTF-8 con LF y `settings.py` con `ALLOWED_HOSTS` y `DB_*` desde el entorno; sin desplegar. Detalle en [bitacora-00-04](../99_bitacora/epica-00-blindaje/bitacora-00-04.md). |
| 2026-10-21 | Iteración 00-04 terminada sin desplegar: índice sin `.idea/` ni la captura de `media/` (commit `965227d`), réplica con `check` limpio y `ALLOWED_HOSTS` con 200, 200 y 400; se cierran AUD-01-023 y AUD-02-009; **el despliegue de la 00-04 queda pendiente de la 00-05**, cuya lista suma el punto 8; iteración activa 00-05. Detalle en [bitacora-00-04](../99_bitacora/epica-00-blindaje/bitacora-00-04.md). |
| 2026-10-21 | Formato de etiquetas cambia a `v<fase>.<correlativo>-<propósito>` (decisión del desarrollador); queda sin efecto el `fase<N>-<propósito>-AAAA-MM-DD` del 2026-10-20. Detalle en [bitacora-00-05](../99_bitacora/epica-00-blindaje/bitacora-00-05.md). |
| 2026-10-21 | Iteración 00-05 en revisión: `docs/operacion/despliegue.md`, `docs/operacion/retroceso.md` y pedido de evidencia con el ensayo en la réplica (parte A) y el despliegue de 00-04 como `v0.1-higiene` (parte B). Detalle en [bitacora-00-05](../99_bitacora/epica-00-blindaje/bitacora-00-05.md). |
| 2026-10-22 | Ensayo de retroceso aprobado en la réplica (caso 2, 1,31 min, migraciones iguales antes y después); numeración desde `.1` con `v0.0-inicial` como estado de partida; `v0.0-inicial` pasa a crearse antes de tocar el servidor; 00-05 sigue en revisión hasta el despliegue. Detalle en [bitacora-00-05-ensayo](../99_bitacora/epica-00-blindaje/bitacora-00-05-ensayo.md). |
| 2026-10-23 | Iteración 00-05 terminada: 00-04 desplegada como `v0.1-higiene` (recarga a las 00:26, sin retroceso; partida `v0.0-inicial`); el servidor queda en `detached HEAD` y los próximos despliegues usan `git fetch origin --tags` y `git checkout <etiqueta>`, no `git pull`; AUD-02-022 resuelto; nuevo AUD-02-023 (Media, `media/` sin copia, protección manual); pistas para la épica 01; iteración activa 00-06. Detalle en [bitacora-00-05-produccion](../99_bitacora/epica-00-blindaje/bitacora-00-05-produccion.md). |
| 2026-10-23 | Iteración 00-06 en revisión: WeasyPrint se importa dentro de la vista del PDF, `robots.txt` es público, el botón de acceso evita el doble envío y la ruta queda `pagos/lista/`; 5 pruebas; medición «antes» con media de 1.029 ms; falta la verificación local, el despliegue como `v0.2-correcciones` y el conteo de 404 de `/robots.txt` ([evidencia-00-06](../10_epicas/epica-00-blindaje/evidencia-00-06.md)). Detalle en [bitacora-00-06](../99_bitacora/epica-00-blindaje/bitacora-00-06.md). |
