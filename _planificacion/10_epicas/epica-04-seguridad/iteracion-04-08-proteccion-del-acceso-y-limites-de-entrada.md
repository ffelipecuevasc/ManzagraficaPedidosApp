# Iteración 04-08 · Protección del acceso y límites de entrada

- **Épica:** 04 · Seguridad y endurecimiento
- **Estado:** Pendiente (redactada, decisiones resueltas). Redactada el 2026-11-17 ([bitacora-04-08-redaccion](../../99_bitacora/epica-04-seguridad/bitacora-04-08-redaccion.md)); D1 a D5 resueltas por el desarrollador el mismo día ([bitacora-04-08-cierre](../../99_bitacora/epica-04-seguridad/bitacora-04-08-cierre.md)).
- **Subfase del plan:** nueva (Auditoría 03); `definicion-epica-04.md`, alcance 8 y decisión de la épica sobre la 04-08.
- **Depende de:** la 04-04 (tope de 20 MB de la restauración, que esta iteración coordina) y las que editan `settings.py` (04-02, 04-03, 04-05): la 04-08 parte de lo que dejen. Se redactó en paralelo a la vigilancia de la 03-05; **su ejecución en local no empieza hasta cerrar esa vigilancia** (decisión del desarrollador, 2026-11-17). **No se despliega antes de cerrar la vigilancia (desde el lunes 2026-11-23 a las 23:48:12).** Orden de despliegue (RDA-007, un propósito cada uno): 04-01 → 04-10 → … → 04-07 → **04-08**.
- **Es requisito de:** la Épica 09 (precondición: «más cuentas, más superficie para fuerza bruta»; registro, fila 09-01).
- **RDA relacionadas:** RDA-007. **Sin RDA nueva:** D1 no agrega dependencia (la siguiente libre sería la RDA-021, porque la RDA-020 está propuesta para la 04-07).
- **Hallazgos que cierra:** AUD-03-004. **Propuesta que absorbe:** redirigir al panel desde el acceso cuando ya hay sesión (registro, sección 4, fila de 00-06). **No cierra:** AUD-02-030 (recuperación de contraseña y acceso propio del admin), que sigue aparte.
- **Cambio de esquema (D4):** **Clase 1**, una migración de metadatos (`choices` de `RegistroEvento.tipo`). **Numeración verificada el 2026-11-17:** `pedidos/migrations/` llega hasta `0007_registroevento`; la 04-06 crea la `0008` y esta iteración, que se despliega después, crea la **`0009`** con dependencia en la `0008` de la 04-06 (nombre exacto de la dependencia: el que dé `makemigrations`). Si al ejecutar la 04-06 aún no está creada, la numeración se revisa con `showmigrations pedidos` antes de escribir nada.
- **Respaldo previo al despliegue:** **sí**, obligatorio: hay migración.
- **Archivos que tocará la ejecución:** `pedidos/limite_acceso.py` (nuevo), `pedidos/forms.py` (formularios de acceso y validación de la imagen), `pedidos/senales.py`, `pedidos/admin.py` (`admin.site.login_form`), `pedidos/views.py` (chequeo temprano del tamaño del cuerpo), `pedidos/templates/registration/login.html`, `pedidos/models.py` y `pedidos/migrations/0009_…` (**consulta previa** para `makemigrations` y `migrate`), pruebas nuevas, `docs/operacion/` (procedimiento de desbloqueo) y **archivos de configuración con consulta previa** (`AGENTS.md`, sección 6): `PedidosApp/settings.py` (`CACHES`, límites de subida, variables de proxies y de límite por dirección), `PedidosApp/urls.py` (la vista de acceso con redirección) y `.env.example`.

## Objetivo

Que adivinar una contraseña por intentos repetidos sea inviable en las dos entradas de acceso que existen hoy, que cada bloqueo deje un evento, que ninguna subida pueda ocupar más memoria o disco del razonable, y que el cliente legítimo pueda volver a entrar sin ayuda técnica compleja.

## Cómo se lee este documento

- **Verificado en el repo:** leído el 2026-11-17 en `main`, con archivo y línea. Lo que dice cómo se comporta Django se leyó en el código de Django 6.0.1 instalado en `.venv` (solo lectura; no se ejecutó nada).
- **Inferido:** sale de leer el código o la documentación; se dice cómo se confirma.
- **No verificado (producción):** solo se ve en el servidor.

## Qué hay hoy (verificado)

### Las dos entradas de acceso

