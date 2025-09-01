from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.decorators import rol_requerido

# Importar modelos
from app.models.mascota import Mascota
from app.models.cita import Cita

# Importar blueprints si necesitas usar sus rutas
from app.routes.citas import citas_bp  # Solo si necesitas registrarla aquí

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    # Opcional: redirigir si ya está logueado
    # if current_user.is_authenticated:
    #     return redirect(url_for("main.dashboard"))
    return render_template("home.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).all()
    citas = Cita.query.filter_by(id_usuario=current_user.id_usuario).order_by(Cita.fecha.asc()).all()
    return render_template("dashboard.html", mascotas=mascotas, citas=citas)

@main_bp.route("/admin")
@login_required
@rol_requerido("admin")
def admin_panel():
    return render_template("admin_panel.html")

@main_bp.route("/veterinario")
@login_required
@rol_requerido("veterinario")
def veterinario_panel():
    return render_template("veterinario_panel.html")