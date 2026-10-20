# Iteración 01-02 · Servicio de registro

- **Épica:** 01 · Observabilidad
- **Estado:** Pendiente
- **Subfase del plan:** 1.2
- **Depende de:** 01-01, 02-01
- **RDA relacionadas:** RDA-005, RDA-008 y una RDA nueva con el diseño del aislamiento
- **Hallazgos que cierra:** ninguno por sí sola. Avanza AUD-01-005.
- **Cambio de esquema:** Ninguno
- **Respaldo previo al despliegue:** Sí (se despliega en 01-06)

## Objetivo

Un servicio con dos funciones públicas, registrar un error y registrar un evento, diseñado para que las cuatro trampas del plan queden resueltas por construcción y demostradas por pruebas. Es la iteración de mayor densidad conceptual de todo el plan.

## Tareas

1. **Diseño escrito como RDA** en `decisiones.md` antes de programar, con una sección por trampa:
   1. **Aislamiento transaccional:** la escritura del error no puede revertirse junto con la transacción que falló. Evaluar al menos dos técnicas (por ejemplo, un segundo alias de base de datos con su propia conexión, o escribir fuera del bloque atómico) con sus costos en un worker único y en las pruebas.
   2. **Dependencia circular:** si la base está caída o la escritura falla, el error se emite igualmente a la salida estándar con el identificador de correlación.
   3. **Fallo en cascada:** el servicio nunca lanza una excepción hacia quien lo llama. Esta es la única captura amplia permitida del proyecto (`AGENTS.md`, regla 4), y el código lo dice con un comentario.
   4. **Costo por petición:** el servicio solo se invoca para errores y para el inventario de eventos; nunca en lecturas ordinarias.
2. **Identificador de correlación**: cómo se genera, cómo se asocia a la petición y cómo llega a la página de error.
3. **Registro de eventos después de confirmar**: el evento se escribe solo cuando la operación de negocio se confirmó en la base (por ejemplo, con `transaction.on_commit`), para no registrar acciones que no ocurrieron.
4. **Implementación** en un módulo propio dentro de `pedidos/`, usando `logging` para la salida estándar. Si el diseño requiere un segundo alias de base de datos, el cambio en `settings.py` requiere consulta.
5. **Pruebas**, una por trampa como mínimo.

## Criterios de aceptación

- [ ] La RDA del diseño está escrita con las cuatro trampas y la alternativa descartada en cada caso.
- [ ] Prueba de aislamiento: un error registrado dentro de un bloque atómico que luego se revierte sigue en la tabla de errores.
- [ ] Prueba de dependencia circular: con la escritura en la base forzada a fallar, el error aparece en la salida capturada de `logging` con su identificador.
- [ ] Prueba de fallo en cascada: con una excepción inyectada dentro del servicio, la función retorna sin lanzar.
- [ ] Prueba de costo: el número de consultas de una vista de listado no cambia con el servicio instalado (`assertNumQueries` con el mismo valor antes y después).
- [ ] Prueba de eventos: un evento registrado dentro de una transacción que se revierte no queda en la tabla; uno dentro de una transacción confirmada, sí.
- [ ] `python manage.py test pedidos` en verde.

## Fuera de alcance

- Conectar el servicio al sistema de registro de Django y retirar el middleware (va en 01-03).
- Llamar al servicio desde las vistas de negocio (va en 01-04).

## Datos requeridos del cliente

- Ninguno.
