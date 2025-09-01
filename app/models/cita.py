from app import db

class Cita(db.Model):
    __tablename__ = 'citas'

    id_cita = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    motivo = db.Column(db.String(255))
    estado = db.Column(db.String(20), default='pendiente')
    id_mascota = db.Column(db.Integer, db.ForeignKey('mascotas.id_mascota'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'))

    # Relaciones
    mascota = db.relationship('Mascota', backref=db.backref('citas', lazy=True))
    usuario = db.relationship('Usuario', backref=db.backref('citas', lazy=True))

    # Evitar duplicados en misma fecha y hora
    __table_args__ = (
        db.UniqueConstraint('fecha', 'hora', name='_fecha_hora_uc'),
        db.Index('ix_cita_fecha', 'fecha'),
    )

    def __repr__(self):
        return f"<Cita {self.fecha} - {self.motivo[:20]}...>"