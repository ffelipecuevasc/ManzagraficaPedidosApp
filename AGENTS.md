# AGENTS.md · Manza Gráfica App

Instrucciones de trabajo para cualquier agente de IA (Claude Code, Antigravity, Codex u otro) que colabore en este repositorio. Este archivo es la entrada principal.

---

## 1. Contexto en 30 segundos

- **Cliente:** Manza Gráfica, empresa de diseño, publicidad e impresión.
- **Objetivo:** que la aplicación interna de pedidos, cotizaciones y pagos sea confiable, segura y mantenible sin poner en riesgo los datos comerciales reales que ya contiene.
- **Naturaleza:** aplicación monolítica **en producción**, con clientes, pedidos, cotizaciones y pagos reales acumulados. Todo cambio se trata como un cambio sobre datos vivos.
- **Alcance comprometido:** refactorización, corrección de defectos, endurecimiento, rendimiento y automatización descritos en `_planificacion/00_producto/plan-de-trabajo.md`. Funcionalidades de negocio nuevas quedan fuera: no las implementes sin una RDA aprobada.
- **Dominio:** manzagrafica.pythonanywhere.com.
- **Desarrollador responsable:** Francisco Felipe Cuevas Cerón · https://felipecuevas.dev.

## 2. Documentos protegidos

`AGENTS.md`, `DESIGN.md`, `README.md` (raíz) y `_planificacion/README.md` son la referencia estable del proyecto y **no los edites**.

Si crees que alguno debería cambiar, entrega al desarrollador una propuesta con:

1. El archivo y la sección.
2. El texto actual y el texto que propones.
3. Por qué conviene el cambio y qué pasa si no se hace.

El desarrollador decide y hace la edición. Mientras tanto, sigue el documento tal como está.

## 3. Orden de lectura obligatorio antes de trabajar

1. `_planificacion/00_producto/registro-pendientes.md`: qué está pendiente y cuál es la iteración activa. Es la fuente única de verdad del trabajo.
2. El archivo de la iteración activa en `_planificacion/10_epicas/<epica>/`.
3. `_planificacion/00_producto/decisiones.md`: RDA vigentes. No contradigas una RDA aceptada.
4. `DESIGN.md`: fuente de verdad del diseño. Léelo siempre que la tarea toque plantillas, estilos o JavaScript de interfaz.
5. `README.md` (raíz): descripción del proyecto y de su arquitectura.
6. `_planificacion/README.md`: estructura de la planificación, convenciones, reglas de mantenimiento y plantillas.
7. El resto de `_planificacion/` según la tarea: `plan-de-trabajo.md` para el razonamiento de cada fase, `producto.md` ante dudas de alcance, `auditoria-tecnica.md` si la iteración cierra hallazgos, y las bitácoras anteriores de la misma épica.
8. `docs/operacion/` cuando la tarea toque respaldos, réplica local, despliegue o retroceso.

Si algo de lo anterior está en conflicto, detente y pregunta.

## 4. Stack y versiones

- **Lenguaje y marco:** Python 3.13 y Django 6.0.1 (patrón Modelo-Vista-Plantilla), con el sistema de autenticación nativo de Django y plantillas del lenguaje de plantillas de Django.
- **Base de datos:** MySQL 8.0 en producción; MySQL 8.0 en un contenedor Docker en local, con la misma versión, conjunto de caracteres, colación y zona horaria que producción.
- **Dependencias Python:** fijadas con versión exacta (`==`) en `requirements.txt`. Las principales: `mysqlclient`, `dj-database-url`, `python-dotenv`, `django-widget-tweaks` y `weasyprint`.
- **Interfaz:** plantillas en `pedidos/templates/`, estilos con Tailwind CSS, JavaScript propio en `pedidos/static/pedidos/js/index.js`, jQuery, Select2, Summernote y SweetAlert2.
- **Herramientas de Node:** solo `pnpm`, con versiones exactas y archivo de bloqueo versionado.
- **IDE y repositorio:** PyCharm Pro; GitHub, rama única `main` con etiquetas anotadas antes de cada despliegue.
- **Hosting:** PythonAnywhere, plan gratuito: 512 MiB de disco compartidos entre archivos y MySQL, un solo worker uWSGI de un núcleo, una tarea programada diaria, 100 segundos de CPU diarios para consolas y tareas, acceso saliente restringido a lista blanca, hibernación por inactividad y expiración de la web app si la cuenta no registra actividad.

## 5. Comandos

