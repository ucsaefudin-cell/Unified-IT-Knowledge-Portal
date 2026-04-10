"""
Modul konfigurasi aplikasi Flask.
Mendukung dua lingkungan: Development (SQLite lokal) dan Production (PostgreSQL RDS).
Semua nilai sensitif dibaca dari environment variable atau file .env.
"""

import os
from dotenv import load_dotenv

# Muat variabel dari file .env jika ada
load_dotenv()


class BaseConfig:
    """
    Konfigurasi dasar yang diwarisi oleh semua lingkungan.
    Nilai-nilai ini berlaku di semua mode kecuali di-override.
    """

    # Kunci rahasia untuk signing session dan token — WAJIB diganti di production
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-ganti-di-production")

    # Nonaktifkan notifikasi perubahan objek SQLAlchemy (hemat memori)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Konfigurasi Flask-Mail untuk pengiriman email verifikasi
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_USERNAME", "noreply@portal.local")

    # Konfigurasi AWS (untuk SES dan S3) — akan diganti ke GCP di production
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_REGION", "ap-southeast-1")
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

    # Konfigurasi GCP (Cloud Storage dan Compute Engine)
    GCP_BUCKET_NAME = os.environ.get("GCP_BUCKET_NAME")
    GCP_INSTANCE_ID = os.environ.get("GCP_INSTANCE_ID")
    GCP_ZONE = os.environ.get("GCP_ZONE", "asia-southeast2-a")
    GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")

    # Durasi sesi aktif: 60 menit (dalam detik)
    PERMANENT_SESSION_LIFETIME = 3600

    # ============================================================
    # Konfigurasi Flask-Babel untuk bilingual EN/ID
    # BABEL_DEFAULT_LOCALE: bahasa default saat tidak ada preferensi user
    # LANGUAGES: dict mapping kode bahasa ke nama tampilan
    # ============================================================
    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "Asia/Jakarta"
    LANGUAGES = {
        "en": "English",
        "id": "Bahasa Indonesia",
    }


class DevelopmentConfig(BaseConfig):
    """
    Konfigurasi untuk lingkungan development lokal.
    Menggunakan SQLite sebagai database default jika DATABASE_URL tidak diset.
    Aktifkan DEBUG mode untuk memudahkan troubleshooting.
    """

    DEBUG = True

    # Gunakan DATABASE_URL dari env jika tersedia, fallback ke SQLite lokal
    # Ini memudahkan migrasi ke PostgreSQL RDS di kemudian hari
    _db_url = os.environ.get("DATABASE_URL")
    if _db_url:
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        # Path absolut ke file SQLite di folder instance portal
        _base_dir = os.path.abspath(os.path.dirname(__file__))
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(
            _base_dir, "..", "instance", "portal_dev.db"
        )


class ProductionConfig(BaseConfig):
    """
    Konfigurasi untuk lingkungan production (AWS EC2 + RDS PostgreSQL).
    DATABASE_URL WAJIB diset sebagai environment variable di production.
    """

    DEBUG = False

    # Di production, DATABASE_URL harus diset ke PostgreSQL RDS
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError(
            "DATABASE_URL environment variable wajib diset di lingkungan production."
        )


class TestingConfig(BaseConfig):
    """
    Konfigurasi untuk testing otomatis.
    Menggunakan SQLite in-memory agar test cepat dan tidak meninggalkan data.
    """

    TESTING = True
    DEBUG = True

    # SQLite in-memory: database dibuat fresh setiap test run
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    # Nonaktifkan CSRF protection saat testing
    WTF_CSRF_ENABLED = False

    # Nonaktifkan pengiriman email nyata saat testing
    MAIL_SUPPRESS_SEND = True
