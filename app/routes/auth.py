from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.users import Usuario
from app.models.carrito import Carrito

auth_bp = Blueprint("auth", __name__)

# -------------------------
# LOGIN
# -------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and check_password_hash(usuario.contraseña, password):
            login_user(usuario)
            if usuario.rol == "admin":
                return redirect(url_for("main.admin_panel"))
            elif usuario.rol == "veterinario":
                return redirect(url_for("main.veterinario_panel"))
            flash("Has iniciado sesión correctamente", "success")
            return redirect(url_for("main.dashboard"))
        else:
            flash("Correo o contraseña incorrectos", "error")

    return render_template("login.html")


# -------------------------
# REGISTRO
# -------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        email = request.form.get("email")
        password = request.form.get("password")
        rol = request.form.get("rol").lower()  # 🔹 Capturamos el rol del formulario
        
        # Verificar si ya existe el correo
        if Usuario.query.filter_by(email=email).first():
            flash("El correo ya está registrado", "error")
            return redirect(url_for("auth.register"))

        # Crear usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            email=email,
            contraseña=generate_password_hash(password),
            rol=rol  # 🔹 Asignamos el rol al nuevo usuario
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

        # Crear carrito vacío para el usuario
        carrito = Carrito(id_usuario=nuevo_usuario.id_usuario)
        db.session.add(carrito)
        db.session.commit()
        
        flash("Usuario registrado correctamente. Ahora inicia sesión.", "success")

    return render_template("register.html")


# -------------------------
# LOGOUT
# -------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.login"))
