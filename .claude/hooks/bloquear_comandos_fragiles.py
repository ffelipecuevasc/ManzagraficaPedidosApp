"""Hook PreToolUse de Claude Code: bloquea comandos de Bash que Git Bash en Windows rompe.

Claude Code envuelve cada comando en un `bash -c` que, en Windows, corta la línea
cerca de los 8 KB y desarma comillas y barras invertidas. El síntoma es
`unexpected EOF while looking for matching`, y el agente gasta tokens reintentando.

Este hook revisa el comando antes de ejecutarlo. Si es frágil, sale con código 2:
Claude Code no lo ejecuta y le entrega a Claude el mensaje de stderr para que
cambie de camino de inmediato.

Usa solo la biblioteca estándar. Ante cualquier problema propio del hook
(entrada vacía o JSON inválido) deja pasar el comando: nunca debe bloquear el trabajo
por un error suyo.
"""

import json
import re
import sys

# Bytes máximos de un comando. El corte real está cerca de 8 KB, pero Claude Code
# suma su propio envoltorio al comando, así que el margen es amplio.
LIMITE_BYTES = 4000

HEREDOC = re.compile(r"<<-?\s*['\"]?[A-Za-z_]\w*")
PYTHON_C = re.compile(r"\bpython[0-9.]*(?:\.exe)?\s+(?:-\w+\s+)*-c\b")

MENSAJE = (
    "Bloqueado por .claude/hooks/bloquear_comandos_fragiles.py: {motivo}. "
    "En este Windows, Git Bash rompe los heredocs, `python -c` multilínea y los comandos largos "
    "(error `unexpected EOF`). Haz esto en su lugar (AGENTS.md, sección 5, «Scripts y comandos largos»): "
    "crea el script como archivo .py en tu carpeta temporal con la herramienta Write y ejecútalo con "
    '`PYTHONIOENCODING=utf-8 python "<ruta>/script.py"`. Para cambiar Markdown o código del '
    "proyecto usa la herramienta Edit. No reintentes el mismo comando con otro escape."
)


def motivo_de_bloqueo(comando: str) -> str | None:
    if HEREDOC.search(comando):
        return "el comando usa un heredoc (<<)"
    if PYTHON_C.search(comando) and "\n" in comando:
        return "el comando usa `python -c` con código de varias líneas"
    largo = len(comando.encode("utf-8"))
    if largo > LIMITE_BYTES:
        return f"el comando mide {largo} bytes (límite {LIMITE_BYTES})"
    return None


def main() -> int:
    try:
        sys.stdin.reconfigure(encoding="utf-8")
        datos = json.load(sys.stdin)
        comando = datos.get("tool_input", {}).get("command", "") or ""
    except (ValueError, AttributeError, OSError):
        return 0

    motivo = motivo_de_bloqueo(comando)
    if motivo is None:
        return 0

    sys.stderr.reconfigure(encoding="utf-8")
    sys.stderr.write(MENSAJE.format(motivo=motivo))
    return 2


if __name__ == "__main__":
    sys.exit(main())