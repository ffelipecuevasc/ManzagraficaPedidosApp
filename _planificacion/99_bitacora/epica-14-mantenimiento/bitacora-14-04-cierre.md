# Bitácora 14-04 · Cierre (RUT del cliente y folio de cotización)

- **Fecha:** 2026-11-28
- **Estado de la iteración:** **Terminada (2026-11-28) · verificada en producción.**
- **Versión en producción y destino de retroceso del despliegue siguiente:** `v14.3-rut-y-folio` (`d8be534`); previo `v4.11-csp-observacion`.
- **Alcance de este cierre:** solo documentos. Sin código, commit, etiqueta ni consultas a bases. No se empezó la 14-05 ni otra iteración.
- **Rótulos:** **[doc]** documento; **[consola]** salida informada por el desarrollador; **[dicho]** dicho por el desarrollador, sin salida; **[inferido]** conclusión no comprobada.
- **Bitácoras anteriores:** [bitacora-14-04](bitacora-14-04.md) (redacción), [bitacora-14-04-analisis](bitacora-14-04-analisis.md) y [bitacora-14-04-implementacion](bitacora-14-04-implementacion.md) (implementación, ensayo y despliegue).

## Qué se hizo

| Fecha | Paso | Resultado |
| :---- | :--- | :-------- |
| 2026-11-20 | Redacción y decisiones D1 a D6; opción C para el folio | [doc] |
| 2026-11-27 | Análisis: AUD-05-026 comprobado (Media, va después), avisos 1 (A) y 2 (C), H2 al alcance, AUD-05-031 nuevo | [doc] |
| 2026-11-27 | Implementación: validador y normalización del RUT, `SecuenciaFolio` con `select_for_update`, `\|unlocalize`, paso único `fijar_inicio_folio`, verificador a 20 tablas; 39 pruebas nuevas; commit `e82c9cf` | [doc] |
| 2026-11-28 | Ensayo en la réplica: 500 pruebas en 604 s; `0010` a `0012` aplicadas; 869 y 33 con relleno; reversa de la `0011`; paso único 34 → 999 y folio 1000; negativa y nueva corrida; revisión manual 1 a 13 en escritorio y a 360 px | [consola] |
| 2026-11-28 | Despliegue: respaldo previo 19 de 19 (verificador de `v4.11`), `collectstatic`, `migrate`, paso único 34 → 999, un solo Reload a las 01:19:44, respaldo posterior 20 de 20; día 0 con folio 1000, nueva corrida 1000 → 999; integridad sin RUT vacíos ni folios en cero o repetidos; 0 errores después del uso | [consola], PDF [pantalla], resto del día 0 [dicho] |

Los ocho criterios de aceptación se cumplen; la tabla con la sección y fila de cada evidencia está en la iteración, «Resultado del cierre» [doc].

## Desviaciones

| # | Qué estaba previsto | Qué pasó | Efecto |
| :- | :------------------ | :------- | :----- |
| 1 | Cotización de validación con un cliente de prueba, borrado después (evidencia, C.3, C.4 y C.4b) | La cotización de prueba se hizo sobre un **cliente real**; la cotización se borró y el cliente se conservó, sin cambios [dicho] | Sin efecto en los datos del cliente, según lo dicho. El folio consumido se recuperó con la nueva corrida (contador 999) [consola]. Puede haber quedado un evento de creación y uno de borrado de esa cotización asociados al cliente [inferido, no revisado] |
| 2 | A2.10 con los valores exactos de la negativa y de la nueva corrida | Constan «NEGADO», la limpieza y «HECHO» sin errores; los números quedaron «no informado» [consola] | Ninguno sobre el resultado: la negativa y la nueva corrida también quedaron probadas en la base de prueba y en producción (C.4c) |
| 3 | A0, filas 3, 3b, 4 y 5 (avisos y hora) registrados antes del despliegue | Siguen «No informado» | Sin efecto observado: 0 RUT vacíos y 0 folios en cero o repetidos (C.9 a C.11) [consola]. Si los avisos se dieron, no consta |

## Lecciones

