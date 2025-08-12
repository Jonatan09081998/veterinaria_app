from app import db
from datetime import datetime

class Carrito(db.Model):
    __tablename__ = "carrito"

    id_carrito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relación con usuario (FK específica)
    usuario = db.relationship(
        "Usuario",
        back_populates="carrito",
        foreign_keys=[id_usuario]
    )
