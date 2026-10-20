# Manza Gráfica App

Aplicación web interna para gestionar los clientes, cotizaciones, pedidos, pagos y producción de Manza Gráfica, una empresa de diseño, publicidad e impresión.

🔹 **Sitio:** https://manzagrafica.pythonanywhere.com (acceso privado con usuario y contraseña)
🔹 **Repositorio:** https://github.com/ffelipecuevasc/ManzagraficaPedidosApp
🔹 **Desarrollo:** Francisco Felipe Cuevas Cerón · https://felipecuevas.dev

---

## 1. De qué trata el proyecto

Una imprenta pequeña vive de muchos trabajos cortos que se cotizan, se aceptan, se producen, se entregan y se cobran, muchas veces en abonos. Llevar eso en planillas o en mensajes hace que se pierdan pedidos, que no se sepa qué urge esta semana y que nadie tenga claro cuánto falta por cobrar. Esta aplicación reúne todo ese ciclo en un solo lugar para el equipo de la empresa.

Funciones principales:

1. **Panel de control:** pedidos atrasados, pedidos que vencen en los próximos siete días, distribución de estados del mes, mejores clientes y fecha del último respaldo.
2. **Pedidos:** registro con ítems del catálogo y precio congelado al momento de la venta, imagen de referencia, abono inicial, estados de producción (pendiente, en proceso, terminado, entregado) y reapertura de un pedido terminado como pedido nuevo.
3. **Trabajo semanal:** clasifica los pedidos activos en críticos, urgentes y normales según su fecha de entrega, y detecta el día con más entregas.
4. **Cotizaciones:** propuestas con validez en días, estados de negociación, descarga en PDF y conversión directa en pedido.
5. **Catálogo de productos:** productos y servicios con unidad de medida (unitario, metro cuadrado, metro lineal) y cálculo automático del IVA.
6. **Pagos:** abonos por pedido con método de pago, saldo pendiente y un panel financiero con deudas de trabajos terminados y pedidos en riesgo.
7. **Estadísticas:** evolución mensual de pedidos, crecimiento respecto del mes anterior y tasa de pedidos terminados.
8. **Administración de la base de datos:** respaldo y restauración, y evolución del peso de la base. Solo para superusuarios.

## 2. Tecnologías y para qué sirve cada una

🔸 **Python y Django:** el lenguaje y el marco web que resuelven todo el servidor: rutas, vistas, formularios, plantillas, sesiones y el panel de administración.
🔸 **Django ORM:** traduce los modelos de Python (cliente, pedido, pago) a tablas y consultas SQL, de modo que el código casi no escribe SQL a mano.
🔸 **Sistema de autenticación de Django:** inicio de sesión, permisos y la distinción entre usuarios y superusuarios.
🔸 **MySQL:** la base de datos relacional donde vive todo el historial comercial.
🔸 **Docker:** levanta en local un MySQL idéntico al de producción, para probar los cambios contra una copia real de los datos.
🔸 **WeasyPrint:** convierte una plantilla HTML en el PDF de una cotización.
🔸 **Tailwind CSS:** el sistema de clases utilitarias con que se escriben los estilos, con modo claro y oscuro.
🔸 **JavaScript, jQuery, Select2, Summernote y SweetAlert2:** la parte interactiva de los formularios: agregar ítems sin recargar la página, buscadores en los selectores, edición de texto enriquecido y avisos modales.
🔸 **PythonAnywhere:** el servicio donde la aplicación está publicada.
🔸 **GitHub y PyCharm:** control de versiones y entorno de desarrollo.

## 3. Cómo está construido

Es un **monolito** de Django con el patrón Modelo-Vista-Plantilla: una sola aplicación, `pedidos`, contiene los modelos, las vistas, los formularios, las plantillas y los archivos estáticos.

