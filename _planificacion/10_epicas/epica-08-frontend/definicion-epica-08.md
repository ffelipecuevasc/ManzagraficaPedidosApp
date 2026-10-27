# Épica 08 · Frontend: estáticos, plantillas y estilos

- **Estado:** Pendiente
- **Fase del plan:** subfases 5.4 y 5.5 (`plan-de-trabajo.md`, «FASE 5») más trabajo nuevo; anexo del plan del 2026-10-27 (RDA-014)
- **Objetivo:** que el navegador reciba una página liviana, sin compiladores ni librerías desde CDN, y que las plantillas tengan una estructura ordenada y reutilizable con el lenguaje de plantillas de Django (DTL).
- **Precondición:** Épica 07 completa (las vistas ya están por dominio, así que mover plantillas toca módulos pequeños) y 04-09 desplegada (la política de seguridad de contenido en observación muestra qué recursos externos quedan).
- **Última revisión:** 2026-10-27 (creada a pedido del desarrollador).

## Por qué esta épica (contexto para quien llega)

Hoy `base.html` carga el compilador de Tailwind desde un CDN: unos 400 KB de JavaScript que en cada página recorren el documento, generan el CSS y lo inyectan. Mientras tanto la página aparece sin estilos. A eso se suman tipografías e íconos de Google Fonts, Select2, Summernote y SweetAlert2 desde jsDelivr, sin atributo `integrity` (AUD-03-005). Las 28 plantillas de `pedidos/templates/pedidos/` están en una sola carpeta, y el `<head>`, la navegación y el pie se repiten en vez de compartirse.

Node.js y pnpm se usan **solo en la máquina del desarrollador** para compilar el CSS. El archivo compilado se versiona y PythonAnywhere lo sirve como cualquier estático: el servidor nunca necesita Node (RDA-010).

## Alcance

1. **Medición inicial del navegador (08-01):** tiempo hasta el primer contenido pintado, peso transferido y número de peticiones en las tres vistas más usadas, con el mismo método que se repetirá en 08-09.
2. **Estáticos y plantillas globales (08-02):**
   - `static/` en la raíz del proyecto (`STATICFILES_DIRS`), con `css/`, `js/`, `img/`, `icons/` (SVG) y `fonts/`. Lo que hoy está en `pedidos/static/pedidos/` se traslada allí.
   - `templates/` global en la raíz (`TEMPLATES['DIRS']`, partiendo de lo que deje la 04-05) con `base.html`, `404.html`, `500.html` y `registration/login.html`.
   - Se verifica la configuración de estáticos del servidor (`collectstatic` y el mapeo de la pestaña **Web** de PythonAnywhere) en un archivo de evidencia.
3. **Parciales de plantilla (08-03):** `templates/partials/` con `_head.html`, `_nav.html` (navegación lateral o superior), `_header.html`, `_footer.html`, `_mensajes.html` (mensajes de Django), `_paginacion.html`, `_confirmacion_post.html` (el formulario con confirmación que introduce la 04-01), `_campo_formulario.html` y `_estado_vacio.html`, incluidos con `{% include %}`. La plantilla de acceso deja de tener su propia copia del `<head>` y de la configuración de Tailwind.
4. **Carpetas semánticas (08-04):** las plantillas de `pedidos/templates/pedidos/` se ordenan por dominio (`pedidos/`, `clientes/`, `cotizaciones/`, `productos/`, `pagos/`, `base_de_datos/`, `estadisticas/`, `trabajo_semanal/`, `pdf/`), con los nombres de plantilla actualizados en las vistas. Refactorización pura: las pantallas se ven igual.
5. **Tailwind compilado en local (08-05)** (RDA-010): Tailwind CSS v3 con pnpm, versiones exactas y `pnpm-lock.yaml` versionado; configuración de tema extraída de `base.html` y `login.html`; barrido de clases que cubre todas las plantillas y los parciales; CSS compilado versionado; `node_modules/` fuera del repositorio. En la misma iteración se resuelven el texto amarillo en modo claro (AUD-02-017) y el respaldo `cursive` de Bebas Neue (AUD-02-018). Compilar pasa a ser un paso de la lista de comprobación previa al despliegue.
6. **Tipografías e íconos autoalojados (08-06):** Inter y Bebas Neue en `static/fonts/` (solo los pesos usados, en `woff2`), y los íconos de Material Icons Round reemplazados por SVG en `static/icons/` con un parcial o una etiqueta de plantilla que los inserte (AUD-01-010). Se mide el espacio que ocupan frente a los 512 MiB. Incluye el `favicon.ico` que hoy responde 404 (propuesta de la sección 4 del registro).
7. **Librerías JavaScript (08-07):** ninguna librería desde CDN; cada una autoalojada y cargada solo en las páginas que la usan. Se decide qué hacer con cada una (RDA-016):
   - **Summernote** (editor enriquecido, necesita jQuery): mantenerla autoalojada o reemplazarla por un editor más liviano. El HTML que produzca sigue pasando por la sanitización de la 04-07.
   - **Select2** (necesita jQuery) y **SweetAlert2**: mantener, reemplazar o retirar.
   - **Interactividad y gráficos:** evaluar HTMX (actualizar partes de una página sin recargarla), Alpine.js (interacciones pequeñas) y Chart.js (gráficos) como alternativas livianas a una aplicación de una sola página.
   - `pedidos/static/pedidos/js/index.js` se revisa y se ordena por página.
