from flask import Blueprint, request, redirect, url_for, session, render_template, flash
from werkzeug.security import generate_password_hash
from models import db, Usuario, Rol, Conversion, Plan, Formato, ConversionPermitida, Suscripcion, Pago, ApiKey
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from functools import wraps

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Decorador para proteger rutas de administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("rol") != "admin":
            flash("Acceso no autorizado.", "danger")
            return redirect(url_for("admin.login"))  # CORREGIDO: Quitado el "admin." extra
        return f(*args, **kwargs)
    return decorated_function

# --- LOGIN Y LOGOUT ---

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(email=email, activo=True).first()
        if usuario and usuario.rol and usuario.rol.nombre_rol.lower() == "admin":
            if usuario.check_password(password):
                session["user_id"] = usuario.id_usuarios
                session["rol"] = usuario.rol.nombre_rol
                flash("Bienvenido al panel de administración.", "success")
                return redirect(url_for("admin.dashboard"))
        
        flash("Correo o contraseña incorrectos, o no tienes permisos de administrador.", "danger")
    return render_template("admin/login.html")

@admin_bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("main.html"))  # CORREGIDO: Cambiado de "main.html" a "main.index"

# --- DASHBOARD ---

@admin_bp.route("/")
@admin_bp.route("/dashboard")
@admin_required
def dashboard():
    num_usuarios = Usuario.query.count()
    num_conversiones = Conversion.query.count()
    return render_template("admin/admin.html", num_usuarios=num_usuarios, num_conversiones=num_conversiones)

# --- GESTIÓN DE USUARIOS ---

@admin_bp.route("/usuarios")
@admin_required
def usuarios_panel():
    usuarios = Usuario.query.options(joinedload(Usuario.rol)).all()
    roles = Rol.query.all()
    return render_template("admin/usuarios.html", usuarios=usuarios, roles=roles)

# --- RUTAS PARA GESTIÓN DE USUARIOS ---

