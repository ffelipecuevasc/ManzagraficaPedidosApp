# Procedimiento de retroceso

Cómo volver producción al estado anterior cuando un despliegue sale mal. Meta: **menos de 15 minutos y sin perder datos** en los casos 1 y 2. El caso 3 sí pierde datos y se usa solo cuando los datos están dañados.

- **Creado en:** iteración 00-05 (2026-10-21).
- **Lo ejecuta:** el desarrollador. Los agentes no tocan PythonAnywhere.
- **Terminales:** las mismas marcas de `docs/operacion/despliegue.md`, sección 0: **[PC · PowerShell 7]**, **[PA · Bash]** y **[PA · Panel]**.
- **Ensayado:** en la réplica local (sección 5).

## 1. Antes de empezar: decide el caso

Anota la hora (hora de Chile) en que empiezas: el tiempo cuenta desde aquí.

| Pregunta | Sí | No |
| :------- | :- | :- |
| ¿El despliegue aplicó alguna migración? (`showmigrations` del paso 3.4 de `despliegue.md`) | Caso 2 | Caso 1 |
| ¿Hay datos incorrectos o perdidos (montos, pedidos, pagos) y no solo pantallas con error? | Caso 3 | Caso 1 o 2 |

Necesitas:

- **La etiqueta de destino:** la anterior a la desplegada (`git tag -n` en tu PC). Para el primer despliegue es `v0.0-inicial` o el commit anotado en el paso 3.1 de `despliegue.md`.
- `<carpeta del proyecto>` y `<ruta del virtualenv>` (pestaña **Web**, sección *Code*).

## 2. Caso 1 · Sin migraciones: volver el código

1. **[PA · Bash]** Ubicarse:

   ```bash
   cd <carpeta del proyecto>
   source <ruta del virtualenv>/bin/activate
   git describe --tags
   ```

   Debe mostrar la etiqueta que falló. Si muestra otra cosa, anótalo antes de seguir.
2. **[PA · Bash]** Volver a la etiqueta anterior:

   ```bash
   git checkout <etiqueta de destino>
   git describe --tags
   ```

   Debe responder `<etiqueta de destino>`. Si dice `Your local changes ... would be overwritten`, ejecuta `git status --short`, anota los archivos y detente: no fuerces.
3. **[PA · Bash]** Si el despliegue había cambiado `requirements.txt` (paso 3.3 de `despliegue.md`): `pip install -r requirements.txt`. Si había cambiado estáticos: `python manage.py collectstatic --noinput`.
4. **[PA · Bash]** `python manage.py check` → `System check identified no issues (0 silenced).`
5. **[PA · Panel]** Pestaña **Web** → **Reload**.
6. Verifica las tres pantallas y el registro de errores (paso 3.7 de `despliegue.md`).
7. Anota la hora de término y el resultado en el registro de la sección 6.

## 3. Caso 2 · Con migraciones de Clase 2

Una migración de Clase 2 solo agrega: tablas nuevas, columnas que admiten nulo e índices. El código anterior no las conoce y las ignora, así que **basta con volver el código (caso 1)**. Las filas que Django guardó en la tabla `django_migrations` para esas migraciones no molestan al código anterior.

**Revierte la migración solo si estorba**, por ejemplo si una tabla nueva ocupa disco que hace falta o si el próximo despliegue necesita partir de cero. En ese caso el orden importa:

1. **Primero revertir, con el código nuevo todavía en su lugar.** Django necesita el archivo de la migración para saber cómo deshacerla. **[PA · Bash]**:

   ```bash
   cd <carpeta del proyecto>
   source <ruta del virtualenv>/bin/activate
   python manage.py showmigrations pedidos
   python manage.py migrate pedidos <última migración de la etiqueta de destino> --plan
   ```

   El plan debe listar solo las migraciones del despliegue que falló, cada una con `Undo`. Si lista otras, detente.
2. **[PA · Bash]** Ejecuta la reversión:

   ```bash
   python manage.py migrate pedidos <última migración de la etiqueta de destino>
   python manage.py showmigrations pedidos
   ```

   Las migraciones del despliegue deben quedar con `[ ]`. Si la reversión falla con `IrreversibleError`, la migración no tiene vuelta: deja la base como está y vuelve solo el código (pasos 3 y 4).
