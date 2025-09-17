from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.producto import Producto
from app import db
import os

producto_bp = Blueprint('producto', __name__, url_prefix='/producto')

@producto_bp.route('/tienda')
def tienda():
    productos = Producto.query.all()
    return render_template('producto/tienda.html', productos=productos)




@producto_bp.route('/editar/<int:id_producto>', methods=['GET', 'POST'])
@login_required
def editar(id_producto):
    if current_user.rol not in ['admin', 'veterinario']:
        flash('No tienes permiso para editar productos', 'error')
        return redirect(url_for('producto.tienda'))
    
    producto = Producto.query.get_or_404(id_producto)
    
    if request.method == 'POST':
        # Actualizar datos
        producto.nombre = request.form['nombre']
        producto.descripcion = request.form['descripcion']
        producto.precio = float(request.form['precio'])
        producto.stock = int(request.form['stock'])
        
        # Actualizar imagen
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file.filename != '':
                # Eliminar imagen antigua
                if producto.imagen and os.path.exists(producto.imagen):
                    os.remove(producto.imagen)
                # Guardar nueva imagen
                imagen = f'uploads/{file.filename}'
                file.save(imagen)
                producto.imagen = imagen
        
        db.session.commit()
        flash('✅ Producto actualizado exitosamente', 'success')
        return redirect(url_for('producto.tienda'))
    
    return render_template('producto/editar.html', producto=producto)

@producto_bp.route('/admin/eliminar/<int:id_producto>')
@login_required
def eliminar(id_producto):
    if current_user.rol != 'admin':
        flash('No tienes permiso para eliminar productos', 'error')
        return redirect(url_for('producto.tienda'))
    
    producto = Producto.query.get_or_404(id_producto)
    # Eliminar imagen si existe
    if producto.imagen and os.path.exists(producto.imagen):
        os.remove(producto.imagen)
    db.session.delete(producto)
    db.session.commit()
    flash('✅ Producto eliminado exitosamente', 'success')
    return redirect(url_for('producto.tienda'))