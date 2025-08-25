from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.mascota import Mascota
from app.decorators import login_required
from flask_login import current_user

mascotas_bp = Blueprint("mascotas", __name__, url_prefix="/mascotas")

# 📌 Listar mascotas del usuario
@mascotas_bp.route("/")
@login_required
def listar():
    mascotas = Mascota.query.filter_by(usuario_id=current_user.id_usuario).all()
    return render_template("mascotas/index.html", mascotas=mascotas)

# 📌 Crear mascota
@mascotas_bp.route("/crear", methods=["GET", "POST"])
@login_required
def crear():
    if request.method == "POST":
        nombre = request.form["nombre"]
        especie = request.form["especie"]
        raza = request.form["raza"]
        edad = request.form["edad"]

        nueva_mascota = Mascota(
            nombre=nombre,
            especie=especie,
            raza=raza,
            edad=int(edad),
            usuario_id=current_user.id_usuario
        )
        db.session.add(nueva_mascota)
        db.session.commit()

        flash("Mascota registrada con éxito", "success")
        return redirect(url_for("mascotas.listar"))

    return render_template("mascotas/crear.html")

# 📌 Editar mascota
@mascotas_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    mascota = Mascota.query.get_or_404(id)

    # Validación de propietario
    if mascota.usuario_id != current_user.id_usuario:
        flash("No tienes permiso para editar esta mascota", "danger")
        return redirect(url_for("mascotas.listar"))

    if request.method == "POST":
        mascota.nombre = request.form["nombre"]
        mascota.especie = request.form["especie"]
        mascota.raza = request.form["raza"]
        mascota.edad = int(request.form["edad"])
        db.session.commit()

        flash("Mascota actualizada con éxito", "success")
        return redirect(url_for("mascotas.listar"))

    return render_template("mascotas/editar.html", mascota=mascota)

# 📌 Eliminar mascota
@mascotas_bp.route("/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar(id):
    mascota = Mascota.query.get_or_404(id)

    # Validación de propietario
    if mascota.usuario_id != current_user.id_usuario:
        flash("No tienes permiso para eliminar esta mascota", "danger")
        return redirect(url_for("mascotas.listar"))

    db.session.delete(mascota)
    db.session.commit()
    flash("Mascota eliminada con éxito", "info")

    return redirect(url_for("mascotas.listar"))
