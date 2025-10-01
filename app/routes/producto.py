from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.producto import Producto
from app import db
import os
from flask import current_app
from werkzeug.utils import secure_filename


producto_bp = Blueprint('producto', __name__, url_prefix='/producto')

@producto_bp.route('/tienda')
def tienda():
    categoria = request.args.get('categoria', 'todos')
    productos = Producto.query.all()
    # Obtener todos los productos
    productos = Producto.query.all()

    # Filtrar en memoria
    if categoria == 'medicamento':
        # Lista de palabras clave que identifican medicamentos
        palabras_clave = ['amoxicilina', 'ivermectina', 'ketofast', 'paracetamol', 'antibiótico', 'antipulgas']
        productos = [
            p for p in productos
            if any(keyword in p.nombre.lower() for keyword in palabras_clave)
        ]
    elif categoria == 'producto':
        palabras_clave = ['amoxicilina', 'ivermectina', 'ketofast', 'paracetamol', 'antibiótico', 'antipulgas']
        productos = [
            p for p in productos
            if not any(keyword in p.nombre.lower() for keyword in palabras_clave)
        ]
    return render_template('producto/tienda.html', productos=productos)

@producto_bp.route('/crear_medicamento', methods=['GET', 'POST'])
@login_required
def crear_medicamento():
    if current_user.rol != 'admin':
        flash('No tienes permiso para crear medicamentos', 'error')
        return redirect(url_for('producto.tienda'))

    # Asegurar que la carpeta 'static/img' exista
    upload_folder = os.path.join(current_app.root_path, 'static', 'img')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])

        # Guardar imagen
        imagen = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)  # Ruta absoluta
                file.save(filepath)
                imagen = filename  # Solo el nombre del archivo

        # Crear producto como medicamento
        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen=imagen,
            categoria='medicamento'  # Asegúrate de tener este campo en tu modelo
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('✅ Medicamento creado exitosamente', 'success')
        return redirect(url_for('producto.tienda'))

    return render_template('producto/crear_medicamento.html') 



@producto_bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    if current_user.rol != 'admin':
        flash('No tienes permiso para crear productos', 'error')
        return redirect(url_for('producto.tienda'))

    # Asegurar que la carpeta 'static/img' exista
    upload_folder = os.path.join(current_app.root_path, 'static', 'img')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion', '')
        precio = float(request.form['precio'])
        stock = int(request.form['stock'])

        # Guardar imagen
        imagen = None
        if 'imagen' in request.files:
            file = request.files['imagen']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(upload_folder, filename)  # ✅ Ruta absoluta
                file.save(filepath)
                imagen = filename  # ✅ Ruta relativa para BD

        nuevo_producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen=imagen
        )
        db.session.add(nuevo_producto)
        db.session.commit()
        flash('✅ Producto creado exitosamente', 'success')
        return redirect(url_for('producto.tienda'))

    return render_template('producto/crear.html')




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