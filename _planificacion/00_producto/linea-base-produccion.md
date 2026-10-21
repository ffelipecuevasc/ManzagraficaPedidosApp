# Línea base de producción

Cifras reales de producción contra las que se compara toda corrección u optimización posterior. Cada cifra lleva su fecha de medición y nunca datos personales (solo conteos, tamaños, fechas y estados).

- **Estado:** medida el 2026-10-20 (iteración 00-01, tarea 6). Detalle y salvedades en `99_bitacora/epica-00-blindaje/bitacora-00-01-produccion.md`.
- **Marcador:** `PENDIENTE_DESARROLLADOR` significa que el dato no vino en la evidencia y no se inventó.
- **Fechas:** formato `AAAA-MM-DD`. La medición se hizo el 2026-10-20 en UTC, que también es 2026-10-20 en hora de Chile continental. Las horas y los días que dicen «UTC» se dejan en UTC.
- **Fuentes:** «Guion SQL» = `scripts/diagnostico/linea_base.sql` (sección entre paréntesis); «Guion Bash» = `scripts/diagnostico/linea_base.sh` (sección entre paréntesis); «Clave» y «Registros» = fragmentos del archivo de evidencia; «Panel» = lectura manual en PythonAnywhere. Todas las salidas las pegó el desarrollador desde las consolas y el panel de PythonAnywhere.

## 1. Registro diario de métricas (`pedidos_historialbd`) · AUD-01-006

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Filas totales | 187 | 2026-10-20 | Guion SQL (1a) |
| Fecha de la primera y de la última fila (UTC) | 2026-02-07 03:41 · 2026-10-20 16:09 | 2026-10-20 | Guion SQL (1a) |
| Días distintos con registro (día en UTC) | 121 | 2026-10-20 | Guion SQL (1a, 1b) |
| Días distintos con registro (día en hora de Chile) | 119 | 2026-10-20 | Guion SQL (1a, 1b) |
| Máximo de filas registradas en un mismo día | 16 (día en UTC) · 17 (día en hora de Chile) | 2026-10-20 | Guion SQL (1b) |
| Días con más de una fila | 23 (UTC) · 24 (hora de Chile) | 2026-10-20 | Guion SQL (1b) |
| Filas sobrantes (filas menos días) | 66 (UTC) · 68 (hora de Chile) | 2026-10-20 | Guion SQL (1b) |
| Filas registradas en los últimos 7 días | 2 | 2026-10-20 | Guion SQL (1a) |
| Cobertura (días con registro sobre días transcurridos desde la primera fila) | 121 de 256 días (47 %) | 2026-10-20 | Cálculo con las filas anteriores |
| ¿Defecto confirmado? (varias filas en un mismo día: sí o no) | Sí | 2026-10-20 | Guion SQL (1b) |

La cobertura es baja porque la métrica solo se registra cuando alguien abre la pantalla de estadísticas y no hay tarea programada (sección 7).

## 2. Peso de la base y disco de la cuenta

Límite del plan: 512 MiB compartidos entre archivos y MySQL.

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Tablas de la base | 18 | 2026-10-20 | Guion SQL (2a) |
| Peso de la base, datos más índices (MB) | 2,20 (referencial, ver nota) | 2026-10-20 | Guion SQL (2a) |
| Datos (MB) / índices (MB) | 1,86 / 0,34 | 2026-10-20 | Guion SQL (2a) |
| Vigencia de las estadísticas de `information_schema` (segundos) | 86400 (hasta 24 h de antigüedad) | 2026-10-20 | Guion SQL (2c) |
| Tamaño del volcado más reciente (bytes) | 1.438.471 | 2026-10-20 | Guion Bash (C) |
| Uso de disco de los archivos de la cuenta (MB) | 181 (proyecto 150; `.cache` 31; `.virtualenvs`, `.local` e `.ipython` 1 cada una) | 2026-10-20 | Guion Bash (B) |
| Uso de disco que informa el panel (valor y límite) | 180,8 MB de 512 MB | 2026-10-20 | Panel (Dashboard) |
| Uso de disco frente a los 512 MiB (porcentaje) | 35 % | 2026-10-20 | Panel (Dashboard) |

**Nota sobre el peso de la base:** las estadísticas de `information_schema` pueden tener hasta 24 horas y las filas estimadas quedan muy por debajo de las reales (pedidos: 191 estimadas contra 870 exactas). El peso sirve solo como referencia; el tamaño del volcado es la cifra más confiable del volumen de datos.

### Peso por tabla (de la más pesada a la más liviana)

