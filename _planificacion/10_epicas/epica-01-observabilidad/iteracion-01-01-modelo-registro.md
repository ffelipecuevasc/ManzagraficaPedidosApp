# Iteración 01-01 · Modelo de registro de eventos

- **Épica:** 01 · Observabilidad
- **Estado:** Pendiente
- **Subfase del plan:** 1.1
- **Depende de:** Épica 00
- **RDA relacionadas:** RDA-003, RDA-005 (reemplazada en parte), RDA-008, RDA-013 (nueva, se escribe aquí)
- **Hallazgos que cierra:** ninguno por sí sola. Avanza AUD-01-005.
- **Cambio de esquema:** Clase 2 (una tabla nueva con sus índices)
- **Respaldo previo al despliegue:** Sí (se despliega en 01-06)

## Objetivo

Crear el modelo que responde «¿quién hizo qué y cuándo?», con índices, retención y purga desde el primer día, y dejar escrita la decisión de que los errores van al registro del servidor y no a una tabla.

## Tareas

1. **Documentar la decisión de la épica** (antes de programar):
   - `decisiones.md`: escribir RDA-013 («Errores en el registro del servidor con `logging`; eventos de negocio en MySQL»), con contexto, decisión, alternativas (tabla de errores en MySQL, descartada por YAGNI: el usuario final no diagnostica errores; servicios externos, descartados por la lista blanca) y consecuencias (los errores dependen de la rotación de registros de PythonAnywhere; su revisión periódica es la 07-03). Marcar RDA-005 como «Reemplazada en parte por RDA-013» y actualizar la tabla del índice.
   - `auditoria-tecnica.md`: actualizar la solución de AUD-01-005.
   - `registro-pendientes.md`: la decisión de retención pasa a ser solo de la tabla de eventos, y los nombres de 01-01, 01-02, 01-03 y 01-05 en la tabla de estado se actualizan a los de estos archivos (revisión del 2026-10-25).
2. **Estimación previa de crecimiento**, antes de escribir la migración: con los volúmenes de `linea-base-produccion.md`, calcular cuántas filas de eventos genera un mes normal (pedidos, pagos, cambios de estado, accesos, respaldos) y cuánto pesan, con un tamaño medio de fila supuesto y explicado. Contrastarlo con el disco libre (180,8 MB usados de 512 MB al 2026-10-20). Si el resultado incomoda, proponer reducir el inventario de eventos antes de seguir.
3. **Modelo de eventos**: momento, tipo de evento (opciones cerradas según el inventario de 01-04), usuario (relación que admite nulo para eventos del sistema y que no borra el evento si se elimina el usuario), entidad afectada, identificador de la entidad y un resumen legible. Sin copias de objetos completos ni datos personales en el resumen más allá de identificadores.
4. **Índices** sobre los campos de consulta: fecha, tipo de evento y usuario.
5. **Retención y purga**: una función que elimina eventos más antiguos que la retención (`PENDIENTE_DESARROLLADOR`: días de retención; propuesta de partida: 365 días, a confirmar con la estimación de la tarea 2) y una orden de gestión `purgar_registros` que la ejecuta, que el desarrollador puede correr a mano hasta que la orden de mantención diaria (06-02) la absorba.
6. **Migración** (con consulta): generarla, clasificarla con `sqlmigrate` y aplicarla en la réplica local (`$env:DB_NAME = 'manzagrafica_replica'`) midiendo la duración.

## Criterios de aceptación

- [ ] RDA-013 está escrita, RDA-005 figura como reemplazada en parte y AUD-01-005 tiene su solución actualizada.
- [ ] La estimación de crecimiento está en la bitácora con sus supuestos, el resultado en filas y en MB por mes y el porcentaje del disco libre que representa.
- [ ] `sqlmigrate` de la migración nueva muestra solo `CREATE TABLE` y `CREATE INDEX` (Clase 2); el SQL completo está en la bitácora.
- [ ] La migración se aplica en la réplica local sin errores y su duración quedó medida.
- [ ] `python manage.py makemigrations --check --dry-run` no detecta cambios pendientes tras crear la migración.
- [ ] Una prueba crea eventos con fechas antiguas y recientes, ejecuta la purga y comprueba que solo quedan los recientes.
- [ ] `python manage.py purgar_registros` corre en la réplica e informa cuántas filas eliminó.
- [ ] Eliminar un usuario no elimina sus eventos (prueba).

## Fuera de alcance

- Una tabla de errores (descartada por RDA-013).
- Escribir en la tabla desde la aplicación (va en 01-02 y 01-04).
- Programar la purga en la tarea diaria (va en 06-02).

## Datos requeridos del cliente

- Ninguno.