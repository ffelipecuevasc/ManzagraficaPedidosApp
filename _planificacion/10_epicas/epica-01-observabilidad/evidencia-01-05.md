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

_(pendiente)_
