# Iteración 01-04 · Instrumentación de eventos de negocio

- **Épica:** 01 · Observabilidad
- **Estado:** Pendiente
- **Subfase del plan:** 1.4
- **Depende de:** 01-02
- **RDA relacionadas:** RDA-008
- **Hallazgos que cierra:** ninguno por sí sola. Avanza AUD-01-005.
- **Cambio de esquema:** Ninguno (si el inventario cambia las opciones del tipo de evento, es Clase 1 y se verifica con `sqlmigrate`)
- **Respaldo previo al despliegue:** Sí (se despliega en 01-06)

## Objetivo

Que cada acción de negocio crítica deje un evento con quién, qué, sobre qué y cuándo, escrito solo después de que la operación se confirmó.

## Tareas

1. **Inventario de eventos**, en una tabla en la bitácora con el punto exacto de instrumentación de cada uno. Punto de partida del plan:
   - Pedido: creación, modificación, eliminación, cambio de estado, duplicación.
   - Pago: registro, modificación, eliminación.
   - Cotización: conversión a pedido.
   - Cliente y producto: eliminación.
   - Acceso: exitoso y fallido (con las señales de autenticación de Django). Para el fallido se registra el nombre de usuario intentado, nunca la contraseña.
   - Base de datos: respaldo generado y restauración ejecutada, con el usuario que la ejecutó.
2. **Eventos sin usuario**: los que genere el sistema (la futura orden de mantención) se registran con usuario nulo y un origen identificable.
3. **Instrumentar** cada punto del inventario con el servicio de 01-02.
4. **Pruebas**: una por evento del inventario.

## Criterios de aceptación

- [ ] El inventario final está en la bitácora y coincide con las opciones del tipo de evento del modelo.
- [ ] Cada evento del inventario tiene una prueba que ejecuta la operación y comprueba exactamente una fila nueva con el tipo, el usuario y la entidad correctos.
- [ ] Prueba: las vistas de solo lectura (listados, detalles, estadísticas) no crean eventos.
- [ ] Prueba: un acceso fallido registra el evento sin la contraseña.
- [ ] Prueba: la restauración de base de datos registra el evento con el usuario que la ejecutó (con la restauración simulada, sin ejecutar `mysql`).
- [ ] `python manage.py test pedidos` en verde.

## Fuera de alcance

- Hacer atómicas las operaciones instrumentadas (va en la Épica 03). Mientras tanto, el evento se escribe tras el guardado que hoy existe.
- Convertir a POST las rutas que hoy escriben con GET (va en 04-01).

## Datos requeridos del cliente

- Ninguno.
