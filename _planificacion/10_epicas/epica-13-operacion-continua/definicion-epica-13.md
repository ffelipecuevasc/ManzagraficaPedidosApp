# Épica 13 · Operación continua

- **Estado:** Pendiente
- **Fase del plan:** 7 (`plan-de-trabajo.md`, «FASE 7»). Era la Épica 07 hasta el 2026-10-27; pasa a ser la 13 para que su número coincida con su orden (RDA-014, decisión del desarrollador).
- **Objetivo:** sostener lo construido. Esta épica no termina: sus iteraciones instalan rutinas que se repiten.
- **Precondición:** cada iteración tiene la suya (ver `registro-pendientes.md`). La vigilancia de la expiración (13-01) puede empezar apenas exista la línea base, porque el riesgo de apagado silencioso existe hoy; el desarrollador decidió el 2026-10-27 mantenerla en el orden de la épica.
- **Última revisión:** 2026-10-27 (renumerada de 07 a 13 y ampliada con las rutinas que agregan las épicas 06, 08, 11 y 14).

## Alcance

1. Recordatorios externos de renovación, procedimiento escrito y visita rutinaria:
   - la **web app** (expira al mes sin renovación);
   - la **tarea programada** de la 06-02, que en el plan gratuito se detiene cada **cuatro semanas** si no se renueva desde el correo de aviso de PythonAnywhere (verificado el 2026-10-27).
2. Lista de comprobación de despliegue consolidada con los pasos de todas las épicas (incluidos «compilar estilos» de la 08-05 y la revisión de la política de seguridad de contenido de la 08-08), como documento vivo en `docs/operacion/despliegue.md`.
3. Rutinas de revisión:
   - **semanal:** errores en `server.log` y ejecución de la tarea diaria;
   - **mensual:** crecimiento de tablas, disco, registro del servidor, que existan los respaldos de los días 1 y 15, y que lleguen los correos de la Épica 11;
   - el hábito de convertir cada error recurrente en una prueba antes de corregirlo.
4. Ensayo semestral de recuperación: restaurar un respaldo en la réplica (y, desde la Épica 14, uno descargado de S3) y verificar su integridad.
5. Registro de la deuda diferida: unificación de `estado_pago` (Clase 3), copia de ítems al duplicar (decisión del cliente), nomenclatura del código e integración continua.
6. Señales que justificarían evaluar un plan de pago, definidas con datos y no por frustración.

## Iteraciones

| Iteración | Nombre | Subfase | Antes |
| :-------- | :----- | :------ | :---- |
| 13-01 | Vigilancia de la expiración de la web app y de la tarea programada | 7.1 | 07-01 |
| 13-02 | Ritual de despliegue consolidado | 7.2 | 07-02 |
| 13-03 | Revisión periódica de registros | 7.3 | 07-03 |
| 13-04 | Ensayo de recuperación ante desastres | 7.4 | 07-04 |
| 13-05 | Deuda diferida y evolución | 7.5 | 07-05 |
| 13-06 | Criterios para evaluar el cambio de plan | 7.6 | 07-06 |

## Decisiones de la épica

- El recordatorio de renovación vive fuera del sistema (calendario personal del desarrollador): si la aplicación se apaga, un aviso dentro de ella no sirve.
- Cada ejecución de una rutina deja una bitácora con un sufijo que dice qué se revisó (`bitacora-13-03-mensual.md`, `bitacora-13-03-mensual-2.md`…). La fecha va dentro del archivo, no en el nombre.
- Respaldo de `media/` (AUD-02-023): la iteración que lo implemente la define el desarrollador; candidatos: una rutina manual en esta épica o el respaldo externo de la Épica 14.

## Criterio de término

- No tiene término: cada iteración se da por instalada cuando su rutina se ejecutó una vez con bitácora, y desde ahí se repite.

## Notas

- **2026-10-27 (reorganización, RDA-014):** renumerada de 07 a 13. Las referencias a 07-01…07-06 en documentos anteriores a esta fecha (bitácoras, auditorías, RDA-013, `docs/operacion/retroceso.md`) se leen como 13-01…13-06. La carpeta cambia de `epica-07-operacion-continua` a `epica-13-operacion-continua`.
