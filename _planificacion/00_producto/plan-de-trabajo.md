# Plan de Trabajo Técnico — ManzagraficaPedidosApp

**Proyecto:** Sistema de gestión de pedidos, cotizaciones y pagos
**Stack:** Python 3.13 · Django 6.0 · MySQL 8.0 · uWSGI · PythonAnywhere (plan gratuito)
**Naturaleza:** Aplicación monolítica en producción, con datos reales acumulados durante meses
**Documento:** Plan de refactorización, endurecimiento y profesionalización
**Alcance:** 100% conceptual — este documento define *qué* hacer y *por qué*, no *cómo* escribirlo

---

## 1. Contexto y principio rector

Esta aplicación no es un proyecto nuevo. Está viva, tiene usuarios, y su base de datos contiene el historial comercial real de una imprenta: clientes, pedidos, cotizaciones y pagos acumulados durante meses. Cualquier plan de mejora que ignore ese hecho es un plan irresponsable.

De ahí el principio que gobierna todo el documento:

> **Ningún cambio llega a producción sin haber sido ejecutado antes contra una copia real de esos mismos datos, y ninguna fase avanza sin un punto de retorno verificado.**

Esto tiene una consecuencia práctica que conviene interiorizar desde ya: **la Fase 0 no es preparación, es trabajo real**. Es la fase que hace que las seis siguientes sean seguras. Saltársela para "empezar a programar antes" es el error más caro que se puede cometer en un proyecto en producción.

### 1.1. Restricciones inamovibles de la plataforma

Estas condiciones del plan gratuito de PythonAnywhere no son negociables y condicionan varias decisiones de diseño. Se listan aquí para que ninguna fase las contradiga por descuido.

| Restricción | Implicación para el plan |
|---|---|
| 512 MiB de disco total, compartido entre archivos y almacenamiento MySQL | Los respaldos, los logs y los datos de negocio compiten por el mismo espacio. Toda tabla nueva necesita política de purga desde su diseño. |
| Una sola tarea programada diaria | Métricas, purga de logs y respaldo deben orquestarse en un único script. |
| Un solo worker uWSGI, un core, sin hilos | Las peticiones se atienden en serie. Cualquier operación lenta bloquea a todos los usuarios. |
| Acceso saliente restringido a lista blanca | Servicios externos de monitoreo (Sentry y equivalentes) quedan descartados. La observabilidad debe ser local. |
| Hibernación tras inactividad prolongada | El arranque en frío es inevitable; solo se puede abaratar, no eliminar. |
| Expiración de la web app al mes sin actividad de la cuenta | Existe riesgo real de apagado silencioso. Requiere rutina de operación explícita. |
| 100 CPU-segundos diarios para consolas y tareas programadas | El script de mantención debe ser eficiente. No aplica a las peticiones web. |

### 1.2. Registro de decisiones adoptadas

Estas nueve decisiones fueron tomadas antes de redactar el plan y explican por qué el documento toma ciertos caminos y descarta otros. Se dejan asentadas para que un lector futuro (o tú mismo en seis meses) entienda el razonamiento sin tener que reconstruirlo.

| # | Decisión | Camino elegido | Motivo |
|---|---|---|---|
| D1 | Entorno de pruebas | Réplica local con volcado real de producción | Máxima fidelidad; los bugs detectados solo se manifiestan con historia acumulada |
| D2 | Cambios de esquema autorizados | Clase 1 (metadatos) y Clase 2 (aditivos e índices). Clase 3 prohibida | Permite mejoras sin riesgo de pérdida de datos |
| D3 | Plan de hosting | Gratuito, con tarea diaria heredada | Define las restricciones de la tabla anterior |
| D4 | Observabilidad | Tablas propias en MySQL para errores y eventos, con respaldo obligatorio a salida estándar | Control total y trazabilidad forense; la lista blanca descarta servicios externos |
| D5 | Motor de pruebas | MySQL en Docker, idéntico a producción | El código depende de particularidades reales de MySQL |
| D6 | Flujo de trabajo | Rama principal única con etiquetas antes de cada despliegue | Simplicidad para desarrollador individual, con retroceso garantizado |
| D7 | Alcance del registro de eventos | Errores más eventos de negocio críticos | Auditoría útil sin coste por petición de lectura |
| D8 | Uso de la tarea programada | Script único de mantención diaria orquestando tres responsabilidades | La plataforma solo concede una ranura |
| D9 | Compilación de estilos | Tailwind CSS v3 compilado localmente mediante pnpm | Elimina 400 KB de JavaScript en producción; pnpm reduce exposición a ataques de cadena de suministro |

### 1.3. Reglas de oro transversales

Aplican a todas las fases sin excepción.

1. **Respaldo descargado antes de cada despliegue que toque datos.** No basta con el respaldo que queda en el servidor: vive en el mismo disco que puede fallar.
2. **Una etiqueta de versión en el repositorio antes de cada actualización de producción.** Es el botón de retroceso.
3. **Un despliegue, un propósito.** No se mezclan correcciones de fases distintas en la misma subida.
4. **Ninguna subfase se da por terminada sin su criterio de salida verificado.**
5. **Todo cambio de esquema se ensaya primero contra la réplica local restaurada desde producción.**
6. **Si una corrección requiere un cambio de Clase 3, se detiene y se replantea.** No se improvisa sobre datos reales.
7. **Las dependencias se fijan con versión exacta.** Sin rangos abiertos, ni en Python ni en el ecosistema de Node.

### 1.4. Clasificación de cambios de base de datos

Vocabulario común usado en todo el documento.

- **Clase 1 — Metadatos.** Etiquetas legibles, textos de ayuda, opciones de selección, ordenamiento por defecto, nombres de relación inversa. Django genera un archivo de migración, pero MySQL no ejecuta ninguna alteración de tabla. Riesgo nulo. **Autorizado.**
- **Clase 2 — Aditivo no destructivo.** Creación de índices, tablas nuevas, o columnas que admiten valor nulo. Sí ejecuta una alteración de tabla, pero no destruye información y es reversible. Riesgo bajo con el volumen actual. **Autorizado, con respaldo previo.**
- **Clase 3 — Destructivo o alterador.** Renombrar, eliminar, cambiar tipo de dato, imponer obligatoriedad sobre una columna existente. Riesgo real de pérdida. **Prohibido en este plan.**

---

## 2. Mapa de fases

| Fase | Nombre | Naturaleza | Esfuerzo relativo | Bloquea a |
|---|---|---|---|---|
| 0 | Blindaje y punto de retorno | Habilitante | Medio | Todas |
| 1 | Observabilidad | Habilitante | Alto | 3, 4, 6 |
| 2 | Red de seguridad | Habilitante | Alto | 3, 5 |
| 3 | Integridad transaccional | Correctivo crítico | Medio | — |
| 4 | Seguridad y endurecimiento | Correctivo | Medio | — |
| 5 | Rendimiento | Optimización | Medio | — |
| 6 | Arquitectura y automatización | Estructural | Alto | — |
| 7 | Operación continua | Sostenimiento | Bajo, recurrente | — |

