from django.db import connection
from django.utils import timezone
from .models import HistorialBD, Pedido, Cliente, Cotizacion, Producto
from datetime import datetime
from django.conf import settings
from contextlib import contextmanager
import codecs
import glob
import re
import logging
import subprocess
import os
import tempfile

logger = logging.getLogger(__name__)


@contextmanager
def archivo_opciones_mysql(db_password):
    """
    Archivo temporal de opciones con la contraseña de la base (04-03, D1).

    Así la contraseña no viaja en los argumentos de mysqldump ni de mysql, que en un servidor
    compartido otros usuarios pueden ver con `ps`. El archivo nace con permisos solo para el
    dueño (mkstemp), en la carpeta temporal del sistema (nunca en backups/), y se borra
    siempre en el finally, también si el comando falla. Entrega la ruta del archivo.
    """
    descriptor, ruta = tempfile.mkstemp(prefix='mysql_opciones_', suffix='.cnf')
    try:
        # Entre comillas dobles, MySQL interpreta \\ y \" como escapes.
        valor = (db_password or '').replace('\\', '\\\\').replace('"', '\\"')
        with os.fdopen(descriptor, 'w', encoding='utf-8') as archivo:
            archivo.write(f'[client]\npassword="{valor}"\n')
        yield ruta
    finally:
        try:
            os.remove(ruta)
        except FileNotFoundError:
            pass  # Ya no está: no queda nada que limpiar.

# ==========================================
# VALIDACIÓN DE VOLCADOS (iteración 04-04, D1 y D2)
# ==========================================

# D1: tope de 20 MB para un volcado a restaurar, más de diez veces el respaldo medido
# (1.545.818 bytes el 2026-11-19). Se revisa si la base crece.
TOPE_VOLCADO_BYTES = 20 * 1024 * 1024

PREFIJO_EMERGENCIA = 'emergencia_'

# D2: sentencias que un volcado de esta aplicación nunca trae (mysqldump sin --databases).
# Se buscan al inicio de una línea, también dentro de un comentario condicional /*!NNNNN ... */.
# Los datos van en INSERT de una sola línea, así que una palabra dentro de un texto no cuenta.
_SENTENCIA_PROHIBIDA = re.compile(
    rb'^\s*(?:/\*!\d*\s*)?(?:CREATE\s+DATABASE|DROP\s+DATABASE|USE\s|GRANT\s|CREATE\s+USER)',
    re.IGNORECASE,
)
_TABLAS_OBLIGATORIAS = {
    'tabla_pedidos_pedido': b'CREATE TABLE `pedidos_pedido`',
    'tabla_django_migrations': b'CREATE TABLE `django_migrations`',
}


def revisar_volcado(ruta):
    """
    Revisa un volcado contra las reglas de D2 sin devolver nada de su contenido.

    Devuelve un diccionario {regla: True/False}. Sobre el tope (D1) no se lee el archivo y
    las reglas de contenido quedan en False. Se lee línea por línea (no se carga entero).
    """
    tamano = os.path.getsize(ruta)
    reglas = {
        'no_vacio': tamano > 0,
        'dentro_del_tope': tamano <= TOPE_VOLCADO_BYTES,
        'texto_utf8': False,
        'cabecera_mysql_dump': False,
        'linea_de_cierre': False,
        'tabla_pedidos_pedido': False,
        'tabla_django_migrations': False,
        'sin_sentencias_prohibidas': False,
    }
    if not reglas['no_vacio'] or not reglas['dentro_del_tope']:
        return reglas

    decodificador = codecs.getincrementaldecoder('utf-8')()
    utf8 = True
    primera = ultima = None
    tablas = dict.fromkeys(_TABLAS_OBLIGATORIAS, False)
    prohibida = False
    with open(ruta, 'rb') as archivo:
        for linea in archivo:
            if utf8:
                try:
                    decodificador.decode(linea)
                except UnicodeDecodeError:
                    utf8 = False
            if linea.strip():
                if primera is None:
                    primera = linea
                ultima = linea
            for regla, marca in _TABLAS_OBLIGATORIAS.items():
                if not tablas[regla] and linea.startswith(marca):
                    tablas[regla] = True
            if not prohibida and _SENTENCIA_PROHIBIDA.match(linea):
                prohibida = True
    if utf8:
        try:
            decodificador.decode(b'', final=True)
        except UnicodeDecodeError:
            utf8 = False

    reglas.update(tablas)
    reglas['texto_utf8'] = utf8
    reglas['cabecera_mysql_dump'] = primera is not None and primera.startswith(b'-- MySQL dump')
    reglas['linea_de_cierre'] = ultima is not None and ultima.startswith(b'-- Dump completed')
    reglas['sin_sentencias_prohibidas'] = not prohibida
    return reglas


