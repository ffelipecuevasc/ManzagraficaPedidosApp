# Épica 06 · Arquitectura y automatización

- **Estado:** Pendiente
- **Fase del plan:** 6 (`plan-de-trabajo.md`, «FASE 6»)
- **Objetivo:** corregir los desajustes estructurales y automatizar el mantenimiento dentro de las restricciones de la plataforma.
- **Precondición:** Épicas 01, 02 y 03 completas.

## Alcance

1. **Fechas locales y registro diario de métricas**: el plan corrige el chequeo diario de `HistorialBD` con un rango de instantes. Se amplía a todas las fechas «de hoy» y «del mes» calculadas en UTC (AUD-02-003) y al gráfico anual de estadísticas (AUD-02-007). Si 00-01 confirmó filas duplicadas, la limpieza conserva exactamente una fila representativa por día, con respaldo previo y ensayo en la réplica.
2. **Orden de mantención diaria** (RDA-009): métricas, purga de registros (absorbe `purgar_registros` de 01-01) y respaldo, con manejo de error independiente por paso, registro de su propia ejecución y consumo de CPU medido. Se retira la invocación desde el panel y desde las estadísticas de la base.
3. **Gestión del disco**: retención de registros, rotación de volcados en el código según lo decidido en 00-02, umbral de espacio libre con evento y crecimiento de `media/referencias/`.
4. **Modularización de las vistas** por dominio, como refactorización pura en un despliegue dedicado, sin cambiar nombres de rutas.
5. **Capa de servicios**, empezando por la conversión de cotización a pedido. Incluye convertir cantidades con `Decimal` (AUD-02-015) y, según la respuesta del cliente, la regla de neto o total en la conversión (AUD-02-014).
6. **Deuda menor**: paginación de clientes, sincronía de `estado_pago`, nomenclatura de rutas, captura de rutas numéricas en la raíz, criterio de idioma del código, el admin de los modelos de negocio (AUD-02-012) y la regla de pedidos entregados y sin fecha en el panel y en el trabajo semanal (AUD-02-013).

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 06-01 | Fechas locales y registro diario de métricas | 6.1 |
| 06-02 | Orden de mantención diaria | 6.2 |
| 06-03 | Gestión del disco | 6.3 |
| 06-04 | Modularización de las vistas | 6.4 |
| 06-05 | Capa de servicios | 6.5 |
| 06-06 | Deuda técnica menor | 6.6 |

## Decisiones de la épica

- La limpieza de filas duplicadas de `HistorialBD` es una operación destructiva sobre datos, no un cambio de esquema: se ejecuta con una orden de gestión revisada, respaldo descargado y ensayo previo en la réplica.
- Unificar `estado_pago` exige Clase 3: queda como deuda diferida (07-05).

## Criterio de término

- La tarea diaria se ejecuta sola durante siete días seguidos y cada ejecución deja su evento.
- Ninguna vista de lectura escribe en la base (prueba con conteo de escrituras).
- Las pruebas de regresión de fechas en UTC y de métricas duplicadas pasan de fallo esperado a verde.
- El uso de disco tiene un umbral vigilado por la orden de mantención.
