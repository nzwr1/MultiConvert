from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Rol(db.Model):
    __tablename__ = "roles"
    id_roles = db.Column(db.Integer, primary_key=True)
    nombre_roles = db.Column(db.String(20), nullable=False)

class Usuario(db.Model):
    __tablename__ = "usuarios"
    id_usuarios = db.Column(db.Integer, primary_key=True)
    id_roles = db.Column(db.Integer, db.ForeignKey("roles.id_roles"))
    nombre_usuario = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())

    rol = db.relationship("Rol")

    def set_password(self, password):
        self.contrasena = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasena, password)