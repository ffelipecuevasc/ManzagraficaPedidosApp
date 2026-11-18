# Bitácora 03-05 · Producción (2): lectura anticipada, parte F, cierre y RDA-021

- **Fecha:** 2026-11-18
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión. La 03-05 y la Épica 03 quedan **Terminadas por decisión del desarrollador** (dicha por él). Solo documentos: sin cambios de código, sin commit, sin etiqueta, sin despliegue y sin tocar PythonAnywhere. **Todo dato de producción y de la réplica es dicho por el desarrollador, de sus consolas; el agente no vio ninguna salida.**

Esta bitácora no edita la [bitacora-03-05-produccion](bitacora-03-05-produccion.md) del día 0, que ya estaba entregada (`_planificacion/README.md`, 5.4: las correcciones van en una bitácora nueva con sufijo). Donde esa bitácora dice «día 7» o «vigilancia», léase superado por esta.

## Resumen

El desarrollador decidió eliminar las esperas de 3, 5 y 7 días (RDA-021) y cancelar la lectura del día 7 de la 03-05. En su lugar hizo una **lectura anticipada** de 38 h 34 min (de `R`, 2026-11-17 02:48:12 UTC, a 2026-11-18 17:22 UTC): sin `ERROR` nuevo salvo el `OSError` ya clasificado (AUD-04-004), sin `5xx`, 11 pedidos nuevos = 10 creados + 1 duplicado + 0 convertidos y `grupos_repetidos=0`. **No cumplió** el criterio (iv) (`/pagos/ingresar/` tardó de 2,7 a 8,0 s en las pruebas del día 0) ni «nadie reporta un “no se guardó”» (un pago): son defectos anteriores, iguales en `v0.3-doble-envio` (dicho), registrados como AUD-05-011 y AUD-05-010. Sin retroceso. La parte F quedó hecha (respaldo nuevo, disco de Docker en D:, réplica refrescada, conteo F4) y AUD-05-002 se cierra. También se anotó el informe C2 de la 00-06, anticipado y parcial.

## Datos dichos por el desarrollador (2026-11-18)