**Sobre el orden.** Puede sorprender que la corrección crítica de integridad transaccional aparezca en tercer lugar y no en primero. La razón es deliberada: refactorizar el manejo de transacciones sin observabilidad significa no enterarse si la corrección introduce un fallo nuevo, y hacerlo sin pruebas automatizadas significa no poder verificar que el comportamiento correcto se conservó. **La red de seguridad va antes del salto.** Este es probablemente el hábito profesional más importante que este plan pretende instalar.

Existe una excepción pragmática: hay un conjunto de correcciones triviales, de riesgo casi nulo y beneficio inmediato, que no justifican esperar seis fases. Se agrupan en la subfase 0.6 como un despliegue temprano y aislado.

---

## FASE 0 — Blindaje y punto de retorno

**Objetivo.** Construir la infraestructura de seguridad que hace que todo lo demás sea reversible. Al terminar esta fase debes poder afirmar, sin dudar: *"si el próximo despliegue sale mal, vuelvo al estado anterior en menos de quince minutos, sin perder datos."*

**Precondición.** Ninguna.

### 0.1. Auditoría del estado real de producción

Antes de planificar sobre supuestos, hay que medir. Esta subfase es de diagnóstico puro: no se modifica nada, solo se recolectan hechos.

**Verificaciones a realizar:**

- **Confirmar o descartar el error de registro diario de métricas.** Contar cuántas filas existen en la tabla de historial de base de datos y examinar sus marcas de tiempo. Si aparecen decenas o cientos de registros separados por minutos en lugar de uno por día, el defecto está confirmado: la comprobación de duplicados nunca funcionó y la tabla ha estado creciendo con cada visita al panel. Este dato cambia la prioridad de la Fase 6.
- **Medir el peso real de la base de datos** y contrastarlo con el espacio libre en disco. Determinar cuánto del presupuesto de 512 MiB está consumido por datos, cuánto por respaldos acumulados, y cuánto queda disponible.
- **Inventariar el directorio de respaldos.** Comprobar cuántos volcados hay, su antigüedad, y si la política de rotación de cinco archivos está funcionando de verdad.
- **Confirmar la disponibilidad de la tarea programada diaria.** Es una prestación heredada de las cuentas anteriores al cambio de condiciones; hay que verificar en el panel que efectivamente está disponible, porque la Fase 6 depende de ella.
- **Registrar la fecha de expiración de la web app** y anotar el procedimiento de renovación.
- **Determinar el volumen real de cada tabla de negocio.** Número de clientes, pedidos, cotizaciones, productos y pagos. Este dato calibra si la creación de índices será instantánea o requerirá ventana de mantención.

**Producto de la subfase:** un documento breve de línea base, con cifras. Sin él, es imposible saber después si una optimización funcionó.

**Criterio de salida:** todas las verificaciones documentadas con valores concretos.

### 0.2. Protocolo de respaldo verificado

El proyecto ya tiene funcionalidad de respaldo, pero adolece de un defecto conceptual: **los respaldos viven en el mismo disco que la base de datos que protegen**. Eso no es un respaldo, es una copia. Si el disco se llena o se corrompe, se pierden ambos a la vez.

**Trabajo a realizar:**

- **Definir el procedimiento de extracción a máquina local.** Generar el volcado en el servidor, descargarlo, y verificar su integridad antes de considerarlo válido. Un archivo descargado a medias es peor que ninguno, porque da falsa confianza.
- **Establecer un criterio de verificación de integridad.** Como mínimo: tamaño esperado, presencia de las sentencias de cierre del volcado, y conteo de tablas. Un respaldo que no se ha verificado no cuenta como respaldo.
- **Definir dónde y con qué protección se almacenan localmente.** Estos archivos contienen nombres, teléfonos y montos de clientes reales. Requieren cifrado de disco y no deben acabar nunca en un directorio sincronizado a la nube sin cifrar, ni mucho menos en el repositorio.
- **Establecer la cadencia:** un respaldo descargado antes de cada despliegue de fase, más uno semanal de rutina.
- **Reducir la retención en servidor.** Cinco volcados completos en un disco de 512 MiB compartido con la base de datos es una temeridad. Con extracción local establecida, dos o tres bastan.

**Criterio de salida:** existe al menos un respaldo íntegro de producción, descargado, verificado y almacenado de forma segura fuera del servidor.

### 0.3. Réplica local fiel

**Objetivo.** Que el entorno de desarrollo deje de ser una maqueta con datos de prueba y pase a ser un espejo de producción.

**Trabajo a realizar:**

- **Restaurar el volcado de producción en el MySQL local en contenedor.** Este ejercicio tiene un valor doble: además de crear el entorno, es el primer ensayo real del procedimiento de recuperación ante desastres. Si falla aquí, mejor descubrirlo ahora que en una emergencia.
- **Elaborar una lista de comprobación de paridad** entre local y producción: versión de MySQL, conjunto de caracteres y colación, zona horaria del servidor de base de datos, versión de Python, y versiones exactas de las dependencias. Cada divergencia es un bug potencial que se manifestará solo en producción.
- **Verificar específicamente las tablas de zona horaria de MySQL.** Su presencia o ausencia determina el comportamiento de las consultas que convierten fechas, y es la clave del defecto sospechado en 0.1. Local y producción deben coincidir en este punto, o los resultados de las pruebas serán engañosos.
- **Documentar el procedimiento de refresco** de la réplica, para poder repetirlo cuando los datos locales queden obsoletos.

**Criterio de salida:** la aplicación arranca en local contra datos reales y las pantallas principales muestran información coherente con producción.

### 0.4. Higiene del repositorio

Limpieza de fondo que reduce ruido y riesgo antes de empezar a modificar código.

**Trabajo a realizar:**

- **Excluir la configuración del entorno de desarrollo integrado.** Los archivos de proyecto del IDE no pertenecen al repositorio: son específicos de tu máquina y generan conflictos sin aportar nada.
- **Eliminar las credenciales de desarrollo incrustadas en la configuración.** Aunque sean valores triviales de un contenedor local, su presencia en el repositorio enseña un mal hábito que tarde o temprano deriva en filtrar una credencial real.
- **Crear una plantilla de variables de entorno** que documente qué variables necesita la aplicación, sin contener valores. Es la única forma de que un despliegue nuevo sepa qué configurar.
- **Congelar dependencias con versiones exactas.** Un archivo de requisitos con rangos abiertos significa que una actualización de terceros puede romper producción sin que hayas tocado una línea. Con la restricción de reproducibilidad de este proyecto, las versiones se fijan.
- **Verificar que el archivo de exclusiones cubre efectivamente** los respaldos, el entorno virtual, los archivos compilados y el archivo de secretos.

**Criterio de salida:** un clon limpio del repositorio no contiene ningún artefacto local ni ninguna credencial.

### 0.5. Protocolo de versionado y despliegue

**Objetivo.** Convertir el despliegue de un acto improvisado en un procedimiento repetible.

**Trabajo a realizar:**

