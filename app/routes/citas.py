# app/routes/citas.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_required, current_user
from app.models.cita import Cita
from app.models.mascota import Mascota
from app import db
from datetime import datetime
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

            mascota = Mascota.query.filter_by(id_mascota=id_mascota, id_usuario=current_user.id_usuario).first()
            if not mascota:
                flash('❌ No tienes permiso para gestionar esta mascota.', 'error')
                return redirect(url_for('mascotas.index'))

            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora = datetime.strptime(hora_str, '%H:%M').time()

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
            return redirect(url_for('citas.listar'))

        except Exception as e:
            db.session.rollback()
            flash('❌ Error al reservar la cita. Inténtalo de nuevo.', 'error')

    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).order_by(Mascota.nombre).all()
    return render_template('citas/reservar.html', mascotas=mascotas)

@citas_bp.route("/listar")
@login_required
def listar_citas():
    citas = Cita.query.filter(
        Cita.id_usuario == current_user.id_usuario,
        Cita.estado == 'pendiente',
        Cita.fecha >= datetime.now()   # ✅ Solo citas futuras o actuales
    ).order_by(Cita.fecha.asc()).all()

    return render_template("citas/listar.html", citas=citas)
# ✅ NUEVAS RUTAS: Editar, Actualizar y Cancelar

@citas_bp.route('/editar/<int:id_cita>')
@login_required
def editar_cita(id_cita):
    cita = Cita.query.get_or_404(id_cita)
    
    if cita.id_usuario != current_user.id_usuario:
        flash('❌ No tienes permiso para editar esta cita.', 'error')
        return redirect(url_for('citas.listar'))
    
    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).all()
    return render_template('citas/editar.html', cita=cita, mascotas=mascotas)

@citas_bp.route("/atender/<int:id_cita>", methods=["POST"])
@login_required
def atender_cita(id_cita):
    cita = Cita.query.get_or_404(id_cita)

    # seguridad: solo el dueño puede marcar su cita
    if cita.id_usuario != current_user.id_usuario:
        flash("No puedes modificar esta cita", "danger")
        return redirect(url_for("citas.listar_citas"))

    cita.estado = "atendida"
    db.session.commit()
    flash("✅ La cita fue marcada como atendida", "success")

    return redirect(url_for("citas.listar_citas"))



@citas_bp.route('/actualizar/<int:id_cita>', methods=['POST'])
@login_required
def actualizar_cita(id_cita):
    cita = Cita.query.get_or_404(id_cita)
    
    if cita.id_usuario != current_user.id_usuario:
        flash('❌ No tienes permiso.', 'error')
        return redirect(url_for('mascotas.index'))
    
    try:
        fecha_str = request.form['fecha']
        hora_str = request.form['hora']
        motivo = request.form['motivo']
        id_mascota = request.form['id_mascota']

        cita.fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        cita.hora = datetime.strptime(hora_str, '%H:%M').time()
        cita.motivo = motivo
        cita.id_mascota = id_mascota

        db.session.commit()
        flash('✅ Cita actualizada exitosamente.', 'success')
        return redirect(url_for('citas.listar_citas'))

    except Exception as e:
        db.session.rollback()
        flash('❌ Error al actualizar la cita.', 'error')
        return redirect(url_for('citas.editar_cita', id_cita=id_cita))


@citas_bp.route('/cancelar/<int:id_cita>')
@login_required
def cancelar_cita(id_cita):
    cita = Cita.query.get_or_404(id_cita)
    
    if cita.id_usuario != current_user.id_usuario:
        flash('❌ No tienes permiso para cancelar esta cita.', 'error')
    elif cita.estado == 'cancelada':
        flash('⚠️ Esta cita ya está cancelada.', 'info')
    else:
        cita.estado = 'cancelada'
        db.session.commit()
        flash('✅ Cita cancelada exitosamente.', 'success')
    
    return redirect(url_for('citas.listar_citas'))