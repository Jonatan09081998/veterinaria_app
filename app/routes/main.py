from flask import Blueprint, render_template
from flask_login import login_required
from app.decorators import rol_requerido
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@login_required
def index():
    return render_template("dashboard.html", current_user=current_user)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

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
