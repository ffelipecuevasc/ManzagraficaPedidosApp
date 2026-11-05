# Bitácora 03-04 · Redacción de la iteración

- **Fecha:** 2026-11-04
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** En revisión (la redacción). La iteración 03-04 queda «Pendiente (redactada)»: no se ejecutó. La Épica 03 no cambia de estado. Solo documentos: sin cambios de código, de pruebas ni de plantillas.

## Resumen

Se redactó la iteración 03-04 · Contrato de error hacia el usuario con evidencia leída en `views.py`, las plantillas, `index.js`, las pruebas y la planificación. Cubre el alcance 4 y 6 de la épica: mensajes de error, conservación del formulario, token de envío único, bloqueo del botón y la regresión R21. R18 (AUD-02-027) no está: se resolvió en la 03-03. Deja diez decisiones `PENDIENTE_DESARROLLADOR`, cada una con opciones, ventajas, riesgos y una recomendada, sin decidir.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `10_epicas/epica-03-integridad-transaccional/iteracion-03-04-contrato-de-error-hacia-el-usuario.md` | Nuevo: iteración con estado «Pendiente (redactada)». |
| `99_bitacora/epica-03-integridad-transaccional/bitacora-03-04-redaccion.md` | Esta bitácora (nueva). |
| `00_producto/registro-pendientes.md` | Fila 03-04 «Pendiente (redactada)» con enlaces; «Próximo hito»; fila de decisiones de la 03-04 en la sección 3 (y la existente del token, tachada y reemplazada); actualización de la observación de mensajes y dos propuestas en la sección 4; una entrada de historial. |

No se tocaron `definicion-epica-03.md`, `auditoria-tecnica.md`, `decisiones.md`, `plan-de-trabajo.md`, `pruebas.md` ni ningún documento protegido.

## Verificación

Evidencia leída (solo lectura): no se ejecutó nada, ni pruebas, ni `docker`, ni `mysql`, ni `manage.py`.

- **Planificación:** `definicion-epica-03.md`, `iteracion-03-03` completa, `bitacora-03-03-cierre`, `-redaccion` y `-medicion`, `registro-pendientes.md`, `plan-de-trabajo.md:317-371`, `auditoria-tecnica.md` (AUD-02-006, AUD-02-027, AUD-04-001, AUD-01-002), `decisiones.md` (RDA-013 y RDA-019), `docs/operacion/pruebas.md` (secciones 7 y 7.1), `docs/operacion/despliegue.md` (filtros de `server.log`), `DESIGN.md` completo.
- **Código:** `views.py:150-302` (pedidos), `:588-640` (clientes y API), `:730-929` (cotizaciones y conversión), `:990-1065` (productos y API), `:1095-1211` (respaldo y restauración), `:1360-1483` (pagos), `:1585-1593` (errores); `index.js:215-304`, `:405-427`, `:625-699`; `pedido_form.html`, `cotizacion_convertir.html`, `restaurar_bd.html`, `500.html`, `base.html:258-266`; `test_capturas_amplias.py`, `test_errores.py`, `test_fronteras_transaccionales.py:50-71`.
- **Búsquedas:** `message` en `pedidos/templates` y `index.js` (una sola plantilla); `<form` en todas las plantillas (inventario de la iteración); `animate-pulse` y `text-red-500` en plantillas; `R21` en el repositorio; `ruta=` y `server.log` en `docs/operacion/`.
- **Django 6.0.1 instalado** (lectura de `django.conf.global_settings` y de `SessionMiddleware.process_response`): sesión en base de datos con 14 días, almacenamiento de mensajes `FallbackStorage`, vista `csrf_failure` por defecto, y la sesión **no se guarda en respuestas 5xx**.
- **Cálculo propio:** contraste de `red-500` sobre blanco, 3,76:1 (fórmula de WCAG, a mano; no medido con herramienta ni recogido en `DESIGN.md`).
- `git status --short`: solo los archivos `.md` de esta redacción.

## Hallazgos de la lectura que importan

1. **Los mensajes de Django son más invisibles de lo que se creía.** Solo `restaurar_bd.html` los recorre, y además únicamente pinta el nivel `success` (`:102-134`). Entonces **los cuatro mensajes de error de respaldo y restauración (los de la 01-09) no se ven en ninguna pantalla**; de las diez llamadas a `messages.*`, solo una se ve (la tarjeta de éxito de la restauración). Las pruebas de la 01-09 leen la cola (`get_messages`), no la pantalla, por eso pasan. Inferido por lectura; no probado en pantalla.
2. **Defecto latente (inferido):** los mensajes `success` de pagos y conversión se acumulan en la cola y se dibujarían como «¡Base de Datos Restaurada Exitosamente!» la próxima vez que un superusuario abra la restauración. Una prueba del paso 2 lo confirma o lo descarta.
3. **«Conservar el formulario» no se cumple hoy para los ítems.** El formulario de Django se conserva, pero `crear_pedido` y `crear_cotizacion` no devuelven `items_json` y las ediciones lo reemplazan por el de la base. Además el método de pago vuelve a «Efectivo» (inferido). El criterio de término de la épica sobre el pedido no se cumple todavía.
4. **El token en la sesión suma consultas por página,** y `AGENTS.md`, sección 11, manda detenerse si el número aumenta. Por eso el paso 0 mide antes y después.
5. **El token estricto choca con el despliegue:** los formularios abiertos al momento de la 03-05 no traen token (decisión 7).
6. **La sesión no se guarda en un 5xx:** un 500 no consume el token. Es una propiedad favorable de la opción A de la decisión 5.
7. **El bloqueo del botón de la 00-07 es un script en línea** y la medición de esa iteración cae el 2026-11-11; por eso la decisión 8 recomienda no tocarlo (opción C).
8. **Hay dos salidas de error fuera del contrato que no se tocan:** el JSON crudo en `index.js:254` y `:686`, y la página 403 por defecto de Django en un fallo de CSRF. Quedaron como propuestas en el registro.

