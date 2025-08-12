from app import db
from flask_login import UserMixin

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(50), nullable=False, default="usuario")
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(45))

    # Relación con carrito (se especifica la FK correcta)
    carrito = db.relationship(
        "Carrito",
        back_populates="usuario",
        foreign_keys="[Carrito.id_usuario]",
        uselist=False  # Un usuario tiene un solo carrito
    )

    # Métodos requeridos por Flask-Login
    @property
    def is_active(self):
        return True

    def get_id(self):
        return str(self.id_usuario)