| Tema | Dato |
| :--- | :--- |
| Decisión | Se eliminan las esperas de 3, 5 y 7 días; cada despliegue se valida con el día 0 y el plan de retroceso; al cerrar una épica se pasa de inmediato a la siguiente. Regístrala como RDA-021 y cancela la lectura del día 7 |
| D2 y D3 | Reemplazadas por la lectura anticipada: sin `ERROR` nuevo salvo el `OSError` (AUD-04-004) y sin `5xx` |
| D4 (UTC 11-17 02:48 a 11-18 17:22) | `pedidos_nuevos=11`, `creado=10`, `duplicado=1` (#1015, AUD-02-006), `convertida=0`, `grupos_repetidos=0` |
| D5 | (i), (ii), (iii) y (v) cumplen. (iv) **no** cumple: `/pagos/ingresar/` de 2,7 a 8,0 s el 11-17 de 02:55 a 02:58 UTC (pruebas del día 0); causa inferida N+1, igual en `v0.3-doble-envio`: excepción, AUD-05-011. El «no se guardó» de un pago que reportó el cliente es AUD-05-010, igual en `v0.3-doble-envio` |
| Regla E | Sin retroceso; «formulario que no guarda» se exceptúa por decisión del desarrollador |
| Informe C2 de la 00-06 | 26 días (2026-10-24 a 2026-11-18 parcial): `Broken pipe` 18 (0,69 por día; base 0,44), `SIGPIPE` 55 (2,1 por día); `/robots.txt` 15 peticiones, 0 con 404 (los 200 no se contaron) |
| Respaldo (respaldo.md, sección 6) | `respaldo_18-11-2026_14-26-45.sql`, 1.535.086 bytes, 19 de 19, `VÁLIDO`, SHA-256 `774bda86774fa54b516d3cf4e92e2246827a9e8cc8b49a6aeef5e83a36625b35`; motivo: réplica |
| Refresco de la réplica | Con ese volcado: 4,4 s, código 0, 19 tablas, migración `0007` |
| F4 | Pedidos 994, sin ítems 127, sin ítems desde el primero con ítems 39 (2026-11: 1); cotizaciones 33, 0 sin ítems; antes 888, 126 y 38: indicio, sin concluir |
| AUD-05-002 | Disco en `D:\Docker\datos_nuevos_nov_2026\DockerDesktopWSL`, sin `.vhdx` en C:, D: cifrada (`manage-bde`: «Cifrado completo», 100,0 %, «Protección activada»); queda una copia vieja de 40,3 GB en `D:\Docker\datos`, también cifrada |
| AUD-05-010 | Crítica: pagos de pedidos desde el #1000 se rechazan en silencio; con `USE_THOUSAND_SEPARATOR` y `es-cl`, `pago_form.html:78` escribe el id «1.002»; desde «v1.0»; destino 04-01 |
| AUD-05-011 | Alta: N+1 en `/pagos/ingresar/`; sin iteración |
| AUD-04-001 | Parte de servidor cerrada |
| AGENTS.md, sección 5 | La propuesta está aplicada desde `27f7ff9` |

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/00_producto/decisiones.md` | RDA-021 (fila del índice y sección). La RDA-020 queda reservada (propuesta `nh3`, se escribe al ejecutar la 04-07) |
| `_planificacion/10_epicas/epica-03-integridad-transaccional/evidencia-03-05.md` | Estado, calendario vigente (el anterior queda como registro), aviso de la parte D, tablas D2 a D5 con lo informado y lo no informado, resultado de la parte E, tablas F1 a F4 y cierre, límites y respuesta del 2026-11-18 |
| `_planificacion/10_epicas/epica-03-integridad-transaccional/iteracion-03-05-validacion-y-despliegue-de-la-integridad.md` | Estado «Terminada» (el anterior queda como registro), dos casillas de criterio marcadas, tres sin marcar y explicadas, y fechas vigentes del 2026-11-18 |
| `_planificacion/10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md` | Cabecera «Terminada» (con «Pendiente» tachado), alcance 5 y criterio «una semana» superados sin borrar, nota fechada |
| `_planificacion/99_bitacora/epica-03-integridad-transaccional/bitacora-03-05-produccion-2.md` | Nuevo (esta bitácora) |
| `docs/operacion/despliegue.md` | Fila del 2026-11-16 en la sección 5: «vigilancia hasta el día 7» tachado y nota del 2026-11-18; en 3.8, una línea que dice que desde la RDA-021 no hay vigilancia posterior |
| `docs/operacion/respaldo.md` | Fila del respaldo del 2026-11-18 14:26:45 en la sección 6 |
| `docs/operacion/replica-local.md` | Sección 2 (nota: la comprobación b ya pasa), sección 9 (fila del refresco y nota que supera la del 2026-11-04) |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-05-002 «Resuelto en 03-05 (parte F, 2026-11-18)»; AUD-04-001, parte de servidor cerrada (sigue Abierto); AUD-05-010 y AUD-05-011 nuevos; cuatro notas fechadas |
| `_planificacion/00_producto/registro-pendientes.md` | Cabecera, próximo hito, fechas, estados, filas de la sección 3 (cinco resueltas, siete nuevas) e historial de tres filas. Lo anterior queda como «anterior, superado» |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-06.md` | Parte C2 con el informe parcial de 26 días |
| `_planificacion/10_epicas/epica-00-blindaje/definicion-epica-00.md` | Seguimiento C2 hecho; propuesta de `AGENTS.md` sección 5 marcada como resuelta |

No toqué `AGENTS.md`, `DESIGN.md`, `README.md`, `_planificacion/README.md`, el código, `.env`, `.claude/`, `.git/` ni ningún archivo de la Épica 04. Sin nombres de personas.

## Verificación

- **Cada reemplazo coincidió exactamente una vez** (el guion aborta sin escribir si no): una ancla coincidió dos veces (AUD-02-006 y AUD-04-001 terminan igual) y se corrigió con una más larga antes de escribir nada.
- **Finales de línea:** CRLF sin una sola LF suelta en los cinco archivos que ya eran CRLF; LF sin CRLF en los seis que ya eran LF. `git status`: solo los once archivos de la tabla, más este.
- **Tachados:** ninguna línea agregada con `~~` impar. **Nombres:** ninguna línea agregada nombra a una persona.
- **RDA-021 libre:** `decisiones.md` llega a la RDA-019; la RDA-020 está solo propuesta (04-07). Las únicas menciones de «RDA-021» eran de la Épica 04 (ver «Contradicciones»).
- **RDA-007:** leída; no fija ninguna espera. Compatible.
- **AGENTS.md y `27f7ff9`:** `git show 27f7ff9 -- AGENTS.md` muestra que el bloque propuesto en la bitácora 00-03 se aplicó con el mismo texto; la sección 5 actual trae `docker compose up -d`, `docker compose stop` y la prohibición.
- **Código leído (no ejecutado):** `pago_form.html:75-84` (el campo oculto está en `:78` y el error del campo `pedido` solo se pinta en la otra rama, `:81-83`), `settings.py:177` y `:201`, `forms.py:89`, `models.py:61`, `views.py:1481` (`pedido_id` llega por la ruta). Coincide con lo dicho; ninguna de las dos causas se reprodujo.
- **Cuentas:** de `R` (02:48:12 UTC del 11-17) a las 17:22 del 11-18 hay 38 h 34 min; 18 ÷ 26 = 0,69; 55 ÷ 26 = 2,1; 11 = 10 + 1 + 0.
- No ejecuté pruebas ni `manage.py`: no hay cambios de código.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] RDA-021 escrita, con la verificación de que la 021 estaba libre y de que no contradice la RDA-007.
- [x] Lectura del día 7 cancelada y reemplazada por la lectura anticipada (D2 a D5 de la evidencia), con lo no informado marcado.
- [x] Informe C2 de la 00-06 anotado (parcial, 26 días).
- [x] Respaldo del 2026-11-18 en `respaldo.md`, sección 6; refresco y F4 en `replica-local.md` y en la evidencia (partes F1 a F4).
- [x] AUD-05-002 cerrado con evidencia (dicha por el desarrollador); AUD-05-010 y AUD-05-011 registrados; AUD-04-001, parte de servidor cerrada, sin pasar a «Resuelto».
- [x] Propuesta de `AGENTS.md`, sección 5, marcada como resuelta en el registro y en `definicion-epica-00.md`.
- [x] 03-05 y Épica 03 Terminadas (cabecera, bitácora, `despliegue.md` y próximo hito), con «día 7» y «vigilancia» superados sin borrar.
- [ ] Tres casillas de la iteración 03-05 siguen sin marcar y se explican en ella: el conteo de `POST /pedidos/nuevo/` con 302 de `access.log` (no se informó), las notas fechadas en los hallazgos que la iteración «confirma en producción» y los `PENDIENTE_CLIENTE`.

