# Bitácora 01-08 · Comentarios del registro alineados con la opción A

- **Fecha:** 2026-10-26
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión. **Sin migraciones; no requiere respaldo ni despliegue propio**: viaja en el siguiente despliegue con cambios de código.

## Resumen

- Los cinco lugares de la tabla de la [iteración](../../10_epicas/epica-01-observabilidad/iteracion-01-08-comentarios-registro.md) tienen el texto propuesto, sin cambios de redacción.
- El diff de `settings.py` es el aprobado por el desarrollador el 2026-10-26 y conserva el fin de línea LF del bloque `LOGGING` (0 retornos de carro en las líneas 205 a 213).
- El punto 5 (`registro.py:69`) cabe en una línea (112 caracteres, similar a la línea 71 del mismo archivo), así que no se repartió.
- Solo cambia texto: ninguna instrucción, valor de configuración, plantilla ni prueba.

## Decisiones del desarrollador (2026-10-26)

1. Aprueba el diff de `settings.py` tal como está en la iteración y los cinco puntos de la tabla, incluido `registro.py:69`.
2. Protección de archivos sensibles: el desarrollador cambió él mismo `.claude/settings.json` (cuatro reglas `deny` nuevas: `Edit(**/.env.*)`, `Read(**/.env)`, `Read(**/.env.*)` y `Read(**/backups/**)`; y quitó la ruta absoluta de la carpeta de respaldos). La corrección de la sección 5 de `.claude/README.md` la pidió al agente, pero el permiso `deny` sobre `.claude/` la bloqueó: el texto propuesto se entregó al desarrollador. La protección es parcial: las reglas `Read` y `Edit` no cubren un `grep -r` ni un guion que abra los archivos, y el sandbox de Claude Code no existe en Windows nativo. Por eso las búsquedas del agente excluyen siempre `.env`, `.env.*`, `backups/` y `respaldos/`.

## Diff

`git diff --stat` (solo código; `.claude/settings.json` es el cambio del desarrollador y no forma parte de esta iteración):

```text
 PedidosApp/settings.py | 8 +++++---
 pedidos/decorators.py  | 4 ++--
 pedidos/eventos.py     | 2 +-
 pedidos/registro.py    | 2 +-
 pedidos/views.py       | 2 +-
 5 files changed, 10 insertions(+), 8 deletions(-)
```

Comprobación de solo comentarios: `git diff -U0 -- PedidosApp pedidos | grep -E '^[+-]' | grep -vE '^(\+\+\+|---) ' | grep -vE '^[+-][[:space:]]*#'` no devuelve ninguna línea (las 18 líneas `+` y `-` empiezan con `#` después de la sangría).