| Tabla | Filas estimadas | Datos (MB) | Índices (MB) | Total (MB) | Fecha de medición | Fuente |
| :---- | :-------------- | :--------- | :----------- | :--------- | :---------------- | :----- |
| `pedidos_pedido` | 191 (exactas: 870) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | 1,547 | 2026-10-20 | Guion SQL (2b) |
| `pedidos_pago` | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | 0,094 | 2026-10-20 | Guion SQL (2b) |
| `django_session` | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | 0,063 | 2026-10-20 | Guion SQL (2b) |
| Las 15 tablas restantes | — | — | — | — | — | No se informaron por separado |

## 3. Respaldos y archivos

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Número de volcados en `backups/` | 5 (la salida original decía 6 porque contaba `.gitkeep`; el guion ya lo excluye) | 2026-10-20 | Guion Bash (C), corregido |
| Tamaño total de los volcados (MB) | 6,19 (1,22; 1,24; 1,27; 1,32; 1,44) | 2026-10-20 | Guion Bash (C) |
| Fechas de los volcados | 2026-03-26, 2026-04-13, 2026-05-05, 2026-06-23, 2026-10-20 (este último, generado a mano por el desarrollador ese día) | 2026-10-20 | Guion Bash (C) |
| Antigüedad del volcado más antiguo y del más reciente (días) | 208 · 0 | 2026-10-20 | Guion Bash (C), corregido |
| Tamaño de `backups/` completo, con subcarpetas (MB) | PENDIENTE_DESARROLLADOR | — | Guion Bash (C) |
| Tamaño de `media/` (MB) y número de archivos | 3 MB · 11 archivos | 2026-10-20 | Guion Bash (D) |

## 4. Volumen por tabla de negocio

| Tabla | Filas | Fecha de medición | Fuente |
| :---- | :---- | :---------------- | :----- |
| Clientes (`pedidos_cliente`) | 722 | 2026-10-20 | Guion SQL (3) |
| Pedidos (`pedidos_pedido`) | 870 | 2026-10-20 | Guion SQL (3) |
| Ítems de pedido (`pedidos_itempedido`) | 850 | 2026-10-20 | Guion SQL (3) |
| Cotizaciones (`pedidos_cotizacion`) | 25 | 2026-10-20 | Guion SQL (3) |
| Ítems de cotización (`pedidos_itemcotizacion`) | 52 | 2026-10-20 | Guion SQL (3) |
| Productos (`pedidos_producto`) | 55 | 2026-10-20 | Guion SQL (3) |
| Pagos (`pedidos_pago`) | 1.033 | 2026-10-20 | Guion SQL (3) |

## 5. MySQL y zona horaria · paridad con la réplica local (00-03) · AUD-02-007

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Versión de MySQL | 8.0.46 | 2026-10-20 | Guion SQL (4) |
| Conjunto de caracteres de la base (`@@character_set_database`) | `utf8mb4` | 2026-10-20 | Guion SQL (4) |
| Colación de la base (`@@collation_database`) | `utf8mb4_unicode_ci` | 2026-10-20 | Guion SQL (4) |
| Zona horaria (`@@time_zone`) y del sistema (`@@system_time_zone`) | `UTC` · `UTC` | 2026-10-20 | Guion SQL (4) |
| Modo SQL (`@@sql_mode`), contexto adicional para la paridad | `NO_ENGINE_SUBSTITUTION` (sin modo estricto, AUD-02-020) | 2026-10-20 | Guion SQL (4) |
| ¿Tablas de zona horaria cargadas? (sí o no) | Sí | 2026-10-20 | Guion SQL (5) |
| ¿El gráfico anual de estadísticas tiene datos? (sí o no) | Sí | 2026-10-20 | Guion SQL (6c) |
| Pedidos del año en curso y los que quedan con conversión nula | 870 (todos los pedidos son de 2026) · 0 | 2026-10-20 | Guion SQL (6a, 6b, 6c) |

### Pedidos por mes de 2026 (mes en hora de Chile)

| Ene | Feb | Mar | Abr | May | Jun | Jul | Ago | Sep | Oct |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 109 | 121 | 91 | 82 | 85 | 87 | 65 | 77 | 89 | 64 |

Con el mes calculado en UTC solo cambian julio (64) y agosto (78). Fuente: Guion SQL (6b), medido el 2026-10-20.

## 6. Consistencia de `estado_pago` · AUD-02-004

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Pedidos totales | 870 | 2026-10-20 | Guion SQL (7a) |
| Pedidos con `estado_pago` inconsistente | 610 (70,1 %) | 2026-10-20 | Guion SQL (7a) |
| Pedidos con valor de venta $0 y, entre ellos, los inconsistentes | 0 · 0 | 2026-10-20 | Guion SQL (7a) |
| Matriz estado registrado frente a estado esperado | Ver tabla siguiente | 2026-10-20 | Guion SQL (7b) |

