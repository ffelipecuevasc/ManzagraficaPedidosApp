# Bitácora 00-07 · Correcciones tempranas II

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión (fase 1 aprobada por el desarrollador el 2026-10-27; fase 2 implementada en local). Faltan `test pedidos` con el contenedor MySQL encendido y la revisión manual.

## Resumen

Fase 1: la iteración 00-07 se ajustó a las seis decisiones del desarrollador del 2026-10-27 (alcance crear y editar pedido, script propio en `pedido_form.html`, indicador igual a la 00-06, `v0.3-doble-envio` con retroceso a `v1.2-capturas`, orden del domingo 2026-11-01 y etiquetas sobre commits distintos). Se creó `evidencia-00-07.md` y se actualizaron la definición de la épica y el registro. `docs/operacion/despliegue.md` no se editó: abajo van los textos propuestos. Sin cambios de código.

Fase 2 (aprobada por el desarrollador el 2026-10-27): el botón `btn-confirmar-pedido` de `pedido_form.html` lleva los cuatro elementos `data-*` de la 00-06 y las clases `disabled:`; un script propio en `{% block scripts %}`, atado al `submit` del formulario, lo desactiva al primer envío, muestra «Guardando…» con el ícono que gira, cancela el segundo envío y lo restaura en `pageshow`. Cubre crear y editar (plantilla compartida). Se aplicaron los tres textos propuestos en `docs/operacion/despliegue.md`.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-07-correcciones-tempranas-ii.md` | Cabecera (etiqueta, retroceso, ventana, evidencia, «Ninguno (sin migración)»), objetivo, tareas, criterios, fuera de alcance y decisiones 1 a 6; el texto anterior queda tachado |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-07.md` | Nuevo: partes A a D |
| `_planificacion/10_epicas/epica-00-blindaje/definicion-epica-00.md` | Alcance 7, tabla de iteraciones y nota |
| `_planificacion/00_producto/registro-pendientes.md` | Fila 00-07, decisión de ventana resuelta, pendiente de `DESIGN.md` §8, dos propuestas e historial |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-07.md` | Esta bitácora |
| `pedidos/templates/pedidos/pedido_form.html` | Fase 2: botón con elementos `data-*` y clases `disabled:`; bloque `scripts` con el manejador de `submit` y `pageshow` |
| `docs/operacion/despliegue.md` | Fase 2: los tres textos propuestos (decisión del desarrollador del 2026-10-27) |
| `iteracion-00-07…`, `registro-pendientes.md` | Fase 2: estado En revisión e historial |

## Verificación

- Fase 1 solo documental: sin pruebas que ejecutar.
- **Fase 2, 2026-10-27:**
  - `python manage.py test pedidos`: **no se pudo ejecutar**. Falló al conectar con la base (`OperationalError: (2002, "Can't connect to server on '127.0.0.1' (10061)")`): el contenedor MySQL local está apagado, y encenderlo le corresponde al desarrollador (`AGENTS.md`, sección 5). Ninguna prueba renderiza el botón nuevo, así que no se espera un cambio en el recuento (184 pruebas, 19 fallos esperados), pero queda **sin verificar**.
  - `python manage.py check`: `System check identified no issues (0 silenced).`
  - `python manage.py makemigrations --check --dry-run`: `No changes detected`.
  - La plantilla compila con el cargador de Django (`get_template('pedidos/pedido_form.html')`, sin base de datos): sin errores de sintaxis.
  - Revisión en el navegador: no hecha por el agente (no abre un navegador). Pasos abajo.

### Diff de `pedido_form.html`

```diff
@@ botón btn-confirmar-pedido
-                                    class="… text-sm uppercase tracking-wide flex items-center">
-                                <span class="material-icons-round mr-2 text-xl">check_circle</span>
-                                Crear Pedido
+                                    class="… text-sm uppercase tracking-wide flex items-center disabled:cursor-wait disabled:opacity-75 disabled:hover:bg-primary disabled:hover:shadow-md">
+                                <span class="material-icons-round mr-2 text-xl" aria-hidden="true" data-icono-normal>check_circle</span>
+                                <span class="material-icons-round mr-2 text-xl animate-spin hidden" aria-hidden="true" data-icono-procesando>autorenew</span>
+                                <span data-texto-normal>Crear Pedido</span>
+                                <span data-texto-procesando class="hidden">Guardando…</span>
@@ final de la plantilla
 {% endblock %}