- **`accounts/login/`:** `PedidosApp/urls.py:25` incluye `django.contrib.auth.urls`; la vista es el `LoginView` de Django con la plantilla `pedidos/templates/registration/login.html`. `LoginView.redirect_authenticated_user` vale `False` por defecto (`django/contrib/auth/views.py:77`): con sesión iniciada, la página muestra de nuevo el formulario. Esa misma inclusión publica además el cambio y la recuperación de contraseña (AUD-02-030, fuera de alcance).
- **Admin de Django:** `PedidosApp/urls.py:24`, ruta **no estándar** `acceso-manzagrafica-admin/`. Su acceso usa `AdminAuthenticationForm` salvo que `admin.site.login_form` diga otra cosa (`django/contrib/admin/sites.py:55` y `:446`), y **ya redirige** al índice si hay sesión (`sites.py:419-422`).
- Ambos llaman a `authenticate()` a través de un formulario que deriva de `AuthenticationForm` (`django/contrib/auth/forms.py:344-357`, `clean()`).

### Lo que existe y lo que falta

- **Registro:** `senales.py:17-26` ya escucha `user_login_failed` y escribe `acceso_fallido` (usuario nulo, resumen con el nombre solo si existe como usuario, nunca la contraseña, decisión del 2026-10-25). Pruebas: `test_eventos_negocio.py:176-215`.
- **Hecho comprobado en Django:** `authenticate()` emite `user_login_failed` también cuando un backend lanza `PermissionDenied` (`django/contrib/auth/__init__.py:107-128`: el `break` termina en la señal). Consecuencia: **bloquear dentro de un backend no evita que cada intento bloqueado escriba otra fila `acceso_fallido`.** Bloquear antes de llamar a `authenticate()` (en el `clean()` del formulario) sí lo evita.
- **Nada limita los intentos.** Un ataque de fuerza bruta hoy produce además **una fila de evento por intento**, sin tope, en un disco de 512 MiB compartido (el evento se conserva 365 días, `eventos.py`, retención 365): el atacante también llena la tabla.
- **Caché:** `settings.py` no define `CACHES` (búsqueda), así que rige el de memoria local de Django, **por proceso**. Por defecto guarda **300 entradas** y, al llenarse, borra una tercera parte (`MAX_ENTRIES` 300 y `CULL_FREQUENCY` 3 en `django/core/cache/backends/base.py:71` y `:77`). Sus operaciones `add` e `incr` son atómicas con un candado (`locmem.py`). Ningún código de la aplicación usa la caché hoy (búsqueda de `cache` en `pedidos/`).
- **Dirección del cliente:** ningún código la lee (búsqueda de `REMOTE_ADDR` y `X-Forwarded` en `pedidos/` y `PedidosApp/`: sin resultados). **Django no interpreta `X-Forwarded-For`**; solo conoce `SECURE_PROXY_SSL_HEADER` y las variantes de host y puerto (`global_settings.py`).
- **Pruebas de acceso:** solo `test_eventos_negocio.py` envía credenciales a `/accounts/login/` (línea 176); `test_acceso.py:106` hace un GET. Como la caché local **no se vacía entre pruebas**, los intentos fallidos de una prueba se sumarían a los de otra desde la misma dirección de prueba (`127.0.0.1`): las pruebas nuevas y las existentes que fallan accesos deben vaciar la caché (riesgo y paso).

### Subidas de archivos

| Qué | Dónde | Estado hoy |
| :-- | :---- | :--------- |
| Imagen de referencia | `Pedido.imagen_referencia`, `models.py:42` (`ImageField`, `upload_to='referencias/'`); `crear_pedido` (`views.py:212`) y `editar_pedido` (`:317`) pasan `request.FILES` a `PedidoForm` | Django comprueba que sea una imagen válida (Pillow); **sin tope de tamaño**. `requirements.txt` fija `pillow==12.1.0`. |
| Archivo `.sql` | `restaurar_bd`, `views.py:1250-1254`; la 04-04 fija el tope de **20 MB** como constante en `utils.py` | Se valida **después** de recibirlo y guardarlo. |
| Resto de los formularios | Solo texto y el campo `items_json` | Rige el valor por defecto. |

- **`DATA_UPLOAD_MAX_MEMORY_SIZE`** vale **2,5 MB** por defecto (`global_settings.py:311`) y **cuenta solo los campos de texto** del formulario, no el contenido de los archivos (`django/http/multipartparser.py:223-250`). Al excederse, Django responde 400.
- **`FILE_UPLOAD_MAX_MEMORY_SIZE`** vale **2,5 MB** por defecto (`global_settings.py:307`) y **no es un tope**: decide si un archivo se retiene en memoria o se escribe en un archivo temporal (`django/core/files/uploadhandler.py:208`). Subirlo lleva más subidas a la memoria del único worker; bajarlo, a más archivos temporales. **Ninguno de los dos frena una imagen de 50 MB.** El tope real de un archivo lo pone una validación propia.
- **Datos de producción medidos el 2026-10-20** (`linea-base-produccion.md`, fila de `media/`): **3 MB en 11 archivos** (promedio ≈ 0,27 MB; el máximo no se midió). El disco total es de 512 MiB compartido con la base.
- **No hay datos del servidor** sobre el límite de cuerpo de la petición que aplique el proxy de PythonAnywhere (no verificado).

