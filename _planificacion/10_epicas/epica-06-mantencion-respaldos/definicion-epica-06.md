# Épica 06 · Mantención automatizada y respaldos

- **Estado:** Pendiente
- **Fase del plan:** 6, subfases 6.1 a 6.3 (`plan-de-trabajo.md`, «FASE 6»), separada el 2026-10-27 (anexo del plan, RDA-014). Las subfases 6.4 a 6.6 pasaron a la Épica 07.
- **Objetivo:** que el mantenimiento ocurra solo, una vez al día y fuera del ciclo de las peticiones, que la base se respalde automáticamente los días 1 y 15 de cada mes, y que el módulo de base de datos de la web muestre información útil y entregue los respaldos al usuario.
- **Precondición:** Épicas 01, 02 y 03 completas. Se ejecuta después de la Épica 05.
- **Última revisión:** 2026-10-27 (separación de la antigua Épica 06; respaldo programado y rediseño del módulo de base de datos agregados).

## Alcance

1. **Fechas locales y registro diario de métricas (06-01):** el plan corrige el chequeo diario de `HistorialBD` con un rango de instantes. Se amplía a todas las fechas «de hoy» y «del mes» calculadas en UTC (AUD-02-003) y al gráfico anual de estadísticas (AUD-02-007). 00-01 confirmó filas duplicadas (187 filas en 121 días): la limpieza conserva exactamente una fila representativa por día, con respaldo previo y ensayo en la réplica.
2. **Orden de mantención diaria y tarea programada (06-02)** (RDA-009): una orden de gestión `mantencion_diaria` con pasos independientes, cada uno con su propio manejo de error:
   - métricas del día;
   - purga de registros (absorbe `purgar_registros` de 01-01);
   - **respaldo de la base solo los días 1 y 15 de cada mes**, calculados en hora de Chile (decisión del desarrollador del 2026-10-27);
   - registro de su propia ejecución en la tabla de eventos (inicio, resultado de cada paso y fin) y consumo de CPU medido contra los 100 segundos diarios.

   Se retira la invocación desde el panel y desde las estadísticas de la base. La tarea se crea en la pestaña **Tasks** de PythonAnywhere: la cuenta conserva **una tarea diaria** porque es anterior al 2026-01-15, con la hora en UTC, y **la tarea gratuita se detiene cada cuatro semanas si no se renueva** desde el correo de aviso (la renovación es rutina de la 13-01). El desarrollador crea y renueva la tarea; el agente prepara el comando exacto en un archivo de evidencia.
3. **Gestión del disco (06-03):** retención de registros, rotación de volcados **por antigüedad** y no por cantidad, que nunca borre un respaldo del día 1 o del 15 reciente (AUD-02-019), umbral de espacio libre con evento y crecimiento de `media/referencias/`. La rotación que hoy borra respaldos es código propio (`limpiar_backups_antiguos` en `pedidos/utils.py`, conserva cinco), no una política de PythonAnywhere.
4. **Rediseño del módulo de base de datos (06-04):** con los datos confiables que deja la orden diaria, la pantalla de estadísticas muestra lo que sirve para decidir (AUD-03-003): uso del disco frente a los 512 MiB, antigüedad del último respaldo con alerta si supera los 16 días, filas por tabla de negocio y crecimiento mensual. La pantalla de respaldos lista cada `.sql` del servidor con su enlace de descarga (complementa AUD-02-024) e indica cuáles generó la tarea programada. El gráfico sigue siendo SVG calculado en el servidor, sin librerías nuevas; si la Épica 08 adopta una librería de gráficos, se migra allí.

## Iteraciones

| Iteración | Nombre | Origen |
| :-------- | :----- | :----- |
| 06-01 | Fechas locales y registro diario de métricas | 6.1 |
| 06-02 | Orden de mantención diaria y tarea programada | 6.2, con el respaldo de los días 1 y 15 |
| 06-03 | Gestión del disco | 6.3 |
| 06-04 | Rediseño del módulo de base de datos | Nueva (reorganización 2026-10-27, AUD-03-003) |

## Decisiones de la épica

- La limpieza de filas duplicadas de `HistorialBD` es una operación destructiva sobre datos, no un cambio de esquema: se ejecuta con una orden de gestión revisada, respaldo descargado y ensayo previo en la réplica.
- **Retención de volcados (para 06-03, medido en 00-01 el 2026-10-20):** cinco volcados suman 6,19 MB, menos del 1,5 % de la cuota de 512 MiB, y el más reciente pesa 1.438.471 bytes. La política conviene que retenga más copias y rote por antigüedad (por ejemplo, los de los días 1 y 15 de los últimos meses), no por cantidad (AUD-02-019).
- **2026-10-27 · Respaldo programado los días 1 y 15 (decisión del desarrollador).** La plataforma solo permite una tarea diaria; la orden corre todos los días y respalda solo esos dos días. El respaldo programado **no reemplaza** la descarga local del protocolo de 00-02 (antes de cada despliegue y semanal): sigue en el mismo disco del servidor hasta que exista el respaldo externo de la Épica 14.
- Hora de la tarea en UTC (se propone madrugada de Chile, fuera del horario de uso): `PENDIENTE_DESARROLLADOR`, se decide en 06-02.
- ¿La orden de mantención avisa si no se ejecutó varios días seguidos? `PENDIENTE_DESARROLLADOR` (registro, sección 3). La Épica 11 puede convertir ese aviso en un correo.

## Fuera de alcance

- Modularización de vistas, capa de servicios y deuda menor: Épica 07.
- Respaldo fuera del servidor (S3): Épica 14.
- Corregir la descarga del respaldo desde la web: la resuelve la 04-01 al pasar el enlace a formulario (AUD-03-002).

## Criterio de término

- La tarea diaria se ejecuta sola durante siete días seguidos y cada ejecución deja su evento.
- Un respaldo generado por la tarea un día 1 o 15 existe en el servidor, se verifica con `scripts/verificar_respaldo.py` y queda su evento.
- Ninguna vista de lectura escribe en la base (prueba con conteo de escrituras).
- Las regresiones de fechas en UTC de la 02-04 pasan de fallo esperado a verde con la 06-01: R8 (el panel y el chequeo diario de métricas usan el día de Chile; incluye que una visita a las 22:00 de Chile no escriba una segunda fila de `HistorialBD` el mismo día) y R9 (los ingresos del mes usan el mes de Chile). La regresión prevista de métricas duplicadas (R5) no se confirmó: el duplicado real lo cubre R8 (corregido el 2026-10-27).
- El uso de disco tiene un umbral vigilado por la orden de mantención.
- La pantalla de estadísticas de la base muestra el uso de disco, la antigüedad del último respaldo y las filas por tabla con datos de la orden diaria.

## Notas

- **2026-10-27 (reorganización, RDA-014):** la antigua «Épica 06 · Arquitectura y automatización» se separa en dos. Esta conserva el número y las subfases 6.1 a 6.3 (sus iteraciones conservan los números 06-01 a 06-03). La modularización, la capa de servicios y la deuda menor pasan a la Épica 07 (antes 06-04, 06-05 y 06-06). La carpeta cambia de `epica-06-arquitectura-automatizacion` a `epica-06-mantencion-respaldos`.
- **2026-10-27 · Unificar `estado_pago`** exige Clase 3: sigue como deuda diferida, ahora en la 13-05 (antes 07-05).
