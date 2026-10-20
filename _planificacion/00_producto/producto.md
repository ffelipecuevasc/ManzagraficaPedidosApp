# Producto · Manza Gráfica App

- **Cliente:** Manza Gráfica (diseño, publicidad e impresión)
- **Desarrollador:** Francisco Felipe Cuevas Cerón · https://felipecuevas.dev
- **Documento base:** `plan-de-trabajo.md` (Plan de Trabajo Técnico — ManzagraficaPedidosApp)
- **Última revisión:** 2026-10-19

---

## 1. Propósito

Que el equipo de Manza Gráfica pueda cotizar, registrar, producir, entregar y cobrar sus trabajos en un solo sistema confiable, y que ese sistema nunca pierda ni corrompa en silencio el historial comercial que ya contiene.

El trabajo de este ciclo no agrega funciones de negocio: convierte una aplicación que funciona en una aplicación en la que se puede confiar, que se puede diagnosticar cuando falla y que se puede cambiar sin miedo.

## 2. Qué es

1. Una aplicación web interna, con acceso por usuario y contraseña, para el equipo de la empresa.
2. Un registro de clientes, catálogo de productos, cotizaciones, pedidos con ítems, pagos y producción semanal, ya en uso con datos reales.
3. Un monolito Django publicado en el plan gratuito de PythonAnywhere, que debe funcionar dentro de sus límites (disco, un solo proceso, una tarea diaria, sin servicios externos).
4. En este ciclo, un proyecto de **mejora continua**: blindaje, observabilidad, pruebas, integridad, seguridad, rendimiento, arquitectura y operación, en ese orden de dependencias.

## 3. Qué no es

1. No es un sitio público ni una tienda en línea: no hay registro de clientes externos, carrito ni pagos en línea.
2. No es un sistema contable ni tributario: no emite boletas ni facturas electrónicas.
3. No es un inventario de stock: el catálogo de productos fija precios, no existencias.
4. No es una API para terceros: los endpoints JSON existen solo para la propia interfaz.
5. En este ciclo no se agregan módulos ni funciones de negocio nuevas; las ideas que aparezcan se anotan como propuestas fuera de alcance.
6. No se cambia de hosting ni de plan como parte de este trabajo; el plan define de antemano las señales que justificarían evaluarlo.

Cualquier sección o función adicional se cotiza por separado.

## 4. Público objetivo

| Perfil | Situación | Qué necesita del producto |
| :----- | :-------- | :------------------------ |
| Equipo de atención y ventas | Atiende clientes y les escribe por WhatsApp desde la aplicación | Crear cotizaciones y pedidos rápido, encontrar al cliente por nombre o teléfono, registrar el abono en el momento |
| Equipo de producción | Planifica la semana según fechas de entrega | Ver qué está atrasado, qué vence esta semana y cambiar el estado del pedido sin errores |
| Dueño o administración | Revisa el estado del negocio y la cobranza | Saldos pendientes confiables, deudas de trabajos terminados, evolución mensual |
| Superusuario (desarrollador) | Mantiene el sistema y la base de datos | Respaldos verificables, diagnóstico de errores sin entrar al servidor, despliegues reversibles |

El número de usuarios, sus roles exactos y los dispositivos que usan son `PENDIENTE_CLIENTE`.

Condiciones de uso a considerar en todo diseño:

- La aplicación hiberna por inactividad: la primera visita del día puede tardar varios segundos en responder.
- Un solo proceso atiende todas las peticiones en serie: una página lenta hace esperar a todos los usuarios.
- Los datos son reales y no tienen otra copia que los respaldos: un error silencioso es pérdida de información comercial.

## 5. Idioma y tono

- Todo el producto está en **español de Chile**: ortografía, vocabulario local y formato de números chilenos (`$15.000`, `+56 9 XXXX XXXX`).
- Trato de **tú**, frases cortas y directas, sin tecnicismos innecesarios.
- Los mensajes de error al usuario no muestran detalles técnicos; muestran qué pasó, qué hacer y un identificador para informar el problema.

## 6. Indicadores de éxito

1. **Retroceso garantizado:** ante un despliegue fallido, volver al estado anterior en menos de 15 minutos sin perder datos, con el procedimiento ensayado al menos una vez.
2. **Diagnóstico remoto:** un error real en producción se diagnostica en menos de 5 minutos sin acceso al servidor.
3. **Integridad:** una operación compuesta que falla a mitad de camino no deja rastro en la base de datos; lo comprueban las pruebas de regresión en verde.
4. **Seguridad:** `python manage.py check --deploy` sin advertencias y ninguna ruta que modifique datos por GET.
5. **Rendimiento:** reducción medida del tiempo hasta el primer contenido pintado, del peso transferido, del número de peticiones y del número de consultas por página en las tres vistas más usadas, contra la línea base.
6. **Operación autónoma:** la tarea diaria se ejecuta sola y deja constancia de cada ejecución; el uso de disco está vigilado con un umbral.

## 7. Hitos comprometidos

| Semana o fecha | Hito | Referencia |
| :------------- | :--- | :--------- |
| PENDIENTE_DESARROLLADOR | Fase 0 completa: respaldo verificado, réplica local y retroceso ensayado | Épica 00 |
| PENDIENTE_DESARROLLADOR | Fases 1 y 2 completas: observabilidad y red de pruebas | Épicas 01 y 02 |
| PENDIENTE_DESARROLLADOR | Fase 3 completa: integridad transaccional en producción | Épica 03 |

El plan no es un cronograma sino una secuencia de dependencias: las fases 0, 1, 2 y 3 van en ese orden estricto; las fases 4, 5 y 6 pueden reordenarse según la prioridad del negocio siempre que se cumplan sus precondiciones.
