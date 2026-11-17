# Bitácora 04-06 · Cierre documental de la redacción (D1 a D4)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-06 queda **Pendiente (redactada, decisiones resueltas)**. Solo documentos; sin código, pruebas, `manage.py` ni `sqlmigrate`.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Resuelta como |
| :- | :------------ |
| D1 | «No se puede eliminar este cliente porque tiene pedidos o cotizaciones registrados. Para conservar su historial, no está permitido borrarlo.» |
| D2 | Advertencia «Solo se puede eliminar un cliente sin pedidos ni cotizaciones»; sin conteos y sin ocultar el botón. |
| D3 | Sin evento por el rechazo. |
| D4 | Pruebas además de R14: cliente que solo tiene cotización, y la vista con y sin historial. |

## Ajustes

- Iteración: estado, decisiones en tabla, alcance (puntos 3 a 5), pruebas (marcadas con D4; el GET comprueba que el botón sigue), riesgos nuevos (botón visible, sin rastro del rechazo).
- Se conserva como `PENDIENTE_CLIENTE` la pregunta sobre pagos borrados en cascada (registro, sección 2).

## Archivos

`iteracion-04-06-proteccion-del-historial.md`, `definicion-epica-04.md`, `00_producto/registro-pendientes.md` (por bytes, CRLF intacto) y esta bitácora.
