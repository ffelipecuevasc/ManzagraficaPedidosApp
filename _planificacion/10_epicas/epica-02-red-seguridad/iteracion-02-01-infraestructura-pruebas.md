# Iteración 02-01 · Infraestructura de pruebas

- **Épica:** 02 · Red de seguridad
- **Estado:** Terminada (2026-10-25; sin desplegar; el bloque de `settings.py` viaja en 01-06, donde se revisa `check --deploy` del servidor)
- **Subfase del plan:** 2.1
- **Depende de:** Épica 00
- **RDA relacionadas:** RDA-002, RDA-006
- **Hallazgos que cierra:** ninguno por sí sola. Avanza AUD-01-015 (cero pruebas) y AUD-02-020 (modo estricto solo en la base de pruebas).
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** No (no despliega nada: solo agrega pruebas y, si se aprueba, ajusta la configuración local de pruebas)

## Objetivo

Dejar una base de pruebas confiable sobre la que se escriban las iteraciones 02-02 a 02-05: ejecución contra MySQL en Docker con una base de pruebas que se crea y se destruye sola, que hereda la configuración de producción y que nunca es una base real; datos construidos con funciones; archivos organizados por dominio; un mecanismo que distinga «fallo esperado» de «fallo nuevo»; y el comando incorporado a la lista de comprobación previa al despliegue.

## Punto de partida (medido en 01-01, 2026-10-25)

- `python manage.py test pedidos` corre **10 pruebas en `OK`** con la infraestructura actual, sin cambios de configuración: Django crea y destruye `test_<DB_NAME>` y el usuario local tiene permiso para hacerlo.
- Con `$env:DB_NAME = 'manzagrafica_replica'` la base de pruebas es `test_manzagrafica_replica`; con el valor por defecto sería `test_manzagrafica_local`. **El nombre depende de una variable de entorno.**
- Todas las pruebas están en `pedidos/tests.py`, en 4 clases: `RobotsTxtTests` (3), `ListaPagosRutaTests` (2), `CargaDiferidaWeasyprintTests` (1) y `RegistroEventoTests` (4).
- `test` muestra la advertencia `mysql.W002` (modo estricto sin activar), porque la réplica copia el `sql_mode` de producción (`NO_ENGINE_SUBSTITUTION`, AUD-02-020).
- `docs/operacion/despliegue.md`, punto 1 de la lista previa, todavía dice «Hasta la 02-01 no hay pruebas».

## Advertencia

**La base de pruebas nunca puede ser `manzagrafica_replica` ni `manzagrafica_local`.** Django destruye la base de pruebas al terminar: si su nombre coincidiera con una base real, la borraría. Toda propuesta de esta iteración que toque el nombre de la base de pruebas lo comprueba de forma explícita y la bitácora copia la línea `Creating test database for alias 'default' ('<nombre>')` de la salida de `test -v 2`.

## Tareas

1. **Ejecución contra MySQL en Docker** (RDA-006):
   - **Nombre fijo de la base de pruebas** (resuelto el 2026-10-25: `test_manzagrafica` con bloqueo; **requiere consulta**: cambia `PedidosApp/settings.py`). Propuesta: `DATABASES['default']['TEST'] = {'NAME': 'test_manzagrafica'}`, para que el nombre no dependa de `DB_NAME`, y una comprobación al cargar la configuración que detenga la ejecución si `TEST.NAME` es `manzagrafica_replica` o `manzagrafica_local`. Alternativa: dejar el comportamiento actual (`test_<DB_NAME>`) y documentarlo.
   - **Juego de caracteres y colación** (resuelto el 2026-10-25: se fijan en `TEST` con los valores de la línea base; **requiere consulta**). Hoy la base de pruebas hereda `utf8mb4` y `utf8mb4_unicode_ci` del servidor (`compose.yaml`). Propuesta: fijarlos también en `TEST` (`CHARSET` y `COLLATION`) para que no dependan del servidor. Alternativa: confiar en la herencia y comprobarla con la prueba siguiente.
   - **Prueba de entorno**: una prueba que consulta, dentro de la base de pruebas, `@@character_set_database`, `@@collation_database`, `@@time_zone` y `DATABASE()`, y comprueba `utf8mb4`, `utf8mb4_unicode_ci`, `UTC` (o `+00:00`) y que el nombre empieza por `test_` y no es una base real. Así la herencia queda verificada en cada ejecución y no solo en la bitácora.
   - Comprobar en la bitácora que la base de pruebas se crea al empezar y se destruye al terminar (líneas `Creating` y `Destroying`), y que tras una ejecución interrumpida la siguiente la recrea sin intervención (o documentar la respuesta a la pregunta de Django).
   - Si el usuario de MySQL perdiera el permiso para crear la base, el agente entrega al desarrollador el comando exacto para ejecutarlo en el contenedor `manzagrafica-mysql`. No lee `.env`.
