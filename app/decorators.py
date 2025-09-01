# app/decorators.py
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


# ✅ Decorador personalizado para requerir login
def login_required(f):
    """
    Decorador para requerir que el usuario esté autenticado.
    Reemplaza al de Flask-Login si lo usas tú.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión para acceder a esta página.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


# ✅ Decorador para requerir un rol específico
def rol_requerido(rol):
    """
    Decorador para restringir acceso a usuarios con un rol específico.
    Ejemplo: @rol_requerido("admin")
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesión para acceder a esta página.", "error")
                return redirect(url_for("auth.login"))
            if getattr(current_user, "rol", None) != rol:
                flash("No tienes permiso para acceder a esta sección.", "error")
                return redirect(url_for("main.dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator