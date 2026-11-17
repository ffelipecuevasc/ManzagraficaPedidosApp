# Bitácora 04-04 · Cierre documental de la redacción (D1 a D6)

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-04 queda **Pendiente (redactada, decisiones resueltas)**. Solo documentos; sin código, pruebas ni `manage.py`.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Resuelta como |
| :- | :------------ |
| D1 | Tope de 20 MB, constante en el código (`utils.py`). |
| D2 | Volcado válido por estructura y sentencias peligrosas, como propuso la redacción; la misma función valida el respaldo de emergencia. |
| D3 | `RESTAURAR` escrito y exigido por el servidor, además del aviso actual. |
| D4 | Línea en `server.log` antes y después; evento con usuario nulo si el volcado no trae al usuario. |
| D5 | Prefijo `emergencia_`, fuera de la rotación por cantidad, solo el último. Excepción mínima que roza la 06-03. |
| D6 | AUD-05-004 **no** se corrige en la 04-04: pasa a la Épica 08. |

## Ajustes

- Iteración: estado, hallazgos que cierra, decisiones en tabla, alcance sin el punto de AUD-05-004, pasos (sin consulta por `settings.py`; plantilla solo con el campo de D3), pruebas (sin la fila 8; la prueba de la 03-04 sigue igual), riesgos (choque con la regla 8.10 como riesgo y propuesta, D2 sobre el respaldo de emergencia, excepción a la rotación).
- `.sql` vacío unificado como **hallazgo hermano** de AUD-02-019 en la iteración, la definición (nota del 2026-10-26 aclarada) y el registro (fila de la sección 3).
- Auditoría: AUD-05-004 apunta a la Épica 08.
- Registro, sección 4: propuesta de restaurar fuera de la petición.

## Archivos

`iteracion-04-04-endurecimiento-de-la-restauracion.md`, `definicion-epica-04.md`, `00_producto/registro-pendientes.md` (por bytes, CRLF intacto), `00_producto/auditoria-tecnica.md` (por bytes, CRLF intacto) y esta bitácora.
