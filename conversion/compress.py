# compress.py
import os
import zipfile
from pydub import AudioSegment
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def procesar_archivo(file_storage):
    filename = secure_filename(file_storage.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file_storage.save(filepath)

    ext = filename.rsplit('.', 1)[-1].lower()

    if ext in ['pdf', 'docx', 'txt']:
        zip_path = os.path.join(UPLOAD_FOLDER, f"{filename}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(filepath, arcname=filename)
        return zip_path

    elif ext == 'mp3':
        audio = AudioSegment.from_file(filepath)
        compressed_path = os.path.join(UPLOAD_FOLDER, f"compressed_{filename}")
        audio.export(compressed_path, format="mp3", bitrate="96k")
        return compressed_path

    else:
        raise ValueError("Formato no compatible")