1. **La validación del día 0 con datos de prueba incluye al cliente.** La opción C del aviso 2 suponía un cliente de prueba; usar uno real deja huella en su historial aunque la cotización se borre. Para la próxima, crear el cliente de prueba antes de la cotización de validación, con un RUT sintético [doc].
2. **Pegar las salidas, no solo el resultado.** En A2.10 consta el «NEGADO» y el «HECHO», pero no los números que los acompañaban. La evidencia queda más fuerte con la línea completa (sin datos de clientes) [doc].
3. **Un paso único escrito como módulo probado** (`pedidos/paso_unico_folio.py`) se ensayó igual en la base de prueba, en la réplica y en producción, y su guarda (que mira las cotizaciones, no el contador) permitió repetirlo sin riesgo. Vale como patrón para pasos manuales futuros [inferido].
4. **El verificador de respaldos con versión fija por etiqueta** (`git show v4.11-csp-observacion:scripts/verificar_respaldo.py`) resolvió el cambio de 19 a 20 tablas sin tocar el script nuevo [consola].
5. **La búsqueda de «1000» necesita un criterio** que distinga el folio de los usos ajenos del número (A1.4): el «Esperado» se ajustó a «ninguna coincidencia que sea el folio» [doc].

## Pendientes que siguen abiertos (no se resuelven aquí)

| Pendiente | Estado | Dónde queda |
| :-------- | :----- | :---------- |
| A0, filas 3, 3b y 4: aviso al dueño (canal, día y hora), aviso de no crear clientes ni cotizaciones y respuesta del cliente a la explicación del 2026-11-27 | «No informado» en la evidencia | Registro, sección 3 |
| Regla de retroceso de la parte D (`PENDIENTE_DESARROLLADOR`, «confirmar o ajustar antes del despliegue») | **Ya no aplica:** el despliegue terminó sin retroceso. Se anota y no se decide | Evidencia, parte D; registro, sección 3 |
| Clientes antiguos con el RUT ficticio `00.000.000-0` (872 al desplegar) deben cargar su RUT real al editarse | Trabajo manual del dueño (D1 y D2); la columna RUT y el filtro «RUT por completar» siguen como propuesta del 2026-11-20 | Registro, secciones 3 y 4 |
| AUD-05-026 (Media): fecha de entrega vacía al editar un pedido; el arreglo cubre `fecha_entrega` y `fecha_emision` | Va a la 14-05, sin redactar | Auditoría; registro |
| AUD-05-031 (Baja): `Cotizacion` sin admin | Destino `PENDIENTE_DESARROLLADOR` (Épica 14 o 09) | Auditoría; registro, sección 3 |
| Orden entre la 14-05 y la Épica 05 | `PENDIENTE_DESARROLLADOR` | Registro, sección 3 |
| Renovar la web app antes del 2026-12-13 | Pendiente | Registro, próximo hito |
| No consta en producción: nombre del archivo PDF, RUT en el detalle y el texto de `git describe` tras el checkout | Cubiertos en la réplica (A2b.7) y por `rev-parse` (B3.2) | Evidencia, «Qué no consta» |

## Auditoría y decisiones

- **`auditoria-tecnica.md`: sin cambios.** La 14-04 es una mejora puntual sin AUD (iteración, «Tipo») y no resolvió ningún hallazgo. AUD-05-026 y AUD-05-031 siguen abiertos [doc].
- **`decisiones.md`: sin cambios.** No surgió una decisión nueva que cambie una regla del negocio o la arquitectura: D1 a D6 y los avisos 1 y 2 ya están amparados por la RDA-024. La lección 1 es de procedimiento: va como ajuste a la plantilla de evidencia de despliegues con datos de prueba, no como RDA [inferido].

## Archivos de este cierre

- `_planificacion/10_epicas/epica-14-mantenimiento/iteracion-14-04-rut-del-cliente-y-folio-de-cotizacion.md`: Terminada y «Resultado del cierre».
- `_planificacion/10_epicas/epica-14-mantenimiento/definicion-epica-14.md`: 14-04 Terminada y próximo hito.
- `_planificacion/10_epicas/epica-14-mantenimiento/evidencia-14-04.md`: estado y nota de la parte D.
- `_planificacion/00_producto/registro-pendientes.md`: iteración activa, sección 1, sección 3 e historial.
- Esta bitácora (nueva).
