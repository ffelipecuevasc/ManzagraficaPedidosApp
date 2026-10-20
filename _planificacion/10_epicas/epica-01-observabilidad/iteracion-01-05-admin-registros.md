# Iteración 01-05 · Consulta de registros en el admin

- **Épica:** 01 · Observabilidad
- **Estado:** Pendiente
- **Subfase del plan:** 1.5
- **Depende de:** 01-01
- **RDA relacionadas:** RDA-005
- **Hallazgos que cierra:** ninguno por sí sola. Avanza AUD-01-005.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** Sí (se despliega en 01-06)

## Objetivo

Consultar errores y eventos desde el admin nativo de Django, sin construir pantallas propias: buscar un error por su identificador en segundos.

## Tareas

1. **Admin de errores**: listado con fecha, tipo de excepción, ruta, usuario e identificador; filtros por fecha y tipo; búsqueda por identificador de correlación; detalle con la traza completa en un campo legible.
2. **Admin de eventos**: listado con fecha, tipo, usuario, entidad y resumen; filtros por fecha, tipo y usuario; jerarquía por fecha.
3. **Solo lectura**: sin agregar, modificar ni eliminar desde el admin (la limpieza la hace la purga).
4. **Solo superusuarios**: un usuario del equipo con acceso al admin pero sin ser superusuario no ve estos modelos.
5. **Sin consultas por fila**: el usuario se carga junto con el listado.

## Criterios de aceptación

- [ ] Prueba: un superusuario ve el listado de errores y la búsqueda por identificador devuelve exactamente la fila buscada.
- [ ] Prueba: un usuario con `is_staff` pero sin `is_superuser` recibe 403 o no ve los modelos.
- [ ] Prueba: el admin no ofrece agregar, modificar ni eliminar en ninguno de los dos modelos.
- [ ] El número de consultas del listado de errores no crece con el número de filas mostradas (`assertNumQueries` con 1 y con 20 filas).
- [ ] `python manage.py test pedidos` en verde.

## Fuera de alcance

- Registrar en el admin los modelos de negocio que faltan (`Pago`, `Cotizacion`, ítems, `HistorialBD`) y revisar `PedidoAdmin` (AUD-02-012, va en 06-06).

## Datos requeridos del cliente

- Ninguno.
