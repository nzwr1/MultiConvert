from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from models import Usuario, Rol, db
from werkzeug.security import generate_password_hash, check_password_hash
from models import Conversion

admin_bp = Blueprint("admin", __name__)

# Login de admin
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
                return redirect(url_for("admin.usuarios_panel"))
        flash("Correo o contraseña incorrectos / No eres admin")
    return render_template("login.html")


# Panel de Usuarios
@admin_bp.route("/admin/usuarios")
def usuarios_panel():
    if session.get("rol") != "admin":
        return "No autorizado"
    usuarios = Usuario.query.all()
    roles = Rol.query.all()  # para el formulario al crear usuarios
    return render_template("usuarios.html", usuarios=usuarios, roles=roles)

# Panel de Roles
@admin_bp.route("/admin/roles")
def roles_panel():
    if session.get("rol") != "admin":
        return "No autorizado"
    roles = Rol.query.all()
    return render_template("roles.html", roles=roles)

# Panel de conversiones con búsqueda
@admin_bp.route("/admin/conversions")
def conversions_panel():
    if session.get("rol") != "admin":
        return "No autorizado"

    q = request.args.get("q", "")
    if q:
        conversions = Conversion.query.filter(
            (Conversion.filename.ilike(f"%{q}%")) |
            (Conversion.converted_name.ilike(f"%{q}%")) |
            (Conversion.type.ilike(f"%{q}%"))
        ).order_by(Conversion.created_at.desc()).all()
    else:
        conversions = Conversion.query.order_by(Conversion.created_at.desc()).all()

    return render_template("conversions.html", conversions=conversions)

# Editar conversión
@admin_bp.route("/admin/editar_conversion/<int:id>", methods=["GET", "POST"])
def editar_conversion(id):
    if session.get("rol") != "admin":
        return "No autorizado"

    conv = Conversion.query.get_or_404(id)

    if request.method == "POST":
        conv.filename = request.form["filename"]
        conv.converted_name = request.form["converted_name"]
        conv.type = request.form["type"]
        conv.status = request.form["status"]
        db.session.commit()
        flash("Conversión actualizada")
        return redirect(url_for("admin.conversions_panel"))

    return render_template("editar_conversion.html", conv=conv)

# Eliminar conversión
@admin_bp.route("/admin/eliminar_conversion/<int:id>", methods=["POST"])
def eliminar_conversion(id):
    if session.get("rol") != "admin":
        return "No autorizado"

    conv = Conversion.query.get_or_404(id)
    db.session.delete(conv)
    db.session.commit()
    flash("Conversión eliminada")
    return redirect(url_for("admin.conversions_panel"))


# Crear usuario
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
    flash("Usuario creado exitosamente")
    return redirect(url_for("admin.usuarios_panel"))


# Editar usuario
@admin_bp.route("/admin/editar_usuario/<int:id>", methods=["GET", "POST"])
def editar_usuario(id):
    if session.get("rol") != "admin":
        return "No autorizado"
    
    usuario = Usuario.query.get_or_404(id)
    roles = Rol.query.all()

    if request.method == "POST":
        usuario.nombre_usuario = request.form["nombre"]
        usuario.email = request.form["email"]
        rol_id = request.form.get("rol_id")
        if rol_id:
            usuario.id_roles = rol_id
        password = request.form.get("password")
        if password:
            usuario.set_password(password)
        db.session.commit()
        flash("Usuario actualizado exitosamente")
        return redirect(url_for("admin.usuarios_panel"))

    return render_template("editar_usuario.html", usuario=usuario, roles=roles)


# Eliminar usuario
@admin_bp.route("/admin/eliminar_usuario/<int:id>", methods=["POST"])
def eliminar_usuario(id):
    if session.get("rol") != "admin":
        return "No autorizado"
    
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    flash("Usuario eliminado")
    return redirect(url_for("admin.usuarios_panel"))


# Crear rol
@admin_bp.route("/admin/crear_rol", methods=["POST"])
def crear_rol():
    if session.get("rol") != "admin":
        return "No autorizado"
    
    nombre = request.form["nombre"]
    nuevo_rol = Rol(nombre_roles=nombre)
    db.session.add(nuevo_rol)
    db.session.commit()
    flash("Rol creado exitosamente")
    return redirect(url_for("admin.roles_panel"))

# Editar rol
@admin_bp.route("/admin/editar_rol/<int:id>", methods=["GET", "POST"])
def editar_rol(id):
    if session.get("rol") != "admin":
        return "No autorizado"
    
    rol = Rol.query.get_or_404(id)

    if request.method == "POST":
        rol.nombre_roles = request.form["nombre"]
        db.session.commit()
        flash("Rol actualizado")
        return redirect(url_for("admin.roles_panel"))

    return render_template("editar_roles.html", rol=rol)

# Eliminar rol
@admin_bp.route("/admin/eliminar_rol/<int:id>", methods=["POST"])
def eliminar_rol(id):
    if session.get("rol") != "admin":
        return "No autorizado"
    
    rol = Rol.query.get_or_404(id)
    db.session.delete(rol)
    db.session.commit()
    flash("Rol eliminado")
    return redirect(url_for("admin.roles_panel"))

@admin_bp.route("/logout")
def logout():
    session.clear()  # limpia toda la sesión
    flash("Has cerrado sesión")
    return redirect(url_for("index"))  # redirige al inicio