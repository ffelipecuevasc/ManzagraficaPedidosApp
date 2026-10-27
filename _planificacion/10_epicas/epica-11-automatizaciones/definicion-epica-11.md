# Épica 11 · Automatizaciones y notificaciones por correo

- **Estado:** Pendiente
- **Fase del plan:** no existe en el plan original; anexo del plan del 2026-10-27 (RDA-014)
- **Objetivo:** que la aplicación avise por correo, sin que nadie tenga que entrar a mirar, de las situaciones que le importan al dueño: pedidos impagos, pedidos muy atrasados y otras que el desarrollador elija. Cada automatización se configura desde la propia aplicación, solo por superusuarios.
- **Precondición:** 06-02 desplegada (la orden de mantención diaria es el único lugar donde corren las automatizaciones), Épica 09 completa (los destinatarios son usuarios con correo y rol), Épicas 07 y 08 completas.
- **Última revisión:** 2026-10-27 (creada a pedido del desarrollador).

## Restricciones de la plataforma que dan forma a la épica (verificadas el 2026-10-27)

- **Una sola tarea diaria** (RDA-004 y RDA-009): las automatizaciones son un paso más de `mantencion_diaria`, con manejo de error propio. Todas se evalúan una vez al día, a la hora de la tarea; «configurable» significa activar o desactivar, umbrales, destinatarios y días de la semana, no la hora exacta.
- **Correo saliente en el plan gratuito:** el único SMTP permitido es el de Gmail, con contraseña de aplicación; la otra vía es una API por HTTPS de un servicio que esté en la lista blanca de PythonAnywhere (por ejemplo Brevo, `api.brevo.com`).
- **100 segundos de CPU diarios** compartidos con métricas, purga y respaldo: cada automatización mide su consumo.

## Alcance

1. **Canal de correo (11-01):** elegir el canal (Gmail con contraseña de aplicación o una API como Brevo) con una RDA; credenciales solo en `.env`; plantillas de correo en DTL (texto plano y HTML simple); orden `enviar_correo_prueba` para verificar el canal en producción.
2. **Configuración de automatizaciones desde la web (11-02):** una tabla nueva (Clase 2) con una fila por automatización: activa o no, umbral (por ejemplo, días de atraso o monto mínimo), días de la semana en que se envía y destinatarios (superusuarios, y opcionalmente operadores). Pantalla solo para superusuarios, construida con los parciales de la Épica 08. Cada cambio de configuración deja un evento.
3. **Aviso de pedidos impagos (11-03):** resumen con la cantidad de pedidos con saldo pendiente, el monto total y el detalle de los más antiguos, con enlace a cada pedido. Usa los selectores de saldo de la 07-02.
4. **Aviso de pedidos muy atrasados (11-04):** pedidos activos cuya fecha de entrega venció hace más de N días (N configurable), ordenados por atraso.
5. **Registro de cada envío:** cada correo enviado (o fallido) deja un evento (`notificacion_enviada`, `notificacion_fallida`), sin copiar el contenido del correo. Amplía el inventario de RDA-008: se estima de nuevo el crecimiento.

## Ideas propuestas para nuevas automatizaciones (el desarrollador elige; cada una sería una iteración 11-05 en adelante)

| Idea | Qué avisa | Para quién |
| :--- | :-------- | :--------- |
| **Agenda de mañana** | Pedidos con entrega al día siguiente, enviado temprano | Superusuarios y operadores |
| **Cotizaciones sin respuesta** | Cotizaciones no convertidas tras N días, para hacer seguimiento comercial | Superusuarios |
| **Salud del sistema** | Disco sobre el umbral de la 06-03, último respaldo con más de 16 días o la orden diaria que no corrió ayer (responde a la pregunta abierta de RDA-009) | Superusuarios |
| **Resumen semanal** | Pedidos del período, monto cobrado y por cobrar | Superusuarios |

## Iteraciones

| Iteración | Nombre |
| :-------- | :----- |
| 11-01 | Canal de correo |
| 11-02 | Configuración de automatizaciones desde la web |
| 11-03 | Aviso de pedidos impagos |
| 11-04 | Aviso de pedidos muy atrasados |
| 11-05 en adelante | Una por cada idea que el desarrollador elija |

## Decisiones de la épica

- Canal de correo (Gmail con contraseña de aplicación o API por HTTPS): `PENDIENTE_DESARROLLADOR`, se decide en 11-01 con una RDA. Una cuenta de Gmail del negocio, no la personal del desarrollador.
- Qué ideas propuestas se implementan: `PENDIENTE_DESARROLLADOR`.
- Un correo que falla no detiene la orden de mantención ni los otros pasos (RDA-009); el fallo queda en `server.log` y como evento.

## Fuera de alcance

- **Correos a los clientes de Manza Gráfica** (avisos de entrega o cobranza a terceros): exigen consentimiento, cuidar la reputación del remitente y redactar textos comerciales. Se evalúan aparte si el negocio lo pide.
- Notificaciones por WhatsApp, SMS o mensajería: no están en la lista blanca del plan gratuito o requieren servicios pagados.
- Envíos en tiempo real (al momento de crear un pedido): todo pasa por la tarea diaria.

## Criterio de término

- El correo de prueba llega a la casilla del superusuario desde producción.
- Las automatizaciones 11-03 y 11-04 se activan, desactivan y ajustan desde la web, y la orden diaria envía solo las activas el día configurado (pruebas automatizadas con el correo simulado y la hora fijada).
- Cada envío deja su evento, y el consumo de CPU de la orden diaria sigue bajo los 100 segundos.

## Notas

- **2026-10-27:** creada a pedido del desarrollador («automatización de tareas con Python»). Las ideas de la tabla son propuestas del asistente.
