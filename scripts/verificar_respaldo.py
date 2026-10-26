"""Verifica un volcado de mysqldump sin mostrar su contenido.

Uso:
    python scripts/verificar_respaldo.py RUTA_DEL_VOLCADO [--min-bytes N]

Comprueba:
  1. Que el tamaño supere un mínimo (por defecto 500.000 bytes).
  2. Que la última línea con texto empiece con «-- Dump completed».
  3. Que haya un CREATE TABLE por cada una de las 19 tablas esperadas.
  4. El SHA-256 del archivo.

El informe solo muestra tamaños, nombres de tabla, conteos y el hash; nunca
una línea del volcado. Termina con código 0 si el volcado es válido y con 1
si no lo es o si no se pudo leer.

Solo usa la biblioteca estándar. No se conecta a ninguna base de datos.
"""

import argparse
import hashlib
import os
import re
import sys

TAMANO_MINIMO_POR_DEFECTO = 500_000

# Deducidas de las migraciones de pedidos (8 modelos, sin muchos a muchos) y
# de las aplicaciones de Django instaladas (admin, auth, contenttypes,
# sessions) más django_migrations. Coinciden con las 18 tablas medidas en
# producción el 2026-10-20 (linea-base-produccion.md, sección 2), más
# pedidos_registroevento (migración 0007, aplicada en producción el
# 2026-10-25 en la 01-06). Los volcados anteriores se verifican con la
# versión de v0.2-correcciones.
TABLAS_ESPERADAS = frozenset({
    "pedidos_cliente",
    "pedidos_producto",
    "pedidos_cotizacion",
    "pedidos_itemcotizacion",
    "pedidos_pedido",
    "pedidos_itempedido",
    "pedidos_pago",
    "pedidos_historialbd",
    "pedidos_registroevento",
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "auth_user",
    "auth_user_groups",
    "auth_user_user_permissions",
    "django_admin_log",
    "django_content_type",
    "django_migrations",
    "django_session",
})

LINEA_DE_CIERRE = b"-- Dump completed"
TAMANO_BLOQUE = 1024 * 1024
# Bytes que se arrastran entre bloques para no perder un CREATE TABLE partido.
SOLAPE = 256
TAMANO_COLA = 4096

PATRON_CREATE = re.compile(rb"^CREATE TABLE `([^`]{1,64})`", re.MULTILINE)
PATRON_NOMBRE_SEGURO = re.compile(r"^[A-Za-z0-9_$]{1,64}$")


def nombre_imprimible(nombre_en_bytes):
    """Devuelve el nombre si es un identificador simple; si no, un aviso."""
    nombre = nombre_en_bytes.decode("utf-8", errors="replace")
    if PATRON_NOMBRE_SEGURO.match(nombre):
        return nombre
    return "(nombre no imprimible)"


def analizar(ruta):
    """Recorre el archivo una sola vez: hash, CREATE TABLE y cola final."""
    sha = hashlib.sha256()
    conteo_tablas = {}
    arrastre = b""
    cola = b""
    with open(ruta, "rb") as archivo:
        while True:
            bloque = archivo.read(TAMANO_BLOQUE)
            if not bloque:
                break
            sha.update(bloque)
            texto = arrastre + bloque
            # Solo se cuentan coincidencias que empiezan antes del solape,
            # para no contar dos veces la misma en el bloque siguiente.
            limite = max(len(texto) - SOLAPE, 0)
            for coincidencia in PATRON_CREATE.finditer(texto):
                if coincidencia.start() < limite:
                    nombre = coincidencia.group(1)
                    conteo_tablas[nombre] = conteo_tablas.get(nombre, 0) + 1
            arrastre = texto[limite:]
            cola = (cola + bloque)[-TAMANO_COLA:]
    # Coincidencias que quedaron en el último solape.
    for coincidencia in PATRON_CREATE.finditer(arrastre):
        nombre = coincidencia.group(1)
        conteo_tablas[nombre] = conteo_tablas.get(nombre, 0) + 1
    lineas = [linea.strip() for linea in cola.splitlines() if linea.strip()]
    tiene_cierre = bool(lineas) and lineas[-1].startswith(LINEA_DE_CIERRE)
    return sha.hexdigest(), conteo_tablas, tiene_cierre


def formato_miles(numero):
    return f"{numero:,}".replace(",", ".")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(
        description="Verifica un volcado de mysqldump sin mostrar su contenido.")
    parser.add_argument("ruta", help="ruta del archivo .sql")
    parser.add_argument(
        "--min-bytes", type=int, default=TAMANO_MINIMO_POR_DEFECTO,
        help=f"tamaño mínimo en bytes (por defecto {TAMANO_MINIMO_POR_DEFECTO})")
    args = parser.parse_args(argv)

    print("Informe de verificación de respaldo")
    print(f"Archivo: {os.path.basename(args.ruta)}")

    if not os.path.isfile(args.ruta):
        print("Resultado: NO VÁLIDO (el archivo no existe o no es un archivo)")
        return 1

    tamano = os.path.getsize(args.ruta)
    try:
        sha256, conteo, tiene_cierre = analizar(args.ruta)
    except OSError as error:
        print(f"Resultado: NO VÁLIDO (no se pudo leer el archivo: {error.strerror})")
        return 1

    encontradas = {nombre_imprimible(n) for n in conteo}
    presentes = sorted(TABLAS_ESPERADAS & encontradas)
    faltantes = sorted(TABLAS_ESPERADAS - encontradas)
    adicionales = sorted(encontradas - TABLAS_ESPERADAS)
    repetidas = sorted(nombre_imprimible(n) for n, c in conteo.items() if c > 1)

    tamano_ok = tamano >= args.min_bytes
    tablas_ok = not faltantes

    print(f"Tamaño: {formato_miles(tamano)} bytes "
          f"(mínimo {formato_miles(args.min_bytes)}): {'OK' if tamano_ok else 'FALLA'}")
    print(f"Línea de cierre «-- Dump completed»: {'presente' if tiene_cierre else 'AUSENTE'}")
    print(f"Sentencias CREATE TABLE: {sum(conteo.values())}")
    print(f"Tablas esperadas encontradas: {len(presentes)} de {len(TABLAS_ESPERADAS)}")
    print(f"Tablas faltantes: {', '.join(faltantes) if faltantes else 'ninguna'}")
    print(f"Tablas adicionales (aviso, no invalida): "
          f"{', '.join(adicionales) if adicionales else 'ninguna'}")
    if repetidas:
        print(f"Tablas con más de un CREATE TABLE (aviso): {', '.join(repetidas)}")
    print(f"SHA-256: {sha256}")

    valido = tamano_ok and tiene_cierre and tablas_ok
    if valido:
        print("Resultado: VÁLIDO")
        return 0
    motivos = []
    if not tamano_ok:
        motivos.append("tamaño bajo el mínimo")
    if not tiene_cierre:
        motivos.append("sin línea de cierre")
    if not tablas_ok:
        motivos.append(f"{len(faltantes)} tabla(s) faltante(s)")
    print(f"Resultado: NO VÁLIDO ({'; '.join(motivos)})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
