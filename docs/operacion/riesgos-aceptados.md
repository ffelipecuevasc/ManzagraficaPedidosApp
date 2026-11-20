# Riesgos aceptados y decisiones solo documentadas

Riesgos que se conocen y se aceptan a propósito, sin una iteración que los cambie. Cada nota dice qué pasa, por qué se acepta, qué lo sostiene y qué hacer si cambia la situación. Esta página no crea reglas nuevas: las decisiones las tomó el desarrollador el 2026-11-17 ([definicion-epica-04](../../_planificacion/10_epicas/epica-04-seguridad/definicion-epica-04.md), «Hallazgos sin iteración») y se escribieron aquí en la iteración 04-07.

- **Creado en:** iteración 04-07 (2026-11-20).
- **Lo revisa:** el desarrollador, cuando una iteración toque alguno de estos puntos.
- **La copia de `media/` (AUD-02-023)** no está aquí: está en [respaldo.md](respaldo.md), sección 7, porque es parte del respaldo.

## 1. La búsqueda queda en los registros de la plataforma (AUD-04-003, riesgo aceptado)

**Qué pasa.** Los cuatro listados con búsqueda la envían por GET, con `?busqueda=` en la dirección. Lo que alguien busca (por ejemplo, un nombre o un teléfono) queda escrito en `access.log` y en `server.log` de PythonAnywhere.

**Por qué se acepta.** Los registros solo los ve el titular de la cuenta de la plataforma. El referente solo se envía al mismo sitio (`SECURE_REFERRER_POLICY = "same-origin"`), así que los CDN que carga la página no reciben la búsqueda.

**Qué se descartó.**
- Buscar por POST: al volver atrás, el navegador pide confirmar el reenvío, y ya no se puede compartir el enlace de una búsqueda.
- Usar POST con redirección y guardar la búsqueda en la sesión: más código y más estado.
- Buscar solo por nombre: cambia una función.

**Qué hacer si cambia.** Si otra persona obtiene acceso a los registros de la plataforma, o si la Épica 09 agrega operadores que no deberían ver búsquedas ajenas, hay que reabrir la decisión.

## 2. Recuperación de contraseña y acceso propio del admin (AUD-02-030, solo documentado)

**Qué pasa.** `accounts/` incluye todas las rutas de `django.contrib.auth.urls`, también las de recuperar y cambiar la contraseña. El servidor no tiene correo configurado, así que la recuperación no envía nada: solo muestra formularios. El panel de administración tiene su propia pantalla de acceso.

**Qué lo sostiene.**
- La plantilla base solo usa `logout`, y lo envía por POST.
- Ninguna plantilla enlaza al cambio de contraseña.
- La 04-08 limitará los intentos fallidos en las dos entradas de acceso, la de la aplicación y la del admin. Al 2026-11-20 todavía no está desplegada.

**Qué se descartó por ahora.**
- Incluir solo `login` y `logout`: toca la misma línea de `urls.py` que la 04-08.
- Llevar el acceso del admin al de la aplicación.

**Qué hacer si cambia.** Si algún día se configura correo en el servidor, la recuperación empezaría a funcionar de verdad. Antes de eso, hay que revisar esta decisión.

## 3. Eliminar una cotización no registra evento (decisión explícita)

**Qué pasa.** Al eliminar una cotización no queda ningún evento en el registro de negocio. Los demás borrados sí lo registran: `cliente_eliminado`, `producto_eliminado`, `pedido_eliminado` y `pago_eliminado`.

**Por qué.** Los eventos son una lista cerrada (RDA-008) y el de cotización eliminada se dejó fuera a propósito. Por esto no se agrega ningún tipo de evento ni ninguna migración.

**Qué hacer si cambia.** Si hace falta saber quién borró una cotización y cuándo, se propone una iteración con el tipo nuevo, su migración y su política de retención (`AGENTS.md`, regla 8.11).
