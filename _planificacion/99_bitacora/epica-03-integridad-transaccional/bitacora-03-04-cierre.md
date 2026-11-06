# Bitácora 03-04 · Cierre de la iteración

- **Fecha:** 2026-11-06
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** Terminada (la 03-04), con la excepción declarada de la presentación de dos avisos (AUD-05-006 y AUD-05-007, Épica 08). Solo documentos; **sin cambios de código ni de pruebas**. La revisión manual la hizo y la dijo el desarrollador: el agente no la repitió ni la verificó. Lo único que el agente midió en esta tarea es la verificación del punto «Verificación a posteriori» (más abajo).

## Resumen

Se cierra la 03-04 con la constancia de la revisión manual del desarrollador, que complementa [bitacora-03-04](bitacora-03-04.md), [bitacora-03-04-revision-servidor](bitacora-03-04-revision-servidor.md) y [bitacora-03-04-correccion-abono](bitacora-03-04-correccion-abono.md) (no se editan: regla 5.4). Los defectos menores que salieron de esa revisión se registran como AUD-05-005 a AUD-05-008, a resolver en la Épica 08, junto con una decisión del desarrollador sobre el aviso nativo del navegador y una propuesta (candado de precio) que no se implementa. Además se verificó a posteriori que, con el token de envío único apagado, fallan R21 y la prueba de la línea `INFO` del rechazo, y se suavizó el texto de `despliegue.md`, sección 3.9, sobre esa línea.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-cierre.md` | Esta bitácora (nueva). |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-04-contrato-de-error-hacia-el-usuario.md` | Estado «Terminada (2026-11-06)»; criterio «Revisión manual hecha» marcado; paso 11 con las dos líneas de error; nota fechada del cierre. |
| `00_producto/auditoria-tecnica.md` | AUD-05-005 a AUD-05-008 en la Auditoría 05 y «Notas de la Auditoría 05 · 2026-11-06» (origen, decisión del aviso nativo, seguimiento de AUD-04-001). |
| `00_producto/registro-pendientes.md` | Cabecera, párrafo de épicas en curso, fila 03-04, decisiones pendientes de la Épica 08, propuesta del candado de precio e historial. |
| `docs/operacion/despliegue.md` | Sección 3.9: la línea `INFO` del formulario vencido queda «por verificar en producción (03-05)». |
| `docs/operacion/pruebas.md` | Sección 9.1: la verificación a posteriori del token y la nota sobre las pruebas que comparan el aviso de ítem fallido. |

No se tocaron `DESIGN.md`, `README.md`, `AGENTS.md`, `index.js`, plantillas, vistas ni pruebas.

## Revisión manual (hecha por el desarrollador, no por el agente)

- **Entorno y fecha:** réplica local, 2026-11-06. Dato dicho por el desarrollador; el agente no lo verificó.
- **Resultado:** pasos 1 a 6 y 8 a 12 de la «Revisión manual» de la iteración, **OK**. El paso 7 (envío repetido contra el servidor) lo cubrió la [revisión de servidor](bitacora-03-04-revision-servidor.md) (comprobación 7).
- **Aclaración del paso 11 (página 500):** en la terminal de `runserver` salen **dos** líneas de error: una de `django.request`, con la traza, el método, la ruta y el usuario, y otra de `django.server`, con el acceso (500). Coincide con lo ya documentado: `django.server` existe solo en `runserver` ([bitacora-01-02](../epica-01-observabilidad/bitacora-01-02.md), [bitacora-01-05](../epica-01-observabilidad/bitacora-01-05.md)) y su `LOGGING` local solo muestra de él las respuestas de nivel `ERROR`. En PythonAnywhere queda únicamente la línea de `django.request`. La redacción del paso 11 decía «una línea»; se aclaró en la iteración.
- **Observaciones del desarrollador** (no son fallos de los pasos; se registran como hallazgos menores):
  - la cantidad parte en 0 y no se borra al escribir, en crear y editar pedido y cotización → AUD-05-005;
  - el ícono y el texto del aviso rojo quedan desalineados → AUD-05-006;
  - el aviso de ítem fallido es un párrafo sin estructura → AUD-05-007;
  - `animate-pulse` y `text-red-500` en tres plantillas, y `from PedidosApp import settings` en `views.py` → AUD-05-008.
- **Decisión del desarrollador, sin hallazgo:** se deja el aviso nativo del navegador «Completa este campo» en los campos obligatorios.

## Verificación a posteriori (medida por el agente, 2026-11-06)

Cierra la desviación 1 de la regla 15 que la iteración declaró para la prueba de la línea `INFO` del rechazo (se había escrito junto con su código, no antes; las demás pruebas del token ya se habían verificado apagando el mecanismo).

