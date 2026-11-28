# Bitácora 14-04 · Análisis previo a la implementación

- **Fecha:** 2026-11-27
- **Estado de la iteración:** Pendiente (redactada, análisis hecho). **Solo análisis y documentos:** ningún cambio de código, migración, commit, etiqueta ni despliegue. Nada se ejecutó contra la réplica ni producción.
- **Commit base:** `e670cef` (`main`; sin cambios salvo `evidencia-14-04.md`, sin versionar).
- **Rótulos:** **[doc]** lo dice un documento; **[código]** leído en el código; **[prueba]** salió de la prueba efímera; **[dicho]** lo informó el desarrollador; **[inferido]** conclusión mía, no comprobada.

## 1. AUD-05-026: fecha de entrega al editar un pedido

**Método.** Prueba efímera en la base de prueba (`test_…` del MySQL local), guardada fuera del repositorio y ejecutada con `manage.py test <carpeta temporal>`. Abre el formulario de edición con el cliente de pruebas de Django, toma el `value` que pinta cada campo, le aplica la regla del estándar HTML para `<input type="date">` (un valor que no es `aaaa-mm-dd` se reemplaza por cadena vacía) y envía el formulario completo sin tocar la fecha. Fecha de prueba: 2026-12-15. Resultado: 3 pruebas, OK.

| Caso | Valor pintado | Enviado | Resultado |
| :--- | :------------ | :------ | :-------- |
| (a) `PedidoForm.fecha_entrega` (`forms.py:97`) | `15/12/2026` [prueba] | `''` [prueba, navegador emulado] | — |
| (b) POST de edición del pedido | — | `''` | 302 y **`fecha_entrega = None`**: se pierde sin aviso [prueba] |
| (c) `CotizacionForm.fecha_emision` (`forms.py:69`), widget | `15/12/2026` [prueba] | — | — |
| (c) Formulario real de cotización | `2026-12-15`: la plantilla no usa el widget; escribe el campo a mano con `\|date:'Y-m-d'`, `type="text"` y `readonly` (`cotizacion_form.html:328-334`) [código, prueba] | `2026-12-15` | 302 y la fecha se conserva [prueba] |
| Control: «Reabrir» (`forms.py:203`) | `2026-12-15` [prueba] | — | Correcto (trae `format='%Y-%m-%d'`) |

**Conclusión.** En pedidos la fecha **se pierde** al guardar sin tocarla: rechazo o pérdida silenciosa de un dato comercial, la definición de **Crítica** de la RDA-022 → **arreglo urgente con despliegue propio, antes de la 14-04** [inferido de la regla; la gravedad la fija el desarrollador]. En cotizaciones **no** se pierde hoy: el widget sigue mal configurado, pero la plantilla lo esquiva (riesgo latente si alguien pasa a `{{ form.fecha_emision }}`).

**Salvedades.** La parte del navegador está emulada, no observada; coincide con el aviso de consola y el campo vacío dichos en la revisión de la 04-09 [dicho]. No se midió si ya ocurrió en producción: la consulta 3.5 da una cota (pedidos sin fecha con al menos una edición registrada), no la prueba.

**Arreglo propuesto (para su propia iteración):** `format='%Y-%m-%d'` en los widgets de `forms.py:69` y `forms.py:97`, con prueba que falle antes; número libre: **14-05** (el 14-03 no se reasigna).

## 2. Código frente a la iteración

### Archivos que cambiarían

`pedidos/models.py`, `pedidos/validadores.py` (nuevo), `pedidos/forms.py`, `pedidos/admin.py`, `pedidos/views.py`, migraciones `0010` a `0012`, `pedidos/templates/pedidos/cotizacion_{list,detail,form,pdf,convertir,confirm_delete}.html`, **`pedido_form.html`** (no figura en la iteración; ver hallazgo H2), `cliente_form.html` (no necesita cambios: recorre `{% for field in form %}` [código]), `pedidos/static/pedidos/js/index.js`, `pedidos/tests/factorias.py` (H5), `scripts/verificar_respaldo.py` y sus pruebas, `docs/operacion/despliegue.md` y `respaldo.md`, pruebas nuevas.

### Caminos que crean o editan un `Cliente`

