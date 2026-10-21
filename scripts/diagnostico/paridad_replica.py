"""Paridad de la réplica local con producción (iteración 00-03).

Solo lectura. Se conecta a la misma base que usaría la aplicación (respeta
DATABASE_URL si está definida en la sesión), activa una sesión de solo
lectura y muestra la configuración de MySQL, la versión de Python y la
diferencia entre `pip freeze` y `requirements.txt`. No muestra filas de
ninguna tabla.

Uso, desde la raíz del repositorio y con el .venv activo:

    python scripts/diagnostico/paridad_replica.py

Código de salida: 0 si todo coincide con producción, 1 si hay diferencias
o no se pudo medir.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

# Valores de producción medidos el 2026-10-20 (linea-base-produccion.md, secciones 5 y 7).
PRODUCCION = {
    "version_mysql": "8.0.46",
    "charset_base": "utf8mb4",
    "colacion_base": "utf8mb4_unicode_ci",
    "time_zone": "UTC",
    "system_time_zone": "UTC",
    "sql_mode": "NO_ENGINE_SUBSTITUTION",
    "tablas_zona_horaria": "sí",
    "python": "3.13.1",
}

# Instante en horario de verano de Chile: 12:00 UTC son las 09:00 en Santiago.
CONSULTA_ZONA = "SELECT CONVERT_TZ('2026-01-15 12:00:00', 'UTC', 'America/Santiago')"


def leer_requirements():
    datos = (RAIZ / "requirements.txt").read_bytes()
    if datos.startswith((b"\xff\xfe", b"\xfe\xff")):
        texto = datos.decode("utf-16")
    else:
        texto = datos.decode("utf-8-sig")
    return {linea.strip() for linea in texto.splitlines() if linea.strip()}


def leer_pip_freeze():
    salida = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True, text=True, check=True,
    ).stdout
    return {linea.strip() for linea in salida.splitlines() if linea.strip()}


def medir_mysql():
    import django
    from django.db import connection

    django.setup()
    with connection.cursor() as cursor:
        cursor.execute("SET SESSION TRANSACTION READ ONLY")
        cursor.execute("START TRANSACTION")
        cursor.execute(
            "SELECT DATABASE(), VERSION(), @@character_set_database, "
            "@@collation_database, @@time_zone, @@system_time_zone, @@sql_mode"
        )
        base, version, charset, colacion, zona, zona_sistema, modo = cursor.fetchone()
        cursor.execute(CONSULTA_ZONA)
        convertido = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE()"
        )
        tablas = cursor.fetchone()[0]
        cursor.execute("ROLLBACK")
    return base, tablas, {
        "version_mysql": version,
        "charset_base": charset,
        "colacion_base": colacion,
        "time_zone": zona,
        "system_time_zone": zona_sistema,
        "sql_mode": modo,
        "tablas_zona_horaria": "sí" if convertido is not None else "no",
    }


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "PedidosApp.settings")
    from django.core.exceptions import ImproperlyConfigured
    from django.db import DatabaseError

    local = {"python": platform.python_version()}
    try:
        base, tablas, valores = medir_mysql()
        local.update(valores)
    except (DatabaseError, ImproperlyConfigured) as error:
        print(f"No se pudo medir MySQL: {type(error).__name__}: {error}")
        return 1

    print("Paridad de la réplica local")
    print(f"Base medida: {base} ({tablas} tablas)")
    print(f"{'Elemento':<22} {'Producción':<26} {'Local':<26} Coincide")
    diferencias = 0
    for clave, esperado in PRODUCCION.items():
        valor = str(local.get(clave))
        coincide = valor == esperado
        diferencias += not coincide
        print(f"{clave:<22} {esperado:<26} {valor:<26} {'Sí' if coincide else 'No'}")

    requeridos = leer_requirements()
    instalados = leer_pip_freeze()
    solo_req = sorted(requeridos - instalados)
    solo_local = sorted(instalados - requeridos)
    print(f"pip freeze local: {len(instalados)} paquetes; requirements.txt: {len(requeridos)}")
    print(f"Solo en requirements.txt: {', '.join(solo_req) or 'ninguno'}")
    print(f"Solo en el entorno local: {', '.join(solo_local) or 'ninguno'}")
    diferencias += bool(solo_req or solo_local)

    print(f"Diferencias: {diferencias}")
    return 1 if diferencias else 0


if __name__ == "__main__":
    sys.exit(main())
