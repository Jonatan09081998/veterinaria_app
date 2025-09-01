from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.historia_clinica import HistoriaClinica
from app.models.mascota import Mascota
from flask_login import login_required, current_user
from datetime import datetime

historia_bp = Blueprint("historia", __name__, url_prefix="/historia")

# 📌 Listar historias de una mascota
@historia_bp.route("/listar/<int:id_mascota>")
@login_required
def listar(id_mascota):
    mascota = Mascota.query.get_or_404(id_mascota)

    # Validar propietario
    if mascota.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para ver la historia clínica de esta mascota", "danger")
        return redirect(url_for("mascotas.listar"))

    historias = HistoriaClinica.query.filter_by(id_mascota=id_mascota).all()
    return render_template("historia/listar.html", mascota=mascota, historias=historias)

# 📌 Crear historia clínica
@historia_bp.route("/crear/<int:id_mascota>", methods=["GET", "POST"])
@login_required
def crear(id_mascota):
    mascota = Mascota.query.get_or_404(id_mascota)

    if mascota.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para agregar historia clínica a esta mascota", "danger")
        return redirect(url_for("mascotas.listar"))

    if request.method == "POST":
        descripcion = request.form["descripcion"]
        diagnostico = request.form.get("diagnostico")
        tratamiento = request.form.get("tratamiento")

        nueva_historia = HistoriaClinica(
            id_mascota=id_mascota,
            descripcion=descripcion,
            diagnostico=diagnostico,
            tratamiento=tratamiento
        )
        db.session.add(nueva_historia)
        db.session.commit()
        flash("Historia clínica registrada con éxito", "success")
        return redirect(url_for("historia.listar", id_mascota=id_mascota))

    return render_template("historia/crear.html", mascota=mascota)
