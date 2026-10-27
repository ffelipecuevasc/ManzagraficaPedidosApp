# Iteración 02-05 · Pruebas de control de acceso

- **Épica:** 02 · Red de seguridad
- **Estado:** En revisión (ejecutada el 2026-10-27; [bitacora-02-05](../../99_bitacora/epica-02-red-seguridad/bitacora-02-05.md))
- **Subfase del plan:** 2.5
- **Depende de:** 02-01
- **RDA relacionadas:** RDA-006
- **Hallazgos que avanza:** AUD-01-015 (cero pruebas) y AUD-01-018 (el módulo de restauración ejecuta SQL arbitrario). No cierra ninguno.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no despliega nada: solo agrega pruebas)

## Objetivo

Comprobar con pruebas **quién puede entrar adónde** y, sobre todo, lo que **no** debe poder hacerse: un visitante sin sesión no ve nada protegido; un usuario común no puede respaldar, restaurar ni ver las estadísticas de la base de datos; los puntos de acceso que responden JSON se comportan de una forma conocida cuando no hay sesión. La mayoría de los agujeros de seguridad viven en los caminos negativos que nadie prueba.

Son pruebas de **caracterización**: fijan la respuesta real de hoy. Si una prueba revela que el sistema deja pasar de más, el defecto se anota y la prueba se declara como regresión en 02-04; no se corrige aquí.

## Punto de partida (a verificar leyendo el código antes de escribir)

- `pedidos/urls.py` define las rutas de la aplicación (panel, pedidos, clientes, cotizaciones, productos, pagos, gestión de la base de datos y los puntos `api/…`). El agente las enumera con el resolvedor de URLs de Django y no copia la lista a mano.
- `pedidos/views.py` importa `login_required`, `login_not_required` y `user_passes_test`: el agente confirma si el proyecto usa el `LoginRequiredMiddleware` de Django (acceso protegido por defecto, con `login_not_required` para las excepciones) o decoradores vista por vista, y lo escribe en la bitácora.
- Las vistas de gestión de la base de datos (`respaldar_bd`, `generar_respaldo_bd`, `restaurar_bd`, `estadisticas_bd`) usan `@user_passes_test(es_superusuario)`. Ese decorador, ante un usuario que no cumple, **redirige al acceso** (302); no responde 403. La prueba fija lo que realmente ocurra.
- `api_crear_cliente_rapido` y `api_crear_producto_rapido` son puntos que responden JSON. Sin sesión, lo esperable es una redirección al acceso en HTML, no un JSON de error: la prueba lo comprueba y lo documenta.
- El panel de administración de Django y la vista de solo lectura de `RegistroEvento` (superusuarios) ya tienen pruebas desde la 01-05; esta iteración no las duplica.
- `RobotsTxtTests` (02-01) ya comprueba que `robots.txt` es público.

## Tareas

1. **Inventario de rutas.** Una prueba que recorre **todas** las rutas de `pedidos/urls.py` con `subTest` (construidas con `reverse` y argumentos ficticios) y registra la respuesta de un visitante anónimo. Resultado esperado: redirección al acceso en todas, salvo una lista explícita de rutas públicas. Esa lista (propuesta: `robots.txt` y el acceso) vive en la prueba, de modo que **una ruta nueva sin protección rompe la prueba**.
2. **Anónimo no escribe.** Para las rutas que crean, editan o eliminan, un POST anónimo no cambia ningún conteo de la base. Se comprueba el número de filas antes y después.
3. **Usuario sin permisos en la base de datos.** Un usuario autenticado que no es superusuario, frente a `respaldar_bd`, `generar_respaldo_bd`, `restaurar_bd` y `estadisticas_bd`: redirección al acceso y ningún efecto. Para `generar_respaldo_bd` y `restaurar_bd` se simulan `generar_respaldo_mysql` y `restaurar_bd_mysql` con `mock` y se comprueba que **no se invocan** (`assert_not_called`). Un superusuario sí puede entrar (camino positivo, con las funciones simuladas).
4. **Puntos JSON sin sesión.** `api_crear_cliente_rapido` y `api_crear_producto_rapido` con un POST anónimo: qué responde (código y tipo de contenido) y que no crean registros. Con sesión, el camino feliz.
5. **Rutas con parámetros ajenos.** Un usuario autenticado que pide un `pk` inexistente recibe 404 y no un error 500 (para detalle, edición y eliminación de pedido, cliente, cotización, producto y pago, salvo `eliminar_pago`, que es la regresión R7 de 02-04).
6. **Documentación.** En `docs/operacion/pruebas.md`, una sección «Control de acceso fijado» con la tabla de rutas y su política. En el registro, las observaciones que ameriten hallazgo nuevo (por ejemplo, que los endpoints JSON no devuelvan 401).
7. **Bitácora** `bitacora-02-05.md` con el mecanismo de protección encontrado, la salida de `test pedidos -v 2` y el recuento.

## Criterios de aceptación

- [x] La prueba de inventario cubre todas las rutas de `pedidos/urls.py` y falla si aparece una ruta nueva sin protección ni lista blanca.
- [x] Las cuatro vistas de gestión de la base de datos rechazan a un usuario que no es superusuario, y las funciones de respaldo y restauración **no se invocan**.
- [x] Los puntos JSON tienen su comportamiento sin sesión fijado y documentado.
- [x] Ningún POST anónimo cambia la base.
- [x] Ninguna prueba ejecuta `mysql` ni `mysqldump` ni escribe en `backups/` o `media/` reales.
- [x] Cualquier comportamiento que deje pasar de más queda como hallazgo en el registro y, si procede, como regresión propuesta para 02-04.
- [x] `python manage.py test pedidos` en verde (más las nuevas) en tres ejecuciones seguidas; `check` sin errores; `makemigrations --check --dry-run` sin cambios.
- [x] El diff no toca código de la aplicación.
- [x] Las decisiones `PENDIENTE_DESARROLLADOR` quedaron resueltas y registradas.

## Fuera de alcance

- Cambiar la política de acceso, agregar roles o permisos, o devolver 401/403 en los puntos JSON (Épica 04).
- Validación del archivo en la restauración (04-04) y escrituras por GET (04-01).
- Pruebas de CSRF, de cabeceras de seguridad o de sesiones.

## Decisiones del desarrollador

Resueltas por el desarrollador el 2026-10-27:

1. **D1 · Lista de rutas públicas:** solo `robots.txt` y el acceso (`login`). Si aparece otra ruta pública, no se agrega a la lista: se reporta y decide el desarrollador. Resultado: en `pedidos/urls.py` no apareció ninguna; fuera de ella, la recuperación de contraseña y el acceso del panel de administración responden sin sesión (reportados en la bitácora).
2. **D2 · Ruta pública o abierta sin querer:** no se cambia la prueba para que pase; se registra el hallazgo (siguiente ID libre) y una regresión en la 02-04. Resultado: no se activó; el recuento de la 02-04 sigue en 18.

## Datos requeridos del cliente

- Ninguno. El número de usuarios, sus roles y los dispositivos que usan siguen pendientes en `producto.md` (`PENDIENTE_CLIENTE`) y no bloquean estas pruebas.