2. **Modo estricto de `sql_mode` en la base de pruebas** (AUD-02-020; resuelto el 2026-10-25: opción A, paridad). Opciones:
   - **A, paridad:** las pruebas corren con `NO_ENGINE_SUBSTITUTION`, igual que producción. Fijan el comportamiento real, incluido el truncado silencioso, y la advertencia `mysql.W002` se silencia o se documenta.
   - **B, estricto solo en pruebas:** `OPTIONS['init_command'] = "SET sql_mode='STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'"` aplicado solo cuando corren las pruebas. Detecta datos que producción truncaría, pero las pruebas dejan de reflejar producción; las que dependen del truncado deben declararlo. Exige un mecanismo para saber que corren las pruebas (un ajuste propio o un ejecutor de pruebas), que también es configuración.
   - Propuesta del agente: **A** en esta iteración, porque la red de seguridad debe fijar lo que hace producción hoy; el modo estricto se prueba contra la réplica en 04-05, como ya dice AUD-02-020. La decisión queda escrita en la bitácora y en la nota de AUD-02-020.
3. **Estrategia de datos de prueba**: funciones que construyen objetos coherentes bajo demanda, nunca accesorios estáticos (`fixtures` JSON).
   - Resuelto el 2026-10-25: **funciones propias** (elegida). Opciones: **funciones propias sin dependencia** (propuesta: un módulo `pedidos/tests/factorias.py` con `crear_usuario()`, `crear_cliente()`, `crear_producto()`, `crear_pedido(items=..., pagos=...)`, `crear_pago()`, `crear_cotizacion(items=...)` y `crear_evento()`, con valores por defecto válidos y parámetros para lo que cada prueba necesita) o **`factory_boy`** (dependencia nueva: requiere consulta, justificar su peso y una RDA).
   - Las funciones usan montos enteros en pesos y cantidades con `Decimal` (AGENTS.md, regla 13), fechas con `timezone` (regla 6) y datos ficticios: nunca nombres, teléfonos ni montos copiados de la réplica.
   - El ayudante `crear_evento` de `RegistroEventoTests` pasa a las funciones comunes.
4. **Organización por dominio** (requiere consulta: mueve un archivo): `pedidos/tests.py` pasa a un paquete `pedidos/tests/` sin perder ninguna de las 10 pruebas. Propuesta de archivos:
   - `__init__.py` y `factorias.py`;
   - `test_entorno.py` (prueba de entorno de la tarea 1);
   - `test_rutas_publicas.py` (`RobotsTxtTests`), `test_pagos.py` (`ListaPagosRutaTests`), `test_arranque.py` (`CargaDiferidaWeasyprintTests`) y `test_eventos.py` (`RegistroEventoTests`);
   - archivos vacíos o con solo su docstring no se crean: 02-02 a 02-05 agregan `test_dinero.py`, `test_pedidos.py`, `test_cotizaciones.py`, `test_regresiones.py` y `test_acceso.py` cuando los necesiten.
   - Criterio: antes y después del cambio, `test pedidos -v 2` lista los mismos 10 nombres de prueba (más la de entorno), copiados en la bitácora.
