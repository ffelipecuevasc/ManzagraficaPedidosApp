# Pruebas automatizadas

Cómo se ejecutan y se escriben las pruebas de Manza Gráfica App. Infraestructura creada en la iteración 02-01 (RDA-006). Comandos en PowerShell 7.

## 1. Requisitos

- El contenedor MySQL local encendido (`docker compose up -d`, ver `replica-local.md`).
- El entorno virtual activo y el `.env` con las variables `DB_*`.

## 2. Comandos

```powershell
# Todas las pruebas (comando oficial de la lista de despliegue)
python manage.py test pedidos

# Con el detalle de cada prueba y el nombre de la base de pruebas
python manage.py test pedidos -v 2

# Solo las pruebas que deben pasar (excluye las regresiones que fallan a propósito)
python manage.py test pedidos --exclude-tag regresion

# Un dominio o una clase
python manage.py test pedidos.tests.test_eventos
python manage.py test pedidos.tests.test_eventos.RegistroEventoTests
```

Resultado esperado: `OK`. Si hay regresiones declaradas, `OK (expected failures=N)`, donde N es el número de pruebas marcadas con `regresion`.

## 3. La base de pruebas

- **Nombre fijo: `test_manzagrafica`** (`DATABASES['default']['TEST']` en `settings.py`). No depende de `DB_NAME`: da lo mismo si apuntas a la réplica o a la base local.
- **Nunca puede ser `manzagrafica_replica` ni `manzagrafica_local`.** Django destruye la base de pruebas al terminar. `settings.py` detiene la carga con `ImproperlyConfigured` si el nombre de la base de pruebas coincide con una base real o con la base activa.
- Django la **crea al empezar y la destruye al terminar** (líneas `Creating test database` y `Destroying test database` de `-v 2`). Las bases reales no se tocan.
- Si una ejecución se interrumpe y la base queda creada, la siguiente pregunta si se puede borrar: responde `yes`. En una ejecución sin atención, usa `--noinput`, que la borra y la vuelve a crear.
- **Juego de caracteres y colación** fijados en `TEST`: `utf8mb4` y `utf8mb4_unicode_ci`, los de producción (`linea-base-produccion.md`, sección 5). La zona horaria viene del servidor (UTC, `compose.yaml`).
- `test_entorno.py` comprueba en cada ejecución el nombre, el juego de caracteres, la colación, la zona horaria y el modo SQL.

## 4. Modo SQL

Las pruebas corren **sin modo estricto** (`NO_ENGINE_SUBSTITUTION`), igual que producción (decisión 02-01, opción A, AUD-02-020). Por eso `test` muestra la advertencia `mysql.W002`: es esperada y no se silencia, porque silenciarla la ocultaría también en `check --deploy`.

Una prueba que dependa del truncado o el ajuste silencioso de MySQL (un texto más largo que la columna, un número fuera de rango) lo declara con un comentario `# Depende del truncado silencioso (AUD-02-020)`, para revisarla cuando 04-05 evalúe el modo estricto.

## 5. Organización

Paquete `pedidos/tests/`, un archivo por dominio:

| Archivo | Contenido |
| :------ | :-------- |
| `factorias.py` | Funciones que construyen datos de prueba |
| `test_entorno.py` | Configuración de la base de pruebas |
| `test_factorias.py` | Coherencia de las funciones de datos |
| `test_arranque.py` | Carga diferida de bibliotecas pesadas |
| `test_rutas_publicas.py` | Rutas sin sesión (`robots.txt`) |
| `test_pagos.py` | Pagos |
| `test_eventos.py` | Registro de eventos, su purga y el servicio `registrar_evento` |
| `test_registro.py` | Formato, emoji por nivel y niveles del registro de la aplicación (`LOGGING`) |
| `test_errores.py` | Páginas 404 y 500 y trazas completas |
| `test_eventos_negocio.py` | Un evento por operación del inventario y lecturas sin eventos |
| `test_admin_eventos.py` | Admin de eventos: solo lectura, solo superusuarios, filtros, búsqueda y consultas |

Las iteraciones siguientes agregan los archivos que necesiten (por ejemplo `test_dinero.py`, `test_pedidos.py`, `test_cotizaciones.py`, `test_regresiones.py`, `test_acceso.py`). No se crean archivos vacíos.

## 6. Datos de prueba

- Se construyen con las funciones de `pedidos/tests/factorias.py` (`crear_usuario`, `crear_superusuario`, `crear_cliente`, `crear_producto`, `crear_pedido`, `crear_item_pedido`, `crear_pago`, `crear_cotizacion`, `crear_item_cotizacion`, `crear_evento`). Nunca accesorios estáticos (`fixtures` JSON).
- Cada función tiene valores por defecto válidos; la prueba pasa solo lo que le importa: `crear_pedido(items=[{'cantidad': '2.5', 'precio_unitario': 4_000}])`.
- Datos ficticios, montos enteros en pesos, cantidades con `Decimal` y fechas con `timezone`.
- Las funciones **no aplican reglas de negocio** de las vistas (no recalculan `valor_venta` ni `estado_pago`): esas reglas son lo que se prueba.
- Sin dependencias externas (decisión 02-01).

## 7. Regresiones que fallan a propósito

Una prueba que demuestra un defecto todavía sin corregir se marca así:

```python
from unittest import expectedFailure

from django.test import TestCase, tag


class EliminarPagoTests(TestCase):
    @tag('regresion')
    @expectedFailure  # AUD-02-002: se corrige en 03-0X. Quitar la marca al corregir.
    def test_eliminar_pago_responde_200(self):
        ...
```

- El resumen de `test` las cuenta aparte: `expected failures=N`. Un `failures` es siempre un fallo nuevo.
- Si el defecto se corrige y la prueba pasa, aparece como `unexpected successes` y el conjunto **falla**: hay que quitar `@expectedFailure` (y la etiqueta) en la misma iteración que corrige.
- No se usa `skip`: no ejecuta la prueba y no avisa cuando el defecto se corrige.
