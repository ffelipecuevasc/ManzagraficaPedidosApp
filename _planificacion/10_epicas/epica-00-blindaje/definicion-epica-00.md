# Épica 00 · Blindaje y punto de retorno

- **Estado:** Reabierta el 2026-10-27 solo para la 00-07 (cerrada el 2026-10-25 con 00-01 a 00-06)
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
7. Un segundo despliegue temprano y aislado: desactivar `btn-confirmar-pedido` («Crear Pedido») al primer envío del formulario de pedido, al crear y al editar (plantilla compartida `pedido_form.html`), con la etiqueta `v0.3-doble-envio` después de validar `v1.2-capturas` (00-07, AUD-04-001). Las cotizaciones no se tocan. El lado del servidor, los demás formularios y la regresión R21 siguen en la 03-04.

Esta épica no corrige defectos de lógica de negocio: los mide y deja la red de seguridad para corregirlos después.

## Reparto del trabajo

El agente no accede a producción (`AGENTS.md`, sección 6). En esta épica eso pesa más que en ninguna otra: el agente prepara guiones de solo lectura, scripts de verificación y procedimientos, y el desarrollador los ejecuta en PythonAnywhere y en su máquina. Cada iteración que lo necesita tiene su archivo de evidencia con los pasos exactos.

## Iteraciones

| Iteración | Nombre | Subfase |
| :-------- | :----- | :------ |
| 00-01 | Línea base de producción (Terminada) | 0.1 |
| 00-02 | Protocolo de respaldo verificado (Terminada) | 0.2 |
| 00-03 | Réplica local fiel (Terminada) | 0.3 |
| 00-04 | Higiene del repositorio (Terminada) | 0.4 |
| 00-05 | Protocolo de versionado, despliegue y retroceso (Terminada) | 0.5 |
| 00-06 | Correcciones tempranas de riesgo nulo (Terminada) | 0.6 |
| 00-07 | Correcciones tempranas II (Pendiente; creada el 2026-10-27; crear y editar pedido, `v0.3-doble-envio`) | 0.6 (continuación) |

## Decisiones de la épica

- Los procedimientos operativos viven en `docs/operacion/` (RDA-012, propuesta).
- La reducción de la retención de volcados en el **código** de rotación queda para 06-03; en esta épica se reduce a mano en el servidor, después de tener una copia verificada fuera de él.
  - **Nota 2026-10-21 (decisión vigente):** el desarrollador decidió conservar en el servidor los **5 volcados** que mantiene hoy la aplicación (6,19 MB), sin reducción a mano. Ver la iteración 00-02 y `docs/operacion/respaldo.md`.
- El despliegue de 00-04 (cambia `settings.py`) se hace con la lista de comprobación de 00-05: es su primer uso real. El despliegue de 00-06 es el segundo, separado, con su propia etiqueta.

## Criterio de término

- [x] `linea-base-produccion.md` tiene todas sus cifras con fecha de medición. Completa el 2026-10-20 (00-01).
- [x] Existe al menos un respaldo de producción descargado, verificado por `scripts/verificar_respaldo.py` y guardado en una carpeta cifrada fuera del servidor y fuera del repositorio. Código 0, 18 de 18 tablas, carpeta con BitLocker (00-02, 2026-10-21).
- [x] La aplicación arranca en local contra la réplica restaurada y la tabla de paridad no tiene divergencias sin resolver. Restauración en 4,17 s, `check` limpio, migraciones 0001 a 0006 (00-03, 2026-10-21).
- [x] Un clon limpio del repositorio no contiene `.idea/`, credenciales ni volcados. Commit `965227d` (00-04, 2026-10-21).
- [x] El retroceso se ensayó contra la réplica local en menos de 15 minutos, medido. 1,31 min (00-05, 2026-10-22).
- [x] Los despliegues de 00-04 y 00-06 están etiquetados y la evidencia de 00-06 muestra que las 404 de `/robots.txt` bajaron a 0. El informe de desconexiones a 28 días del despliegue de 00-06 se entrega en paralelo y no bloquea el término de la épica ni el inicio de la Épica 01. `v0.1-higiene` (2026-10-23, 00:26) y `v0.2-correcciones` (2026-10-23, 18:35), ambos sin retroceso; 404 de `/robots.txt` en 0 desde el despliegue (C1, 2026-10-25), con el seguimiento indicado abajo.

## Resumen de cierre (2026-10-25)

La épica se cerró por decisión del desarrollador con la evidencia C1 de la 00-06. El objetivo se cumple: si un despliegue sale mal, se vuelve a la etiqueta anterior en minutos (ensayo: 1,31 min) y hay un respaldo verificado fuera del servidor.

- **Etiquetas:** `v0.0-inicial` (estado de partida), `v0.1-higiene` (00-04) y `v0.2-correcciones` (00-06, en producción). El servidor se actualiza con `git fetch origin --tags` y `git checkout <etiqueta>`, nunca con `git pull`.
- **Hallazgos cerrados en la épica:** AUD-01-020, AUD-01-021, AUD-01-023, AUD-02-009 y AUD-02-022. **Avanzados:** AUD-01-011 (sigue en 05-01) y AUD-01-024 (sigue en 06-06). **Nuevos:** AUD-02-019 a AUD-02-023.
- **Mediciones de la 00-06:** importar `pedidos.urls` bajó de 1.029,0 ms a 26,3 ms de media en local; las 404 de `/robots.txt` pasaron de 2 a 3 por día a 0 desde el despliegue.

### Seguimientos abiertos (no bloquean la Épica 01)

- **C2 de la 00-06 (2026-11-20):** tasa diaria de `Broken pipe` a 28 días, sin umbral. En el mismo conteo, confirmar que un rastreador real recibe 200 en `/robots.txt` (seguimiento del cierre de AUD-01-020).
- **AUD-02-023:** `media/` sin copia automática; protección manual hasta que el desarrollador defina la iteración de la épica 07.
- **`favicon.ico`:** 404 en producción; hallazgo menor registrado en `registro-pendientes.md`, sección 4.
- **Propuesta para la Épica 04:** redirigir al panel desde el acceso cuando ya hay sesión.
- **`AGENTS.md`, sección 5:** la propuesta del comando del contenedor (bitacora-00-03) sigue pendiente de edición del desarrollador.

## Notas

- **2026-10-27 · Reapertura para la 00-07 (decisión del desarrollador).** Los registros de producción del 2026-10-27 verificaron un pedido duplicado por doble clic (AUD-04-001, Auditoría 04). Se crea la 00-07 con una sola corrección del lado del cliente y despliegue propio, y la épica se reabre solo para ella. La 00-06 y su bitácora no cambian. Los criterios de término de arriba siguen cumplidos; la épica se vuelve a cerrar cuando la 00-07 termine.
- **2026-10-27 · Decisiones del desarrollador sobre la 00-07:** alcance crear y editar pedido; script propio en `pedido_form.html`; etiqueta `v0.3-doble-envio` con retroceso a `v1.2-capturas`; despliegue el domingo 2026-11-01 después de validar `v1.2-capturas` ([iteracion-00-07](iteracion-00-07-correcciones-tempranas-ii.md)).
