# Bitácora · Cierre de la redacción de la Épica 04

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** la Épica 04 queda **Pendiente (redactada completa, sin ejecutar)**, en limpio. Solo documentos; sin código, pruebas, `manage.py` ni consultas a la base.

## Decisiones registradas (del desarrollador, 2026-11-17, dichas por él)

| # | Decisión | Dónde queda |
| :- | :------- | :---------- |
| 1 | **W005 y W021** (HSTS sin `includeSubDomains` ni `preload`): se aceptan y quedan documentadas como esperadas; **no se silencian**. | Nota en la 04-02; criterio de término de la 04-02, de la definición y de la revisión final: «`check --deploy` sin advertencias, salvo W005 y W021, documentadas» |
| 2 | **La 04-10 se despliega justo después de la 04-01**, no al final. | Orden: 04-01 → 04-10 → 04-02 (dos escalones) → 04-03 → … → 04-09. Revisión final (tabla con etiquetas propuestas renumeradas), registro, definición y las diez iteraciones |
| 3 | **Consulta adicional de la 04-10 aceptada.** | Excepción a la sección 11 de `AGENTS.md`, fechada 2026-11-17, solo para esa pantalla y solo +1 consulta; consta en la 04-10, la definición, el registro y la revisión final |
| 4 | **La ejecución de la 04-01 en local no empieza ahora:** espera el cierre de la vigilancia de la 03-05. | Próximo hito: (a) 2026-11-20 informe C2 de desconexiones; (b) desde el 2026-11-23 a las 23:48, lectura del día 7, cierre de la 03-05 y limpieza de la réplica (parte F); (c) después, decidir el inicio de la 04-01 |
| 5 | **Sin cambios por defecto:** las notas «documentado» en `docs/operacion/` y la RDA-020 se escriben al ejecutar la 04-07; etiquetas, fechas y revisiones de datos en la réplica (tras la parte F) siguen `PENDIENTE_DESARROLLADOR`. | Registro (sección 3), definición, auditoría y revisión final |

**Por qué se aceptan W005 y W021** (nota completa en la 04-02): el dominio es de PythonAnywhere. `preload` exige el dominio registrable (`pythonanywhere.com`), que pertenece a la plataforma; `includeSubDomains` protegería subdominios de `manzagrafica.pythonanywhere.com`, que no existen (inferido), y activarlo sin necesidad agrega un riesgo. Verificado en Django: las dos advertencias salen cuando `SECURE_HSTS_SECONDS` es mayor que cero y esas opciones no son `True` (`django/core/checks/security/base.py:177-195`).

## Reorden de la 04-10: dependencias y archivos compartidos

**Nada se pisa** (detalle en la sección 2 de la revisión final): la 04-10 solo depende de la 04-01; `views.py` (funciones distintas) y plantillas (la de pagos copia antes el patrón que la 04-10 cambia después) no se cruzan; la comparación de `ELIMINAR` y `RESTAURAR` ya está fijada en las dos y la 04-04 reutiliza la función si existe. **Sin cambios de diseño en ninguna iteración.**

## Coherencia verificada (búsquedas en los documentos, 2026-11-17)

| Punto | Resultado |
| :---- | :-------- |
| Orden de despliegue | Igual en la definición, el registro, la revisión final y los encabezados de las diez iteraciones; las menciones antiguas («04-10 al final», «después de la 04-09») quedaron solo en notas fechadas de la redacción |
| Estado | Definición: «Pendiente (redactada completa, sin ejecutar)»; las diez iteraciones: «Pendiente (redactada, decisiones resueltas)» |
| Migraciones | Solo dos: `0008` (04-06) y `0009` (04-08, depende de la `0008`); la 04-10 **no** crea ninguna (la `0010` quedó descartada) |
| Variables de entorno | Cinco nuevas: `SEGURIDAD_PRODUCCION`, `CSRF_TRUSTED_ORIGINS`, `ACCESO_PROXIES_CONFIABLES`, `ACCESO_FALLOS_POR_DIRECCION`, `CSP_OBSERVACION`; en `.env` antes que el código |
| Fallos esperados | **9** hoy → **4** tras la 04-01 (R8, R9, R14, R15) → **3** tras la 04-06 (R8, R9, R15); la 04-10 y las demás no cambian el conteo. Verificado en `test_regresiones.py` (nueve `@expectedFailure`) |
| Criterio de término | Coincide en la definición, la 04-02 y la revisión final |

### Errores de redacción corregidos en esta pasada

- Todas las iteraciones decían «se desarrolla en local en paralelo a la vigilancia»; pasó a «se redactó en paralelo; su ejecución en local no empieza hasta cerrar la vigilancia».
- La definición y el registro tenían un orden de despliegue y un hito antiguos; actualizados.
- Las notas «documentado» figuraban para la revisión final; ahora, al ejecutar la 04-07.

### Decisiones encontradas (no se tomaron aquí)

- **Etiquetas propuestas:** los nombres de la revisión final (`v4.2-…` a `v4.11-…`) son una propuesta del agente según el patrón de las anteriores; confirmarlos es `PENDIENTE_DESARROLLADOR`.
- **Dos despliegues de la 04-02:** el escalón 2 (HSTS 604800) también necesita etiqueta.

## Lo que queda abierto

- **`PENDIENTE_CLIENTE`:** si el borrado de pagos con el pedido es intencional (la 04-10 no espera la respuesta) y si al duplicar un pedido se copian ítems y pagos.
- **`PENDIENTE_DESARROLLADOR`:** etiquetas y fechas; cuándo empieza la 04-01 (tras cerrar la 03-05); revisiones de datos en la réplica tras la parte F; mediciones de producción de la 04-08 (dirección real, usuarios); página 405 propia (04-01); propuesta de restaurar fuera de la petición (06-03 o Épica 14).
- **Se escriben al ejecutar la 04-07:** la RDA-020 y las notas operativas «documentado».
- **No verificado en producción:** todo lo que dependa de PythonAnywhere (etiquetas, dirección real, instalación de `nh3`, límites del proxy, cabecera de CSP).

## Archivos

Las diez iteraciones (`iteracion-04-01` a `04-10`), `definicion-epica-04.md`, `bitacora-04-revision-final.md`, `00_producto/registro-pendientes.md` y `00_producto/auditoria-tecnica.md` (ambos por bytes, CRLF intacto) y esta bitácora.
