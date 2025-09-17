from app import db

class Carrito(db.Model):
    __tablename__ = 'carrito'

    id_carrito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    
    usuario = db.relationship('Usuario', back_populates='carrito')
    items = db.relationship('CarritoItem', back_populates='carrito', lazy=True, cascade='all, delete-orphan')

class CarritoItem(db.Model):
    __tablename__ = 'carrito_items'

    id_item = db.Column(db.Integer, primary_key=True)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito.id_carrito'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    
    carrito = db.relationship('Carrito', back_populates='items')
    producto = db.relationship('Producto', backref='carrito_items')