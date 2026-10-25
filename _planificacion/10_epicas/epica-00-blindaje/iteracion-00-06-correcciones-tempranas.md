# Iteración 00-06 · Correcciones tempranas de riesgo nulo

- **Épica:** 00 · Blindaje y punto de retorno
- **Estado:** Terminada (2026-10-25; desplegada el 2026-10-23 como `v0.2-correcciones`)
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
6. **Archivo de evidencia** `evidencia-00-06.md`: después del despliegue, contar por fecha, con el método reutilizable de `evidencia-00-01.md`, las 404 de `/robots.txt` por día (señal principal, cierra la iteración cuando bajan a 0) y las desconexiones `Broken pipe` por día (señal secundaria). Las desconexiones se informan en un segundo pedido a los 28 días del despliegue, sin umbral y sin bloquear el inicio de la Épica 01.

## Criterios de aceptación

- [x] Tras importar `pedidos.views`, `'weasyprint' in sys.modules` es `False` (comando y salida en la bitácora). Antes `True`, después `False`.
- [x] El tiempo medio de importación de `pedidos.urls` baja respecto de la medición previa (tres corridas antes y tres después, en la bitácora). Media de 1.029,0 ms a 26,3 ms.
- [x] En local, la exportación de una cotización a PDF responde 200 con `Content-Type: application/pdf` y un cuerpo que empieza con `%PDF`. Cotización 5: `200`, `application/pdf`, `%PDF`; en producción también se generó.
- [x] En local, `GET /robots.txt` sin sesión responde 200, `text/plain`, con `Disallow: /`. HEAD también da 200 (`require_safe`).
- [x] En local, `GET /pagos/lista/` responde 200 con sesión y `GET /pagos/lista` redirige a `/pagos/lista/`. `200` y `301`.
- [x] El botón de acceso queda deshabilitado tras el primer clic y vuelve a estar disponible si el acceso falla y la página se recarga (revisado en escritorio y a 360 px). Revisado en Firefox, las cinco revisiones en «Sí».
- [x] El despliegue tiene su propia etiqueta, distinta de la de 00-04. `v0.2-correcciones` (commit `7944943`), recarga el 2026-10-23 a las 18:35 Chile; partida `v0.1-higiene`.
- [x] La evidencia muestra, con el conteo por fecha de 00-01, la tasa diaria de 404 de `/robots.txt` (señal principal; línea base: 7 en los 7 días del 2026-10-15 al 2026-10-21; las líneas de muestra revisadas son de Googlebot) y de desconexiones `Broken pipe` (señal secundaria; línea base: 4 en esos 7 días y 0,44 por día en 89 días). La iteración se da por cumplida cuando las 404 de `/robots.txt` bajan a 0. Las desconexiones se informan a los 28 días del despliegue, sin umbral, en paralelo y sin bloquear el inicio de la Épica 01.
  - **Resultado (C1, 2026-10-25):** del 19 al 22 de octubre, 9 de 9 peticiones de `/robots.txt` dieron 404; desde el despliegue, 0. La única petición posterior (2026-10-23, verificación manual) dio 200; el 24 y el 25 ningún rastreador la pidió. `Broken pipe`: 3 en 7 días, igual que la línea base. **Cerrada por decisión del desarrollador**, con seguimiento: confirmar que un rastreador real recibe 200 al repetir el conteo junto con C2 (2026-11-20).

## Fuera de alcance

- Diferir otras importaciones (va en 05-01).
- Prevenir el doble envío en los demás formularios (se evalúa en 03-04 junto con el contrato de error).
- Renombrar otras rutas (va en 06-06).

## Datos requeridos del cliente

- Ninguno.