```bash
# Servidor de desarrollo (requiere el MySQL local en Docker encendido)
python manage.py runserver

# Pruebas automatizadas (se ejecutan contra MySQL, nunca contra SQLite)
python manage.py test pedidos

# Revisión de configuración
python manage.py check
# Revisión de producción: ejecútala con la variable de entorno DEBUG=False
python manage.py check --deploy

# Detectar cambios de modelo sin migración, sin crear archivos
python manage.py makemigrations --check --dry-run

# Ver el SQL exacto que ejecuta una migración (obligatorio para clasificarla)
python manage.py sqlmigrate pedidos <numero_de_migracion>

# Estado de las migraciones en la base local
python manage.py showmigrations pedidos

# Contenedor MySQL local (compose.yaml en la raíz; lo ejecuta el desarrollador)
docker compose up -d
docker compose stop
# Nunca `docker compose down -v` ni `docker volume rm mysql_data`.
# Réplica de producción y su refresco: docs/operacion/replica-local.md
```

Usa siempre `pip` para Python y `pnpm` para Node. Nunca `npm`, `yarn` ni `npx`. No dejes servidores de desarrollo corriendo al terminar.

## 6. Límites de actuación

**Prohibido (lo hace solo el desarrollador):**

- `git commit`, `git push`, `git merge`, `git pull`, `git rebase`, `git reset`, `git tag` y cualquier operación que reescriba o publique historial.
- Desplegar o tocar PythonAnywhere de cualquier forma: consolas, SSH, recarga de la web app, tarea programada, variables de entorno del servidor, base de datos de producción.
- Ejecutar comandos contra cualquier base de datos que no sea la local en Docker.
- Leer, abrir o copiar respaldos (`backups/`, la carpeta de respaldos descargados que el desarrollador guarda fuera del repositorio y cualquier volcado de la base): contienen nombres, teléfonos y montos de clientes reales.
- Leer o editar `.env`, editar los documentos protegidos (sección 2), `.claude/` o `.git/`.
- Escribir una migración de Clase 3 (sección 8, regla 1).

**Requiere consulta previa:**

- Crear una migración (`makemigrations`) o aplicarla en local (`migrate`), y editar cualquier archivo de `pedidos/migrations/`.
- Crear o cambiar de rama. El flujo vigente es rama única `main`; una rama solo existe si el desarrollador la pide.
- Editar archivos de configuración: `PedidosApp/settings.py`, `PedidosApp/urls.py`, `PedidosApp/wsgi.py`, `manage.py`, `requirements.txt`, `.gitignore`, `.env.example`, el archivo compose del contenedor y la configuración de Tailwind o de `pnpm`.
- Instalar, actualizar o eliminar dependencias de Python o de Node. Cada dependencia nueva requiere justificar su peso, su impacto en el arranque en frío y en el disco, la alternativa sin dependencia y, si es estructural, una RDA.
- Eliminar o mover archivos.
- Ejecutar `mysql`, `mysqldump` o `python manage.py dbshell`, incluso en local.

**Permitido sin consulta:** editar `pedidos/` (salvo `pedidos/migrations/`), `docs/`, `scripts/` y `_planificacion/` (salvo `_planificacion/README.md`); ejecutar los comandos de la sección 5; leer el repositorio.

## 7. Reglas de contenido

1. Todo el texto visible y toda la documentación están en **español de Chile**, trato de **tú**, lenguaje simple y directo, sin anglicismos innecesarios. Montos en pesos chilenos con punto como separador de miles (`$15.000`); teléfonos con formato `+56 9 XXXX XXXX`.
2. **No inventes datos.** Las reglas de negocio (qué significa cada estado, qué incluye un precio, qué se copia al duplicar) las confirma el cliente. Las cifras de producción salen de una medición, nunca de una estimación presentada como dato.
3. Si falta un dato, usa un marcador explícito: `PENDIENTE_CLIENTE` para reglas o datos del negocio y `PENDIENTE_DESARROLLADOR` para decisiones técnicas o de diseño. Regístralo en `registro-pendientes.md`.
4. **Datos personales fuera de la documentación.** Bitácoras, auditorías y evidencias registran conteos, tamaños y tiempos, nunca nombres, teléfonos, correos ni montos de clientes concretos.
5. Nombres de archivo y carpeta en ASCII: minúsculas, guiones, sin tildes ni ñ.

## 8. Reglas técnicas