- **Método:** se apagó el mecanismo en **un solo punto**, `envio_unico.estado`, que devuelve siempre «nuevo» (la verificación del 2026-11-04 había apagado el token en las tres vistas). Con una copia previa del archivo en la carpeta temporal de la sesión y su SHA-256 anotado.
- **Prueba de la línea `INFO` del rechazo** (`test_envio_unico.EnvioSinTokenValidoTests.test_el_rechazo_deja_una_linea_info_sin_el_contenido_del_formulario`): **falla**, `AssertionError: no logs of level INFO or higher triggered on pedidos.views`. Es la razón correcta: sin el mecanismo nadie rechaza el envío, así que no hay línea.
- **R21** (`test_regresiones.EnvioUnicoTests.test_r21_dos_post_identicos_crean_un_solo_pedido`): **falla**, `AssertionError: 2 != 1` (dos pedidos en vez de uno).
- **Módulo `test_envio_unico` completo, con el mecanismo apagado:** 20 pruebas, 14 fallos y 2 errores (la causa de los dos errores no se inspeccionó). Es lo esperado: con el mecanismo apagado no se rechaza nada y un envío repetido crea un segundo registro.
- **Restauración:** se copió el archivo original. El SHA-256 de `pedidos/envio_unico.py` es idéntico al de antes (`a48b15503b9c…`), `git diff` no muestra cambios en el archivo y `git status` quedó limpio. Con el código restaurado, `test_envio_unico` y R21: **21 pruebas, `OK`**.
- **No se repitió la suite completa:** no hay cambios de código desde la última medición (267 pruebas, `OK (expected failures=9)` en tres ejecuciones, en [bitacora-03-04-correccion-abono](bitacora-03-04-correccion-abono.md)).
- Se borró la copia temporal.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Revisión manual hecha por el desarrollador (2026-11-06; dato dicho por él): pasos 1 a 6 y 8 a 12 OK; el 7 lo cubrió la revisión de servidor. **Excepción:** la presentación del aviso rojo (AUD-05-006) y del aviso de ítem fallido (AUD-05-007), a resolver en la Épica 08.
- [x] R21 y la prueba de la línea `INFO` fallan con el mecanismo apagado y pasan con él (sección anterior).
- [x] AUD-04-001, **solo la parte de servidor**, queda «Resuelto en 03-04» con pruebas verdes (267, `OK (expected failures=9)`); el hallazgo sigue **Abierto** por la medición de `access.log` (03-05), la consulta de duplicados históricos (06-04) y el indicador de carga (08-07). No se aplicó «Resuelto en 03-04» a ningún otro hallazgo (AUD-02-006 y AUD-02-008 siguen con su nota de avance).
- [x] Código y pruebas sin cambios en esta tarea (`git status` solo con documentos).
- [ ] Despliegue y vigilancia: 03-05.

## Decisiones tomadas

- **«Terminada» con excepción.** La iteración se declara Terminada porque lo que pedían sus criterios se cumple; b y c (AUD-05-006 y AUD-05-007) son de presentación de avisos que esta misma iteración creó, y el desarrollador los difiere a la Épica 08. Constan en la iteración, en el registro y en la auditoría.
- **Propuesta, no hallazgo: candado de precio** (Épica 08), registrada en `registro-pendientes.md`, sección 4. No se implementa. Ver «Pendientes y riesgos».
- **Aviso nativo «Completa este campo»:** se deja (decisión del desarrollador). No se registra como hallazgo.
- **`despliegue.md`, sección 3.9:** la línea `INFO` del formulario vencido pasa de afirmada a «por verificar en producción (03-05)». Localmente sí sale (revisión de servidor, comprobación 9); en producción no se ha visto.

## Pendientes y riesgos

- **Contradicciones y dudas (no corregidas):**
  1. **AUD-05-005 contra la lectura del código.** El desarrollador dice que la cantidad parte en 0. El campo de alta del ítem se declara con `value="1"` (`pedido_form.html:164`, `cotizacion_form.html:160`) y `index.js:438` lo repone a 1 al agregar. No se encontró dónde parte en 0. Se registró lo dicho y la discrepancia; falta reproducirlo y ubicar el campo exacto.
  2. **«Terminada» con avisos desalineados.** El paso 12 («los avisos se leen bien») se dio por OK y, a la vez, se observó el desalineado (AUD-05-006). Se resolvió tratándolo como observación de pulido, no como fallo del criterio. Si el desarrollador lo ve de otro modo, la iteración volvería a «En revisión».
  3. **Candado de precio.** (a) Es funcionalidad nueva, y `AGENTS.md` (sección 1) pide una RDA aprobada antes de implementarla. (b) `pruebas.md`, sección 9, fija como regla confirmada que el precio lo fija el vendedor y prohíbe validarlo contra el catálogo o recalcularlo en el servidor sin consultar. El candado propuesto es de interfaz y deja que el servidor guarde el precio que llega, así que no la contradice, pero cambia cómo se escribe. (c) El desarrollador dice que ya se consultó al cliente, **sin detalle**: no consta qué se preguntó ni qué respondió; no se registra como confirmado. Preguntas abiertas: qué es el «precio original» al editar un pedido (el del catálogo hoy o el que quedó guardado) y si basta un aviso por porcentaje de descuento (y con qué umbral).
  4. **Fuera del pedido:** `definicion-epica-03.md` conserva «Última revisión» con la 03-04 «En revisión». No se tocó (no se pidió). El registro prevalece.
- **AUD-05-008, alcance de la búsqueda.** La búsqueda de `animate-pulse` y `text-red-500` encuentra 38 coincidencias en 19 plantillas; se registraron las tres que nombró el desarrollador (`dashboard.html`, `trabajo_semanal.html`, `producto_confirm_delete.html`). Las demás no se evaluaron.
- **AUD-05-007 y las pruebas.** Tres pruebas afirman el aviso de ítem fallido con `assertContains` sobre el texto completo (`test_fronteras_transaccionales.py:83`, `test_pedidos.py:215`, `test_contrato_error.py:173`). Si la Épica 08 parte el texto en varios elementos, hay que ajustarlas en la misma iteración.
- **AUD-05-002** (disco de Docker en C:) sigue pendiente de Operación al cerrar la Épica 03; los datos de prueba de la 03-04 se limpian con ese refresco.
- **Siguiente:** 03-05 (validación y despliegue). No se empezó.

## Commit sugerido

`Épica 3 - Iteración 03-04: cierra la iteración con la revisión manual, registra AUD-05-005 a AUD-05-008 y la propuesta del candado de precio; solo documentos`
