from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.medicamento import Medicamento
from app import db

medicamento_bp = Blueprint('medicamento', __name__, url_prefix='/medicamentos')

@medicamento_bp.route('/')
@login_required
def listar():
    if current_user.rol not in ['veterinario', 'admin']:
        flash('No tienes permiso para acceder a medicamentos', 'error')
        return redirect(url_for('main.dashboard'))
    
    medicamentos = Medicamento.query.all()
    return render_template('medicamento/listar.html', medicamentos=medicamentos)

# CORREGIDO: Usa id_medicamento (primary key) en lugar de id_producto
@medicamento_bp.route('/editar/<int:id_producto>', methods=['GET', 'POST'])
@login_required
def editar(id_producto):
    if current_user.rol not in ['admin', 'veterinario']:
        flash('No tienes permiso para editar medicamentos', 'error')
        return redirect(url_for('medicamento.listar'))
    
    # CORREGIDO: Buscar por id_producto (primary key)
    medicamento = Medicamento.query.get_or_404(id_producto)
    
    if request.method == 'POST':
        # Actualizar campos
        medicamento.dosis = request.form['dosis']
        medicamento.indicaciones = request.form['indicaciones']
        medicamento.contraindicaciones = request.form['contraindicaciones']
        medicamento.laboratorio = request.form['laboratorio']
        
        # Solo admins pueden editar estos campos
        if current_user.rol == 'admin':
            medicamento.nombre = request.form['nombre']
            medicamento.precio = float(request.form['precio'])
            medicamento.stock = int(request.form['stock'])
            medicamento.registro_sanitario = request.form['registro_sanitario']
        
        db.session.commit()
        flash('✅ Medicamento actualizado exitosamente', 'success')
        return redirect(url_for('medicamento.listar'))
    
    return render_template(
        'medicamento/editar.html', 
        medicamento=medicamento,
        es_admin=(current_user.rol == 'admin')
    )

@medicamento_bp.route('/eliminar/<int:id_producto>', methods=['POST'])
@login_required
def eliminar(id_producto):
    if current_user.rol != 'admin':
        flash('No tienes permiso para eliminar medicamentos', 'error')
        return redirect(url_for('medicamento.listar'))
    
    # CORREGIDO: Buscar por id_producto
    medicamento = Medicamento.query.get_or_404(id_producto)
    db.session.delete(medicamento)
    db.session.commit()
    flash('✅ Medicamento eliminado exitosamente', 'success')
    return redirect(url_for('medicamento.listar'))