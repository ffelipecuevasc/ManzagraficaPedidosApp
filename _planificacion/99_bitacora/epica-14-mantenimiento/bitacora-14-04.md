# Bitácora 14-04 · RUT del cliente y folio de cotización

- **Fecha:** 2026-11-20
- **Estado de la iteración:** Pendiente (redactada, decisiones resueltas). **Solo Fase 1 (documentación).** La Fase 2 no empezó.
- **Commit base:** `6b79f63` (`main`, `git status` limpio).

## Verificación previa (cláusula de control)

| Punto | Resultado | Por qué importa |
| :---- | :-------- | :-------------- |
| `git status` | Limpio, sobre `6b79f63` (04-07 sin desplegar) | La iteración parte de un punto conocido |
| Última migración | `0008_proteger_historial_cliente.py`. **La `0009` de la 04-08 no existe** | Si esta iteración tomara la `0009`, el orden de las migraciones y el de los despliegues (04-08 antes que 14-04) dejarían de coincidir. Por eso me detengo después de la Fase 1, como pide la cláusula |
| Iteración libre | **14-04** (14-03 no se reasigna, RDA-022, punto 4) | Reasignar un número sin uso exige excepción explícita del desarrollador |
| RDA libre | **RDA-024** | La última es la RDA-023 |
| Etiqueta libre | **`v14.3-rut-y-folio`** (propuesta) | La última de la fase 14 es `v14.2-duplicar-items`; cada fase sigue sin saltos |

## Qué documenté y por qué

- **RDA-024 (enmienda a la RDA-022, sin borrarla).** El pedido del cliente no es una falla: no tiene gravedad ni AUD. Sin una RDA, meterlo en la Épica 14 contradiría la RDA-022, que la define para fallas. Fijé un criterio verificable de «mejora puntual» (cuatro condiciones) para que la épica no se vuelva un cajón de sastre: lo que necesite rediseño o dependa de las Épicas 07 u 08 sigue yendo a la Épica 10.
- **Carpeta sin renombrar.** Renombrar rompe los enlaces de bitácoras ya entregadas, que no se editan. El nombre corto «mantenimiento» sigue siendo verdadero.
- **Definición de la épica:** título, objetivo, «Cómo funciona», tabla de iteraciones, fuera de alcance y notas. Lo anterior quedó tachado, no borrado.
- **Iteración 14-04** con la plantilla de la 14-02.
- **Registro:** fila de la iteración, hito 5, dos decisiones por tomar, propuesta de la columna RUT y una fila de historial.

## Hallazgo al redactar: la migración del folio choca con la regla 8.1

El pedido define tres migraciones: (1) `folio` nulo y tabla contador; (2) datos; (3) `folio` obligatorio y único. La tercera **impone obligatoriedad sobre una columna existente**, que es literalmente la Clase 3 de `AGENTS.md` 8.1 (prohibida), aunque en la práctica no destruye nada: la columna se creó en la misma iteración y todas las filas ya tienen valor. No la reclasifiqué por mi cuenta: la regla dice «detente y replantea». Opciones para el desarrollador:

- **A.** Aceptarla como excepción explícita (la columna nació en esta misma iteración y nunca estuvo en producción sin valor), registrada en la RDA-024 o en una RDA propia.
- **B.** Dejar `folio` nulo y único en la base (`unique=True, null=True`; MySQL admite varios `NULL` en un índice único) y garantizar el valor en `save()` y con una prueba. Todo queda Clase 2; el costo es que la base no impide un folio vacío.
- **C.** Crear la columna directamente obligatoria en la `0010` con un valor provisional y rellenarla en la misma migración. No sirve con `unique`: todas las filas tendrían el mismo valor provisional antes del relleno.

~~Mi recomendación: **B**, porque respeta la regla sin excepciones y el único camino de escritura (`save()`) queda cubierto por pruebas.~~

**Decisión del desarrollador (2026-11-20): opción C, en su versión:** `folio` nace obligatorio con un valor transitorio en la `0010` (sin `unique`), la `0011` lo rellena con `folio = id` y la `0012` agrega **solo** el índice único. Así ninguna migración impone obligatoriedad sobre una columna existente: la obligatoriedad nace con la columna, y el índice es aditivo. El índice no puede ir en la `0010` porque, hasta el relleno, todas las filas comparten el valor transitorio. Se confirma con `sqlmigrate` al implementar; si algún paso resulta Clase 3, me detengo y vuelvo a preguntar.

**Por qué el RUT es Clase 2:** `Cliente.rut` es una columna **nueva** que nace `NOT NULL` con relleno (`00.000.000-0`) en el mismo `ALTER TABLE … ADD COLUMN`; `preserve_default=False` solo quita el valor por defecto del estado de Django (no deja `DEFAULT` en MySQL tras la migración, lo que se confirma con `sqlmigrate`). No se cambia tipo ni obligatoriedad de nada que ya existiera.

**Orden con la 04-08 (decisión del desarrollador, 2026-11-20):** esperar a que la `0009` esté en `main`.

## Documentos protegidos (propuesta, no editados)

- **`_planificacion/README.md`, línea 112** (severidades). Texto actual: «…las Media y Baja, en la Épica 14, agrupadas por tema.» Propuesto: «…las Media y Baja, en la Épica 14, agrupadas por tema. La Épica 14 recibe también mejoras puntuales que cumplen el criterio de la RDA-024.» Por qué: sin la frase, un lector de la guía entiende que la Épica 14 solo recibe fallas. Si no se hace, el criterio vive solo en la RDA-024 y en la definición de la épica.
- `AGENTS.md` y `README.md` no describen la Épica 14 (verificado con búsqueda). `plan-de-trabajo.md` no se reescribe (su fila de la Épica 14 ya está superada por la RDA-022).

## Qué no pude ver y qué puede ir desactualizado

No leí todavía, completos, `views.py`, `forms.py`, las plantillas de cotización y de clientes, `index.js`, `verificar_respaldo.py` ni los documentos de operación, porque la Fase 2 no empieza. Lo verificado: `Cliente.telefono` y `email` (`models.py:10-11`), `USE_THOUSAND_SEPARATOR = True` (`settings.py:255`), que el admin no registra `Cotizacion` (`admin.py`) y que las cotizaciones no se crean con `Cotizacion(` ni `Cotizacion.objects.create` (se crean vía formulario). Los nombres de vistas del alcance salen del pedido del desarrollador y se confirman al implementar. La 04-08 puede cambiar `forms.py` y la numeración antes de que esta iteración empiece.
