# Iteración 00-05 · Protocolo de versionado, despliegue y retroceso

- **Épica:** 00 · Blindaje y punto de retorno
- **Estado:** Pendiente
- **Subfase del plan:** 0.5
- **Depende de:** 00-03, 00-04
- **RDA relacionadas:** RDA-003, RDA-007, RDA-012
- **Hallazgos que cierra:** ninguno. Es la condición para todos los despliegues siguientes.
- **Cambio de esquema:** Ninguno (el ensayo usa una migración temporal que nunca se versiona)
- **Respaldo previo al despliegue:** Sí, para el despliegue de 00-04 que sirve de primer uso

## Objetivo

Convertir el despliegue en un procedimiento repetible y el retroceso en algo ensayado: si un despliegue sale mal, volver al estado anterior en menos de 15 minutos, sin perder datos.

## Tareas

1. **Convención de etiquetas** en `docs/operacion/despliegue.md`: etiquetas anotadas que identifican la fase y el propósito. El agente propone un formato (por ejemplo `fase0-higiene-2026-10-25`) y el desarrollador decide (`PENDIENTE_DESARROLLADOR`).
2. **Lista de comprobación previa al despliegue**, en el mismo documento:
   1. Pruebas en verde (cuando existan).
   2. `python manage.py check --deploy` ejecutado con `DEBUG=False`, con cada advertencia anotada.
   3. `python manage.py makemigrations --check --dry-run` sin cambios no previstos.
   4. Migraciones pendientes listadas, cada una con su clase según el SQL de `sqlmigrate`; ninguna de Clase 3.
   5. Respaldo de producción descargado y verificado con `scripts/verificar_respaldo.py` si el despliegue toca datos o esquema.
   6. Estilos compilados, cuando el proyecto compile Tailwind.
   7. Etiqueta anotada creada y publicada por el desarrollador.
3. **Pasos del despliegue en PythonAnywhere**, escritos para el desarrollador: actualizar el código en la consola, instalar dependencias si cambió `requirements.txt`, aplicar migraciones, recolectar estáticos, recargar la web app y verificar después (tres pantallas, el registro de errores del servidor).
4. **Procedimiento de retroceso** `docs/operacion/retroceso.md`, con tres casos:
   1. Sin migraciones: volver el código a la etiqueta anterior y recargar.
   2. Con una migración de Clase 2: el código anterior ignora las tablas, columnas que admiten nulo e índices nuevos, así que basta con volver el código; revertir la migración solo si estorba, y con qué orden.
   3. Con datos dañados: restaurar el último respaldo verificado, asumiendo la pérdida de lo registrado después de él, y avisar al equipo.
5. **Ensayo del retroceso en la réplica local**, guiado por el agente y ejecutado por el desarrollador: desplegar en local una etiqueta de prueba con una migración temporal de Clase 2 (una tabla vacía creada con consulta y eliminada al terminar, nunca versionada), retroceder con el procedimiento y medir el tiempo.
6. **Primer uso real**: el desarrollador despliega 00-04 siguiendo la lista. Evidencia en `evidencia-00-05.md`.

## Criterios de aceptación

- [ ] `docs/operacion/despliegue.md` contiene la convención de etiquetas, la lista de comprobación y los pasos en PythonAnywhere.
- [ ] `docs/operacion/retroceso.md` cubre los tres casos con pasos numerados.
- [ ] El ensayo de retroceso en la réplica quedó medido en la bitácora con un tiempo menor a 15 minutos, y la réplica terminó en el mismo estado de migraciones que al empezar (`showmigrations` antes y después).
- [ ] La migración temporal del ensayo no aparece en `git status` ni en `pedidos/migrations/` al terminar.
- [ ] La evidencia muestra la etiqueta del despliegue de 00-04 (`git tag -n`) y la lista de comprobación completada.

## Fuera de alcance

- Automatizar el despliegue o integración continua (deuda diferida de 07-05).
- Consolidar la lista con los pasos de las fases posteriores (va en 07-02).

## Datos requeridos del cliente

- Ninguno.