## Contradicciones con la planificación

- **La definición nombra `FILE_UPLOAD_MAX_MEMORY_SIZE` como «límite de tamaño»**; en Django es un umbral entre memoria y disco, no un tope. Se fija como valor explícito y comentado, y el tope de verdad es la validación de la imagen y la de la 04-04.
- **La definición dice «dirección»** sin precisar cómo se obtiene tras el proxy: la respuesta no está en el repo ni en Django (sección «Dirección real»).
- **Bloquear no equivale a no registrar:** la definición pide «evento registrado»; sin cuidado, un bloqueo hecho en un backend deja **dos** eventos por intento (comprobado arriba). El diseño bloquea antes de `authenticate()`.
- **La regla 8.10 de `AGENTS.md`** (un solo worker, peticiones en serie) coincide con la definición: el limitador evita la fuerza bruta, **no** frena una inundación (DoS, fuera de alcance, ver abajo).

## Fuera de alcance

- **DoS y DDoS.** Con un solo worker, una petición maliciosa ya ocupó al trabajador cuando llega al formulario: un contador en la aplicación **no** contiene una inundación y daría una falsa sensación de seguridad (`definicion-epica-04.md`, «Fuera de alcance»). Esta iteración limita **intentos de contraseña** y **tamaños de subida**, nada más. Tampoco se agrega limitación general de peticiones por ruta.
- Cambio y recuperación de contraseña de `accounts/` y desactivar el acceso propio del admin (AUD-02-030).
- Contraseñas más fuertes, doble factor y avisos por correo (el canal de correo es la Épica 11).
- Borrar de `media/` las imágenes de pedidos eliminados (no verificado que hoy se borren; no es de esta iteración).
- Sacar recursos del CDN (08-02, 08-07) y la política de contenido (04-09).

## Alcance

1. **Límite de intentos fallidos** en `accounts/login/` y en el acceso del admin, con **dos contadores independientes** (D2): por usuario (nombre normalizado) y por dirección. Al llegar al límite, bloqueo temporal; los intentos bloqueados **no** llaman a `authenticate()` y no escriben `acceso_fallido`.
2. **Un evento `acceso_bloqueado` por bloqueo** (tipo nuevo, D4), escrito una sola vez cuando el bloqueo empieza, con usuario nulo y sin dirección IP ni nombre tecleado (solo el identificador del usuario si existe).
3. **Mensaje al usuario** en español de Chile, igual exista o no el usuario, con el tiempo de espera; en `login.html` se agrega la rama del bloqueo (hoy la plantilla muestra siempre «Credenciales incorrectas»).
4. **Éxito:** un acceso correcto reinicia el contador del usuario (no el de la dirección).
5. **Dirección del cliente** con una función única (D3), con la variable `ACCESO_PROXIES_CONFIABLES` (cantidad de proxies de confianza, defecto `0`); sin ella (local), `REMOTE_ADDR`. El límite por dirección se lee de una variable opcional (`ACCESO_FALLOS_POR_DIRECCION`, defecto 20; `0` desactiva solo ese contador): hace posible la medición de producción y es el interruptor de emergencia (ver «Dirección real»).
6. **Mecanismo** (D1): contador propio en un alias de caché dedicado (`CACHES`, con `MAX_ENTRIES` explícito).
7. **Límites de tamaño** (D5): valores explícitos y comentados de `DATA_UPLOAD_MAX_MEMORY_SIZE` y `FILE_UPLOAD_MAX_MEMORY_SIZE` (2,5 MB, sin cambio de comportamiento); imagen de referencia de **5 MB** validada en `PedidoForm`; chequeo temprano de `CONTENT_LENGTH` en las vistas que reciben archivos, coordinado con los 20 MB de la 04-04.
8. **Redirección:** `accounts/login/` con `redirect_authenticated_user=True` (la propuesta del registro).
9. **Procedimiento de desbloqueo** en `docs/operacion/` (nueva página breve) y su mención en `retroceso.md` si corresponde.
10. **Fuera:** lo de la sección «Fuera de alcance».

## Cómo funciona el diseño recomendado

