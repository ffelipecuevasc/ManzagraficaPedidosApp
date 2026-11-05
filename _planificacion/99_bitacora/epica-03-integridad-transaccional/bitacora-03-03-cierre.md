# Bitácora 03-03 · Cierre de la iteración: revisión manual contra la réplica

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** Terminada (la 03-03). Solo documentos; sin cambios de código ni de pruebas. Todo lo que sigue lo hizo y lo dijo el desarrollador, salvo lo marcado «salida pegada», que es texto que el desarrollador pegó de la terminal o de una consulta. El agente no abrió la réplica, no usó `docker` ni `mysql`, y no repitió ninguna prueba.

## Resumen

Se cerró la 03-03 con la constancia de la revisión manual que faltaba en [bitacora-03-03](bitacora-03-03.md) (sección «Revisión manual»). Complementa esa bitácora, que no se edita (regla 5.4), y la de la [medición de consultas](bitacora-03-03-medicion.md). La Épica 03 sigue «Pendiente»: la 03-04 no está redactada.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-03-cierre.md` | Esta bitácora (nueva). |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-03-fronteras-transaccionales-por-vista.md` | Estado «Terminada (2026-11-04)»; criterio «Revisión manual hecha» marcado; enlaces al cierre y a la medición. |
| `00_producto/registro-pendientes.md` | Cabecera, párrafo de épicas en curso, fila 03-03 e historial. |
| `10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md` | Nota fechada del cierre y «Última revisión». El estado de la épica no cambia. |

## Revisión manual (hecha por el desarrollador, no por el agente)

- **Entorno:** réplica local, `DEBUG=False` y `runserver --insecure`.
- **Anchos:** escritorio y 360 px.
- **Numeración:** P1 a P8 siguen el orden en que el desarrollador entregó los resultados. No coincide uno a uno con los pasos 1 a 9 de [bitacora-03-03](bitacora-03-03.md): el paso 3 de esa bitácora (crear una cotización válida) corresponde a P3, y su paso 4, a P4.

| N.º | Prueba | Resultado (dicho por el desarrollador) |
| :-- | :----- | :------------------------------------- |
| P1 | Editar el pedido #910 con un ítem fallido | **500**. En la terminal, una línea `django.request` con la ruta `/pedido/editar/910/`, `DoesNotExist` y `views.py:268` (**salida pegada**). El #910 quedó intacto (captura). |
| P2 | Crear una cotización con un ítem fallido | **500** (`views.py:761`). La última cotización siguió siendo la #28: no apareció ninguna nueva. |
| P3 | Crear una cotización válida | Cotización #30. |
| P4 | Editar la #30 con un ítem fallido | **500** (`views.py:804`). La #30 quedó sin cambios. |
| P5 | Convertir la #30 con un abono mayor que el total y con la fecha vacía | En ambos casos, error en pantalla y nada creado. **Sin captura y sin confirmación del texto exacto del mensaje.** |
| P6 | Conversión válida de la #30 | Se creó el pedido **#912**. Repetir la conversión por reenvío y por URL directa vuelve al detalle de la cotización. Un solo pedido nuevo; sin `ERROR` en la terminal. |
| P7 | Mover el pago del #912 al #910 | Consulta de solo lectura (**salida pegada**): el #910 pasó de `PENDIENTE` a `PAGADO` y el #912, de `PARCIAL` a `PENDIENTE` (R12). Quedó **sobrepago** en el #910 (`PENDIENTE_CLIENTE`, ya registrado). |
| P8 | Crear el pedido #913 de $10.000 con un abono de $4.000 | `PARCIAL` (consulta de solo lectura, **salida pegada**) (R10). |

Verificado en el código por el agente: las líneas 268, 761 y 804 de `pedidos/views.py` son `Producto.objects.get(pk=item['producto_id'])` dentro de `editar_pedido`, `crear_cotizacion` y `editar_cotizacion`.

### Notas del desarrollador

- **#911 y #29 se consumieron en intentos revertidos.** Es una inferencia: MySQL no devuelve el número autoincremental cuando una transacción se revierte. No se comprobó por separado.
- **El paso 1 de la bitácora decía «valor de venta», pero la pantalla toma el total de los ítems.** Se cambió el precio unitario, no el valor de venta. La bitácora no se corrige (regla 5.4); queda aquí la aclaración.

### Datos de prueba que quedan en la réplica

Pedidos #910, #912 y #913 y la cotización #30. Se limpian al refrescar la réplica, al cierre de la Épica 03 (AUD-05-002). El #910 tiene ahora un pago movido desde el #912 y un sobrepago, así que ya no sirve como pedido de prueba limpio.

## Qué dice la revisión sobre los criterios de la iteración

| Criterio | Respaldo |
| :------- | :------- |
| Un ítem fallido no deja pedido ni cotización a medias, responde 500 y deja una línea `django.request` | P1, P2 y P4 (en P1 la línea se pegó; en P2 y P4 el desarrollador informa el 500 y la línea de código, sin pegar la salida). |
| Convertir dos veces crea un solo pedido y el segundo intento termina en el detalle de la cotización | P6. |
| La fecha y el abono de la conversión se validan | P5, con las reservas indicadas arriba. |
| Un pago que cambia de pedido deja ambos pedidos con el `estado_pago` correcto | P7. |
| `crear_pedido` con abono deja `PARCIAL` | P8. |

## Verificación

- Pruebas: no se ejecutaron (sin cambios de código). Las de la 03-03 están en [bitacora-03-03](bitacora-03-03.md): 220 pruebas, `OK (expected failures=9)` en tres ejecuciones.
- Consultas por vista, antes y después: [bitacora-03-03-medicion](bitacora-03-03-medicion.md).
- No se usó `docker` ni `mysql`. Los resultados de la réplica los entregó el desarrollador.

## ¿Queda algo abierto de la 03-03?

Nada propio de la iteración. Lo que sigue pendiente pertenece a otras iteraciones o a la operación:

- Redactar la 03-04 (contrato de error hacia el usuario, mensajes, conservación del formulario y envío único, R21). No se redacta aquí.
- El despliegue viaja con la 03-05.
- Repetir el conteo P3 y refrescar la réplica al cierre de la Épica 03 (AUD-05-002); eso también limpia los datos de prueba de esta revisión.
- Sobrepago, pedido de valor $0 y valor de la cotización con o sin IVA (AUD-02-014): `PENDIENTE_CLIENTE`, sin cambios.
- Los 610 de 870 `estado_pago` históricos no se reparan (decisión 6-A).
- El abono inicial que la edición descarta en silencio (decisión 8-A) y R19 (04-01) siguen fuera de alcance.

## Decisiones tomadas

Del desarrollador, 2026-11-04:

1. La revisión manual se cierra con la constancia descrita arriba y la 03-03 pasa a «Terminada».
2. El estado de la Épica 03 no cambia: sigue «Pendiente».
3. La 03-04 no se redacta todavía.

## Commit sugerido

`Épica 3 - Iteración 03-03: cierra la iteración con la revisión manual contra la réplica, la medición de consultas enlazada y los datos de prueba anotados`
