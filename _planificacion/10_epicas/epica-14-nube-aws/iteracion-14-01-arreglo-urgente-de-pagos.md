# Iteración 14-01 · Arreglo urgente de pagos

- **Épica:** 14 · Mantenimiento
- **Estado:** Pendiente (redactada, decisiones resueltas). D1 a D5 y la etiqueta, resueltas el 2026-11-18 (decisión del desarrollador, dicha por él): D1 A, D2 A, D3 A, D4 A, D5 B, `v14.1-pagos`. Redactada el 2026-11-18 ([bitacora-04-replanificacion](../../99_bitacora/epica-04-seguridad/bitacora-04-replanificacion.md)). Es el primer arreglo urgente del método de la RDA-022.
- **Subfase del plan:** ninguna (no existe en el plan original; RDA-022).
- **Depende de:** ninguna. **Se ejecuta y se despliega ANTES de la 04-01** (decisión del desarrollador, 2026-11-18). Producción está en `v3.1-integridad`, sobre `7e14398` (dicho por el desarrollador).
- **RDA relacionadas:** RDA-007 (un despliegue, un propósito; aviso al cliente), RDA-021 (sin esperas: verificación del mismo día y plan de retroceso), RDA-022 (gravedad Crítica y arreglo urgente).
- **Hallazgos que cierra:** AUD-05-010 (Crítica) y AUD-05-011 (Alta). **AUD-05-009 (Baja): no entra** (D3 A, 2026-11-18); sigue en la Épica 08 o en una iteración de frontend de la Épica 14.
- **Cambio de esquema:** ninguno. No hay migración.
- **Respaldo previo al despliegue:** no lo exige por sí misma (solo plantillas y un formulario; ni datos ni esquema). El último respaldo verificado es `respaldo_18-11-2026_14-26-45.sql` (19 de 19, `VÁLIDO`, dicho por el desarrollador). Si el desarrollador quiere uno nuevo, se hace con el protocolo normal.
- **Etiqueta y ventana:** despliegue propio. Etiqueta **`v14.1-pagos`** (formato `v<fase>.<correlativo>-<propósito>` de `despliegue.md`, sección 1; confirmada por el desarrollador el 2026-11-18). Destino de retroceso: **`v3.1-integridad`**. Fecha y ventana: `PENDIENTE_DESARROLLADOR`; el defecto sigue vivo en producción hasta entonces.
- **Archivos que tocará la ejecución:** `pedidos/templates/pedidos/pago_form.html`, `pedidos/forms.py` (`PagoForm`), `pedidos/templates/pedidos/pedido_form.html`, `pedidos/templates/pedidos/cotizacion_form.html` y pruebas nuevas. **No toca** `views.py`, configuración, dependencias, estáticos ni migraciones: no necesita consulta previa (`AGENTS.md`, sección 6).

## Objetivo

Que un pago se registre desde el detalle de **cualquier** pedido, también desde el #1000 en adelante, y que, si un pago no se puede guardar, el formulario lo diga; y que el selector de pedidos de `/pagos/ingresar/` deje de hacer una consulta por pedido.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-18 en `main` (`a4a0f37`), con archivo y línea. El código de `pedidos/`, `PedidosApp/` y `requirements.txt` es idéntico al de `7e14398`, el commit desplegado (`git diff --stat 7e14398..HEAD`, sin salida).
- **Dicho por el desarrollador:** no comprobado por el agente (el cliente reportó un pago que «no se guardó»; los tiempos de `/pagos/ingresar/` de las pruebas del día 0).
- **Inferido:** sale de leer el código; no se reprodujo en pantalla. La primera prueba de esta iteración lo confirma o lo desmiente.

## Qué pasa hoy

### AUD-05-010 · el pago se rechaza sin avisar (Crítica)