8. **Política de seguridad de contenido estricta (08-08):** sin CDN, `SECURE_CSP` reemplaza al modo observación de la 04-09, con `nonce` para los scripts en línea que queden.
9. **Medición final del navegador (08-09):** repetir 08-01 y comparar.

## Iteraciones

| Iteración | Nombre | Origen |
| :-------- | :----- | :----- |
| 08-01 | Medición inicial del navegador | 5.6 (métricas del navegador) |
| 08-02 | Estáticos y plantillas globales | Nueva |
| 08-03 | Parciales de plantilla | Nueva |
| 08-04 | Plantillas en carpetas semánticas | Nueva |
| 08-05 | Compilación local de Tailwind con pnpm | 5.4 (antes 05-04) |
| 08-06 | Tipografías e íconos autoalojados | 5.5 (antes 05-05, parte de recursos) |
| 08-07 | Librerías JavaScript sin CDN | 5.5 (antes 05-05, parte de librerías) |
| 08-08 | Política de seguridad de contenido estricta | Nueva (continúa la 04-09) |
| 08-09 | Medición final del navegador | 5.6 (métricas del navegador) |

## Decisiones de la épica

- **2026-10-27 · Sin migración a React (RDA-016).** La aplicación sigue renderizada en el servidor con DTL. Una aplicación de una sola página exigiría una API, duplicar la autenticación y el CSRF, y un segundo proyecto con su propio proceso de compilación, y sumaría JavaScript justo en la épica que busca quitarlo. La generación de PDF (WeasyPrint) ocurre en el servidor y no cambia con ninguna librería del navegador.
- Cada librería que se agregue (HTMX, Alpine.js, Chart.js u otra) es una dependencia nueva: requiere consulta y queda en una RDA. `PENDIENTE_DESARROLLADOR`, se decide en 08-07.
- Tailwind v3, según RDA-010. Pasar a v4 requeriría una RDA nueva que la reemplace.
- 08-02 y 08-04 mueven archivos sin cambiar su contenido; se hacen con `git mv` para conservar el historial de cada plantilla.

## Fuera de alcance

- Rediseño visual de las pantallas. Esta épica cambia cómo se construyen y se sirven, no cómo se ven (salvo AUD-02-017 y AUD-02-018).
- Pantallas nuevas: Épicas 09 a 12, que ya usan los parciales.
- Cambiar la generación de PDF.

## Criterio de término

- Ninguna página carga recursos desde un dominio externo (verificado con la pestaña de red del navegador y con la política estricta sin violaciones).
- Reducción medida del tiempo hasta el primer contenido pintado, del peso transferido y del número de peticiones en las tres vistas, comparada con 08-01.
- Ninguna plantilla de página repite el `<head>`, la navegación o el pie: todas los incluyen desde `templates/partials/`.
- `pedidos/templates/pedidos/` organizado por dominio, y la suite de pruebas en verde.
- El paso «compilar estilos» figura en `docs/operacion/despliegue.md`.

## Notas

- **2026-10-27 (reorganización, RDA-014):** creada a pedido del desarrollador. Absorbe la compilación de estilos (antes 05-04), los recursos externos (antes 05-05) y las métricas del navegador de la antigua 05-06. `docs/operacion/despliegue.md` menciona la 05-04: se lee como 08-05.