## Decisiones abiertas (`PENDIENTE_DESARROLLADOR`)

| # | Tema | Recomendada |
| :- | :--- | :---------- |
| 1 | Dónde se muestran los mensajes de Django | A. Bloque común en `base.html` |
| 2 | Qué hacer con los cuatro avisos que no son de error y hoy no se ven | A. Mostrar solo los de error y consumir el resto |
| 3 | Qué pasa cuando un ítem no se puede guardar (con sub-pregunta del código de estado) | B. Capturar excepciones concretas fuera del `atomic` y devolver el formulario |
| 4 | Qué se conserva al devolver un formulario con error | A. Desde el servidor: `items_json` y método de pago |
| 5 | Mecanismo del token de envío único | A. Token en la sesión |
| 6 | Qué ve el usuario ante un envío repetido | A. Redirigir al registro ya creado, sin mensaje |
| 7 | POST sin token o con token vencido | A. Rechazar y devolver el formulario con los datos |
| 8 | Cómo se bloquea el botón | C. Función común; `pedido_form.html` queda con el script de la 00-07 |
| 9 | Mención de la carpeta `backups/` en el fallo de la restauración | A. Quitarla |
| 10 | Una iteración o dos | A. Una, con pasos ordenados |

Todas figuran en la sección 3 de `registro-pendientes.md`.

## Contradicciones y puntos a revisar (sin corregir)

1. **`DESIGN.md:102` contra RDA-013.** La sección 5 dice que la página de error lleva «un identificador del error que el usuario puede informar». RDA-013 y el alcance 4 de la épica lo descartan, y `500.html` no lo tiene. Documento protegido: la propuesta está abajo.
2. **La premisa del encargo era más optimista que la lectura.** Se dijo que los mensajes solo se muestran en `restaurar_bd.html`; la lectura de la plantilla agrega que ahí solo se muestra el nivel `success`. La iteración parte de la lectura (hallazgo 1).
3. **AUD-02-006 asigna a la 03-04 «mensaje sin detalles técnicos y error registrado».** La 01-09 ya lo hizo; lo que queda para la 03-04 es que el aviso se vea. La fila no se corrigió (no se pidió tocar la auditoría).
4. **`definicion-epica-03.md` queda desactualizado en dos líneas:** la cabecera (`:7`, «03-04 como siguiente iteración, sin redactar») y la nota del cierre de la 03-03 (`:65`, «todavía no está redactada»). No se tocó, como se pidió. El estado de la épica sigue «Pendiente».
5. **Estado «Pendiente (redactada)».** `_planificacion/README.md` (protegido) no define «Redactada». Se usó el término acordado.
6. **`pedido_form.html:34` y `cotizacion_form.html:35`:** `animate-pulse` en el aviso de error y `text-red-500` en los errores junto al campo, contra `DESIGN.md` §8 y la regla 8.17. Se resuelve en el paso 7 de la iteración, que el desarrollador debe confirmar al aprobar la redacción.
7. **Premisa de R21:** la definición habla de «dos POST idénticos». Si la decisión 7 es B (aceptar sin token), un par de POST sin token seguiría creando dos pedidos y R21 solo pasa si trae el token del GET.

### Propuesta de cambio a un documento protegido

- **Archivo y sección:** `DESIGN.md`, sección 5 «Componentes», fila «Página de error» (`:102`).
- **Texto actual:** «Mensaje comprensible, sin detalles técnicos, con un identificador del error que el usuario puede informar y un enlace al panel de control.»
- **Texto propuesto:** «Mensaje comprensible, sin detalles técnicos, que pide informar en qué pantalla estaba el usuario y a qué hora, y un enlace al panel de control. No muestra un identificador del error (RDA-013).»
- **Por qué:** RDA-013 descartó el identificador y la página de la 01-03 no lo tiene. Si no se cambia, `DESIGN.md` exige algo que la aplicación no hace y que una iteración futura podría implementar por error, contra una RDA aceptada.
- **Pendiente relacionado:** la sección 5 no tiene una fila para el aviso de Django. Cuando se resuelva la decisión 1, conviene describirlo ahí (color por nivel, foco, `role`). Se deja `PENDIENTE_DESARROLLADOR`.

## Migraciones

- Ninguna. Con la decisión 5-A tampoco habrá; con la 5-B o 5-C la iteración se detiene y se consulta.

## Commit sugerido

`Épica 3 - Iteración 03-04: redacta el contrato de error hacia el usuario con diez decisiones abiertas y la revisión de los mensajes de Django`
