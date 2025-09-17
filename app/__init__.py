import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

# Inicialización de extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configuración unificada
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Importar modelos
    from app.models.usuario import Usuario
    from app.models.mascota import Mascota
    from app.models.carrito import Carrito, CarritoItem
    from app.models.historia_clinica import HistoriaClinica
    from app.models.cita import Cita
    from app.models.producto import Producto
    from app.models.receta import Receta, RecetaMedicamento
    from app.models.medicamento import Medicamento
    from app.models.factura import Factura

    # Cargar usuario para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.mascotas import mascotas_bp
    from app.routes.historia_clinica import historia_bp
    from app.routes.citas import citas_bp
    from app.routes.producto import producto_bp
    from app.routes.carrito import carrito_bp
    from app.routes.factura import factura_bp
    from app.routes.medicamento import medicamento_bp
    from app.routes.receta import receta_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(mascotas_bp, url_prefix="/mascotas")
    app.register_blueprint(historia_bp, url_prefix="/historia")
    app.register_blueprint(citas_bp, url_prefix="/citas")
    app.register_blueprint(producto_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(factura_bp)
    app.register_blueprint(medicamento_bp)
    app.register_blueprint(receta_bp)

    # Crear carpeta instance si no existe
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    return app