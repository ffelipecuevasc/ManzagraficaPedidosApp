# Réplica local de producción

Cómo levantar el MySQL local, restaurar en él un respaldo verificado de producción, comprobar que se comporta igual que producción y refrescarlo cuando los datos queden viejos.

- **Creado en:** iteración 00-03 (2026-10-21).
- **Lo ejecuta:** el desarrollador. Los agentes no ejecutan `docker`, `mysql` ni `mysqldump`, y no leen volcados.
- **Comandos:** PowerShell 7 (`pwsh`) en Windows 10, desde la raíz del repositorio. Windows PowerShell 5 pasa mal las comillas a `docker`: no lo uses para estos comandos.

> **Advertencia: la réplica contiene datos personales reales.** Trae nombres, teléfonos y montos de clientes, las sesiones de `django_session` y **los hashes de contraseña de los usuarios de producción** (`auth_user`). Por eso:
>
> - **La unidad cifrada es obligatoria.** La réplica vive en el volumen de Docker, cuyo disco virtual (`ext4.vhdx`) está en D:, igual que el repositorio y la carpeta de respaldos. D: debe tener BitLocker con «Protección activada» y el 100 % cifrado, y el disco de Docker tiene que estar en D: (sección 2). Sin esas dos confirmaciones no se restauran datos reales.
> - No exportes, copies ni compartas la réplica, y no le saques capturas con datos de clientes.
> - No dejes el puerto de MySQL abierto a la red: el compose lo publica solo en `127.0.0.1`.

> **Nunca ejecutes `docker volume rm mysql_data` ni `docker compose down -v`.** Borran el volumen con todas las bases locales: `manzagrafica_local` (tus datos de desarrollo) y la réplica. Para detener el contenedor usa `docker compose stop` o `docker compose down` **sin** `-v`.

## 1. Qué hay en el contenedor

| Elemento | Valor |
| :------- | :---- |
| Archivo | `compose.yaml` en la raíz |
| Servicio · contenedor | `db` · `manzagrafica-mysql` |
| Imagen | `mysql:8.0.46`, la misma versión que producción |
| Volumen | `mysql_data`, externo: el compose lo usa pero no lo crea ni lo borra |
| Puerto | `127.0.0.1:3306`, o el de `DB_PORT` |
| Configuración | `utf8mb4`, `utf8mb4_unicode_ci`, `--default-time-zone=UTC`, `sql_mode = NO_ENGINE_SUBSTITUTION` |
| Bases | `manzagrafica_local` (desarrollo, **no se toca**) y `manzagrafica_replica` (copia de producción) |

**Variables de `.env`** (las mismas que va a documentar `.env.example` en 00-04):

| Variable | Uso |
| :------- | :-- |
| `DB_NAME` | Nombre de la base que usa la app. Hoy no se lee: `settings.py` fija `manzagrafica_local` hasta la 00-04. |
| `DB_USER` | Usuario de MySQL (`root` en local). Hoy no se lee, por la misma razón. |
| `DB_PASSWORD` | Contraseña de root. El compose la pasa como `MYSQL_ROOT_PASSWORD`. |
| `DB_HOST` | `127.0.0.1`. Hoy no se lee. |
| `DB_PORT` | Puerto publicado (por defecto `3306`). |

`MYSQL_ROOT_PASSWORD` solo se aplica cuando el volumen está vacío. Como se reutiliza `mysql_data`, `DB_PASSWORD` tiene que ser **la contraseña de root que ya tiene el volumen**. Si no coincide, el contenedor arranca igual, pero la conexión falla.

## 2. Comprobación previa: cifrado

Las dos comprobaciones deben pasar. Si alguna falla, detente y no restaures.

**a) D: cifrada.** En PowerShell como administrador:

```powershell
manage-bde -status D:
```

Debe decir **«Estado de protección: Protección activada»** («Protection Status: Protection On») y **«Porcentaje cifrado: 100,0 %»** («Percentage Encrypted: 100.0%»).

