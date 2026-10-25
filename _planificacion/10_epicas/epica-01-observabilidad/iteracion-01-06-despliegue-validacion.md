# Iteración 01-06 · Despliegue y validación de la observabilidad

- **Épica:** 01 · Observabilidad
- **Estado:** Pendiente
- **Subfase del plan:** 1.6
- **Depende de:** 01-03, 01-04, 01-05
- **RDA relacionadas:** RDA-003, RDA-007, RDA-008, RDA-013
- **Hallazgos que cierra:** AUD-01-005 (con 01-01 a 01-05)
- **Cambio de esquema:** Clase 2 (la migración de 01-01)
- **Respaldo previo al despliegue:** Sí

## Objetivo

Llevar la observabilidad a producción con el protocolo de 00-05 y demostrar con un error real que se diagnostica en menos de cinco minutos desde `error.log`, y que los eventos de negocio quedan en el admin.

## Tareas

1. **Preparar el despliegue**: lista de comprobación de `docs/operacion/despliegue.md` completa en local (pruebas, `check --deploy`, `makemigrations --check`, `sqlmigrate` de la migración con su clase). Etiqueta `v1.1-observabilidad`, con partida y destino de retroceso `v0.2-correcciones`. El mensaje de la etiqueta se escribe con su fecha real antes de crearla; nunca con texto de relleno.
2. **Respaldo previo** generado, descargado a la carpeta cifrada y verificado con `scripts/verificar_respaldo.py` (`docs/operacion/respaldo.md`).
3. **Método para provocar un error controlado** en producción, sin modificar datos, propuesto por el agente y elegido por el desarrollador (`PENDIENTE_DESARROLLADOR`). Candidato principal: abrir la eliminación de un pago (AUD-02-002, mientras siga abierto), que hoy falla siempre sin escribir nada. Alternativa: una ruta temporal solo para superusuarios que se retira en el despliegue siguiente.
4. **Archivo de evidencia** `evidencia-01-06.md`, con comandos para PowerShell 7 y Bash ya probados en sus particularidades conocidas (por ejemplo, `-MaximumRedirection 0` falla en PowerShell 7.6; capturar con `| Select-Object -Last 1` la salida de `manage.py shell`):
   - Respaldo, etiqueta, `checkout` y migración aplicada.
   - Provocar el error, anotar la hora y medir el tiempo hasta encontrar en `error.log` la línea con tipo de excepción, traza completa, método, ruta y usuario. Recordar que `error.log` está en UTC.
   - Generar un PDF y comprobar que `error.log` no recibe líneas informativas de `fontTools`.
   - Ejecutar una acción del inventario (por ejemplo, cambiar el estado de un pedido de prueba si existe, o un acceso) y verla en el admin de eventos.
   - Una semana después: contar filas nuevas de eventos, su peso y las líneas de `error.log` por nivel.
5. **Configuración de pruebas de 02-01** (agregado el 2026-10-25): el bloque 3 de `settings.py` (base de pruebas `test_manzagrafica` con bloqueo de nombres reales) viaja en este despliegue. En el servidor, `python manage.py check --deploy` debe seguir sin errores nuevos después del `checkout`; el resultado va en la evidencia.
6. **Sin líneas duplicadas en `error.log`** (agregado el 2026-10-25, 01-02): `LOGGING` reemplaza el manejador de la raíz, pero si PythonAnywhere instala uno propio, cada línea podría salir dos veces. Tras el error controlado, la evidencia muestra que cada línea aparece una sola vez.
7. **Contraste con la estimación** de 01-01 en la bitácora de producción. Si el crecimiento real supera la estimación, proponer el ajuste del inventario antes de cerrar.

## Criterios de aceptación

- [ ] La lista de comprobación previa está completa en la bitácora y el respaldo está verificado.
- [ ] La evidencia muestra la etiqueta `v1.1-observabilidad` y la migración aplicada en producción.
- [ ] El error controlado aparece en `error.log` de producción con tipo de excepción, traza completa, método, ruta, usuario y hora.
- [ ] El tiempo de diagnóstico medido es menor a cinco minutos.
- [ ] Después del despliegue, `error.log` no tiene líneas informativas de `fontTools`.
- [ ] Una acción de negocio real o de prueba aparece en el admin de eventos con su usuario.
- [ ] El crecimiento de una semana de la tabla de eventos está medido en filas y MB y comparado con la estimación.

## Fuera de alcance

- Corregir el error usado para la validación (AUD-02-002 se corrige en 04-01).
- La revisión periódica de `error.log` (va en 07-03).

## Datos requeridos del cliente

- Ninguno.