-- =====================================================================
-- Linea base de produccion - Iteracion 00-01
-- SOLO LECTURA: unicamente SELECT y SHOW. Resultados agregados (conteos,
-- tamanos, fechas minimas y maximas); ninguna consulta devuelve filas de
-- clientes, pedidos ni pagos.
--
-- Como usarlo: pegar el archivo completo en la consola MySQL de
-- PythonAnywhere (pestana Databases, consola de tu base de datos).
-- Devuelve 14 resultados; el primer campo de cada uno (`seccion`) dice
-- cual es. Pasos exactos y formato de respuesta: ver evidencia-00-01.md.
--
-- Los comentarios no llevan tildes a proposito: el archivo se pega en una
-- consola cuya codificacion no controlamos.
--
-- Nombres de tablas y columnas tomados de pedidos/models.py (sin db_table
-- personalizado, asi que las tablas se llaman pedidos_<modelo>).
-- Fechas: Django guarda en UTC; 'America/Santiago' es la zona de la app.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 0. Instante de la medicion
-- ---------------------------------------------------------------------
SELECT '0' AS seccion,
       UTC_TIMESTAMP() AS medido_utc,
       NOW() AS medido_hora_servidor_mysql;

-- ---------------------------------------------------------------------
-- 1. HistorialBD (AUD-01-006)
-- 1a. Resumen. dias_distintos_santiago devuelve 0 si las tablas de zona
--     horaria no estan cargadas (ver seccion 5).
-- ---------------------------------------------------------------------
SELECT '1a' AS seccion,
       COUNT(*) AS filas_total,
       MIN(fecha_registro) AS primera_fila_utc,
       MAX(fecha_registro) AS ultima_fila_utc,
       COUNT(DISTINCT DATE(fecha_registro)) AS dias_distintos_utc,
       COUNT(DISTINCT DATE(CONVERT_TZ(fecha_registro, 'UTC', 'America/Santiago'))) AS dias_distintos_santiago,
       COALESCE(SUM(fecha_registro >= UTC_TIMESTAMP() - INTERVAL 7 DAY), 0) AS filas_ultimos_7_dias
FROM pedidos_historialbd;

-- 1b. Filas por dia. Si `maximo_filas_en_un_dia` es mayor que 1, hay varios
--     registros el mismo dia y el defecto de AUD-01-006 esta confirmado.
--     La fila 'santiago' replica el calculo de dia que hace Django en
--     fecha_registro__date; con zona horaria sin cargar agrupa todo en un
--     solo grupo NULL.
SELECT '1b' AS seccion,
       'utc' AS dia_calculado_en,
       COUNT(*) AS dias_con_registro,
       COALESCE(MAX(n), 0) AS maximo_filas_en_un_dia,
       COALESCE(SUM(n > 1), 0) AS dias_con_mas_de_una_fila,
       COALESCE(SUM(n - 1), 0) AS filas_sobrantes
FROM (SELECT DATE(fecha_registro) AS dia, COUNT(*) AS n
      FROM pedidos_historialbd
      GROUP BY dia) AS por_dia
UNION ALL
SELECT '1b',
       'santiago',
       COUNT(*),
       COALESCE(MAX(n), 0),
       COALESCE(SUM(n > 1), 0),
       COALESCE(SUM(n - 1), 0)
FROM (SELECT DATE(CONVERT_TZ(fecha_registro, 'UTC', 'America/Santiago')) AS dia, COUNT(*) AS n
      FROM pedidos_historialbd
      GROUP BY dia) AS por_dia;

-- ---------------------------------------------------------------------
-- 2. Peso de la base (datos mas indices), misma consulta que usa la app
--    en obtener_peso_real_bd().
-- 2a. Total
-- ---------------------------------------------------------------------
SELECT '2a' AS seccion,
       COUNT(*) AS tablas,
       ROUND(SUM(data_length) / 1048576, 2) AS datos_mb,
       ROUND(SUM(index_length) / 1048576, 2) AS indices_mb,
       ROUND(SUM(data_length + index_length) / 1048576, 2) AS peso_total_mb
FROM information_schema.TABLES
WHERE table_schema = DATABASE();

