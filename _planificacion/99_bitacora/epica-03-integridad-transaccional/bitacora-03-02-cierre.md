# Bitácora 03-02 · Cierre de la iteración: conteo P3, respuesta del cliente y revisión manual

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** Terminada (la 03-02). Solo documentos; sin cambios de código ni de pruebas. Los datos de este cierre los entregó el desarrollador; el agente no ejecutó consultas ni abrió la réplica.

## Resumen

Se cerró la 03-02 con tres constancias que faltaban en [bitacora-03-02](bitacora-03-02.md): el conteo de pedidos sin ítems en la réplica (evidencia P3 de AUD-02-008), la respuesta del cliente sobre si guarda pedidos sin ítems y la revisión manual de la página 500 al fallar un ítem al crear un pedido. Complementa esa bitácora, que no se edita (regla 5.4). También deja registrado un hallazgo menor ajeno a la 03-02 (AUD-05-003) y deja la 03-03 como siguiente iteración, sin redactarla.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-02-erradicacion-supresion-silenciosa.md` | Estado «Terminada (2026-11-04)»; criterios del conteo P3 y de la revisión manual marcados; cierre del `PENDIENTE_CLIENTE` en «Datos requeridos del cliente». |
| `00_producto/auditoria-tecnica.md` | Nota fechada de avance en AUD-02-008 (estado sin cambio); AUD-05-003 en la Auditoría 05. |
| `00_producto/registro-pendientes.md` | Cabecera, párrafo de épicas en curso, fila 03-02 (Terminada), fila del conteo de la sección 3 e historial. |
| `10_epicas/epica-03-integridad-transaccional/definicion-epica-03.md` | Nota fechada del avance y «Última revisión». |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-02-cierre.md` | Esta bitácora (nueva). |

## Conteos P3 en la réplica (solo lectura)

Consultas 1 a 3 de la sección «Evidencia P3» de la iteración, ejecutadas por el desarrollador el 2026-11-04 en la réplica local. Solo `SELECT` y solo agregados: sin nombres, teléfonos, correos ni montos.

| Consulta | Resultado |
| :------- | :-------- |
| 1 · pedidos | pedidos = 888 · sin_items = 126 · desde_el_primero_con_items = 38 · con_valor = 126 |
| 2 · cotizaciones | cotizaciones = 27 · sin_items = 0 |
| 3 · por mes (UTC) de los 38 | 2026-01 = 20 · 2026-02 = 8 · 2026-05 = 3 · 2026-08 = 2 · 2026-09 = 4 · 2026-10 = 1 |

- **Cuadre:** 20 + 8 + 3 + 2 + 4 + 1 = 38, igual a la consulta 1. Por resta, 126 − 38 = 88 pedidos sin ítems son anteriores al primer pedido con ítems (dato derivado, no medido por separado).
- **Con valor mayor que 0:** 126, igual al total de pedidos sin ítems: ninguno de ellos tiene valor de venta 0.
- **Cotizaciones:** 0 sin ítems de 27; en cotizaciones la réplica no muestra el síntoma.
- **Fecha de la réplica:** volcado del 2026-10-25 21:02:34, más la conversión de prueba del 2026-11-04 (último refresco registrado en `replica-local.md`). No es el estado actual de producción.

**Límites declarados:**

- «Sin ítems» **no distingue** un pedido guardado sin ítems a propósito de uno cuyo guardado de ítems falló. Es un indicio, no una medida de fallos.
- No detecta pedidos con ítems parciales (el caso de R3) ni ediciones que perdieron ítems: solo cuenta los que quedaron sin ninguno.
- La consulta 3 agrupa por mes en UTC, solo para ubicar los casos en el tiempo.
- **Pedido de prueba #910 (resuelto el 2026-11-04, decisión del desarrollador):** tiene un ítem («100 IMANES 7X6 CM», visto por el desarrollador), así que **no está entre los 126 ni entre los 38**, se haya hecho el conteo antes o después de crearlo. Es un pedido de prueba en la réplica; se limpia al refrescarla al cierre de la Épica 03 (ver «Revisión manual»). Cierra el `PENDIENTE_DESARROLLADOR` que esta bitácora había dejado.
- Se repite tras el refresco de la réplica, al cerrar la Épica 03 (decisión 4 de la iteración, AUD-05-002).

## Respuesta del cliente

