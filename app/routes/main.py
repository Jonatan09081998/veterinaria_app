from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.decorators import rol_requerido
from app.models.mascota import Mascota
from app.models.cita import Cita
from app.models.usuario import Usuario
from datetime import datetime, date  # ✅ Corregido: Importa date específicamente
from app.models.historia_clinica import HistoriaClinica
from app.models.receta import Receta
from app import db
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    
    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).all()

    # Mostrar citas pendientes más antiguas primero
    citas_pendientes = Cita.query.filter_by(
        id_usuario=current_user.id_usuario,
        estado="pendiente"
    ).order_by(Cita.fecha.asc()).all()

     # Mostrar citas atendidas más recientes primero
    citas_atendidas = Cita.query.filter_by(
        id_usuario=current_user.id_usuario,
        estado="atendida"
    ).order_by(Cita.fecha.desc()).all()

    return render_template(
        "dashboard.html",
        mascotas=mascotas,
        citas_pendientes=citas_pendientes,
        citas_atendidas=citas_atendidas
    )


@main_bp.route("/admin")
@login_required
@rol_requerido("admin")
def admin_panel():
    if current_user.rol != "admin":
        flash("No tienes permiso para acceder a este panel", "error")
        return redirect(url_for("main.dashboard"))
    # Datos para el administrador
    usuarios = Usuario.query.all()
    mascotas = Mascota.query.all()
    citas = Cita.query.filter_by(estado="pendiente").order_by(Cita.fecha.asc()).all()

    return render_template("admin_panel.html", usuarios=usuarios, mascotas=mascotas, citas=citas)


@main_bp.route('/veterinario')
@login_required
def veterinario_panel():
    if current_user.rol != 'veterinario':
        flash('No tienes permiso para acceder a este panel', 'error')
        return redirect(url_for('main.dashboard'))
    
    # ✅ Mostrar TODAS las citas pendientes (no solo de hoy)
    citas_pendientes = Cita.query.filter(
        Cita.estado == 'pendiente',
        Cita.id_veterinario == current_user.id_usuario
    ).join(Mascota).all()
    
    # ✅ Citas atendidas (últimas 10)
    citas_atendidas = Cita.query.filter(
        Cita.estado == 'atendida',
        Cita.id_veterinario == current_user.id_usuario
    ).order_by(Cita.fecha.desc()).limit(10).all()
    
    # Recetas recientes
    recetas = Receta.query.join(HistoriaClinica).filter(
        HistoriaClinica.id_veterinario == current_user.id_usuario
    ).order_by(Receta.fecha.desc()).limit(10).all()
    
    return render_template('veterinario_panel.html', 
                          citas_pendientes=citas_pendientes,
                          citas_atendidas=citas_atendidas,
                          recetas=recetas)
    
@main_bp.route('/veterinario/atender/<int:id_cita>', methods=['POST'])
@login_required
def atender_cita(id_cita):
    if current_user.rol != 'veterinario':
        flash('No tienes permiso para realizar esta acción', 'error')
        return redirect(url_for('main.dashboard'))
    
    cita = Cita.query.get_or_404(id_cita)
    
    # ✅ DEPURACIÓN: Imprime información para entender el problema
    print(f"DEBUG - Cita ID: {id_cita}")
    print(f"DEBUG - Estado actual: {cita.estado}")
    print(f"DEBUG - Fecha cita: {cita.fecha}, Tipo: {type(cita.fecha)}")
    print(f"DEBUG - Fecha hoy: {date.today()}, Tipo: {type(date.today())}")
    
    # ✅ CORREGIDO: Comparación más flexible de fechas
    if cita.estado != 'pendiente' or cita.fecha < date.today():
        flash(f'Esta cita no puede ser atendida. Estado: {cita.estado}, Fecha: {cita.fecha}', 'error')
        return redirect(url_for('main.veterinario_panel'))
    
    # Verificar que la cita esté asignada a este veterinario
    if cita.id_veterinario != current_user.id_usuario:
        flash('No puedes atender esta cita', 'error')
        return redirect(url_for('main.veterinario_panel'))
    
    # Marcar como atendida
    cita.estado = 'atendida'
    db.session.commit()
    
    flash('✅ Cita atendida correctamente', 'success')
    return redirect(url_for('main.veterinario_panel'))