# _planificacion · Guía de la documentación del proyecto

Esta carpeta contiene todo lo que un agente de IA o una persona necesita para saber **qué se construye, por qué, en qué orden y qué se hizo**. No contiene código ni se publica.

> Si este archivo discrepa con `00_producto/registro-pendientes.md` sobre el estado del trabajo, prevalece el registro. Sobre las reglas de la carpeta, prevalece este archivo.

---

## 1. Estructura

```text
_planificacion/
├── README.md                          Esta guía, sus reglas y las plantillas
├── 00_producto/
│   ├── producto.md                    Qué es el producto, para quién y qué no es
│   ├── registro-pendientes.md         Fuente única de verdad del trabajo pendiente
│   ├── decisiones.md                  Registro de Decisiones Arquitectónicas (RDA)
│   ├── auditoria-tecnica.md           Auditorías acumulativas y sus hallazgos
│   ├── plan-de-trabajo.md             Plan técnico por fases: el documento base
│   └── linea-base-produccion.md       Cifras medidas en producción (se crea al medir)
├── 10_epicas/
│   └── epica-XX-nombre/
│       ├── definicion-epica-XX.md
│       ├── iteracion-XX-YY-descripcion.md
│       └── evidencia-XX-YY.md         Solo si hizo falta pedir datos de producción
└── 99_bitacora/
    └── epica-XX-nombre/
        ├── bitacora-XX-YY.md
        └── bitacora-XX-YY-sufijo.md   Bitácoras adicionales de la misma iteración
```

## 2. Contenido de cada carpeta

### 2.1 `00_producto/`

Documentos vivos que describen el producto completo.

1. **`producto.md`:** propósito, qué es, qué no es, público, idioma y tono, indicadores de éxito e hitos. Cambia poco; se consulta ante dudas de alcance.
2. **`registro-pendientes.md`:** estado de épicas e iteraciones, datos pendientes del cliente, decisiones por tomar, propuestas fuera de alcance e historial. Es lo primero que se lee y lo último que se actualiza en cada iteración.
3. **`decisiones.md`:** cada decisión técnica relevante como RDA numerada.
4. **`auditoria-tecnica.md`:** auditorías acumulativas con sus hallazgos.
5. **`plan-de-trabajo.md`:** el plan técnico por fases que da origen a las épicas. Explica *qué* hacer en cada fase y *por qué*; las iteraciones dicen *cómo* y *con qué criterio* se da por hecho. No se reescribe: si el trabajo revela algo que el plan no anticipó, se registra como RDA o hallazgo, y el plan se actualiza solo con una fila en el historial del registro que lo explique.
6. **`linea-base-produccion.md`:** las cifras reales de producción (peso de la base, espacio en disco, volumen por tabla, respaldos, fecha de expiración). Toda optimización posterior se compara contra este archivo. Lleva fecha de medición en cada cifra y nunca datos personales.

### 2.2 `10_epicas/`

Una subcarpeta por épica, con nombre descriptivo en ASCII (`epica-00-blindaje/`). **Cada épica corresponde a una fase del plan de trabajo con el mismo número**, y cada iteración, a una subfase: la iteración `00-03` es la subfase 0.3. Cada una contiene su definición, sus iteraciones y, solo si fue necesario, los archivos de evidencia de producción.

### 2.3 `99_bitacora/`

Una subcarpeta por épica, con el mismo nombre que la carpeta de la épica en `10_epicas/`. Dentro, las bitácoras de sus iteraciones.

## 3. Convenciones

- **Numeración:** épicas `00`–`99`, con el mismo número que la fase del plan; iteraciones `XX-YY`, donde `XX` es la épica e `YY` el número de la subfase. Una iteración que no existía en el plan toma el siguiente correlativo libre de su épica.
- **Nombres de archivo y carpeta:** minúsculas, guiones y solo caracteres ASCII, sin tildes ni ñ (`epica-03-integridad-transaccional/`). El contenido sí lleva tildes y ñ.
- **Iteraciones:** `iteracion-XX-YY-descripcion-corta.md`.
- **Bitácoras:** `bitacora-XX-YY.md` para la primera de la iteración; las siguientes llevan un sufijo descriptivo (`bitacora-XX-YY-correccion.md`, `bitacora-XX-YY-produccion.md`) y, si el sufijo se repite, un número (`bitacora-XX-YY-ajustes-2.md`). La fecha va dentro del archivo, no en el nombre.
- **Estados:** `Pendiente`, `En curso`, `Bloqueada`, `En revisión`, `Terminada`, `Descartada`.
- **Fechas:** formato ISO `AAAA-MM-DD`, hora de Chile continental.
- **Idioma:** español de Chile en toda la documentación.
- **Ramas:** rama única `main`. Una rama existe solo si el desarrollador la pide, con el formato `iteracion/XX-YY-descripcion-corta`.
- **Etiquetas:** cada estado desplegado en producción lleva una etiqueta anotada, creada por el desarrollador antes del despliegue, con el formato definido en `docs/operacion/despliegue.md`.
- **Commits:** `Épica N - Iteración NN-NN: descripción`, una línea de máximo 200 caracteres (por ejemplo `Épica 0 - Iteración 00-04: excluye .idea y fija requirements.txt en UTF-8`). Los hace solo el desarrollador.
- **Clases de cambio de esquema:** toda iteración que crea una migración declara su clase (1, 2 o 3) según `AGENTS.md` y copia en la bitácora el SQL que entrega `sqlmigrate`. La Clase 3 está prohibida.
- **Marcadores de datos faltantes:** `PENDIENTE_CLIENTE` (datos del negocio) y `PENDIENTE_DESARROLLADOR` (decisiones técnicas o de diseño). Todo marcador se registra en `registro-pendientes.md`.

