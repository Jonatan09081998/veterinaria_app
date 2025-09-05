from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.decorators import rol_requerido
from app.models.mascota import Mascota
from app.models.cita import Cita
from app.models.usuario import Usuario

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("home.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).all()

    # ✅ Citas pendientes
    citas_pendientes = Cita.query.filter_by(
        id_usuario=current_user.id_usuario,
        estado="pendiente"
    ).order_by(Cita.fecha.asc()).all()

    # ✅ Citas atendidas
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
    # Datos para el administrador
    usuarios = Usuario.query.all()
    mascotas = Mascota.query.all()
    citas = Cita.query.filter_by(estado="pendiente").order_by(Cita.fecha.asc()).all()

    return render_template("admin_panel.html", usuarios=usuarios, mascotas=mascotas, citas=citas)


@main_bp.route("/veterinario")
@login_required
@rol_requerido("veterinario")
def veterinario_panel():
    # Citas pendientes para el veterinario
    citas = Cita.query.filter_by(estado='pendiente').order_by(Cita.fecha.asc()).all()
    return render_template("veterinario_panel.html", citas=citas)