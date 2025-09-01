from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.mascota import Mascota
from app.decorators import login_required
from flask_login import current_user
from datetime import datetime

mascotas_bp = Blueprint("mascotas", __name__, url_prefix="/mascotas")

# 📌 Listar mascotas del usuario
@mascotas_bp.route("/")
@login_required
def index():
    mascotas = Mascota.query.filter_by(id_usuario=current_user.id_usuario).all()
    return render_template("mascotas/index.html", mascotas=mascotas)

# 📌 Crear mascota
@mascotas_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        nombre = request.form["nombre"]
        especie = request.form["especie"]
        raza = request.form["raza"]
        genero = request.form["genero"]

        # 📌 Procesar fecha
        fecha_nacimiento = request.form.get("fecha_nacimiento")
        if fecha_nacimiento:
            fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
        else:
            fecha_nacimiento = None  # por si no llenan el campo

        nueva_mascota = Mascota(
            nombre=nombre,
            especie=especie,
            raza=raza,
            genero=genero,
            fecha_nacimiento=fecha_nacimiento,
            id_usuario=current_user.id_usuario
        )
        db.session.add(nueva_mascota)
        db.session.commit()
        flash("Mascota registrada con éxito", "success")
        return redirect(url_for("mascotas.index"))

    return render_template("mascotas/crear.html")

# 📌 Editar mascota
@mascotas_bp.route("/editar/<int:id_mascota>", methods=["GET", "POST"])
@login_required
def editar(id_mascota):
    mascota = Mascota.query.get_or_404(id_mascota)

    # Validación de propietario
    if mascota.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para editar esta mascota", "danger")
        return redirect(url_for("mascotas.index"))

    if request.method == "POST":
        mascota.nombre = request.form["nombre"]
        mascota.especie = request.form["especie"]
        mascota.raza = request.form["raza"]
        mascota.genero = request.form["genero"]

        # 📌 Procesar fecha
        fecha_nacimiento = request.form.get("fecha_nacimiento")
        if fecha_nacimiento:
            mascota.fecha_nacimiento = datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()
        else:
            mascota.fecha_nacimiento = None

        db.session.commit()
        flash("Mascota actualizada con éxito", "success")
        return redirect(url_for("mascotas.index"))

    return render_template("mascotas/editar.html", mascota=mascota)

# 📌 Eliminar mascota
@mascotas_bp.route("/eliminar/<int:id_mascota>", methods=["POST"])
@login_required
def eliminar(id_mascota):
    mascota = Mascota.query.get_or_404(id_mascota)

    # Validación de propietario
    if mascota.id_usuario != current_user.id_usuario:
        flash("No tienes permiso para eliminar esta mascota", "danger")
        return redirect(url_for("mascotas.index"))

    db.session.delete(mascota)
    db.session.commit()
    flash("Mascota eliminada con éxito", "info")

    return redirect(url_for("mascotas.index"))