-- 2b. Por tabla, de la mas pesada a la mas liviana. filas_estimadas es una
--     estimacion de InnoDB; los conteos exactos estan en la seccion 3.
SELECT '2b' AS seccion,
       table_name AS tabla,
       table_rows AS filas_estimadas,
       ROUND(data_length / 1048576, 3) AS datos_mb,
       ROUND(index_length / 1048576, 3) AS indices_mb,
       ROUND((data_length + index_length) / 1048576, 3) AS total_mb
FROM information_schema.TABLES
WHERE table_schema = DATABASE()
ORDER BY (data_length + index_length) DESC;

-- 2c. MySQL 8 guarda en cache las estadisticas de information_schema; si el
--     valor es 86400, las cifras de 2a y 2b pueden tener hasta 24 horas.
SHOW VARIABLES LIKE 'information_schema_stats_expiry';

-- ---------------------------------------------------------------------
-- 3. Filas por tabla de negocio (conteo exacto)
-- ---------------------------------------------------------------------
SELECT '3' AS seccion, 'clientes' AS tabla, COUNT(*) AS filas FROM pedidos_cliente
UNION ALL
SELECT '3', 'pedidos', COUNT(*) FROM pedidos_pedido
UNION ALL
SELECT '3', 'items de pedido', COUNT(*) FROM pedidos_itempedido
UNION ALL
SELECT '3', 'cotizaciones', COUNT(*) FROM pedidos_cotizacion
UNION ALL
SELECT '3', 'items de cotizacion', COUNT(*) FROM pedidos_itemcotizacion
UNION ALL
SELECT '3', 'productos', COUNT(*) FROM pedidos_producto
UNION ALL
SELECT '3', 'pagos', COUNT(*) FROM pedidos_pago;

-- ---------------------------------------------------------------------
-- 4. Version y parametros de MySQL (paridad con la replica local, 00-03).
--    sql_mode se agrega como contexto para esa misma paridad.
-- ---------------------------------------------------------------------
SELECT '4' AS seccion,
       VERSION() AS version_mysql,
       @@character_set_database AS charset_base,
       @@collation_database AS collation_base,
       @@time_zone AS time_zone,
       @@system_time_zone AS system_time_zone,
       @@sql_mode AS sql_mode;

-- ---------------------------------------------------------------------
-- 5. Tablas de zona horaria de MySQL cargadas (AUD-01-006, AUD-02-007).
--    Resultado esperado si estan cargadas: 2026-01-15 09:00:00
--    (en enero Chile esta en UTC-3). NULL significa que no estan cargadas.
-- ---------------------------------------------------------------------
SELECT '5' AS seccion,
       CONVERT_TZ('2026-01-15 12:00:00', 'UTC', 'America/Santiago') AS instante_convertido,
       CASE WHEN CONVERT_TZ('2026-01-15 12:00:00', 'UTC', 'America/Santiago') IS NULL
            THEN 'NO' ELSE 'SI' END AS tablas_zona_horaria_cargadas;

-- ---------------------------------------------------------------------
-- 6. Grafico anual de estadisticas_pedidos (AUD-02-007)
--    El filtro fecha_solicitud__year de Django genera un rango BETWEEN
--    (sin conversion de zona horaria): el ano en Chile empieza el 1 de
--    enero a las 03:00 UTC. TruncMonth, en cambio, si convierte la zona
--    horaria en la base. Las consultas replican ambas cosas.
-- 6a. Pedidos del ano en curso por mes, con la conversion que hace TruncMonth.
--     Una fila con mes NULL significa que la conversion devuelve NULL.
-- ---------------------------------------------------------------------
SELECT '6a' AS seccion,
       DATE_FORMAT(CONVERT_TZ(fecha_solicitud, 'UTC', 'America/Santiago'), '%Y-%m') AS mes_con_conversion_santiago,
       COUNT(*) AS pedidos
FROM pedidos_pedido
WHERE fecha_solicitud >= CONCAT(YEAR(UTC_TIMESTAMP()), '-01-01 03:00:00')
  AND fecha_solicitud <  CONCAT(YEAR(UTC_TIMESTAMP()) + 1, '-01-01 03:00:00')
GROUP BY mes_con_conversion_santiago
ORDER BY mes_con_conversion_santiago;