1. **Clasificación de cambios de esquema.** Toda migración se clasifica antes de proponerla, mirando el SQL que entrega `sqlmigrate`:
   - **Clase 1, metadatos:** etiquetas, textos de ayuda, opciones, orden por defecto, nombres de relación inversa, comportamiento de borrado gestionado por Django. Genera migración, pero MySQL no altera la tabla. Autorizada.
   - **Clase 2, aditiva:** índices, tablas nuevas o columnas que admiten nulo. Altera la tabla sin destruir información. Autorizada, con respaldo previo y ensayo en la réplica local.
   - **Clase 3, destructiva:** renombrar, eliminar, cambiar tipo o imponer obligatoriedad sobre una columna existente. **Prohibida.** Si una corrección la necesita, detente y replantea con el desarrollador.

   Si `sqlmigrate` muestra un `ALTER` donde esperabas Clase 1, la migración no es Clase 1: detente. El SQL de cada migración se copia en la bitácora.
2. **Las migraciones aplicadas no se editan.** Un cambio sobre una migración ya aplicada en producción se hace con una migración nueva.
3. **Atomicidad.** Toda operación que escribe más de una fila relacionada (pedido e ítems, cotización e ítems, conversión de cotización, pago y estado financiero) vive en un único `transaction.atomic()`. Una excepción capturada **dentro** del bloque atómico hace que la transacción se confirme igual: la captura va **fuera** del bloque o la excepción se propaga.
4. **Nada de supresión silenciosa.** Prohibido `except Exception: pass` y equivalentes. Se captura la excepción concreta que se sabe manejar y se registra con el servicio de registro del proyecto. La única captura amplia permitida está dentro del propio servicio de registro, porque el registrador nunca puede hacer fallar una petición; esa captura emite el error a la salida estándar antes de absorberlo.
5. **GET nunca escribe.** Toda vista que crea, modifica, elimina o ejecuta procesos (respaldos, cambios de estado, duplicaciones) acepta solo POST con token CSRF y lo declara con `require_POST` o comprobación explícita del método. En las plantillas, esas acciones son formularios, no enlaces.
6. **Fechas en hora de Chile.** `USE_TZ` está activo y la base guarda UTC. «Hoy» se obtiene con `timezone.localdate()` y los límites de un día o de un mes se construyen con `timezone.localtime()`; `timezone.now().date()` entrega la fecha UTC, que en Chile continental ya es el día siguiente durante las últimas horas de la noche. Los filtros sobre un `DateTimeField` usan rangos explícitos de instantes (`__gte` y `__lt`) en lugar de `__date`, `__month`, `__day` o funciones de truncado y extracción (`TruncMonth`, `ExtractMonth` y similares): estos hacen que MySQL convierta la zona horaria columna por columna, no usan índices y devuelven nulo si el servidor no tiene cargadas sus tablas de zona horaria. `__year` con un valor exacto es la excepción: Django lo traduce a un rango de instantes y no convierte la zona horaria.
7. **Configuración.** Se importa siempre como `from django.conf import settings`, nunca desde el módulo del proyecto. Los secretos y las credenciales vienen solo de variables de entorno; `.env.example` documenta las variables sin valores.
8. **Registro, no `print`.** El diagnóstico usa `logging` y el servicio de registro del proyecto. Ningún `print` en código de aplicación.
9. **Arranque liviano.** Las bibliotecas pesadas que usa una sola vista (por ejemplo WeasyPrint) se importan dentro de la función que las necesita: con un solo worker que hiberna, cada importación al arrancar se paga en cada arranque en frío.
10. **Un worker, peticiones en serie.** Ninguna tarea periódica ni operación lenta corre en el ciclo de una petición: van a la orden de gestión de mantención diaria. Ningún servicio externo de terceros en tiempo de ejecución del servidor: la lista blanca de PythonAnywhere lo impide.
11. **Disco escaso.** Toda tabla nueva nace con su política de retención y su purga implementada en la misma iteración. Ningún registro guarda objetos completos ni archivos.
12. **Consultas.** En listados y detalles, los totales y saldos se calculan con anotaciones del conjunto de consulta (`annotate`, `Coalesce`, `Sum`), no con propiedades del modelo que consultan la base por fila. Las relaciones que la plantilla recorre se cargan con `select_related` o `prefetch_related`. Toda optimización registra en la bitácora el número de consultas antes y después.
13. **Dinero y cantidades.** Los montos son enteros en pesos chilenos. Las cantidades se convierten con `Decimal`, nunca con `float`. El IVA es el 19 % del valor neto, redondeado al peso.
14. **Integridad referencial.** Un registro con historial comercial (cliente con pedidos o cotizaciones, producto usado en ítems) no se elimina en cascada: la relación protege el historial y la vista informa al usuario por qué no se puede borrar.
15. **Pruebas primero en las correcciones.** Cada defecto se corrige escribiendo antes una prueba que falla y que pasa con la corrección. Las pruebas se organizan por dominio en un paquete de pruebas, usan funciones o factorías que construyen datos coherentes y corren contra MySQL.
16. **Dependencias.** Versiones exactas siempre, en Python y en Node. `requirements.txt` se guarda en UTF-8 sin BOM y con fin de línea LF.
17. **Interfaz.** Las plantillas extienden `pedidos/base.html` y siguen `DESIGN.md`. No se agregan recursos nuevos desde CDN. Texto y controles cumplen contraste WCAG 2.2 AA y tienen foco visible.

