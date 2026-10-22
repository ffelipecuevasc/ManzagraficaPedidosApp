# Bitácora 00-05 · Ensayo de retroceso y ajustes de la parte B

- **Fecha:** 2026-10-22
- **Agente:** Claude Code (Opus 5.5)
- **Estado final:** En revisión (falta el despliegue de 00-04, parte B)

## Resumen

- **Ensayo aprobado.** El desarrollador ejecutó la parte A en `manzagrafica_replica` el 2026-10-22 y el agente revisó las salidas: el retroceso del caso 2 tardó 1,31 minutos.
- **Parte B reordenada:** `v0.0-inicial` se crea y se publica en B5, justo después de anotar el commit de producción en B4 y antes de tocar el servidor. Antes iba en B10, al final.
- **`PROYECTO` y `VENV`:** los comandos del servidor usan los mismos valores que `scripts/diagnostico/linea_base.sh`, con una línea que los comprueba.
- **Numeración:** cada fase parte en `.1`; `v0.0-inicial` es el estado de partida. Lo decidió el desarrollador.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |
| `_planificacion/10_epicas/epica-00-blindaje/evidencia-00-05.md` | Revisión de la parte A; B4 a B11 reordenados (antes B4 a B11 con la etiqueta en B10); fila de `v0.0-inicial` en la lista de B2. |
| `docs/operacion/despliegue.md` | Sección 0 con `PROYECTO` y `VENV`; `v0.0-inicial` en el paso 3.1; correlativo desde `.1`; sección 4 reordenada. |
| `docs/operacion/retroceso.md` | `PROYECTO` y `VENV` en los comandos; fila del ensayo en el registro de retrocesos. |
| `_planificacion/10_epicas/epica-00-blindaje/iteracion-00-05-protocolo-despliegue.md` | Criterios 3 y 4 marcados. |
| `_planificacion/00_producto/registro-pendientes.md` | Numeración aprobada, enlace a esta bitácora e historial. |
| `_planificacion/99_bitacora/epica-00-blindaje/bitacora-00-05-ensayo.md` | Esta bitácora. |

## Verificación (salidas del desarrollador en `evidencia-00-05.md`, parte A)

| Criterio | Antes (A2) | Después (A6) | Resultado |
| :------- | :--------- | :----------- | :-------- |
| `showmigrations pedidos` | `0001` a `0006` con `[X]` | `0001` a `0006` con `[X]` | Igual |
| Tabla `ensayo_retroceso` y filas `0007` en `django_migrations` | `tabla: False \| filas 0007: 0` | `tabla: False \| filas 0007: 0` | Igual |
| Tiempo del retroceso (A5) | — | 1,31 minutos | Menos de 15 |
| `0007` en `git status --short` y en `pedidos/migrations/` (incluido `__pycache__`) | — | Sin salida en ambos | Cumple |
| Etiqueta `ensayo-retroceso` | Creada en A3, sin `push` | `Deleted tag`; `git tag -l "ensayo-*"` vacío | Cumple |

- **Durante el ensayo (A4):** `[X] 0007_ensayo_retroceso` y `tabla: True | filas 0007: 1`. Así se comprueba que la migración se aplicó y que el retroceso la deshizo.
- **Orden del caso 2:** `migrate pedidos 0006` se ejecutó con el archivo todavía presente (`Unapplying ... OK`). Después se borró el archivo y se hizo `checkout` de la etiqueta. `check` quedó sin problemas y `migrate --plan` respondió `No planned migration operations.`
- **Commit del ensayo:** `8b492f8`, la punta de `main`, con el árbol limpio.
- **`mysql.W002`** en cada `migrate`: es el `sql_mode` de producción, decidido en 00-03 (AUD-02-020). No es un hallazgo nuevo.

## Migraciones

- `0007_ensayo_retroceso.py`, temporal y sin versionar. Es **Clase 2**: tabla nueva, ya borrada. SQL de `sqlmigrate pedidos 0007`:

```sql
--
-- Raw SQL operation
--
CREATE TABLE ensayo_retroceso (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY) ENGINE=InnoDB;
```

## Criterios de aceptación

- [x] Ensayo medido en menos de 15 minutos, con `showmigrations` igual antes y después: 1,31 minutos; A2 y A6 son idénticos.
- [x] Migración temporal ausente de `git status` y de `pedidos/migrations/`: A6, sin salida.
- [ ] Etiqueta del despliegue de 00-04 en `git tag -n` y lista completada: pendiente de la parte B.

## Decisiones tomadas

- **Numeración (desarrollador, 2026-10-22):** cada fase parte en `.1`, y `v0.0-inicial` es la etiqueta del estado de partida.
- **`v0.0-inicial` antes de tocar el servidor (desarrollador):** pasa de B10 a B5. En `despliegue.md` queda en el paso 3.1, para que el retroceso siempre tenga destino antes del `checkout`.

## Pendientes y riesgos

- **La medición cubre la base y el código en local.** En producción se suman la consola y la recarga. El margen sigue siendo amplio, pero la cifra real solo se conoce con un retroceso real. El ensayo de recuperación ante desastres es la 07-04.
- **Casos 1 y 3:** el caso 1 está contenido en el caso 2. El caso 3 no se ensayó en esta iteración: su restauración por consola se probó en la réplica en 00-03 (4,17 s), y la restauración con la función de la aplicación no se ha probado.
- **Etiqueta local `fase0-linea-base-2026-10-20`:** tiene el formato anterior. B5 pide comparar su commit con el de producción antes de decidir qué hacer con ella.
- **Docker Desktop:** el primer `docker compose up -d` falló con un error 500 mientras Docker Desktop arrancaba; el segundo intento funcionó.

## Commit sugerido

`Épica 0 - Iteración 00-05: aprueba el ensayo de retroceso (1,31 min), crea v0.0-inicial antes de tocar el servidor y usa PROYECTO y VENV de linea_base.sh`