1. El formulario de acceso (el de `accounts/login/` y el del admin comparten la misma comprobación) revisa en su `clean()`, **antes** de llamar a `super().clean()`, si el usuario normalizado o la dirección están bloqueados. Si lo están, levanta el error con el mensaje de bloqueo y marca `form.bloqueado = True` (la plantilla lo usa). No llama a `authenticate()`.
2. Si no están bloqueados, sigue el flujo normal. Un fallo emite `user_login_failed` (`senales.py`), y un receptor suma uno a cada contador (`cache.add` + `cache.incr`, atómicos en la caché local). Al alcanzar N, crea la clave de bloqueo con vencimiento y escribe **un** evento.
3. Un acceso correcto (`user_logged_in`) borra el contador del usuario.
4. **Normalización del nombre:** `strip()` y `casefold()`. La base de producción usa la colación `utf8mb4_unicode_ci` (`linea-base-produccion.md`, línea 98, medida el 2026-10-20; la misma que fija `settings.py:150` para las pruebas), **insensible a mayúsculas**: «ADMIN» y «admin» llegarían al mismo usuario y, sin normalizar, un atacante repartiría sus intentos entre variantes (inferido de la colación; se confirma con una prueba contra MySQL).
5. **Las claves no guardan texto del usuario:** el nombre se convierte en un resumen criptográfico corto; la dirección se guarda tal cual (solo en memoria, sin escribirla en eventos ni en registros).

## Dirección real detrás del proxy de PythonAnywhere

- **Lo que se sabe:** la web app de producción está detrás del proxy de PythonAnywhere (`linea-base-produccion.md`, línea 141: HTTPS forzado y estáticos mapeados por el panel; y la 04-02 depende de cómo ese proxy entrega el esquema, sin verificar). **No consta en el repo qué cabecera trae la dirección real ni cuántos proxies hay.** Se supone, sin verificar, que `X-Forwarded-For` la trae.
- **El riesgo de falsificarla:** cada proxy **agrega** la dirección que ve al final de `X-Forwarded-For`. Lo que está a la izquierda lo puede escribir el propio cliente: quien confíe en el **primer** valor deja que un atacante cambie su «dirección» en cada intento y evite el contador. Lo confiable es el valor que agregó **nuestro** proxy: el de la derecha, a la altura del número de proxies que sí controlamos.
- **Si se usa `REMOTE_ADDR` sin más** (sin cabecera) detrás de un proxy, todos los clientes parecerían tener **la dirección del proxy**: el contador de dirección sumaría los fallos de todos y **bloquearía a todos a la vez**, incluido el cliente legítimo. Es el peor error posible de esta iteración.
- **Diseño resuelto (D3):** variable de entorno con la **cantidad de proxies de confianza**, `ACCESO_PROXIES_CONFIABLES` (nombre fijado por el desarrollador, por defecto `0`). Con `0`, `REMOTE_ADDR`. Con `n` mayor que cero, el elemento número `n` contando desde la derecha de `X-Forwarded-For`; si la cabecera trae menos de `n` elementos o el valor no es una dirección válida, vuelve a `REMOTE_ADDR`. El valor de producción **se mide, no se supone** (verificación 3).
- **Interruptor de emergencia:** si un valor mal medido hiciera que todos compartan una misma dirección, poner `0` en `ACCESO_FALLOS_POR_DIRECCION` y recargar desactiva el contador por dirección (queda el del usuario) mientras se corrige `ACCESO_PROXIES_CONFIABLES`. Poner `ACCESO_PROXIES_CONFIABLES` en `0` **no** sirve para eso: devolvería la dirección del proxy.
- **Sin dependencia:** `django-ipware` o equivalentes serían una dependencia más para una función de diez líneas.
- **IPv6 (no verificado):** si el servidor entrega direcciones IPv6, un atacante con un bloque propio puede rotar de dirección; el contador por usuario sigue protegiendo.

## Mecanismo: contador propio frente a `django-axes`

| | **A · Contador propio en la caché local** | **B · `django-axes`** |
| :-- | :-- | :-- |
| Dependencia | Ninguna | Sí: versión exacta, consulta previa y RDA (`AGENTS.md`, secciones 6 y 11). Peso y arranque en frío: **no medidos** |
| Tablas | Ninguna: memoria (regla 8.11 cumplida sin purga) | Tablas nuevas, de **Clase 2**, con retención y purga obligatorias (regla 8.11). Nombres y órdenes de limpieza: de mi conocimiento, **no verificados** |
| Disco y CPU del worker | Cero escrituras | Una escritura por intento fallido (según su manejador de base de datos, no verificado) |
| Sobrevive a la recarga | **No**: se pierde (ver abajo) | Sí, si usa la base |
| Desbloqueo | **Solo recargando la web app** (la caché es de un solo proceso; una orden de gestión desde la consola no la alcanza) | Con su orden de gestión |
| Control del mensaje, del evento (`acceso_bloqueado`) y de la dirección | Total | Parcial: cabeceras y proxies con su propia configuración |
| Operación en producción | Variable de entorno y recarga | `pip install`, `migrate` en producción, respaldo previo |

