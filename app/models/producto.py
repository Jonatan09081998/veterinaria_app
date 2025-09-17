# app/models/producto.py
from app import db

class Producto(db.Model):
    __tablename__ = 'productos'

    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(200), default='/static/img/producto-default.jpg')
    categoria = db.Column(db.String(50))
    receta_medicamentos = db.relationship('RecetaMedicamento', back_populates='medicamento')
    def __repr__(self):
        return f"<Producto {self.nombre}>"