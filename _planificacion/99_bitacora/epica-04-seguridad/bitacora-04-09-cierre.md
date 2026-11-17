# Bitácora 04-09 · Cierre documental de la redacción (D1 a D4) y destino de los hallazgos

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** la 04-09 queda **Pendiente (redactada, decisiones resueltas)**. Solo documentos; sin código, pruebas ni `manage.py`.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Resuelta como |
| :- | :------------ |
| D1 | Política observada final, solo `'self'`. |
| D2 | Sin nonces. |
| D3 | Variable `CSP_OBSERVACION`, activa por defecto e independiente de `SEGURIDAD_PRODUCCION`. |
| D4 | Reporte en la consola del navegador en la réplica. |

## 04-08: confirmaciones

El desarrollador confirmó `ACCESO_FALLOS_POR_DIRECCION` (defecto 20; `0` apaga solo el contador por dirección) y los dos valores explícitos de 2,5 MB. Se retiró el «por confirmar» de `iteracion-04-08` y del registro. [bitacora-04-08-cierre](bitacora-04-08-cierre.md) se conserva como estaba (registro de lo que se supuso en su momento).

## Destino de los hallazgos sin iteración (decisiones del desarrollador)

| Hallazgo | Destino |
| :------- | :------ |
| AUD-04-003 (búsqueda por GET en los registros) | **Riesgo aceptado y documentado.** |
| AUD-02-030 (recuperación de contraseña y acceso del admin) | **Solo documentado**, sin cambio de código. |
| Eliminar cotización sin evento | **Decisión explícita documentada:** sin evento. |
| Página de error de CSRF | **Épica 08.** |
| AUD-02-023 (`media/` sin copia) | **Documentado y Épica 14.** |
| Pagos borrados en cascada con el pedido | **Iteración nueva 04-10:** confirmación reforzada con evento. El cliente **no ha respondido** si el borrado es intencional (aviso: la iteración no espera esa respuesta y no cambia la cascada). |

La auditoría recibe el destino en la columna de corrección y en el estado de AUD-04-003, AUD-02-030 y AUD-02-023, **sin cambiar gravedades** y por bytes (CRLF intacto). Solo AUD-04-003 pasa a «Riesgo aceptado», porque fue la única con esas palabras del desarrollador (`_planificacion/README.md`, sección 5.3: «solo si el desarrollador lo aceptó y consta dónde»); las otras dos quedan «Abierto (destino: …)». **Falta escribir la nota operativa** de los destinos «documentado» (en `docs/operacion/`, durante la revisión final de la Épica 04).

## Archivos

`iteracion-04-09-politica-de-contenido-en-observacion.md`, `iteracion-04-08-proteccion-del-acceso-y-limites-de-entrada.md`, `definicion-epica-04.md`, `00_producto/registro-pendientes.md` y `00_producto/auditoria-tecnica.md` (ambos por bytes, CRLF intacto) y esta bitácora.