- **Definir la convención de etiquetado.** Cada estado desplegado a producción queda marcado con una etiqueta anotada que identifique la fase y el propósito. Sin esto, retroceder implica buscar identificadores de confirmación entre el historial, bajo presión, con el sistema caído.
- **Redactar la lista de comprobación previa al despliegue.** Como mínimo: pruebas en verde, respaldo descargado y verificado, etiqueta creada, comprobación de despliegue de Django ejecutada, y revisión de que las migraciones pendientes son solo de clases autorizadas.
- **Redactar el procedimiento de retroceso** paso a paso, incluyendo el caso más delicado: qué hacer si el despliegue incluyó una migración de Clase 2 y hay que volver atrás.
- **Ensayar el retroceso al menos una vez contra la réplica local.** Un procedimiento de recuperación no probado es una hipótesis, no un procedimiento.

**Criterio de salida:** ambos documentos redactados y el retroceso ensayado con éxito.

### 0.6. Despliegue temprano de correcciones triviales

Un conjunto acotado de correcciones de riesgo prácticamente nulo, agrupadas en un único despliegue para obtener beneficio inmediato sin esperar el ciclo completo.

**Alcance:**

- **Carga diferida de la biblioteca de generación de documentos PDF.** Actualmente se importa al arrancar el proceso, para todas las peticiones, aunque solo una vista la use. Es una dependencia notoriamente pesada que arrastra enlaces a bibliotecas gráficas del sistema y realiza un escaneo de tipografías al cargarse. Moverla al interior de la función que la necesita reduce directamente el tiempo de arranque en frío, que es el patrón que explica una parte considerable de las desconexiones observadas en el registro de uWSGI.
- **Ruta explícita para el archivo de exclusión de robots.** Actualmente las peticiones de rastreadores automáticos no encuentran ruta, caen al manejador de error 404 y consumen un renderizado completo de plantilla para un cliente que ya cerró la conexión. Publicar el archivo elimina aproximadamente una cuarta parte del ruido del registro y, de paso, indica a los buscadores que no indexen una aplicación privada.
- **Prevención del doble envío en el formulario de acceso.** El registro muestra pares de peticiones de autenticación separadas por dos segundos: el usuario no ve respuesta inmediata y vuelve a pulsar. Deshabilitar el control tras el primer envío resuelve el síntoma.
- **Normalización de la ruta de listado de pagos**, que carece de la barra final y provoca una redirección innecesaria en cada visita, a diferencia del resto de rutas del proyecto.

**Justificación del adelanto:** ninguna de estas correcciones toca datos, lógica de negocio ni estructura. El riesgo de introducir una regresión es mínimo y el beneficio es medible desde el día siguiente en el registro del servidor.

**Criterio de salida:** despliegue realizado y descenso observable de eventos de desconexión en el registro durante la semana posterior.

---

## FASE 1 — Observabilidad

**Objetivo.** Dejar de estar ciego. Hoy, cuando algo falla, el sistema muestra una página de error genérica, imprime una línea suelta y descarta toda la información de diagnóstico. No hay forma de saber qué falló, dónde, con qué datos ni quién lo provocó.

**Precondición.** Fase 0 completa.

**Por qué va antes que las correcciones.** Sin instrumentación, la Fase 3 se ejecutaría a ciegas: no habría manera de confirmar que el nuevo manejo de transacciones se comporta como se espera en producción, ni de detectar los casos límite que las pruebas no cubrieron.

### 1.1. Diseño del modelo de registro

Se crearán dos entidades separadas, porque responden a preguntas distintas y tienen ciclos de vida distintos.

**Registro de errores.** Responde a *"¿qué se rompió y por qué?"*. Debe capturar, como mínimo: momento exacto, tipo de excepción, mensaje, traza completa, ruta solicitada, método HTTP, usuario asociado si lo hubiera, y un identificador de correlación que permita enlazar el error con lo que el usuario vio en pantalla.

Ese identificador de correlación merece atención especial. La página de error debe mostrarlo al usuario, de modo que cuando alguien te diga *"me dio error al guardar"*, puedas pedirle ese código y localizar la traza exacta en segundos, en lugar de interrogarlo sobre qué estaba haciendo. Es una práctica de sistemas profesionales que cuesta muy poco implementar y ahorra horas.

**Registro de eventos.** Responde a *"¿quién hizo qué y cuándo?"*. Debe capturar: momento, tipo de evento, usuario responsable, entidad afectada con su identificador, y un resumen legible de la acción. No debe almacenar el contenido completo de los objetos: eso duplica la base de datos y agota el disco.

**Consideraciones de diseño obligatorias:**

- **Ambas tablas nacen con política de retención definida.** No se implementa el registro sin implementar simultáneamente su purga. Es la única forma de respetar el presupuesto de 512 MiB.
- **Índices desde el inicio** sobre los campos por los que se consultará: fecha y tipo de evento. Crear un índice sobre una tabla vacía es gratis; hacerlo sobre una tabla de cien mil filas, no.
- **Estimación previa de crecimiento.** Antes de escribir la migración, calcular cuántas filas generará un mes de operación normal según el volumen medido en 0.1, y contrastarlo con el espacio disponible. Si el resultado incomoda, se reduce el alcance de lo que se registra.

**Naturaleza del cambio:** Clase 2 (tablas nuevas). Autorizado, con respaldo previo.

### 1.2. Diseño de la capa de servicio de registro

Esta es la subfase de mayor densidad conceptual del plan, porque contiene cuatro trampas identificadas que hay que neutralizar por diseño, no por parche posterior.

**Trampa del aislamiento transaccional.** La Fase 3 envolverá las vistas de escritura en transacciones atómicas. Si el registro de un error se escribe dentro de esa transacción y la transacción se revierte, **el registro del error se revierte con ella**. Te quedas sin evidencia justo del fallo que más importaba. El diseño debe garantizar que la escritura del error ocurra fuera del ámbito transaccional de la operación que falló, o sobre una conexión independiente. Esta restricción obliga a diseñar las Fases 1 y 3 de forma coordinada, no secuencial e independiente.

**Trampa de la dependencia circular.** No se puede registrar en la base de datos un fallo de la base de datos. Si MySQL está caído, el disco lleno, o la conexión expirada, el registrador falla al intentar registrar. **Es obligatorio un camino de respaldo**: si la escritura falla, el error se emite igualmente a la salida estándar, que la plataforma recoge en su propio registro del servidor. No es una alternativa al diseño elegido, es un cinturón de seguridad dentro de él.

**Trampa del fallo en cascada.** El registrador nunca, bajo ninguna circunstancia, puede provocar que una petición falle. Un error dentro del código de registro debe ser absorbido silenciosamente tras intentar el camino de respaldo. Esta es la única situación en todo el plan donde suprimir una excepción es correcto — y precisamente por eso hay que dejarlo documentado, para que no se confunda con el patrón que la Fase 3 viene a erradicar.

**Trampa del coste por petición.** Con un solo worker de un núcleo, cada escritura añade latencia a la petición del usuario. El registro se limita estrictamente a lo definido en la decisión D7: errores y eventos de negocio. Nunca a peticiones de lectura ordinarias.

