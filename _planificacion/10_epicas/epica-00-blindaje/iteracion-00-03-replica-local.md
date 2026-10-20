# Iteración 00-03 · Réplica local fiel

- **Épica:** 00 · Blindaje y punto de retorno
- **Estado:** Pendiente
- **Subfase del plan:** 0.3
- **Depende de:** 00-02
- **RDA relacionadas:** RDA-002, RDA-006
- **Hallazgos que cierra:** ninguno. Habilita todas las pruebas y ensayos posteriores.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no hay despliegue)

## Objetivo

Que el entorno local deje de ser una maqueta y pase a ser un espejo de producción: el MySQL local en Docker con la misma configuración que producción y con los datos del respaldo verificado en 00-02. Restaurarlo es, además, el primer ensayo real de recuperación ante desastres.

## Tareas

1. **Contenedor reproducible.** Proponer un `compose.yaml` en la raíz (requiere consulta) con la imagen de MySQL en la versión exacta medida en 00-01, el conjunto de caracteres, la colación y la zona horaria de producción, un volumen con nombre para los datos y las credenciales tomadas de variables de entorno. Si el desarrollador prefiere mantener su contenedor actual, documentar su comando exacto. En ambos casos, la decisión cierra el `PENDIENTE_DESARROLLADOR` de la sección 5 de `AGENTS.md` mediante una propuesta de cambio al desarrollador.
2. **Tablas de zona horaria.** Dejar el contenedor en el **mismo estado que producción** según 00-01: si producción no las tiene cargadas, el contenedor tampoco, para que el defecto de AUD-01-006 y AUD-02-007 se reproduzca en local. Documentar cómo cargarlas si algún día cambia.
3. **Procedimiento** `docs/operacion/replica-local.md`: levantar el contenedor, crear la base vacía, restaurar un volcado verificado, comprobar la paridad, arrancar la aplicación y refrescar la réplica cuando los datos queden viejos. Incluye la advertencia de que la réplica contiene datos personales reales.
4. **Lista de paridad** dentro del mismo procedimiento, en una tabla `Elemento · Producción (00-01) · Local · Coincide`: versión de MySQL, conjunto de caracteres, colación, `@@time_zone`, tablas de zona horaria, versión de Python y la diferencia entre `pip freeze` de producción y el entorno local.
5. **Archivo de evidencia** `evidencia-00-03.md`: el desarrollador restaura el volcado en el contenedor (el agente no lee volcados), mide el tiempo de la restauración y pega el resultado del guion de paridad.
6. Con la réplica restaurada, el agente ejecuta `python manage.py showmigrations pedidos`, `python manage.py check` y el guion SQL de 00-01 contra la base local, y compara los conteos con la línea base.

## Criterios de aceptación

- [ ] La tabla de paridad no tiene filas con «No» sin una decisión escrita al lado.
- [ ] `python manage.py showmigrations pedidos` muestra aplicadas de la `0001` a la `0006` y ninguna pendiente.
- [ ] `python manage.py check` termina sin errores contra la réplica.
- [ ] Los conteos por tabla de la réplica coinciden con los de `linea-base-produccion.md` para la fecha del volcado (diferencias explicadas por la actividad posterior al volcado).
- [ ] El desarrollador confirma que el panel de control, el listado de pedidos, el trabajo semanal y el panel financiero muestran información coherente con producción.
- [ ] El tiempo de restauración quedó medido en la bitácora.
- [ ] El procedimiento de refresco está escrito y se puede seguir sin conocimiento previo.

## Fuera de alcance

- Sacar las credenciales locales incrustadas en `settings.py` (va en 00-04).
- Configurar la base de datos de pruebas (va en 02-01).

## Datos requeridos del cliente

- Ninguno.
