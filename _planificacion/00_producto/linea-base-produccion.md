# Línea base de producción

Cifras reales de producción contra las que se compara toda corrección u optimización posterior. Cada cifra lleva su fecha de medición y nunca datos personales (solo conteos, tamaños, fechas y estados).

- **Estado:** plantilla sin medir. Se llena al consolidar `10_epicas/epica-00-blindaje/evidencia-00-01.md` (iteración 00-01, tarea 6).
- **Marcador:** `PENDIENTE_DESARROLLADOR` significa que el valor depende de la respuesta del desarrollador en el archivo de evidencia.
- **Fechas:** formato `AAAA-MM-DD`, hora de Chile continental.
- **Fuentes:** «Guion SQL» = `scripts/diagnostico/linea_base.sql` (sección entre paréntesis); «Guion Bash» = `scripts/diagnostico/linea_base.sh` (sección entre paréntesis); «Clave» y «Registros» = fragmentos del archivo de evidencia; «Panel» = lectura manual en PythonAnywhere.

## 1. Registro diario de métricas (`pedidos_historialbd`) · AUD-01-006

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Filas totales | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (1a) |
| Fecha de la primera y de la última fila (UTC) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (1a) |
| Días distintos con registro (día en UTC) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (1a, 1b) |
| Días distintos con registro (día en hora de Chile) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (1a, 1b) |
| Máximo de filas registradas en un mismo día | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (1b) |
| Filas sobrantes (filas menos días) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (1b) |
| Filas registradas en los últimos 7 días | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (1a) |
| ¿Defecto confirmado? (varias filas en un mismo día: sí o no) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (1b) |

## 2. Peso de la base y disco de la cuenta

Límite del plan: 512 MiB compartidos entre archivos y MySQL.

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Peso de la base, datos más índices (MB) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (2a) |
| Datos (MB) / índices (MB) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (2a) |
| Vigencia de las estadísticas de `information_schema` (segundos) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (2c) |
| Uso de disco de los archivos de la cuenta (MB) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion Bash (B) |
| Uso de disco que informa el panel (valor y límite) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Panel (Dashboard) |
| Uso de disco frente a los 512 MiB (porcentaje) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Cálculo con las dos filas anteriores y la de peso de la base |

### Peso por tabla (de la más pesada a la más liviana)

| Tabla | Filas estimadas | Datos (MB) | Índices (MB) | Total (MB) | Fecha de medición | Fuente |
| :---- | :-------------- | :--------- | :----------- | :--------- | :---------------- | :----- |
| PENDIENTE_DESARROLLADOR | | | | | | Guion SQL (2b) |

## 3. Respaldos y archivos

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Número de volcados en `backups/` | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion Bash (C) |
| Tamaño total de los volcados (MB) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion Bash (C) |
| Antigüedad del volcado más antiguo y del más reciente (días) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion Bash (C) |
| Tamaño de `backups/` completo, con subcarpetas (MB) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion Bash (C) |
| Tamaño de `media/` (MB) y número de archivos | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion Bash (D) |

## 4. Volumen por tabla de negocio

| Tabla | Filas | Fecha de medición | Fuente |
| :---- | :---- | :---------------- | :----- |
| Clientes (`pedidos_cliente`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (3) |
| Pedidos (`pedidos_pedido`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (3) |
| Ítems de pedido (`pedidos_itempedido`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (3) |
| Cotizaciones (`pedidos_cotizacion`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (3) |
| Ítems de cotización (`pedidos_itemcotizacion`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (3) |
| Productos (`pedidos_producto`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (3) |
| Pagos (`pedidos_pago`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (3) |

## 5. MySQL y zona horaria · paridad con la réplica local (00-03) · AUD-02-007

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Versión de MySQL | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (4) |
| Conjunto de caracteres de la base (`@@character_set_database`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (4) |
| Colación de la base (`@@collation_database`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (4) |
| Zona horaria (`@@time_zone`) y del sistema (`@@system_time_zone`) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (4) |
| Modo SQL (`@@sql_mode`), contexto adicional para la paridad | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (4) |
| ¿Tablas de zona horaria cargadas? (sí o no) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (5) |
| ¿El gráfico anual de estadísticas tiene datos? (sí o no) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (6c) |
| Pedidos del año en curso y los que quedan con conversión nula | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (6a, 6b, 6c) |

## 6. Consistencia de `estado_pago` · AUD-02-004

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Pedidos totales | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (7a) |
| Pedidos con `estado_pago` inconsistente | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (7a) |
| Pedidos con valor de venta $0 y, entre ellos, los inconsistentes | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (7a) |
| Matriz estado registrado frente a estado esperado | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion SQL (7b) |

## 7. Entorno de la web app

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Versión de Python de producción | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion Bash (E) |
| Diferencias entre `pip freeze` y `requirements.txt` | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Guion Bash (F) |
| ¿Tarea programada disponible? (sí o no) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Panel (Tasks) |
| Fecha de expiración de la web app | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Panel (Web) |
| Procedimiento de renovación de la web app | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Panel (Web) |

## 8. Registro del servidor · insumo para medir 00-06

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| Desconexiones en los últimos 7 días | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Registros (`contar_logs`, registro del servidor) |
| Peticiones a `/robots.txt` en los últimos 7 días | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Registros (`contar_logs`, registro de accesos) |
| Patrón de texto usado para contar desconexiones | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Registros (`contar_logs`, mensajes más repetidos) |

## 9. Clave secreta · AUD-02-010

Nunca se registra la clave, solo estas dos respuestas.

| Métrica | Valor | Fecha de medición | Fuente |
| :------ | :---- | :---------------- | :----- |
| ¿La clave de producción empieza con `django-insecure-`? (sí o no) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Clave (paso 3 de la evidencia) |
| ¿Coincide con la clave del commit `713260c`? (sí o no) | PENDIENTE_DESARROLLADOR | PENDIENTE_DESARROLLADOR | Clave (paso 3 de la evidencia) |
