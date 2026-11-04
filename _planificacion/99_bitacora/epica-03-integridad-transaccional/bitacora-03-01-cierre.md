# Bitácora 03-01 · Cierre de la iteración y hallazgo AUD-05-001

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** Terminada (la 03-01). Solo documentos; sin cambios de código ni de pruebas.

## Resumen

Se cerró la 03-01 con la constancia de la revisión manual que hizo el desarrollador en la réplica local. En esa revisión apareció un hallazgo ajeno a la 03-01 (AUD-05-001, columna ACCIONES del listado de cotizaciones), que se registró en una auditoría nueva y se asignó a la Épica 08. Complementa [bitacora-03-01](bitacora-03-01.md), que no se edita (regla 5.4).

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-01-rediseno-decorador-transaccional.md:4` | Estado «Terminada (2026-11-04)» y historial de estados. |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-01-rediseno-decorador-transaccional.md:157` | Criterio de revisión manual marcado, con la constancia de la decisión 1. |
| `00_producto/auditoria-tecnica.md` (final del archivo) | Auditoría 05 con AUD-05-001. |
| `10_epicas/epica-08-frontend/definicion-epica-08.md:43-45` | Sección «Para la redacción (iteración por definir)», con nota fechada. Sin cambio de alcance ni de iteraciones. |
| `00_producto/registro-pendientes.md:6`, `:7`, `:16` y `:43` | Estado de la 03-01 «Terminada» y siguiente paso: redactar la 03-02. |
| `00_producto/registro-pendientes.md` (sección 3) | Fila «Épica 08 · iteración que corrige la columna ACCIONES…» (`PENDIENTE_DESARROLLADOR`). |
| `00_producto/registro-pendientes.md` (último de la sección 5) | Entrada de historial 2026-11-04. |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-01-cierre.md` | Esta bitácora (nueva). |

## Revisión manual (hecha por el desarrollador, no por el agente)

- **Entorno:** réplica local, `DEBUG=False` y `runserver --insecure`. Con `DEBUG=False` Django muestra la página 404 de la aplicación y no la pantalla técnica de depuración; con `--insecure` sirve los archivos estáticos, que sin eso no se cargan con `DEBUG=False`.
- **Pantallas:** editar pedido y editar cliente con un `pk` inexistente. Se vio la página 404 de la aplicación, en escritorio y a 360 px.
- **Convertir cotización con `pk` inexistente:** no se probó a mano. Lo cubre R20, que verifica 404 en las 12 rutas con `pk` (incluida la de convertir cotización), en verde en las tres ejecuciones de la [bitácora 03-01](bitacora-03-01.md).
- El criterio se cierra con esa constancia (decisión 1 del desarrollador).

## Prueba extra (hecha por el desarrollador)

- Convertir una cotización existente funcionó.
- La cotización ya convertida muestra un aviso y no ofrece Editar ni Eliminar.
- Es un **bloqueo de pantalla**. No cierra AUD-02-005 ni R13 (convertir dos veces crea un solo pedido), que siguen siendo de la 03-03.

## Hallazgo nuevo · AUD-05-001

- **Qué se vio:** en el listado de cotizaciones, a pantalla completa, la columna ACCIONES queda fuera de vista y exige desplazamiento horizontal.
- **Dato leído en la plantilla:** la tabla va dentro de un contenedor `overflow-x-auto` (`cotizacion_list.html:42-43`) y el encabezado «Acciones» está en `:71`. La causa no se investigó, y no se comprobó si ocurre en producción ni en otros listados.
- **Clasificación:** Media, Frontend/UX, asignado a la Épica 08 con la iteración `PENDIENTE_DESARROLLADOR`. No se corrige en la Épica 03.
- **ID:** el archivo exige sumar uno al último número de auditoría (la 04) y los IDs nunca se reutilizan. Como el origen es otro (revisión manual de la 03-01) y no encaja con el alcance de la Auditoría 04 (audios del cliente y registros del servidor), se creó la **Auditoría 05**, y el hallazgo es **AUD-05-001**. Si prefieres sumarlo a la 04 como AUD-04-006, es un cambio de un ID.

## Verificación

- Pruebas: no se ejecutaron (sin cambios de código). Las de la 03-01 están en [bitacora-03-01](bitacora-03-01.md): 186 pruebas, `OK (expected failures=18)` en tres ejecuciones.
- `git --no-pager status --short` y `git --no-pager diff --stat`: solo los `.md` de la tabla.

## ¿Queda algo abierto de la 03-01?

Nada. Los criterios de la iteración están marcados y la revisión manual está constatada. Lo que sigue pendiente pertenece a otras iteraciones:

- AUD-01-001 se cierra en la 03-03 (decisión del 2026-11-04).
- El despliegue viaja con la 03-05.
- AUD-05-001 es de la Épica 08.

## Decisiones tomadas

Decisiones del desarrollador del 2026-11-04:

1. La revisión manual se cierra con la constancia descrita arriba.
2. La conversión de una cotización es solo un bloqueo de pantalla y no cierra AUD-02-005 ni R13.
3. AUD-05-001: Media, Frontend/UX, Épica 08, iteración `PENDIENTE_DESARROLLADOR`.

## Commit sugerido

`Épica 3 - Iteración 03-01: cierra la iteración y registra el hallazgo de acciones`
