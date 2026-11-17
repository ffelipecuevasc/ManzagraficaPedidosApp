# Bitácora 04-08 · Cierre documental de la redacción (D1 a D5)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** la 04-08 queda **Pendiente (redactada, decisiones resueltas)**. Solo documentos; sin código, pruebas, `manage.py`, `sqlmigrate` ni consultas a la base.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Resuelta como |
| :- | :------------ |
| D1 | Contador propio en la caché local. |
| D2 | 5 fallos por usuario y 20 por dirección, en 15 minutos, con bloqueo de 15; medir antes con la consulta incluida. |
| D3 | Dirección real por la variable de proxies de confianza `ACCESO_PROXIES_CONFIABLES`, medida en producción. |
| D4 | Tipo de evento nuevo `acceso_bloqueado`, con migración de Clase 1. |
| D5 | Imagen de referencia de 5 MB y chequeo temprano de `CONTENT_LENGTH`. |

## Verificación de la numeración de la migración

`pedidos/migrations/` llega hasta `0007_registroevento` (listado el 2026-11-17, sin `0008`). La 04-06 crea la `0008` (`proteger_historial_cliente`) y se despliega antes, así que la de la 04-08 es la **`0009`**, con dependencia en la `0008`. Ninguna otra iteración de la épica crea migraciones (la 04-05 es Clase 1 sin migraciones; la 04-07 no toca esquema; la 04-09 tampoco). La iteración fija un paso de comprobación con `showmigrations` si el orden cambiara.

## Ajustes

- Iteración: estado, decisiones en tabla, qué se descartó, alcance, pasos (la evidencia previa pasa a obligatoria, con regla de detención: 4 o más fallos de un usuario en una ventana de 15 minutos), pruebas, riesgos, retroceso (caso 2, con `migrate pedidos 0008` primero) y criterio de término.
- **Corrección de un defecto de la redacción:** el retroceso decía que poner `ACCESO_PROXIES_CONFIABLES` en `0` desbloquea a todos, y eso devolvería la dirección del proxy (peor). Además la verificación 3 hablaba de bajar «el límite de dirección por variable» sin que existiera. Se agrega la variable opcional **`ACCESO_FALLOS_POR_DIRECCION`** (defecto 20; `0` desactiva solo ese contador): permite medir y es el interruptor de emergencia.
- **Supuesto que el desarrollador debe confirmar:** (1) esa variable adicional no estaba en las decisiones; (2) D5 se tomó como la opción recomendada completa, o sea, además de la imagen de 5 MB y del chequeo temprano, los dos valores explícitos de 2,5 MB (sin cambio de comportamiento).

## Archivos

`iteracion-04-08-proteccion-del-acceso-y-limites-de-entrada.md`, `definicion-epica-04.md`, `00_producto/registro-pendientes.md` (por bytes, CRLF intacto) y esta bitácora.
