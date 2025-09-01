import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Inicialización de extensiones
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configuración
    app.config["SECRET_KEY"] = "clave_secreta"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "flaskdb.sqlite")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # Importar modelos
    from app.models.usuario import Usuario
    from app.models.mascota import Mascota
    from app.models.carrito import Carrito
    from app.models.historia_clinica import HistoriaClinica
    from app.models.cita import Cita

    # Cargar usuario para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Registrar Blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.mascotas import mascotas_bp
    from app.routes.historia_clinica import historia_bp
    from app.routes.citas import citas_bp  # ✅ Nombre consistente

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(mascotas_bp, url_prefix="/mascotas")
    app.register_blueprint(historia_bp, url_prefix="/historia")
    app.register_blueprint(citas_bp, url_prefix="/citas")  # ✅ Usa prefijo

    # Crear carpeta instance si no existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app