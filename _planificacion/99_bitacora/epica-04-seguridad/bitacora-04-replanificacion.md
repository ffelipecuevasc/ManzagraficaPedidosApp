# Bitácora 04 · Replanificación del 2026-11-18

- **Fecha:** 2026-11-18
- **Agente:** Claude Code (Claude Sonnet 5.5)
- **Estado final:** En revisión (solo documentos: sin código, sin commit ni push, sin pruebas ni `manage.py`)

## 1. Resumen

El desarrollador pidió, con las decisiones del 2026-11-18 (dichas por él), cuatro cosas: (1) alinear la Épica 04 con la RDA-021 (sin esperas); (2) redactar un arreglo urgente de pagos como iteración 14-01, con despliegue propio antes de la 04-01; (3) cerrar los `PENDIENTE_CLIENTE` con las 13 respuestas del cliente y proponer destinos; (4) fijar el método de gravedad y pasar la Épica 14 a «Mantenimiento», sin AWS (RDA-022). Todo está hecho en documentos. **La 14-01 queda Pendiente (redactada, decisiones abiertas D1 a D5)**; la 04-01 y la 04-10 pueden ejecutarse cuando el desarrollador lo indique, **después** de la 14-01.

Antes de escribir se comprobó con `git` qué había: árbol limpio en `a4a0f37`, sin `RDA-022`, sin archivos de la 14-01 ni de esta bitácora, y el código de `pedidos/`, `PedidosApp/` y `requirements.txt` idéntico al del commit desplegado (`7e14398`).

## 2. Archivos creados o modificados

