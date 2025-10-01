# app/models/factura.py
from app import db
from datetime import datetime

class Factura(db.Model):
    __tablename__ = 'facturas'

    id_factura = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.now().date())
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    
    nombre_cliente = db.Column(db.String(100))
    email_cliente = db.Column(db.String(100))
    direccion_envio = db.Column(db.Text)
    telefono_cliente = db.Column(db.String(20))
    metodo_pago = db.Column(db.String(50))

    # Relación con usuario
    usuario = db.relationship('Usuario', backref='facturas')

    # Relación con detalles
    detalles = db.relationship('DetalleFactura', backref='factura', lazy=True)

class DetalleFactura(db.Model):
    __tablename__ = 'detalles_factura'

    id_detalle = db.Column(db.Integer, primary_key=True)
    id_factura = db.Column(db.Integer, db.ForeignKey('facturas.id_factura'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    # Relación con producto
    producto = db.relationship('Producto', backref='detalles_factura')