# Iteración 00-06 · Correcciones tempranas de riesgo nulo

- **Épica:** 00 · Blindaje y punto de retorno
- **Estado:** Pendiente
- **Subfase del plan:** 0.6
- **Depende de:** 00-05
- **RDA relacionadas:** RDA-007
- **Hallazgos que cierra:** AUD-01-020, AUD-01-021. Avanza AUD-01-011 (la revisión del resto de importaciones va en 05-01) y AUD-01-024 (la normalización completa de rutas va en 06-06).
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no toca datos), pero sí etiqueta propia

## Objetivo

Un despliegue temprano y aislado con cuatro correcciones que no tocan datos, lógica de negocio ni estructura, y cuyo beneficio se mide en el registro del servidor desde el día siguiente.

## Tareas

1. **Carga diferida de WeasyPrint.** Mover `import weasyprint` de la cabecera de `pedidos/views.py` al interior de `exportar_cotizacion_pdf`, con un comentario breve que explique por qué está ahí.
2. **`robots.txt`.** Una ruta `robots.txt` que responde `text/plain` con `User-agent: *` y `Disallow: /`, sin exigir sesión y sin renderizar plantillas.
3. **Doble envío en el acceso.** En `registration/login.html`, deshabilitar el botón de ingresar al primer envío y mostrar que se está procesando, con JavaScript propio de la plantilla (la página de acceso no carga `index.js`).
4. **Barra final en pagos.** Cambiar la ruta `pagos/lista` por `pagos/lista/`. Las plantillas usan `{% url 'lista_pagos' %}`, así que no cambian; las direcciones guardadas sin barra siguen funcionando porque Django redirige a la versión con barra.
5. **Medición de arranque** antes y después: tiempo de importar `pedidos.urls` después de `django.setup()`, en tres corridas, y comprobación de que `weasyprint` no está en `sys.modules` tras importar las vistas.
6. **Archivo de evidencia** `evidencia-00-06.md`: después del despliegue, contar en el registro del servidor las desconexiones y las peticiones a `/robots.txt` de los siete días siguientes, con el mismo método de 00-01.

## Criterios de aceptación

- [ ] Tras importar `pedidos.views`, `'weasyprint' in sys.modules` es `False` (comando y salida en la bitácora).
- [ ] El tiempo medio de importación de `pedidos.urls` baja respecto de la medición previa (tres corridas antes y tres después, en la bitácora).
- [ ] En local, la exportación de una cotización a PDF responde 200 con `Content-Type: application/pdf` y un cuerpo que empieza con `%PDF`.
- [ ] En local, `GET /robots.txt` sin sesión responde 200, `text/plain`, con `Disallow: /`.
- [ ] En local, `GET /pagos/lista/` responde 200 con sesión y `GET /pagos/lista` redirige a `/pagos/lista/`.
- [ ] El botón de acceso queda deshabilitado tras el primer clic y vuelve a estar disponible si el acceso falla y la página se recarga (revisado en escritorio y a 360 px).
- [ ] El despliegue tiene su propia etiqueta, distinta de la de 00-04.
- [ ] La evidencia muestra el conteo de desconexiones y de 404 de `/robots.txt` de la semana posterior, comparado con la línea base de 00-01.

## Fuera de alcance

- Diferir otras importaciones (va en 05-01).
- Prevenir el doble envío en los demás formularios (se evalúa en 03-04 junto con el contrato de error).
- Renombrar otras rutas (va en 06-06).

## Datos requeridos del cliente

- Ninguno.