**Criterio de salida:** diseño documentado con las cuatro trampas explícitamente resueltas.

### 1.3. Retirada del middleware de captura global

El middleware actual intercepta cualquier excepción y devuelve una página de error. El problema no es la página amigable, sino que **destruye el traza de la excepción y desconecta la aplicación del sistema de manejo de errores de Django**, que registra en su propio canal, notifica a los administradores y se integra con herramientas de diagnóstico.

**Trabajo a realizar:**

- **Comprender por qué el middleware es en gran medida redundante.** Django ya convierte las excepciones de las vistas en respuestas antes de que lleguen a los middlewares superiores. El proyecto además ya declara manejadores personalizados de error 404 y 500, que Django invoca automáticamente cuando el modo de depuración está desactivado, conservando el registro del fallo. La página bonita ya estaba resuelta por el camino correcto.
- **Retirar el middleware** y verificar que los manejadores declarados siguen produciendo las páginas esperadas.
- **Configurar el sistema de registro de Django** para que el canal de peticiones dirija los errores hacia la capa de servicio diseñada en 1.2.
- **Verificar que las excepciones de tipo "no encontrado" siguen produciendo 404** y no quedan atrapadas como errores de servidor.

### 1.4. Instrumentación de eventos de negocio

**Trabajo a realizar:**

- **Elaborar el inventario de eventos a registrar.** Propuesta de partida: creación, modificación y eliminación de pedido; registro, modificación y eliminación de pago; cambio de estado de pedido; conversión de cotización a pedido; eliminación de cliente o producto; acceso exitoso y fallido; ejecución de respaldo y de restauración de base de datos.
- **Definir el punto exacto de instrumentación.** La regla es registrar *después* de que la operación se haya confirmado, nunca antes, para evitar registrar acciones que no ocurrieron.
- **Decidir el tratamiento de los eventos sin usuario asociado**, como los que genere la tarea programada.
- **Prestar atención especial a los eventos del módulo de administración de base de datos.** Una restauración sobrescribe todo el sistema; que quede constancia de quién la ejecutó y cuándo no es opcional en un sistema con datos comerciales.

### 1.5. Superficie de consulta

**Trabajo a realizar:**

- **Exponer ambas tablas mediante el panel de administración nativo de Django**, en modo de solo lectura, con filtros por fecha, tipo y usuario, y búsqueda por identificador de correlación.
- **No construir una interfaz propia.** El panel de administración resuelve el 100% de esta necesidad. Construir pantallas nuevas para consultar logs es trabajo que no aporta valor al negocio y añade superficie que mantener.
- **Restringir el acceso a superusuarios**, coherente con el resto del módulo administrativo.

### 1.6. Despliegue y validación

- Respaldo descargado, etiqueta creada, migración de Clase 2 aplicada.
- **Validación activa:** provocar deliberadamente un error controlado en producción y confirmar que queda registrado con traza completa e identificador de correlación visible al usuario.
- Observar durante una semana el crecimiento real de ambas tablas y contrastarlo con la estimación de 1.1. Si diverge al alza, ajustar el alcance antes de que se convierta en un problema de disco.

**Criterio de salida de la Fase 1:** un error real en producción es diagnosticable en menos de cinco minutos, sin acceso al servidor.

---

## FASE 2 — Red de seguridad

**Objetivo.** Construir las pruebas automatizadas que permitirán refactorizar la lógica crítica sin miedo. El proyecto actualmente tiene cero pruebas, y maneja dinero.

**Precondición.** Fase 0 completa. Puede desarrollarse en paralelo a la Fase 1.

**Alcance deliberadamente limitado.** El objetivo no es cobertura total — eso sería un proyecto en sí mismo y no es lo que necesita esta aplicación. El objetivo es **cubrir exactamente las rutas de código que las Fases 3, 4 y 5 van a modificar**, más la lógica de dinero. Todo lo demás queda fuera por ahora.

### 2.1. Infraestructura de pruebas

- **Configurar la ejecución contra MySQL en contenedor**, conforme a la decisión D5. Verificar que la base de datos de pruebas se crea y destruye correctamente y que hereda la configuración de caracteres y zona horaria de producción.
- **Definir la estrategia de datos de prueba.** Se recomiendan factorías o funciones auxiliares que construyan objetos coherentes bajo demanda, en lugar de accesorios estáticos que se desincronizan del modelo con cada cambio.
- **Establecer la organización de los archivos de prueba** por dominio, no en un archivo único.
- **Documentar el comando de ejecución** e incorporarlo a la lista de comprobación previa al despliegue definida en 0.5.

### 2.2. Pruebas de la lógica de dinero

Prioridad máxima. Es el área donde un error silencioso tiene consecuencias comerciales directas.

**Casos a cubrir:**

- **Cálculo de impuesto y valor bruto en productos.** Incluyendo el comportamiento de redondeo, que es donde se esconden las discrepancias de un peso que erosionan la confianza en el sistema.
- **Total pagado, saldo pendiente y porcentaje pagado en pedidos.** Con especial atención al caso de valor de venta igual a cero, que la implementación actual trata como pagado al cien por ciento — decisión que puede ser correcta o no, pero que debe quedar fijada por una prueba.
- **Pagos parciales acumulados**, sobrepagos, y pedidos sin ningún pago registrado.
- **Validación de que el abono inicial no exceda el valor total.**
- **Agregaciones del panel financiero**, comparando el resultado del cálculo optimizado contra un cálculo ingenuo equivalente sobre un conjunto conocido.

### 2.3. Pruebas de flujos críticos

- **Creación de pedido con múltiples ítems**, verificando que los ítems quedan correctamente asociados y con el precio histórico congelado.
- **Edición de pedido con modificación de ítems**, que es el flujo con el defecto más grave del proyecto.
- **Conversión de cotización a pedido**, verificando la migración íntegra de ítems y datos del cliente.
- **Cambio de estado**, incluyendo el rechazo de estados no válidos.
- **Duplicación de pedido**, verificando qué se copia y qué no. Nota: la implementación actual no copia los ítems, lo cual puede ser un defecto o una decisión — hay que resolverlo y fijarlo con una prueba.

### 2.4. Pruebas de regresión de los defectos conocidos

Cada defecto detectado en la auditoría obtiene una prueba que **falla ahora** y pasará cuando se corrija. Es la forma disciplinada de trabajar: la prueba documenta el defecto, verifica la corrección, y evita que reaparezca.

- **Pérdida silenciosa de ítems.** Simular un fallo a mitad del guardado de ítems y verificar el estado resultante. Esta prueba fallará en la Fase 2 y pasará en la Fase 3. Es la prueba más importante de todo el plan.
- **Comprobación de duplicados en el registro diario de métricas.** Verificar que una segunda ejecución el mismo día no crea un registro nuevo.
- **Ausencia de escritura mediante peticiones de lectura.** Verificar que las rutas de cambio de estado y duplicación rechazan el método GET. Fallará ahora, pasará en la Fase 4.

