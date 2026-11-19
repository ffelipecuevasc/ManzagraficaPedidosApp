# Épica 14 · Mantenimiento

- **Estado:** Abierta siempre (RDA-022). Nunca se marca Terminada: se cierran sus iteraciones, no la épica.
- **Fase del plan:** no existe en el plan original; anexo del plan del 2026-10-27 (RDA-014), donde era «Tecnología en la nube (AWS)». **Desde el 2026-11-18 (RDA-022) es «Mantenimiento» y AWS sale del plan** (ver «Qué salió de la épica»). La carpeta se llamó `epica-14-nube-aws` hasta el 2026-11-18, cuando se renombró a `epica-14-mantenimiento` en `10_epicas` y en `99_bitacora` (aprobado por el desarrollador).
- **Objetivo:** que las fallas se corrijan según su gravedad y no queden sin dueño: los arreglos urgentes con despliegue propio, las fallas Media y Baja agrupadas por tema y el respaldo fuera del servidor.
- **Precondición:** ninguna. La 14-01 se ejecuta y se despliega **antes** de la 04-01 (decisión del desarrollador, 2026-11-18).
- **Última revisión:** 2026-11-18 (reescrita por RDA-022; antes, creada el 2026-10-27 a pedido del desarrollador).

## Cómo funciona (RDA-022)

| Gravedad | Qué es | Dónde y cuándo se corrige |
| :------- | :----- | :------------------------ |
| **Crítica** | Rechazo o pérdida silenciosa de datos comerciales en producción | **Arreglo urgente**: una iteración propia con despliegue propio, antes de cualquier otra iteración pendiente, sin mezclar otros propósitos. Se numera aquí |
| **Alta** | La definición vigente de `_planificacion/README.md`, sección 5.3 | La siguiente iteración que se ejecute |
| **Media** y **Baja** | Las definiciones vigentes de la sección 5.3 | Esta épica, agrupadas por tema |

- **Una iteración, un propósito (RDA-007).** Una iteración de mantenimiento reúne las fallas de **un** tema; si dos fallas no comparten tema, van en iteraciones y despliegues distintos.
- **Cada arreglo escribe antes la prueba que falla** (`AGENTS.md`, sección 8, regla 15) y trae su plan de retroceso y su verificación del mismo día (RDA-021).
- **Lo que ya está asignado a otra épica se queda ahí** hasta que el desarrollador lo mueva (por ejemplo, AUD-05-001 y AUD-05-005 a AUD-05-008, a la Épica 08): `PENDIENTE_DESARROLLADOR`. Hoy no hay ninguna falla Media o Baja movida a esta épica.
- **Cuándo se ejecutan las iteraciones de Media y Baja** (entre épicas, al cerrar cada una o al final del plan): `PENDIENTE_DESARROLLADOR`.

## Iteraciones

| Iteración | Nombre | Estado |
| :-------- | :----- | :----- |
| 14-01 | [Arreglo urgente de pagos](iteracion-14-01-arreglo-urgente-de-pagos.md): AUD-05-010 (Crítica) y AUD-05-011 (Alta); AUD-05-009 no entró (D3 A) | **Terminada (2026-11-18): verificada en producción**, `v14.1-pagos` |
| 14-02 | [Copiar los ítems al duplicar un pedido](iteracion-14-02-copiar-items-al-duplicar.md): AUD-05-012 (Alta) | ~~Implementada, pendiente de revisión manual y despliegue (2026-11-19)~~ **Terminada · verificada en producción el 2026-11-19** (`v14.2-duplicar-items`, `068be10`); D1 a D4 resueltas ([bitacora-14-02](../../99_bitacora/epica-14-mantenimiento/bitacora-14-02.md)). Número reasignado el 2026-11-18 por decisión del desarrollador, segunda excepción explícita a la RDA-022, punto 4 |
| ~~14-02 (anterior)~~ | ~~Respaldo de la base en S3~~ | **Descartada** (RDA-022). El número 14-02 se reasignó a AUD-05-012 |
| ~~14-03~~ | ~~Restauración ensayada desde S3~~ | **Descartada** (RDA-022). El número no se reasigna |
| ~~14-01 (anterior)~~ | ~~Cuenta de AWS y seguridad~~ | **Descartada** (RDA-022). El número 14-01 se reasignó al arreglo de pagos por decisión del desarrollador; esta iteración nunca tuvo archivo |

