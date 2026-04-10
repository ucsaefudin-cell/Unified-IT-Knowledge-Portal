"""
Modul auth_service.py — Layanan autentikasi Unified IT Knowledge Portal.

Tanggung jawab modul ini:
- Registrasi user baru dengan validasi lengkap
- Autentikasi user saat login
- Logout user dari session aktif

Prinsip Clean Code yang diterapkan:
- Single Responsibility: setiap fungsi hanya melakukan SATU hal
- DRY: validasi email dan password diekstrak ke fungsi terpisah
- Nama deskriptif: tidak ada nama ambigu seperti 'data' atau 'result'
- Docstring Bahasa Indonesia untuk semua fungsi publik
"""

from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app.models.user import User


# ============================================================
# KONSTANTA — Nilai tetap yang digunakan di seluruh modul
# Menggunakan konstanta menghindari "magic numbers" di kode
# ============================================================

MINIMUM_PASSWORD_LENGTH = 8  # Panjang minimum password sesuai requirement 5.6
MAXIMUM_EMAIL_LENGTH = 255    # Batas panjang email sesuai kolom database


# ============================================================
# FUNGSI VALIDASI PRIVAT — Hanya digunakan di dalam modul ini
# Diawali underscore (_) sebagai konvensi "private" di Python
# ============================================================

def _validate_password_length(plain_password: str) -> bool:
    """
    Validasi apakah panjang password memenuhi syarat minimum.

    Args:
        plain_password: Password dalam bentuk teks biasa (belum di-hash).

    Returns:
        True jika panjang password >= MINIMUM_PASSWORD_LENGTH, False jika tidak.
    """
    return len(plain_password) >= MINIMUM_PASSWORD_LENGTH


def _is_email_already_registered(email_address: str) -> bool:
    """
    Cek apakah alamat email sudah terdaftar di database.

    Menggunakan query filter_by untuk efisiensi — hanya mengambil
    satu record, tidak memuat seluruh tabel.

    Args:
        email_address: Alamat email yang akan dicek.

    Returns:
        True jika email sudah ada di database, False jika belum.
    """
    existing_user = User.query.filter_by(email=email_address).first()
    return existing_user is not None


def _find_user_by_email(email_address: str):
    """
    Cari user berdasarkan alamat email.

    Args:
        email_address: Alamat email yang dicari.

    Returns:
        Objek User jika ditemukan, None jika tidak ada.
    """
    return User.query.filter_by(email=email_address).first()


# ============================================================
# FUNGSI PUBLIK — Dipanggil dari routes/auth.py
# ============================================================

def register_new_user(email_address: str, plain_password: str) -> dict:
    """
    Daftarkan user baru ke database setelah melewati semua validasi.

    Alur proses:
    1. Validasi panjang password (min 8 karakter)
    2. Cek apakah email sudah terdaftar
    3. Hash password menggunakan Werkzeug (bcrypt-based)
    4. Simpan user baru ke database
    5. Kembalikan status sukses atau pesan error

    MVP Note: Email verification di-bypass untuk saat ini.
    User langsung aktif setelah registrasi (is_verified=True).
    Implementasi email verification via Gmail SMTP akan ditambahkan nanti.

    Args:
        email_address: Alamat email calon user.
        plain_password: Password dalam bentuk teks biasa.

    Returns:
        dict dengan key:
        - 'success' (bool): True jika registrasi berhasil
        - 'message' (str): Pesan sukses atau deskripsi error
        - 'user' (User|None): Objek user yang baru dibuat, atau None jika gagal
    """
    # --- Validasi 1: Panjang password ---
    # Cek sebelum menyentuh database untuk efisiensi
    if not _validate_password_length(plain_password):
        return {
            "success": False,
            "message": (
                f"Password terlalu pendek. "
                f"Minimal {MINIMUM_PASSWORD_LENGTH} karakter."
            ),
            "user": None,
        }

    # --- Validasi 2: Email unik ---
    # Cek duplikasi email sebelum mencoba insert ke database
    if _is_email_already_registered(email_address):
        return {
            "success": False,
            "message": "Email ini sudah terdaftar. Silakan gunakan email lain atau login.",
            "user": None,
        }

    # --- Proses: Hash password dan simpan user baru ---
    # generate_password_hash menggunakan algoritma pbkdf2:sha256 secara default
    # TIDAK PERNAH simpan password dalam bentuk plaintext
    hashed_password = generate_password_hash(plain_password)

    new_user = User(
        email=email_address,
        password_hash=hashed_password,
        # MVP: langsung set is_verified=True, bypass email verification
        is_verified=True,
    )

    # Tambahkan ke session SQLAlchemy dan commit ke database
    db.session.add(new_user)
    db.session.commit()

    return {
        "success": True,
        "message": "Akun berhasil dibuat! Silakan login.",
        "user": new_user,
    }