## 4. Ciclo de una iteración

1. El desarrollador marca la iteración como `En curso` en `registro-pendientes.md` (o pide al agente que lo haga).
2. El agente lee `AGENTS.md`, el registro, la iteración, la subfase correspondiente de `plan-de-trabajo.md` y las RDA relacionadas.
3. El agente ejecuta **la iteración completa en local**: implementa, verifica contra la réplica local y escribe la bitácora.
4. Si un criterio de aceptación depende de producción (PythonAnywhere, datos reales, registro del servidor), el agente prepara los pasos exactos en un archivo de evidencia (sección 5.5). El agente nunca accede a producción.
5. El agente deja la iteración en `En revisión` e indica si el despliegue necesita respaldo previo y qué migraciones incluye, con su clase.
6. El desarrollador revisa, hace commit y push, descarga y verifica el respaldo si corresponde, crea la etiqueta y despliega.
7. Si quedan criterios que se verifican en producción, el desarrollador responde la evidencia y el agente consolida en `bitacora-XX-YY-produccion.md`.
8. El desarrollador marca la iteración como `Terminada` solo cuando **todos** sus criterios están verificados, incluidos los de producción. Una subfase a medias en un sistema en producción es peor que no haberla empezado.

## 5. Reglas de mantenimiento

### 5.1 Registro de pendientes

- El historial lleva **una fila por cambio y una sola línea**, con enlace a la bitácora que tiene el detalle. Las mediciones, decisiones y salvedades van en la bitácora, no en el historial.
- Nada se borra. Si un cambio anterior queda sin efecto, se agrega una fila nueva que lo dice.
- La tabla de estado enlaza todas las bitácoras de cada iteración.

### 5.2 Decisiones (RDA)

- Numeración correlativa: `RDA-001`, `RDA-002`… Antes de crear una, revisa el último número usado.
- Una RDA aceptada no se contradice: se reemplaza con una nueva que la declare «Reemplazada por RDA-XXX» (o «Reemplazada parcialmente»), y la antigua recibe una línea que remite a la nueva.
- Las actualizaciones van al final de la RDA como «**Actualización AAAA-MM-DD:** …», breves. Si una RDA acumula varias actualizaciones de fondo, se reemplaza con una nueva.
- La tabla índice del inicio del archivo se mantiene al día.

### 5.3 Auditorías

- Las auditorías se agregan al final y nunca se borran ni se reescriben.
- **Antes de agregar una auditoría, busca el último número usado en el archivo y suma uno.** Los IDs de hallazgo tienen el formato `AUD-NN-MMM` (auditoría y correlativo) y nunca se reutilizan.
- Un hallazgo se cierra indicando dónde: «Resuelto en XX-YY» o «Resuelto en RDA-XXX», con la evidencia mínima. «Riesgo aceptado» solo si el desarrollador lo aceptó y consta dónde.
- Severidad: Alta (bloquea la publicación o afecta al usuario o al negocio), Media (afecta calidad o rendimiento), Baja (mejora).

### 5.4 Bitácoras

- Se escriben al terminar cada tramo de trabajo, con la plantilla de la sección 6.2.
- No se editan después de entregadas: las correcciones van en una bitácora nueva con sufijo.
- Registran mediciones reales. «Verificado» sin decir cómo y dónde no cuenta.
- Una casilla de criterio se marca solo si se midió.

### 5.5 Evidencia de producción

**Por defecto, una iteración se ejecuta completa y sin fases.** El agente resuelve todo lo que se puede resolver en local, con la réplica local restaurada desde un respaldo real de producción.

