# Procedimiento de respaldo verificado

Cómo generar, descargar, verificar y guardar un respaldo de la base de producción. Un respaldo que vive en el mismo disco que la base no es un respaldo, es una copia; y un respaldo que no se verificó no cuenta.

- **Creado en:** iteración 00-02 (2026-10-20).
- **Lo ejecuta:** el desarrollador. Los agentes no generan, no descargan ni abren volcados.
- **Comandos:** PowerShell en Windows 10, desde la raíz del repositorio.

## 1. Antes de empezar: cómo rota el servidor

La aplicación guarda los volcados en `backups/` del servidor y conserva **solo los 5 más recientes** (`limpiar_backups_antiguos`, `mantener=5`). Cada volcado nuevo borra el más antiguo.

- **Cada clic en «Generar Nuevo Respaldo BD» crea un volcado** y desplaza al más antiguo de los 5. Haz un solo clic y espera la descarga.
- **Ese botón es un enlace GET** (`/base_datos/respaldar_bd/accion/`). Cada vez que esa dirección se abre se crea un volcado: al recargar la página, al reabrir la pestaña o al volver a pulsar el enlace en el historial del navegador. No abras esa dirección varias veces. Se corrige en la iteración 04-01 (AUD-02-006).
- **Cada restauración crea además un volcado de emergencia** antes de restaurar, que también cuenta como uno de los 5.
- Con 5 volcados de unos 1,4 MB (6,19 MB medidos el 2026-10-20), el disco no es el límite: la cuota es de 512 MB y se usaba el 35 %.

**Hora del nombre del archivo.** El nombre (`respaldo_DD-MM-AAAA_HH-MM-SS.sql`) lleva la **hora de Chile**, porque `TIME_ZONE = 'America/Santiago'` fija la zona horaria del proceso. La fecha y hora que muestra el servidor (panel de archivos o `ls -l`) está en **UTC**. Ejemplo medido: `respaldo_20-10-2026_13-09-17.sql` figura a las 16:09 UTC (3 horas de diferencia en horario de verano), y `respaldo_22-06-2026_20-37-15.sql`, a las 00:37 UTC del día siguiente (4 horas de diferencia en horario de invierno).

## 2. Generar y descargar

**Opción A, desde la aplicación (recomendada):**

1. Inicia sesión con un usuario superusuario y abre «Respaldar BD» (`/base_datos/respaldar_bd/`).
2. Pulsa **una sola vez** «Generar Nuevo Respaldo BD». El navegador descarga el `.sql` recién creado.
3. Si la descarga no empieza o aparece «Error crítico», no repitas el clic de inmediato: revisa en la misma pantalla si el volcado quedó listado. Si quedó, descárgalo desde el panel de archivos (opción B, paso 2).

**Opción B, desde PythonAnywhere (si la aplicación no responde):**

1. Genera el volcado desde una consola Bash con `mysqldump`, con las mismas opciones que usa la aplicación (`--no-tablespaces --set-gtid-purged=OFF`). No agregues `--skip-comments`: esa opción quita la línea de cierre que el script verifica.
2. Descarga el archivo desde la pestaña **Files** del panel.
3. Un volcado hecho a mano dentro de `backups/` también cuenta en la rotación la próxima vez que la aplicación genere uno.

Guarda la descarga **directamente** en la carpeta de respaldos definida por el desarrollador. No la dejes en `Descargas`, ni en el escritorio, ni dentro del repositorio.

## 3. Verificar

```powershell
python scripts\verificar_respaldo.py "<ruta del volcado>"
$LASTEXITCODE
```

- `0`: el volcado es válido. `1`: no es válido o no se pudo leer.
- El script revisa el tamaño (mínimo 500.000 bytes por defecto; se cambia con `--min-bytes N`), la línea de cierre `-- Dump completed`, las 18 tablas esperadas y el SHA-256. El informe no muestra ninguna línea del volcado, así que se puede copiar en la tabla de la sección 6 y en las evidencias.
- Para comprobar el hash por otro camino:

```powershell
(Get-FileHash "<ruta del volcado>" -Algorithm SHA256).Hash.ToLower()
```

Debe coincidir con la línea `SHA-256` del informe.

### Si la verificación falla

1. **No borres nada en el servidor** y no restaures con ese archivo.
2. Lee el motivo en la última línea del informe:
   - **Tamaño bajo el mínimo o sin línea de cierre:** casi siempre es una descarga interrumpida. Vuelve a descargar **el mismo** volcado desde la pestaña Files (no generes otro) y verifícalo de nuevo.
   - **Tabla faltante:** el volcado está incompleto o la base cambió de esquema. Si una migración nueva agregó una tabla, hay que actualizar la lista del script en una iteración; si no, avisa antes de seguir.
3. Si el volcado del servidor también falla, genera uno nuevo (un solo clic) y verifícalo.
4. Si sigue fallando, detén el despliegue previsto y registra el fallo en la tabla de la sección 6 con el resultado «NO VÁLIDO».

No bajes el tamaño mínimo ni ignores la línea de cierre para que un volcado pase: un criterio se cambia solo con una decisión registrada.

## 4. Dónde se guarda

- En **la carpeta de respaldos definida por el desarrollador**: una carpeta cifrada en su máquina, fuera del repositorio. Su ruta no se escribe en el repositorio.
- Nunca dentro del repositorio ni en una carpeta sincronizada con la nube sin cifrar (RDA-002): los volcados contienen nombres, teléfonos y montos de clientes reales.
- Los agentes de IA no leen, no abren ni copian esa carpeta (`AGENTS.md`, sección 6).

## 5. Cadencia y retención

**Cadencia:**

- **Uno antes de cada despliegue de fase**, verificado antes de empezar el despliegue.
- **Uno semanal de rutina.**

Motivo: hasta el 2026-10-20, los volcados del servidor se hicieron sin calendario y tuvieron huecos de hasta 120 días entre uno y otro (el mayor, de 119 días, entre el 2026-06-23 y el 2026-10-20 en UTC, `linea-base-produccion.md`, sección 3).

**Retención:**

| Dónde | Cuántos | Estado |
| :---- | :------ | :----- |
| Servidor (`backups/`) | 5, los que conserva hoy la aplicación | Decidido por el desarrollador el 2026-10-20 |
| Carpeta de respaldos definida por el desarrollador | Los 4 volcados semanales más recientes y el previo a cada despliegue, hasta que se cierre la fase siguiente | Confirmado por el desarrollador el 2026-10-21 |

Con la retención local vigente, un volcado previo a un despliegue de la fase N se puede borrar cuando la fase N+1 queda terminada.

## 6. Registro de respaldos

Una línea por respaldo verificado (o fallido). Solo fecha, tamaño, hash y resultado: nunca contenido del volcado.

| Fecha (hora de Chile) | Motivo | Tamaño (bytes) | SHA-256 | Resultado |
| :-------------------- | :----- | :------------- | :------ | :-------- |
| 2026-10-20 13:09:17 | Primer respaldo verificado (iteración 00-02) | 1.438.471 | `0fea064cb65fa1fc620663f2d66f6406d943489cd426a6e0cb37f31249d8d008` | VÁLIDO (código 0) |
| 2026-10-22 23:56:36 | Previo al despliegue `v0.1-higiene` (iteración 00-05) | 1.444.819 | `90765c548e5c8f9676431c3c774e4d5aea6deed2559c91cdec0f773130de5fbe` | VÁLIDO (código 0) |
