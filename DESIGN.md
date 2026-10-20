# DESIGN.md · Sistema de diseño de Manza Gráfica App

Fuente única de verdad del diseño de la interfaz. Documenta el diseño que la aplicación ya usa: sus valores salen de la configuración de Tailwind, de la hoja `pedidos/static/pedidos/css/index.css` y de las plantillas. Lo que el diseño todavía no define queda marcado como `PENDIENTE_DESARROLLADOR` y no se completa con valores supuestos.

---

## 1. Concepto visual

**PENDIENTE_DESARROLLADOR.** La interfaz actual combina un amarillo de marca sobre superficies neutras casi negras o casi blancas, títulos en una tipografía condensada de cartel y texto en una sans serif de lectura.

Principios:

1. **Herramienta de trabajo antes que vitrina.** La usa el equipo de la empresa para operar el día a día: la información urgente (atrasos, saldos) se ve primero.
2. **El amarillo marca acción o énfasis, nunca texto largo.** Ver la regla de contraste.
3. **Dos modos completos.** Cada pantalla funciona en modo claro y en modo oscuro.

## 2. Color

### 2.1 Superficies

| Token | Hex | Uso |
| :---- | :-- | :-- |
| `background-light` | `#F9FAFB` | Fondo de página en modo claro |
| `background-dark` | `#0A0A0A` | Fondo de página y barra lateral en modo oscuro |
| `card-dark` | `#171717` | Tarjetas, paneles y estado hover del menú en modo oscuro |
| `border-dark` | `#262626` | Bordes de separación en modo oscuro |
| Blanco | `#FFFFFF` | Tarjetas, barra lateral e inputs en modo claro |

### 2.2 Acento y texto

| Token | Hex | Uso |
| :---- | :-- | :-- |
| `primary` | `#FBBF24` | Amarillo de marca: botón principal, resaltado del logotipo, íconos activos |
| Texto principal claro | `#0F172A` (slate-900) | Texto sobre superficies claras |
| Texto principal oscuro | `#F1F5F9` (slate-100) | Texto sobre superficies oscuras |
| Texto secundario claro | `#64748B` (slate-500) | Etiquetas y textos de apoyo en modo claro |
| Texto secundario oscuro | `#94A3B8` (slate-400) | Etiquetas y textos de apoyo en modo oscuro |
| Peligro | `#DC2626` (red-600) | Botones de acciones destructivas |

Los colores de estado (verde, azul, rojo y amarillo de Tailwind en sus variantes 50, 100, 400, 600 y 900) se usan en etiquetas de estado de pedidos y pagos. Su asignación por estado es `PENDIENTE_DESARROLLADOR`.

### 2.3 Contraste

Contrastes medidos según WCAG 2.2:

| Combinación | Ratio | Resultado |
| :---------- | :---- | :-------- |
| Negro `#000000` sobre `primary` | 12,58:1 | AAA. Texto de botones principales |
| `primary` sobre `background-dark` | 11,86:1 | AAA |
| `primary` sobre `card-dark` | 10,74:1 | AAA |
| `primary` sobre blanco | 1,67:1 | **Falla.** No sirve ni para texto grande |
| `primary` sobre `background-light` | 1,60:1 | **Falla.** No sirve ni para texto grande |
| slate-900 sobre `background-light` | 17,08:1 | AAA |
| slate-100 sobre `background-dark` | 18,07:1 | AAA |
| slate-500 sobre blanco | 4,76:1 | AA |
| slate-400 sobre `card-dark` | 6,99:1 | AA |
| slate-400 sobre `background-dark` | 7,72:1 | AAA |
| Blanco sobre red-600 | 4,83:1 | AA |

Regla práctica: `primary` como **color de texto o de ícono informativo** se usa solo sobre superficies oscuras (`dark:text-primary`). Sobre superficies claras, `primary` solo es **fondo**, con texto negro encima. El color de reemplazo para texto amarillo en modo claro es `PENDIENTE_DESARROLLADOR`.

## 3. Tipografía

| Rol | Familia | Pesos | Uso |
| :-- | :------ | :---- | :-- |
| Display | Bebas Neue | 400 | Logotipo, títulos de página y cifras destacadas (clases `font-display` y `display-font`) |
| Texto | Inter | 300, 400, 500, 600, 700 | Todo el resto de la interfaz |

Fallbacks: `sans-serif` para ambas familias. Bebas Neue no usa `cursive` como respaldo: si la fuente no carga, una cursiva del sistema rompe la lectura de títulos y cifras. Origen de las fuentes: PENDIENTE_DESARROLLADOR (autoalojadas o servicio externo, ver `registro-pendientes.md`).

### 3.1 Escala tipográfica

PENDIENTE_DESARROLLADOR. Las plantillas usan la escala por defecto de Tailwind sin una asignación fija por rol.

Reglas:

1. Bebas Neue solo en títulos y cifras, nunca en párrafos ni en etiquetas de formulario: es una fuente condensada de mayúsculas y pierde legibilidad en tamaños pequeños.
2. Las etiquetas de formulario usan Inter 600 a 14 px (`0.875rem`); los textos de ayuda, 12 px (`0.75rem`).