- **Causa (inferida, no reproducida):** `settings.py:177` fija `LANGUAGE_CODE = 'es-cl'` y `:201` activa `USE_THOUSAND_SEPARATOR`. El motor de plantillas formatea los enteros con el separador de miles de la configuración regional, así que `{{ pedido_obj.id }}` escribe **«1.002»** para el pedido 1002. `pago_form.html:78` lo pone en el campo oculto `name="pedido"` cuando el formulario se abre con un pedido elegido (`pedido_obj` y sin `form.instance.pk`, `:75`). `PagoForm` recibe «1.002», no lo reconoce como un pedido y el formulario vuelve con el campo `pedido` en error.
- **Por qué no se ve:** esa rama de la plantilla (`:75-78`) no pinta `form.pedido.errors`; el aviso solo existe en la rama del selector (`:81-83`). El usuario ve el formulario de nuevo, sin mensaje, y el pago no se guardó. Los mensajes de Django (`messages`) no se usan en este caso: la vista devuelve el formulario con 200.
- **Quién queda afectado:** abrir el formulario desde el detalle de un pedido con id de 1.000 o más (`ingresar_pago(request, pedido_id)`, `views.py:1481`). **No afecta** a pedidos menores a 1.000, ni a `editar_pago` (usa el selector: las opciones de un `<select>` no se localizan), ni a registrar el pago desde `/pagos/ingresar/` sin pedido elegido, que escoge el pedido en el selector, ni al abono inicial al crear el pedido. Existe «desde v1.0» y es igual en `v0.3-doble-envio` (dicho por el desarrollador; «v1.0» no es una etiqueta del protocolo y no la verifiqué). **No es una regresión de la Fase 3.**
- **Los pagos rechazados no quedaron guardados en ninguna parte:** el formulario devolvió el error y no hubo escritura ni evento. Cuántos fueron y si el cliente los volvió a registrar: `PENDIENTE_CLIENTE` (ver «Datos requeridos»).

### Latente, misma causa: el id del producto

`pedido_form.html:142` y `cotizacion_form.html:138` escriben `<option value="{{ producto.id }}"`. Un producto con id de 1.000 o más saldría como «1.002» y `index.js` lo mandaría así dentro de los ítems. Hoy no se sabe si existe uno: la línea base contó 55 productos el 2026-10-20 y no midió el id mayor (`PENDIENTE_DESARROLLADOR`, medición de solo lectura en el desarrollador). `data-precio` no tiene el problema: usa `|stringformat:'d'`, que no localiza.

Revisión de las demás plantillas (búsqueda en `pedidos/templates`, 2026-11-18): no hay otro id escrito con `{{ }}` dentro de un campo, un enlace o un atributo. Los demás casos escriben el id como **texto visible** (`#{{ x.id }}`, 31 líneas en 18 plantillas, más `cotizacion_pdf.html:237` y `pago_detail.html:44`) y muestran «#1.002»: es solo presentación, queda fuera (propuesta en el registro, sección 4).

### AUD-05-011 · una consulta por pedido en el selector (Alta)

- `PagoForm.__init__` arma el selector con `Pedido.objects.all().order_by('-id')` (`forms.py:89`), sin `select_related('cliente')`. Cada opción llama a `Pedido.__str__`, que lee `self.cliente.nombre` (`models.py:61`): **una consulta por pedido**. Con los 994 pedidos de la réplica al 2026-11-18, del orden de mil consultas (cuenta calculada, no medida).
- **Dónde ocurre:** cuando la plantilla pinta el selector (`pago_form.html:80`): `/pagos/ingresar/` sin pedido elegido y `editar_pago`. Con un pedido elegido en la URL no se pinta, así que no hay N+1 (inferido de la plantilla).
- **Medido por el desarrollador (dicho):** de 2,7 a 8,0 s en las pruebas del día 0 de la 03-05 (2026-11-17, de 02:55 a 02:58 UTC). Incumple la regla 12 de `AGENTS.md` y el criterio (iv) de la 03-05, exceptuado por el desarrollador.
- Revisión de otros selectores (`forms.py`, 2026-11-18): `PagoForm.pedido` es el único `ModelChoiceField` con un queryset propio; los demás campos de relación (`cliente` en `PedidoForm` y `CotizacionForm`) usan el queryset por defecto y `Cliente.__str__` no lee otra tabla (`models.py:25-26`). No se encontró el mismo patrón en otro formulario.

