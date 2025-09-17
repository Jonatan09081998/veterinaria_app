from app import db
from app.models.producto import Producto

class Medicamento(Producto):
    __tablename__ = 'medicamentos'
    
    # CORREGIDO: Usamos id_producto como primary key (heredado de Producto)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), primary_key=True)
    dosis = db.Column(db.String(100))
    indicaciones = db.Column(db.Text)
    contraindicaciones = db.Column(db.Text)
    laboratorio = db.Column(db.String(100))
    registro_sanitario = db.Column(db.String(50), unique=True)
    
    # Relación con recetas
    receta_medicamentos = db.relationship('RecetaMedicamento', back_populates='medicamento', lazy=True)