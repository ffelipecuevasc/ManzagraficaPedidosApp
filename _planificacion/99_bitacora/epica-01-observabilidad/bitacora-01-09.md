# Bitácora 01-09 · Capturas amplias que incumplen la regla 4

- **Fecha:** 2026-10-26
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión. Implementada en local; **sin migraciones**. Se despliega como `v1.2-capturas`, junto con la 01-08, **después** de la parte D de la 01-06 (2026-11-01), con respaldo descargado antes del despliegue (decisión 6).

## Resumen

- Decisión del desarrollador (2026-10-26): la 01-09 se implementa ahora en local; el despliegue sigue después de la parte D de la 01-06.
- Ítems (`editar_pedido`, `crear_cotizacion`, `editar_cotizacion`): opción A. El `pass` se reemplazó por `logger.exception(..., extra={'request': request})` con el mismo comentario que `crear_pedido` (remite a 03-02). El usuario ve lo mismo que antes.
- Respaldo y restauración (`generar_respaldo_bd`, `restaurar_bd`): opción C con los textos aprobados. `generar_respaldo_bd` usa `messages.error` y redirige a `respaldar_bd`. `restaurar_bd` guarda el nombre del respaldo de emergencia y solo lo nombra si se generó.
- Ninguna captura muestra `str(e)`. El diff no toca transacciones, métodos HTTP, plantillas, `utils.py` ni el inventario de eventos.
- 7 pruebas nuevas en `pedidos/tests/test_capturas_amplias.py` (una por captura, y dos para `:1191`: con y sin respaldo previo). Fallos simulados con datos inválidos (producto inexistente) o con `mock`; no se ejecutan `mysql` ni `mysqldump`.

## Pruebas primero (regla 8.15)

Salida antes de la corrección (líneas de traza recortadas):

```text
Found 7 test(s).
FFFFFFF
FAIL: test_crear_cotizacion_registra_el_fallo_de_items
AssertionError: no logs of level ERROR or higher triggered on pedidos.views
FAIL: test_editar_cotizacion_registra_el_fallo_de_items
AssertionError: no logs of level ERROR or higher triggered on pedidos.views
FAIL: test_editar_pedido_registra_el_fallo_de_items
AssertionError: no logs of level ERROR or higher triggered on pedidos.views
FAIL: test_generar_respaldo_fallido_registra_y_muestra_texto_fijo
AssertionError: no logs of level ERROR or higher triggered on pedidos.views
FAIL: test_respaldo_previo_fallido_registra_y_no_restaura
AssertionError: no logs of level ERROR or higher triggered on pedidos.views
FAIL: test_restauracion_fallida_antes_del_respaldo_previo_no_nombra_archivo
AssertionError: no logs of level ERROR or higher triggered on pedidos.views
FAIL: test_restauracion_fallida_nombra_el_respaldo_previo
AssertionError: no logs of level ERROR or higher triggered on pedidos.views
Ran 7 tests in 6.726s
FAILED (failures=7)
```

Cada prueba comprueba, después de la corrección: un solo `ERROR` de `pedidos.views`, con traza (`exc_info`) y con la petición del usuario; en respaldo y restauración, la redirección y el texto exacto aprobado (que no contiene el texto de la excepción simulada).

## Verificación

| Comando | Resultado |
| :------ | :-------- |
| `python manage.py test pedidos` | 86 pruebas (79 + 7), `OK` |
| `python manage.py check` | `System check identified no issues (0 silenced).` |
| `python manage.py makemigrations --check --dry-run` | `No changes detected` |

## Revisión manual en la réplica

- **Generar respaldo (camino normal):** con el cliente de pruebas de Django contra la réplica local y el primer superusuario, `GET /base_datos/respaldar_bd/accion/` respondió **302**, no la descarga. Causa: `mysqldump` no está en el PATH de este equipo Windows (`FileNotFoundError: [WinError 2]`). El camino de error nuevo funcionó en condiciones reales: un `ERROR` «Error al generar el respaldo» con traza en el registro y el mensaje fijo aprobado en pantalla. El listado `respaldar_bd` respondió 200.
- **Efecto secundario:** `generar_respaldo_mysql()` abre el `.sql` antes de llamar a `mysqldump` y solo lo borra ante `CalledProcessError`, no ante `FileNotFoundError`. Los dos intentos dejaron **dos archivos `.sql` vacíos** en `backups/` de la réplica. El agente no los abrió ni los borró (eliminar requiere consulta): los borra el desarrollador. Anotado como propuesta en `registro-pendientes.md` (fuera de alcance: toca `utils.py`).
- **Camino normal en local:** no verificado. Decisión del desarrollador (2026-10-26): no se instala el cliente de MySQL en su equipo. El camino normal se valida después del despliegue: generar un respaldo desde la aplicación y comprobar que se descarga.
- **Restauración real: no verificada en real.** Decisión del desarrollador (2026-10-26): no se hace en local ni en producción. La cubren las 7 pruebas con `mock` y la comprobación de los caminos de error en la réplica.
- **En producción nunca se provoca** un fallo de respaldo ni de restauración.
- **Archivos vacíos y pantallas:** los dos `.sql` vacíos de la réplica los borra el desarrollador. El diff no toca plantillas (los mensajes usan el bloque de `base.html`); la revisión visual en escritorio y a 360 px está a cargo del desarrollador.

## Diff