En este proyecto el agente tiene **prohibido** acceder a PythonAnywhere y a la base de producción (`AGENTS.md`, sección 6). Por eso el archivo de evidencia es el único canal con producción, y corresponde cuando se cumplen las dos condiciones:

1. Un criterio de aceptación depende de información que solo existe en producción: cifras del servidor, el registro de uWSGI, el panel de PythonAnywhere, el comportamiento de la aplicación publicada o una medición después del despliegue.
2. El agente comprobó que esa información no se puede obtener ni reproducir en local (la réplica, los registros versionados, la documentación pública de PythonAnywhere).

Pedir evidencia sigue siendo trabajo para el desarrollador: el agente agrupa en un solo archivo todo lo que necesita de producción para la iteración, con comandos listos para copiar y el formato exacto de la respuesta.

En ese caso, el agente:

1. Termina y registra en la bitácora todo lo que sí pudo hacer.
2. Crea `10_epicas/<epica>/evidencia-XX-YY.md` con la plantilla de la sección 6.3, que incluye **qué intentó y por qué no pudo**. Sin esa sección el pedido no es válido.
3. Pide solo los datos que faltan, con pasos exactos y el menor esfuerzo posible para el desarrollador.
4. Deja la iteración en `En revisión` y avisa.
5. Cuando el desarrollador responde en el archivo de evidencia, consolida en una bitácora nueva (`bitacora-XX-YY-produccion.md`).

## 6. Plantillas

### 6.1 Iteración

```markdown
# Iteración XX-YY · Nombre

- **Épica:** XX · Nombre
- **Estado:** Pendiente
- **Subfase del plan:** X.Y
- **Depende de:** XX-YY
- **RDA relacionadas:** RDA-XXX
- **Hallazgos que cierra:** AUD-NN-MMM
- **Cambio de esquema:** Ninguno | Clase 1 | Clase 2
- **Respaldo previo al despliegue:** Sí | No

## Objetivo

Una o dos frases.

## Tareas

1. …

## Criterios de aceptación

- [ ] … (verificable con una medición o un comando)

## Fuera de alcance

- …

## Datos requeridos del cliente

- …
```

### 6.2 Bitácora

```markdown
# Bitácora XX-YY · Nombre de la iteración

- **Fecha:** AAAA-MM-DD
- **Agente:** (herramienta y modelo)
- **Estado final:** En revisión | Bloqueada

## Resumen

Qué se hizo, en tres a cinco líneas.

## Archivos creados o modificados

| Archivo | Cambio |
| :------ | :----- |

## Verificación

- (comando o medición): resultado
- Pruebas: `python manage.py test pedidos` → N pruebas, resultado
- Revisión de pantallas en escritorio y a 360 px contra la réplica local: …

## Migraciones

- Ninguna | `NNNN_nombre.py` · Clase N · SQL de `sqlmigrate`:

```sql
(salida de sqlmigrate)
```

## Criterios de aceptación

- [x] … (con la medición que lo respalda)

## Decisiones tomadas

- … (si es estructural, enlaza la RDA nueva)

## Pendientes y riesgos

- …

## Commit sugerido

`Épica N - Iteración NN-NN: descripción`
```

### 6.3 Evidencia de producción

```markdown
# Evidencia XX-YY · Nombre de la iteración

- **Fecha del pedido:** AAAA-MM-DD
- **Pedido por:** (agente)
- **Criterios que dependen de esta evidencia:** …

> Este archivo existe solo porque el agente no pudo obtener estos datos por su cuenta. Responde solo lo que se pide.

## Qué intentó el agente

| Dato | Qué intentó en local | Por qué se necesita producción |
| :--- | :---------- | :-------------- |

## Qué necesito del desarrollador

### 1. (dato)

- **Para qué:** criterio o hallazgo que cierra.
- **Cómo obtenerlo:** pasos exactos.
- **Respuesta:**

## Lo que no se pudo verificar

- …
```

### 6.4 RDA

```markdown
## RDA-XXX · Título

- **Fecha:** AAAA-MM-DD
- **Estado:** Propuesta | Aceptada | Reemplazada por RDA-XXX | Descartada

**Contexto:** qué problema o fuerza obliga a decidir.
**Decisión:** qué se hace.
**Alternativas consideradas:** qué se descartó y por qué.
**Consecuencias:** qué se gana, qué se pierde y qué hay que vigilar.
```

### 6.5 Hallazgo de auditoría

```markdown
| ID | Severidad | Área | Hallazgo | Acción recomendada | Estado |
| :- | :-------- | :--- | :------- | :----------------- | :----- |
| AUD-NN-MMM | Alta / Media / Baja | … | … | … | Abierto / Resuelto en XX-YY o RDA-XXX |
```