## Decisiones tomadas

- **Del desarrollador (dichas por él):** RDA-021; cancelar el día 7; 03-05 y Épica 03 Terminadas; las excepciones de (iv) y del «no se guardó»; severidad Crítica de AUD-05-010 y destino 04-01; AUD-05-011 sin iteración; AUD-05-002 cerrado; la fuente del respaldo para la réplica (un respaldo nuevo).
- **Mías, a confirmar:**
  1. «Resuelto» solo con respaldo: lo leí como «con evidencia mínima», que es lo que exige `_planificacion/README.md` (5.3), y no como «con un volcado». AUD-05-002 lo cumple por las dos lecturas. Los demás hallazgos de la 03-05 no pasaron a «Resuelto».
  2. Escribí «Crítica» tal como se pidió, aunque la escala definida es Alta, Media y Baja (ver «Contradicciones»).
  3. En `respaldo.md` anoté «VÁLIDO (19 de 19)» sin «código 0», porque el código no se informó.
  4. Dejé «Terminada» con tres casillas de la iteración sin marcar, porque es una decisión del desarrollador y no tengo cómo marcarlas sin inventar datos.

## Contradicciones

1. **La Épica 04 (no editada) contradice la RDA-021.** Dice que nada se despliega ni se ejecuta hasta cerrar la vigilancia de la 03-05; fija la 04-01 «no antes del 2026-11-23 23:48»; y la 04-02 (D6) pide 3 días de observación entre sus dos escalones de HSTS. Están en `definicion-epica-04.md`, `iteracion-04-02` y `bitacora-04-revision-final.md`, `bitacora-04-cierre-redaccion.md`. La condición ya se cumple (la 03-05 está Terminada); la espera de 3 días de la 04-02 hay que decidirla. Lo dejé en el registro como superado y como `PENDIENTE_DESARROLLADOR`, sin reescribir esos documentos. Los dos escalones de HSTS siguen siendo dos despliegues: HSTS no se deshace en los navegadores que ya lo vieron, así que conviene decidir con calma si se sube de 3600 a 604800 sin esperar (consideración general, no medida aquí).
2. **«RDA-021» ya aparece en la Épica 04:** la 04-08 dice que «la siguiente libre sería la RDA-021» y la revisión final dice «RDA-021: no hace falta». Ahora la 021 está tomada; la siguiente libre es la RDA-022 (la 020 está reservada).
3. **AUD-05-010 con destino 04-01 frente a «un despliegue, un propósito»** (`AGENTS.md`, sección 10, punto 3, y RDA-007): la 04-01 es «mutaciones solo por POST» y el hallazgo es de localización de números en una plantilla. Queda en el registro como pendiente. Mientras no se despliegue, el defecto sigue en producción.
4. **Severidad «Crítica»:** `_planificacion/README.md` (5.3) y el encabezado de la auditoría definen solo Alta, Media y Baja. Es un documento protegido, así que va una propuesta al desarrollador en el resumen de la entrega.
5. **Criterio y regla E:** la regla E dice que un «formulario que no guarda» se retrocede, y el criterio (iv) y «nadie reporta…» no se cumplieron. Se resolvió por decisión del desarrollador (defecto anterior, no regresión); queda anotado en la evidencia y la iteración.
6. **Terminada con casillas sin marcar:** `_planificacion/README.md` (sección 4, punto 8) pide todos los criterios verificados para «Terminada». Decisión del desarrollador; se explicó en la iteración.
7. **«v1.0» (AUD-05-010):** no es una etiqueta del protocolo (`v0.0-inicial`, `v0.1-higiene`…). Lo transcribí como lo dijo el desarrollador y lo marqué sin verificar.
8. **Número de línea:** el pedido citaba `registro-pendientes.md:121` para la propuesta de `AGENTS.md`; esa fila estaba en la línea 127 (la 121 era el encabezado de la sección 3). `definicion-epica-00.md:66` sí coincidía.
9. **Espera de 5 días:** no encontré ninguna en los documentos (solo 3 días en la 04-02 y 7 en la 03-05). Quedó como pendiente.
10. **F4 «(2026-11: 1)»:** lo copié literal; no sé si significa «1 de ellos es de 2026-11» u otra cosa. Las diferencias con el conteo anterior (+106 pedidos, +1 sin ítems, +1 posterior al primero, +6 cotizaciones) son cuentas mías, no una conclusión.

