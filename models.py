from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# --- MODELOS PRINCIPALES ---

class Rol(db.Model):
    __tablename__ = "roles"
    id_roles = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column('nombre_roles', db.String(50), nullable=False, unique=True)  # ✅ Mapeo explícito

    usuarios = db.relationship("Usuario", back_populates="rol")
class Usuario(db.Model):
    __tablename__ = "usuarios"
    id_usuarios = db.Column(db.Integer, primary_key=True)
    id_roles = db.Column(db.Integer, db.ForeignKey("roles.id_roles"), nullable=False)  # ✅ Foreign key correcta
    nombre_usuario = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.Text, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    rol = db.relationship("Rol", back_populates="usuarios")

    # Relaciones
    rol = db.relationship("Rol", back_populates="usuarios")
    suscripciones = db.relationship("Suscripcion", back_populates="usuario")
    pagos = db.relationship("Pago", back_populates="usuario")
    api_keys = db.relationship("ApiKey", back_populates="usuario")
    conversions = db.relationship("Conversion", back_populates="usuario")

    def set_password(self, password):
        self.contrasena = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.contrasena, password)

class Plan(db.Model):
    __tablename__ = "planes"
    id_planes = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    precio = db.Column(db.Float, nullable=False)
    limite_conversiones = db.Column(db.Integer, nullable=False)
    duracion_dias = db.Column(db.Integer, nullable=False)

    # Relaciones
    suscripciones = db.relationship("Suscripcion", back_populates="plan")

class Suscripcion(db.Model):
    __tablename__ = "suscripciones"
    id_suscripcion = db.Column(db.Integer, primary_key=True)
    id_usuarios = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuarios"), nullable=False)
    id_planes = db.Column(db.Integer, db.ForeignKey("planes.id_planes"), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_fin = db.Column(db.DateTime, nullable=True)

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="suscripciones")
    plan = db.relationship("Plan", back_populates="suscripciones")

class Pago(db.Model):
    __tablename__ = "pagos"
    id_pagos = db.Column(db.Integer, primary_key=True)
    id_usuarios = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuarios"), nullable=False)
    id_transaccion = db.Column(db.String(255), unique=True, nullable=True) 
    numero_orden = db.Column(db.String(255), unique=True, nullable=True) 
    monto = db.Column(db.Float, nullable=False)
    moneda = db.Column(db.String(10), nullable=True) 
    metodo_pago = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_pago = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="pagos")


# --- MODELOS DE CONVERSIONES ---

class Formato(db.Model):
    __tablename__ = "formatos"
    id_formatos = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), unique=True, nullable=False) # e.g., 'pdf', 'docx', 'jpg'
    categoria = db.Column(db.String(100), nullable=True) # e.g., 'Documento', 'Imagen'

class ConversionPermitida(db.Model):
    __tablename__ = "conversiones_permitidas"
    id_conversionesper = db.Column(db.Integer, primary_key=True)
    id_origen = db.Column(db.Integer, db.ForeignKey("formatos.id_formatos"), nullable=False)
    id_destino = db.Column(db.Integer, db.ForeignKey("formatos.id_formatos"), nullable=False)
    
    # Restricción para evitar pares duplicados (origen -> destino)
    __table_args__ = (db.UniqueConstraint('id_origen', 'id_destino', name='_origen_destino_uc'),)

class Conversion(db.Model):
    __tablename__ = "conversiones"
    id_conversiones = db.Column(db.Integer, primary_key=True)
    id_usuarios = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuarios"), nullable=False)
    id_formato_origen = db.Column(db.Integer, db.ForeignKey("formatos.id_formatos"), nullable=False)
    id_formato_destino = db.Column(db.Integer, db.ForeignKey("formatos.id_formatos"), nullable=False)
    nombre_archivo_origen = db.Column(db.String(255), nullable=False)
    nombre_archivo_convertido = db.Column(db.String(255), nullable=True)
    peso_origen_kb = db.Column(db.Integer, nullable=True)
    peso_resultado_kb = db.Column(db.Integer, nullable=True)
    duracion_segundos = db.Column(db.Float, nullable=True)
    estado = db.Column(db.String(50), nullable=False, default="iniciado")
    fecha = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relaciones
    usuario = db.relationship("Usuario", back_populates="conversions")
    formato_origen = db.relationship("Formato", foreign_keys=[id_formato_origen])
    formato_destino = db.relationship("Formato", foreign_keys=[id_formato_destino])


# --- MODELOS DE API ---

class ApiKey(db.Model):
    __tablename__ = "api_keys"
    id_api = db.Column(db.Integer, primary_key=True)
    id_usuarios = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuarios"), nullable=False)
    clave_api = db.Column(db.String(255), unique=True, nullable=False)
    activa = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_expiracion = db.Column(db.DateTime, nullable=True)
    nombre_etiqueta = db.Column(db.String(100), nullable=True)
    
    # Relaciones
    usuario = db.relationship("Usuario", back_populates="api_keys")