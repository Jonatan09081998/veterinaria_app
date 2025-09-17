# app/models/usuario.py

from app import db
from flask_login import UserMixin 

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='cliente')
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(15))

    # Solo estas relaciones
    carrito = db.relationship('Carrito', back_populates='usuario', uselist=False)
    citas_cliente = db.relationship('Cita', foreign_keys='Cita.id_usuario', back_populates='usuario')
    citas_veterinario = db.relationship('Cita', foreign_keys='Cita.id_veterinario', back_populates='veterinario_rel')
    mascotas = db.relationship('Mascota', back_populates='usuario')

    def get_id(self):
        return str(self.id_usuario)

    def __repr__(self):
        return f"<Usuario {self.nombre}>"