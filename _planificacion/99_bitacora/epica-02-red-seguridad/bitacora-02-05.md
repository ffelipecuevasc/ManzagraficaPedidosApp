# Bitácora 02-05 · Pruebas de control de acceso

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** En revisión

## Resumen

Se fijó en `pedidos/tests/test_acceso.py` (13 pruebas) quién entra adónde. Cubre el inventario de las 40 rutas de `pedidos/urls.py`, leídas del resolvedor, que un anónimo no escribe, los permisos de las cuatro vistas de la base de datos con respaldo y restauración simulados, los puntos JSON y los `pk` inexistentes. La protección es **vista por vista**, sin `LoginRequiredMiddleware`. No apareció ninguna ruta pública nueva en `pedidos/urls.py`, así que D2 no se activó y la 02-04 sigue en 18 regresiones. El hallazgo principal: `@transaccion_segura` convierte el 404 en 500. No se cambió código de la aplicación.

## Mecanismo de protección encontrado

- `PedidosApp/settings.py`, `MIDDLEWARE`: **no** incluye `LoginRequiredMiddleware`. Cada vista de `pedidos/views.py` lleva `@login_required`. `robots_txt` lleva `@login_not_required`, que sin el middleware no tiene efecto, y es pública solo porque no lleva `@login_required`.
- Las cuatro vistas de la base de datos suman `@user_passes_test(es_superusuario)`. Con un usuario común redirigen al acceso (302), no responden 403.
- `es_superusuario` está decorada con `@login_required` aunque no es una vista. Llamada directo con un usuario, devuelve `False` o `True` correctamente, pero el decorador sobra (hallazgo propuesto H3).
- Consecuencia: **una vista nueva sin decorador queda pública.** `InventarioRutasTests` lo detecta.

## Punto de partida frente al código real

| Punto de la iteración | Resultado |
| :-------------------- | :-------- |
| Las rutas se enumeran con el resolvedor | Sí: `pedidos.urls.urlpatterns` (40 patrones, sin `include` anidados) y `reverse` con argumentos ficticios. A nivel de proyecto, `get_resolver()` lista además el panel de administración, `django.contrib.auth.urls` y `media/`, que existe solo con `DEBUG` |
| Middleware o decoradores | Decoradores vista por vista (arriba) |
| Vistas de la base con `user_passes_test`: 302, no 403 | Confirmado, por GET y por POST |
| Puntos JSON sin sesión: 302 en HTML | Confirmado: `text/html`, al acceso. Con sesión, GET da 405 (`require_POST`) |
| Admin y `RegistroEvento` ya probados (01-05) | No se duplican |
| `RobotsTxtTests` (02-01) | Existe; el inventario lo vuelve a cubrir como ruta pública |
| **Difiere:** tarea 5 espera 404 ante un `pk` inexistente | **12 vistas responden 500**: `@transaccion_segura` captura también el `Http404`. Solo las 6 vistas sin ese decorador responden 404 |

## Rutas y su política

| Rutas | Política | Anónimo | Usuario común | Superusuario |
| :---- | :------- | :------ | :------------ | :----------- |
| `robots.txt` | Pública | 200 | 200 | 200 |
| `/accounts/login/` | Pública | 200 | — | — |
| 35 rutas de pedidos, clientes, cotizaciones, productos, pagos, panel y `api/…` | `@login_required` | 302 al acceso, sin escribir | Entra | Entra |
| `api/cliente/nuevo/`, `api/producto/nuevo/` | `@login_required` + `@require_POST` | 302 en HTML, sin crear | JSON `success`; GET 405 | Igual |
| 4 rutas de `base_datos/` | + `@user_passes_test(es_superusuario)` | 302 al acceso | 302 al acceso, sin efecto | 200 |
| `pk` inexistente, 6 vistas sin `@transaccion_segura` | — | — | 404 | — |
| `pk` inexistente, 12 vistas con `@transaccion_segura` | — | — | **500** | — |

