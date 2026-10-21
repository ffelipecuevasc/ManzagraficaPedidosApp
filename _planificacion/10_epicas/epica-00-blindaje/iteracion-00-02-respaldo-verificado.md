# Iteración 00-02 · Protocolo de respaldo verificado

- **Épica:** 00 · Blindaje y punto de retorno
- **Estado:** Terminada
- **Subfase del plan:** 0.2
- **Depende de:** 00-01
- **RDA relacionadas:** RDA-002, RDA-004, RDA-012
- **Hallazgos que cierra:** ninguno por completo. Avanza AUD-01-014 (la parte de código queda para 06-03).
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no hay despliegue)

## Objetivo

Que exista al menos un respaldo íntegro de producción fuera del servidor, y un procedimiento repetible para generarlo, descargarlo, verificarlo y guardarlo. Un respaldo que vive en el mismo disco que la base no es un respaldo, es una copia; y un respaldo que no se verificó no cuenta.

## Tareas

1. **Script de verificación** `scripts/verificar_respaldo.py`, solo con la biblioteca estándar de Python, que recibe la ruta de un volcado y:
   1. Comprueba que el tamaño supere un mínimo configurable (por defecto, una fracción del peso de la base medido en 00-01).
   2. Comprueba que el archivo termine con la línea de cierre que escribe `mysqldump` (`-- Dump completed`).
   3. Cuenta las sentencias `CREATE TABLE` y las compara con la lista de tablas esperadas (las de Django y las de la aplicación `pedidos`, deducidas de las migraciones).
   4. Calcula el SHA-256 del archivo.
   5. Imprime un informe con tamaño, tablas encontradas y faltantes, presencia de la línea de cierre y hash, **sin imprimir ningún contenido del volcado**, y termina con código 0 si es válido y 1 si no.
2. **Pruebas del script** con tres volcados sintéticos que el agente fabrica en una carpeta temporal (sin datos reales): uno íntegro, uno truncado sin línea de cierre y uno con una tabla faltante.
3. **Procedimiento** `docs/operacion/respaldo.md`:
   1. Cómo generar el volcado en el servidor (botón de respaldo de la aplicación o consola de PythonAnywhere).
   2. Cómo descargarlo y verificarlo con el script antes de darlo por válido; qué hacer si la verificación falla.
   3. Dónde se guarda: carpeta cifrada en la máquina del desarrollador (`PENDIENTE_DESARROLLADOR`), nunca dentro del repositorio ni en una carpeta sincronizada sin cifrar.
   4. Cadencia: uno antes de cada despliegue de fase y uno semanal de rutina, con un registro de una línea por respaldo (fecha, tamaño, hash, resultado) en el mismo documento.
   5. Retención: cuántos volcados quedan en el servidor (`PENDIENTE_DESARROLLADOR`: dos o tres) y cuántos en local.
      - **Decisión del desarrollador (2026-10-20):** en el servidor quedan **5 volcados**, lo que hace hoy la aplicación (6,19 MB, menos del 1,5 % de la cuota). No se borra nada a mano. En local, la retención queda como propuesta por confirmar en `evidencia-00-02.md`.
      - **Confirmado por el desarrollador (2026-10-21):** en local se guardan los 4 volcados semanales más recientes y el previo a cada despliegue, hasta que se cierre la fase siguiente.
4. **Archivo de evidencia** `evidencia-00-02.md`: pasos para generar y descargar un respaldo real, correr el script en la máquina del desarrollador, pegar solo el informe del script (nunca el volcado) y, una vez verificado, borrar a mano en el servidor los volcados que sobren según la retención decidida.
5. Con la evidencia respondida, escribir `bitacora-00-02-produccion.md`.
   - **Ajuste 2026-10-21:** por indicación del desarrollador, la evidencia se consolidó en `bitacora-00-02.md` y no se creó un archivo aparte.

## Criterios de aceptación

- [x] `python scripts/verificar_respaldo.py` termina con código 0 para el volcado sintético íntegro y con código 1 para el truncado y para el que tiene una tabla faltante (salidas copiadas en la bitácora).
- [x] El informe del script no contiene ninguna línea del contenido del volcado.
- [x] `docs/operacion/respaldo.md` cubre generación, descarga, verificación, almacenamiento, cadencia, retención y qué hacer ante una verificación fallida.
- [x] La evidencia muestra el informe de un respaldo real de producción con código de salida 0 y su hash.
- [x] El desarrollador confirma que el respaldo está en una carpeta cifrada fuera del repositorio.
- [x] El listado de `backups/` en el servidor muestra a lo más la cantidad de volcados decidida.
  - **Ajuste 2026-10-20:** la cantidad decidida es 5 (decisión del desarrollador); el criterio se cumple con 5 o menos volcados, sin borrar nada a mano.

## Fuera de alcance

- Cambiar el código de rotación de `limpiar_backups_antiguos` (va en 06-03).
- Sacar la contraseña de la línea de órdenes de `mysqldump` en el código (va en 04-03).
- Restaurar el respaldo (va en 00-03).

## Datos requeridos del cliente

- Ninguno.
