# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    # Configuración básica
    app.config['SECRET_KEY'] = 'clave_secreta_cambia_esto'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veterinaria.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)

    # Importar modelos para que SQLAlchemy los registre
    from app.models.users import Usuario
    from app.models.carrito import Carrito
    # Si tienes más modelos, impórtalos aquí:
    # from app.models.producto import Producto
    # from app.models.cita import Cita
    # etc.

    # Configuración de Flask-Login
    login_manager.login_view = 'auth.login'  # Ruta de login
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