### 2.5. Pruebas de control de acceso

- Verificar que toda vista protegida rechaza al usuario anónimo.
- Verificar que las vistas de administración de base de datos rechazan a usuarios autenticados que no sean superusuarios.
- Verificar el comportamiento de los puntos de acceso que responden en formato JSON ante peticiones no autenticadas.

**Criterio de salida de la Fase 2:** las pruebas de regresión de 2.4 fallan de forma reproducible, demostrando que capturan los defectos reales. El resto está en verde.

---

## FASE 3 — Integridad transaccional

**Objetivo.** Corregir el defecto más grave del proyecto: la ausencia total de atomicidad en operaciones de escritura compuesta, combinada con supresión silenciosa de excepciones.

**Precondición.** Fases 1 y 2 completas. **Esta precondición no es negociable.**

**Naturaleza del problema.** Existe un decorador denominado "transacción segura" que no abre ninguna transacción: es un bloque de captura de excepciones con un nombre que promete algo que no entrega. La documentación del proyecto afirma que el sistema usa transacciones atómicas. El módulo correspondiente de Django está importado pero nunca utilizado. El resultado es que una operación que guarda un pedido y luego sus ítems puede completar la primera mitad y fallar la segunda, dejando datos parciales sin ninguna traza.

El caso más severo está en la edición de pedidos: se eliminan todos los ítems existentes antes de recrearlos, y el bloque completo está protegido por una supresión silenciosa. Un fallo a mitad de camino destruye los ítems originales, crea solo algunos de los nuevos, y no avisa a nadie. El usuario ve la pantalla de confirmación y cree que guardó correctamente.

### 3.1. Rediseño conceptual del decorador

**Principio de diseño: atomicidad y manejo de errores son responsabilidades distintas y no deben vivir en el mismo componente.**

**Puntos a resolver:**

- **El orden de anidación es determinante, y es contraintuitivo.** Si la excepción se captura *dentro* del bloque atómico, la transacción concluye sin error desde el punto de vista de la base de datos y **no se revierte nada**. La reversión solo ocurre si la excepción escapa del bloque. Comprender esto a fondo es el objetivo pedagógico central de esta fase.
- **Decidir si el decorador se divide en dos** —uno que garantice atomicidad, otro que traduzca fallos a respuesta de usuario— o si se mantiene unificado con el orden interno correcto. La primera opción es más limpia y más fácil de razonar; la segunda es menos invasiva.
- **Renombrar el componente para que su nombre sea honesto.** Un nombre que miente sobre lo que hace el código es una forma de deuda técnica particularmente perniciosa, porque induce a confiar en garantías inexistentes.
- **Corregir la documentación del proyecto** para que refleje la realidad. Un documento que promete garantías que el código no cumple es peor que la ausencia de documento.

### 3.2. Erradicación de la supresión silenciosa

- **Localizar todos los bloques que capturan excepciones sin actuar.** El patrón de capturar cualquier excepción y no hacer nada convierte errores en corrupción silenciosa, y es el peor antipatrón presente en el código.
- **Sustituirlos por el comportamiento correcto según el caso:** propagar para que la transacción revierta, o capturar de forma específica y registrar mediante la capa construida en la Fase 1.
- **Reemplazar la impresión directa a consola** usada como diagnóstico por registro estructurado. Aplica también a los mensajes de depuración de validación de formularios.

### 3.3. Revisión de fronteras transaccionales

Recorrido vista por vista para determinar dónde debe empezar y terminar cada transacción.

**Vistas que requieren atención prioritaria:**

- **Creación de pedido:** el pedido, sus ítems y el pago inicial opcional deben constituir una única unidad indivisible.
- **Edición de pedido:** la eliminación y recreación de ítems debe ser atómica junto con la modificación del pedido.
- **Creación y edición de cotización:** mismo patrón, mismo riesgo.
- **Conversión de cotización a pedido:** operación compuesta que crea un pedido, migra ítems y actualiza el estado de la cotización. Un fallo parcial deja la cotización marcada como aceptada sin pedido asociado, o un pedido sin ítems.
- **Registro de pago:** si además actualiza el estado financiero del pedido, ambas escrituras deben ir juntas.

**Consideración adicional:** identificar qué operaciones tienen efectos fuera de la base de datos, como la escritura de archivos de imagen de referencia. Los sistemas de archivos no participan en transacciones de base de datos: si la transacción se revierte, el archivo escrito permanece. Hay que decidir conscientemente cómo tratar esas huérfanas.

### 3.4. Contrato de error hacia el usuario

- **Definir qué ve el usuario ante un fallo:** mensaje comprensible, sin detalles técnicos, con el identificador de correlación de la Fase 1 para que pueda reportarlo.
- **Distinguir errores de validación de errores del sistema.** Los primeros deben devolver al formulario con los datos conservados y los mensajes correspondientes; los segundos van a la página de error. Actualmente ambos casos se tratan igual, lo que genera pérdida de trabajo del usuario.
- **Evitar el peor escenario posible:** que el usuario pierda un formulario largo por un error del sistema y no tenga forma de recuperarlo.

### 3.5. Validación y despliegue

- Las pruebas de regresión de 2.4 deben pasar a verde. **Este es el criterio objetivo de que la fase funcionó.**
- Ejercitar manualmente los flujos completos contra la réplica local con datos reales.
- Respaldo descargado, etiqueta creada, despliegue.
- **Vigilancia intensiva durante la primera semana** mediante las tablas de registro de la Fase 1.

**Criterio de salida de la Fase 3:** una operación compuesta que falla a mitad de camino no deja rastro en la base de datos, queda registrada con traza completa, y el usuario recibe un mensaje comprensible.

---

## FASE 4 — Seguridad y endurecimiento

**Objetivo.** Cerrar las vulnerabilidades identificadas y aplicar el estándar de configuración para producción.

**Precondición.** Fase 2 completa.

### 4.1. Corrección de las mutaciones por petición de lectura

**El problema.** Dos rutas modifican la base de datos respondiendo a peticiones GET: el cambio de estado de pedido y la duplicación de pedido. Esto viola la semántica de HTTP, que exige que las peticiones de lectura sean seguras y sin efectos observables.

**Consecuencias concretas:**

- **Vulnerabilidad de falsificación de petición entre sitios.** Django no valida token en peticiones de lectura. Una etiqueta de imagen incrustada en cualquier correo o página que abra un usuario autenticado basta para alterar el estado de un pedido, sin ningún clic.
- **Prelectura del navegador.** Los navegadores modernos precargan enlaces que anticipan que el usuario visitará. Un pedido puede cambiar de estado porque alguien pasó el cursor por encima.
- **Rastreadores y extensiones** pueden recorrer la aplicación disparando cambios de estado.

El registro de uWSGI confirma que estas rutas reciben tráfico real.

**Trabajo a realizar:**

- Convertir ambas operaciones a peticiones POST con token de seguridad.
- Adaptar las plantillas: los enlaces pasan a ser formularios.
- Considerar confirmación explícita del usuario para los cambios irreversibles.
- Revisar el resto de rutas buscando el mismo patrón.

