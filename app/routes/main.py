from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.decorators import rol_requerido

main_bp = Blueprint("main", __name__)

@main_bp.route("/")  # Landing pública
def home():
    # Si ya está logueado, puedes mandarlo directo a su panel:
    # return redirect(url_for("main.dashboard"))
    return render_template("home.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")  # tu panel con sidebar

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