**Qué pasa cuando la caché se pierde al recargar.** Los contadores y los bloqueos vigentes **se borran**. Efectos: (1) un bloqueo activo desaparece, lo cual es el desbloqueo manual más simple; (2) un atacante recupera sus intentos en cada recarga. Recargas hay en cada despliegue, cuando el cliente recarga la aplicación desde el panel (lo hizo dos veces el 2026-10-27, AUD-04-002) y cuando el servidor reinicia el proceso (frecuencia por hibernación y expiración: **no verificada**). El atacante **no** puede provocar la recarga. Aritmética de lo recomendado (5 intentos por usuario cada 15 minutos): hasta 480 intentos por día contra un usuario, frente a ilimitados hoy: **frena, no vuelve imposible**; la contraseña sigue siendo la defensa de fondo (validadores de `settings.py:157-170`, que solo actúan al crear o cambiar contraseñas).

**Otros dos riesgos del contador propio:**
- **Expulsión por llenado:** la caché local guarda 300 entradas por defecto y borra una tercera parte al llenarse; un atacante que invente muchos nombres podría expulsar contadores y bloqueos. Mitigación: alias de caché **dedicado** a este uso con `MAX_ENTRIES` explícito (propuesta: 2.000) y el contador por dirección, que frena al atacante antes de llenar.
- **Un solo proceso:** con más de un worker cada uno tendría su propia memoria y el límite efectivo se multiplicaría por el número de workers. Hoy es uno (`AGENTS.md`, sección 4); se revisa si el hosting cambia (Épica 14).

**Por qué no la caché en base de datos ni en archivos** (descartadas): la caché en base exige una tabla creada con `createcachetable` (fuera de las migraciones: un paso más en producción) y una escritura por intento; la de archivos escribe en el disco compartido. Ganan persistencia a costa de operación; para un acceso con pocos usuarios no compensa.

## Riesgo de bloquear al cliente legítimo y cómo se desbloquea

- **Quién puede bloquearse:** (a) el propio dueño, tras equivocarse N veces (cuenta compartida detrás de la misma dirección); (b) **otra persona que conozca el nombre de usuario** y falle a propósito: con un contador por usuario puede dejar al dueño fuera cada 15 minutos. Mitigación parcial: la ruta del admin no es la estándar y la aplicación no publica los nombres; el costo es una espera, no una pérdida de datos. La alternativa de contar por pareja usuario más dirección eliminaría ese riesgo pero deja pasar a un atacante con muchas direcciones; el desarrollador la descartó en D2.
- **Bloqueo de todos por error de dirección:** si la cantidad de proxies queda mal puesta (sección «Dirección real»), el contador por dirección bloquea a todos. Por eso la verificación 3 se hace **antes** de dar por buena la iteración y el interruptor de emergencia es una variable de entorno (`ACCESO_FALLOS_POR_DIRECCION=0`).
- **Desbloqueo:** (1) **automático** al vencer el tiempo (el mensaje lo dice); (2) **manual**, **recargar la web app** (borra la caché local); (3) en el peor caso, retroceso (`retroceso.md`, caso 1). Una orden de gestión no sirve con la caché local. El cliente tiene acceso al panel de PythonAnywhere (AUD-04-002) y recarga la aplicación; el procedimiento se escribe en `docs/operacion/` en lenguaje simple.
- **Quién entra:** no se sabe cuántos usuarios tiene producción (`PENDIENTE_DESARROLLADOR`, es un conteo de solo lectura); con un solo superusuario, el bloqueo de 15 minutos es un inconveniente, no una pérdida de servicio.

## Evidencia previa obligatoria (la reúne el desarrollador; no medida)

D2 fijó los números de partida (5 por usuario, 20 por dirección, 15 y 15 minutos) y pidió **medir antes**: no se conoce cuántos intentos fallidos hace hoy una persona legítima. **Regla de detención:** si la consulta muestra que algún usuario existente ya tuvo **4 o más fallos en una misma ventana de 15 minutos**, el límite de 5 queda demasiado justo y se consulta antes de seguir. La réplica trae los eventos `acceso_fallido` a la fecha de su último refresco, y esta consulta de solo lectura da los máximos por ventana de 15 minutos sin mostrar nada más que conteos (`mysql` exige consulta previa incluso en local, `AGENTS.md`, sección 6; **no ejecutada ni probada** por el agente):

```sql
SELECT TIMESTAMPDIFF(MINUTE, '2000-01-01', momento) DIV 15 AS ventana,
       resumen,
       COUNT(*) AS fallos
FROM pedidos_registroevento
WHERE tipo = 'acceso_fallido'
GROUP BY ventana, resumen
ORDER BY fallos DESC
LIMIT 10;
```

En la bitácora se anotan solo los conteos (la columna `resumen` puede traer un nombre de usuario real: no se copia). Los eventos **no guardan la dirección**, así que **el límite por dirección no se puede calibrar con datos** (no verificado). La carpeta `media/` de producción se midió el 2026-10-20 (3 MB, 11 archivos); el archivo más grande de `media/referencias/` se mide para comprobar que los 5 MB de D5 no rechazan un uso normal (el desarrollador, desde el panel de PythonAnywhere); si hay archivos de más de 5 MB, se consulta antes de seguir.

