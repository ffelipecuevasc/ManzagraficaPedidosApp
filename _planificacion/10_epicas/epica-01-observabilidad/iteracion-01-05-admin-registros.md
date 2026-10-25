# Iteración 01-05 · Consulta de eventos en el admin

- **Épica:** 01 · Observabilidad
- **Estado:** En revisión (2026-10-25; falta la revisión manual de [evidencia-01-05](evidencia-01-05.md); se despliega en 01-06)
- **Subfase del plan:** 1.5
- **Depende de:** 01-01
- **RDA relacionadas:** RDA-008, RDA-013
- **Hallazgos que cierra:** ninguno por sí sola. Avanza AUD-01-005.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** Sí (se despliega en 01-06)

## Objetivo

Consultar quién hizo qué y cuándo desde el admin nativo de Django (decisión del desarrollador del 2026-10-25), sin construir pantallas propias.

## Tareas

1. **Admin de eventos**: listado con fecha, tipo, usuario, entidad, identificador de la entidad y resumen; filtros por fecha, tipo y usuario; búsqueda por identificador de la entidad (por ejemplo, el número de pedido); jerarquía por fecha. **Decisión del 2026-10-25:** sin `date_hierarchy` (contradice la regla técnica 6: trunca con conversión de zona horaria en MySQL); la fecha se filtra con `DateFieldListFilter`, que usa rangos de instantes en hora de Chile.
2. **Fechas legibles en hora de Chile** en el listado y el detalle (la base guarda UTC). Si hoy `TIME_ZONE` no lo permite, dejarlo en la bitácora para 06-01 y mostrar la zona horaria junto a la fecha.
3. **Solo lectura**: sin agregar, modificar ni eliminar desde el admin (la limpieza la hace la purga).
4. **Solo superusuarios**: un usuario del equipo con acceso al admin pero sin ser superusuario no ve el modelo.
5. **Sin consultas por fila**: el usuario se carga junto con el listado.

## Criterios de aceptación

- [x] Prueba: un superusuario ve el listado de eventos y la búsqueda por identificador de entidad devuelve exactamente las filas de esa entidad.
- [x] Prueba: el filtro por tipo y por usuario devuelve solo las filas correspondientes. Además, el filtro por fecha usa el día de Chile.
- [x] Prueba: un usuario con `is_staff` pero sin `is_superuser` recibe 403 o no ve el modelo. No ve el modelo y recibe 403, incluso con los permisos del modelo asignados.
- [x] Prueba: el admin no ofrece agregar, modificar ni eliminar eventos.
- [x] El número de consultas del listado no crece con el número de filas mostradas (`assertNumQueries` con 1 y con 20 filas).
- [ ] Revisión manual en la réplica con capturas o descripción en la bitácora (listado, filtros y detalle). Pendiente del desarrollador: [evidencia-01-05](evidencia-01-05.md).
- [x] `python manage.py test pedidos` en verde. 72 pruebas, tres veces.

## Fuera de alcance

- Una pantalla propia con el diseño de la app (propuesta para una épica posterior, si el desarrollador la pide).
- Consultar errores desde el admin (los errores están en `error.log`, RDA-013).
- Registrar en el admin los modelos de negocio que faltan (`Pago`, `Cotizacion`, ítems, `HistorialBD`) y revisar `PedidoAdmin` (AUD-02-012, va en 06-06).

## Datos requeridos del cliente

- Ninguno.