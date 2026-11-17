# Bitácora 04-09 · Redacción de la iteración

- **Fecha:** 2026-11-17
- **Agente:** Claude Code (Sonnet 5.5)
- **Estado final:** la 04-09 queda **Pendiente (redactada, decisiones abiertas D1 a D4)**. Solo documentos; sin código, pruebas, `manage.py` ni consultas a la base.

## Resumen

Se redactó [iteracion-04-09](../../10_epicas/epica-04-seguridad/iteracion-04-09-politica-de-contenido-en-observacion.md): activar `ContentSecurityPolicyMiddleware` solo con `SECURE_CSP_REPORT_ONLY`, con la política final (solo `'self'`) para que el navegador anote todo lo externo y todo lo en línea. Sin cambios en plantillas ni JavaScript, sin punto de recepción de reportes y sin repetir las cabeceras de la 04-02.

## Verificación (solo lectura; Django 6.0.1 de `.venv`)

- Nombres: `django.middleware.csp.ContentSecurityPolicyMiddleware`; ajustes `SECURE_CSP` y `SECURE_CSP_REPORT_ONLY` (diccionarios, `{}` por defecto, `global_settings.py:669-670`); constantes `django.utils.csp.CSP`; procesador `django.template.context_processors.csp`; decoradores `csp_override` y `csp_report_only_override`.
- Comportamiento del middleware: configuración vacía no agrega cabecera; no pisa una cabecera ya puesta; el nonce es perezoso; solo actúa al responder; no hay comprobación de `check --deploy` sobre CSP.
- Recursos externos: **cinco servidores** (`fonts.googleapis.com`, `fonts.gstatic.com`, `cdn.tailwindcss.com`, `cdn.jsdelivr.net`, `code.jquery.com`), con archivo y línea en `base.html` y `login.html` (que no extiende la base).
- En línea: **siete scripts** (`base.html:17-36`, `login.html:18-36` y `:149-181`, `pedido_form.html:436-468`, `pago_form.html:141-152`, `producto_form.html:127-148`, `restaurar_bd.html:59-90`), sin etiquetas de plantilla; **dos bloques `<style>`** del navegador; **ocho atributos `style`**; **siete manejadores en línea** (cuatro en plantillas, tres generados en `index.js:566-574`).
- Cabeceras ya existentes: `X-Frame-Options: DENY` (`settings.py:76`, `global_settings.py:443`), `nosniff`, política de referente y COOP (`global_settings.py:656-662`).

## Contradicciones

1. La definición pide conocer «qué recursos carga»: solo se logra con la política final; con los CDN permitidos no se anotaría nada.
2. `login.html` repite su propio `<head>`: el inventario debe mirar las dos plantillas.

## Qué no se pudo ver

- Qué infracciones anota cada navegador (no se abrió ninguno), si las librerías usan `eval` o inyectan estilos, y qué muestra el panel de administración.
- Si el proxy de PythonAnywhere entrega la cabecera intacta, y qué versiones de navegador usa el cliente.
- Qué hacen por dentro Summernote, Select2, SweetAlert2 y el Tailwind del navegador.

## Decisiones abiertas

D1 política observada (recomendada: la final), D2 nonces (recomendada: ninguno, la Épica 08 mueve el código en línea), D3 interruptor (recomendada: variable `CSP_OBSERVACION`, activa por defecto) y D4 lectura del reporte (recomendada: consola del navegador, sin punto de recepción).

## Hallazgos de la Épica 04 sin iteración

Listados con opciones, sin decidir, en una sección nueva de `definicion-epica-04.md` («Hallazgos sin iteración, para la revisión final»).

## Archivos

Nuevo `iteracion-04-09-politica-de-contenido-en-observacion.md`; `definicion-epica-04.md`; `00_producto/registro-pendientes.md` (fila, decisiones, próximo hito, historial); esta bitácora.