## Decisiones (resueltas por el desarrollador, 2026-11-17)

| # | Decisión | Resuelta como |
| :- | :------- | :------------ |
| D1 | Mecanismo | **Contador propio en la caché local** (opción A), en un alias de caché dedicado, sin dependencia ni tabla. Pierde los contadores al recargar y se desbloquea recargando. |
| D2 | Qué se cuenta y cuánto | **5 fallos por usuario y 20 por dirección**, en una ventana de **15 minutos**, con **bloqueo de 15 minutos**; dos contadores independientes; un acceso correcto borra el del usuario. **Medir antes con la consulta incluida** (sección «Evidencia previa obligatoria»). |
| D3 | Dirección real | **Variable de proxies de confianza, `ACCESO_PROXIES_CONFIABLES`**, defecto `0` (`REMOTE_ADDR`); el valor de producción se mide (verificación 3), con vuelta a `REMOTE_ADDR` ante cualquier duda. |
| D4 | Evento del bloqueo | **Tipo nuevo `acceso_bloqueado`**, con migración de **Clase 1** (`0009`, después de la `0008` de la 04-06). La iteración se detiene si `sqlmigrate` muestra cualquier `ALTER` (`AGENTS.md`, regla 8.1). |
| D5 | Límites de tamaño | **Imagen de referencia de 5 MB** y **chequeo temprano de `CONTENT_LENGTH`** (20 MB de la 04-04 más 1 MB de margen en `restaurar_bd`; imagen más 2,5 MB en `crear_pedido` y `editar_pedido`). Valores explícitos de `DATA_UPLOAD_MAX_MEMORY_SIZE` y `FILE_UPLOAD_MAX_MEMORY_SIZE` en 2,5 MB (confirmados el 2026-11-17, sin cambio de comportamiento). |

**Qué se descartó (para no volver a discutirlo):** `django-axes` (dependencia con RDA, tablas de Clase 2 con purga y una escritura por intento), la caché en base de datos y en archivos, contar por pareja usuario más dirección, el bloqueo creciente, `REMOTE_ADDR` sin más (bloquea a todos detrás del proxy), el primer valor de `X-Forwarded-For` (lo escribe el cliente), reutilizar `acceso_fallido` para el bloqueo y bajar `DATA_UPLOAD_MAX_MEMORY_SIZE`.

**Confirmado por el desarrollador el 2026-11-17:** la variable `ACCESO_FALLOS_POR_DIRECCION` (opcional, defecto 20; `0` apaga solo el contador por dirección) y los dos valores explícitos de 2,5 MB de `DATA_UPLOAD_MAX_MEMORY_SIZE` y `FILE_UPLOAD_MAX_MEMORY_SIZE`. La redacción la había agregado para poder medir la dirección en producción y tener un interruptor de emergencia; no estaba en las decisiones originales. Los valores de D2 siguen siendo constantes del código.

## Coordinación con los 20 MB de la 04-04

- Son **límites de capas distintas** y no se pisan: la 04-04 limita **un archivo `.sql`** (después de recibirlo); `DATA_UPLOAD_MAX_MEMORY_SIZE` cuenta **solo los campos de texto** (no el archivo); la imagen tiene su tope propio; el chequeo temprano de D5 es la única pieza que mira el tamaño total de la petición.
- `DATA_UPLOAD_MAX_MEMORY_SIZE` **no** rechaza el `.sql` de 20 MB (comprobado en `multipartparser.py:223-250`: no cuenta archivos). Una prueba lo confirma.
- Un respaldo de 20 MB supera los 2,5 MB de `FILE_UPLOAD_MAX_MEMORY_SIZE`: va a un archivo temporal, no a la memoria. **No verificado:** el directorio temporal del servidor y si cuenta para la cuota de disco.
- **No verificado:** el límite de cuerpo que aplica el proxy de PythonAnywhere (podría rechazar antes que la aplicación). Si lo hubiera y fuera menor que 20 MB, la 04-04 ya estaría afectada: se mide en producción durante la 04-04.
- El chequeo temprano de D5 toca `restaurar_bd`, que la 04-04 ya modificó: la 04-08 parte de lo que deje.

## Pasos

