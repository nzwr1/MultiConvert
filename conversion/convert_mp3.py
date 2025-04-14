from moviepy import VideoFileClip
import os

def convert_mp4_to_mp3(input_path, output_path):
    # Asegurar que el directorio de salida exista
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        with VideoFileClip(input_path) as video:
            audio = video.audio
            if audio:
                audio.write_audiofile(output_path)
            else:
                print("El archivo no contiene audio.")
                return None
        return output_path
    except Exception as e:
        print(f"Error durante la conversión: {e}")
        return None