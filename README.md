# Manza Gráfica App (ERP)

---

## Descripción General del Proyecto

**Manza Gráfica ERP** es una aplicación web monolítica diseñada a medida para la gestión integral de procesos de una empresa de diseño, publicidad e impresión. El sistema centraliza la operación del negocio, abarcando desde la gestión de clientes y la emisión de cotizaciones hasta el control de producción, gestión de inventario y monitoreo de la base de datos.

Aunque la arquitectura es de un **monolito clásico** basado en el patrón Modelo-Vista-Template (MVT), la aplicación implementa funcionalidades propias de un **SaaS** moderno, tales como interfaces reactivas, generación de PDFs en tiempo real, análisis de datos (Business Intelligence) y gestión automatizada de respaldos de la base de datos.

---

## Arquitectura y Diseño Técnico

El sistema está construido sobre un conjunto de tecnologías moderno y escalable.

### Stack Tecnológico

#### Backend
* **Lenguaje:** Python 3.10+
* **Framework:** Django 5.0
* **ORM:** Django ORM para abstracción de base de datos.
* **Utilidades:** `WeasyPrint` para renderizado de reportes PDF, `Subprocess` para gestión de comandos del sistema operativo (respaldos).

#### Base de Datos
* **Motor:** MySQL 8.0 (Producción y Desarrollo Dockerizado).
* **Diseño:** Modelo relacional normalizado con integridad transaccional (`ACID`).
* **Optimización:** Uso de índices y consultas de agregación (`Aggregate`, `Annotate`, `TruncMonth`) para métricas de rendimiento.

#### Frontend
* **Estructura:** HTML5 semántico renderizado por el motor de plantillas de Django (Jinja2 syntax).
* **Estilos:** Tailwind CSS para diseño responsivo y sistema de modo oscuro/claro.
* **Scripting:** JavaScript (Vanilla ES6+) y jQuery para manipulación del DOM y peticiones AJAX asíncronas.
* **Componentes UI:** Select2 para selectores avanzados, Summernote para edición de texto enriquecido (WYSIWYG), SweetAlert2 para notificaciones modales.

#### Infraestructura y Despliegue
* **Entorno Local:** Contenedores Docker para servicios de base de datos.
* **Producción:** Despliegue en plataforma PaaS (PythonAnywhere) sobre servidor WSGI.
* **Gestión de Archivos:** `FileSystemStorage` para manejo seguro de medios y archivos temporales de respaldo.

---

## Módulos del Sistema

La aplicación se divide en módulos lógicos que encapsulan reglas de negocio específicas:

### 1. Panel de Control (Dashboard)
Centro de mando que visualiza KPIs financieros y operativos en tiempo real.
* **Métricas:** Ingresos totales, cuentas por cobrar, tasa de finalización de pedidos.
* **Visualización:** Gráficos CSS puros (Conic Gradients) y barras de progreso para distribución de estados de pedidos.

### 2. Gestión de Pedidos y Producción
Núcleo operativo del sistema.
* **CRUD Completo:** Creación, lectura, actualización y eliminación (lógica o física) de pedidos.
* **Items Complejos:** Manejo de relación uno a muchos para ítems de pedido con cálculo de precios unitarios y subtotales.
* **Trabajo Semanal:** Vista tipo Kanban/Agenda que clasifica pedidos en *Críticos*, *Urgentes* y *Normales* según fecha de entrega, detectando "Peak Loads" (días de saturación).

### 3. Cotizaciones y Conversión
Módulo comercial para la negociación previa a la venta.
* **Generación de PDF:** Renderizado de cotizaciones formales descargables.
* **Ciclo de Vida:** Estados de flujo (*Borrador*, *Enviada*, *Aceptada*).
* **Conversión:** Funcionalidad para transformar una cotización aprobada directamente en un Pedido activo, migrando todos los ítems y datos del cliente automáticamente.

### 4. Inteligencia de Negocios y Analítica
Módulos dedicados a la interpretación de datos históricos.
* **Analítica de Ventas:** Cálculo de crecimiento porcentual mes a mes, eficiencia operativa y proyección de ingresos.
* **Gráficos SVG Server-Side:** Generación de gráficos vectoriales (SVG) calculados matemáticamente en el backend (Python) para visualizar tendencias de 12 meses sin depender de librerías JS pesadas.

### 5. Administración de Base de Datos
Módulo crítico para la seguridad y mantenimiento de la información (acceso restringido a Superusuarios).
* **Respaldo (Backup):** Ejecución programada o manual de `mysqldump` con política de rotación de archivos (retención de los últimos 5 respaldos).
* **Restauración (Restore):** Capacidad de inyectar volcados SQL para recuperación de desastres, incluyendo validaciones de seguridad y respaldos de emergencia previos a la ejecución.
* **Monitoreo:** Inspección directa a `information_schema` para calcular el peso real (MB) de datos e índices, registrando la evolución del almacenamiento diariamente.

---

## Seguridad

El sistema implementa múltiples capas de seguridad:
* **Decoradores de Vista:** `@login_required` y `@user_passes_test(es_superusuario)` para control de acceso (RBAC).
* **Protección CSRF:** Tokens de seguridad en todos los formularios POST.
* **Transacciones Atómicas:** Uso de `transaction.atomic` (vía decorador personalizado `@transaccion_segura`) para asegurar la integridad de datos en operaciones complejas.
* **Sanitización:** Uso de ORM para prevenir inyecciones SQL y validación estricta de archivos subidos.

---

## Desarrollador

Francisco Felipe Cuevas Cerón.