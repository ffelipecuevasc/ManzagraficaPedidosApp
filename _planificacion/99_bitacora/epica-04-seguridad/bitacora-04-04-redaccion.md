# Bitácora 04-04 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** la 04-04 queda **Pendiente (redactada, decisiones abiertas D1 a D6)**. Solo documentos; sin código, pruebas ni `manage.py`.

## Resumen

Se redactó [iteracion-04-04](../../10_epicas/epica-04-seguridad/iteracion-04-04-endurecimiento-de-la-restauracion.md): validación de extensión, tamaño y estructura; aborto si el respaldo de emergencia falla o sale vacío; confirmación verificada por el servidor; constancia en `server.log` que sobrevive a la restauración; `.sql` vacío y subida huérfana; respaldo de emergencia en el mismo disco (AUD-02-024) y AUD-05-004. Cada punto tiene su prueba. Orden de despliegue: 04-01 → 04-02 → 04-03 → 04-04.

## Verificación (solo lectura)

- `views.py:1240-1316` (`restaurar_bd`), `utils.py:13-143`, `restaurar_bd.html` (`:36-89`, `:100-112`), `respaldar_bd.html` (lista sin enlace de descarga), `models.py:271-272` (`RegistroEvento.usuario` admite nulo), nombres de pruebas de `test_capturas_amplias.py`.
- `auditoria-tecnica.md` (AUD-02-019, AUD-02-024, AUD-05-004), `definicion-epica-04.md` (notas 01-04 y 01-09), `respaldo.md` (encabezados y sección 4).

## Hallazgos de la lectura

1. **Contradicción:** AUD-02-019 es la rotación por cantidad (06-03), no el `.sql` vacío; la nota de la definición los mezcla. La 04-04 corrige el `.sql` vacío como hallazgo hermano.
2. **Nuevo, no registrado antes:** si la restauración falla, la subida queda en `backups/tmp/` (solo se borra en el camino feliz). Se suma al alcance (punto 6).
3. El respaldo de emergencia no se comprueba: un `mysqldump` con código 0 y salida incompleta dejaría restaurar igual (inferido).
4. La confirmación actual solo vive en el navegador (SweetAlert); el servidor no la verifica.
5. La restauración corre dentro de la petición, en tensión con `AGENTS.md`, regla 8.10; anotado, sin cambio.

## Qué no se pudo ver

- El formato exacto de la cabecera y el final de `mysqldump` 8.0 (inferido; se confirma con un respaldo real de la réplica, sin abrir datos personales en la documentación).
- El uso actual del disco del servidor y cuántos respaldos hay hoy en `backups/`.
- Si el usuario que restaura existe en los volcados de producción.

## Decisiones abiertas

D1 tope de tamaño, D2 qué es un volcado válido, D3 confirmación explícita, D4 constancia, D5 respaldo de emergencia, D6 AUD-05-004. Fila en la sección 3 del registro.

## Archivos

Nuevo `iteracion-04-04-endurecimiento-de-la-restauracion.md`; `definicion-epica-04.md`; `00_producto/registro-pendientes.md` (fila, decisiones, próximo hito 04-05, historial); esta bitácora.