## 9. Convenciones de la API

La aplicación no expone una API pública. Tiene endpoints internos JSON que el propio JavaScript de la interfaz consume (creación rápida de clientes y productos desde los formularios de pedido y cotización).

- **Rutas:** bajo el prefijo `api/`, en español, con barra final (`api/cliente/nuevo/`).
- **Autenticación:** la misma sesión de Django que el resto de la aplicación; toda ruta exige usuario autenticado.
- **Método y CSRF:** solo POST; el token CSRF viaja en la cabecera `X-CSRFToken`.
- **Respuesta:** `{"success": true, ...datos del objeto creado}` o `{"success": false, "errors": {...}}` con los errores del formulario de Django. Este contrato lo consume `index.js`: cambiarlo requiere cambiar ambos lados en la misma iteración.
- **Validación:** siempre con un formulario de Django; nunca se confía en los datos que calcula el navegador (precios, subtotales, totales).
- **Sin versionado:** el cliente y el servidor se despliegan juntos.
- **Errores del sistema:** se registran con el servicio de registro y no exponen detalles técnicos en la respuesta.

## 10. Flujo de trabajo por iteración

1. Lee el registro y la iteración activa (sección 3).
2. Trabaja sobre `main`. No crees ramas salvo que el desarrollador lo pida.
3. Implementa solo lo descrito en los criterios de aceptación. Si detectas trabajo fuera de alcance, anótalo como propuesta en `registro-pendientes.md`; no lo hagas. **Un despliegue, un propósito:** no mezcles en una iteración correcciones que pertenecen a fases distintas.
4. Ejecuta la iteración completa. Resuelve por tu cuenta todo lo que puedas en local. Lo que exige mirar producción (PythonAnywhere, datos reales, registros del servidor) no lo puedes hacer tú: sigue la sección «Evidencia de producción» de `_planificacion/README.md` y entrega al desarrollador los pasos exactos.
5. Verifica: `python manage.py test pedidos` en verde (salvo las pruebas de regresión que la iteración declara como fallidas a propósito), `python manage.py check` sin errores, `python manage.py makemigrations --check --dry-run` sin cambios no previstos, `sqlmigrate` de cada migración nueva con su clase, y revisión manual de las pantallas tocadas contra la réplica local, en escritorio y en un ancho de 360 px.
6. Escribe la bitácora en `_planificacion/99_bitacora/<epica>/` con la plantilla de `_planificacion/README.md`.
7. Actualiza el estado en `registro-pendientes.md` (historial de una línea con enlace a la bitácora) y, si corresponde, `decisiones.md` y `auditoria-tecnica.md`.
8. Deja la iteración en `En revisión` y entrega al desarrollador un resumen con los archivos modificados, si el despliegue requiere respaldo previo y un mensaje de commit sugerido con el formato `Épica N - Iteración NN-NN: descripción`, en una sola línea de máximo 200 caracteres y en español de Chile; cuenta los caracteres antes de entregarlo. Por ejemplo: `Épica 0 - Iteración 00-06: difiere la carga de WeasyPrint y publica robots.txt`. El commit, la etiqueta y el despliegue los hace el desarrollador.

## 11. Cuándo detenerse y preguntar

- Una corrección necesita una migración de Clase 3.
- `sqlmigrate` muestra SQL distinto del esperado para la clase declarada.
- Falta una regla de negocio que decide el comportamiento (marcada `PENDIENTE_CLIENTE`).
- La tarea contradice una RDA, `DESIGN.md` o el plan de trabajo.
- Hay que agregar una dependencia, cambiar configuración, crear una migración o crear una rama.
- Conviene cambiar un documento protegido (sección 2).
- Un cambio aumentaría el tiempo de arranque en frío, el consumo de disco, el número de consultas por página o el consumo de CPU de la tarea programada.