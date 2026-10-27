# Épica 14 · Tecnología en la nube (AWS)

- **Estado:** Pendiente
- **Fase del plan:** no existe en el plan original; anexo del plan del 2026-10-27 (RDA-014). Es la última épica por decisión del desarrollador.
- **Objetivo:** sacar los respaldos del disco de PythonAnywhere y guardarlos en Amazon S3, en una cuenta de AWS del negocio, protegida y con costo vigilado. El servidor deja de ser el único lugar donde viven las copias automáticas.
- **Precondición:** 06-02 y 06-03 desplegadas (la orden diaria genera los respaldos de los días 1 y 15, y la rotación local ya es por antigüedad). La Épica 13 sigue corriendo en paralelo: sus rutinas incorporan las de esta épica.
- **Última revisión:** 2026-10-27 (creada a pedido del desarrollador).

## Por qué S3 y no otro servicio (contexto para quien llega)

- **El riesgo que se cubre:** hoy los respaldos automáticos quedan en `backups/` del servidor, en el mismo disco de 512 MiB que la base. Si el disco falla o se llena, se pierden la base y sus copias a la vez (AUD-01-014, AUD-02-019, AUD-02-024). La rotación que borra respaldos es código propio (`limpiar_backups_antiguos`), no una política de PythonAnywhere: la corrige la 06-03.
- **S3 es almacenamiento de archivos:** un `.sql` comprimido es exactamente eso. Un servicio de bases de datos (RDS, DynamoDB) sería un servidor que administrar y pagar, no un lugar donde guardar copias.
- **Viabilidad verificada el 2026-10-27:** `.amazonaws.com` está en la lista blanca de salida de PythonAnywhere, así que el plan gratuito puede subir archivos a S3.
- **Costo:** desde julio de 2025, las cuentas nuevas de AWS entran a un plan gratuito con hasta USD 200 en créditos que dura seis meses o hasta agotar los créditos; después hay que pasar al plan pagado. Con unos 24 respaldos al año de pocos MB, el almacenamiento en S3 cuesta del orden de centavos de dólar al mes, pero exige una tarjeta registrada: por eso la épica parte por la seguridad y la alerta de presupuesto.

## Alcance

1. **Cuenta y seguridad (14-01):**
   - cuenta de AWS a nombre del negocio, porque los datos son de Manza Gráfica;
   - autenticación de dos factores en la cuenta raíz, sin usarla para el trabajo diario;
   - un usuario IAM para la aplicación con **mínimo privilegio**: solo subir objetos a un prefijo de un bucket, sin permiso para borrar ni listar todo, de modo que una clave filtrada no pueda destruir los respaldos;
   - alerta de presupuesto (AWS Budgets) con un umbral bajo;
   - región a decidir;
   - credenciales solo en `.env` y en `.env.example` sin valores.

   Se documenta en `docs/operacion/`.
2. **Respaldo de la base en S3 (14-02):** la orden diaria, los días 1 y 15, comprime el volcado (`gzip` de la biblioteca estándar), lo sube a un bucket privado con cifrado del lado del servidor, bloqueo de acceso público y versionado, y registra el resultado como evento. Una regla de ciclo de vida del bucket fija la retención en la nube. Un fallo de subida no impide que el respaldo quede en el servidor (RDA-009).
3. **Restauración ensayada desde S3 (14-03):** descargar un respaldo de S3, verificarlo con `scripts/verificar_respaldo.py` y restaurarlo en la réplica local. Se suma al ensayo semestral de la 13-04.

## Iteraciones

| Iteración | Nombre |
| :-------- | :----- |
| 14-01 | Cuenta de AWS y seguridad |
| 14-02 | Respaldo de la base en S3 |
| 14-03 | Restauración ensayada desde S3 |

## Ideas propuestas (el desarrollador decide; serían 14-04 en adelante)

- **Respaldo de `media/` en S3** (AUD-02-023): las imágenes de referencia hoy no tienen copia automática.
- **Correo con Amazon SES** como alternativa al canal de la 11-01, si este resultara poco confiable.

## Decisiones de la épica

- Biblioteca para hablar con S3: `boto3` (oficial, pero ocupa decenas de MB en un disco de 512 MiB) u otra más liviana: `PENDIENTE_DESARROLLADOR`, se decide en 14-02 midiendo el espacio y con RDA (dependencia nueva). La RDA de la épica también registra el primer servicio externo de la aplicación, que RDA-004 no contemplaba.
- Región de AWS y retención en el bucket: `PENDIENTE_DESARROLLADOR`, se deciden en 14-01 y 14-02.
- Quién abre la cuenta y registra el medio de pago (Ignacio, con apoyo del desarrollador): `PENDIENTE_CLIENTE`.
- **2026-10-27 · Sin aprendizaje automático en la nube (RDA-018).**

## Fuera de alcance

- Cambiar de hosting o mover la base de datos a AWS.
- Servicios de aprendizaje automático (SageMaker y similares).
- Subir a S3 los respaldos generados a mano desde la web: siguen el protocolo de descarga local de 00-02.

## Criterio de término

- Un respaldo del día 1 o del 15 aparece en S3 sin intervención manual y queda su evento.
- La clave de la aplicación no puede borrar objetos del bucket (comprobado con un intento que falla).
- Un respaldo descargado de S3 se restaura en la réplica y pasa la verificación.
- La alerta de presupuesto está activa.

## Notas

- **2026-10-27:** creada a pedido del desarrollador, que pidió sacar de la Épica 06 todo lo de S3 y reunir lo de AWS al final del plan.
