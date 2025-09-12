from flask import Flask, request, send_file, render_template, jsonify
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
from conversion.word_to_pdf import convert_word_to_pdf
from conversion.pdf_to_word import convert_pdf_to_word
from conversion.convert_mp3 import convert_mp4_to_mp3
from conversion.compress import procesar_archivo
from moviepy import VideoFileClip
from conversion.file_cleaner import start_cleanup
from urllib.parse import quote_plus
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from extensions import db
from flask import session, redirect, url_for, flash
from models import Conversion
from datetime import datetime, timedelta
from models import Plan, Pago, Suscripcion
import random


app = Flask(__name__)
app.secret_key = "clave_secreta_para_sesiones"

# Configuración de la base de datos
password = quote_plus("682065025468637Nzwr")  # tu contraseña real
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://postgres:{password}@localhost:5432/MultiConvert'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa SQLAlchemy
db.init_app(app)


# Importar rutas y modelos
import models
from routes.admin import admin_bp
app.register_blueprint(admin_bp)

# Inicia el proceso de limpieza al inicio del servidor
start_cleanup()
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

@app.route('/word_to_pdf_page')
def word_to_pdf_page():
    return render_template('word_to_pdf.html')

@app.route('/mp4_to_mp3_page')
def mp4_to_mp3_page():
    return render_template('mp4_to_mp3.html')

@app.route('/compress_page')
def compress_page():
    return render_template('compress.html')

@app.route('/pdf_to_jpg_page')
def pdf_to_jpg_page():
    return render_template('pdf_to_jpg.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

#---------------------------- Rutas de conversión de archivos ------------------------#

@app.route('/word-to-pdf', methods=['POST'])
def word_to_pdf():
    file = request.files.get('file')
    if not file:
        return "No se recibió ningún archivo", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    output_filename = filename.replace('.docx', '.pdf')
    output_path = os.path.join(RESULT_FOLDER, output_filename)

    try:
        convert_word_to_pdf(input_path, output_path)
        return send_file(
            output_path,
            as_attachment=True,
            mimetype='application/pdf',
            download_name=output_filename
        )
    except Exception as e:
        return jsonify({"error": f"Error durante la conversión: {str(e)}"}), 500

@app.route('/pdf-to-word', methods=['POST'])
def pdf_to_word():
    file = request.files.get('file')
    if not file:
        return "No se recibió ningún archivo", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    output_filename = filename.replace('.pdf', '.docx')
    output_path = os.path.join(RESULT_FOLDER, output_filename)

    try:
        # 🔹 Aquí ocurre la conversión real
        convert_pdf_to_word(input_path, output_path)

        # 🔹 Guardar registro en la base de datos
        nueva_conversion = Conversion(
            filename=filename,
            converted_name=output_filename,
            type="pdf_to_word",
            status="success"
        )
        db.session.add(nueva_conversion)
        db.session.commit()

        # 🔹 Enviar el archivo convertido al usuario
        return send_file(
            output_path,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            download_name=output_filename
        )

    except Exception as e:
        # 🔹 Guardar error en la base de datos
        nueva_conversion = Conversion(
            filename=filename,
            converted_name=output_filename,
            type="pdf_to_word",
            status="failed"
        )
        db.session.add(nueva_conversion)
        db.session.commit()

        return jsonify({"error": f"Error durante la conversión: {str(e)}"}), 500
    
@app.route('/convert_mp3', methods=['POST'])
def convert_mp3():
    archivo = request.files.get('archivo')
    if not archivo or not archivo.filename.endswith('.mp4'):
        return "Archivo no válido", 400

    filename = secure_filename(archivo.filename)
    ruta_video = os.path.join(UPLOAD_FOLDER, filename)
    archivo.save(ruta_video)

    nombre_base = os.path.splitext(filename)[0]
    ruta_mp3 = os.path.join(RESULT_FOLDER, f"{nombre_base}.mp3")

    try:
        convert_mp4_to_mp3(ruta_video, ruta_mp3)
        return send_file(
            ruta_mp3,
            as_attachment=True,
            download_name=f"{nombre_base}.mp3",
            mimetype="audio/mpeg"
        )
    except Exception as e:
        return jsonify({"error": f"Error durante la conversión: {str(e)}"}), 500

@app.route('/compress', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return "No se subió archivo", 400

    try:
        resultado_path = procesar_archivo(file)
        return send_file(resultado_path, as_attachment=True)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500

@app.route("/convert_pdf_to_jpg", methods=["POST"])
def convert_pdf_to_jpg():
    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Archivo no válido"}), 400

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    output_folder = os.path.join("static", "converted", os.path.splitext(file.filename)[0])
    os.makedirs(output_folder, exist_ok=True)

    from pdf2image import convert_from_path
    try:
        images = convert_from_path(pdf_path)
        image_urls = []
        for i, image in enumerate(images):
            image_filename = f"{os.path.splitext(file.filename)[0]}_page_{i+1}.jpg"
            image_path = os.path.join(output_folder, image_filename)
            image.save(image_path, "JPEG")
            image_urls.append(f"/{image_path}")

        return jsonify({"images": image_urls})

    except Exception as e:
        return jsonify({"error": f"Error durante la conversión: {str(e)}"}), 500
    
    # -------------------- Rutas de usuario -------------------- #

@app.route('/perfil')
def user_profile():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para acceder a tu perfil', 'warning')
        return redirect(url_for('login_page'))
    
    from models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    return render_template('user_profile.html', usuario=usuario)

@app.route('/mis-conversiones')
def my_conversions():
    if 'user_id' not in session:
        flash('Debes iniciar sesión para ver tus conversiones', 'warning')
        return redirect(url_for('login_page'))
    
    from models import Conversion
    conversiones = Conversion.query.filter_by(id_usuarios=session['user_id']).all()
    return render_template('my_conversions.html', conversiones=conversiones)

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('index'))

# -------------------- Rutas de autenticación -------------------- #

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        from models import Usuario
        usuario = Usuario.query.filter_by(email=email, activo=True).first()
        if usuario and usuario.check_password(password):
            session['user_id'] = usuario.id_usuarios
            session['email'] = usuario.email
            session['rol'] = usuario.rol.nombre_rol if usuario.rol else None
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('index'))
        
        flash('Credenciales incorrectas', 'danger')
    
    return render_template('login.html')