| Camino | Dónde | Cómo queda cubierto |
| :----- | :---- | :------------------ |
| Crear cliente | `views.py:715-719` (`ClienteForm`, `fields='__all__'`) | Validador del modelo [código] |
| Editar cliente | `views.py:727-732` | Ídem; el ficticio bloquea guardar (D2) |
| Modal de cliente rápido | `views.py:759-762` (`api_crear_cliente_rapido`) | Validador del modelo; **pero el modal es HTML escrito a mano** en `pedido_form.html:96` y `cotizacion_form.html:95`, e `index.js:216-239` solo envía `nombre`, `telefono` y `email` [código]. Sin cambiar los dos modales y `index.js`, el modal queda siempre rechazado |
| Admin de clientes | `admin.py:10` | `ModelForm` del admin aplica el validador [código]; la normalización debe vivir en el modelo (`clean_fields` o `clean`) para cubrirlo |
| Factoría de pruebas | `tests/factorias.py:46` (`objects.create` sin `rut`) | `create` no valida: guardaría `rut=''` [inferido]. Agregar un RUT sintético válido |
| Restauración de respaldo | `views.py:1304` (`restaurar_bd`) | Reemplaza las tablas completas; restaurar un volcado anterior a la `0010` devuelve el esquema y `django_migrations` a ese punto [inferido] |

### Caminos que crean o editan una `Cotizacion`

| Camino | Dónde | Folio |
| :----- | :---- | :---- |
| Crear | `views.py:896` (`form.save()` dentro de `atomic`) | `save()` asigna |
| Editar | `views.py:951` | No cambia (`editable=False`) |
| Convertir a pedido | `views.py:1075` (`cotizacion.save()` para marcarla `ACEPTADA`) | No cambia; el mensaje y la nota del abono (`views.py:1066`) usan hoy `#{cotizacion.id}` |
| PDF | `views.py:1119` (`filename="Cotizacion_{cotizacion.id}.pdf"`) | Pasa a folio |
| Admin | **`Cotizacion` no está registrada en el admin** (`admin.py`: solo Cliente, Pedido, Producto y RegistroEvento) [código] | El alcance B.3 («folio de solo lectura, también en el admin») no tiene objeto (H3) |
| Duplicar | No existe para cotizaciones; `duplicar_pedido` (`views.py:517`) crea pedidos [código] | — |
| Factoría | `tests/factorias.py:86` (`objects.create`) | `save()` asigna |

### RUT sin índice único

La iteración dice `CharField(max_length=12)`, **sin `unique`** (alcance A.1 y «Fuera de alcance») [doc]. Correcto: con índice único la `0010` fallaría al rellenar 870 filas con el mismo ficticio [inferido].

### Folio y separador de miles

Medido en local con `es-cl`: `{{ n }}` con `n = 1000` pinta **`1 000`** (con espacio, no punto); `{{ n|unlocalize }}` y `{{ n|stringformat:"d" }}` pintan `1000`; el f-string del nombre de archivo da `Cotizacion_1000.pdf` [prueba]. Consecuencia: el problema está solo en las plantillas (13 usos de `cotizacion.id` en 6 plantillas, de los que los visibles son los de título, número, listado y confirmaciones) [código]; las URL (`{% url %}`) y los f-strings no se localizan. `USE_THOUSAND_SEPARATOR = True` está en `settings.py:263`, no en la 255 que cita la iteración [código].

## 3. Riesgos y consultas

### Aviso 1: ventana entre `migrate` y el Reload

Confirmo el mecanismo: el código viejo inserta sin `folio` ni `rut`; con `preserve_default=False` la columna queda sin `DEFAULT` y, sin modo estricto, MySQL guarda el valor implícito (`0` y `''`) con una advertencia [inferido de la documentación de MySQL; no ensayado]. El **segundo** folio 0 lo rechaza el índice único (un 500 visible, no silencioso). Matiz: el checkout ocurre antes de `migrate`, así que un worker que arranque en frío en la ventana ya carga el código nuevo; el riesgo es solo el worker ya caliente [inferido].

Opciones (sin decidir):

- **A.** Hora de baja actividad y aviso de no crear clientes ni cotizaciones; contar casos después (parte C, filas 9 y 10). Costo cero; depende de la disciplina.
- **B.** Desactivar la web app en el panel durante `migrate` y activarla con el Reload. Cierra la ventana; unos minutos sin servicio. Hay que confirmar que el plan gratuito lo permite y que no cuenta como «inactividad».
- **C.** `db_default='00.000.000-0'` para `rut` en la `0010` (Django 6 lo admite): el código viejo guardaría el ficticio, no `''`. No resuelve el folio. Cambia el SQL de la migración: se reclasifica con `sqlmigrate`.
- **D.** Incluir en el bloque del paso único una reparación: si hay folios 0, asignarles el siguiente antes de fijar 999. Agrega lógica al paso manual.

