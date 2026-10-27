# Épica 10 · Mejoras para el negocio: Trabajo Semanal

- **Estado:** Pendiente
- **Fase del plan:** no existe en el plan original; anexo del plan del 2026-10-27 (RDA-014)
- **Objetivo:** enriquecer el tablero «Trabajo Semanal», la pantalla que Ignacio revisa varias veces al día, con funciones que le ahorren pasos y le anticipen problemas.
- **Precondición:** Épicas 07 y 08 completas (selectores reutilizables y parciales), 05-02 terminada (saldos por anotación, sin consultas por fila) y 04-01 desplegada (los cambios de estado son POST).
- **Última revisión:** 2026-10-27 (creada a pedido del desarrollador).

## Cómo se define el alcance

Las mejoras las idea y elige **el desarrollador**, sin una entrevista previa con el cliente (decisión del 2026-10-27). El antecedente lo justifica: Ignacio no sabía que necesitaba el tablero hasta que el desarrollador lo implementó y se lo explicó, y hoy es la pantalla que más usa. La primera iteración deja por escrito qué mejoras se construyen, con su comportamiento esperado; cada mejora elegida es después una iteración propia.

## Qué hace hoy el tablero (medido en el código, `trabajo_semanal` en `pedidos/views.py`, commit `ac70401`)

- Toma los pedidos que no están `TERMINADO` y los separa en **críticos** (entrega vencida), **urgentes** (entrega en los próximos 7 días) y **normales** (después).
- Calcula un **nivel de presión** (críticos más urgentes sobre el total de activos) y el **día peak** de entregas de la semana.
- Observaciones para la definición:
  - Un pedido activo **sin fecha de entrega** no cae en ninguna de las tres listas, pero sí cuenta en el total de activos.
  - Un pedido `ENTREGADO` con fecha vencida aparece como crítico.

  Ambas son las reglas sin confirmar de AUD-02-013, que la 07-04 resuelve antes de esta épica.
- «Hoy» se calcula con `timezone.now().date()`, que es la fecha en UTC (AUD-02-003, se corrige en 06-01).

## Ideas propuestas para que el desarrollador elija (no son compromisos)

| # | Idea | Qué le resuelve a Ignacio |
| :- | :--- | :------------------------ |
| A | **Vista por días:** columnas de lunes a sábado con los pedidos de cada día y su carga | Ver de un vistazo cómo se reparte la semana, no solo el día peak |
| B | **Cambio de estado desde el tablero** con un formulario POST en cada tarjeta | Marcar avances sin abrir el detalle de cada pedido |
| C | **Saldo por cobrar** en cada tarjeta y total por cobrar de lo que se entrega en la semana | Llegar a la entrega sabiendo cuánto cobrar |
| D | **Días de atraso** visibles en los críticos, ordenados del más atrasado al menos | Priorizar lo que más urge |
| E | **Navegación entre semanas** (anterior y siguiente) y vista «mañana» | Planificar más allá de los próximos 7 días |
| F | **Filtros rápidos:** por estado, solo con saldo pendiente, solo de hoy | Encontrar rápido lo que busca |
| G | **Lista imprimible del día** para el taller | Llevar el trabajo del día al taller sin pantalla |
| H | **Actualización automática** cada cierto tiempo (por ejemplo con HTMX, si la 08-07 lo adopta) | La pantalla siempre al día, sin recargar a mano |
| I | **Sección de pedidos sin fecha de entrega** | Que ningún pedido activo quede invisible |

## Iteraciones

| Iteración | Nombre |
| :-------- | :----- |
| 10-01 | Definición funcional de las mejoras del tablero |
| 10-02 en adelante | Una iteración por mejora elegida en 10-01, en el orden que fije el desarrollador |

## Decisiones de la épica

- Qué ideas se construyen y en qué orden: `PENDIENTE_DESARROLLADOR`, se decide en 10-01.
- Ninguna mejora agrega escrituras en peticiones de lectura ni consultas por fila: cada una se mide con la herramienta de diagnóstico de consultas de la 05-02.
- Las mejoras que dependan de una librería nueva (por ejemplo, la actualización automática) esperan la decisión de la 08-07.

## Fuera de alcance

- Mejoras de otras pantallas: si aparecen ideas, se anotan en la sección 4 del registro y se evalúan como épica o iteración aparte.
- Avisos por correo de lo que muestra el tablero: Épica 11.

## Criterio de término

- Cada mejora elegida en 10-01 está desplegada y cumple el comportamiento escrito en 10-01.
- El tablero no hace más consultas por carga que antes de la épica, salvo las justificadas en la bitácora (medido con la herramienta de diagnóstico de consultas).

## Notas

- **2026-10-27:** creada a pedido del desarrollador. Las ideas A a I son propuestas del asistente; el desarrollador puede descartarlas o agregar otras en 10-01.