Fin de línea conservado en cada archivo (comprobado con `git status` y un conteo de `CRLF` y `LF`: ningún archivo quedó mezclado). Sin BOM.

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-14-nube-aws/iteracion-14-01-arreglo-urgente-de-pagos.md` | **Nuevo.** La 14-01: contexto leído en el código, decisiones D1 a D5, alcance, pasos, pruebas T1 a T5, medición, aviso, verificación del mismo día, plan de retroceso, criterios y riesgos |
| `_planificacion/99_bitacora/epica-04-seguridad/bitacora-04-replanificacion.md` | **Nuevo.** Esta bitácora |
| `_planificacion/00_producto/decisiones.md` | RDA-022 (sección e índice); fila de la RDA-020 en el índice como «Propuesta» reservada; RDA-014 «reemplazada en parte»; actualización de la RDA-021 (HSTS el mismo día) |
| `_planificacion/10_epicas/epica-14-nube-aws/definicion-epica-14.md` | Reescrita: «Mantenimiento», abierta siempre, método por gravedad, iteraciones descartadas y propuestas de destino; AWS sale |
| `_planificacion/00_producto/producto.md` | Subsección «Objetivos a largo plazo» (AWS) en la sección 1; referencias a AWS y S3 de las secciones 1, 2, 3 y 6 |
| `_planificacion/00_producto/registro-pendientes.md` | Iteración activa y próximos hitos; fila 14-01 y filas descartadas; filas de la Épica 04 sin esperas; sección 2 con las 13 respuestas y seis preguntas nuevas; sección 3 y 4 al día; cuatro filas de historial |
| `_planificacion/00_producto/auditoria-tecnica.md` | AUD-05-010 y AUD-05-011: destino 14-01 (lo anterior, tachado); AUD-05-009: evaluación; cuatro notas |
| `_planificacion/10_epicas/epica-04-seguridad/definicion-epica-04.md` | Esperas tachadas y nota del 2026-11-18 (orden 14-01 → 04-01 → …); respuestas 1 y 2 |
| `_planificacion/10_epicas/epica-04-seguridad/iteracion-04-01` a `iteracion-04-10` (10 archivos) | Esperas tachadas con la nota «Superado el 2026-11-18 (RDA-021)»; 04-01: sin AUD-05-010 ni 011 y retroceso a la etiqueta de la 14-01; 04-02: D6, paso 6, criterio y riesgo de HSTS; 04-05: criterio de «tres días»; 04-06 y 04-10: respuesta 1; 04-08: mención de la RDA |
| `_planificacion/99_bitacora/epica-04-seguridad/bitacora-04-01-redaccion`, `bitacora-04-02-cierre`, `bitacora-04-cierre-redaccion`, `bitacora-04-revision-final` | Solo una nota fechada bajo el título; el texto no se editó |
| `_planificacion/10_epicas/epica-06-mantencion-respaldos/definicion-epica-06.md`, `epica-13-operacion-continua/definicion-epica-13.md` | Una frase cada una: «S3» tachado (RDA-022) |
| `docs/operacion/pruebas.md` | Secciones 8 y 9: columna `PENDIENTE_CLIENTE` con lo confirmado y lo respondido el 2026-11-18, y una nota de lectura |

**No tocados (protegidos o fuera de alcance):** `AGENTS.md`, `DESIGN.md`, `README.md` (raíz), `_planificacion/README.md`, `plan-de-trabajo.md`, todo el código y las pruebas, `.claude/`, `.git/`, los archivos de evidencia y las bitácoras de las Épicas 00 a 03.

## 3. Verificación

- `git status --short`: 23 archivos modificados y 2 nuevos, todos documentos (`.md`). Ningún archivo de código. Enlaces relativos de los 25 archivos comprobados: 0 rotos.
- Conteo de `CRLF` y `LF` por archivo: sin mezcla (`auditoria-tecnica.md`, `registro-pendientes.md` y `pruebas.md` en CRLF; el resto, en LF).
- Búsqueda de esperas sin tachar en las filas vivas del registro (secciones 1 a 4): ninguna. Quedan, sin tocar, las filas de historial y los bloques «anterior… se conserva como registro».
- Cada reemplazo de texto exigió que la frase existiera una sola vez; los que no cumplieron abortaron antes de escribir.
- Sin pruebas ni `manage.py` (instrucción): **no se verificó que la causa de AUD-05-010 sea la leída**; la primera prueba de la 14-01 lo confirma o lo desmiente.
- Datos personales: ninguno (solo ids de pedido y conteos).

## 4. Contradicciones encontradas

1. **RDA-022 ya estaba pedida dos veces.** El punto 1 decía «la siguiente RDA libre es la RDA-022: corrige la mención de la 04-08» y el punto 4 pide **escribir** la RDA-022. Con la RDA-022 escrita, la siguiente libre es la **RDA-023**: la 04-08 quedó corregida a «RDA-023» (la 020 sigue reservada para `nh3`, la 021 y la 022 están tomadas). Sin esto la 04-08 habría quedado apuntando a un número ocupado.
2. **El 14-01 reasignado choca con RDA-014**, que dice que un número sin uso no se reasigna. Es una excepción explícita de la decisión del desarrollador, escrita en la RDA-022; 14-02 y 14-03 no se reasignan. Las tres iteraciones de AWS no tenían archivo.
3. **AUD-05-011 no tenía «04-01»** en los documentos (decía «sin iteración asignada; la 05-02 candidata»). Se asignó a la 14-01. AUD-05-010 sí tenía 04-01.
4. **«Un despliegue, un propósito» en la 14-01.** Lleva un hallazgo de datos (010), uno de rendimiento (011) y el mismo defecto latente en los ids de producto. Por la decisión del desarrollador entran juntos porque tocan el mismo formulario; si algo falla, el retroceso saca los tres. Lo dejé escrito como riesgo y mantuve el propósito en una frase («el formulario de pagos y el mismo defecto de ids»). AUD-05-009 no entra en mi recomendación (D3), justamente para no agrandarlo.
5. **Bitácoras y `_planificacion/README.md` 5.4** («no se editan después de entregadas»): por tu lista incluí las bitácoras de la Épica 04 y lo hice con una **nota fechada bajo el título**, sin tocar el texto. Si prefieres que no se toquen, se quitan las cuatro notas.
6. **Documentos protegidos que quedan desalineados con la RDA-022:** `_planificacion/README.md` (sección 2.2, carpeta `epica-14-nube-aws`; sección 5.3, solo tres severidades) y `plan-de-trabajo.md` (anexo, fila «14 · Tecnología en la nube (AWS)»). No los edité; propuestas en la sección 6 y una fila de historial para el plan.
7. **HSTS el mismo día reduce una protección** que la 04-02 había diseñado (3600 s primero, para que un error durara una hora). Lo escribí en los riesgos de la 04-02: un problema que aparezca después de subir a 604800 puede durar hasta 7 días en los navegadores que ya recibieron la cabecera. «Force HTTPS» ya estaba activo (medido el 2026-10-20), lo que lo hace menos probable (inferido).
8. **Las respuestas 5 y 6 chocan en un borde:** con $0 = pagado y el sobrepago prohibido, un abono en un pedido de $0 sería un sobrepago. Hoy se acepta. Quedó como pregunta nueva.
9. **La respuesta 7 habla del tablero semanal;** el panel principal también cuenta `ENTREGADO` atrasado como crítico (`DashboardOraculoTests`). Quedó como pregunta nueva.
10. **La zona violeta no está en `DESIGN.md`:** declara verde, azul, rojo y amarillo en las variantes 50, 100, 400, 600 y 900 para los estados. `violet-800/50` y `violet-300/950` quedan fuera de esa lista: hace falta una propuesta de cambio a `DESIGN.md` si confirmas el violeta.
11. **Los comentarios `PENDIENTE_CLIENTE` de `pedidos/tests/` siguen en el código** (no toqué código). La nota de `pruebas.md` dice cuáles pruebas están confirmadas y cuáles cambian; los comentarios se actualizan en la iteración que cambie cada regla.
12. **El retroceso de la 04-01** apuntaba a «la etiqueta desplegada antes». Desde ahora esa etiqueta es la de la 14-01 (propuesta `v14.1-pagos`); lo anoté en la 04-01.
13. **«v14.1» en la etiqueta:** el formato de `despliegue.md` (`v<fase>.<correlativo>`, fase = épica) lo permite; es propuesta, no decisión.

## 5. Destinos propuestos para las respuestas del cliente (sin redactar)

Respuestas dichas por el desarrollador el 2026-11-18; el agente no habló con el cliente. Los números de iteración nuevos se fijan al redactar (14-02 y 14-03 no se reasignan).

| # | Respuesta | ¿Cambia el código actual? | Destino propuesto | Observaciones |
| :- | :-------- | :------------------------ | :---------------- | :------------ |
| 1 | Borrar los pagos con el pedido es intencional | No | Ninguna (la 04-10 sigue igual) | Se cierra la pregunta; no se replantea `PROTECT` ni anular |
| 2 | Duplicar copia ítems, no pagos | Sí (hoy no copia ni ítems ni pagos) | Épica 14, tema Pedidos, **después de la 04-01** (reescribe `duplicar_pedido`) | La prueba `test_lo_que_no_se_copia` describe lo anterior |
| 3 | Cotización neta con línea de IVA y total bruto | Sí (presentación y total; hoy `valor_total` va sin IVA) | Épica 14, tema Cotizaciones | **Requiere RDA** (cambia una regla del negocio). Abierto: qué valor pasa al pedido al convertir |
| 4 | El valor de venta distinto de la suma se mantiene | No | Ninguna | Prueba confirmada |
| 5 | $0 = pagado al 100 % | No | Ninguna | Pruebas confirmadas; ver el borde con la respuesta 6 |
| 6 | Sobrepago prohibido: avisar y repintar el formulario | Sí (hoy se acepta) | Épica 14, tema Pagos, **después de la 14-01 y no con ella** | Abierto: abono en pedido de $0 |
| 7 | `ENTREGADO` sale del tablero semanal | Sí | Épica 14, tema Tablero semanal y panel (la 07-04 es refactorización pura, RDA-015) | Abierto: ¿también del «crítico» del panel? |
| 8 | Zona sin fecha antes de la crítica, con otro color; fecha obligatoria al crear, mínimo mañana, solo al crear, hora de Chile | Sí | **Épica 10** (idea I de la 10-01, con la fecha obligatoria al crear) | Nombre «Zona Por Agendar» y violeta (`violet-800/50` claro; `violet-300/950` oscuro): **propuesta a confirmar por el desarrollador** (contraste calculado 8,19:1 y 8,25:1, no medido en pantalla; hex de la paleta de Tailwind, no verificados en el repo). Abierto: ¿rige el mínimo al duplicar y al convertir? |
| 9 | Precio original = catálogo, «editable por el dueño», aviso sobre 15 % de descuento | Sí (funcionalidad nueva) | Candado de precio, Épica 08 (con la 09-01 si solo el superusuario edita) | **Requiere RDA.** Abierto: qué significa «editable por el dueño». Contradice `pruebas.md` sección 9 («el precio lo fija el vendedor») hasta que se apruebe |
| 10 | No recuerda qué vio antes de recargar | No | Ninguna | AUD-04-002 sigue como está |
| 11 | Duplicados se borran con confirmación | No | 06-04 (consulta de solo lectura) y el borrado, que lo hace el desarrollador | **#1015 registrado** para borrar con confirmación del cliente |
| 12 | 1 usuario superusuario y módulo de gestión de usuarios | No | Épica 09 (09-02), sin iteración nueva | Faltan los dispositivos |
| 13 | Aviso del botón hecho | No | Ninguna | No consta a cuál de los avisos de la 03-05 se refiere |

## 6. Texto propuesto para los documentos protegidos (el desarrollador decide y edita)

### 6.1 `_planificacion/README.md`, sección 5.3 · gravedad «Crítica»

- **Texto actual (línea 112):** `- Severidad: Alta (bloquea la publicación o afecta al usuario o al negocio), Media (afecta calidad o rendimiento), Baja (mejora).`
- **Texto propuesto:**

  ```markdown
  - Severidad: **Crítica** (rechazo o pérdida silenciosa de datos comerciales en producción; se corrige con un arreglo urgente de despliegue propio, antes de cualquier otra iteración, RDA-022), Alta (bloquea la publicación o afecta al usuario o al negocio), Media (afecta calidad o rendimiento) y Baja (mejora). Las fallas Alta se corrigen en la siguiente iteración; las Media y Baja, en la Épica 14, agrupadas por tema.
  ```
- **Texto actual de la plantilla 6.5:** `| AUD-NN-MMM | Alta / Media / Baja | … | … | … | Abierto / Resuelto en XX-YY o RDA-XXX |`
- **Texto propuesto:** `| AUD-NN-MMM | Crítica / Alta / Media / Baja | … | … | … | Abierto / Resuelto en XX-YY o RDA-XXX |`
- **Por qué:** AUD-05-010 es el primer hallazgo Crítico y la escala no lo tiene; sin la definición, otra persona decide por su cuenta qué es «crítico» y dónde se corrige.
- **Si no se hace:** la Auditoría 05 y la RDA-022 usan «Crítica» sin respaldo en el documento de reglas, y los agentes siguen leyendo tres niveles.

### 6.2 `_planificacion/README.md`, sección 2.2 · nombre de la Épica 14 (solo si se renombra la carpeta)

- **Texto actual (línea 57):** `| 06 | `epica-06-mantencion-respaldos` | 14 | `epica-14-nube-aws` |`
- **Texto propuesto:** `| 06 | `epica-06-mantencion-respaldos` | 14 | `epica-14-mantenimiento` |`
- **Por qué:** la carpeta dice «nube-aws» y AWS salió del plan. **Si no se hace:** la carpeta confunde a quien llegue, pero nada se rompe (los enlaces usan el nombre actual). Renombrar exige mover `10_epicas/epica-14-nube-aws/` y `99_bitacora/epica-14-nube-aws/` (consulta previa) y actualizar los enlaces de este cambio.

### 6.3 `DESIGN.md` · violeta (solo si confirmas la zona «Por Agendar»)

- **Texto actual (línea 40):** «Los colores de estado (verde, azul, rojo y amarillo de Tailwind en sus variantes 50, 100, 400, 600 y 900) se usan en etiquetas de estado de pedidos y pagos. Su asignación por estado es `PENDIENTE_DESARROLLADOR`.»
- **Texto propuesto:** agregar «y violeta (variantes 50, 300, 800 y 950) para la zona de pedidos sin fecha de entrega», con el par de contraste que se mida en pantalla.
- **Si no se hace:** la zona usaría colores fuera de `DESIGN.md`, contra la regla 8.17 de `AGENTS.md`.

## 7. Lo que no vi

- **Producción:** nada. Todo lo que dice «dicho por el desarrollador» (producción en `v3.1-integridad`, el reporte del cliente, los tiempos de 2,7 a 8,0 s, las 13 respuestas del cliente, el respaldo del 2026-11-18) no está verificado por el agente.
- **La causa de AUD-05-010:** la leí en el código (`settings.py:177` y `:201`, `pago_form.html:75-84`) pero no la reproduje, y no corrí Django para ver cómo la plantilla escribe el id; está marcada como inferida en la 14-01.
- **Si hay un producto con id de 1.000 o más** (la línea base contó 55 productos y no el id mayor): sin medir.
- **Cuántos pagos se rechazaron y si el cliente los volvió a ingresar:** la aplicación no dejó rastro.
- **Que el #1015 sea un duplicado no deseado ni si tiene pagos:** solo sé que es el `pedido_duplicado` de la lectura anticipada (AUD-02-006, dicho).
- **Las etiquetas:** `git tag` me fue denegado; solo confirmé con `git rev-parse` que `v3.1-integridad` existe en el repositorio local. No listé el resto.
- **Los colores:** los hex de Tailwind (`#5B21B6`, `#F5F3FF`, `#C4B5FD`, `#2E1065`) son los que recuerdo de la paleta v3, no los leí en el repo (Tailwind aún no se compila aquí, RDA-010); los contrastes 8,19:1 y 8,25:1 salen de ellos.
- **El número de pruebas vigente:** usé 267 y `expected failures=9` (última cifra registrada, 2026-11-16); no corrí la suite.
- **Documentos que no releí completos:** las bitácoras y evidencias de las Épicas 00 a 03 (solo busqué las esperas y los `PENDIENTE_CLIENTE`) y las 10 iteraciones de la Épica 04 fuera de las líneas editadas.

