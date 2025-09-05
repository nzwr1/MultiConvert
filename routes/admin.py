from flask import Blueprint, request, redirect, url_for, session, render_template
from models import Usuario, Rol, db
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email, activo=True).first()
        if usuario and usuario.rol.nombre_roles.lower() == "admin":
            if usuario.check_password(password):
                session["user_id"] = usuario.id_usuarios
                session["rol"] = usuario.rol.nombre_roles
                return redirect(url_for("admin.admin_panel"))
        return "Correo o contraseña incorrectos / No eres admin"

    return render_template("login.html")


@admin_bp.route("/admin")
def admin_panel():
    if session.get("rol") != "admin":
        return "No autorizado"
    usuarios = Usuario.query.all()
    roles = Rol.query.all()
    return render_template("admin.html", usuarios=usuarios, roles=roles)


@admin_bp.route("/admin/crear_usuario", methods=["POST"])
def crear_usuario():
    if session.get("rol") != "admin":
        return "No autorizado"
    
    nombre = request.form["nombre"]
    email = request.form["email"]
    password = request.form["password"]
    rol_id = request.form.get("rol_id", 2)  # Por defecto usuario normal

    nuevo_usuario = Usuario(
        nombre_usuario=nombre,
        email=email,
        id_roles=rol_id
    )
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return redirect(url_for("admin.admin_panel"))