`git diff --stat`: `pedidos/views.py | 44 +++++++++++++++++++++++++++++++-------------` (31 inserciones, 13 eliminaciones), más el archivo nuevo `pedidos/tests/test_capturas_amplias.py`.

```diff
diff --git a/pedidos/views.py b/pedidos/views.py
index dc78ade..299cbbd 100644
--- a/pedidos/views.py
+++ b/pedidos/views.py
@@ -268,7 +268,9 @@ def editar_pedido(request, pk):
                             precio_unitario=int(item['precio_unitario'])
                         )
                 except Exception:
-                    pass
+                    # Supresión que descarta ítems: se corrige en 03-02. Mientras, queda en server.log.
+                    logger.exception('Error procesando items del pedido %s', pedido.pk,
+                                     extra={'request': request})
             registrar_evento('pedido_modificado', request.user, 'pedido', pedido.pk,
                              f'Pedido #{pedido.pk} modificado')
             # Redirigir al detalle del pedido editado
@@ -763,9 +765,10 @@ def crear_cotizacion(request):
                             cantidad=float(item['cantidad']),
                             precio_unitario=int(item['precio_unitario'])
                         )
-                except Exception as e:
-                    # En producción podrías loguear esto
-                    pass
+                except Exception:
+                    # Supresión que descarta ítems: se corrige en 03-02. Mientras, queda en server.log.
+                    logger.exception('Error procesando items de la cotización %s', cotizacion.pk,
+                                     extra={'request': request})
             # -------------------------------------------------------------
 
             # Redirigimos al detalle para revisar antes de "enviar"
@@ -808,7 +811,9 @@ def editar_cotizacion(request, pk):
                             precio_unitario=int(item['precio_unitario'])
                         )
                 except Exception:
-                    pass
+                    # Supresión que descarta ítems: se corrige en 03-02. Mientras, queda en server.log.
+                    logger.exception('Error procesando items de la cotización %s', cotizacion.pk,
+                                     extra={'request': request})
             return redirect('detalle_cotizacion', pk=pk)
     else:
         form = CotizacionForm(instance=cotizacion)
@@ -1125,8 +1130,11 @@ def generar_respaldo_bd(request):
         nombre_archivo = os.path.basename(ruta_archivo)
         response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
         return response
-    except Exception as e:
-        return HttpResponse(f"Error crítico: {str(e)}")
+    except Exception:
+        # El detalle técnico (salida de mysqldump, rutas) va solo a server.log.
+        logger.exception('Error al generar el respaldo', extra={'request': request})
+        messages.error(request, 'No se pudo generar el respaldo. El detalle quedó en el registro del servidor.')
+        return redirect('respaldar_bd')
 
 @login_required
 @user_passes_test(es_superusuario)
@@ -1149,6 +1157,7 @@ def restaurar_bd(request):
             messages.error(request, "Error: El archivo debe tener extensión .sql")
             return redirect('restaurar_bd')
 
+        respaldo_previo = None  # nombre del respaldo de emergencia, si llega a generarse
         try:
             # 3. Guardar el archivo temporalmente en 'backups/tmp/'
             # (Usamos FileSystemStorage para manejar la subida de forma segura)
@@ -1164,13 +1173,15 @@ def restaurar_bd(request):
             # EL AIRBAG: Respaldo de Emergencia Automático
             # ====================================================
             try:
-                generar_respaldo_mysql()  # Si esto falla, NO restauramos
-            except Exception as e:
+                respaldo_previo = os.path.basename(generar_respaldo_mysql())  # Si esto falla, NO restauramos
+            except Exception:
                 # Si no podemos hacer el respaldo de seguridad, ABORTAMOS la misión.
                 # Es mejor no restaurar que restaurar sin red de seguridad.
+                logger.exception('Error al crear el respaldo de seguridad previo a restaurar',
+                                 extra={'request': request})
                 if os.path.exists(ruta_absoluta): os.remove(ruta_absoluta)  # Limpieza
-                messages.error(request,
-                               f"Operación abortada: No se pudo crear el respaldo de seguridad previo ({str(e)}).")
+                messages.error(request, 'Operación cancelada: no se pudo crear el respaldo de seguridad '
+                                        'previo, así que la base no se tocó.')
                 return redirect('restaurar_bd')
 
             # ====================================================
@@ -1188,8 +1199,15 @@ def restaurar_bd(request):
             if os.path.exists(ruta_absoluta):
                 os.remove(ruta_absoluta)
 
-        except Exception as e:
-            messages.error(request, f"Error crítico al restaurar: {str(e)}")
+        except Exception:
+            # El detalle técnico (salida de mysql, rutas) va solo a server.log.
+            logger.exception('Error en la restauración de la base de datos', extra={'request': request})
+            mensaje = ('La restauración falló. La base puede haber quedado restaurada en parte: '
+                       'revisa el registro del servidor antes de seguir.')
+            if respaldo_previo:
+                mensaje += (f' El respaldo de seguridad previo es {respaldo_previo}. '
+                            'Está en la carpeta backups/ del servidor.')
+            messages.error(request, mensaje)
 
         return redirect('restaurar_bd')
```

## Hallazgos

- AUD-01-002 y AUD-02-006 **avanzan sin cerrarse**: el fallo queda registrado y sin texto técnico, pero la pérdida de ítems (03-02) y el GET de `generar_respaldo_bd` (04-01) siguen abiertos.
- Nuevo (pendiente registrado, sin implementar): `generar_respaldo_mysql()` deja un `.sql` vacío en `backups/` si `mysqldump` no existe en el PATH.