### Aviso 2: los folios de prueba se consumen

- **A.** No crear cotización de prueba en producción: validar el folio 1000 con la primera cotización real del dueño, y en el día 0 solo ver el contador en 999 desde el shell.
- **B.** Crear la de prueba, borrarla y aceptar que la primera real sea 1001.
- **C.** Crear la de prueba, borrarla y volver a correr el paso único (se negaría solo si queda un folio ≥ 1000; si nadie creó otra, vuelve a dejar 999). Requiere que el bloque admita volver a correr y que nadie cree cotizaciones en medio.
- **D.** Pedir al cliente que la cotización 1000 sea una real que él mismo cree mientras el desarrollador mira.

### Folios ≥ 1000 existentes

Como las existentes toman `folio = id`, el paso único se niega si **`MAX(id)` ≥ 1000**, no si hay más de 999 cotizaciones. Con 33 cotizaciones [dicho], eso depende de los huecos del `AUTO_INCREMENT` (borradas, restauraciones). Si se niega, opciones: renumerar (contradice D3), partir donde quede o fijar otro inicio (`PENDIENTE_DESARROLLADOR`). También: si `MAX(id)` ya es ≥ 1000, hoy esas cotizaciones se ven como `1 000` en pantalla.

### Consultas de solo lectura (las corre el desarrollador en la réplica y en producción)

```sql
-- 3.1 Cotizaciones: conteo, menor y mayor id
SELECT COUNT(*) AS cotizaciones, MIN(id) AS min_id, MAX(id) AS max_id FROM pedidos_cotizacion;
-- 3.2 Cotizaciones con id >= 1000 (harían negar el paso único)
SELECT COUNT(*) AS con_id_1000_o_mas FROM pedidos_cotizacion WHERE id >= 1000;
-- 3.3 Clientes
SELECT COUNT(*) AS clientes FROM pedidos_cliente;
-- 3.4 Próximo AUTO_INCREMENT de cotizaciones (informativo; MySQL 8 puede mostrarlo en caché)
SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'pedidos_cotizacion';
-- 3.5 AUD-05-026: pedidos sin fecha de entrega, y cuántos de ellos tienen alguna edición registrada (cota, no prueba)
SELECT COUNT(*) AS sin_fecha FROM pedidos_pedido WHERE fecha_entrega IS NULL;
SELECT COUNT(DISTINCT p.id) AS sin_fecha_y_editados FROM pedidos_pedido p JOIN pedidos_registroevento e ON e.entidad = 'pedido' AND e.entidad_id = p.id AND e.tipo = 'pedido_modificado' WHERE p.fecha_entrega IS NULL;
```

Solo conteos: no pegues filas. El registro de eventos existe desde la `0007` (2026-10-25), así que 3.5 no ve ediciones anteriores.

## 4. Hallazgos del análisis

| # | Qué | Efecto | Propuesta |
| :- | :-- | :----- | :-------- |
| H1 | AUD-05-026 comprobado: la fecha de entrega se pierde al editar un pedido | Crítica (RDA-022) | Arreglo urgente 14-05 antes de la 14-04 |
| H2 | El modal de cliente rápido es HTML propio en **dos** plantillas, `pedido_form.html` (no listada en la iteración) y `cotizacion_form.html`, y `index.js` solo envía tres campos | Sin cambiarlos, el modal siempre falla tras el despliegue | Sumar `pedido_form.html` a los archivos de la iteración |
| H3 | `Cotizacion` no está en el admin | B.3 «también en el admin» no aplica | Quitarlo o registrar el modelo (sería alcance nuevo) |
| H4 | Con `es-cl` el separador de miles es un espacio: `1 000`, no `1.000` | Corrige el ejemplo de la iteración y del aviso 4 de la evidencia | `\|unlocalize` en las plantillas |
| H5 | La factoría `crear_cliente` no pasa por validación y no trae RUT | Pruebas con `rut=''` | RUT sintético en la factoría |
| H6 | La iteración cita `settings.py:255`; está en la 263 | Referencia menor | Corregir al implementar |
| H7 | Réplica con 824 clientes frente a 870 en producción, refrescada el 2026-11-18 [dicho] | El ensayo de la `0010` y los conteos de A2.7 no reflejan producción | Refrescar la réplica antes del ensayo (`replica-local.md`) |
| H8 | `CotizacionForm.fecha_emision` tiene el mismo widget sin formato, hoy esquivado por la plantilla | Riesgo latente | Arreglar en la 14-05 junto con el de pedidos |

