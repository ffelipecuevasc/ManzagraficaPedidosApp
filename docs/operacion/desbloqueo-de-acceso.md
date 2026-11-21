# Desbloqueo del acceso

Desde la iteración 04-08 (`v4.10-acceso-limites`), la aplicación bloquea el acceso por un tiempo cuando hay demasiados intentos fallidos. Esta página explica qué ve la persona bloqueada y cómo se vuelve a entrar.

## Qué pasa

- **5 contraseñas equivocadas seguidas con el mismo usuario** en 15 minutos bloquean ese usuario por **15 minutos**, desde cualquier computador.
- **20 intentos fallidos desde una misma conexión** en 15 minutos, con cualquier usuario, bloquean esa conexión por **15 minutos**.
- Vale para las dos entradas: la de la aplicación (`/accounts/login/`) y la del admin. Los intentos se suman entre ambas.
- La pantalla dice: «Acceso bloqueado por 15 minutos. Hubo demasiados intentos fallidos. Espera 15 minutos y vuelve a intentarlo.» El mensaje es el mismo aunque el usuario no exista.
- Mientras dura el bloqueo, **ni la contraseña correcta deja entrar**.
- Un acceso correcto antes del quinto error borra la cuenta de errores de ese usuario.
- Cada bloqueo deja **un** evento «Acceso bloqueado» en el admin (Registro de eventos), sin la dirección ni el nombre escrito.

## Cómo volver a entrar

1. **Esperar 15 minutos** y volver a intentar con la contraseña correcta. Es lo normal y no requiere nada más.
2. **Si no se puede esperar: recargar la aplicación.** En el panel de PythonAnywhere, pestaña **Web**, botón **Reload**. Recargar borra todos los contadores y bloqueos, de todos los usuarios, porque viven en la memoria de la aplicación. La aplicación queda unos segundos sin responder mientras arranca.
   - Desde la consola no se puede desbloquear: la memoria de la aplicación no es accesible desde ahí.
3. **Si después de recargar todos siguen bloqueados una y otra vez** (por ejemplo, después de pocos errores de personas distintas), la aplicación está viendo a todos como si vinieran de la misma conexión. Interruptor de emergencia:
   1. En el archivo `.env` del servidor, pon `ACCESO_FALLOS_POR_DIRECCION=0`. Eso apaga solo el contador por conexión; el de usuario sigue.
   2. **Reload**.
   3. Avisa al desarrollador para corregir `ACCESO_PROXIES_CONFIABLES` (`despliegue.md`, sección 3.15 C).
   - **No** pongas `ACCESO_PROXIES_CONFIABLES=0` para arreglarlo: haría que la aplicación vea la dirección del proxy de PythonAnywhere, que es la misma para todos.
4. **Último recurso:** volver a la versión anterior (`retroceso.md`, caso 2, que vale para esta migración de Clase 1).

## Qué no hace

- No frena una inundación de peticiones (DoS): con un solo proceso, eso se contiene en la red de PythonAnywhere.
- No sobrevive a una recarga: cada Reload, despliegue o reinicio del servidor borra los contadores. Frena la fuerza bruta, no la hace imposible; la defensa de fondo sigue siendo una buena contraseña.
- No cambia la recuperación de contraseña ni el acceso propio del admin (AUD-02-030).
