"""
Modul __init__.py -- Application Factory Unified IT Knowledge Portal.

Menggunakan pola Application Factory agar mudah dikonfigurasi
untuk berbagai lingkungan (dev, test, production).

Security extensions:
- Flask-WTF (CSRFProtect): Proteksi CSRF untuk semua form POST
- Flask-Talisman: Security headers (production only)
- Flask-Limiter: Rate limiting untuk mencegah brute-force

Prinsip Clean Code:
- create_app() adalah satu-satunya entry point pembuatan app
- Setiap kelompok inisialisasi dipisahkan ke fungsi privat tersendiri
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ============================================================
# INISIALISASI EKSTENSI -- Lazy initialization (tanpa app)
# Ekstensi baru aktif setelah init_app(app) dipanggil
# ============================================================

# ORM database
db = SQLAlchemy()

# Migrasi skema database
migrate = Migrate()

# Manajemen session login
login_manager = LoginManager()

# Pengiriman email
mail = Mail()

# Internasionalisasi bilingual EN/ID
babel = Babel()

# CSRF Protection -- mencegah Cross-Site Request Forgery
csrf = CSRFProtect()

# Rate Limiter -- mencegah brute-force attack
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)


def _get_active_locale() -> str:
    """
    Callback locale selector untuk Flask-Babel.

    Dipanggil otomatis oleh Flask-Babel pada setiap HTTP request
    untuk menentukan bahasa yang akan digunakan dalam request tersebut.

    Urutan prioritas:
    1. session['lang'] -- diset via /api/set-language
    2. BABEL_DEFAULT_LOCALE dari config ('en')

    Returns:
        Kode bahasa aktif: 'en' atau 'id'.
    """
    from flask import session, current_app

    language_from_session = session.get("lang")
    supported_languages = current_app.config.get("LANGUAGES", {"en": "English"})

    if language_from_session in supported_languages:
        return language_from_session

    return current_app.config.get("BABEL_DEFAULT_LOCALE", "en")


def create_app(config_override: dict = None) -> Flask:
    """
    Factory function untuk membuat instance aplikasi Flask.

    Urutan inisialisasi:
    1. Buat Flask app
    2. Muat konfigurasi
    3. Inisialisasi ekstensi
    4. Daftarkan blueprints
    5. Daftarkan error handlers

    Args:
        config_override: Dict konfigurasi untuk testing.

    Returns:
        Instance Flask yang sudah dikonfigurasi.
    """
    flask_app = Flask(__name__)

    _load_configuration(flask_app, config_override)
    _initialize_extensions(flask_app)
    _register_blueprints(flask_app)
    _register_error_handlers(flask_app)

    return flask_app


def _load_configuration(flask_app: Flask, config_override: dict = None) -> None:
    """
    Muat konfigurasi dari DevelopmentConfig, lalu terapkan override jika ada.

    Args:
        flask_app: Instance Flask yang akan dikonfigurasi.
        config_override: Dict konfigurasi tambahan (opsional, untuk testing).
    """
    from app.config import DevelopmentConfig
    flask_app.config.from_object(DevelopmentConfig)

    if config_override:
        flask_app.config.update(config_override)


def _initialize_extensions(flask_app: Flask) -> None:
    """
    Inisialisasi semua ekstensi Flask dengan mengikatnya ke app instance.

    Flask-Babel diinisialisasi dengan locale_selector=_get_active_locale
    agar bahasa ditentukan dari session user pada setiap request.

    Args:
        flask_app: Instance Flask yang sudah dikonfigurasi.
    """
    # Database dan ORM
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    # Autentikasi -- redirect ke login jika akses halaman terlindungi
    login_manager.init_app(flask_app)
    login_manager.login_view = "auth.handle_login_form"
    login_manager.login_message = "Silakan login untuk mengakses halaman ini."
    login_manager.login_message_category = "info"

    # Email
    mail.init_app(flask_app)

    # ============================================================
    # Flask-Babel -- i18n bilingual EN/ID
    #
    # locale_selector=_get_active_locale memberitahu Flask-Babel
    # untuk memanggil fungsi _get_active_locale() pada setiap request
    # guna menentukan bahasa yang aktif dari session user.
    # ============================================================
    babel.init_app(flask_app, locale_selector=_get_active_locale)

    # CSRF Protection -- aktif untuk semua form POST
    csrf.init_app(flask_app)

    # Rate Limiter
    limiter.init_app(flask_app)

    # Talisman hanya aktif di production (memerlukan HTTPS)
    is_production = not flask_app.config.get("DEBUG", True)
    if is_production:
        _initialize_talisman_for_production(flask_app)


def _initialize_talisman_for_production(flask_app: Flask) -> None:
    """
    Inisialisasi Flask-Talisman untuk environment production.

    Menambahkan security headers: HSTS, X-Content-Type-Options,
    X-Frame-Options, dan Content-Security-Policy.

    Args:
        flask_app: Instance Flask production.
    """
    try:
        from flask_talisman import Talisman

        content_security_policy = {
            "default-src": "'self'",
            "script-src": [
                "'self'",
                "https://cdn.tailwindcss.com",
                "https://fonts.googleapis.com",
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",
                "https://fonts.googleapis.com",
            ],
            "font-src": ["'self'", "https://fonts.gstatic.com"],
            "img-src": ["'self'", "data:", "https:"],
        }

        Talisman(
            flask_app,
            force_https=True,
            strict_transport_security=True,
            content_security_policy=content_security_policy,
        )
    except ImportError:
        flask_app.logger.warning(
            "Flask-Talisman tidak terinstall. Security headers tidak aktif."
        )


def _register_blueprints(flask_app: Flask) -> None:
    """
    Daftarkan semua blueprint ke aplikasi Flask.

    Blueprint dan prefix URL:
    - main_bp  : /          (dashboard, pillar pages)
    - auth_bp  : /auth      (register, login, logout)
    - api_bp   : /api       (search, set-language -- JSON)

    Rate limiting 10 req/menit diterapkan pada auth_bp
    untuk mencegah brute-force attack pada endpoint login.

    Args:
        flask_app: Instance Flask yang akan didaftarkan blueprint-nya.
    """
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp

    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(auth_bp, url_prefix="/auth")
    flask_app.register_blueprint(api_bp, url_prefix="/api")

    # Rate limiting khusus untuk auth -- mencegah brute-force login
    limiter.limit("10 per minute")(auth_bp)


def _register_error_handlers(flask_app: Flask) -> None:
    """
    Daftarkan handler untuk error HTTP umum.

    Menampilkan halaman error yang ramah pengguna, bukan
    halaman default Flask yang mengekspos informasi teknis.

    Args:
        flask_app: Instance Flask yang akan didaftarkan error handler-nya.
    """
    @flask_app.errorhandler(404)
    def handle_not_found_error(error):
        """Tampilkan halaman 404 saat resource tidak ditemukan."""
        from flask import render_template
        return render_template("errors/404.html"), 404

    @flask_app.errorhandler(500)
    def handle_internal_server_error(error):
        """Tampilkan halaman 500 saat terjadi kesalahan server internal."""
        from flask import render_template
        return render_template("errors/500.html"), 500

    @flask_app.errorhandler(429)
    def handle_rate_limit_exceeded(error):
        """
        Tampilkan pesan 429 saat rate limit terlampaui.
        Terjadi saat user mencoba login terlalu banyak dalam waktu singkat.
        """
        from flask import flash, redirect, url_for
        flash("Terlalu banyak percobaan. Silakan tunggu beberapa menit.", "error")
        return redirect(url_for("auth.handle_login_form"))
