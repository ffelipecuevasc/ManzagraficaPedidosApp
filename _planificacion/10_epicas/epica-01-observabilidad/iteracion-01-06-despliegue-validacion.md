# Iteración 01-06 · Despliegue y validación de la observabilidad

- **Épica:** 01 · Observabilidad
- **Estado:** Pendiente
- **Subfase del plan:** 1.6
- **Depende de:** 01-03, 01-04, 01-05
- **RDA relacionadas:** RDA-003, RDA-005, RDA-007
- **Hallazgos que cierra:** AUD-01-005 (con 01-01 a 01-05)
- **Cambio de esquema:** Clase 2 (la migración de 01-01)
- **Respaldo previo al despliegue:** Sí

## Objetivo

Llevar la observabilidad a producción con el protocolo de 00-05 y demostrar con un error real que se diagnostica en menos de cinco minutos sin acceso al servidor.

## Tareas

1. **Preparar el despliegue**: lista de comprobación de `docs/operacion/despliegue.md` completa en local (pruebas, `check --deploy`, `makemigrations --check`, `sqlmigrate` de la migración con su clase).
2. **Método para provocar un error controlado** en producción, sin modificar datos, propuesto por el agente y elegido por el desarrollador (`PENDIENTE_DESARROLLADOR`). Opciones: una ruta que hoy ya falla sin escribir nada (por ejemplo, abrir con GET la confirmación de eliminar un pago, AUD-02-002, mientras siga abierto), o una ruta temporal solo para superusuarios que se retira en el despliegue siguiente.
3. **Archivo de evidencia** `evidencia-01-06.md`: respaldo descargado y verificado, etiqueta creada, migración aplicada; provocar el error, anotar el identificador que muestra la página, buscarlo en el admin y medir el tiempo desde que se ve el identificador hasta tener la traza; una semana después, contar filas nuevas de errores y de eventos y su peso.
4. **Contraste con la estimación** de 01-01 en la bitácora de producción. Si el crecimiento real supera la estimación, proponer el ajuste del inventario antes de cerrar.

## Criterios de aceptación

- [ ] La lista de comprobación previa está completa en la bitácora.
- [ ] La evidencia muestra la etiqueta del despliegue y la migración aplicada en producción.
- [ ] El error controlado aparece en el admin de producción con traza completa y el mismo identificador que vio el usuario.
- [ ] El tiempo de diagnóstico medido es menor a cinco minutos.
- [ ] El crecimiento de una semana de ambas tablas está medido en filas y MB y comparado con la estimación.

## Fuera de alcance

- Corregir el error usado para la validación (AUD-02-002 se corrige en 04-01).

## Datos requeridos del cliente

- Ninguno.