- Los **modelos** describen el negocio: clientes, pedidos con sus ítems, cotizaciones con sus ítems, productos, pagos y un historial diario del peso de la base de datos.
- Las **vistas** reciben cada petición, consultan los modelos y entregan una plantilla renderizada en el servidor. Las estadísticas y los gráficos se calculan en Python y se dibujan como SVG, sin bibliotecas de gráficos en el navegador.
- El **navegador** recibe HTML ya armado. JavaScript solo se ocupa de lo interactivo: la tabla de ítems de un pedido se arma en la página y viaja al servidor dentro del formulario, y unos pocos endpoints internos permiten crear un cliente o un producto sin salir del formulario.
- Las **operaciones de base de datos** (respaldo y restauración) llaman a las herramientas de línea de comandos de MySQL desde Python.

Dos restricciones del servicio de publicación moldean todo el diseño: la aplicación atiende las peticiones de una en una (un solo proceso) y comparte 512 MiB de disco entre archivos, respaldos y base de datos. Por eso las tareas periódicas no corren dentro de las peticiones y toda tabla que crece tiene una política de limpieza.

## 4. Organización del repositorio

```text
ManzagraficaPedidosApp/
├── PedidosApp/          Configuración del proyecto Django: ajustes, rutas principales y punto de entrada WSGI
├── pedidos/             La aplicación: modelos, vistas, formularios, rutas, migraciones,
│   │                    utilidades de respaldo y métricas
│   ├── templates/       Plantillas HTML de cada pantalla, del PDF y de las páginas de error
│   └── static/          Hoja de estilos, JavaScript propio e ícono del sitio
├── backups/             Respaldos generados en el servidor (su contenido nunca se versiona)
├── docs/operacion/      Procedimientos de respaldo, réplica local, despliegue y retroceso
├── _planificacion/      Producto, decisiones, auditorías, épicas, iteraciones y bitácoras
├── .claude/             Permisos de los agentes de IA y su explicación
├── AGENTS.md            Reglas y comandos para los agentes de IA
├── DESIGN.md            Sistema de diseño de la interfaz
├── LICENSE              Licencia MIT del código
├── manage.py            Utilidad de administración de Django
└── requirements.txt     Dependencias de Python con versión exacta
```

## 5. Qué necesitas para trabajar con el proyecto

Python 3.13, Docker para el MySQL 8.0 local y un archivo de variables de entorno basado en `.env.example`. Para recompilar los estilos, Node.js con pnpm. Los comandos de desarrollo, pruebas y revisión están en `AGENTS.md`.

## 6. Cómo se publica

La aplicación corre en PythonAnywhere sobre un servidor WSGI, con la base de datos MySQL del mismo servicio. Cada versión publicada queda marcada con una etiqueta en el repositorio, de modo que siempre existe un punto exacto al que volver. Antes de publicar se descarga y verifica un respaldo de la base, se corren las pruebas y la revisión de despliegue de Django, y se confirma que las migraciones pendientes no destruyen datos. El procedimiento completo, incluido el retroceso, está en `docs/operacion/`.

## 7. Metodología de trabajo

El desarrollo se organiza en épicas e iteraciones documentadas en `_planificacion/`, y cada épica corresponde a una fase del plan de trabajo técnico (blindaje, observabilidad, pruebas, integridad, seguridad, rendimiento, arquitectura y operación). Cada iteración deja una bitácora con lo que se hizo y cómo se verificó, y las decisiones técnicas se registran como RDA (Registro de Decisión Arquitectónica). El detalle está en `_planificacion/README.md`.

Los agentes de IA que colaboran en el proyecto siguen las reglas de `AGENTS.md`. Los commits, pushes, etiquetas y despliegues los hace exclusivamente el desarrollador.

## 8. Autoría y licencia

Desarrollado por **Francisco Felipe Cuevas Cerón** (https://felipecuevas.dev) para **Manza Gráfica**.

Licencia: MIT (ver `LICENSE`). La licencia cubre el código del repositorio; el nombre, el logo y la marca Manza Gráfica pertenecen a su dueño y no están incluidos en ella.