# Bitácora 04-08 · Protección del acceso y límites de entrada

- **Fecha:** 2026-11-21
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** **En revisión, pendiente de despliegue.**
  - Etiqueta prevista: `v4.10-acceso-limites`. Retroceso: `v4.9-sanitizacion-html`, que sigue siendo la versión estable vigente.
  - Falta: la revisión manual en la réplica (paso 6), pegar el texto de `.env.example` y el despliegue con la medición de la dirección (`despliegue.md` 3.15).
- **Regla:** solo conteos, tiempos e identificadores. Ningún nombre de usuario, dirección IP, contenido ni monto.
- **Marcas:** «Consola»: el desarrollador pegó la salida y se vio. «Dicho»: lo afirma el desarrollador. «Agente»: lo ejecutó el agente en local. «Inferido»: sin verificar.

## Resumen

El acceso (`accounts/login/` y el admin) cuenta fallos por usuario y por dirección en una caché local dedicada. Con 5 fallos de un usuario o 20 de una dirección en 15 minutos, bloquea 15 minutos. El bloqueo se revisa **antes** de `authenticate()`, así que un intento bloqueado no escribe más eventos; cada bloqueo deja **un** evento `acceso_bloqueado` (migración `0009`, Clase 1). `accounts/login/` redirige al panel si ya hay sesión. La imagen de referencia tiene tope de 5 MB, y un middleware rechaza sin leerlo el POST demasiado grande a crear o editar pedidos y a restaurar. 35 pruebas nuevas.

## Estado de partida (agente)

- `main` = `90d5107` (commit de la Tarea 1, dicho: hecho y publicado por el desarrollador).
- Última migración: `0008_proteger_historial_cliente`. Sin formularios de acceso propios, sin `admin.site.login_form`, sin `CACHES`, sin límites de subida explícitos, sin variables `ACCESO_`.
- Desfases de línea respecto de la redacción (no cambian el diseño): `restaurar_bd` está en `views.py:1304` (la redacción decía `:1250`); el tope de 20 MB es `TOPE_VOLCADO_BYTES` en `utils.py`.

## Evidencia previa (paso 2)