## Decisiones (resueltas el 2026-11-18)

**Resolución del desarrollador (2026-11-18, dicha por él):**

| # | Elegida | Efecto |
| :- | :------ | :----- |
| D1 | **A** | `{% load l10n %}` y `{{ pedido_obj.pk\|unlocalize }}` en `pago_form.html`, mismo patrón que `dashboard.html`. No cambia `views.py`. |
| D2 | **A** | `Pedido.objects.select_related('cliente').order_by('-id')` en `forms.py`. |
| D3 | **A** | AUD-05-009 no entra. |
| D4 | **A** | Texto propio con tuteo en `PagoForm.Meta.error_messages` (`invalid_choice`): «No se reconoció el pedido. Vuelve a abrir el pago desde el pedido o elígelo en la lista.» |
| D5 | **B** | Sin aviso provisional al cliente antes del despliegue. Siguen los avisos de antes y después del despliegue. |
| Etiqueta | `v14.1-pagos` | Retroceso a `v3.1-integridad`. |

Opciones tal como se redactaron (se conservan como historia):

| # | Decisión | Opciones |
| :- | :------- | :------- |
| D1 | Cómo se escribe el id del pedido en el campo oculto | **A (recomendada):** `{{ pedido_obj.pk\|unlocalize }}` con `{% load l10n %}`, el mismo patrón de `dashboard.html:3` y `:129-131`; una línea, misma causa que las otras dos plantillas. B: armar el campo con el formulario (`form.pedido.as_hidden`). C: A, y además la vista toma el pedido de la URL e ignora el del formulario (cambia `views.py`). |
| D2 | Cómo se corrige AUD-05-011 | **A (recomendada):** `Pedido.objects.select_related('cliente').order_by('-id')`; una consulta con `JOIN` en lugar de una por pedido, sin cambiar lo que ve el usuario. B: limitar el selector (por ejemplo, solo pedidos con saldo): cambia una regla del negocio (¿se puede registrar un pago en un pedido ya pagado?, `PENDIENTE_CLIENTE`); no se hace aquí. |
| D3 | ¿Entra AUD-05-009 (`$(document).ready` antes de que cargue jQuery, mismo archivo)? | **A (recomendada): no entra.** Razones: (1) es otro propósito (JavaScript de interfaz, Baja, sin efecto en datos) y RDA-022 manda las Baja a la Épica 14 por tema; (2) moverlo cambia cómo arranca Select2 en el selector que esta iteración ya toca por AUD-05-011: si algo falla en el despliegue no se sabría cuál de los dos cambios lo causó y el retroceso no sería limpio; (3) por la lectura de AUD-05-009, su efecto probable es solo un error en la consola, porque `index.js:77-82` ya inicializa `.select2` (hipótesis, no probada en pantalla). B: entra, porque es el mismo archivo y son 12 líneas; exige revisar a mano el selector en escritorio y a 360 px en la verificación del día. Si no entra, sigue en la Épica 08 (o en una iteración de frontend de formularios de la Épica 14, si el desarrollador la mueve). |
| D4 | Texto del aviso cuando el pedido no es válido | El de Django en español es «Escoja una opción válida. Esa opción no es una de las disponibles.» (trato de usted; `AGENTS.md`, sección 7, regla 1 pide tú). **A (recomendada):** texto propio en `PagoForm.Meta.error_messages` para `invalid_choice`: «No se reconoció el pedido. Vuelve a abrir el pago desde el pedido o elígelo en la lista.» (**por aprobar**). B: dejar el de Django. |
| D5 | Aviso provisional al cliente hasta el despliegue | **A (recomendada):** avisar ya del camino alterno (Pagos → Registrar pago, elegir el pedido en el selector, que no usa el campo oculto; **inferido, no probado**; el selector tarda de 2,7 a 8,0 s) y pedir que revise los pagos de pedidos desde el #1000 que intentó registrar. B: no avisar antes. Lo decide y lo envía el desarrollador. |

