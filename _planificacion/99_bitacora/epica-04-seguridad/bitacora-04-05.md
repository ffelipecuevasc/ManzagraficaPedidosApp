# Bitácora 04-05 · Correcciones de configuración

- **Fecha:** 2026-11-19
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** Implementada, pendiente de despliegue. Etiqueta prevista `v4.7-correcciones-config`, sin fecha fija (RDA-021); retroceso `v4.6-restauracion`. La revisión manual en la réplica (escritorio y 360 px) está **pendiente de ejecutar por el desarrollador**.
- **Regla:** ningún valor de clave, ningún contenido de volcado y ningún nombre de persona en este documento.

## Resumen

AUD-01-009, AUD-01-016, AUD-01-025, AUD-02-016 y la parte (2) de AUD-05-008, corregidos en código. Clase 1: sin migraciones ni cambios de pantalla. `settings.py` editado con la consulta previa aprobada el 2026-11-19, solo en los cuatro puntos autorizados. Punto 6 del alcance retirado (la línea ya no existía). AUD-01-016 queda «corregido en código, pendiente de verificar en producción» (hibernación, observación posterior).

## Decisiones del desarrollador (2026-11-19, dichas por él)

- Consulta previa aprobada para `settings.py`: `conn_health_checks=True` (con `conn_max_age=60`), `BASE_DIR` una vez, `DIRS=[]` y la coma suelta. Sin tocar los bloques de la 04-02.
- D2 cubre las **nueve** pruebas que parchaban `views.settings`.
- Punto 6 del alcance retirado.
- Verificación 3 (hibernación): observación posterior, no bloquea el cierre; puntos 1 y 2 el mismo día.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `PedidosApp/settings.py` | `BASE_DIR` una vez; `DIRS: []` sin la coma suelta; `conn_health_checks=True` (CRLF). |
| `pedidos/views.py` | `from django.conf import settings`; `F` una vez; sin `HttpResponseForbidden` (LF). |
| `pedidos/urls.py` | Sin la importación redundante (CRLF). |
| `pedidos/tests/test_configuracion.py` | Nuevo: 4 pruebas (LF). |
| `test_acceso.py`, `test_capturas_amplias.py`, `test_contrato_error.py` (CRLF), `test_dinero.py`, `test_eventos_negocio.py`, `test_regresiones.py` (CRLF), `test_restauracion_endurecida.py` | Nueve parches de `views.settings.BASE_DIR` → `self.settings(BASE_DIR=...)`; en `test_dinero.py`, fuera `mock` y `views` sin uso. |
| `docs/operacion/despliegue.md` | Sección 3.12 (revisión manual y orden) y fila en la sección 5 (CRLF). |
| `_planificacion/00_producto/auditoria-tecnica.md` | Estado de los cinco hallazgos y nota de H3. |
| Iteración, `definicion-epica-04.md`, `registro-pendientes.md` (CRLF), esta bitácora | Estado. |

**Fuera del repo** (carpeta temporal de esta sesión del agente):

- `C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\f2f9a3a5-9ccf-4bf1-97a7-8cd78d581188\scratchpad\despliegue-04-05\clase1_04_05.py` (comprobación de Clase 1; no imprime credenciales).
- `C:\Users\ffeli\AppData\Local\Temp\claude\ffeca7695322248c\f2f9a3a5-9ccf-4bf1-97a7-8cd78d581188\scratchpad\despliegue-04-05\revisar_volcado_d2.py` (copia sin cambios del script D2 de la 04-04, para el paso 1 del despliegue).

## Correcciones a la redacción

- Líneas: import en `views.py:21`; `DIRS` en `settings.py:141`; `conn_max_age` en `:191`; `TruncMonth` en `views.py:611`.
- Nueve parches, no seis (ver la iteración).
- **Orden del paso 2 invertido:** con el import viejo, `override_settings` no llega a `views.py` y las pruebas habrían usado el `backups/` real. Primero el import (suite en verde con los parches viejos), después las pruebas.
- `python -c` reemplazado por un script en la carpeta temporal (`AGENTS.md`, sección 5).
- **`check --deploy` local:** el pedido esperaba W005, W009 y W021. Con la clave generada y `SEGURIDAD_PRODUCCION=True` sale **solo W005 y W021** (W009 ya no aparece desde la 04-03: la clave generada cumple y una que no cumpla da `ImproperlyConfigured`). Coincide con `despliegue.md`, sección 2.

## Verificación: línea base y resultado