- **Réplica:** refresco del **2026-11-18**. **Del 2026-11-18 al 2026-11-21 no hay medición.**
- **Paridad (consola):** 0 diferencias no aceptadas (Python 3.13.0 frente a 3.13.1, aceptada).
- **Respaldo de la réplica (consola):** `replica_antes_04-08.sql`, 1.537.213 bytes, 19 de 19, `CUMPLE D2`, SHA-256 `E88572C477C739AB6C6E3FFC77321485035BA5EAC8CFF33B0CDF3F65BC64BE17`.
- **Fallos por ventana (consola, réplica):** 1 `acceso_fallido` en total, del 2026-10-26 01:12:58 UTC, de un usuario existente; máximo por ventana de 15 minutos: 1. Umbral de detención: 4. **No se activa.** La consulta no devolvía `resumen`, solo conteos y una marca de usuario desconocido.
- **`media/referencias/` en producción (dicho, panel; servidor en `v4.9-sanitizacion-html`):** 2 archivos; el mayor, 624.912 bytes. Tope: 5 MB. **No se activa.**

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/limite_acceso.py` | Nuevo. Constantes de D2 y D5, `direccion_cliente` (D3), contadores y bloqueos en el alias `acceso`, y `LimiteCuerpoMiddleware`. |
| `pedidos/forms.py` | `LimiteAccesoMixin`, `FormularioAcceso`, `FormularioAccesoAdmin`; `PedidoForm.clean_imagen_referencia` (5 MB). |
| `pedidos/senales.py` | Receptores `contar_fallo` (`user_login_failed`, escribe `acceso_bloqueado`) y `reiniciar_contador` (`user_logged_in`). |
| `pedidos/admin.py` | `admin.site.login_form = FormularioAccesoAdmin`. |
| `pedidos/models.py` | `('acceso_bloqueado', 'Acceso bloqueado')` en `TIPO_CHOICES`. |
| `pedidos/migrations/0009_acceso_bloqueado.py` | Nueva, `AlterField` de `RegistroEvento.tipo` (Clase 1). |
| `pedidos/templates/registration/login.html` | Rama `form.bloqueado` con «Acceso bloqueado por 15 minutos», `role="alert"`, sin animación. |
| `PedidosApp/settings.py` | `DATA_UPLOAD_MAX_MEMORY_SIZE` y `FILE_UPLOAD_MAX_MEMORY_SIZE` en 2.621.440; `CACHES` (`default` igual al defecto y `acceso` con `MAX_ENTRIES` 2000); `ACCESO_PROXIES_CONFIABLES` (0) y `ACCESO_FALLOS_POR_DIRECCION` (20), con `ImproperlyConfigured` ante un valor inválido; middleware al final de `MIDDLEWARE`. |
| `PedidosApp/urls.py` | `accounts/login/` con `FormularioAcceso` y `redirect_authenticated_user=True`, antes de `accounts/`. |
| `pedidos/tests/test_limite_acceso.py` | Nuevo, 25 pruebas. |
| `pedidos/tests/test_limites_subida.py` | Nuevo, 10 pruebas. |
| `pedidos/tests/test_eventos_negocio.py` | `EventosAccesoTests` vacía la caché `acceso` en `setUp`. |
| `docs/operacion/desbloqueo-de-acceso.md` | Nuevo. |
| `docs/operacion/despliegue.md` | Sección 3.15 y fila prevista en la sección 5. |
| Iteración 04-08, registro, auditoría | Estado, evidencia y AUD-03-004. |

## Verificación (agente)

- Pruebas primero: las 35 nuevas antes de implementar → `FAILED (failures=6, errors=23)`. Los 23 errores son por el alias de caché `acceso`, que no existía; los 6 fallos, por comportamiento (redirección, chequeo temprano en tres rutas, imagen grande en el formulario y en la vista). Las 6 que ya pasaban se cumplían antes del cambio: los dos 2,5 MB (son el defecto de Django), la imagen del tope exacto, el `.sql` de 3 MB, el cuerpo justo en el tope, las rutas no revisadas y el GET sin sesión.
- Después: las 56 de los tres archivos tocados → `OK`. `python manage.py test pedidos` → **446 pruebas, `OK (expected failures=3)`** (411 de la línea base más 35).
- `python manage.py check` → `System check identified no issues (0 silenced).`
- `python manage.py makemigrations --check --dry-run` → `No changes detected`.
- `check --deploy` no se corrió con la configuración nueva; lo hace el desarrollador en 3.15 B.5.
- Revisión de pantallas en escritorio y a 360 px contra la réplica: **no consta** (pasos en 3.15 A).

## Migraciones

`0009_acceso_bloqueado.py` · **Clase 1** · dependencia `("pedidos", "0008_proteger_historial_cliente")`. `sqlmigrate pedidos 0009` contra la réplica (agente):

```sql
--
-- Alter field tipo on registroevento
--
-- (no-op)
```

Aplicada en la réplica con `migrate pedidos` (agente): `Applying pedidos.0009_acceso_bloqueado... OK` y `[X] 0009_acceso_bloqueado`. Apareció la advertencia conocida `mysql.W002` (AUD-02-020). Para volver la réplica: `python manage.py migrate pedidos 0008` con `DB_NAME` de la réplica.

## Criterios de aceptación

- [x] Tabla de pruebas en verde, incluido el bloqueo por N intentos y su evento (agente).
- [x] `sqlmigrate pedidos 0009` copiado, sin SQL; `0009` después de la `0008` (agente).
- [x] Evidencia previa sin activar la regla de detención (consola: fallos; dicho: archivo más grande). Réplica hasta el 2026-11-18.
- [ ] Revisión manual en la réplica: **no consta**.
- [ ] Verificación 3 de producción y valor de proxies: pendiente del despliegue (3.15 C).
- [x] AUD-03-004 «Corregido en código, pendiente de verificar en producción» y procedimiento de desbloqueo escrito (agente).

## Decisiones tomadas

- **Chequeo temprano en un middleware y no en las vistas (decisión del desarrollador, 2026-11-21).** `CsrfViewMiddleware` lee `request.POST` en su `process_view` (`django/middleware/csrf.py:368`), así que en la vista el archivo ya se recibió. El middleware va al final de `MIDDLEWARE`: corre antes que cualquier `process_view` y ya tiene sesión, usuario y mensajes. La prueba lo comprueba sustituyendo `MultiPartParser.parse`: no se llama. `views.py` no cambió.
- **Respuesta del rechazo por tamaño:** mensaje y redirección (302) a la misma ruta, no un 400 ni un 413 sin pantalla. Deja una línea `INFO` sin contenido.
- **Solo cuentan los intentos con petición.** `authenticate()` sin petición (por ejemplo `client.login()` o código interno) no suma a los contadores.
- **Al empezar un bloqueo se borra la cuenta de fallos de esa clave;** al vencer el bloqueo se empieza de cero.
- **Evento:** `entidad='usuario'`, `entidad_id` solo si el bloqueo es por usuario y el usuario existe; el resumen dice «Bloqueo de 15 minutos por usuario», «por dirección» o «por usuario y dirección». Nunca la dirección ni el nombre escrito.
- **Variables inválidas detienen el arranque** (`ImproperlyConfigured`), como `SECRET_KEY`. Se ve en `check --deploy` antes del Reload (3.15 B.5).
- **Textos nuevos, escritos por el agente y sin aprobar** (`PENDIENTE_DESARROLLADOR` si se quieren otros): «Acceso bloqueado por 15 minutos», «Hubo demasiados intentos fallidos. Espera 15 minutos y vuelve a intentarlo.», «La imagen de referencia supera los 5 MB. Elige una imagen más liviana.» y «El archivo supera el tamaño permitido y no se recibió. No se guardó nada.» Las pruebas los fijan literales.
- **Despliegue con medición:** se entra con `ACCESO_FALLOS_POR_DIRECCION=3` y un Reload de ajuste deja los valores finales (3.15 C). La verificación 3 (c) de la iteración, falsificar `X-Forwarded-For` en producción, se reemplaza por la prueba automatizada `FalsificacionTests`.

## Texto para `.env.example` (lo pega el desarrollador)

Una regla de permisos de `.claude/` impidió al agente leer `.env.example`, así que no se sabe dónde va mejor. Propuesta, al final del archivo:

```
# Límite de intentos de acceso (04-08). Ambas son opcionales.
# Cantidad de proxies propios delante de la web app. Sin definir o 0: se usa REMOTE_ADDR.
# En producción se mide (docs/operacion/despliegue.md, 3.15 C); no lo supongas.
ACCESO_PROXIES_CONFIABLES=
# Fallos por dirección en 15 minutos antes del bloqueo (defecto 20). 0 apaga solo este contador:
# es el interruptor de emergencia si todos quedan bloqueados (docs/operacion/desbloqueo-de-acceso.md).
ACCESO_FALLOS_POR_DIRECCION=
```

Vacías equivalen a no definidas (`settings.py` trata el texto vacío como ausente).

## Pendientes y riesgos

- **Revisión manual en la réplica (3.15 A):** no consta.
- **Dirección real en producción:** no verificada. Si `REMOTE_ADDR` es el proxy y se deja `0`, 20 fallos de cualquiera bloquean a todos. Mitigación: medición 3.15 C e interruptor `ACCESO_FALLOS_POR_DIRECCION=0`.
- **Respuesta sin leer el cuerpo:** no verificado si el proxy o uWSGI de PythonAnywhere cortan la conexión con un cuerpo grande sin leer (el navegador podría mostrar un error de conexión en vez del mensaje). El rechazo ocurre igual.
- **Contadores en memoria:** se pierden en cada recarga o reinicio; el límite frena, no impide.
- **IPv6** (no verificado): un atacante con un bloque propio puede rotar de dirección; el contador por usuario sigue protegiendo.
- **Un tercero que conozca un nombre de usuario** puede bloquearlo 15 minutos (aceptado en D2).
- **`definicion-epica-04.md`** sigue mostrando la 04-08 como «Pendiente» en su tabla: no se tocó (no estaba en el cierre pedido).
- **`retroceso.md`:** no se editó; 3.15 D remite al caso 2, que ya rige para la Clase 1.

## Commit sugerido

`Épica 4 - Iteración 04-08: límite de intentos con evento acceso_bloqueado (0009, Clase 1), imagen de 5 MB y chequeo temprano del cuerpo; sin desplegar` (150 caracteres)
