from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user

def rol_requerido(rol):
    """
    Decorador para restringir acceso a usuarios con un rol específico.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesión para acceder a esta página.", "error")
                return redirect(url_for("auth.login"))
            if current_user.rol != rol:
                flash("No tienes permiso para acceder a esta sección.", "error")
                return redirect(url_for("main.dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