### 4.2. Configuración de producción

- **Ejecutar la comprobación de despliegue de Django** y resolver cada advertencia con criterio, no de forma mecánica.
- **Cookies de sesión y de token solo por conexión cifrada.**
- **Redirección forzosa a conexión cifrada** y política de transporte estricto, introducida con periodo de prueba corto antes de fijar un valor alto. Un valor elevado aplicado con la configuración incorrecta puede dejar el dominio inaccesible durante meses, porque los navegadores lo recuerdan.
- **Orígenes de confianza para el token de seguridad**, requisito de las versiones recientes de Django tras un proxy.
- **Revisar la configuración de hosts permitidos** para que no obstaculice el desarrollo local.
- **Verificar que el modo de depuración está efectivamente desactivado en producción**, y considerar que la aplicación se niegue a arrancar si detecta una configuración insegura. Fallar ruidosamente al inicio es preferible a operar de forma insegura en silencio.

### 4.3. Credenciales y secretos

- **Eliminar el paso de la contraseña de base de datos por línea de órdenes** en los procesos de respaldo y restauración. En un entorno compartido como el de la plataforma, los argumentos de un proceso son visibles para otros usuarios del sistema. La alternativa es transmitirla por variable de entorno del subproceso o mediante archivo de configuración con permisos restringidos.
- **Verificar que la clave secreta de la aplicación** proviene exclusivamente del entorno y que su ausencia detiene el arranque con un mensaje claro.
- **Revisar el historial del repositorio** en busca de credenciales filtradas en confirmaciones antiguas.

### 4.4. Endurecimiento del módulo de restauración

Este módulo permite ejecutar un archivo SQL arbitrario contra la base de datos de producción. Está restringido a superusuarios, lo cual es correcto, pero merece defensas adicionales por la magnitud del daño potencial.

- **Validación del archivo recibido** antes de ejecutarlo: extensión, tamaño máximo, y comprobación de que su estructura corresponde a un volcado de esta base de datos.
- **Verificar que el respaldo de emergencia previo efectivamente se generó** antes de proceder. La lógica actual lo intenta, pero conviene revisar que la condición de aborto es infalible.
- **Registro obligatorio del evento** conforme a la Fase 1.
- **Confirmación explícita e inequívoca** en la interfaz, dada la irreversibilidad de la operación.

### 4.5. Correcciones de configuración

- **Corregir la importación de la configuración de Django.** El proyecto importa el módulo de ajustes directamente en lugar de usar el objeto de configuración perezoso que provee el marco. La diferencia no es cosmética: el objeto perezoso aplica los valores por defecto del marco, respeta la variable de entorno que selecciona el módulo de ajustes, y es el único que funciona con las utilidades de sustitución de configuración en pruebas.
- **Añadir verificación de salud de conexión** de base de datos. La configuración actual reutiliza conexiones durante sesenta segundos sin comprobar que sigan vivas, lo que produce fallos intermitentes tras periodos de inactividad — un escenario frecuente en esta aplicación, como demuestra el episodio de hibernación registrado.
- **Eliminar importaciones duplicadas y código muerto.**

**Criterio de salida de la Fase 4:** la comprobación de despliegue de Django no reporta advertencias, y las pruebas de método HTTP de 2.4 pasan a verde.

---

## FASE 5 — Rendimiento

**Objetivo.** Reducir el tiempo real y percibido de respuesta, atacando la causa raíz del patrón dominante en el registro de uWSGI.

**Precondición.** Fase 2 completa.

**Diagnóstico de partida.** El registro muestra desconexiones concentradas de forma abrumadora en la ruta de listado de pedidos. Una parte corresponde a arranque en frío; el resto ocurre con el proceso ya caliente, lo que apunta a que la página tarda lo suficiente como para que el usuario recargue o navegue antes de recibirla. Es importante entender que la desconexión es el síntoma, no la enfermedad.

### 5.1. Reducción del arranque en frío

- **Confirmar el efecto de la carga diferida** aplicada en 0.6, comparando los tiempos de inicialización registrados antes y después.
- **Inventariar el resto de importaciones a nivel de módulo** y evaluar cuáles pueden diferirse. La regla: si una dependencia pesada solo la usa una vista, no debe cargarse para todas.
- **Aceptar el límite.** Con hibernación activa e imposible de desactivar en el plan gratuito, el arranque en frío se abarata pero no se elimina. Documentarlo como comportamiento conocido evita perseguirlo indefinidamente.

### 5.2. Eliminación de consultas repetidas en plantillas

**El problema.** El modelo de pedido expone propiedades calculadas que consultan la base de datos en cada acceso: total pagado, saldo pendiente y porcentaje pagado. Las optimizaciones aplicadas a las vistas mediante carga anticipada de relaciones no protegen frente a esto, porque las propiedades se evalúan durante el renderizado de la plantilla, una vez por fila.

Con diez filas por página, mostrar el saldo genera diez consultas adicionales; mostrar además la barra de progreso las duplica, porque la propiedad correspondiente vuelve a invocar la primera.

**Trabajo a realizar:**

- **Auditar cada plantilla de listado** buscando accesos a propiedades que consultan.
- **Trasladar el cálculo a anotaciones del conjunto de consulta.** El proyecto ya aplica esta técnica correctamente en el panel financiero; se trata de extender el mismo patrón a los listados, el detalle de pedido y la vista de trabajo semanal.
- **Instalar y usar una herramienta de diagnóstico de consultas** en el entorno local, para medir en lugar de suponer. Es la herramienta pedagógica más valiosa para interiorizar el problema de las consultas repetidas.
- **Registrar el número de consultas antes y después** de cada corrección, como evidencia objetiva.

### 5.3. Índices de base de datos

Cambio de Clase 2, autorizado.

- **Identificar los campos usados sistemáticamente en filtros y ordenaciones:** estado de pedido, fecha de entrega, fecha de solicitud, fecha de registro del historial, y las fechas de los registros creados en la Fase 1.
- **Evaluar índices compuestos** para las combinaciones de filtro y orden más frecuentes.
- **Ensayar cada creación contra la réplica local** midiendo la duración. Con el volumen actual debería ser instantáneo, pero conviene confirmarlo antes de tocar producción.
- **No indexar por reflejo.** Cada índice acelera lecturas y ralentiza escrituras, y ocupa espacio en un disco escaso. Se justifica cada uno con una consulta concreta.

### 5.4. Compilación local de estilos

**El problema.** La plantilla base carga el compilador de Tailwind desde una red de distribución de contenidos. Eso significa aproximadamente 400 KB de JavaScript que el navegador descarga, interpreta, y usa para recorrer el árbol del documento, generar las reglas CSS e inyectarlas — en cada carga de página. Durante ese proceso la página aparece sin estilos o en blanco. La propia documentación de Tailwind desaconseja explícitamente ese uso fuera de prototipado.

A eso se suman cuatro dominios externos adicionales para tipografías, iconografía y componentes, cada uno con su propio establecimiento de conexión cifrada.

**Trabajo a realizar:**

