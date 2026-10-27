# Bitácora 02-cierre-epica · Cierre de la Épica 02 · Red de seguridad

- **Fecha:** 2026-10-27
- **Agente:** Claude Code (Claude Opus 5.5)
- **Estado final:** Terminada (la Épica 02, con su criterio de término marcado)

## Resumen

La Épica 02 se cierra por decisión del desarrollador del 2026-10-27, con su criterio de término cumplido:

- 184 pruebas, de las cuales 165 están en verde y 19 son regresiones que fallan a propósito, de forma reproducible.
- `docs/operacion/pruebas.md` lista cada regresión con su hallazgo y la iteración que la volverá verde.
- El comando de pruebas ya está en `despliegue.md`.

La épica no despliega nada por sí misma: sus pruebas llegan al servidor con `v1.2` y allí no se ejecutan. Solo cambian archivos `.md`.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-02-red-seguridad/definicion-epica-02.md` | Estado «Terminada (2026-10-27)» (corrige además la línea de estado, que había quedado mal redactada en el cierre de la 02-05); criterio de término marcado con evidencia; sección «Resultados de la épica»; nota del cierre |
| `_planificacion/00_producto/registro-pendientes.md` | Próximo hito; épicas terminadas y en curso; tarea del domingo 2026-11-01 en la fila de la 01-06; historial |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-cierre-epica.md` | Esta bitácora |
| `_planificacion/99_bitacora/epica-02-red-seguridad/bitacora-02-cierre-carpetas-antiguas.md` | Informe de las carpetas anteriores a RDA-014 |

## Verificación

- `python manage.py test pedidos -v 2`, una ejecución de control:

```text
Found 184 test(s).
Ran 184 tests in 166.474s
OK (expected failures=19)
```

- Evidencia del criterio de término, del cierre de la 02-05: tres ejecuciones con `Ran 184 tests` y `OK (expected failures=19)`; `--exclude-tag regresion`: 165 en `OK`; `--tag regresion`: 19 fallos esperados.
- `docs/operacion/pruebas.md`, sección 7.1: 19 filas (R1 a R4, R6a a R6c, R7 a R15, R18 a R20), cada una con su hallazgo y la iteración que la volverá verde. «Valor vigente: `expected failures=19`».
- Recuento de 19: `pruebas.md` (7.1), `iteracion-02-04-regresiones.md` («Recuento vigente: 19»), `definicion-epica-02.md` (alcance y resultados) y registro (historial del cierre de la 02-05 y de la épica). Las menciones a 17 y 18 que quedan son notas fechadas de su momento.
- `git status --short` y `git diff --stat`: solo archivos `.md`.

## Migraciones

- Ninguna.

## Criterios de aceptación

- [x] Criterio de término de la épica: las cuatro casillas marcadas, con su evidencia, en `definicion-epica-02.md`.

## Decisiones tomadas

Decisiones del desarrollador del 2026-10-27:

- **Cierre:** la Épica 02 se cierra ahora; su criterio de término está cumplido. No despliega nada por sí misma; sus pruebas llegan al servidor con la próxima etiqueta (`v1.2`) y allí no se ejecutan.
- **Numeración:** lo escrito antes de RDA-014 no se reescribe. Toda referencia **nueva** usa la numeración vigente con la anterior entre paréntesis, por ejemplo «07-02 (antes 06-05)». R15 queda con «06-05» en los documentos ya escritos. La sección «Resultados de la épica» aplica la regla.
- **AUD-02-028 (R19):** sigue `PENDIENTE_DESARROLLADOR`.
- **Épica 03:** no puede empezar hasta cerrar la Épica 01. Su precondición, «Épicas 01 y 02 completas», no es negociable; anotado en el registro.

## Lecciones técnicas observadas

- **Oráculo del IVA (02-02).** Comparar el cálculo de la aplicación con un oráculo independiente (`Decimal`, redondeo comercial) encontró lo que una tabla de casos a mano no habría mostrado: `round()` de Python redondea las mitades al par, con $1 de diferencia en 500 de los 100.001 valores netos entre 0 y 100.000. Por decisión del desarrollador quedó solo anotado en AUD-02-015. La lección: los oráculos se escriben sin reutilizar el código que prueban (el de `estado_pago` suma los pagos en Python, sin usar las propiedades del modelo).
- **R5 no confirmada (02-04).** Ejecutar cada regresión sin la marca antes de declararla evitó registrar un defecto falso. La comprobación de métricas duplicadas sí funciona dentro del mismo día; el duplicado solo aparece a las 22:00 de Chile, por el día en UTC, y eso ya lo cubre R8. La misma disciplina confirmó R18, que se había sospechado solo leyendo el código. Además, el parche de la hora debe devolver un instante en UTC, igual que el reloj real con `USE_TZ`: con la zona de Chile, `.date()` habría escondido el defecto.
- **`cerrar_respuesta` y el aislamiento entre pruebas (02-05).** `respuesta.close()` de un `FileResponse` emite `request_finished`, que cierra la conexión dentro de la transacción de `TestCase` y la deja marcada para revertir. La prueba que lo hace pasa; la **siguiente** falla con `TransactionManagementError`. R6c tenía el problema latente y no se notaba porque era la última de su clase. La ayuda desconecta `close_old_connections` mientras cierra, igual que el cliente de pruebas de Django. Un efecto parecido apareció en R18: un `ValidationError` dentro de `save_base` deja la transacción de la prueba marcada para revertir, así que la prueba comprueba la respuesta antes de consultar la base. La lección: el orden de las aserciones y de las pruebas importa cuando el código bajo prueba rompe la transacción.
- **El decorador convierte el 404 en 500 (02-05, AUD-02-029).** `@transaccion_segura` captura `Exception`, y `Http404` lo es. En las 12 vistas que lo usan, un `pk` inexistente responde 500 y deja una traza en el registro de errores, mientras las 6 vistas sin el decorador responden 404. Una captura amplia en un decorador también se traga las respuestas HTTP que Django espera recibir como excepción. La 03-01 (rediseño del decorador) tiene a R20 como prueba de aceptación.

## Pendientes y riesgos

- **Épica 01:** parte D de la 01-06 y despliegue de `v1.2`. Al prepararlo, comprobar que `despliegue.md` acepta `expected failures=19` (anotado en la fila de la 01-06 del registro).
- **Discrepancias encontradas** (no corregidas):
  - `iteracion-02-04-regresiones.md:54` dice «R10 a R12, R15, R18 y R19, una cada una», y el criterio de aceptación (`:72`) dice «R1 a R15, R18 y R19». Ninguno nombra R20, aunque el recuento vigente (19) sí la incluye.
  - `definicion-epica-02.md`, alcance 4: menciona «métricas duplicadas» entre las regresiones del plan; la misma frase aclara que R5 no se confirmó.
  - El criterio de término de la Épica 06 vigente cita una regresión «de métricas duplicadas» que no existe (ver el informe de carpetas).
  - El registro llama a la próxima etiqueta `v1.2-capturas` (historial del 2026-10-26) y esta decisión la llama `v1.2`.
- **AUD-02-028:** iteración que lo corrige, `PENDIENTE_DESARROLLADOR`.

## Commit sugerido

`Épica 2 - Cierre: termina la épica con 184 pruebas (19 regresiones), agrega los resultados y el informe de las carpetas anteriores a RDA-014`
