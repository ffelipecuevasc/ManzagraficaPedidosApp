# Épica 00 · Blindaje y punto de retorno

- **Estado:** En curso (00-01 terminada el 2026-10-20; sigue 00-02)
- **Fase del plan:** 0 (`plan-de-trabajo.md`, «FASE 0»)
- **Objetivo:** construir la infraestructura que hace reversible todo lo demás. Al terminar, el desarrollador puede afirmar sin dudar: «si el próximo despliegue sale mal, vuelvo al estado anterior en menos de quince minutos, sin perder datos».
- **Precondición:** ninguna.

## Alcance

1. Medir el estado real de producción y dejarlo en `00_producto/linea-base-produccion.md`.
2. Un respaldo de producción descargado, verificado y guardado fuera del servidor, con un procedimiento repetible.
3. Una réplica local restaurada desde ese respaldo, con paridad verificada contra producción.
4. Un repositorio sin configuración del IDE ni credenciales, con plantilla de variables de entorno y dependencias legibles.
5. Procedimientos de despliegue y de retroceso, con el retroceso ensayado.
6. Un despliegue temprano y aislado con cuatro correcciones de riesgo nulo.

Esta épica no corrige defectos de lógica de negocio: los mide y deja la red de seguridad para corregirlos después.

## Reparto del trabajo

El agente no accede a producción (`AGENTS.md`, sección 6). En esta épica eso pesa más que en ninguna otra: el agente prepara guiones de solo lectura, scripts de verificación y procedimientos, y el desarrollador los ejecuta en PythonAnywhere y en su máquina. Cada iteración que lo necesita tiene su archivo de evidencia con los pasos exactos.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 00-01 | Línea base de producción (Terminada) | 0.1 |
| 00-02 | Protocolo de respaldo verificado | 0.2 |
| 00-03 | Réplica local fiel | 0.3 |
| 00-04 | Higiene del repositorio | 0.4 |
| 00-05 | Protocolo de versionado, despliegue y retroceso | 0.5 |
| 00-06 | Correcciones tempranas de riesgo nulo | 0.6 |

## Decisiones de la épica

- Los procedimientos operativos viven en `docs/operacion/` (RDA-012, propuesta).
- La reducción de la retención de volcados en el **código** de rotación queda para 06-03; en esta épica se reduce a mano en el servidor, después de tener una copia verificada fuera de él.
- El despliegue de 00-04 (cambia `settings.py`) se hace con la lista de comprobación de 00-05: es su primer uso real. El despliegue de 00-06 es el segundo, separado, con su propia etiqueta.

## Criterio de término

- `linea-base-produccion.md` tiene todas sus cifras con fecha de medición.
- Existe al menos un respaldo de producción descargado, verificado por `scripts/verificar_respaldo.py` y guardado en una carpeta cifrada fuera del servidor y fuera del repositorio.
- La aplicación arranca en local contra la réplica restaurada y la tabla de paridad no tiene divergencias sin resolver.
- Un clon limpio del repositorio no contiene `.idea/`, credenciales ni volcados.
- El retroceso se ensayó contra la réplica local en menos de 15 minutos, medido.
- Los despliegues de 00-04 y 00-06 están etiquetados y la evidencia de 00-06 muestra que las 404 de `/robots.txt` bajaron a 0. El informe de desconexiones a 28 días del despliegue de 00-06 se entrega en paralelo y no bloquea el término de la épica ni el inicio de la Épica 01.
