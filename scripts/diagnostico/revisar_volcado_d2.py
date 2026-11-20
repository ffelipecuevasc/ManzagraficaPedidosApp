"""Formato D2 (04-04): revisa un respaldo `.sql` con la MISMA función que usa la aplicación.

Versionado en la 04-06 (antes vivía en la carpeta temporal del agente). Se usa en el paso 1 de
cada despliegue, junto con `scripts/verificar_respaldo.py`, sobre el respaldo de producción
descargado al PC.

Uso, desde la raíz del repositorio y con el .venv activo:

    python scripts/diagnostico/revisar_volcado_d2.py "<ruta del respaldo .sql>"

Imprime el tamaño, «regla: True/False» por cada regla de D2 (`pedidos.utils.revisar_volcado`)
y el resultado: «RESULTADO: CUMPLE D2» o «RESULTADO: NO CUMPLE D2». Nunca imprime una línea del
volcado y no se conecta a ninguna base de datos (solo carga la configuración de Django).

Código de salida: 0 si cumple todas las reglas; 1 si alguna no; 2 si no se pudo ejecutar.
"""
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print('Uso: python scripts/diagnostico/revisar_volcado_d2.py "<ruta del respaldo .sql>"')
        return 2
    ruta = os.path.abspath(argv[0])
    if not os.path.isfile(ruta):
        print('NO SE EJECUTA: el archivo no existe.')
        return 2

    if str(RAIZ) not in sys.path:
        sys.path.insert(0, str(RAIZ))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PedidosApp.settings')
    import django
    django.setup()
    from pedidos.utils import revisar_volcado

    reglas = revisar_volcado(ruta)
    print(f'tamano_en_bytes: {os.path.getsize(ruta)}')
    for regla, cumple in reglas.items():
        print(f'{regla}: {cumple}')
    todas = all(reglas.values())
    print('RESULTADO: CUMPLE D2' if todas else 'RESULTADO: NO CUMPLE D2')
    return 0 if todas else 1


if __name__ == '__main__':
    sys.exit(main())