## Pendientes y riesgos

- **`PENDIENTE_DESARROLLADOR`:** cómo queda la observación de 3 días de la 04-02; si hay una espera de 5 días y dónde; si AUD-05-010 se suma a la 04-01 o va aparte; qué iteración corrige AUD-05-011 (la 05-02 es candidata, no asignada); borrar o conservar la copia vieja de 40,3 GB de `D:\Docker\datos`; si los hallazgos que la 03-05 «confirma en producción» pasan a «Resuelto»; cómo cuenta el respaldo del 2026-11-18 en la retención local (`respaldo.md`, sección 5: no es semanal ni previo a un despliegue).
- **Riesgo:** AUD-05-010 es un defecto vivo en producción y el cliente ya lo sufrió. Medida provisional, inferida y no probada: abrir `/pagos/ingresar/` sin pedido elegido y escogerlo en el selector, que no usa el campo oculto.
- **Riesgo:** sin lecturas programadas (RDA-021), un problema de los días siguientes a un despliegue se verá solo si el usuario lo reporta o si se hace una lectura a demanda.
- **Riesgo:** la lectura anticipada cubre 38 h 34 min y el día 0 fue de noche y sin tráfico en `/pedidos/nuevo/`; el criterio (iii) se puso a prueba con 11 pedidos nuevos.

## Lo que no pude ver ni verificar

- **Todo el servidor y los registros:** no vi ninguna salida de las lecturas, de `manage-bde`, del refresco ni de la verificación del respaldo. Lo informado es dicho por el desarrollador.
- **No informado:** conteo por nivel, horas y rutas de los `ERROR`; reinicios de uWSGI; `POST /pedidos/nuevo/` por código y 302 de `access.log`; cuántas respuestas traían `response-time=` y el máximo global; si hubo otras respuestas de más de 2 s; sesiones; código de salida de la verificación del respaldo; paridad del refresco; día y hora del «no se guardó» del cliente; si el informe C2 separó la recarga de `R`.
- **Que ambos defectos sean iguales en `v0.3-doble-envio`:** dicho, no verificado. Las dos causas salen de lectura de código, sin ejecutar ni medir (la cuenta de «del orden de mil consultas» es calculada).
- **El respaldo, el volcado y la copia vieja de D::** no los abrí ni los leí (`AGENTS.md`, sección 6).

## Commit sugerido

`Épica 3 - Iteración 03-05: cierra la 03-05 y la Épica 03, acepta la RDA-021 (sin esperas), cierra AUD-05-002 y registra AUD-05-010 y AUD-05-011; solo documentos`
