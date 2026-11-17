# Bitácora 04-02 · Cierre documental de la redacción (D1 a D6)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-02 queda **Pendiente (redactada, decisiones resueltas)**. Solo documentos.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Resuelta como |
| :- | :------------ |
| D1 | HSTS 3600 s y luego 604800 s tras la observación; sin `preload`. |
| D2 | Django **también** redirige (`SECURE_SSL_REDIRECT`), además de «Force HTTPS». Se ensaya en la réplica; se suma a riesgos, pruebas y retroceso. Se cambió la recomendación de la redacción (era confiar solo en Force HTTPS). |
| D3 | Variable de entorno explícita, no derivada de `DEBUG` (`SEGURIDAD_PRODUCCION`, nombre fijado el 2026-11-17). Riesgo de olvidarla registrado. |
| D4 | `CSRF_TRUSTED_ORIGINS` del entorno, con valor local por defecto. |
| D5 | No arranca con el dominio de producción y la variable apagada (compensa D3). |
| D6 | 3 días de observación antes de subir HSTS (sustituye 7). |
| 04-01 | Etiqueta `v4.1-mutaciones-post`; fecha al cerrar la vigilancia de la 03-05 (no antes del 2026-11-23 23:48). |

## Observaciones al redactar el cierre

- **El ensayo de D2 en la réplica no puede descartar el bucle:** `runserver` no sirve HTTPS, así que confirma la redirección pero no cómo el proxy de PythonAnywhere entrega el esquema. El bucle solo se verifica en producción (verificación 3, con `curl -sIL`); por eso el retroceso del caso 1 queda listo.
- **D5 condiciona el retroceso rápido:** apagar la variable en el servidor no basta, porque D5 impide arrancar así con el dominio de producción; hay que volver también el código. Se ensaya cuál camino se documenta.
- **Orden en el servidor:** `.env` → código → Reload; si se recarga código nuevo sin la variable, el sitio no arranca.
- **04-01 (confirmado, sin cambios):** su tabla de pruebas ya incluye retirar `test_errores.test_regresion_eliminar_pago_deja_tipo_y_traza` y revisar `test_acceso.PkInexistenteTests` y R20.

## Archivos

`iteracion-04-02-configuracion-de-produccion.md`, `iteracion-04-01-mutaciones-solo-por-post.md` (etiqueta), `definicion-epica-04.md`, `00_producto/registro-pendientes.md` (editado por bytes, CRLF intacto) y esta bitácora.
