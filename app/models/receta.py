from app import db
import datetime

class Receta(db.Model):
    __tablename__ = 'recetas'
    
    id_receta = db.Column(db.Integer, primary_key=True)
    id_historia = db.Column(db.Integer, db.ForeignKey('historias_clinicas.id_historia'), nullable=False)
    fecha = db.Column(db.Date, default=datetime.date.today)
    
    # Relaciones
    medicamentos = db.relationship('RecetaMedicamento', back_populates='receta', cascade='all, delete-orphan', lazy=True)
    historia_clinica = db.relationship('HistoriaClinica', back_populates='recetas')

class RecetaMedicamento(db.Model):
    __tablename__ = 'receta_medicamento'
    
    id_receta_medicamento = db.Column(db.Integer, primary_key=True)
    id_receta = db.Column(db.Integer, db.ForeignKey('recetas.id_receta'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    indicaciones = db.Column(db.String(255), nullable=False)
    
    id_historia = db.Column(db.Integer, db.ForeignKey('historias_clinicas.id_historia'), nullable=False)
    
    medicamento = db.relationship('Producto', back_populates='receta_medicamentos')
    receta = db.relationship('Receta', back_populates='medicamentos')