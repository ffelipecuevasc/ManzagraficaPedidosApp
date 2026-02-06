import os
import subprocess
from datetime import datetime
from django.conf import settings
import glob


def generar_respaldo_mysql():
    """
    Genera un respaldo .sql de la base de datos MySQL configurada en 'default'.
    Guarda el archivo en la carpeta 'backups/' y mantiene solo los 5 más recientes.
    Retorna la ruta absoluta del archivo generado.
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
    filename = f"respaldo_{timestamp}.sql"
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
    dump_cmd = [
        'mysqldump',
        f'-h{db_host}',
        f'-u{db_user}',
        f'--password={db_password}',
        '--no-tablespaces',
        '--set-gtid-purged=OFF',
        db_name
    ]

    try:
        with open(filepath, 'w') as f:
            # Ejecutamos el comando y enviamos la salida (stdout) al archivo
            subprocess.run(dump_cmd, stdout=f, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        # Si falla (ej: contraseña incorrecta), borramos el archivo vacío y lanzamos error
        if os.path.exists(filepath):
            os.remove(filepath)
        raise Exception(f"Error al generar respaldo MySQL: {e.stderr.decode()}")

    # 4. POLÍTICA DE ROTACIÓN (PASO 3 del Plan)
    # Limpiar backups antiguos, mantener solo los 5 más recientes
    limpiar_backups_antiguos(backup_dir, mantener=5)

    return filepath

def limpiar_backups_antiguos(directorio, mantener=5):
    """
    Busca archivos .sql en el directorio, los ordena por fecha
    y borra los más viejos para dejar solo la cantidad 'mantener'.
    """
    # Patrón para encontrar solo archivos SQL
    pattern = os.path.join(directorio, "*.sql")
    lista_backups = glob.glob(pattern)

    # Ordenar por fecha de modificación (del más viejo al más nuevo)
    lista_backups.sort(key=os.path.getmtime)

    # Si hay más archivos de los permitidos...
    if len(lista_backups) > mantener:
        # ...obtenemos los que sobran (los primeros de la lista son los más viejos)
        a_borrar = lista_backups[:-mantener]

        for archivo in a_borrar:
            try:
                os.remove(archivo)
                print(f"Respaldo antiguo eliminado: {archivo}")
            except OSError as e:
                print(f"Error al borrar respaldo antiguo {archivo}: {e}")

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
    # Estructura: mysql -h host -u user --password=pass nombre_bd
    # Nota: No pasamos el archivo aquí, lo pasaremos vía 'stdin' (entrada estándar)
    restore_cmd = [
        'mysql',
        f'-h{db_host}',
        f'-u{db_user}',
        f'--password={db_password}',
        db_name
    ]

    try:
        # Abrimos el archivo SQL en modo lectura
        with open(ruta_archivo_sql, 'r') as f:
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