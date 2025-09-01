from app import db
from datetime import datetime

class HistoriaClinica(db.Model):
    __tablename__ = "historia_clinica"

    id_historia= db.Column(db.Integer, primary_key=True)
    id_mascota = db.Column(db.Integer, db.ForeignKey("mascotas.id_mascota"), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.Text, nullable=False)
    tratamiento = db.Column(db.Text, nullable=True)
    diagnostico = db.Column(db.Text, nullable=True)
    # Relación con mascota
    mascota = db.relationship("Mascota", backref="historias")
    def __repr__(self):
        return f"<HistoriaClinica {self.id} - Mascota {self.id_mascota}>"