## 4. Espaciado, retícula y forma

| Token | Valor |
| :---- | :---- |
| Ancho de la barra lateral | 256 px (`w-64`), fija |
| Relleno de inputs | `0.625rem 1rem` |
| Separación entre campos de formulario | `1.5rem` |

- Contenedor: PENDIENTE_DESARROLLADOR.
- Retícula: PENDIENTE_DESARROLLADOR.
- Radios: inputs con `0.5rem` (`rounded-lg`). En las plantillas conviven `rounded-md`, `rounded-lg`, `rounded-xl` y `rounded-full`; su asignación por componente es PENDIENTE_DESARROLLADOR.
- Sombras: PENDIENTE_DESARROLLADOR.

## 5. Componentes

| Componente | Descripción y reglas |
| :--------- | :------------------- |
| Barra lateral | Navegación fija a la izquierda, con secciones en acordeón (Pedidos, Clientes, Cotizaciones, Productos, Pagos, Base de datos). El ítem activo se marca según la ruta actual. |
| Inputs, selects y áreas de texto | Ancho completo, borde `#D1D5DB` de 1 px, radio `0.5rem`, texto `#111827` sobre blanco en modo claro, con su variante oscura en `index.css`. |
| Selectores con búsqueda | Select2 para clientes, pedidos y productos. |
| Editor de texto enriquecido | Summernote solo en los campos de detalle técnico. |
| Modal de confirmación | Toda acción irreversible (eliminar, reabrir, restaurar la base) se confirma en un modal que explica la consecuencia antes de ejecutarla. La acción confirmada se envía como formulario POST. |
| Página de error | Mensaje comprensible, sin detalles técnicos, con un identificador del error que el usuario puede informar y un enlace al panel de control. |

### 5.1 Botones

| Variante | Fondo | Texto | Hover |
| :------- | :---- | :---- | :---- |
| Principal | `primary` `#FBBF24` | Negro | `yellow-400` |
| Secundario | Blanco / `neutral-800` en oscuro, con borde | slate-700 / slate-300 en oscuro | `slate-50` / `neutral-700` |
| Peligro | `red-600` | Blanco | `red-700` |

Todos: texto en negrita, ícono opcional a la izquierda. Estilo de foco: PENDIENTE_DESARROLLADOR (debe ser visible en ambos modos). Un botón que envía un formulario se deshabilita después del primer clic para evitar envíos dobles.

## 6. Iconografía

Material Icons Round, por ligaduras (el nombre del ícono como texto dentro de `<span class="material-icons-round">`). Origen de la fuente de íconos: PENDIENTE_DESARROLLADOR (igual que las tipografías).

| Uso | Ícono |
| :-- | :---- |
| Panel de control | `dashboard` |
| Pedidos | `assignment` |
| Estadísticas | `analytics` |
| Listados | `toc` |
| Editar | `edit` |
| Eliminar | `delete` |
| Iniciar pedido | `play_arrow` |
| Terminar pedido | `done_all` |
| Reabrir pedido | `refresh` |

Íconos decorativos con `aria-hidden="true"`; los que actúan solos como botón llevan `aria-label` en el elemento interactivo. Como el ícono es texto, un lector de pantalla lee su nombre en inglés si no se oculta.

## 7. Imágenes

1. Las únicas imágenes de contenido son las imágenes de referencia que el equipo sube a un pedido; se guardan en `media/referencias/` y consumen el mismo disco que la base de datos.
2. Formatos aceptados, tamaño máximo y optimización: PENDIENTE_DESARROLLADOR.
3. Todas con texto alternativo descriptivo en español y dimensiones explícitas.

## 8. Movimiento

- Permitido: transiciones de color y de fondo en hover y foco (`transition-colors`, 200 a 300 ms) y el giro del chevron del acordeón.
- No se usa: PENDIENTE_DESARROLLADOR.
- Con `prefers-reduced-motion: reduce`, PENDIENTE_DESARROLLADOR.

## 9. Implementación de los tokens

- Los tokens de color y las familias tipográficas viven en un único archivo de configuración de Tailwind CSS v3, compilado localmente con pnpm. El CSS compilado se sirve como archivo estático junto a `index.css`. Ninguna plantilla define su propia configuración de Tailwind ni carga el compilador en el navegador.
- El modo oscuro usa la estrategia `class`: la clase `dark` en `<html>` activa las variantes `dark:`. La preferencia se guarda en `localStorage` con la clave `color-theme`; sin preferencia guardada, se respeta `prefers-color-scheme`.
- `index.css` contiene solo lo que Tailwind no cubre: estilos globales de formularios generados por Django, ajustes de Select2 y Summernote, y la barra de desplazamiento.

## 10. Voz y textos

- Español de Chile, trato de tú, frases cortas. Primero la acción, después la explicación.
- Los botones dicen lo que hacen («Registrar pago», «Terminar pedido»), no «Aceptar».
- Los montos se muestran como `$15.000`, con punto como separador de miles y sin decimales.
- Los mensajes de error dicen qué pasó y qué puede hacer la persona, sin términos técnicos.
