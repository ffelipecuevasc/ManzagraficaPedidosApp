# Evidencia 01-05 · Revisión manual del admin de eventos en la réplica

- **Iteración:** 01-05 · Consulta de eventos en el admin
- **Quién ejecuta:** el desarrollador, en su PC, contra la réplica local (`manzagrafica_replica`). El agente no inicia sesión ni arranca el servidor.
- **Qué se cierra:** el criterio «Revisión manual en la réplica con capturas o descripción en la bitácora (listado, filtros y detalle)».
- **Efecto en la réplica:** iniciar sesión crea filas reales en `pedidos_registroevento` (`acceso_exitoso` y, en el paso 3, `acceso_fallido`), una sesión en `django_session` y actualiza `last_login`. Es esperado: esas filas son la evidencia. Ningún paso toca producción.

## 1. Preparación (PowerShell 7, en la raíz del proyecto)

```powershell
docker compose up -d
$env:DB_NAME = 'manzagrafica_replica'
python manage.py showmigrations pedidos | Select-Object -Last 2    # debe mostrar [X] 0007_registroevento
python manage.py shell -c "from pedidos.models import RegistroEvento as R; print(R.objects.count())" | Select-Object -Last 1
python manage.py runserver
```

Anota el conteo inicial de eventos (se espera `0`).

## 2. Generar eventos de prueba desde la aplicación

En el navegador, en `http://127.0.0.1:8000/`:

1. Cierra sesión si estás dentro y entra con un **nombre de usuario inexistente** (por ejemplo `nadie-prueba`) y cualquier contraseña. Debe fallar.
2. Entra con tu superusuario de la réplica y una **contraseña equivocada**. Debe fallar.
3. Entra con tu superusuario y la contraseña correcta.
4. Opcional, solo si quieres ver un evento de negocio: cambia el estado de un pedido de prueba y devuélvelo a su estado original (deja 2 eventos `pedido_estado_cambiado`). Si prefieres no tocar datos de la réplica, omítelo.

## 3. Revisar el admin

Abre `http://127.0.0.1:8000/acceso-manzagrafica-admin/pedidos/registroevento/`.

| # | Qué mirar | Qué pegarme |
| :- | :-------- | :---------- |
| 1 | **Listado:** columnas «Momento (hora de Chile)», tipo, usuario, entidad, identificador y resumen; el más reciente arriba | Captura o las filas (sin datos de clientes) |
| 2 | **Hora:** la del acceso coincide con la hora de tu reloj (hora de Chile) y muestra `(UTC-0300)` en horario de verano | La fecha y hora de la fila del acceso y la hora de tu reloj |
| 3 | **Accesos fallidos:** el de `nadie-prueba` dice «Usuario intentado: usuario desconocido» (sin el texto escrito); el de la contraseña equivocada dice tu nombre de usuario, sin contraseña | Los dos resúmenes |
| 4 | **Filtros:** a la derecha, «Momento» (Cualquier fecha, Hoy, Últimos 7 días, Este mes, Este año), «Tipo» y «Usuario». Prueba «Hoy», un tipo y tu usuario | Cuántas filas deja cada filtro |
| 5 | **Búsqueda:** si hiciste el paso 2.4, busca el número del pedido: solo deben salir sus eventos | El resultado |
| 6 | **Solo lectura:** no hay botón «Añadir», ni acciones en el listado, ni «Guardar» o «Eliminar» en el detalle | Confirmación |
| 7 | **Detalle:** al abrir una fila, todos los campos se ven como texto, con la misma hora y zona | Captura o descripción |
| 8 | **Ancho de 360 px** (herramientas del navegador, modo dispositivo): el listado se puede leer y desplazar | Descripción |

## 4. Cierre

```powershell
# Ctrl+C para detener runserver
python manage.py shell -c "from pedidos.models import RegistroEvento as R; print(R.objects.count())" | Select-Object -Last 1
```

