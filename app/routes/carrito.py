# app/routes/carrito.py
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from app.models.carrito import Carrito, CarritoItem
from app.models.producto import Producto
from app import db

carrito_bp = Blueprint('carrito', __name__, url_prefix='/carrito')

@carrito_bp.route('/agregar/<int:id_producto>', methods=['POST'])
@login_required
def agregar(id_producto):
    producto = Producto.query.get_or_404(id_producto)

    if producto.stock <= 0:
        flash('❌ Producto sin stock.', 'error')
        return redirect(url_for('producto.tienda'))

    try:
        # Obtener cantidad del formulario
        cantidad = int(request.form.get('cantidad', 1))
        
        if cantidad < 1:
            flash('❌ Cantidad inválida.', 'error')
            return redirect(url_for('producto.tienda'))
        
        if cantidad > producto.stock:
            flash(f'❌ Solo hay {producto.stock} unidades disponibles.', 'warning')
            return redirect(url_for('producto.tienda'))

        # Obtener o crear carrito del usuario
        carrito = Carrito.query.filter_by(id_usuario=current_user.id_usuario).first()
        if not carrito:
            carrito = Carrito(id_usuario=current_user.id_usuario)
            db.session.add(carrito)
            db.session.flush()

        # Verificar si el producto ya está en el carrito
        item = CarritoItem.query.filter_by(
            id_carrito=carrito.id_carrito, 
            id_producto=producto.id_producto
        ).first()

        if item:
            nueva_cantidad = item.cantidad + cantidad
            if nueva_cantidad <= producto.stock:
                item.cantidad = nueva_cantidad
                producto.stock -= cantidad
                flash(f'✅ {producto.nombre} actualizado en el carrito. Total: {nueva_cantidad} unidades.', 'success')
            else:
                flash(f'❌ No hay suficiente stock. Máximo disponible: {producto.stock - item.cantidad} unidades más.', 'warning')
        else:
            # Crear nuevo ítem
            item = CarritoItem(
                id_carrito=carrito.id_carrito, 
                id_producto=producto.id_producto, 
                cantidad=cantidad
            )
            db.session.add(item)
            producto.stock -= cantidad
            flash(f'✅ {producto.nombre} agregado al carrito ({cantidad} unidades).', 'success')

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('❌ Error al agregar al carrito. Inténtalo de nuevo.', 'error')
        print(f"Error al agregar al carrito: {str(e)}")

    return redirect(url_for('producto.tienda'))
@carrito_bp.route('/eliminar/<int:id_item>', methods=['POST'])
@login_required
def eliminar(id_item):
    item = CarritoItem.query.get_or_404(id_item)
    
    # Verificar que el item pertenezca al carrito del usuario actual
    if item.carrito.id_usuario != current_user.id_usuario:
        flash('No tienes permiso para eliminar este item', 'error')
        return redirect(url_for('carrito.ver'))
    
    # Recuperar el producto y aumentar su stock
    producto = item.producto
    producto.stock += item.cantidad
    
    # Eliminar el item del carrito
    db.session.delete(item)
    db.session.commit()
    
    flash('✅ Producto eliminado del carrito', 'success')
    return redirect(url_for('carrito.ver'))

@carrito_bp.route('/')
@login_required
def ver():
    carrito = Carrito.query.filter_by(id_usuario=current_user.id_usuario).first()
    items = []
    total = 0.0

    if carrito:
        items = CarritoItem.query.filter_by(id_carrito=carrito.id_carrito).all()
        total = sum(item.cantidad * item.producto.precio for item in items)

    return render_template('carrito/ver.html', items=items, total=total)