### Propuestas de destino, sin redactar (2026-11-18)

Salen de las respuestas del cliente (registro, sección 2). Son **propuestas**: el desarrollador confirma el destino y el número se fija al redactar cada una (el 14-02 quedó para AUD-05-012 y el 14-03 no se reasigna, así que las nuevas parten en 14-04). Las que cambian una regla del negocio necesitan una RDA aprobada antes de redactarse (`AGENTS.md`, sección 1).

| Tema | Qué | Origen | Gravedad |
| :--- | :-- | :----- | :------- |
| Pagos | No permitir el sobrepago: avisar y repintar el formulario (pago, edición del pago y abono inicial) | Respuesta 6 | `PENDIENTE_DESARROLLADOR`; va después de la 14-01, no con ella |
| Pedidos | Al duplicar un pedido, copiar los ítems (no los pagos) | Respuesta 2 | `PENDIENTE_DESARROLLADOR`; después de la 04-01, que reescribe `duplicar_pedido` |
| Tablero semanal y panel | Sacar los pedidos `ENTREGADO` del tablero semanal (si también salen de «crítico» del panel principal: `PENDIENTE_CLIENTE`) | Respuesta 7 | `PENDIENTE_DESARROLLADOR` |
| Cotizaciones | Cotización neta con línea de IVA y total bruto, como una factura chilena | Respuesta 3 | Cambia una regla del negocio: requiere RDA |
| Respaldos | Copia de los respaldos y de `media/` fuera del servidor (AUD-02-023, AUD-02-024) | RDA-022 | Media; destino de la copia sin S3: `PENDIENTE_DESARROLLADOR` |

El resto de las respuestas (8, 9 y 12) tiene destino fuera de esta épica: ver el registro.

## Qué salió de la épica (AWS)

La definición anterior (2026-10-27) proponía sacar los respaldos a Amazon S3 en una cuenta de AWS del negocio (14-01 cuenta y seguridad, 14-02 respaldo en S3, 14-03 restauración ensayada). **El desarrollador sacó AWS del plan el 2026-11-18 (RDA-022).** Pasa a «Objetivos a largo plazo» de `producto.md`, sección 1, con el contexto de la definición anterior (la viabilidad con la lista blanca, el costo y las condiciones de seguridad). Si algún día se retoma, se conversa primero con el cliente y se redacta de nuevo, con su RDA.

Siguen vigentes dos hallazgos que ese plan resolvía y que ahora quedan en esta épica sin destino técnico definido: AUD-02-023 (las imágenes de `media/` no tienen copia) y AUD-02-024 (el respaldo de emergencia de la restauración vive en el mismo disco que la base). Mientras tanto, la protección es la descarga manual del protocolo de la 00-02 (`docs/operacion/respaldo.md`).

## Decisiones de la épica

- 2026-11-18 · Gravedad, destino de cada falla y «Mantenimiento, abierta siempre»: RDA-022.
- A dónde va la copia fuera del servidor ahora que AWS salió: `PENDIENTE_DESARROLLADOR`.
- Si las fallas ya asignadas a otras épicas se mueven aquí: `PENDIENTE_DESARROLLADOR`.
- 2026-10-27 · Sin aprendizaje automático en la nube (RDA-018). Sigue vigente, sin nube.

## Fuera de alcance

- Funcionalidades nuevas del negocio sin una RDA aprobada.
- Cambiar de hosting o mover la base de datos a la nube.
- Servicios de aprendizaje automático (RDA-018).

## Criterio de término

Ninguno: la épica queda abierta. Cada iteración trae sus propios criterios de aceptación.

## Notas

- **2026-10-27:** creada a pedido del desarrollador, que pidió sacar de la Épica 06 todo lo de S3 y reunir lo de AWS al final del plan.
- **2026-11-18:** RDA-022. La épica pasa a «Mantenimiento», abierta siempre; AWS sale a `producto.md`; la 14-01 pasa a ser el arreglo urgente de pagos ([bitacora-04-replanificacion](../../99_bitacora/epica-04-seguridad/bitacora-04-replanificacion.md)).
