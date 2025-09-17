from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.usuario import Usuario
from app.models.carrito import Carrito

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.contraseña, password):
            login_user(usuario)
            
            # ✅ CORRECCIÓN CRÍTICA: Usa el formato CORRECTO con el blueprint "main"
            if usuario.rol == "admin":
                return redirect(url_for("main.admin_panel"))
            elif usuario.rol == "veterinario":
                return redirect(url_for("main.veterinario_panel"))
            else:
                return redirect(url_for("main.dashboard"))
        
        flash("Correo o contraseña incorrectos", "error")
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        contraseña = request.form.get("contraseña")  # ✅ Nombre corregido
        confirm_password = request.form.get("confirm_password")  # Añadido para validar
        rol = request.form.get("rol") or "usuario"
        telefono = request.form.get("telefono") or ""
        direccion = request.form.get("direccion") or ""

        # Validar que la contraseña no sea None
        if not contraseña:
            flash("❌ La contraseña es obligatoria.", "error")
            return redirect(url_for("auth.register"))

        if contraseña != confirm_password:
            flash("❌ Las contraseñas no coinciden.", "error")
            return redirect(url_for("auth.register"))

        if Usuario.query.filter_by(email=email).first():
            flash("El correo ya está registrado", "error")
            return redirect(url_for("auth.register"))

        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            contraseña=generate_password_hash(contraseña),  # ✅ Ahora no es None
            rol=rol,
            telefono=telefono,
            direccion=direccion
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        carrito = Carrito(id_usuario=nuevo_usuario.id_usuario)
        db.session.add(carrito)
        db.session.commit()

        flash("Usuario registrado correctamente. Ahora inicia sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("main.home"))