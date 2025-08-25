import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configuración básica
    app.config["SECRET_KEY"] = "clave_secreta"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "flaskdb.sqlite")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializar extensiones
    db.init_app(app)

    # 🔹 Configuración de LoginManager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # Importar modelos (para que SQLAlchemy los registre)
    from app.models.usuario import Usuario
    from app.models.mascota import Mascota
    from app.models.carrito import Carrito
    

    # Función para cargar usuario en Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.mascotas import mascotas_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(mascotas_bp, url_prefix="/mascotas")

    # Crear carpeta instance si no existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
