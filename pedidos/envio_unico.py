"""Token de envío único en la sesión (03-04, AUD-04-001, decisión 5-A).

Al abrir un formulario de creación (pedido, cotización o pago) se emite un token y viaja en un campo
oculto. Al guardar con éxito se consume y se anota qué registro creó. Un segundo envío con el mismo
token no crea nada y termina donde terminó el primero.

- Sin tabla ni migración: el token vive en la sesión (`django_session`). El `SessionMiddleware` no guarda
  la sesión en una respuesta 5xx, así que un error del sistema no gasta el token.
- Solo protege con un worker (peticiones en serie). Con varios, dos lecturas simultáneas de la sesión
  podrían dejar pasar un duplicado; la restricción única en la base es la única garantía total.
- La sesión guarda como máximo `TOPE` tokens; al pasarse, se descartan los más antiguos.
"""
import uuid

CLAVE = 'tokens_envio'
CAMPO = 'token_envio'
TOPE = 20  # PENDIENTE_DESARROLLADOR: valor de partida, a confirmar en la revisión manual.

NUEVO = 'nuevo'          # token emitido por este formulario y todavía sin usar
USADO = 'usado'          # ya guardó un registro: el envío es repetido
INVALIDO = 'invalido'    # ausente, desconocido, de otra sesión, de otro formulario o descartado por el tope


def emitir(request, ambito):
    """Crea un token para el formulario `ambito` ('pedido', 'cotizacion' o 'pago') y lo deja en la sesión."""
    tokens = dict(request.session.get(CLAVE, {}))
    token = uuid.uuid4().hex
    tokens[token] = {'ambito': ambito, 'pk': None}
    while len(tokens) > TOPE:
        del tokens[next(iter(tokens))]
    request.session[CLAVE] = tokens
    return token


def estado(request, ambito):
    """Devuelve (estado, token, pk): `pk` es el registro creado cuando el estado es USADO."""
    token = request.POST.get(CAMPO, '')
    registro = request.session.get(CLAVE, {}).get(token)
    if not registro or registro.get('ambito') != ambito:
        return INVALIDO, token, None
    if registro.get('pk') is not None:
        return USADO, token, registro['pk']
    return NUEVO, token, None


def consumir(request, token, pk):
    """Marca el token como usado por el registro `pk`. Se llama después de confirmar la transacción."""
    tokens = dict(request.session.get(CLAVE, {}))
    if token in tokens:
        tokens[token] = {**tokens[token], 'pk': pk}
        request.session[CLAVE] = tokens
