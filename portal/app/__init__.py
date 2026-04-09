"""
Modul inisialisasi aplikasi Flask — Unified IT Knowledge Portal.
Menggunakan pola Application Factory agar mudah dikonfigurasi
untuk berbagai lingkungan (development, testing, production).
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel

# Inisialisasi ekstensi Flask tanpa mengikat ke app tertentu
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
babel = Babel()


def create_app(config_override=None):
    """
    Factory function untuk membuat instance aplikasi Flask.
    Menerima parameter config_override (dict) untuk keperluan testing.
    """
    app = Flask(__name__)

    # Muat konfigurasi dari kelas Config
    from app.config import DevelopmentConfig
    app.config.from_object(DevelopmentConfig)

    # Terapkan override konfigurasi jika ada (misalnya untuk testing)
    if config_override:
        app.config.update(config_override)

    # Inisialisasi semua ekstensi dengan app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    babel.init_app(app)

    # Tentukan halaman redirect jika user belum login
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Silakan login untuk mengakses halaman ini."

    # Daftarkan semua blueprint (routes)
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Daftarkan error handler global
    _register_error_handlers(app)

    return app


def _register_error_handlers(app):
    """Mendaftarkan handler untuk error HTTP umum."""

    @app.errorhandler(404)
    def not_found(e):
        """Tampilkan halaman 404 saat resource tidak ditemukan."""
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        """Tampilkan halaman 500 saat terjadi kesalahan server."""
        from flask import render_template
        return render_template("errors/500.html"), 500