@admin_bp.route("/crear_usuario", methods=["POST"])
@admin_required
def crear_usuario():
    try:
        nombre = request.form["nombre"]
        email = request.form["email"]
        password = request.form["password"]
        rol_id = request.form["rol_id"]
        
        # Verificar si el email ya existe
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            flash("El email ya está registrado", "danger")
            return redirect(url_for("admin.usuarios_panel"))
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre_usuario=nombre,
            email=email,
            contrasena=generate_password_hash(password),
            id_roles=rol_id,
            activo=True
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("Usuario creado exitosamente", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al crear usuario: {str(e)}", "danger")
    
    return redirect(url_for("admin.usuarios_panel"))

@admin_bp.route("/editar_usuario/<int:id>", methods=["GET", "POST"])
@admin_required
def editar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    roles = Rol.query.all()
    
    if request.method == "POST":
        try:
            usuario.nombre_usuario = request.form["nombre"]
            usuario.email = request.form["email"]
            usuario.id_roles = request.form["rol_id"]
            usuario.activo = "activo" in request.form
            
            if request.form["password"]:
                usuario.contrasena = generate_password_hash(request.form["password"])
            
            db.session.commit()
            flash("Usuario actualizado exitosamente", "success")
            return redirect(url_for("admin.usuarios_panel"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar usuario: {str(e)}", "danger")
    
    return render_template("admin/editar_usuario.html", usuario=usuario, roles=roles)

@admin_bp.route("/eliminar_usuario/<int:id>", methods=["POST"])
@admin_required
def eliminar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    
    try:
        # En lugar de eliminar, marcamos como inactivo
        usuario.activo = False
        db.session.commit()
        flash("Usuario desactivado exitosamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al desactivar usuario: {str(e)}", "danger")
    
    return redirect(url_for("admin.usuarios_panel"))

@admin_bp.route("/activar_usuario/<int:id>", methods=["POST"])
@admin_required
def activar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    
    try:
        usuario.activo = True
        db.session.commit()
        flash("Usuario activado exitosamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al activar usuario: {str(e)}", "danger")
    
    return redirect(url_for("admin.usuarios_panel"))

# --- GESTIÓN DE ROLES ---

def obtener_roles_conteo():
    from models import Rol, Usuario
    roles = Rol.query.all()
    resultado = []
    for rol in roles:
        conteo = Usuario.query.filter_by(id_roles=rol.id_roles).count()
        resultado.append({'rol': rol, 'user_count': conteo})
    return resultado

@admin_bp.route("/roles")
@admin_required
def roles_panel():
    roles = Rol.query.all()  # ✅ Simple y directo
    return render_template("admin/roles.html", roles=roles)

@admin_bp.route("/crear_rol", methods=["POST"])
@admin_required
def crear_rol():
    nombre = request.form["nombre"]
    nuevo_rol = Rol(nombre_rol=nombre)
    db.session.add(nuevo_rol)
    db.session.commit()
    flash("Rol creado exitosamente", "success")
    return redirect(url_for("admin.roles_panel"))

@admin_bp.route('/editar_rol', methods=['GET'])
@admin_bp.route('/editar_rol/<int:id>', methods=['GET', 'POST'])
@admin_required
def editar_rol(id=None):
    # Obtener todos los roles y conteo de usuarios (ajusta según tu lógica)
    roles_conteo = obtener_roles_conteo()  # Debes tener esta función

    rol_editar = None
    if id:
        rol_editar = Rol.query.get(id)  # O tu método para obtener el rol

        if request.method == 'POST':
            nuevo_nombre = request.form['nombre']
            rol_editar.nombre_rol = nuevo_nombre
            db.session.commit()
            flash('Rol actualizado correctamente', 'success')
            return redirect(url_for('admin.editar_rol'))

    return render_template(
        'admin/editar_rol.html',
        roles_conteo=roles_conteo,
        rol_editar=rol_editar
    )

@admin_bp.route("/eliminar_rol/<int:id>", methods=["POST"])
@admin_required
def eliminar_rol(id):
    rol = Rol.query.get_or_404(id)
    
    try:
        # Verificar si hay usuarios usando este rol
        from models import Usuario
        usuarios_con_rol = Usuario.query.filter_by(id_roles=id).count()
        
        if usuarios_con_rol > 0:
            flash(f"No se puede eliminar el rol '{rol.nombre_rol}' porque tiene {usuarios_con_rol} usuario(s) asignado(s).", "danger")
            return redirect(url_for("admin.roles_panel"))
        
        # Si no hay usuarios, proceder a eliminar
        db.session.delete(rol)
        db.session.commit()
        flash(f"Rol '{rol.nombre_rol}' eliminado exitosamente", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar rol: {str(e)}", "danger")
    
    return redirect(url_for("admin.roles_panel"))

# --- GESTIÓN DE CONVERSIONES ---

@admin_bp.route("/conversions")
@admin_required
def conversions_panel():
    q = request.args.get("q", "")
    page = request.args.get('page', 1, type=int)
    
    query = Conversion.query.options(
        joinedload(Conversion.usuario),
        joinedload(Conversion.formato_origen),
        joinedload(Conversion.formato_destino)
    )

    if q:
        query = query.join(Usuario).filter(
            or_(
                Conversion.nombre_archivo_origen.ilike(f"%{q}%"),
                Conversion.nombre_archivo_convertido.ilike(f"%{q}%"),
                Usuario.email.ilike(f"%{q}%")
            )
        )
    
    conversions = query.order_by(Conversion.fecha.desc()).paginate(page=page, per_page=15)
    return render_template("admin/conversions.html", conversions=conversions, q=q)

@admin_bp.route("/editar_conversion/<int:id>", methods=["GET", "POST"])
@admin_required
def editar_conversion(id):
    conv = Conversion.query.get_or_404(id)
    if request.method == "POST":
        conv.estado = request.form["estado"]
        db.session.commit()
        flash("Estado de la conversión actualizado", "success")
        return redirect(url_for("admin.conversions_panel"))
    return render_template("admin/editar_conversion.html", conv=conv)

# --- GESTIÓN DE PLANES ---

@admin_bp.route("/planes")
@admin_required
def planes_panel():
    planes = Plan.query.all()
    return render_template("admin/planes.html", planes=planes)

@admin_bp.route("/crear_plan", methods=["GET", "POST"])
@admin_required
def crear_plan():
    if request.method == "POST":
        nuevo_plan = Plan(
            nombre=request.form['nombre'],
            precio=request.form['precio'],
            limite_conversiones=request.form['limite_conversiones'],
            duracion_dias=request.form['duracion_dias']
        )
        db.session.add(nuevo_plan)
        db.session.commit()
        flash('Plan creado con éxito.', 'success')
        return redirect(url_for('admin.planes_panel'))
    return render_template('admin/crear_plan.html')

@admin_bp.route("/editar_plan/<int:id>", methods=["GET", "POST"])
@admin_required
def editar_plan(id):
    plan = Plan.query.get_or_404(id)
    if request.method == "POST":
        plan.nombre = request.form['nombre']
        plan.precio = request.form['precio']
        plan.limite_conversiones = request.form['limite_conversiones']
        plan.duracion_dias = request.form['duracion_dias']
        db.session.commit()
        flash('Plan actualizado con éxito.', 'success')
        return redirect(url_for('admin.planes_panel'))
    return render_template('admin/editar_plan.html', plan=plan)

# --- GESTIÓN DE FORMATOS Y PERMISOS ---

@admin_bp.route("/formatos")
@admin_required
def formatos_panel():
    formatos = Formato.query.all()
    conversiones_permitidas = ConversionPermitida.query.options(
        joinedload(ConversionPermitida.formato_origen),
        joinedload(ConversionPermitida.formato_destino)
    ).all()
    return render_template("admin/formatos.html", formatos=formatos, conversiones_permitidas=conversiones_permitidas)

@admin_bp.route("/crear_formato", methods=["POST"])
@admin_required
def crear_formato():
    nuevo_formato = Formato(
        tipo=request.form['tipo'],
        categoria=request.form['categoria']
    )
    db.session.add(nuevo_formato)
    db.session.commit()
    flash('Formato creado con éxito.', 'success')
    return redirect(url_for('admin.formatos_panel'))

@admin_bp.route("/crear_conversion_permitida", methods=["POST"])
@admin_required
def crear_conversion_permitida():
    id_origen = request.form.get('id_origen')
    id_destino = request.form.get('id_destino')

    if id_origen == id_destino:
        flash('El formato de origen y destino no pueden ser el mismo.', 'warning')
        return redirect(url_for('admin.formatos_panel'))

    existente = ConversionPermitida.query.filter_by(id_origen=id_origen, id_destino=id_destino).first()
    if existente:
        flash('Esta regla de conversión ya existe.', 'warning')
    else:
        nueva_regla = ConversionPermitida(id_origen=id_origen, id_destino=id_destino)
        db.session.add(nueva_regla)
        db.session.commit()
        flash('Regla de conversión creada con éxito.', 'success')
        
    return redirect(url_for('admin.formatos_panel'))

# --- PANELES DE VISUALIZACIÓN ---

@admin_bp.route("/pagos")
@admin_required
def pagos_panel():
    pagos = Pago.query.options(joinedload(Pago.usuario)).order_by(Pago.fecha_pago.desc()).all()
    return render_template("admin/pagos.html", pagos=pagos)

@admin_bp.route("/suscripciones")
@admin_required
def suscripciones_panel():
    suscripciones = Suscripcion.query.options(
        joinedload(Suscripcion.usuario),
        joinedload(Suscripcion.plan)
    ).order_by(Suscripcion.fecha_inicio.desc()).all()
    return render_template("admin/suscripciones.html", suscripciones=suscripciones)

@admin_bp.route("/api_keys")
@admin_required
def api_keys_panel():
    api_keys = ApiKey.query.options(joinedload(ApiKey.usuario)).order_by(ApiKey.fecha_creacion.desc()).all()
    return render_template("admin/api_keys.html", api_keys=api_keys)