Pega el conteo final: se esperan 3 eventos (o 5 con el paso 2.4). Si quieres dejar la tabla como estaba, dímelo y te paso la orden para borrar solo esas filas; no es necesario, porque la réplica se refresca con el próximo volcado.

## Respuesta del desarrollador

Resultados entregados por el desarrollador el 2026-10-25 (archivo `evidencia-01-05-resultados.md`), integrados sin cambios de contenido.

- **Fecha:** 2026-10-25
- **Quién:** Felipe Cuevas (desarrollador)
- **Entorno:** réplica local (`DB_NAME = manzagrafica_replica`), `python manage.py runserver`, Django 6.0.1. Navegador de escritorio y vista de dispositivo a 360 × 800 (Samsung Galaxy A55 en las herramientas del navegador).
- **Estado:** verificados los 9 puntos, todos con captura o con la salida de la consola.

### Preparación

| Paso | Resultado | Estado |
| :--- | :-------- | :----- |
| Docker arriba | `Container manzagrafica-mysql  Running` | ✅ |
| Migración 0007 aplicada en la réplica | `[X] 0007_registroevento` (última de `showmigrations pedidos`) | ✅ |
| Eventos antes de la revisión | `RegistroEvento.objects.count()` = **0** | ✅ |
| Arranque del servidor | `System check identified no issues (0 silenced).` | ✅ |
| Eventos tras la primera parte de la revisión | `RegistroEvento.objects.count()` = **3** (coincide con la primera captura) | ✅ |
| Eventos al terminar la revisión | **8** («8 total» en el listado) | ✅ |

### Eventos generados durante la revisión (listado completo, 8 filas)

| Momento (hora de Chile) | Tipo | Usuario | Entidad | Id. entidad | Resumen |
| :---------------------- | :--- | :------ | :------ | :---------- | :------ |
| 25-10-2026 17:53:27 (UTC-0300) | Acceso exitoso | usuario #1 | usuario | 1 | Acceso de usuario #1 |
| 25-10-2026 17:53:58 (UTC-0300) | Acceso fallido | - | usuario | - | Usuario intentado: usuario desconocido |
| 25-10-2026 17:54:18 (UTC-0300) | Acceso exitoso | usuario #1 | usuario | 1 | Acceso de usuario #1 |
| 25-10-2026 18:01:36 (UTC-0300) | Acceso fallido | - | usuario | - | Usuario intentado: usuario #1 |
| 25-10-2026 18:01:55 (UTC-0300) | Acceso exitoso | usuario #1 | usuario | 1 | Acceso de usuario #1 |
| 25-10-2026 18:02:38 (UTC-0300) | Acceso exitoso | usuario #1 | usuario | 1 | Acceso de usuario #1 |
| 25-10-2026 18:02:47 (UTC-0300) | Acceso fallido | - | usuario | - | Usuario intentado: usuario #1 |
| 25-10-2026 18:02:57 (UTC-0300) | Acceso exitoso | usuario #1 | usuario | 1 | Acceso de usuario #1 |

Resumen: 5 accesos exitosos y 3 fallidos (1 con nombre inexistente y 2 con el usuario `usuario #1` y una contraseña inventada).

### Resultados por punto

