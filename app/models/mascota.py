from app import db

class Mascota(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)  # perro, gato, etc.
    raza = db.Column(db.String(100))
    edad = db.Column(db.Integer)
   # models/mascota.py
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False)
    usuario = db.relationship("Usuario", back_populates="mascotas")

    def __init__(self, nombre, especie, raza, edad, usuario_id):
        self.nombre = nombre
        self.especie = especie
        self.raza = raza
        self.edad = edad
        self.usuario_id = usuario_id
        


    def __repr__(self):
        return f"<Mascota {self.nombre}>"