0. Consulta previa para `settings.py`, `urls.py`, `.env.example`, `makemigrations` y `migrate` en local (`AGENTS.md`, sección 6). Respaldo de la réplica.
1. Línea base: `test pedidos` (número y fallos esperados tras la 04-07) y `showmigrations pedidos` (hasta `0008` si la 04-06 ya está; si no, hasta `0007` y se revisa la numeración: esta migración es la que sigue a la de la 04-06).
2. **Evidencia previa (obligatoria, D2 y D5):** consulta de los fallos por ventana en la réplica y archivo más grande de `media/referencias/`. Si se activa la regla de detención, se consulta antes de seguir.
3. Pruebas primero (tabla siguiente); ver fallar las de bloqueo.
4. `pedidos/limite_acceso.py`, los dos formularios de acceso, el receptor en `senales.py`, `admin.site.login_form`, `urls.py` con `redirect_authenticated_user=True`, `CACHES`, límites de subida, `login.html` y el chequeo temprano.
5. `makemigrations pedidos --name acceso_bloqueado` (debe crear **solo** `0009`, con un `AlterField`), **`sqlmigrate pedidos 0009` en la réplica** (esperado, inferido: solo el comentario del `AlterField`, sin sentencias SQL; cualquier `ALTER`, `DROP` o `ADD CONSTRAINT` detiene la iteración) y copiarlo en la bitácora; `migrate` en local y `makemigrations --check --dry-run` sin cambios.
6. Revisión manual en la réplica: equivocarse N veces en `accounts/login/` y en el admin (mensaje, bloqueo, espera), entrar con sesión ya iniciada (redirige), subir una imagen de 5 MB y otra más grande, intentar restaurar un archivo de más de 20 MB; escritorio y 360 px.
7. Procedimiento de desbloqueo en `docs/operacion/`.
8. Bitácora, registro, auditoría (AUD-03-004), `.env.example`, estado «En revisión».

## Pruebas

Todas vacían la caché en `setUp` (la caché local persiste entre pruebas) y fijan la dirección con `REMOTE_ADDR` del cliente de pruebas; los límites se leen de las constantes, no se repiten a mano.

| Punto | Prueba |
| :---- | :----- |
| Bloqueo por N intentos (usuario) | N POST fallidos a `/accounts/login/` con el mismo usuario existente: el intento N+1 responde con el mensaje de bloqueo y **no** llama a `authenticate` (se comprueba con un `mock`), incluso con la **contraseña correcta**. |
| Bloqueo por dirección | Fallos con nombres distintos desde la misma dirección hasta el límite de dirección: bloquea; desde otra dirección (otro `REMOTE_ADDR`) no. |
| Evento | Al empezar el bloqueo hay **un** evento (`acceso_bloqueado`) con usuario nulo y sin la dirección ni el nombre tecleado; los intentos bloqueados siguientes **no** escriben más filas (conteo de eventos igual). |
| Sin fuga | El mensaje de bloqueo es el mismo con usuario existente que con uno inexistente. |
| Mayúsculas | «ADMIN» y «admin» suman al mismo contador (contra MySQL). |
| Éxito reinicia | N−1 fallos, un acceso correcto, y N−1 fallos más no bloquean. |
| Vencimiento | Con el reloj movido más allá del tiempo de bloqueo (`mock` del reloj de la caché o claves con vencimiento corto de prueba), el acceso vuelve a la normalidad. |
| Recarga | `cache.clear()` (equivale a recargar la web app) desbloquea. |
| Admin | Lo mismo en `acceso-manzagrafica-admin/login/`; los contadores se comparten con `accounts/login/`. |
| Dirección real (D3) | Sin variable: se usa `REMOTE_ADDR` y se ignora `X-Forwarded-For`. Con `n = 1`: el último elemento de la cabecera, **ignorando** lo que el cliente escribió a la izquierda (cabecera `falsa, real`); cabecera con menos elementos o inválida: `REMOTE_ADDR`. |
| Redirección | GET a `/accounts/login/` con sesión iniciada: 302 al panel; sin sesión: 200 con el formulario. |
| Variable de dirección | `ACCESO_FALLOS_POR_DIRECCION=0` desactiva el contador por dirección y deja el del usuario; un valor pequeño lo hace saltar antes. |
| Tamaños (D5) | Imagen de tope exacto pasa; un byte más se rechaza con el mensaje y no se guarda; `crear_pedido` y `editar_pedido` con un cuerpo declarado más grande que el permitido se rechazan **antes** de leer archivos; un `.sql` de menos de 20 MB **no** lo rechaza `DATA_UPLOAD_MAX_MEMORY_SIZE`; el rechazo no muestra `str(e)`. |
| Contrato de eventos | `test_eventos_negocio.py:176-215` en verde (con la caché vaciada en su `setUp`). |
| Guardias | `makemigrations --check --dry-run` sin cambios tras crear `0009`; sin `print` ni `except Exception: pass` en el módulo nuevo (regla 8). |
| Existentes | Suite completa con los fallos esperados heredados. |

## Verificación en producción (la hace el desarrollador; todo **no verificado** hasta entonces)

