from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_required, current_user
from app.models.cita import Cita
from app.models.mascota import Mascota
from app import db

citas_bp = Blueprint('citas', __name__, url_prefix='/citas')

@citas_bp.route('/reservar', methods=['GET', 'POST'])
@login_required
def reservar_cita():
    if request.method == 'POST':
        try:
            fecha_str = request.form['fecha']
            hora_str = request.form['hora']
            motivo = request.form['motivo']
            id_mascota = request.form['id_mascota']

            # Validar que la mascota pertenezca al usuario
            mascota = Mascota.query.filter_by(id_mascota=id_mascota, id_usuario=current_user.id_usuario).first()
            if not mascota:
                flash('❌ No tienes permiso para gestionar esta mascota.', 'error')
                return redirect(url_for('mascotas.index'))

            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora = datetime.strptime(hora_str, '%H:%M').time()

            # Evitar duplicados
            existe_cita = Cita.query.filter_by(fecha=fecha, hora=hora).first()
            if existe_cita:
                flash('❌ Ya existe una cita en ese horario. Elige otro.', 'error')
                return render_template('citas/reservar.html', mascotas=mascotas)

            cita = Cita(
                fecha=fecha,
                hora=hora,
                motivo=motivo,
                id_mascota=id_mascota,
                id_usuario=current_user.id_usuario
            )
            db.session.add(cita)
            db.session.commit()

            flash('✅ Cita reservada exitosamente.', 'success')
            return redirect(url_for('citas.listar_citas'))

        except Exception as e:
            db.session.rollback()
            flash('❌ Error al reservar la cita. Inténtalo de nuevo.', 'error')

    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).order_by(Mascota.nombre).all()
    return render_template('citas/reservar.html', mascotas=mascotas)

@citas_bp.route('/listar')
@login_required
def listar_citas():
    citas = Cita.query.filter_by(id_usuario=current_user.id_usuario).order_by(Cita.fecha.desc()).all()
    return render_template('citas/listar.html', citas=citas)