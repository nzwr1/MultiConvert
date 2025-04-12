from flask import Flask, request, send_file, render_template
from flask_cors import CORS
import os
from conversion.pdf_to_word import convert_pdf_to_word  # Importamos desde la subcarpeta

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('main.html')

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

if __name__ == '__main__':
    app.run(debug=True)