-- 6b. Los mismos pedidos por mes sin conversion (mes en UTC), para comparar.
SELECT '6b' AS seccion,
       DATE_FORMAT(fecha_solicitud, '%Y-%m') AS mes_utc,
       COUNT(*) AS pedidos
FROM pedidos_pedido
WHERE fecha_solicitud >= CONCAT(YEAR(UTC_TIMESTAMP()), '-01-01 03:00:00')
  AND fecha_solicitud <  CONCAT(YEAR(UTC_TIMESTAMP()) + 1, '-01-01 03:00:00')
GROUP BY mes_utc
ORDER BY mes_utc;

-- 6c. Veredicto: el grafico tiene datos si hay pedidos este ano y ninguno
--     queda con conversion nula.
SELECT '6c' AS seccion,
       COUNT(*) AS pedidos_del_anio,
       COALESCE(SUM(CONVERT_TZ(fecha_solicitud, 'UTC', 'America/Santiago') IS NULL), 0) AS con_conversion_nula,
       CASE WHEN COUNT(*) = 0
            THEN 'NO: sin pedidos en el anio'
            WHEN SUM(CONVERT_TZ(fecha_solicitud, 'UTC', 'America/Santiago') IS NULL) > 0
            THEN 'NO: la conversion de zona horaria devuelve NULL'
            ELSE 'SI' END AS grafico_anual_con_datos
FROM pedidos_pedido
WHERE fecha_solicitud >= CONCAT(YEAR(UTC_TIMESTAMP()), '-01-01 03:00:00')
  AND fecha_solicitud <  CONCAT(YEAR(UTC_TIMESTAMP()) + 1, '-01-01 03:00:00');

-- ---------------------------------------------------------------------
-- 7. estado_pago frente a lo que dicen los pagos (AUD-02-004)
--    Regla de actualizar_estado_pago_pedido(): PAGADO si el saldo
--    (valor_venta - suma de pagos) es menor o igual a cero; PARCIAL si hay
--    pagos y queda saldo; PENDIENTE si no hay pagos. Un pedido con valor $0
--    y sin pagos cuenta como PAGADO por esa regla (regla de negocio
--    PENDIENTE_CLIENTE); por eso se informan aparte.
--    No se suman montos en pesos: solo conteos.
-- 7a. Resumen
-- ---------------------------------------------------------------------
SELECT '7a' AS seccion,
       COUNT(*) AS pedidos_total,
       COALESCE(SUM(registrado <> esperado), 0) AS estado_pago_inconsistente,
       COALESCE(SUM(valor_venta = 0), 0) AS pedidos_con_valor_cero,
       COALESCE(SUM(registrado <> esperado AND valor_venta = 0), 0) AS inconsistentes_con_valor_cero
FROM (SELECT p.id,
             p.valor_venta,
             p.estado_pago AS registrado,
             CASE WHEN CAST(p.valor_venta AS SIGNED) - COALESCE(SUM(g.monto), 0) <= 0 THEN 'PAGADO'
                  WHEN COALESCE(SUM(g.monto), 0) > 0 THEN 'PARCIAL'
                  ELSE 'PENDIENTE' END AS esperado
      FROM pedidos_pedido AS p
      LEFT JOIN pedidos_pago AS g ON g.pedido_id = p.id
      GROUP BY p.id, p.valor_venta, p.estado_pago) AS calculo;

-- 7b. Matriz: estado registrado frente a estado esperado (incluye los
--     consistentes, que son los de la diagonal).
SELECT '7b' AS seccion,
       registrado,
       esperado,
       COUNT(*) AS pedidos
FROM (SELECT p.id,
             p.estado_pago AS registrado,
             CASE WHEN CAST(p.valor_venta AS SIGNED) - COALESCE(SUM(g.monto), 0) <= 0 THEN 'PAGADO'
                  WHEN COALESCE(SUM(g.monto), 0) > 0 THEN 'PARCIAL'
                  ELSE 'PENDIENTE' END AS esperado
      FROM pedidos_pedido AS p
      LEFT JOIN pedidos_pago AS g ON g.pedido_id = p.id
      GROUP BY p.id, p.valor_venta, p.estado_pago) AS calculo
GROUP BY registrado, esperado
ORDER BY registrado, esperado;