## 8. Decisiones por tomar (desarrollador)

1. **14-01, D1 a D5** (recomendadas primero): `unlocalize` para el id; `select_related('cliente')`; AUD-05-009 **no** entra; texto del aviso de pedido no válido; aviso provisional al cliente (que puedes enviar ahora, sin esperar el despliegue).
2. **Etiqueta, fecha y ventana de la 14-01** (propuesta `v14.1-pagos`), texto literal del aviso y vigencia del protocolo de pedido y pago de prueba.
3. **Editar `_planificacion/README.md`** (6.1 y, si renombras, 6.2) y decidir si se renombra la carpeta de la Épica 14.
4. **Confirmar los destinos de la sección 5** y la zona «Por Agendar» y su color.
5. **Épica 14:** a dónde va la copia fuera del servidor sin AWS; cuándo se ejecutan las iteraciones Media y Baja; si las fallas ya asignadas a la Épica 08 u otras pasan a la 14; si una falla Alta se numera en la 14 o en la épica de su tema.
6. **Cuatro preguntas nuevas para el cliente** (sección 2 del registro): valor al convertir una cotización neta; abono en un pedido de $0; `ENTREGADO` en el panel principal y mínimo «mañana» al duplicar o convertir; significado de «editable por el dueño». Más la de los pagos que no se guardaron.
7. **#1015:** la confirmación explícita del cliente para borrarlo, y que se haga después de la 04-10 y con un respaldo verificado.
8. Sin respuesta: si existe una espera de **5 días** y dónde (la RDA-021 no la encontró; tampoco la encontré en la Épica 04).