5. **Fallos esperados** (resuelto el 2026-10-25: `expectedFailure` con `@tag('regresion')`, sin prueba de demostración): mecanismo para las pruebas de regresión de 02-04 que fallan hoy a propósito. Propuesta: `unittest.expectedFailure` más la etiqueta `@tag('regresion')` de Django y un comentario con el hallazgo (`AUD-…`) y la iteración que lo corrige. El resumen de `test` informa `expected failures=N` aparte de `failures`, y si una prueba marcada empieza a pasar se informa como `unexpected successes`, que avisa de quitar la marca. Alternativa: `skip` (descartable: no ejecuta la prueba y no avisa si el defecto se corrige). Se incluye una prueba de demostración solo si el desarrollador la quiere; si no, el mecanismo queda documentado y lo estrena 02-04.
6. **Comando documentado e incorporado al despliegue**:
   - Comando oficial en PowerShell 7: `python manage.py test pedidos` (con `-v 2` para ver el nombre de la base de pruebas), con el contenedor encendido. Si se aprueba la tarea 5, también `python manage.py test pedidos --exclude-tag regresion` para ver solo las pruebas que deben pasar.
   - `docs/operacion/despliegue.md`, punto 1 de la lista previa: reemplazar «Hasta la 02-01 no hay pruebas» por el resultado esperado (`OK`, con `expected failures=N` permitido solo si coincide con las regresiones declaradas). Se puede editar sin consulta (RDA-012) y el cambio queda en la bitácora.
   - Documentar dónde se describe la infraestructura (propuesta: una sección en `docs/operacion/replica-local.md` o un archivo nuevo `docs/operacion/pruebas.md`; resuelto el 2026-10-25: `docs/operacion/pruebas.md`).

## Criterios de aceptación

- [x] La salida de `python manage.py test pedidos -v 2` está en la bitácora con las líneas `Creating test database` y `Destroying test database`, y el nombre de la base de pruebas no es `manzagrafica_replica` ni `manzagrafica_local`. `test_manzagrafica`.
- [x] La prueba de entorno comprueba dentro de la base de pruebas `utf8mb4`, `utf8mb4_unicode_ci` y zona horaria UTC, y pasa. También comprueba el nombre de la base y el modo SQL.
- [x] La decisión sobre el modo estricto está escrita en la bitácora y en la nota de AUD-02-020, y la configuración refleja la opción elegida (o queda sin cambios si se eligió A). Opción A, sin cambios en `OPTIONS`.
- [x] `pedidos/tests.py` ya no existe y `pedidos/tests/` contiene las 10 pruebas anteriores con los mismos nombres de método, más las nuevas de esta iteración; `test pedidos` las encuentra todas. 17 pruebas: las 10 anteriores, 4 de entorno y 3 de factorías.
- [x] Existen las funciones de datos de prueba acordadas, usadas al menos por las pruebas de eventos, y ninguna prueba usa accesorios estáticos.
- [x] El mecanismo de fallos esperados está documentado (en la bitácora y en el procedimiento de pruebas) y el resumen de `test` distingue `expected failures` de `failures`. En `docs/operacion/pruebas.md`, sección 7; sin prueba de demostración.
- [x] `docs/operacion/despliegue.md`, punto 1, describe el comando y el resultado esperado.
- [x] `python manage.py test pedidos` en verde en tres ejecuciones seguidas, `check` sin errores y `makemigrations --check --dry-run` sin cambios.
- [x] Toda decisión `PENDIENTE_DESARROLLADOR` de esta iteración quedó resuelta y registrada en `registro-pendientes.md`. Las 6 resueltas el 2026-10-25.

## Fuera de alcance

- Escribir las pruebas de dinero, flujos, regresiones y acceso (02-02 a 02-05).
- Activar el modo estricto en la réplica o en producción (se prueba en 04-05).
- Medir cobertura o integrar ejecución automática en GitHub (no está en el plan).
- Cambiar código de la aplicación: si al mover las pruebas aparece un defecto, se anota en `registro-pendientes.md`.

## Datos requeridos del cliente

- Ninguno.