- **Establecer el proceso de compilación local con pnpm**, conforme a la decisión D9. El gestor elegido aporta un archivo de bloqueo con verificación de integridad por paquete y un modelo de almacén enlazado que reduce la superficie frente a ataques de cadena de suministro — consideración pertinente dado que esta aplicación maneja datos comerciales sensibles.
- **Fijar versiones exactas** de todas las dependencias del ecosistema Node. Sin rangos abiertos.
- **Extraer la configuración de tema** que hoy vive incrustada en la plantilla hacia el archivo de configuración de la herramienta.
- **Verificar que el barrido de clases cubre todas las plantillas**, incluida la de acceso, que mantiene su propia copia de la configuración.
- **Incorporar el archivo compilado al repositorio** y añadir el paso de compilación a la lista de comprobación previa al despliegue. Este es el coste del enfoque: si se olvida compilar tras cambiar clases, los estilos nuevos no aparecen en producción. Hay que dejarlo explícito en el procedimiento.
- **Verificar el archivo generado** antes de desplegarlo, con especial atención a la elección del modo claro u oscuro y a los estilos de los componentes de terceros.

### 5.5. Consolidación de recursos externos

- **Evaluar el alojamiento local de tipografías e iconografía**, eliminando dependencias de terceros y establecimientos de conexión adicionales. Considerar el impacto sobre la cuota de disco.
- **Revisar si los componentes de selección y edición enriquecida se usan en todas las páginas** o solo en algunas, y cargarlos únicamente donde hagan falta.
- **Verificar la configuración de archivos estáticos** en el servidor.

### 5.6. Medición

- **Establecer la línea base antes de intervenir:** tiempo hasta primer contenido pintado, peso total transferido, número de peticiones y número de consultas por página, en las tres vistas más usadas.
- **Repetir la medición al terminar** y documentar la mejora.
- **Observar el registro del servidor durante dos semanas** para confirmar la reducción de eventos de desconexión sobre la ruta de listado. Es la validación definitiva de que se atacó la causa y no el síntoma.

**Criterio de salida de la Fase 5:** reducción medible y documentada en las cuatro métricas, y descenso observable del patrón dominante en el registro.

---

## FASE 6 — Arquitectura y automatización

**Objetivo.** Corregir los desajustes estructurales y automatizar el mantenimiento dentro de las restricciones de la plataforma.

**Precondición.** Fases 1, 2 y 3 completas.

### 6.1. Corrección del registro diario de métricas

**El problema.** La comprobación de si ya existe un registro del día aplica un filtro por fecha sobre un campo de fecha y hora, con zonas horarias activas. MySQL traduce eso a una conversión de zona horaria sobre la columna, lo que impide usar cualquier índice y, si las tablas de zona horaria del servidor no están cargadas, devuelve un valor nulo. En ese caso la comparación nunca resulta verdadera y **se inserta un registro nuevo en cada visita al panel de control**.

La auditoría de 0.1 determinó si el defecto está activo. Independientemente del resultado, la consulta debe corregirse.

**Trabajo a realizar:**

- **Sustituir el filtro por un rango explícito de instantes**, construido con consciencia de zona horaria. Esta formulación sí aprovecha índices y no depende de las tablas de zona horaria del servidor.
- **Si el defecto estaba activo, planificar la limpieza de los registros espurios.** Esta es una operación destructiva sobre datos: requiere respaldo previo, ensayo en la réplica local, y verificación de que se conserva exactamente un registro representativo por día.
- **Confirmar con la prueba de regresión de 2.4.**

### 6.2. Externalización a tarea programada

**El problema estructural.** El registro de métricas se ejecuta hoy dentro del ciclo de petición de dos vistas de lectura. Una operación de escritura periódica no pertenece al camino de respuesta de un usuario: añade latencia, se ejecuta un número impredecible de veces, y falla de forma invisible.

**Trabajo a realizar:**

- **Diseñar un único guion de mantención diaria**, conforme a la decisión D8, que orqueste tres responsabilidades: registro de métricas, purga de registros antiguos según las políticas de retención, y generación del respaldo de base de datos.
- **Cada paso debe tener manejo de error independiente.** Si el respaldo falla, las métricas deben registrarse igualmente. Un guion de mantención que se detiene en el primer tropiezo es peor que tres guiones separados.
- **El guion debe registrar su propia ejecución** en la tabla de eventos: inicio, resultado de cada paso, y fin. Es la única forma de detectar que dejó de ejecutarse.
- **Implementarlo como orden de gestión del marco**, no como archivo suelto, para que herede la configuración y el acceso al modelo de datos.
- **Vigilar el consumo de tiempo de procesador**, que en el plan gratuito está limitado a 100 segundos diarios y sí aplica a las tareas programadas.
- **Retirar la invocación desde las vistas** una vez la tarea esté operativa y verificada.
- **Considerar el escenario de tarea no ejecutada.** Si la tarea falla varios días seguidos, el gráfico de evolución mostrará huecos. Definir si eso es aceptable o si requiere aviso.

### 6.3. Gestión del disco

- **Definir y aplicar la política de retención** de las tablas de registro, ejecutada por el guion de mantención.
- **Reducir la retención de volcados en servidor** conforme a lo establecido en 0.2.
- **Añadir vigilancia del espacio disponible** al guion de mantención, con registro de evento cuando se cruce un umbral. Quedarse sin disco en un plan con 512 MiB compartidos entre datos, respaldos, registros y archivos subidos es un escenario realista, no teórico.
- **Revisar el crecimiento del directorio de imágenes de referencia**, que también consume el mismo presupuesto y hoy no tiene política alguna.

### 6.4. Modularización del módulo de vistas

**El problema.** Todas las vistas del proyecto conviven en un único archivo que ha crecido hasta hacerse difícil de navegar. No es un defecto funcional, pero es fricción permanente para cualquier trabajo futuro.

**Trabajo a realizar:**

- **Dividir por dominio:** pedidos, clientes, cotizaciones, productos, pagos, administración de base de datos.
- **Ejecutarlo como refactorización pura**, sin ningún cambio de comportamiento, y validado por la suite de pruebas.
- **Preservar los nombres de las rutas** para no romper las referencias de las plantillas.
- **Realizarlo en un despliegue dedicado**, sin mezclar con cambios funcionales, de modo que si algo falla la causa sea inequívoca.

### 6.5. Extracción de la capa de servicios

- **Identificar la lógica de negocio incrustada en las vistas:** interpretación del contenido enviado por el formulario dinámico de ítems, cálculo de totales, conversión de cotización a pedido, aplicación de pagos.
- **Trasladarla a funciones de servicio** que reciban datos y devuelvan resultados, sin dependencia del objeto de petición.
- **Beneficio principal: comprobabilidad.** La lógica de negocio aislada del ciclo HTTP se prueba de forma directa y rápida.
- **Aplicarlo de forma incremental**, empezando por la conversión de cotización a pedido, que es la operación de mayor complejidad.

### 6.6. Deuda técnica menor