def authenticate_user(
    email_address: str,
    plain_password: str,
    remember_session: bool = False,
) -> dict:
    """
    Autentikasi user berdasarkan email dan password.

    Prinsip keamanan yang diterapkan:
    - Pesan error TIDAK membedakan antara "email tidak ada" dan "password salah"
      (mencegah user enumeration attack — sesuai Requirement 6.2)
    - check_password_hash menggunakan perbandingan constant-time untuk
      mencegah timing attack

    Args:
        email_address: Alamat email yang diinput user.
        plain_password: Password yang diinput user (belum di-hash).
        remember_session: Jika True, session bertahan setelah browser ditutup.

    Returns:
        dict dengan key:
        - 'success' (bool): True jika login berhasil
        - 'message' (str): Pesan sukses atau deskripsi error
        - 'user' (User|None): Objek user yang berhasil login, atau None
    """
    # Pesan error generik — TIDAK mengungkapkan apakah email ada atau tidak
    # Ini mencegah attacker mengetahui email mana yang terdaftar
    GENERIC_AUTH_ERROR_MESSAGE = "Email atau password tidak valid."

    # --- Cari user berdasarkan email ---
    user_record = _find_user_by_email(email_address)

    # --- Validasi: user tidak ditemukan ---
    # Kembalikan pesan generik, bukan "email tidak terdaftar"
    if user_record is None:
        return {
            "success": False,
            "message": GENERIC_AUTH_ERROR_MESSAGE,
            "user": None,
        }

    # --- Validasi: password tidak cocok ---
    # check_password_hash membandingkan hash secara aman
    password_is_correct = check_password_hash(
        user_record.password_hash, plain_password
    )
    if not password_is_correct:
        return {
            "success": False,
            "message": GENERIC_AUTH_ERROR_MESSAGE,
            "user": None,
        }

    # --- Validasi: akun belum diverifikasi ---
    # (Untuk MVP ini tidak akan terjadi karena is_verified=True saat register)
    if not user_record.is_verified:
        return {
            "success": False,
            "message": "Akun belum diverifikasi. Periksa email Anda.",
            "user": None,
        }

    # --- Proses: Login berhasil — buat session Flask-Login ---
    # login_user() menyimpan user_id ke session cookie yang di-sign
    login_user(user_record, remember=remember_session)

    return {
        "success": True,
        "message": f"Selamat datang kembali!",
        "user": user_record,
    }


def logout_current_user() -> dict:
    """
    Logout user yang sedang aktif dan hapus session.

    Flask-Login menangani penghapusan session cookie secara otomatis
    melalui fungsi logout_user().

    Returns:
        dict dengan key:
        - 'success' (bool): Selalu True
        - 'message' (str): Pesan konfirmasi logout
    """
    # logout_user() dari Flask-Login menghapus user dari session aktif
    logout_user()

    return {
        "success": True,
        "message": "Anda telah berhasil keluar.",
    }
