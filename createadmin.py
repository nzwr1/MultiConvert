from werkzeug.security import generate_password_hash
from extensions import db
from models import Usuario, Rol
from main import app   # Importamos la app de Flask ya configurada

with app.app_context():
    # Crear las tablas si no existen
    db.create_all()

    # Crear rol admin si no existe
    from models import Rol, Usuario
    rol_admin = Rol.query.filter_by(nombre_roles="admin").first()
    if not rol_admin:
        rol_admin = Rol(nombre_roles="admin")
        db.session.add(rol_admin)
        db.session.commit()

    # Crear usuario admin si no existe
    admin = Usuario.query.filter_by(email="admin@local.com").first()
    if not admin:
        admin = Usuario(
            nombre_usuario="Administrador",
            email="admin@local.com",
            id_roles=rol_admin.id_roles,
            activo=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin creado")
    else:
        print("ℹ️ Admin ya existe")