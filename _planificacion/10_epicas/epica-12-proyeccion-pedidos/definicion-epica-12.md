# Épica 12 · Proyección de pedidos

- **Estado:** Pendiente
- **Fase del plan:** no existe en el plan original; anexo del plan del 2026-10-27 (RDA-014)
- **Objetivo:** responder con datos a la pregunta que más angustia al negocio, «¿cuánto trabajo viene en los próximos meses?», con dos respuestas distintas y honestas: lo que **ya está comprometido** (dato real) y lo que **probablemente llegue** (estimación estadística con su margen).
- **Precondición:** 06-01 desplegada (los meses se calculan en hora de Chile, AUD-02-003), Épica 07 completa (los cálculos viven en selectores y servicios con pruebas directas) y 08-07 decidida (con qué se dibujan los gráficos).
- **Última revisión:** 2026-10-27 (creada a pedido del desarrollador; sin aprendizaje automático por decisión del desarrollador, RDA-018).

## Por qué sin aprendizaje automático (contexto para quien llega)

Al 2026-10-20 la base tiene 870 pedidos, todos de 2026 (línea base, sección 5): **diez puntos mensuales** (de 109 en enero a 64 en octubre, este último con el mes en curso). Un modelo supervisado (por ejemplo, con scikit-learn) entrenado con diez puntos aprende ruido y no puede ver la estacionalidad, que necesita al menos dos años (marzo escolar, diciembre). Además, numpy, scipy y scikit-learn ocupan una parte importante de los 512 MiB de disco. La biblioteca estándar de Python 3.13 (`statistics`, `datetime`, `calendar`) basta para lo que se necesita, sin dependencias nuevas (RDA-018).

## Alcance

1. **Carga comprometida (12-01):** pedidos activos con fecha de entrega futura, agrupados por semana y por mes: cantidad, valor de venta y saldo por cobrar. No es una predicción: es trabajo que ya existe. Incluye cuántos pedidos activos no tienen fecha de entrega, para que no queden fuera de la cuenta.
2. **Proyección estadística (12-02)**, sobre los pedidos recibidos por mes (`fecha_solicitud`, mes en hora de Chile), con la biblioteca estándar:
   - **ritmo del mes en curso:** pedidos recibidos hasta hoy sobre los días transcurridos, proyectado al total de días del mes;
   - **promedio móvil** de los últimos tres meses completos;
   - **tendencia lineal** por mínimos cuadrados con `statistics.linear_regression`;
   - **margen:** un rango plausible (por ejemplo, el mínimo y el máximo de los últimos seis meses, o el promedio más o menos una desviación estándar con `statistics.stdev`);
   - **comparación interanual** (mismo mes del año anterior), que se activa sola cuando existan al menos trece meses de historia.
3. **Validación con el pasado (en 12-02):** para cada mes ya cerrado se calcula qué habría proyectado cada método con los datos anteriores a ese mes, y se mide el error medio. La pantalla usa el método con menor error y lo dice. Así la proyección se gana la confianza con evidencia y no por promesa.
4. **Pantalla de proyección (12-03):** solo lectura, para superusuarios y operadores. Muestra la carga comprometida, la proyección de los próximos tres meses con su margen, cuántos meses de historia la respaldan y una advertencia en lenguaje simple: «estimación basada en N meses; mejora con más historia». Los cálculos se hacen al pedir la página (870 pedidos se agrupan en milisegundos), sin tablas nuevas.

## Iteraciones

| Iteración | Nombre |
| :-------- | :----- |
| 12-01 | Carga comprometida |
| 12-02 | Proyección estadística y validación con el pasado |
| 12-03 | Pantalla de proyección |

## Decisiones de la épica

- **2026-10-27 · Sin aprendizaje automático (RDA-018, decisión del desarrollador).** Python estándar, sin numpy, scipy ni scikit-learn.
- Qué margen se muestra (mínimo y máximo, o desviación estándar) y cuántos meses se proyectan: `PENDIENTE_DESARROLLADOR`, se decide en 12-02 con los resultados de la validación con el pasado.
- ¿Se proyecta también el monto (valor de venta) o solo la cantidad de pedidos? `PENDIENTE_DESARROLLADOR`, se decide en 12-01.

## Fuera de alcance

- Aprendizaje automático, en el servidor o en la nube (RDA-018).
- Proyección por cliente o por producto.
- Guardar las proyecciones calculadas (no hace falta con este volumen).

## Criterio de término

- La carga comprometida coincide con un conteo hecho a mano en la réplica (prueba con datos ficticios y oráculo, al estilo de la 02-02).
- Cada método de proyección tiene pruebas con series conocidas (resultado calculado a mano), incluidas las series cortas: uno, dos y tres meses.
- La validación con el pasado queda documentada en la bitácora con el error de cada método.
- La pantalla se ve correctamente en escritorio y a 360 px.

## Notas

- **2026-10-27:** creada a pedido del desarrollador. La cifra de pedidos por mes es de la línea base (`linea-base-produccion.md`, sección 5, medida el 2026-10-20).