## 5. Documentos tocados

- `iteracion-14-04-…md`: estado (la `0009` ya existe), paso 2 del despliegue (`fetch --tags` y `checkout`, `despliegue.md` 3.2) y criterio 8 (461).
- `decisiones.md`: fila RDA-024 en el índice (faltaba).
- `definicion-epica-14.md`: fila de la 14-04.
- `evidencia-14-04.md`: estado, punto de partida (870/33 producción, 824/33 réplica, procedimiento de la 04-09 sin desviaciones) y A0.1 con el método usado.
- `auditoria-tecnica.md`: estado de AUD-05-026.
- `registro-pendientes.md`: próximo hito, decisiones por tomar e historial.

## Decisiones del 2026-11-27

Fase documental posterior (solo `.md`; sin código, consultas ni commit). Antes de editar se comprobó que `despliegue.md` 3.12 B, paso 6.3, ya cuenta `IntegrityError` [doc].

| Tema | Decisión [dicho] | Dónde quedó |
| :--- | :--------------- | :---------- |
| AUD-05-026 | **Media**, no Crítica. Se arregla **después** de la 14-04, en iteración propia (14-05, número al redactarla), con `format='%Y-%m-%d'` en `forms.py:97` y `:69` y prueba que falle antes. La 14-04 mantiene `v14.3-rut-y-folio` y retroceso `v4.11-csp-observacion` | Auditoría, registro, épica, evidencia (A0.2 y aviso 6) |
| Aviso 1 | **Opción A:** hora de poco uso, aviso al dueño de no crear clientes ni cotizaciones, conteo en la parte C (filas 9 a 11) y plan de contingencia escrito, sin código | Iteración (despliegue paso 3 y «Riesgos y avisos»), evidencia (A0) |
| Aviso 2 | **Opción C:** cotización de prueba; se borra antes que su cliente de prueba (`PROTECT`) y se re-corre el paso único, cuya guarda mira las cotizaciones existentes con folio ≥ 1000, no el contador, y anota valor antes y después | Iteración (pasos 4 y 7), evidencia (C, filas 4b y 4c) |
| H2 | `pedido_form.html` e `index.js` al alcance (campo RUT en los dos modales). Despliegue con `collectstatic` tras el checkout y antes de `migrate`, y `Ctrl+F5` | Iteración (archivos, A.5b, paso 2 y 5b), evidencia (B3b, C 4d, E) |
| H3 | Tachado «también en el admin» de B.3. Nuevo **AUD-05-031** (Baja, propuesta): `Cotizacion` no está en el admin; destino `PENDIENTE_DESARROLLADOR` (Épica 14 o 09) | Iteración, auditoría, registro |
| H4 y H6 | Corregidos en la iteración (`1 000` con `es-cl`; `settings.py:263`) | Iteración B.4 |

**Datos nuevos [consola, 2026-11-27]:** producción (~21:41): 33 cotizaciones (id 2 a 34), 0 con id ≥ 1000, **872** clientes (reemplaza el 870 dicho), 1.051 pedidos, 22 sin fecha de entrega, 1 con edición registrada. Réplica refrescada con `respaldo_27-11-2026_10-51-07.sql` (1.585.017 bytes, SHA-256 `2126d253bace…`, `VÁLIDO`, 19 de 19; 5,5 s; paridad 0; 19 tablas; `0009`): 33 (2 a 34), 0, 869, 1.049, 22 y 1; la diferencia con producción sería actividad posterior [inferido]. Cifrado verificado después de restaurar. Con `MAX(id)` = 34 el paso único no se niega [inferido de la guarda].

**Respaldo previo de la 04-09:** su nombre, tamaño y SHA-256 se toman como los del respaldo de arriba [inferido: el nombre coincide con la rotación de 10:51:08 y precede al checkout de 10:52]. Se precisó en `despliegue.md` sección 5 (fila `v4.11`) y en el registro; `bitacora-04-09.md` no se editó (bitácora ya entregada).

**Otros documentos:** `replica-local.md` (fila de refresco del 2026-11-27 en la sección 9; «18 tablas» → 19 en la sección 5).

**H7 (réplica atrasada):** resuelto con el refresco.

## 6. Qué no consta

- Si AUD-05-026 ya borró fechas en producción (consulta 3.5 sin correr).
- `MAX(id)` de las cotizaciones en réplica y producción.
- Método y hora de los conteos de 870 y 33 [dicho].
- La prueba efímera no corrió la suite completa: la cuenta de 461 es la de la 04-09 [doc].
