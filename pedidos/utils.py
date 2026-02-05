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
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
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