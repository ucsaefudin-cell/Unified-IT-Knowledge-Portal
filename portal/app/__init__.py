"""
Modul __init__.py — Application Factory Unified IT Knowledge Portal.

Menggunakan pola Application Factory agar:
- Mudah dikonfigurasi untuk berbagai lingkungan (dev, test, production)
- Mendukung multiple app instances untuk testing
- Semua ekstensi diinisialisasi di satu tempat

Security extensions yang diinisialisasi di sini:
- Flask-WTF (CSRFProtect): Proteksi CSRF untuk semua form POST
- Flask-Talisman: Security headers (HSTS, CSP, X-Frame-Options, dll)
- Flask-Limiter: Rate limiting untuk mencegah brute-force attack

Prinsip Clean Code:
- Fungsi create_app() adalah satu-satunya entry point pembuatan app
- Setiap kelompok inisialisasi dipisahkan ke fungsi privat tersendiri
- Nama fungsi deskriptif: _initialize_extensions, _register_blueprints, dll
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
# INISIALISASI EKSTENSI — Tanpa mengikat ke app instance tertentu
# Pola ini disebut "lazy initialization" — ekstensi baru aktif
# setelah init_app(app) dipanggil di dalam create_app()
# ============================================================

# ORM database — mengelola semua interaksi dengan PostgreSQL/SQLite
db = SQLAlchemy()

# Migrasi skema database — mengelola perubahan struktur tabel
migrate = Migrate()

# Manajemen session login — melacak user yang sedang aktif
login_manager = LoginManager()

# Pengiriman email — untuk notifikasi dan verifikasi (implementasi nanti)
mail = Mail()

# Internasionalisasi — mendukung bilingual EN/ID
babel = Babel()

# CSRF Protection — mencegah Cross-Site Request Forgery pada semua form POST
# Setiap form harus menyertakan token CSRF tersembunyi yang divalidasi server
csrf = CSRFProtect()

# Rate Limiter — membatasi jumlah request per IP untuk mencegah brute-force
# get_remote_address: menggunakan IP address client sebagai identifier
limiter = Limiter(
    key_func=get_remote_address,
    # Default: 200 request per hari, 50 per jam untuk semua route
    default_limits=["200 per day", "50 per hour"],
    # Simpan counter di memory (development) — ganti ke Redis untuk production
    storage_uri="memory://",
)


def create_app(config_override: dict = None) -> Flask:
    """
    Factory function untuk membuat dan mengkonfigurasi instance aplikasi Flask.

    Urutan inisialisasi penting:
    1. Buat Flask app
    2. Muat konfigurasi
    3. Inisialisasi ekstensi (db, login, security)
    4. Daftarkan blueprints (routes)
    5. Daftarkan error handlers

    Args:
        config_override: Dict konfigurasi tambahan, biasanya untuk testing.
                         Contoh: {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}

    Returns:
        Instance Flask yang sudah dikonfigurasi dan siap dijalankan.
    """
    flask_app = Flask(__name__)

    _load_configuration(flask_app, config_override)
    _initialize_extensions(flask_app)
    _register_blueprints(flask_app)
    _register_error_handlers(flask_app)

    return flask_app


def _load_configuration(flask_app: Flask, config_override: dict = None) -> None:
    """
    Muat konfigurasi aplikasi dari kelas Config yang sesuai.

    Urutan prioritas konfigurasi:
    1. DevelopmentConfig (default)
    2. config_override (untuk testing — menimpa nilai dari DevelopmentConfig)

    Args:
        flask_app: Instance Flask yang akan dikonfigurasi.
        config_override: Dict konfigurasi tambahan (opsional).
    """
    from app.config import DevelopmentConfig
    flask_app.config.from_object(DevelopmentConfig)

    # Terapkan override jika ada — berguna untuk unit testing
    if config_override:
        flask_app.config.update(config_override)


def _initialize_extensions(flask_app: Flask) -> None:
    """
    Inisialisasi semua ekstensi Flask dengan mengikatnya ke app instance.

    Setiap ekstensi dipanggil dengan init_app(flask_app) agar bisa
    mengakses konfigurasi app dan app context saat dibutuhkan.

    Security extensions:
    - CSRFProtect: Aktif untuk semua route secara default
    - Talisman: Menambahkan security headers ke semua response
    - Limiter: Rate limiting — dikonfigurasi per-route di blueprints

    Args:
        flask_app: Instance Flask yang sudah dikonfigurasi.
    """
    # Ekstensi database dan ORM
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)

    # Ekstensi autentikasi
    login_manager.init_app(flask_app)
    login_manager.login_view = "auth.handle_login_form"
    login_manager.login_message = "Silakan login untuk mengakses halaman ini."
    login_manager.login_message_category = "info"

    # Ekstensi email dan i18n
    mail.init_app(flask_app)
    babel.init_app(flask_app)

    # --- Security Extensions ---

    # CSRF Protection: lindungi semua form POST dari serangan CSRF
    # Token CSRF otomatis diinjeksi ke semua form yang menggunakan {{ form.hidden_tag() }}
    # atau bisa diakses manual via {{ csrf_token() }} di template
    csrf.init_app(flask_app)

    # Rate Limiter: inisialisasi tanpa Talisman untuk development
    # (Talisman memerlukan HTTPS — diaktifkan hanya di production)
    limiter.init_app(flask_app)

    # Flask-Talisman: Security headers untuk production
    # Dinonaktifkan di development karena memerlukan HTTPS
    # Aktifkan di production dengan: Talisman(flask_app, force_https=True)
    is_production_environment = not flask_app.config.get("DEBUG", True)
    if is_production_environment:
        _initialize_talisman_for_production(flask_app)


def _initialize_talisman_for_production(flask_app: Flask) -> None:
    """
    Inisialisasi Flask-Talisman untuk environment production.

    Security headers yang ditambahkan:
    - Strict-Transport-Security (HSTS): Paksa HTTPS
    - X-Content-Type-Options: Cegah MIME sniffing
    - X-Frame-Options: Cegah clickjacking
    - Content-Security-Policy: Batasi sumber resource yang diizinkan

    Args:
        flask_app: Instance Flask production.
    """
    try:
        from flask_talisman import Talisman

        # Content Security Policy — sesuaikan dengan CDN yang digunakan
        content_security_policy = {
            "default-src": "'self'",
            "script-src": [
                "'self'",
                "https://cdn.tailwindcss.com",
                "https://fonts.googleapis.com",
            ],
            "style-src": [
                "'self'",
                "'unsafe-inline'",  # Diperlukan untuk Tailwind inline styles
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
        # Jika Flask-Talisman belum terinstall, log warning dan lanjutkan
        flask_app.logger.warning(
            "Flask-Talisman tidak terinstall. Security headers tidak aktif."
        )


def _register_blueprints(flask_app: Flask) -> None:
    """
    Daftarkan semua blueprint (modul route) ke aplikasi Flask.

    Setiap blueprint memiliki url_prefix untuk namespace yang jelas:
    - main_bp: / (root — dashboard, pillar pages)
    - auth_bp: /auth (register, login, logout)
    - api_bp: /api (search, set-language — mengembalikan JSON)

    Args:
        flask_app: Instance Flask yang akan didaftarkan blueprint-nya.
    """
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp

    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(auth_bp, url_prefix="/auth")
    flask_app.register_blueprint(api_bp, url_prefix="/api")

    # Terapkan rate limiting khusus pada route login untuk mencegah brute-force
    # Maksimal 10 percobaan login per menit per IP address
    limiter.limit("10 per minute")(auth_bp)


def _register_error_handlers(flask_app: Flask) -> None:
    """
    Daftarkan handler untuk error HTTP umum.

    Menampilkan halaman error yang ramah pengguna alih-alih
    halaman error default Flask yang mengekspos informasi teknis.

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
        Tampilkan halaman 429 saat rate limit terlampaui.
        Terjadi saat user mencoba login terlalu banyak dalam waktu singkat.
        """
        from flask import render_template, flash, redirect, url_for
        flash(
            "Terlalu banyak percobaan. Silakan tunggu beberapa menit.",
            "error"
        )
        return redirect(url_for("auth.handle_login_form"))