1. Respaldo previo, descargado y verificado (`respaldo.md`); `migrate` y `showmigrations pedidos` (marca `0009`) antes del Reload.
2. Tras el Reload, entrar con la contraseña correcta; `server.log` sin errores nuevos.
3. **Medir la dirección (obligatorio antes de dar por buena la iteración).** Con la variable de proxies aún en `0`, desde **la misma conexión** del desarrollador: (a) con un **nombre de usuario inexistente**, no la cuenta real, provocar fallos hasta que el contador de dirección bloquee (por eso, durante la prueba, `ACCESO_FALLOS_POR_DIRECCION` se baja a un valor pequeño, por ejemplo 3, y se vuelve a 20 al terminar); (b) **desde otra red** (datos móviles) intentar un acceso normal: **si está bloqueado, `REMOTE_ADDR` es la dirección del proxy**, hay que fijar `ACCESO_PROXIES_CONFIABLES` y recargar; (c) con la variable puesta, repetir (a) enviando `X-Forwarded-For` falsos distintos en cada intento: **el bloqueo debe llegar igual** (la falsificación no sirve). Recargar al final (borra todo).
4. Un fallo y un bloqueo reales del usuario de pruebas del desarrollador: ver el evento en el admin y confirmar el desbloqueo recargando.
5. Subir una imagen de referencia dentro y fuera del tope; no se intenta restaurar archivos grandes en producción para probar.
- **No verificado:** qué cabecera trae la dirección real y cuántos proxies hay; con cuántos usuarios cuenta producción; si el proxy limita el cuerpo; la frecuencia de reinicio del proceso (perdería los contadores); el directorio temporal y su cuota.

## Plan de retroceso

- **`retroceso.md`, caso 2** (con migraciones; escrito para Clase 2, se aplica igual a esta de Clase 1): `python manage.py migrate pedidos 0008` (revierte la `0009`; sin SQL, igual que al aplicarla, inferido) y luego volver a la etiqueta anterior y Reload. **Orden:** primero la migración, después el código (el código viejo no conoce `acceso_bloqueado`). Si `migrate` atrás fallara, el respaldo previo y el caso 3.
- **Retroceso parcial sin tocar el código:** si el contador por dirección bloqueara a todos, `ACCESO_FALLOS_POR_DIRECCION=0` y recargar lo desactiva, y se corrige `ACCESO_PROXIES_CONFIABLES`. Recargar la web app es siempre el desbloqueo de emergencia (borra todos los contadores).
- **Lo que queda tras un retroceso:** los eventos `acceso_bloqueado` ya escritos permanecen en la tabla (el tipo no se valida en la base) y se purgan con la retención de 365 días; el admin de eventos los mostraría sin el nombre legible del tipo. Los contadores viven en memoria y no dejan nada.

## Criterio de término

- Tabla de pruebas en verde (incluido el bloqueo por N intentos y su evento).
- `sqlmigrate pedidos 0009` copiado en la bitácora, sin SQL; `0009` creada después de la `0008` de la 04-06.
- Evidencia previa hecha (consulta de fallos por ventana y archivo más grande de `media/referencias/`) y sin activar la regla de detención.
- Revisión manual en la réplica hecha.
- Verificación 3 de producción hecha y valor de proxies fijado.
- AUD-03-004 resuelto en la auditoría y procedimiento de desbloqueo escrito.

## Riesgos

- **Bloquear al cliente legítimo** (dos vías: errores propios y bloqueo provocado por un tercero): espera de 15 minutos o recarga; documentado arriba.
- **Bloquear a todos por una dirección mal medida:** peor caso de la iteración; se previene con la verificación 3 y se revierte con `ACCESO_FALLOS_POR_DIRECCION=0`.
- **Contadores perdidos al recargar y expulsión por llenado de la caché:** el límite frena, no impide; mitigaciones en la sección del mecanismo.
- **Cambios en archivos de configuración:** `settings.py`, `urls.py` y `.env.example` exigen consulta previa; `settings.py` también lo editan la 04-02, la 04-03 y la 04-05 (se parte de lo que dejen).
- **Migración de Clase 1 con numeración dependiente de la 04-06:** si el orden de ejecución cambiara, la `0009` pasa a ser la siguiente libre; se verifica con `showmigrations` y la iteración se detiene ante cualquier `ALTER`.
- **Límites sin medición previa:** los 5 y 20 intentos salen de la decisión, no de datos; la evidencia previa y la regla de detención lo cubren para el usuario, pero **el límite por dirección no se puede calibrar** (los eventos no guardan la dirección).
- **Pruebas que se contaminan entre sí:** por la caché compartida; se vacía en cada `setUp`.
- **Chequeo de `CONTENT_LENGTH`:** una cabecera ausente o falsa no es un tope duro; la validación de la imagen y el tope de 20 MB siguen aplicando después.
- **Rechazos de tamaño poco amables:** Django responde 400 sin pantalla propia cuando se excede `DATA_UPLOAD_MAX_MEMORY_SIZE`; con el valor actual no lo alcanza un uso normal.
- **Un despliegue, un propósito (RDA-007):** va solo, después de la 04-07.
