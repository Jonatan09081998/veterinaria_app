# app/routes/citas.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import login_required, current_user
from app.models.cita import Cita
from app.models.mascota import Mascota
from app import db
from datetime import datetime
from app.models.usuario import Usuario

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

            # ✅ OBTÉN EL VETERINARIO CON ID 2 (el que tiene rol 'veterinario')
            veterinario = Usuario.query.filter_by(rol='veterinario').first()
            
            if not veterinario:
                flash('❌ No hay veterinarios disponibles. Contacta al administrador.', 'error')
                return redirect(url_for('citas.reservar_cita'))

            # ✅ VERIFICA QUE NO EXISTA UNA CITA PARA ESTE VETERINARIO EN ESE HORARIO
            existe_cita = Cita.query.filter_by(
                fecha=fecha,
                hora=hora,
                id_veterinario=veterinario.id_usuario
            ).first()
            
            if existe_cita:
                flash('❌ Ya existe una cita en ese horario. Elige otro.', 'error')
                mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).all()
                return render_template('citas/reservar.html', mascotas=mascotas)

            # ✅ CREA LA CITA CON EL VETERINARIO CORRECTO
            cita = Cita(
                fecha=fecha,
                hora=hora,
                motivo=motivo,
                id_mascota=id_mascota,
                id_usuario=current_user.id_usuario,
                id_veterinario=veterinario.id_usuario  # ✅ Asegúrate que esto esté aquí
            )
            db.session.add(cita)
            db.session.commit()

            flash(f'✅ Cita reservada exitosamente con {veterinario.nombre}.', 'success')
            return redirect(url_for('citas.listar'))

        except Exception as e:
            db.session.rollback()
            flash('❌ Error al reservar la cita. Inténtalo de nuevo.', 'error')

    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).order_by(Mascota.nombre).all()
    return render_template('citas/reservar.html', mascotas=mascotas)

    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).order_by(Mascota.nombre).all()
    return render_template('citas/reservar.html', mascotas=mascotas)
@citas_bp.route("/listar")
@login_required
def listar_citas():
    citas = Cita.query.filter(
        Cita.id_usuario == current_user.id_usuario,
        Cita.estado == 'pendiente',
        Cita.fecha >= datetime.now().date()   # ✅ Solo citas futuras o actuales
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
    if current_user.rol != 'veterinario':
        flash("❌ No tienes permiso para atender citas", "error")
        return redirect(url_for("main.dashboard"))

    cita = Cita.query.get_or_404(id_cita)

    # ✅ Verificar que la cita esté asignada a este veterinario
    if cita.id_veterinario != current_user.id_usuario:
        flash("❌ No puedes atender esta cita", "error")
        return redirect(url_for("main.veterinario_panel"))

    # ✅ Verificar que la cita esté pendiente
    if cita.estado != 'pendiente':
        flash("❌ Esta cita ya fue atendida o cancelada", "error")
        return redirect(url_for("main.veterinario_panel"))

    cita.estado = "atendida"
    db.session.commit()
    flash("✅ La cita fue marcada como atendida", "success")

    return redirect(url_for("main.veterinario_panel"))



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