```diff
diff --git a/PedidosApp/settings.py b/PedidosApp/settings.py
index e8f92ff..498cf90 100644
--- a/PedidosApp/settings.py
+++ b/PedidosApp/settings.py
@@ -204,9 +204,11 @@ MEDIA_URL = '/media/'
 MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
 
 # REGISTRO (iteración 01-02, RDA-013)
-# Todo va a stderr, que PythonAnywhere guarda en error.log (con su fecha UTC al inicio de
-# cada línea: por eso el formato no repite la fecha). Sin archivos de registro propios.
-# Configurar la raíz reemplaza cualquier manejador previo del entorno y evita líneas dobles.
+# Todo va a stderr. En PythonAnywhere, stderr termina en server.log (hora de Chile, con la
+# traza en una línea y los saltos como #012): es el archivo de diagnóstico (opción A, 01-06).
+# error.log recibe además los mismos errores en el formato de PythonAnywhere, por un manejador
+# del entorno que esta configuración no reemplaza (deducción no confirmada). El formato no
+# lleva fecha porque el recolector la antepone. Sin archivos de registro propios.
 LOGGING = {
     'version': 1,
     'disable_existing_loggers': False,
diff --git a/pedidos/decorators.py b/pedidos/decorators.py
index 582a01c..454457c 100644
--- a/pedidos/decorators.py
+++ b/pedidos/decorators.py
@@ -19,8 +19,8 @@ def transaccion_segura(view_func):
             return view_func(request, *args, **kwargs)
         except Exception as e:
             # Si algo falla, capturamos el error aquí mismo
-            # Traza completa a error.log con el contexto de la petición (01-03). El rediseño
-            # del decorador es de la Épica 03.
+            # Traza completa con el contexto de la petición (01-03); en producción se lee en
+            # server.log (opción A, 01-06). El rediseño del decorador es de la Épica 03.
             logger.exception('Error capturado por decorador en %s', view_func.__name__,
                              extra={'request': request})
 
diff --git a/pedidos/eventos.py b/pedidos/eventos.py
index 108df1e..649f395 100644
--- a/pedidos/eventos.py
+++ b/pedidos/eventos.py
@@ -44,7 +44,7 @@ def registrar_evento(tipo, usuario=None, entidad='', entidad_id=None, resumen=''
         transaction.on_commit(lambda: _escribir_evento(datos))
     except Exception:  # noqa: BLE001
         # Captura amplia permitida (AGENTS.md, regla 4): el servicio de registro nunca puede
-        # hacer fallar una petición. El problema queda en error.log con su traza.
+        # hacer fallar una petición. El problema queda en server.log con su traza.
         logger.exception('No se pudo programar el evento %s', tipo)
 
 
diff --git a/pedidos/registro.py b/pedidos/registro.py
index fc68396..ca77300 100644
--- a/pedidos/registro.py
+++ b/pedidos/registro.py
@@ -66,7 +66,7 @@ class FiltroContextoPeticion(logging.Filter):
                 record.ruta = request.path  # sin la cadena de consulta
                 record.usuario = _usuario(request)
         except Exception as error:  # noqa: BLE001
-            # Única captura amplia permitida (AGENTS.md, regla 4): el registrador nunca puede
+            # Captura amplia permitida (AGENTS.md, regla 4), como las de eventos.py: el registrador nunca puede
             # hacer fallar una petición. Se emite el problema a stderr antes de absorberlo.
             sys.stderr.write(f'nivel=ERROR registrador=pedidos.registro mensaje="Fallo del filtro de contexto: '
                              f'{type(error).__name__}"\n')
diff --git a/pedidos/views.py b/pedidos/views.py
index 7573059..dc78ade 100644
--- a/pedidos/views.py
+++ b/pedidos/views.py
@@ -191,7 +191,7 @@ def crear_pedido(request):
                                 precio_unitario=int(item['precio_unitario'])
                             )
                     except Exception as e:
-                        # Supresión que descarta ítems: se corrige en 03-02. Mientras, queda en error.log.
+                        # Supresión que descarta ítems: se corrige en 03-02. Mientras, queda en server.log.
                         logger.exception('Error procesando items del pedido %s', pedido.pk,
                                          extra={'request': request})
                         # No detenemos el proceso, los items son recuperables o editables
```

## Verificación

| Comprobación | Resultado |
| :----------- | :-------- |
| `python manage.py test pedidos` | 79 pruebas, `OK` |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check --dry-run` | `No changes detected` |
| Migraciones nuevas | Ninguna |
| Pantallas | No aplica: no se tocaron plantillas, estilos ni JavaScript |

## Búsqueda de comentarios pendientes

```bash
grep -rn --exclude=.env --exclude='.env.*' --exclude-dir=backups --exclude-dir=respaldos \
  -E "error\.log|l[ií]neas dobles" pedidos PedidosApp scripts \
  --include=*.py --include=*.html --include=*.js --include=*.sh
```

```text
PedidosApp/settings.py:209:# error.log recibe además los mismos errores en el formato de PythonAnywhere, por un manejador
```

Revisión a mano: la única mención es el comentario nuevo, y dice que `error.log` recibe una copia de los errores en el formato de PythonAnywhere; el archivo de diagnóstico que nombra es `server.log` (línea 208). Ningún comentario afirma que los errores se leen en `error.log` ni que `LOGGING` evita líneas dobles.

## Criterios de aceptación

- [x] Los cinco lugares tienen el texto propuesto.
- [x] El diff de `settings.py` lo aprobó el desarrollador antes de aplicarlo y coincide con el de la iteración.
- [x] El diff total cambia solo comentarios.
- [x] 79 pruebas en `OK`, `check` sin errores, `No changes detected`.
- [x] Ningún comentario afirma que los errores se leen en `error.log` ni que `LOGGING` evita líneas dobles.

## Pendientes

- Desplegar con el siguiente cambio de código (01-09 o la próxima iteración de la Épica 02 o 03).
- Sección 5 de `.claude/README.md`: la aplica el desarrollador con el texto entregado.
