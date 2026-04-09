"""
Model User untuk sistem autentikasi portal.
Menyimpan data akun pengguna termasuk status verifikasi email dan token.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    """
    Model database untuk tabel 'users'.
    Mewarisi UserMixin dari Flask-Login untuk integrasi session management.
    """

    __tablename__ = "users"

    # Kolom primary key — auto-increment integer
    id = db.Column(db.Integer, primary_key=True)

    # Email unik sebagai identitas utama pengguna
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)

    # Hash password — tidak pernah menyimpan password plaintext
    password_hash = db.Column(db.String(255), nullable=False)

    # Status verifikasi email: False = belum diverifikasi, True = sudah
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

    # Token unik yang dikirim ke email untuk proses verifikasi
    verification_token = db.Column(db.String(255), nullable=True)

    # Waktu kadaluarsa token verifikasi (24 jam setelah dibuat)
    token_expires_at = db.Column(db.DateTime, nullable=True)

    # Waktu pembuatan akun — otomatis diisi saat record dibuat
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        """
        Hash password menggunakan Werkzeug dan simpan ke kolom password_hash.
        Tidak pernah menyimpan password dalam bentuk plaintext.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifikasi password yang diinput dengan hash yang tersimpan.
        Mengembalikan True jika cocok, False jika tidak.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Representasi string untuk debugging."""
        return f"<User id={self.id} email={self.email} verified={self.is_verified}>"


@login_manager.user_loader
def load_user(user_id):
    """
    Callback yang digunakan Flask-Login untuk memuat user dari session.
    Dipanggil otomatis setiap request untuk mengisi current_user.
    """
    return User.query.get(int(user_id))