- **Pregunta:** ¿el cliente crea pedidos sin ítems a propósito?
- **Respuesta (el cliente, 2026-11-04, dicha por él, transmitida por el desarrollador):** siempre guarda pedidos con al menos 1 ítem y nunca sin ítems.
- **Efecto:** cierra el `PENDIENTE_CLIENTE` de la iteración (el que solo aplicaba si el conteo era mayor que 0, y lo fue). **No se cambia el alcance ni se agrega validación.**
- **Observación, sin concluir:** la respuesta y la cifra de 38 pedidos sin ítems posteriores al primero con ítems no coinciden de forma directa. Con lo medido no se sabe cuál es la causa (el conteo no distingue las causas posibles, ver «Límites»). Queda como dato para la 03-03 y la 03-05, no como conclusión.

## Revisión manual (hecha por el desarrollador, no por el agente)

- **Entorno:** réplica local, `DEBUG=False` y `runserver --insecure`.
- **Prueba:** con `items_json` alterado para apuntar a un `producto_id` inexistente, `POST /pedidos/nuevo/` devolvió **500**. El desarrollador vio la **página 500 propia de la aplicación**, en escritorio y a 360 px (dicho por el desarrollador).
- **Traza en `django.request`:** `DoesNotExist` en `views.py:186` (`crear_pedido`). La línea 186 corresponde a `Producto.objects.get(pk=item['producto_id'])`, verificado en el código.
- **Nada a medio crear:** el último pedido siguió siendo el #910, es decir, no apareció ningún pedido nuevo. El #910 es un pedido de prueba de la réplica, con un ítem («100 IMANES 7X6 CM», visto por el desarrollador).
- **Inferencia:** que el id inexistente fuera 999999 es inferencia, no dato.
- **Primer intento sin efecto:** el primer intento no ejercitó la falla (la página reescribió el campo `items_json` antes de enviar) y dejó el pedido de prueba #910 en la réplica. Se limpia al refrescar la réplica al cierre de la Épica 03 (AUD-05-002).

## Hallazgo menor · AUD-05-003

- **Qué se vio (dicho por el desarrollador):** en local, con `DEBUG=False` y `--insecure`, las peticiones a `/assets/fonts/Inter-*.woff2` responden 404.
- **Clasificación:** Baja. Por verificar en producción. **Sin corregir y sin asignar a una iteración**; la 08-06 (tipografías e íconos autoalojados) es solo candidata, decisión del desarrollador del 2026-11-04. No se investigó la causa ni se comprobó si ocurre en producción.
- **ID:** va en la Auditoría 05 (revisiones manuales de la réplica local). Su alcance dice «iteración 03-01»; AUD-05-003 nace de la revisión de la 03-02. Se anotó en el propio hallazgo, sin reescribir el alcance.

## Verificación

- Pruebas: no se ejecutaron (sin cambios de código). Las de la 03-02 están en [bitacora-03-02](bitacora-03-02.md): 189 pruebas, `OK (expected failures=17)` en tres ejecuciones.
- No se usó `docker` ni `mysql`. Los números de la réplica los entregó el desarrollador.

## ¿Queda algo abierto de la 03-02?

Nada propio de la iteración. Lo que sigue pendiente pertenece a otras iteraciones o a la operación:

- Repetir el conteo P3 tras el refresco de la réplica (decisión 4, AUD-05-002, al cerrar la Épica 03).
- Limpieza del pedido #910 al refrescar la réplica.
- Capturas de ítems de `editar_pedido`, `crear_cotizacion` y `editar_cotizacion`, R1, R2 y R4, AUD-01-002 y AUD-01-001: 03-03.
- Mensaje al usuario y conservación del formulario: 03-04.
- El despliegue viaja con la 03-05.
- AUD-02-008 sigue «Abierto»: su estado lo decide el desarrollador.

## Decisiones tomadas

Del desarrollador, 2026-11-04:

1. El conteo P3 se registra con sus límites y la respuesta del cliente cierra el `PENDIENTE_CLIENTE`, sin cambio de alcance ni validación nueva.
2. La revisión manual se cierra con la constancia descrita arriba.
3. AUD-02-008: nota fechada de avance, sin cambiar el estado.
4. AUD-05-003: Baja, por verificar en producción, sin corregir y sin asignar (la 08-06 es candidata, no asignada).
5. La 03-03 queda como siguiente iteración, sin redactarla todavía.

Del desarrollador, 2026-11-04 (revisión posterior del cierre):

6. El nombre propio del cliente se reemplaza por «el cliente» en toda la documentación del repositorio (regla 7.4). El historial de git conserva las versiones anteriores.
7. El pedido #910 tiene un ítem y no está entre los 126 ni los 38; es un pedido de prueba de la réplica. Queda cerrado el `PENDIENTE_DESARROLLADOR`.

## Commit sugerido

`Épica 3 - Iteración 03-02: cierra la iteración con el conteo de pedidos sin ítems, la respuesta del cliente y la revisión manual, y registra AUD-05-003`
