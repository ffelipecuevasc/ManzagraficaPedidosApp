# Bitácora 00-01 · Línea base de producción (cierre)

- **Fecha:** 2026-10-20
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Terminada (por decisión del desarrollador)

## Resumen

El desarrollador entregó los datos que faltaban en la evidencia: el tamaño de `backups/`, el uso de CPU, el desglose por tabla, los formatos de fecha de los registros y su método de conteo por fecha. También tomó cinco decisiones. Se completó la línea base y se guardó el método de conteo, verificado y con tres ajustes para 00-06. Se reemplazó el último criterio de 00-06, se ajustó el término de la épica 00, se agregó la nota de retención a la épica 06, se bajó AUD-02-007 a Baja y se cerró la iteración. Esta bitácora complementa `bitacora-00-01-produccion.md`, que no se editó.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/00_producto/linea-base-produccion.md` | `backups/` completo (7 MB), CPU del Dashboard, las 18 tablas del desglose y los formatos de fecha de los registros. |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-01.md` | CPU en la tabla de respuesta, el método del desarrollador con su resultado, la verificación del agente y el método reutilizable para 00-06. |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-06-correcciones-tempranas.md` | Último criterio reemplazado y tarea 6 ajustada. |
| `_planificacion/10_epicas/epica-00-blindaje/definicion-epica-00.md` | Estado de la épica, 00-01 terminada y último punto del criterio de término. |
| `_planificacion/10_epicas/epica-06-arquitectura-automatizacion/definicion-epica-06.md` | Nota de retención de volcados para 06-03. |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-01-linea-base-produccion.md` | Estado «Terminada» y criterios marcados. |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-02-007 en Baja y abierto; notas de AUD-02-007 y AUD-02-021. |
| `_planificacion/00_producto/registro-pendientes.md` | 00-01 terminada, iteración activa 00-02, pendientes resueltos y nuevos, historial. |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-01-cierre.md` | Esta bitácora. |

## Verificación

- `git status` antes de editar: árbol limpio (el desarrollador ya había hecho commit `a9d0171`). No había cambios del desarrollador que respetar.
- **Comandos de conteo del desarrollador:** probados contra registros simulados en el scratchpad, con líneas del servidor que empiezan con `AAAA-MM-DD HH:MM:SS` y líneas de acceso con `[dd/Mon/aaaa:hh:mm:ss +0000]`. Agrupan bien por día: un `Broken pipe` el día anterior y un `Broken pipe` más un `SIGPIPE` hoy dan 1/0 y 1/1. Con una 404 y una 200 de `/robots.txt` el mismo día, `robots=2`. Eso confirma que el comando no separa el código de respuesta.
- **Método reutilizable:** con `zcat -f` sobre todos los archivos, incluido un `.gz`, y el filtro `" 404 "`, informa `robots` y `robots_404` por separado y lee los archivos rotados.
- **Desglose por tabla:** 18 filas, las mismas 18 tablas de la sección 2a. La suma de los totales es 2,20 MB, igual que el peso total ya registrado.
- Pruebas: no aplican, no se tocó código.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Los cinco criterios de 00-01, según `bitacora-00-01-produccion.md`, con la línea base ahora sin datos faltantes, salvo la confirmación del origen de la fecha de expiración (el dato existe: 2026-11-20).

## Decisiones tomadas

- **Estado «Terminada» en lugar de «Completada».** `_planificacion/README.md` (sección 3) define los estados válidos y «Completada» no está entre ellos: el equivalente es `Terminada`.
- **La épica 00 queda «En curso»**, no terminada. En su definición solo se marcó 00-01 como terminada, porque faltan 00-02 a 00-06.
- **En el criterio de 00-06 se cambió «todas de Googlebot» por «las líneas de muestra revisadas son de Googlebot».** La evidencia solo mostró dos líneas de muestra; no hay medición del agente de las 7. Si contaste las 7, puedes devolver el texto original.
- **AUD-02-007 sigue abierto con severidad Baja**, por el desfase de un pedido en el límite entre julio y agosto (65/77 en hora de Chile contra 64/78 en UTC). Se corrige en 06-01.
- **AUD-02-021 sigue abierto**, con la causa pendiente.

## Pendientes y riesgos

- `PENDIENTE_DESARROLLADOR`: confirmar si la expiración del 2026-11-20 viene de una renovación hecha el día de la medición. No venía en este cierre.
- AUD-02-021: falta el comando que entregue la fecha y el mensaje completo de cada error del decorador.
- Informe de desconexiones a 28 días de 00-06 (registrado en `registro-pendientes.md`).

## Commit sugerido

`Épica 0 - Iteración 00-01: cierra la iteración, completa la línea base, guarda el método de conteo por fecha y ajusta el criterio de 00-06`
