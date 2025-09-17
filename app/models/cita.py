from app import db

# app/models/cita.py
class Cita(db.Model):
    __tablename__ = 'citas'
    id_cita = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    id_mascota = db.Column(db.Integer, db.ForeignKey('mascotas.id_mascota'), nullable=False)
    
    # Dos relaciones con la tabla usuarios
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)  # Dueño de la mascota
    id_veterinario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=True)  # Veterinario asignado

    # Relaciones (¡aquí está el cambio clave!)
    mascota = db.relationship('Mascota', back_populates='citas')
    historia_clinica = db.relationship('HistoriaClinica', back_populates='cita', uselist=False)
    
    # ✅ Cambiamos las relaciones para que sean claras
    usuario = db.relationship('Usuario', foreign_keys=[id_usuario], back_populates='citas_cliente')
    veterinario_rel = db.relationship('Usuario', foreign_keys=[id_veterinario], back_populates='citas_veterinario')
    # Evitar duplicados en misma fecha y hora
    __table_args__ = (
        db.UniqueConstraint('fecha', 'hora', name='_fecha_hora_uc'),
        db.Index('ix_cita_fecha', 'fecha'),
    )

    def __repr__(self):
        return f"<Cita {self.fecha} - {self.motivo[:20]}...>"