@app.route("/suscribirse", methods=["GET", "POST"])
def suscribirse():
    if "user_id" not in session:
        flash("Debes iniciar sesión para suscribirte.", "warning")
        return redirect(url_for("login_page"))

    usuario_id = session["user_id"]  # <-- Mueve esto aquí, después de la validación
    print("¿Usuario logueado?", "user_id" in session)

    planes = Plan.query.all()
    if request.method == "POST":
        plan_id = request.form.get("plan_id")
        if not plan_id:
            flash("Debes seleccionar un plan.", "danger")
            return redirect(url_for("suscribirse"))

        try:
            plan_id_int = int(plan_id)
        except ValueError:
            flash("Plan inválido.", "danger")
            return redirect(url_for("suscribirse"))

        plan = Plan.query.get(plan_id_int)
        if not plan:
            flash("Plan no encontrado.", "danger")
            return redirect(url_for("suscribirse"))
        print("Entrando a la creación de pago y suscripción")

        try:
            print("Creando pago...")
            numero_orden = f"ORD-{random.randint(100000, 999999)}"
            pago = Pago(
                id_usuarios=usuario_id,
                monto=plan.precio,
                fecha_pago=datetime.now(),
                metodo_pago="simulado",
                estado="pagado",
                numero_orden=numero_orden
            )
            db.session.add(pago)
            db.session.flush()
            print("Pago creado con id:", pago.id_pagos)

            print("Creando suscripción...")
            suscripcion = Suscripcion(
                id_usuarios=usuario_id,
                id_planes=plan.id_planes,
                fecha_inicio=datetime.now(),
                fecha_fin=datetime.now() + timedelta(days=plan.duracion_dias)
            )
            db.session.add(suscripcion)
            db.session.commit()
            print("Suscripción creada con id:", suscripcion.id_suscripcion)
            flash("¡Pago simulado y suscripción creada con éxito!", "success")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            print("Error al guardar:", e)
            flash(f"Error al guardar la suscripción: {str(e)}", "danger")
            return redirect(url_for("suscribirse"))

    return render_template("suscribirse.html", planes=planes)


if __name__ == '__main__':  
    app.run(debug=True) 