| Registrado → esperado | Pedidos |
| :-------------------- | :------ |
| `PAGADO` → `PAGADO` | 234 |
| `PARCIAL` → `PARCIAL` | 4 |
| `PENDIENTE` → `PAGADO` | 563 |
| `PENDIENTE` → `PARCIAL` | 47 |
| `PENDIENTE` → `PENDIENTE` | 22 |

## 7. Entorno de la web app

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Versión de Python de producción | 3.13.1 | 2026-10-20 | Guion Bash (E) |
| Diferencias entre `pip freeze` y `requirements.txt` | Ninguna: 21 paquetes en cada uno (`requirements.txt` en UTF-16) | 2026-10-20 | Guion Bash (F) |
| ¿Tarea programada disponible? (sí o no) | Sí, disponible; **no hay ninguna creada**. El formulario para crear una diaria está habilitado (hora por defecto 21:15 UTC) | 2026-10-20 | Panel (Tasks) |
| Fecha de expiración de la web app | 2026-11-20 (`PENDIENTE_DESARROLLADOR`: confirmar si viene de una renovación hecha el mismo día) | 2026-10-20 | Panel (Web) |
| Procedimiento de renovación de la web app | Iniciar sesión y pulsar «Run until 1 month from today», al menos una vez al mes. PythonAnywhere avisa por correo una semana antes | 2026-10-20 | Panel (Web) |
| Tráfico según el panel | Este mes 1.197 (anterior 1.835); hoy 96 (ayer 65) | 2026-10-20 | Panel (Web) |
| Configuración visible de la web app | Force HTTPS activado; sin protección con contraseña; campo «Source code» vacío; estáticos `/static/` → `staticfiles`, `/media/` → `media` | 2026-10-20 | Panel (Web) |
| Código desplegado | `HEAD` `2442f3b` (2026-03-12), rama `main`, sin archivos versionados modificados; sin versionar: `media/pedidos/` (8 imágenes), `media/referencias/` y `staticfiles/` | 2026-10-20 | Consola Bash (`git`) |

## 8. Registro del servidor · insumo para medir 00-06

Método: conteo **por fecha de cada línea**, no por archivo, porque los archivos rotan de forma irregular (ver `evidencia-00-01.md`, «Método reutilizable para 00-06»). Periodo: 2026-10-15 a 2026-10-21 en UTC; el 21 cubre solo unos minutos.

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Desconexiones en los últimos 7 días | `Broken pipe` 4 · `SIGPIPE` o cerrado 12 | 2026-10-20 | Registros (conteo por día, registro del servidor) |
| Desconexiones por día (`Broken pipe` / `SIGPIPE`) | 15: 2/4 · 16: 0/1 · 17: 1/2 · 18: 0/1 · 19: 0/2 · 20: 1/2 · 21: 0/0 | 2026-10-20 | Registros (conteo por día) |
| Tasa de `Broken pipe` en el periodo largo | 39 en 89 días (2026-07-23 a 2026-10-20), unas 0,44 por día; `write error` 0; `SIGPIPE` o cerrado 152 | 2026-10-20 | Registros (`contar_logs`, por archivo) |
| Peticiones a `/robots.txt` en los últimos 7 días | 7 (15: 2 · 16: 0 · 17: 0 · 18: 1 · 19: 2 · 20: 2 · 21: 0); las líneas de muestra responden 404 | 2026-10-20 | Registros (conteo por día, registro de accesos) |
| Tasa de `/robots.txt` en el periodo largo | Unas 1,1 por día (44 en todos los archivos de acceso disponibles) | 2026-10-20 | Registros (`contar_logs`, por archivo) |
| Patrón de texto usado para contar desconexiones | `Broken pipe` (aparece como `uwsgi_response_write_headers_do(): Broken pipe`) y `SIGPIPE: writing to a closed pipe/socket/fd`; `write error` no aparece | 2026-10-20 | Registros (`contar_logs`, mensajes más repetidos) |
| Errores capturados por el decorador (enero a octubre de 2026) | 33: `eliminar_pago` 14, `crear_pedido` 7, `eliminar_producto` 4, `crear_cotizacion` 3, `crear_cliente` 3, `eliminar_cotizacion` 2 | 2026-10-20 | Registros (registro del servidor) |

## 9. Clave secreta · AUD-02-010

Nunca se registra la clave, solo estas dos respuestas.

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| ¿La clave de producción empieza con `django-insecure-`? (sí o no) | No | 2026-10-20 | Clave (paso 3 de la evidencia) |
| ¿Coincide con la clave del commit `713260c`? (sí o no) | No | 2026-10-20 | Clave (paso 3 de la evidencia) |
