# app/models/historia_clinica.py

from app import db
from datetime import datetime

class HistoriaClinica(db.Model):
    __tablename__ = 'historias_clinicas'

    id_historia = db.Column(db.Integer, primary_key=True)
    id_mascota = db.Column(db.Integer, db.ForeignKey('mascotas.id_mascota'), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.Text, nullable=False)
    tratamiento = db.Column(db.Text)
    diagnostico = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    id_cita = db.Column(db.Integer, db.ForeignKey('citas.id_cita'))
    id_veterinario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    # Relaciones
    mascota = db.relationship('Mascota', back_populates='historia_clinica')
    cita = db.relationship('Cita', back_populates='historia_clinica', uselist=False)
    
    # ✅ Usa backref para crear automáticamente la relación en Usuario
    veterinario = db.relationship('Usuario', backref='historias_clinicas')
    
    recetas = db.relationship('Receta', back_populates='historia_clinica', lazy=True)
    
    def __repr__(self):
        return f"<HistoriaClinica {self.id_historia}>"