**b) El disco de Docker está en D:.** En Docker Desktop, abre *Settings → Resources → Advanced → Disk image location*: la ruta tiene que empezar con `D:\`. Para confirmar que el archivo existe ahí:

```powershell
Get-ChildItem "<ruta de Disk image location>" -Recurse -Filter *.vhdx | Select-Object FullName, Length
```

Debe aparecer `ext4.vhdx` (en versiones recientes de Docker Desktop puede llamarse `docker_data.vhdx`) con una ruta en D:.

## 3. Pasar del contenedor «mysql» al compose (una sola vez)

El contenedor anterior se llama `mysql`, usa `mysql:8.0` (8.0.43) y guarda los datos en el volumen `mysql_data`. Quitarlo **no** borra el volumen.

1. Opcional, pero recomendado: respalda tus datos de desarrollo antes de la actualización de versión.

   ```powershell
   docker exec mysql sh -c 'exec mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --no-tablespaces --set-gtid-purged=OFF manzagrafica_local' > "<carpeta de respaldos>\manzagrafica_local_antes_00-03.sql"
   ```

   Comprueba después que el archivo pese más de 0 bytes. Guárdalo en la carpeta cifrada, nunca en el repositorio.

2. Comprueba el volumen y el contenedor:

   ```powershell
   docker volume ls --filter name=mysql_data
   docker inspect mysql --format "{{range .Mounts}}{{.Name}} -> {{.Destination}}{{println}}{{end}}"
   ```

   Debe aparecer `mysql_data -> /var/lib/mysql`. Si aparece otro nombre, detente: el compose apuntaría a un volumen equivocado.

3. Detén el contenedor y quítalo **sin** `-v`:

   ```powershell
   docker stop mysql
   docker rm mysql
   docker volume ls --filter name=mysql_data
   ```

   El volumen tiene que seguir apareciendo.

4. Levanta el compose:

   ```powershell
   docker compose up -d
   docker compose logs -f db
   ```

   Espera a ver `ready for connections` y sal con Ctrl+C. Como la imagen pasa de 8.0.43 a 8.0.46, MySQL actualiza las tablas de sistema solo la primera vez (en los registros aparece «upgrade»). **No se puede volver a 8.0.43 con ese volumen**: para eso sirve el respaldo del paso 1.

5. Comprueba que tus datos de desarrollo siguen ahí:

   ```powershell
   docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "SHOW DATABASES; SELECT @@version, @@time_zone, @@sql_mode;"'
   ```

   Esperado: `manzagrafica_local` en la lista, `8.0.46`, `UTC` y `NO_ENGINE_SUBSTITUTION`.

**Si el contenedor no arranca y el registro dice `Unknown or incorrect time zone: 'UTC'`**, las tablas de zona horaria no están cargadas en el volumen. Producción sí las tiene (línea base, sección 5) y el volumen actual también (bitácora 00-01 SQL local). Para cargarlas: quita temporalmente `--default-time-zone=UTC` del compose, levanta el contenedor y ejecuta:

```powershell
docker compose exec db sh -c 'mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -uroot -p"$MYSQL_ROOT_PASSWORD" mysql'
```

Después vuelve a poner la opción y ejecuta `docker compose up -d`.

## 4. Crear la base de la réplica

Primero confirma que no existe, para no pisar nada:

```powershell
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "SHOW DATABASES LIKE ''manzagrafica_replica'';"'
```

Si no devuelve nada, créala vacía:

```powershell
docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE manzagrafica_replica CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
```

## 5. Restaurar un volcado verificado

1. El volcado tiene que haber pasado `scripts\verificar_respaldo.py` con código 0 y estar en el registro de `docs/operacion/respaldo.md`.
2. Restaura y mide el tiempo. La redirección `<` va dentro de `cmd /c` para que PowerShell no cambie la codificación del archivo:

   ```powershell
   $t = Measure-Command { cmd /c "docker compose exec -T db sh -c ""exec mysql -uroot -p`$MYSQL_ROOT_PASSWORD manzagrafica_replica"" < ""<ruta del volcado>""" }
   "Código: $LASTEXITCODE · Segundos: $([math]::Round($t.TotalSeconds, 1))"
   ```

   Código 0 y sin mensajes `ERROR` significa que terminó bien.
3. Comprueba que no apareció ninguna base inesperada y que la réplica tiene 18 tablas:

   ```powershell
   docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "SHOW DATABASES; SELECT COUNT(*) AS tablas FROM information_schema.tables WHERE table_schema = ''manzagrafica_replica'';"'
   ```

## 6. Apuntar la aplicación a la réplica

Hasta la 00-04, `settings.py` apunta a `manzagrafica_local`. Para usar la réplica sin tocarlo, define `DATABASE_URL` **solo en la sesión de PowerShell**:

```powershell
$env:DATABASE_URL = "mysql://root:<contraseña>@127.0.0.1:3306/manzagrafica_replica"
```

- Reemplaza `<contraseña>` en tu terminal. No la escribas en ningún archivo del repositorio. Si tiene caracteres especiales (`@`, `:`, `/`, `#`, `%`), escríbelos codificados para URL (por ejemplo, `@` se escribe `%40`).
- **La variable se pierde al cerrar la sesión.** Al abrir otra terminal, la app vuelve a `manzagrafica_local`. Para volver antes, ejecuta `Remove-Item Env:DATABASE_URL`.
- Comprueba a qué base apunta antes de hacer cualquier cosa: la línea «Base medida» de la sección 7.

