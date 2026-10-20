# Épica 07 · Operación continua

- **Estado:** Pendiente
- **Fase del plan:** 7 (`plan-de-trabajo.md`, «FASE 7»)
- **Objetivo:** sostener lo construido. Esta épica no termina: sus iteraciones instalan rutinas que se repiten.
- **Precondición:** cada iteración tiene la suya (ver `registro-pendientes.md`). La vigilancia de la expiración (07-01) puede empezar apenas exista la línea base, porque el riesgo de apagado silencioso existe hoy.

## Alcance

1. Recordatorio externo de renovación de la web app, procedimiento escrito y visita rutinaria.
2. Lista de comprobación de despliegue consolidada con los pasos de todas las fases, como documento vivo en `docs/operacion/despliegue.md`.
3. Rutinas de revisión: semanal (errores, ejecución de la tarea diaria) y mensual (crecimiento de tablas, disco, registro del servidor), y el hábito de convertir cada error recurrente en una prueba antes de corregirlo.
4. Ensayo semestral de recuperación: restaurar un respaldo en la réplica y verificar su integridad.
5. Registro de la deuda diferida: unificación de `estado_pago` (Clase 3), copia de ítems al duplicar (decisión del cliente), nomenclatura del código e integración continua.
6. Señales que justificarían evaluar un plan de pago, definidas con datos y no por frustración.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 07-01 | Vigilancia de la expiración de la web app | 7.1 |
| 07-02 | Ritual de despliegue consolidado | 7.2 |
| 07-03 | Revisión periódica de registros | 7.3 |
| 07-04 | Ensayo de recuperación ante desastres | 7.4 |
| 07-05 | Deuda diferida y evolución | 7.5 |
| 07-06 | Criterios para evaluar el cambio de plan | 7.6 |

## Decisiones de la épica

- El recordatorio de renovación vive fuera del sistema (calendario personal del desarrollador): si la aplicación se apaga, un aviso dentro de ella no sirve.
- Cada ejecución de una rutina deja una bitácora con un sufijo que dice qué se revisó (`bitacora-07-03-mensual.md`, `bitacora-07-03-mensual-2.md`…). La fecha va dentro del archivo, no en el nombre.

## Criterio de término

- No tiene término: cada iteración se da por instalada cuando su rutina se ejecutó una vez con bitácora, y desde ahí se repite.