def volcado_valido(ruta):
    """True si el volcado cumple todas las reglas de D2 (la misma función valida la subida y el
    respaldo de emergencia)."""
    return all(revisar_volcado(ruta).values())


def _borrar_si_existe(ruta):
    try:
        os.remove(ruta)
    except FileNotFoundError:
        pass  # Nunca llegó a crearse: no queda nada que limpiar.


def generar_respaldo_mysql(prefijo='respaldo'):
    """
    Genera un respaldo .sql de la base de datos MySQL configurada en 'default'.
    Guarda el archivo en la carpeta 'backups/' y mantiene solo los 5 más recientes.
    Retorna la ruta absoluta del archivo generado.

    Con prefijo='emergencia' (04-04, D5) es el respaldo previo a restaurar: queda fuera de la
    rotación por cantidad y se conserva solo el último.
    """
    # 1. Obtener configuración de la BD
    db_config = settings.DATABASES['default']
    db_name = db_config['NAME']
    db_user = db_config['USER']
    db_password = db_config['PASSWORD']
    db_host = db_config['HOST']
    # db_port = db_config.get('PORT', '3306') # Opcional si usaras puerto no estándar

    # 2. Definir rutas y nombre de archivo
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    filename = f"{prefijo}_{timestamp}.sql"
    filepath = os.path.join(backup_dir, filename)

    # Asegurar que el directorio exista (redundancia de seguridad)
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 3. Construir el comando mysqldump
    # Nota: No usamos shell=True ni redirección '>' para evitar problemas de inyección
    # y manejo de caracteres especiales como '$' en el nombre de la BD.
    # Escribimos el archivo directamente desde Python.

    # IMPORTANTE: --no-tablespaces evita el error de permisos en PythonAnywhere
    # --set-gtid-purged=OFF evita problemas de metadatos al restaurar
    # La contraseña va en el archivo temporal de opciones, que debe ser el primer argumento (04-03, D1).
    try:
        with archivo_opciones_mysql(db_password) as opciones, open(filepath, 'w') as f:
            dump_cmd = [
                'mysqldump',
                f'--defaults-extra-file={opciones}',
                f'-h{db_host}',
                f'-u{db_user}',
                '--no-tablespaces',
                '--set-gtid-purged=OFF',
                db_name
            ]
            # Ejecutamos el comando y enviamos la salida (stdout) al archivo
            subprocess.run(dump_cmd, stdout=f, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        # Si falla (ej: contraseña incorrecta), borramos el archivo vacío y lanzamos error
        _borrar_si_existe(filepath)
        raise Exception(f"Error al generar respaldo MySQL: {e.stderr.decode()}") from e
    except Exception:
        # 04-04, punto 5: ante cualquier otro fallo (sin mysqldump, disco) tampoco queda un .sql
        # vacío que la rotación cuente entre los cinco. La excepción sigue su curso.
        _borrar_si_existe(filepath)
        raise

    # 4. POLÍTICA DE ROTACIÓN (PASO 3 del Plan)
    # Limpiar backups antiguos, mantener solo los 5 más recientes
    limpiar_backups_antiguos(backup_dir, mantener=5)

    # D5: del respaldo de emergencia se conserva solo el último.
    if filename.startswith(PREFIJO_EMERGENCIA):
        for anterior in glob.glob(os.path.join(backup_dir, f'{PREFIJO_EMERGENCIA}*.sql')):
            if os.path.basename(anterior) != filename:
                try:
                    os.remove(anterior)
                    logger.info("Respaldo de emergencia anterior eliminado: %s", anterior)
                except OSError:
                    logger.warning("Error al borrar el respaldo de emergencia %s", anterior, exc_info=True)

    return filepath

def limpiar_backups_antiguos(directorio, mantener=5):
    """
    Busca archivos .sql en el directorio, los ordena por fecha
    y borra los más viejos para dejar solo la cantidad 'mantener'.
    """
    # Patrón para encontrar solo archivos SQL. El de emergencia queda fuera de la rotación por
    # cantidad (04-04, D5: excepción mínima que la 06-03 hereda al rediseñar la rotación).
    pattern = os.path.join(directorio, "*.sql")
    lista_backups = [ruta for ruta in glob.glob(pattern)
                     if not os.path.basename(ruta).startswith(PREFIJO_EMERGENCIA)]

    # Ordenar por fecha de modificación (del más viejo al más nuevo)
    lista_backups.sort(key=os.path.getmtime)

    # Si hay más archivos de los permitidos...
    if len(lista_backups) > mantener:
        # ...obtenemos los que sobran (los primeros de la lista son los más viejos)
        a_borrar = lista_backups[:-mantener]

        for archivo in a_borrar:
            try:
                os.remove(archivo)
                logger.info("Respaldo antiguo eliminado: %s", archivo)
            except OSError as e:
                logger.warning("Error al borrar respaldo antiguo %s", archivo, exc_info=True)

def restaurar_bd_mysql(ruta_archivo_sql):
    """
    Restaura la base de datos configurada en 'default' usando un archivo .sql.
    ADVERTENCIA: Esta acción sobrescribe los datos actuales con los del archivo.
    """
    # 1. Validar existencia del archivo
    if not os.path.exists(ruta_archivo_sql):
        raise FileNotFoundError(f"No se encontró el archivo de respaldo: {ruta_archivo_sql}")

    # 2. Obtener credenciales (Reutilizamos la lógica segura de settings)
    db_config = settings.DATABASES['default']
    db_name = db_config['NAME']
    db_user = db_config['USER']
    db_password = db_config['PASSWORD']
    db_host = db_config['HOST']

    # 3. Construir comando de restauración
    # Estructura: mysql --defaults-extra-file=<opciones> -h host -u user nombre_bd
    # La contraseña va en el archivo temporal de opciones, nunca en los argumentos (04-03, D1).
    # Nota: No pasamos el archivo aquí, lo pasaremos vía 'stdin' (entrada estándar)
    try:
        # Abrimos el archivo SQL en modo lectura
        with archivo_opciones_mysql(db_password) as opciones, open(ruta_archivo_sql, 'r') as f:
            restore_cmd = [
                'mysql',
                f'--defaults-extra-file={opciones}',
                f'-h{db_host}',
                f'-u{db_user}',
                db_name
            ]
            # Ejecutamos 'mysql' inyectándole el contenido del archivo como si escribiéramos en la consola
            # Esto evita el uso de 'shell=True' y es más seguro contra inyecciones
            subprocess.run(restore_cmd, stdin=f, check=True)

    except FileNotFoundError:
        # Este error ocurre si el sistema operativo no encuentra el ejecutable 'mysql'
        # Común en Windows si no está en las Variables de Entorno (PATH)
        raise Exception(
            "Error de Sistema: No se encontró el comando 'mysql'. "
            "Si estás en local (Windows), asegúrate de que la carpeta 'bin' de MySQL Server esté en tu PATH."
        )
    except subprocess.CalledProcessError as e:
        # Este error ocurre si MySQL intenta ejecutar el SQL y falla (ej: archivo corrupto)
        raise Exception(f"Error al ejecutar la restauración en MySQL: El proceso falló.")

    return True

# ==========================================
# GESTIÓN DE ESTADÍSTICAS (PESO BD)
# ==========================================

def obtener_peso_real_bd():
    """
    Consulta directamente a MySQL (information_schema) el peso real en disco
    de la base de datos (Datos + Índices).
    Retorna el valor en MB (float).
    """
    # Obtenemos el nombre real de la BD desde settings
    db_name = settings.DATABASES['default']['NAME']

    # Query técnica para sumar el tamaño de datos e índices de todas las tablas
    sql = """
          SELECT SUM(data_length + index_length)
          FROM information_schema.TABLES
          WHERE table_schema = %s \
          """

    with connection.cursor() as cursor:
        cursor.execute(sql, [db_name])
        resultado = cursor.fetchone()

    # Si hay resultado, convertimos Bytes a Megabytes
    if resultado and resultado[0]:
        bytes_total = resultado[0]
        mb_total = round(bytes_total / (1024 * 1024), 2)
        return mb_total

    return 0.00

def registrar_metricas_diarias():
    """
    Función inteligente:
    1. Verifica si YA registramos el peso HOY.
    2. Si NO, calcula el peso y guarda una foto del estado actual.
    3. Si SI, no hace nada (para no llenar la tabla de duplicados).
    """
    hoy = timezone.now().date()

    # 1. Check de duplicados (¿Ya existe un registro con fecha de hoy?)
    if HistorialBD.objects.filter(fecha_registro__date=hoy).exists():
        return False  # Ya se corrió hoy, no hacemos nada

    # 2. Calcular Peso Real
    peso_mb = obtener_peso_real_bd()

    # 3. Recopilar métricas de negocio
    total_pedidos = Pedido.objects.count()
    total_clientes = Cliente.objects.count()
    total_cotizaciones = Cotizacion.objects.count()
    total_productos = Producto.objects.count()

    # 4. Guardar la "foto" en el historial
    HistorialBD.objects.create(
        tamano_mb=peso_mb,
        total_pedidos=total_pedidos,
        total_clientes=total_clientes,
        total_cotizaciones=total_cotizaciones,
        total_productos=total_productos
    )

    return True  # Se creó un nuevo registro exitosamente