| # | Punto a verificar | Resultado observado | Estado |
| :- | :---------------- | :------------------ | :----- |
| 1 | Listado | «Registro de eventos» aparece en el menú «Pedidos». El listado muestra momento, tipo de evento, usuario, entidad afectada, identificador de la entidad y resumen, ordenado del más reciente al más antiguo. | ✅ |
| 2 | Hora de Chile | Todos los momentos salen con la zona al lado, `(UTC-0300)`, el desfase de Chile continental en octubre. El encabezado de la columna dice «Momento (hora de Chile)». | ✅ |
| 3 | Acceso fallido con un nombre que no existe | Fila 17:53:58: usuario `-`, resumen «Usuario intentado: usuario desconocido». No aparece lo que se escribió. | ✅ |
| 3b | Acceso fallido con un usuario que existe (`usuario #1`) | Filas 18:01:36 y 18:02:47: resumen «Usuario intentado: usuario #1». La contraseña inventada que se escribió no aparece en el listado ni en el detalle. | ✅ |
| 4 | Accesos exitosos | Cinco filas con tipo «Acceso exitoso», usuario `usuario #1`, entidad `usuario`, identificador `1` y resumen «Acceso de usuario #1». | ✅ |
| 5 | Solo lectura (listado) | En el menú lateral, «Registro de eventos» no tiene el enlace «Añadir» que sí tienen Clientes, Pedidos y Productos. El listado no ofrece botón de agregar. | ✅ |
| 5b | Solo lectura (detalle) | El detalle se titula «Vista Registro de evento». Solo ofrece el botón «Cerrar» (y «Histórico»); no hay «Guardar» ni «Eliminar» y los campos no son editables. | ✅ |
| 6 | Búsqueda por identificador de la entidad | Buscar `1`: «5 resultados (8 total)», todos de la entidad `usuario` con identificador 1. Buscar `10`: «0 resultados (8 total)»: el 1 no se confunde con el 10. | ✅ |
| 6b | Filtros de la barra lateral | La barra muestra «Por Momento» (Cualquier fecha, Hoy, Últimos 7 días, Este mes, Este año) y «Por Tipo de evento» (con todos los tipos). El desarrollador aplicó «Por Tipo de evento → Acceso fallido» y el listado mostró **3 resultados**, que coinciden con los 3 accesos fallidos de la tabla de arriba. Confirmado con captura: «3 resultados (8 total)», las tres filas son accesos fallidos (18:02:47, 18:01:36 y 17:53:58) y la barra lateral muestra «Borrar todos los filtros». | ✅ |
| 7 | Detalle de un evento | Detalle del acceso fallido de las 18:02:47: momento `25-10-2026 18:02:47 (UTC-0300)`, tipo «Acceso fallido», usuario `-`, entidad `usuario`, identificador `-`, resumen «Usuario intentado: usuario #1». | ✅ |
| 8 | Vista a 360 px | A 360 × 800 el encabezado, la barra de búsqueda y el listado se ven bien y se leen. La tabla es más ancha que la pantalla, así que aparece una barra de desplazamiento horizontal para ver usuario, entidad, identificador y resumen. Es el comportamiento normal de las tablas del admin de Django en pantallas angostas. | ✅ (con desplazamiento horizontal) |

### Cobertura por pruebas automáticas (para contraste)

La parte que no se probó a mano la cubren las 9 pruebas de `test_admin_eventos.py` (filtro por tipo y por usuario, 403 para un usuario `is_staff` sin superusuario, ausencia de agregar, modificar y eliminar, y número de consultas igual con 1 y con 20 filas). La suite completa está en 72 pruebas en verde, tres veces seguidas.

### Salida de consola registrada

Con `runserver`, la petición a `/favicon.ico` (404) salió en la terminal con el formato acordado en la 01-02:

```text
nivel=WARNING registrador=django.server metodo=- ruta=- usuario=- excepcion=- mensaje="\"GET /favicon.ico HTTP/1.1\" 404 13842"
```

- Esa línea la emite `django.server`, que existe solo en `runserver`. No es `django.request`, así que no contradice la decisión del 2026-10-25 de que los 404 no vayan a `error.log`.
- El `favicon.ico` sigue siendo una propuesta menor en `registro-pendientes.md`.

### Pendiente

Ninguno.

### Conclusión

La 01-05 cumple todos los criterios de la revisión manual en la réplica (listado, filtros y detalle), respaldados además por las 9 pruebas automáticas del admin. No requiere migración. El criterio «Revisión manual en la réplica con capturas o descripción» queda completo.