## Alcance

1. **`pago_form.html`:** `{% load l10n %}`; el id del campo oculto sin separador de miles (D1); el aviso de `form.pedido.errors` también en la rama del campo oculto, con el mismo marcado que la otra rama (`id="error-pedido"`, `role="alert"`, colores de `DESIGN.md`); el aviso es visible a escritorio y a 360 px.
2. **`forms.py`:** `select_related('cliente')` en el selector (D2) y el texto del aviso con tuteo (D4 A).
3. **`pedido_form.html` y `cotizacion_form.html`:** `{% load l10n %}` y `value="{{ producto.id|unlocalize }}"`.
4. **Pruebas** (sección siguiente), escritas antes que la corrección.
5. **Documentación:** bitácora, registro, auditoría (AUD-05-010 y AUD-05-011 pasan a «Resuelto en 14-01» al verificarse en producción) y la fila del despliegue en `docs/operacion/despliegue.md`, sección 5 (la agrega el desarrollador al desplegar).

## Pasos

0. Sin consulta previa: no toca configuración, dependencias, migraciones ni documentos protegidos.
1. **Línea base local:** `python manage.py test pedidos` (267 pruebas, `OK (expected failures=9)` el 2026-11-16: se anota el número vigente), `check` y `makemigrations --check --dry-run`. **Medir antes** las consultas de `GET /pagos/ingresar/` (sección «Medición»).
2. **Pruebas primero:** las pruebas T1 a T5 **fallan** con el código actual.
3. Corregir (alcance 1 a 3) hasta que pasen.
4. Suite completa: `OK (expected failures=9)` (los nueve fallos esperados no cambian: ninguno es de pagos); `check`; `makemigrations --check --dry-run` sin cambios.
5. **Medir después** (misma medición).
6. **Revisión manual en la réplica**, en escritorio y a 360 px: (a) detalle de un pedido con id ≥ 1000 (inferido: el #1015 es anterior al respaldo con que se refrescó la réplica el 2026-11-18; se confirma al abrir el listado de pedidos) → «Registrar pago» → guardar; el campo oculto lleva el id sin punto; (b) forzar el error: con las herramientas del navegador cambiar el valor oculto a «1.002» y enviar: el aviso se ve junto al pedido; (c) `/pagos/ingresar/` sin pedido y `editar_pago`: el selector carga y busca (Select2); (d) crear pedido y cotización: el selector de productos funciona. El caso de un producto con id ≥ 1000 lo cubren las pruebas: si el id mayor de la réplica es menor, no se puede ver a mano.
7. Bitácora, registro, auditoría, estado «En revisión», con los pasos de producción para el desarrollador y el mensaje de commit.

## Pruebas (reglas 15 y 12 de `AGENTS.md`; en `pedidos/tests/test_pagos.py` o un archivo nuevo del dominio de pagos, con las factorías de `factorias.py`)

- **T1 · el pago desde un pedido grande se guarda.** `crear_pedido(id=1002, valor_venta=10_000)`; `GET /pagos/ingresar/1002/`: el campo `name="pedido"` trae `value="1002"` y la respuesta no contiene `value="1.002"`. Con el valor leído del HTML se envía el `POST`: redirige a la lista, hay un `Pago`, el pedido queda `PARCIAL` o `PAGADO` y existe el evento `pago_registrado`. **Falla hoy** (el formulario vuelve con 200).
- **T2 · el error de «pedido» se ve.** `POST /pagos/ingresar/1002/` con `pedido='1.002'`: 200, ningún pago nuevo, y el HTML contiene `id="error-pedido"` con el texto de D4. **Falla hoy** (sin aviso).
- **T3 · ids de producto.** `crear_producto(id=1002)`; `GET /pedidos/nuevo/` y `GET /cotizaciones/nueva/` traen `<option value="1002"` y no `value="1.002"`. **Fallan hoy.**
- **T4 · el selector no hace una consulta por pedido.** Con `CaptureQueriesContext`, `GET /pagos/ingresar/` con 3 y con 30 pedidos de clientes distintos hace **el mismo número de consultas**. **Falla hoy** (crece con el número de pedidos).
- **T5 · `editar_pago`** responde 200 con el selector y el mismo número de consultas con 3 y con 30 pedidos (misma causa que T4).
- **Regresión:** `PagosTests` (`test_pedidos.py`) y `test_fronteras_transaccionales.py:252` siguen en verde sin cambios.

## Medición (regla 12: consultas antes y después, en la bitácora)

| Dónde | Qué | Antes | Después |
| :---- | :-- | :---- | :------ |
| Pruebas (MySQL) | Consultas de `GET /pagos/ingresar/` con 3 y con 30 pedidos | crece con N | constante |
| Réplica (994 pedidos al 2026-11-18) | Consultas y tiempo de `GET /pagos/ingresar/` | sin medir (del orden de mil, calculado) | sin medir |

La herramienta de diagnóstico de consultas es de la 05-02 y aún no existe: en la réplica se mide con una prueba temporal o con el procedimiento que el desarrollador indique; si hace falta `manage.py shell`, se pide consulta previa (no está entre los comandos de `AGENTS.md`, sección 5).

## Aviso al cliente (RDA-007)

- **Antes del despliegue:** un aviso breve («Hoy a las HH:MM se actualiza la aplicación; si estás registrando un pago en ese momento, termina antes»). Texto literal **por aprobar** por el desarrollador. El despliegue no cambia estáticos: no hace falta Ctrl+F5.
- **Después:** que el cliente registre de nuevo los pagos que no se guardaron, empezando por el del #1004 («Datos requeridos»).
- **Aviso provisional:** no se envía (D5 B, 2026-11-18).

## Verificación el mismo día (RDA-021; la hace el desarrollador; todo **no verificado** hasta entonces)

1. **[PC]** Lista de `despliegue.md`, sección 2: pruebas `OK (expected failures=9)`, `check --deploy` con las advertencias ya conocidas, `makemigrations --check --dry-run` sin cambios, etiqueta publicada (`git ls-remote --tags origin v14.1-pagos`). El punto 5 (respaldo) no aplica.
2. **[PC]** `git diff --stat v3.1-integridad v14.1-pagos -- requirements.txt pedidos/migrations PedidosApp/settings.py pedidos/static` **sin salida** (sin dependencias, migraciones, configuración ni estáticos).
3. **[PA]** Despliegue sin `pip`, `migrate` ni `collectstatic`; `git describe --tags` = `v14.1-pagos`; `check`; Reload (`despliegue.md`, sección 3).
4. **[Navegador, ventana privada]** las pantallas de `despliegue.md`, sección 3.7 (inicio, panel, listado y detalle de pedido).
5. **[Navegador]** pago de prueba desde el detalle de un pedido de prueba con id ≥ 1000 (los pedidos nuevos ya lo son: el último conocido es el #1015), con el protocolo de pedido y pago de prueba de la parte C de [evidencia-03-05](../epica-03-integridad-transaccional/evidencia-03-05.md): se guarda y queda `pago_registrado` (`PENDIENTE_DESARROLLADOR`: confirmar que ese protocolo sigue vigente y cómo se borran los datos de prueba).
6. **[PA]** `server.log` desde el reinicio efectivo: sin `nivel=ERROR` nuevos.
7. **Tiempo:** ninguna respuesta de `/pagos/ingresar/` pasa de 2 s (el umbral de (iv) de la 03-05), sin contar la recarga; si `access.log` no trae `response-time=`, el criterio no se puede medir y se anota.
8. **Mediciones opcionales de solo lectura (conteos, sin datos de clientes):** el id mayor de productos y de pedidos; la fecha en que se creó el pedido #1000 (`fecha_solicitud`), para acotar desde cuándo existe el defecto.

## Plan de retroceso

- **Disparadores:** cualquier 500 en un formulario de pago, pedido o cotización; un pago que vuelve a no guardarse con id ≥ 1000; el selector de pedidos o de productos que no carga.
- **Cómo:** `retroceso.md`, caso 1 (sin migraciones): volver a **`v3.1-integridad`**, recargar y verificar. Sin migraciones ni estáticos, no hay nada más que deshacer.
- **Qué no se pierde:** ningún dato. Lo único que vuelve es el defecto, que ya existía.

## Criterios de aceptación

- [ ] T1 a T5 fallan antes de la corrección y pasan después.
- [ ] Suite completa en verde con `OK (expected failures=9)`; `check` y `makemigrations --check --dry-run` sin cambios.
- [ ] Consultas de `GET /pagos/ingresar/` medidas antes y después en la bitácora, constantes con N.
- [ ] Revisión manual en la réplica a escritorio y a 360 px (puntos a a d del paso 6).
- [ ] Un pago desde un pedido con id ≥ 1000 se guarda en producción (verificación 5) y no hay `ERROR` nuevos (6).
- [ ] AUD-05-010 y AUD-05-011 pasan a «Resuelto en 14-01» en la auditoría, con la evidencia mínima.

## Riesgos

- **Causa inferida:** si T1 no falla con el código actual, la causa no es la que se leyó: se detiene la iteración y se vuelve a diagnosticar.
- **`unlocalize` no es el único camino:** un cambio de configuración regional (por ejemplo, quitar `USE_THOUSAND_SEPARATOR`) también arreglaría el campo, pero cambiaría el formato de todos los montos de la aplicación: no se hace aquí.
- **Pagos ya perdidos:** el arreglo no recupera los pagos que se rechazaron; solo evita los nuevos.
- **Un despliegue, un propósito (RDA-007):** solo el formulario de pagos y el mismo defecto en los ids de producto. No viaja nada de la Épica 04 ni AUD-05-009 (D3 A).

## Fuera de alcance

- Los ids con separador de miles en **texto visible** («#1.002»): propuesta en el registro, sección 4.
- No permitir el sobrepago, la mayor parte de la regla de saldos y cualquier otro cambio de las reglas de pagos: propuesta de destino en la Épica 14 (respuesta 6 del cliente).
- AUD-05-009 (D3 A).
- Borrar el pedido #1015: va después de la 04-10, con confirmación del cliente y respaldo verificado. **Antes de borrarlo**, el desarrollador revisa duplicados en producción con una consulta de solo lectura (conteos, sin datos de clientes en la documentación).
- Cualquier otra optimización de consultas: Épica 05.

## Datos requeridos del cliente

- **Pagos que «no se guardaron»** (`PENDIENTE_CLIENTE`): si el cliente intentó registrar otros pagos de pedidos desde el #1000 y no los volvió a ingresar. Sin ese dato no se sabe qué faltó: la aplicación no dejó rastro de los rechazos.
- **Pago no guardado conocido: pedido #1004** (audio del cliente del 2026-11-18, dicho por el desarrollador; no verificado). Coincide con la causa (id ≥ 1000). Tras el despliegue, el cliente lo registra de nuevo. Si hubo otros, sigue `PENDIENTE_CLIENTE`.