+
+{% block scripts %}
+<script>
+    (function () { … form 'pedidoForm', botón 'btn-confirmar-pedido';
+      mostrar(procesando): disabled, aria-busy y alterna los elementos data-*;
+      submit: si el botón ya está desactivado, preventDefault; si no, mostrar(true);
+      pageshow: mostrar(false). })();
+</script>
+{% endblock %}
```

El script es el de `login.html` con otros ids y dos comentarios. Los íconos llevan `aria-hidden="true"` (`DESIGN.md:130`). Las clases `disabled:` son las del botón de acceso, salvo `disabled:active:scale-100`, que no aplica porque este botón no tiene `active:scale-95`, y con `disabled:hover:shadow-md` para que el botón desactivado no cambie su sombra.

### Diff de `docs/operacion/despliegue.md` (decisión del desarrollador, 2026-10-27)

```diff
@@ sección 1, después de «Si push responde rejected…»
+**Etiquetar un commit anterior a la punta.** (texto completo de la propuesta 1 de abajo, con su bloque de comandos y sus tres viñetas)
@@ sección 2, lista de comprobación
-| 6 | Estilos compilados | PC | Cuando el proyecto compile Tailwind (05-04). Hasta entonces: «no aplica». |
+| 6 | Estilos compilados | PC | Cuando el proyecto compile Tailwind (08-05; antes 05-04, RDA-014). Hasta entonces: «no aplica». |
-| 8 | Solo despliegue de 00-04 | PA | Sección 4. |
+| 8 | Pasos propios del despliegue | PA | Los que indique la evidencia de la iteración (por ejemplo, la sección 4 para la 00-04). |
```

Solo esos tres cambios (17 líneas agregadas y 2 cambiadas). La observación 4 (fases de 0 a 7) no se aplicó.

### Revisión manual pendiente (desarrollador, contra la réplica)

Con `docker compose up -d`, `python manage.py runserver` y sesión iniciada:

1. **Crear:** cuenta los pedidos antes (por ejemplo, el total del listado), llena «Nuevo pedido» y haz doble clic rápido en «Crear Pedido». Esperado: el botón pasa a «Guardando…» con el ícono girando, y el total sube en 1. Anota solo los conteos.
2. **Editar:** abre un pedido, entra a editar y haz doble clic rápido. Esperado: un solo guardado (en `access.log` de `runserver`, un solo `POST /pedido/editar/<id>/`).
3. **Validación nativa:** escribe un abono negativo (el campo tiene `min="0"`) y pulsa «Crear Pedido». Esperado: el navegador marca el campo y el botón sigue activo, con «Crear Pedido».
4. **Atrás:** después de crear, vuelve con «atrás». Esperado: el botón dice «Crear Pedido» y está activo.
5. **Escritorio y 360 px, modo claro y oscuro:** texto legible en el estado desactivado y foco visible al llegar con Tab.
6. **«Nueva cotización»:** se ve y envía igual que antes (no se tocó su plantilla).

Después, corre `python manage.py test pedidos` (esperado: `Ran 184 tests`, `OK (expected failures=19)`) y anota el resultado.
- Verificado en el código antes de redactar: `base.html:317` carga `index.js` y `base.html:319` define `{% block scripts %}`, que ninguna plantilla de pedidos usa hoy; `pedido_form.html:416-421` tiene el botón `btn-confirmar-pedido` con el texto «Crear Pedido»; `views.py:244` y `:294` renderizan esa plantilla; `cotizacion_form.html:31` usa el mismo id `pedidoForm`.

## Migraciones

- Ninguna.

## Criterios de aceptación

- Ninguno marcado todavía (fase 2).

## Decisiones tomadas

- Las seis decisiones del desarrollador del 2026-10-27, copiadas en la iteración.
- En la evidencia, el «último commit anterior a la 00-07» se ubica como el commit inmediatamente anterior al primero que cambia `pedido_form.html`. Los commits solo de documentos marcados «00-07» pueden quedar dentro de `v1.2-capturas` sin efecto en el servidor; B2 lo comprueba con `git diff --stat`.

## Propuestas para `docs/operacion/despliegue.md` (no aplicadas; decide el desarrollador)

### 1. Paso nuevo: etiquetar un commit anterior a la punta de `main`

Ubicación propuesta: sección 1, después del bloque «Crear y publicar la etiqueta».

> **Etiquetar un commit anterior a la punta.** Cuando `main` ya tiene el trabajo del despliegue siguiente (por ejemplo, la 00-07 sobre `v1.2-capturas`), la etiqueta se crea sobre el hash del último commit que pertenece a este despliegue, no sobre la punta:
>
> ```powershell
> git log --oneline -n 15
> git diff --stat <hash>..main -- . ":(exclude)_planificacion" ":(exclude)docs"
> $hoy = Get-Date -Format "yyyy-MM-dd"
> git tag -a <etiqueta> <hash> -m "Iteración XX-YY · desplegada el $hoy"
> git tag -n <etiqueta>
> git push origin <etiqueta>
> ```
>
> - El `diff` debe listar solo los archivos ejecutables del despliegue siguiente; cualquier otro archivo significa que el hash elegido deja fuera algo de este despliegue o mete algo del siguiente: detente.
> - El resto de las reglas no cambia: `git status --short` vacío y `main` igual a `origin/main` antes de etiquetar.
> - El destino de retroceso del despliegue siguiente es esta etiqueta, aunque su número de fase sea mayor (por ejemplo, `v0.3-doble-envio` vuelve a `v1.2-capturas`). El destino es la etiqueta desplegada antes, no la anterior en el orden de `git tag -n`.

### 2. Punto 6 de la lista de comprobación (numeración anterior a RDA-014)

- **Texto actual:** «| 6 | Estilos compilados | PC | Cuando el proyecto compile Tailwind (05-04). Hasta entonces: «no aplica». |»
- **Texto propuesto:** «| 6 | Estilos compilados | PC | Cuando el proyecto compile Tailwind (08-05; antes 05-04, RDA-014). Hasta entonces: «no aplica». |»
- **Por qué:** RDA-014 movió la compilación de Tailwind a la 08-05. Si no se cambia, quien lea la lista busca una iteración 05-04 que ya no existe.

### 3. Punto 8 de la lista de comprobación

- **Texto actual:** «| 8 | Solo despliegue de 00-04 | PA | Sección 4. |»
- **Texto propuesto:** «| 8 | Pasos propios del despliegue | PA | Los que indique la evidencia de la iteración (por ejemplo, la sección 4 para la 00-04). |»
- **Por qué:** el punto solo aplicaba al primer despliegue (`v0.1-higiene`); hoy cada iteración trae sus pasos propios en su evidencia.

### 4. Observación relacionada (sin texto propuesto)

- Sección 1, «`<fase>`: … `0`, `1`… `7`»: con RDA-014 las épicas van de 00 a 14. Si el desarrollador quiere, se ajusta en la misma edición.

## Pendientes y riesgos

- `DESIGN.md` §8 frente al ícono que gira: registrado en el registro, sección 3.
- Propuestas sin iteración: `btn-submit-pedido` inexistente en `index.js:302` y «Crear Pedido» en modo edición (registro, sección 4).
- Pruebas con MySQL encendido y revisión manual: pendientes del desarrollador.
- Con la protección solo en el navegador, un envío repetido por otro medio (recarga del POST, red lenta con reintento) sigue siendo posible hasta la 03-04.

## Commit sugerido

`Épica 0 - Iteración 00-07: evita el doble envío de Crear Pedido al crear y editar, prepara v0.3-doble-envio y precisa en despliegue.md cómo etiquetar un commit anterior a la punta`
