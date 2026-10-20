# Épica 05 · Rendimiento

- **Estado:** Pendiente
- **Fase del plan:** 5 (`plan-de-trabajo.md`, «FASE 5»)
- **Objetivo:** reducir el tiempo real y percibido de respuesta atacando la causa del patrón dominante en el registro de uWSGI: desconexiones concentradas en el listado de pedidos. La desconexión es el síntoma, no la enfermedad.
- **Precondición:** Épica 02 completa.

## Alcance

1. **Medición inicial antes de intervenir** (primera mitad de 05-06): tiempo hasta el primer contenido pintado, peso transferido, número de peticiones y número de consultas por página en las tres vistas más usadas. Se hace antes de 05-01, aunque su número sea el último.
2. Arranque en frío: confirmar el efecto de 00-06, diferir otras importaciones pesadas y documentar el límite que impone la hibernación.
3. Consultas por fila: pasar `total_pagado_real`, `saldo_pendiente` y `porcentaje_pagado` a anotaciones en listados, detalle de pedido, trabajo semanal, detalle de pago y panel financiero, midiendo consultas antes y después con una herramienta de diagnóstico de consultas en local.
4. Índices justificados uno por uno con una consulta concreta (Clase 2), ensayados en la réplica.
5. Tailwind CSS v3 compilado con pnpm (RDA-010), con la configuración de tema extraída de `base.html` y `login.html`. En la misma iteración se resuelven las restricciones de `DESIGN.md`: el texto amarillo en modo claro (AUD-02-017) y el respaldo `cursive` de Bebas Neue (AUD-02-018).
6. Recursos externos: tipografías e íconos autoalojados o no, según la decisión pendiente; Select2 y Summernote solo en las páginas que los usan.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 05-01 | Reducción del arranque en frío | 5.1 |
| 05-02 | Consultas por fila en plantillas | 5.2 |
| 05-03 | Índices de base de datos | 5.3 |
| 05-04 | Compilación local de estilos | 5.4 |
| 05-05 | Consolidación de recursos externos | 5.5 |
| 05-06 | Medición de rendimiento | 5.6 |

## Decisiones de la épica

- Instalar la herramienta de diagnóstico de consultas solo como dependencia de desarrollo, con consulta y sin que llegue a producción.
- Compilar estilos pasa a ser un paso de la lista de comprobación previa al despliegue.

## Criterio de término

- Reducción medida y documentada en las cuatro métricas, comparada con la medición inicial.
- Dos semanas de registro del servidor con menos desconexiones en el listado de pedidos que la línea base.
