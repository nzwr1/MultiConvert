import os
import time
import os
import time
import threading

# Directorios donde se almacenan los archivos
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'

# Tiempo de vida de los archivos en segundos (3 minutos)
FILE_LIFETIME = 180  # 3 minutos

# Crear carpetas si no existen
for folder in [UPLOAD_FOLDER, RESULT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def delete_old_files():
    current_time = time.time()

    for folder in [UPLOAD_FOLDER, RESULT_FOLDER]:
        if not os.path.exists(folder):
            continue  # salta si la carpeta no existe (seguridad extra)

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > FILE_LIFETIME:
                    try:
                        os.remove(file_path)
                        print(f"Archivo {filename} eliminado exitosamente de {folder}.")
                    except Exception as e:
                        print(f"Error al eliminar el archivo {filename}: {e}")

def start_cleanup():
    # Hacer la limpieza de archivos cada 60 segundos
    threading.Timer(60, start_cleanup).start()
    delete_old_files()

# Iniciar el proceso de limpieza en segundo plano
start_cleanup()