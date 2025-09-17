from datetime import date
from app import db

class Mascota(db.Model):
    __tablename__ = "mascotas"

    id_mascota = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(50))
    genero = db.Column(db.String(10))
    fecha_nacimiento = db.Column(db.Date)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)

    
    usuario = db.relationship('Usuario', back_populates='mascotas')
    historia_clinica = db.relationship('HistoriaClinica', back_populates='mascota', uselist=False)
    citas = db.relationship('Cita', back_populates='mascota')
    
    # 🔹 Método para calcular la edad automáticamente
    @property
    def edad(self):
        if self.fecha_nacimiento:
            hoy = date.today()
            return hoy.year - self.fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None