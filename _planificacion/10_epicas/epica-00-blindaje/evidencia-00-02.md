# Evidencia 00-02 · Protocolo de respaldo verificado

- **Fecha del pedido:** 2026-10-20
- **Pedido por:** Claude Code (Opus 5.5)
- **Criterios que dependen de esta evidencia:** informe de un respaldo real con código 0 y su hash; respaldo en carpeta cifrada fuera del repositorio; `backups/` del servidor con a lo más 5 volcados.

> Este archivo existe solo porque el agente no pudo obtener estos datos por su cuenta. Responde solo lo que se pide. **Nunca pegues contenido del volcado**, solo el informe del script.

## Qué intentó el agente

| Dato | Qué intentó en local | Por qué se necesita producción |
| :--- | :---------- | :-------------- |
| Informe del respaldo real | Probó el script con tres volcados sintéticos (códigos 0, 1 y 1) | El volcado real tiene datos de clientes: el agente tiene prohibido leerlo o abrirlo (`AGENTS.md`, sección 6) |
| Carpeta cifrada | Nada: su ruta no está en el repositorio y no debe estarlo | Solo el desarrollador sabe dónde está y si está cifrada |
| Volcados en `backups/` | La línea base del 2026-10-20 informa 5 | El agente no accede a PythonAnywhere; hay que confirmar que no cambió |

## Qué necesito del desarrollador

### 1. Informe del script sobre el respaldo del 2026-10-20

- **Para qué:** criterio «La evidencia muestra el informe de un respaldo real de producción con código de salida 0 y su hash».
- **Cómo obtenerlo** (PowerShell, desde la raíz del repositorio):

```powershell
python scripts\verificar_respaldo.py "<ruta del volcado en la carpeta de respaldos>"
"Codigo de salida: $LASTEXITCODE"
(Get-FileHash "<ruta del volcado en la carpeta de respaldos>" -Algorithm SHA256).Hash.ToLower()
```

  El renglón `Archivo:` muestra solo el nombre del archivo, no la ruta. Si la línea de cierre sale `AUSENTE`, pega igual el informe y no cambies nada: se decide aparte.
- **Respuesta:** (pega las líneas del informe, el código de salida y el hash de `Get-FileHash`)

### 2. Carpeta cifrada

- **Para qué:** criterio «El desarrollador confirma que el respaldo está en una carpeta cifrada fuera del repositorio».
- **Cómo obtenerlo:** confirma con sí o no las tres cosas, sin escribir la ruta: (a) el volcado está en la carpeta de respaldos definida por el desarrollador; (b) esa carpeta está cifrada (indica el método, por ejemplo BitLocker o VeraCrypt); (c) no está dentro del repositorio ni en una carpeta sincronizada sin cifrar.
- **Respuesta:**

### 3. Volcados en el servidor

- **Para qué:** criterio «El listado de `backups/` en el servidor muestra a lo más la cantidad de volcados decidida» (5). **No hay que borrar nada a mano.**
- **Cómo obtenerlo:** en una consola Bash de PythonAnywhere, desde la carpeta del proyecto:

```bash
ls -l backups/*.sql | wc -l
```

- **Respuesta:** (el número)

### 4. Retención local

- **Para qué:** cerrar la propuesta de `docs/operacion/respaldo.md`, sección 5.
- **Pregunta:** ¿confirmas que en local guardas los 4 volcados semanales más recientes y el previo a cada despliegue, hasta que se cierre la fase siguiente? (sí, o la regla que prefieras)
- **Respuesta:**

## Lo que no se pudo verificar

- Que el volcado real traiga la línea `-- Dump completed`. El código no usa `--skip-comments`, así que debería traerla, pero solo el informe lo confirma.
