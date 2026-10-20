# Iteración 01-01 · Modelo de registro de errores y eventos

- **Épica:** 01 · Observabilidad
- **Estado:** Pendiente
- **Subfase del plan:** 1.1
- **Depende de:** Épica 00
- **RDA relacionadas:** RDA-003, RDA-005, RDA-008
- **Hallazgos que cierra:** ninguno por sí sola. Avanza AUD-01-005.
- **Cambio de esquema:** Clase 2 (dos tablas nuevas con sus índices)
- **Respaldo previo al despliegue:** Sí (se despliega en 01-06)

## Objetivo

Crear los dos modelos que responden preguntas distintas: «¿qué se rompió y por qué?» (errores) y «¿quién hizo qué y cuándo?» (eventos), con índices, retención y purga desde el primer día.

## Tareas

1. **Estimación previa de crecimiento**, antes de escribir la migración: con los volúmenes de `linea-base-produccion.md`, calcular cuántas filas de eventos genera un mes normal (pedidos, pagos, cambios de estado, accesos) y cuánto pesan, con un tamaño medio de fila supuesto y explicado. Contrastarlo con el disco libre. Si el resultado incomoda, proponer reducir el inventario de eventos antes de seguir.
2. **Modelo de errores**: momento, tipo de excepción, mensaje, traza completa, ruta, método HTTP, usuario (relación que admite nulo y no borra el registro si se elimina el usuario) e identificador de correlación único.
3. **Modelo de eventos**: momento, tipo de evento (opciones cerradas según el inventario de 01-04), usuario (admite nulo para eventos del sistema), entidad afectada, identificador de la entidad y un resumen legible. Sin copias de objetos completos ni datos personales en el resumen más allá de identificadores.
4. **Índices** sobre los campos de consulta: fecha en ambos modelos, tipo de evento y el identificador de correlación.
5. **Retención y purga**: una función que elimina registros más antiguos que la retención de cada tabla (`PENDIENTE_DESARROLLADOR`: días de retención de errores y de eventos) y una orden de gestión `purgar_registros` que la ejecuta y que el desarrollador puede correr a mano hasta que la orden de mantención diaria (06-02) la absorba.
6. **Migración** (con consulta): generarla, clasificarla con `sqlmigrate` y aplicarla en la réplica local midiendo la duración.

## Criterios de aceptación

- [ ] La estimación de crecimiento está en la bitácora con sus supuestos, el resultado en filas y en MB por mes y el porcentaje del disco libre que representa.
- [ ] `sqlmigrate` de la migración nueva muestra solo `CREATE TABLE` y `CREATE INDEX` (Clase 2); el SQL completo está en la bitácora.
- [ ] La migración se aplica en la réplica local sin errores y su duración quedó medida.
- [ ] `python manage.py makemigrations --check --dry-run` no detecta cambios pendientes tras crear la migración.
- [ ] Una prueba crea registros con fechas antiguas y recientes, ejecuta la purga y comprueba que solo quedan los recientes.
- [ ] `python manage.py purgar_registros` corre en la réplica e informa cuántas filas eliminó de cada tabla.
- [ ] Eliminar un usuario no elimina sus registros de errores ni de eventos (prueba).

## Fuera de alcance

- Escribir en las tablas desde la aplicación (va en 01-02 y 01-04).
- Programar la purga en la tarea diaria (va en 06-02).

## Datos requeridos del cliente

- Ninguno.
