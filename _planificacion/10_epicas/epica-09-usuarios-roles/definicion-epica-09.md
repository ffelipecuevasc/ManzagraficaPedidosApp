# Épica 09 · Usuarios y roles

- **Estado:** Pendiente
- **Fase del plan:** no existe en el plan original; anexo del plan del 2026-10-27 (RDA-014)
- **Objetivo:** que Ignacio (dueño de Manza Gráfica, superusuario) pueda administrar desde la propia aplicación las cuentas de su equipo, con dos roles: **superusuario** y **operador**. Con varias personas usando el sistema, la tabla de eventos de la Épica 01 pasa a responder de verdad «quién hizo qué».
- **Precondición:** 04-07 desplegada (**obligatoria**: sin sanitizar el HTML enriquecido, un operador podría ejecutar código en la sesión de un superusuario, AUD-03-001), 04-08 desplegada (más cuentas, más superficie para fuerza bruta), Épicas 07 y 08 completas (el módulo nace en la estructura nueva y con los parciales) y 02-05 terminada (las pruebas de control de acceso son la red de esta épica).
- **Última revisión:** 2026-10-27 (creada a pedido del desarrollador).

## Roles (RDA-017)

| Rol | Cómo se representa | Puede | No puede |
| :-- | :----------------- | :---- | :------- |
| **Superusuario** | `is_superuser=True` y `is_staff=True` en la tabla nativa `auth_user` | Todo, incluido el módulo de base de datos («Estadísticas BD», «Respaldar BD», «Restaurar BD»), el módulo de usuarios y el admin de Django | — |
| **Operador** | Usuario activo con `is_superuser=False` e `is_staff=False` | Todo el trabajo diario: clientes, productos, cotizaciones, pedidos, pagos, estadísticas de negocio y trabajo semanal | Entrar al módulo de base de datos, al módulo de usuarios ni al admin de Django |

No se crean grupos, permisos por modelo ni tablas nuevas: con dos roles, el indicador `is_superuser` ya distingue todo lo necesario (decisión del desarrollador del 2026-10-27). Si algún día aparece un tercer rol, se evalúa `Group` de Django con una RDA nueva.

## Alcance

1. **Control de acceso centralizado (09-01):** un único decorador (o mixin) `solo_superusuario` reemplaza los `user_passes_test(es_superusuario)` repartidos en las vistas y protege el módulo de base de datos y el nuevo módulo de usuarios. Se define qué recibe un operador que intenta entrar (propuesta: respuesta 403 con la página de error del proyecto, en lugar de la redirección al acceso que hace hoy `user_passes_test`). La navegación (`_nav.html` de la Épica 08) no muestra a un operador las opciones que no puede usar. Las pruebas de la 02-05 se amplían con un usuario operador.
2. **Módulo de gestión de usuarios (09-02), solo superusuarios:**
   - listado de usuarios con su rol y su último acceso;
   - crear usuario con nombre de usuario, nombre, correo (lo usará la Épica 11), rol y contraseña inicial, validada con `AUTH_PASSWORD_VALIDATORS`;
   - editar nombre, correo y rol;
   - restablecer la contraseña de otro usuario;
   - **cambio de la propia contraseña** para cualquier usuario, superusuario u operador (vistas nativas de Django).
3. **Eliminación de usuarios con confirmación (09-03):** por decisión del desarrollador, un usuario **se borra de la base** (no se desactiva). El borrado exige:
   - una página de confirmación que explique las consecuencias con cifras: cuántos pedidos, pagos y eventos quedarán sin autor;
   - escribir el nombre de usuario para habilitar el botón (segunda confirmación);
   - petición POST con token CSRF.

   Reglas que la vista impide: un usuario no puede borrarse a sí mismo y el sistema nunca queda sin superusuario. El evento `usuario_eliminado` se registra a nombre de quien borra y guarda en su resumen el nombre de usuario borrado.
4. **Eventos de la gestión de usuarios (en 09-02 y 09-03):** `usuario_creado`, `usuario_modificado`, `rol_cambiado`, `contrasena_restablecida` y `usuario_eliminado`. Amplía el inventario cerrado de RDA-008: se estima de nuevo el crecimiento (despreciable) y se agregan las opciones al campo de tipo (migración de Clase 1).

## Iteraciones

| Iteración | Nombre |
| :-------- | :----- |
| 09-01 | Control de acceso centralizado por rol |
| 09-02 | Módulo de gestión de usuarios |
| 09-03 | Eliminación de usuarios con confirmación |

## Decisiones de la épica

- **2026-10-27 · Dos roles sobre la tabla nativa, sin grupos (RDA-017, decisión del desarrollador).**
- **2026-10-27 · Borrado físico con doble confirmación (RDA-017, decisión del desarrollador).** **Consecuencia que se acepta:** `Pedido.creado_por`, `Pago.registrado_por` y `RegistroEvento.usuario` usan `on_delete=SET_NULL`, así que al borrar un usuario esos registros quedan sin autor y su autoría solo sobrevive en el texto del resumen de cada evento. La página de confirmación lo informa antes de borrar.
- ¿El evento guarda una copia del nombre del usuario en una columna propia (Clase 2), para que la autoría sobreviva al borrado en todos los eventos y no solo en el resumen? `PENDIENTE_DESARROLLADOR`, se decide en 09-03.
- Respuesta a un operador que entra a una ruta prohibida (403 o redirección): `PENDIENTE_DESARROLLADOR`, se decide en 09-01.
- El admin de Django sigue disponible solo para superusuarios; el módulo nuevo existe porque el admin no está pensado para el uso diario de Ignacio.

## Fuera de alcance

- Más de dos roles o permisos por modelo.
- Registro de usuarios desde fuera ni recuperación de contraseña por correo (exigiría el canal de correo de la Épica 11; se puede evaluar allí).
- Desactivar usuarios en lugar de borrarlos (descartado por el desarrollador).

## Criterio de término

- Un operador recibe la respuesta definida en todas las rutas del módulo de base de datos, del módulo de usuarios y del admin (pruebas automatizadas que recorren las rutas).
- Un superusuario crea, edita, cambia de rol, restablece la contraseña y borra un usuario desde la web, y cada acción deja su evento.
- Ninguna combinación de acciones deja el sistema sin superusuario ni permite borrarse a sí mismo (pruebas automatizadas).
- El borrado no procede sin la segunda confirmación.

## Notas

- **2026-10-27:** creada a pedido del desarrollador. Medido en la réplica (volcado del 2026-10-20): hoy hay un solo usuario y es superusuario.