## 9. Criterios de aceptación

- [x] Esperas de la RDA-021 tachadas, sin borrar, en la definición, las diez iteraciones y cuatro bitácoras de la Épica 04 (búsqueda de la sección 3).
- [x] HSTS de la 04-02: segundo escalón el mismo día, dos despliegues (D6, paso 6, criterio de término y riesgo).
- [x] 04-08 corregida (RDA-023 como siguiente libre) y 04-01 y 04-10 listas para ejecutarse.
- [x] 14-01 redactada, Pendiente, con pruebas, retroceso, verificación del mismo día y aviso; evalúa AUD-05-009 como decisión (D3); destinos de AUD-05-010 y 011 cambiados a «14-01» y quitados de la 04-01.
- [x] #1015 registrado para borrar con confirmación del cliente.
- [x] 13 respuestas del cliente cerradas, pruebas marcadas en `pruebas.md` y destinos propuestos sin redactar; zona «Por Agendar» registrada como propuesta.
- [x] RDA-022 escrita; Épica 14 «Mantenimiento, abierta siempre»; AWS en `producto.md`, sección 1, «Objetivos a largo plazo»; respaldo fuera del servidor en la Épica 14.
- [x] Texto propuesto para la gravedad «Crítica» redactado, sin editar el README.
- [ ] Nada de esto está desplegado ni probado: es planificación; la 14-01 y la 04-01 siguen sin ejecutar.

## 10. Commit sugerido (157 caracteres)

`Épica 14 - Iteración 14-01: redacta el arreglo urgente de pagos (RDA-022), alinea la Épica 04 con la RDA-021 y cierra respuestas del cliente; solo documentos`