## 7. Comprobar la paridad

Con `DATABASE_URL` definida y el `.venv` activo:

```powershell
python scripts\diagnostico\paridad_replica.py
$LASTEXITCODE
```

El guion es de solo lectura y no muestra filas. Compara con producción la versión de MySQL, el conjunto de caracteres, la colación, `@@time_zone`, `@@system_time_zone`, `@@sql_mode`, las tablas de zona horaria, la versión de Python y la diferencia entre `pip freeze` y `requirements.txt`. Las diferencias aceptadas están en `DIFERENCIAS_ACEPTADAS`, al inicio del guion (hoy solo Python 3.13.0 frente a 3.13.1). Salen como «No (aceptada)» y no cambian el resultado. **Código 0:** paridad, con o sin diferencias aceptadas. **Código 1:** hay al menos una diferencia no aceptada o no se pudo medir. Para aceptar una diferencia nueva, primero se registra la decisión en la tabla siguiente y después en el guion.

### Tabla de paridad

Producción medida el 2026-10-20 (`linea-base-produccion.md`, secciones 5 y 7). Los valores locales de MySQL son los que fija el compose. Se confirman con el guion en `evidencia-00-03.md`.

| Elemento | Producción (00-01) | Local | Coincide |
| :------- | :----------------- | :---- | :------- |
| Versión de MySQL | 8.0.46 | 8.0.46 (`mysql:8.0.46`; antes 8.0.43) | Sí |
| Conjunto de caracteres de la base | `utf8mb4` | `utf8mb4` (base creada con ese conjunto) | Sí |
| Colación de la base | `utf8mb4_unicode_ci` | `utf8mb4_unicode_ci` | Sí |
| `@@time_zone` | `UTC` | `UTC` (`--default-time-zone=UTC`; antes `SYSTEM`) | Sí |
| `@@system_time_zone` | `UTC` | `UTC` | Sí |
| Tablas de zona horaria | Cargadas | Cargadas (vienen en el volumen) | Sí |
| `@@sql_mode` | `NO_ENGINE_SUBSTITUTION` | `NO_ENGINE_SUBSTITUTION` | Sí. Decisión del desarrollador (2026-10-21): opción A, paridad. El modo estricto solo para la base de pruebas (opción C) se evalúa en 02-01 (AUD-02-020). |
| Versión de Python | 3.13.1 | 3.13.0 (`.venv`, medido el 2026-10-21) | No. Decisión: se acepta por ser un parche menor de la misma versión. |
| `pip freeze` frente a `requirements.txt` | 21 y 21, sin diferencias | 21 y 21, sin diferencias (medido el 2026-10-21) | Sí |

## 8. Arrancar la aplicación

Antes de abrir pantallas, termina la comparación de conteos con la línea base: **abrir «Estadísticas» agrega una fila a `pedidos_historialbd`** (AUD-01-006) y cambia ese conteo.

```powershell
python manage.py showmigrations pedidos
python manage.py check
python manage.py runserver
```

- Inicia sesión con **tu propia cuenta de producción**: la réplica trae los usuarios de producción. No crees usuarios nuevos en la réplica.
- **No uses en la réplica «Respaldar BD» ni «Restaurar»**: escriben volcados con datos reales en `backups/` del repositorio y modifican la base.
- Al terminar, detén `runserver` (Ctrl+C) y ejecuta `docker compose stop`.

## 9. Refrescar la réplica

Cuando los datos queden viejos (por ejemplo, antes de ensayar una migración o un retroceso):

1. Genera, descarga y verifica un respaldo nuevo (`docs/operacion/respaldo.md`).
2. Repite la comprobación de cifrado (sección 2).
3. Borra **solo la base de la réplica** y créala de nuevo vacía. Revisa dos veces el nombre antes de pulsar Enter:

   ```powershell
   docker compose exec db sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD" -e "DROP DATABASE manzagrafica_replica; CREATE DATABASE manzagrafica_replica CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'
   ```

   Nunca borres `manzagrafica_local` ni el volumen.
4. Restaura (sección 5), comprueba la paridad (sección 7) y anota la fecha del volcado usado y el tiempo de restauración en la tabla siguiente.

| Fecha del refresco | Volcado (fecha en hora de Chile) | Tiempo de restauración (s) | Paridad |
| :----------------- | :------------------------------- | :------------------------- | :------ |
| 2026-10-21 (primera restauración, 00-03) | 2026-10-20 13:09:17 | 4,17 | 7 de 8 coinciden; Python aceptado; `pip freeze` 21/21 |