**Fuera de `pedidos/urls.py`, sin sesión** (no se agregaron a la lista, D1):
- `/accounts/password_reset/`, `…/done/`, `/accounts/reset/<uidb64>/<token>/` y `/accounts/reset/done/` responden 200.
- `/accounts/logout/` responde 405 a GET; en Django 6 solo acepta POST.
- `/accounts/password_change/` redirige al acceso.
- `/acceso-manzagrafica-admin/` redirige a su propio acceso (`…/login/`), que es público.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `pedidos/tests/test_acceso.py` | Nuevo: 13 pruebas |
| `pedidos/tests/ayudas.py` | `cerrar_respuesta`: cierra un `FileResponse` sin romper la transacción de la prueba |
| `pedidos/tests/test_regresiones.py` | R6c usa `ayudas.cerrar_respuesta` (antes `respuesta.close()`) |
| `docs/operacion/pruebas.md` | Sección 10 «Control de acceso fijado» |
| `_planificacion/10_epicas/epica-02-red-seguridad/iteracion-02-05-control-acceso.md` | En revisión; D1 y D2; criterios |
| `_planificacion/10_epicas/epica-02-red-seguridad/definicion-epica-02.md` | Estado y nota de la 02-05 |
| `_planificacion/00_producto/registro-pendientes.md` | 02-05 en revisión; D1 y D2 resueltas; 4 hallazgos propuestos en la sección 4; historial |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-05.md` | Esta bitácora |

## Verificación

- Exploración previa, con pruebas temporales borradas después: respuestas de anónimo, usuario común y superusuario en las cuatro vistas de la base; puntos JSON; rutas de `accounts/` y del panel de administración; los 19 `pk` inexistentes, por GET y por POST.
- **Tres ejecuciones seguidas** de `python manage.py test pedidos -v 2`:

```text
Ejecución 1: Found 183 test(s). Ran 183 tests in 255.390s  OK (expected failures=18)
Ejecución 2: Found 183 test(s). Ran 183 tests in 299.948s  OK (expected failures=18)
Ejecución 3: Found 183 test(s). Ran 183 tests in 272.123s  OK (expected failures=18)
```

  Sin `failures`, `errors` ni `unexpected successes`. 183 = 170 anteriores + 13 de `test_acceso.py`.
- `python manage.py test pedidos --exclude-tag regresion` → `Ran 165 tests` … `OK`.
- `python manage.py test pedidos --tag regresion` → `Ran 18 tests` … `OK (expected failures=18)`.
- `python manage.py check` → `System check identified no issues (0 silenced).`
- `python manage.py makemigrations --check --dry-run` → `No changes detected` (código de salida 0).
- `git status --short` y `git diff --stat`: solo `pedidos/tests/` y archivos `.md`.
- Pantallas: no aplica.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] El inventario cubre las 40 rutas de `pedidos/urls.py` (leídas del módulo; `test_el_inventario_sale_del_resolvedor` fija el número) y falla si una ruta nueva no redirige al acceso y no está en `RUTAS_PUBLICAS`.
- [x] Las cuatro vistas de la base rechazan a un usuario común por GET y por POST. `generar_respaldo_mysql` y `restaurar_bd_mysql` cumplen `assert_not_called`, los conteos no cambian y no se crea `backups/` en la carpeta temporal.
- [x] Puntos JSON: sin sesión, 302 en HTML sin crear; con sesión, JSON y 405 por GET.
- [x] Ningún POST anónimo cambia la base: 25 rutas que escriben, 9 modelos contados antes y después, estados sin cambio.
- [x] Ninguna prueba ejecuta `mysql` ni `mysqldump` ni escribe en `backups/` o `media/` reales: funciones simuladas y `BASE_DIR` temporal.
- [x] Lo que deja pasar de más queda como hallazgo propuesto. No hubo rutas abiertas en `pedidos/urls.py`, así que no hubo regresión nueva.
- [x] Tres ejecuciones en verde; `check` y `makemigrations` sin cambios.
- [x] El diff no toca código de la aplicación.
- [x] D1 y D2 resueltas y registradas.

## Decisiones tomadas

- **D1 (desarrollador):** lista pública = `robots.txt` y el acceso. `RUTAS_PUBLICAS = {'robots_txt'}` en la prueba; el acceso se prueba aparte porque no está en `pedidos/urls.py`.
- **D2 (desarrollador):** una ruta abierta sin querer pasa a hallazgo y regresión en la 02-04. No se activó.
- **Agente · `pk` inexistente que da 500:** se fija como caracterización (`test_vistas_con_transaccion_segura_responden_500`), con comentario, en vez de afirmar 404. D2 trata de rutas abiertas, no de errores, y la iteración dice no corregir. Si el desarrollador lo acepta como defecto, pasa a la 02-04 como regresión que afirme 404.
- **Agente · `ayudas.cerrar_respuesta`:** `respuesta.close()` de un `FileResponse` emite `request_finished`, que cierra la conexión dentro de la transacción de `TestCase` y rompe la prueba siguiente (`TransactionManagementError`). La ayuda desconecta `close_old_connections` mientras cierra, igual que el cliente de pruebas de Django. R6c de la 02-04 tenía el mismo problema latente: pasaba por ser la última de su clase. Ahora usa la ayuda.

## Pendientes y riesgos

Hallazgos propuestos, en la sección 4 del registro, sin ID:

- **H1 · `@transaccion_segura` convierte el 404 en 500** en 12 vistas: editar y eliminar pedido, cliente, cotización y producto; duplicar pedido; convertir cotización; editar pago; ingresar pago con pedido. Ensucia el registro de errores y muestra la página de error en vez de «no encontrado». Severidad propuesta: Baja. Candidato a regresión en la 02-04 y a corrección en la 03-01 (rediseño del decorador).
- **H2 · Rutas públicas fuera de `pedidos/urls.py`:** recuperación de contraseña (4 rutas) y acceso del panel de administración. La recuperación de contraseña no tiene correo configurado; si se usa, falla o no llega. Severidad propuesta: Baja. `PENDIENTE_DESARROLLADOR`: si se agregan a la lista, se quitan de `urls.py` (Épica 04) o se declaran regresión.
- **H3 · `@login_required` sobre `es_superusuario`:** sobra; limpieza en la Épica 04.
- **H4 · Puntos JSON sin sesión devuelven 302 en HTML** (no JSON ni 401), y el usuario común recibe 302 en las vistas de la base, no 403. Comportamiento fijado; cambiarlo es de la Épica 04.

## Commit sugerido

`Épica 2 - Iteración 02-05: fija el control de acceso con 13 pruebas (inventario de 40 rutas, permisos de la base y puntos JSON) y propone el 404 que hoy responde 500`