3. **Después volver el código:** caso 1, pasos 2 a 7.
4. **[PA · Bash]** Comprueba que el código anterior ya no ve migraciones pendientes:

   ```bash
   python manage.py migrate --plan
   ```

   Debe responder `No planned migration operations.`

**Nunca al revés:** si vuelves primero el código, el archivo de la migración desaparece y Django ya no puede deshacerla. Si eso pasa, vuelve a la etiqueta nueva, revierte y retrocede otra vez.

Una migración de Clase 3 no tiene retroceso seguro sin respaldo: por eso está prohibida.

## 4. Caso 3 · Datos dañados: restaurar el último respaldo verificado

**Se pierde todo lo registrado después del respaldo** (pedidos, pagos, cambios de estado). Úsalo solo si los casos 1 y 2 no bastan.

1. **Avisa al equipo de Manza Gráfica** que no registre nada hasta nuevo aviso, y anota la hora.
2. **Elige el volcado:** el último con resultado VÁLIDO en `docs/operacion/respaldo.md`, sección 6 (normalmente el previo al despliegue). Anota su SHA-256.
3. **Vuelve el código** a la etiqueta que corresponde a ese respaldo (caso 1, pasos 1 a 4, sin recargar todavía). El esquema del código y el del volcado tienen que coincidir.
4. **Guarda el estado dañado** antes de pisarlo, por si hace falta rescatar algo: en la aplicación, «Respaldar BD», **un solo clic** (`respaldo.md`, sección 2). No lo borres hasta cerrar el incidente.
5. **[PA · Bash]** Ubica el volcado en el servidor y confirma que es el mismo que verificaste:

   ```bash
   ls -l <carpeta del proyecto>/backups/
   sha256sum <carpeta del proyecto>/backups/<archivo del volcado>
   ```

   El hash debe ser igual al del registro. Si el volcado ya rotó y no está, súbelo desde tu carpeta cifrada con la pestaña **Files** a una carpeta **fuera** del proyecto (por ejemplo `~/restauracion/`) y comprueba el hash igual.
6. **[PA · Bash]** Restaura. Los datos de conexión están en la pestaña **Databases** (usuario, servidor y nombre de la base, que tiene la forma `<usuario>$<base>`). La contraseña se pide al ejecutar; no la escribas en el comando:

   ```bash
   time mysql -u <usuario> -h <servidor de la base> -p '<usuario>$<base>' < <ruta del volcado>
   echo "Código: $?"
   ```

   Esperado: `Código: 0` y ningún mensaje `ERROR`. Si aparece `ERROR`, no reintentes a ciegas: anota el mensaje y la línea, y vuelve a intentarlo solo una vez después de revisarlos.

   Alternativa sin consola, si la aplicación responde: «Restaurar» en la aplicación. Crea antes un volcado de emergencia, que cuenta en la rotación de 5 (`respaldo.md`, sección 1).
7. **[PA · Bash]** `python manage.py showmigrations pedidos`: las migraciones deben coincidir con las de la etiqueta del paso 3.
8. **[PA · Panel]** **Reload** y verifica las tres pantallas y el registro de errores (`despliegue.md`, paso 3.7).
9. **Avisa al equipo** que puede volver a registrar, y **qué debe volver a ingresar**: todo lo hecho desde la fecha y hora del respaldo.
10. Si subiste el volcado a `~/restauracion/`, bórralo: tiene datos de clientes. Anota el incidente en el registro de la sección 6 y en la bitácora de la iteración, sin datos de clientes.

## 5. Ensayo en la réplica local

El retroceso se ensaya en `manzagrafica_replica`, nunca en producción ni en `manzagrafica_local`. El ensayo de la 00-05 está en `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-05.md`, parte A, y su resultado en la bitácora de la 00-05. Para repetirlo (por ejemplo en 07-04), usa los mismos pasos.

## 6. Registro de retrocesos

Ensayos y retrocesos reales. Solo tiempos, etiquetas y resultado.

| Fecha (hora de Chile) | Real o ensayo | Caso | De → a | Minutos | Resultado |
| :-------------------- | :------------ | :--- | :----- | :------ | :-------- |
