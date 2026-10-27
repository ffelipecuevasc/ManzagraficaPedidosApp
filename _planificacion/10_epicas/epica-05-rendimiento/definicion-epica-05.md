# Épica 05 · Rendimiento del servidor

- **Estado:** Pendiente
- **Fase del plan:** 5 (`plan-de-trabajo.md`, «FASE 5»), reordenada el 2026-10-27 (anexo del plan, RDA-014)
- **Objetivo:** reducir el tiempo de respuesta del servidor atacando la causa del patrón dominante en el registro de uWSGI: desconexiones concentradas en el listado de pedidos. La desconexión es el síntoma, no la enfermedad.
- **Precondición:** Épica 02 completa. Se ejecuta después de la Épica 04.
- **Última revisión:** 2026-10-27 (estructura reordenada: la medición abre y cierra la épica; los estilos y los recursos externos pasan a la Épica 08).

## Alcance

1. **Medición inicial antes de intervenir (05-00):** en las tres vistas más usadas, el número de consultas por página y el tiempo de respuesta del servidor, más el conteo de desconexiones del listado de pedidos en el registro de uWSGI. Sin esta cifra no se puede demostrar que una optimización funcionó.
2. **Arranque en frío (05-01):** confirmar el efecto de 00-06, diferir otras importaciones pesadas y documentar el límite que impone la hibernación.
3. **Consultas por fila (05-02):** pasar `total_pagado_real`, `saldo_pendiente` y `porcentaje_pagado` a anotaciones en listados, detalle de pedido, trabajo semanal, detalle de pago y panel financiero, midiendo consultas antes y después con una herramienta de diagnóstico de consultas en local.
4. **Índices (05-03):** justificados uno por uno con una consulta concreta (Clase 2), ensayados en la réplica.
5. **Medición final (05-06):** repetir la medición de 05-00 con el mismo método y comparar, más dos semanas del registro del servidor.

## Iteraciones

| Iteración | Nombre | Origen | Orden |
| :-------- | :----- | :----- | :---- |
| 05-00 | Medición inicial del servidor | Primera mitad de la subfase 5.6 | 1.º |
| 05-01 | Reducción del arranque en frío | 5.1 | 2.º |
| 05-02 | Consultas por fila en plantillas | 5.2 | 3.º |
| 05-03 | Índices de base de datos | 5.3 | 4.º |
| 05-06 | Medición final del servidor | Segunda mitad de la subfase 5.6 | 5.º |

Los números 05-04 y 05-05 no se usan: la compilación local de estilos (antes 05-04) y la consolidación de recursos externos (antes 05-05) pasaron a la Épica 08. Se dejan libres para que las referencias antiguas a 05-04 y 05-05 no apunten a otra cosa (RDA-014).

## Decisiones de la épica

- Instalar la herramienta de diagnóstico de consultas solo como dependencia de desarrollo, con consulta y sin que llegue a producción.
- **2026-10-27 · Medición en dos tiempos (decisión del desarrollador).** La medición se divide en una iteración inicial (05-00) y una final (05-06), para que el orden de los números coincida con el orden de ejecución.
- **2026-10-27 · Métricas del navegador fuera de esta épica.** El tiempo hasta el primer contenido pintado, el peso transferido y el número de peticiones dependen sobre todo de los estilos y las librerías del navegador: los mide la Épica 08 (08-01 y 08-09) antes y después de sus cambios.

## Criterio de término

- Reducción medida y documentada del número de consultas por página y del tiempo de respuesta del servidor en las tres vistas, comparada con 05-00.
- Dos semanas de registro del servidor con menos desconexiones en el listado de pedidos que la medición de 05-00.

## Notas

- **2026-10-27 (reorganización, RDA-014):** la épica pasa a llamarse «Rendimiento del servidor». La compilación de Tailwind (RDA-010, AUD-02-017, AUD-02-018) y los recursos externos (AUD-01-010) pasan a la Épica 08, que los atiende junto con la reorganización de estáticos y plantillas pedida por el desarrollador.
