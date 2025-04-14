from flask import Flask, request, send_file, render_template
from flask_cors import CORS
import os
from conversion.pdf_to_word import convert_pdf_to_word  # Importamos desde la subcarpeta
from conversion.convert_mp3 import convert_mp4_to_mp3  # Importamos desde el nuevo archivo
from werkzeug.utils import secure_filename
from moviepy import VideoFileClip

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

#-------------------------------- Rutas a otras paginas -----------------------------#

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/pdf_to_word_page')
def pdf_to_word_page():
    return render_template('pdf_to_word.html')

@app.route('/mp4_to_mp3_page')
def mp4_to_mp3_page():
    return render_template('mp4_to_mp3.html')
#------------------------------------------------------------------------------------#

@app.route('/pdf-to-word', methods=['POST'])
def pdf_to_word():
    file = request.files.get('file')
    if not file:
        return "No se recibió ningún archivo", 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    output_filename = file.filename.replace('.pdf', '.docx')
    output_path = os.path.join(RESULT_FOLDER, output_filename)

    # Convertir el PDF a Word
    convert_pdf_to_word(input_path, output_path)

    return send_file(
        output_path,
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        download_name=output_filename
    )


@app.route('/convert_mp3', methods=['POST'])
def convert_mp3():
    archivo = request.files.get('archivo')
    if not archivo or not archivo.filename.endswith('.mp4'):
        return "Archivo no válido", 400

    filename = secure_filename(archivo.filename)
    ruta_video = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        archivo.save(ruta_video)
    except Exception as e:
        return f"Error al guardar el archivo: {e}", 500

    nombre_base = os.path.splitext(filename)[0]
    ruta_mp3 = os.path.join(RESULT_FOLDER, f"{nombre_base}.mp3")

    try:
        # Llamamos a la función de convertir MP4 a MP3 desde convert_mp3.py
        convert_mp4_to_mp3(ruta_video, ruta_mp3)
    except Exception as e:
        return f"Error durante la conversión: {e}", 500

    # Enviar el MP3 al usuario como descarga directa
    return send_file(
        ruta_mp3,
        as_attachment=True,
        download_name=f"{nombre_base}.mp3",
        mimetype="audio/mpeg"
    )

if __name__ == '__main__':
    app.run(debug=True)