| Comprobación | Línea base (`v4.6`, antes del cambio) | Resultado |
| :----------- | :------------------------------------ | :-------- |
| `test pedidos` | 375 pruebas, `OK (expected failures=4)` | 379 pruebas, `OK (expected failures=4)` (375 + 4 nuevas) |
| `check` | Sin problemas | Sin problemas |
| `check --deploy`, `DEBUG=False`, `SEGURIDAD_PRODUCCION=True`, clave generada | W005, W021 | W005, W021 |
| `check --deploy`, `DEBUG=False`, sin `SEGURIDAD_PRODUCCION`, clave generada | (no medido antes) | W004, W008, W012, W016 (las de la variable apagada, como dice `despliegue.md`) |
| `check --deploy` con la clave del `.env` local y `SEGURIDAD_PRODUCCION=True` | `ImproperlyConfigured` (clave local corta) | `ImproperlyConfigured` (igual) |
| `makemigrations --check --dry-run` | `No changes detected` | `No changes detected` |
| Script de Clase 1, local | `BASE_DIR` = raíz; `DIRS` = `[<raíz>/templates]`; `CONN_MAX_AGE` 0; `CONN_HEALTH_CHECKS` False; `views.settings is django.conf.settings` False | Mismo `BASE_DIR`; `DIRS` = `[]`; 0; False; **True** |
| Script de Clase 1, con `DATABASE_URL` de ejemplo | `CONN_MAX_AGE` 60; `CONN_HEALTH_CHECKS` False | 60; **True** |
| `grep -rn "from PedidosApp import" pedidos` | `views.py:21` | Solo el comentario de la prueba nueva |
| `grep -rn "views.settings, 'BASE_DIR'" pedidos/tests` | 9 | 0 |

Suite tras cada cambio: import → 375 OK; pruebas migradas + 4 nuevas → 379 con 3 fallos (2 esperados: `DIRS` y salud; 1 de la propia prueba local, que leía el diccionario sin los valores por defecto de Django; corregida para leer `connections.settings`); `settings.py` → 379 OK; importaciones → 379 OK.

**`backups/` real:** se tomó una huella del listado antes de empezar, pero la comprobación posterior la bloqueó el permiso del entorno (listar `backups/`), y no se insistió. **No verificado por el agente.** Indicio: ninguna prueba conserva un parche al módulo; todas usan `self.settings(BASE_DIR=<carpeta temporal>)`, que también llega a `utils.py:151`. Comprobación sugerida para el desarrollador: `Get-ChildItem backups | Measure-Object` antes y después de `python manage.py test pedidos` (mismo número y mismas fechas).

**Revisión manual a 360 px y en escritorio: no hecha por el agente** (no abrió el navegador). Paso a paso abajo.

## Revisión manual en la réplica (PowerShell 7)

Es el texto de `despliegue.md`, sección 3.12 A: proyecto y `.venv`; contenedor arriba; `DB_NAME=manzagrafica_replica` y paridad `0`; `runserver`; panel (`/`), lista (`/pedidos/lista/`), un detalle, `/base_datos/respaldar_bd/` (sin generar), `/base_datos/restaurar_bd/` (solo carga) y el PDF de una cotización; las cinco primeras a 360 px; ante error 500 o `TemplateDoesNotExist`, no desplegar; limpieza con `Remove-Item Env:DB_NAME` y `docker compose stop`.

## Orden de despliegue de `v4.7-correcciones-config`

`despliegue.md`, sección 3.12 B:

1. Respaldo de producción **antes del checkout**, `VÁLIDO` y `CUMPLE D2`, con SHA-256 anotado.
2. Etiqueta `v4.7-correcciones-config`; `git diff --stat` sin `requirements.txt`, migraciones ni estáticos.
3. Checkout y `git describe`.
4. `check --deploy` antes del Reload: solo W005 y W021.
5. **Un** Reload, confirmado con una línea `Starting uWSGI`; no repetirlo.
6. Verificaciones 1 y 2 y registros sin errores el mismo día.
7. Hibernación: observación posterior (AUD-01-016).
8. Retroceso: `retroceso.md`, caso 1, a `v4.6-restauracion`.

## Riesgos y lo que no se vio

- **`conn_health_checks` no tiene efecto en local** (sin `CONN_MAX_AGE`); la prueba solo confirma la configuración, no la reconexión. Se observa en producción.
- **`DIRS` vacío:** la carpeta `templates/` de la raíz sigue existiendo vacía en esta copia, sin versionar; no se tocó. La revisión manual confirma que ninguna pantalla dependía de ella.
- **Sin `TruncMonth`** (Épica 06), sin `MEDIA_ROOT` con `Path` y sin estilos de AUD-05-008 parte (1) (Épica 08): fuera.
- No se vio: el `.env`, el contenido de `backups/` (ni su listado posterior), el servidor y las pantallas en un navegador.
- D5 de la 04-03 sigue `PENDIENTE_DESARROLLADOR`.