- **Paginación en el listado de clientes**, hoy inexistente.
- **Revisar el campo de estado financiero del pedido**, que duplica información derivable de los pagos registrados y constituye una doble fuente de verdad. Corregirlo requeriría un cambio de Clase 3, prohibido en este plan: **se documenta como deuda conocida y se difiere**, con la salvedad de asegurar que ambos valores se mantienen sincronizados mientras tanto.
- **Normalizar la nomenclatura de rutas**, hoy inconsistente entre secciones.
- **Revisar el patrón de captura de rutas numéricas en la raíz**, que hace que cualquier ruta de un solo número se interprete como detalle de pedido.
- **Homogeneizar la nomenclatura del código.** El proyecto mezcla castellano e inglés; conviene fijar un criterio único, aunque se aplique gradualmente.

**Criterio de salida de la Fase 6:** la tarea diaria se ejecuta de forma autónoma y verificable, las vistas ya no realizan escrituras de mantenimiento, y el consumo de disco está bajo vigilancia.

---

## FASE 7 — Operación continua

**Objetivo.** Sostener lo construido. Esta fase no termina.

### 7.1. Vigilancia de la expiración de la web app

**Riesgo crítico y específico del plan gratuito.** Las web apps de cuentas gratuitas expiran tras un periodo sin actividad de la cuenta, y la plataforma no envía aviso previo. La aplicación puede quedar apagada en silencio.

- **Establecer un recordatorio recurrente externo** —en el calendario personal, no en el propio sistema— para acceder y renovar.
- **Documentar el procedimiento de renovación.**
- **Comprobar periódicamente que la aplicación responde**, mediante una visita rutinaria.

### 7.2. Ritual de despliegue

- **Consolidar la lista de comprobación** de 0.5 con los pasos añadidos por las fases posteriores: pruebas en verde, compilación de estilos actualizada, comprobación de despliegue sin advertencias, respaldo descargado y verificado, etiqueta creada, revisión de migraciones pendientes.
- **Mantenerla como documento vivo** en el repositorio.

### 7.3. Revisión periódica de registros

- **Rutina semanal:** revisar la tabla de errores, atender lo recurrente, verificar que la tarea diaria se ejecutó todos los días.
- **Rutina mensual:** revisar el crecimiento de las tablas de registro y el espacio disponible; revisar el registro del servidor buscando patrones nuevos.
- **Establecer el hábito de convertir cada error recurrente en una prueba** antes de corregirlo.

### 7.4. Ensayo de recuperación ante desastres

- **Al menos una vez por semestre**, restaurar un respaldo en el entorno local y verificar la integridad del resultado.
- **Un procedimiento de recuperación que no se ensaya, no existe.** Es la lección más repetida de la operación de sistemas y la más ignorada.

### 7.5. Deuda diferida y evolución

Registro explícito de lo que este plan decidió no abordar, para que no se pierda:

- Unificación del estado financiero del pedido (requiere cambio de Clase 3).
- Copia de ítems en la duplicación de pedidos, pendiente de decisión de negocio.
- Unificación de la nomenclatura del código.
- Integración continua automatizada, condicionada a disponer de un entorno adecuado.

### 7.6. Criterios para evaluar el cambio de plan

Este plan está diseñado para operar dentro del plan gratuito. Conviene definir de antemano qué señales justificarían el cambio a un plan de pago, para tomar esa decisión con datos y no por frustración:

- El disco disponible cae de forma sostenida por debajo de un margen de seguridad.
- El arranque en frío sigue afectando la operación diaria pese a las optimizaciones.
- Se necesita más de una tarea programada, o con frecuencia superior a la diaria.
- El riesgo de expiración silenciosa se materializa alguna vez.
- Se requiere acceso saliente sin restricciones, o un entorno de preproducción real.

Un plan de pago básico elimina la hibernación, amplía el disco, concede múltiples tareas programadas y libera el acceso saliente — resolviendo de golpe cuatro de las restricciones estructurales de este documento.

---

## 3. Matriz de trazabilidad

Cada hallazgo de la auditoría, con su severidad y la subfase que lo resuelve.

| Severidad | Hallazgo | Subfase |
|---|---|---|
| Crítico | El decorador de transacción no abre transacción alguna | 3.1, 3.3 |
| Crítico | Supresión silenciosa de excepciones con pérdida de ítems | 3.2 |
| Crítico | Modificación de datos mediante peticiones de lectura | 4.1 |
| Alto | Middleware que destruye la información de diagnóstico | 1.3 |
| Alto | Ausencia total de observabilidad | 1.1 – 1.6 |
| Alto | Registro diario de métricas potencialmente defectuoso | 0.1, 6.1 |
| Alto | Escritura de mantenimiento dentro del ciclo de petición | 6.2 |
| Alto | Consultas repetidas por propiedades calculadas en plantillas | 5.2 |
| Alto | Importación incorrecta del objeto de configuración | 4.5 |
| Alto | Compilador de estilos ejecutándose en el navegador | 5.4 |
| Alto | Dependencia pesada cargada en cada arranque | 0.6, 5.1 |
| Medio | Configuración de producción sin endurecer | 4.2 |
| Medio | Credenciales visibles en la tabla de procesos | 4.3 |
| Medio | Respaldos alojados en el mismo disco que protegen | 0.2, 6.3 |
| Medio | Ausencia absoluta de pruebas automatizadas | 2.1 – 2.5 |
| Medio | Conexiones de base de datos sin verificación de salud | 4.5 |
| Medio | Listado de clientes sin paginación | 6.6 |
| Medio | Módulo de restauración sin validación de entrada | 4.4 |
| Medio | Riesgo de expiración silenciosa de la aplicación | 7.1 |
| Bajo | Ruido de rastreadores en el registro del servidor | 0.6 |
| Bajo | Doble envío en el formulario de acceso | 0.6 |
| Bajo | Módulo de vistas monolítico | 6.4 |
| Bajo | Configuración del entorno de desarrollo versionada | 0.4 |
| Bajo | Inconsistencias de nomenclatura de rutas | 6.6 |
| Bajo | Importaciones duplicadas y código muerto | 4.5 |
| Diferido | Doble fuente de verdad en el estado financiero | 6.6 (documentado) |

---

## 4. Cómo usar este documento

**No es un cronograma.** Es una secuencia de dependencias. Las fases 0, 1, 2 y 3 tienen un orden estricto que no debe alterarse: cada una construye la seguridad que la siguiente necesita. Las fases 4, 5 y 6 pueden reordenarse según prioridad del negocio, siempre que sus precondiciones se cumplan.

**Cada subfase es una unidad de trabajo.** Se termina o no se empieza. Dejar una subfase a medias en un sistema en producción es peor que no haberla iniciado.

**Los criterios de salida no son decorativos.** Son la definición objetiva de "terminado". Sin ellos, el avance se mide por sensación, y la sensación miente.

**El documento evoluciona.** Cuando una fase revele algo que este plan no anticipó, se actualiza. Un plan que no se corrige con lo aprendido es un documento muerto.

---

*Documento de trabajo técnico. Sujeto a revisión al completar cada fase.*
