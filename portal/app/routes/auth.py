"""
Modul routes/auth.py — Blueprint autentikasi Unified IT Knowledge Portal.

Tanggung jawab modul ini:
- Menerima request HTTP untuk register, login, dan logout
- Mendelegasikan logika bisnis ke auth_service (prinsip thin controller)
- Menampilkan flash messages sebagai feedback ke user
- Melindungi route dengan rate limiting (via Flask-Limiter)

Prinsip Clean Code yang diterapkan:
- Thin Controller: route hanya menangani HTTP, logika di service layer
- Nama fungsi deskriptif: handle_registration_form, handle_login_form
- Tidak ada duplikasi logika validasi (DRY — ada di auth_service)
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import current_user

from app.services.auth_service import (
    register_new_user,
    authenticate_user,
    logout_current_user,
)

# Buat blueprint autentikasi — semua route diawali /auth (via url_prefix di __init__.py)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def handle_registration_form():
    """
    Tampilkan dan proses form registrasi akun baru.

    GET  → Render halaman form registrasi.
    POST → Ambil data form, delegasikan ke register_new_user(),
           tampilkan flash message, redirect sesuai hasil.

    Redirect ke dashboard jika user sudah login (mencegah double-register).
    """
    # Cegah user yang sudah login mengakses halaman registrasi
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        # Ambil data dari form HTML — strip() untuk hapus whitespace tidak sengaja
        submitted_email = request.form.get("email", "").strip().lower()
        submitted_password = request.form.get("password", "")

        # Validasi dasar: pastikan field tidak kosong sebelum ke service layer
        if not submitted_email or not submitted_password:
            flash("Email dan password wajib diisi.", "error")
            return render_template("auth/register.html")

        # Delegasikan logika registrasi ke service layer (thin controller)
        registration_result = register_new_user(
            email_address=submitted_email,
            plain_password=submitted_password,
        )

        if registration_result["success"]:
            # Registrasi berhasil — tampilkan pesan sukses dan arahkan ke login
            flash(registration_result["message"], "success")
            return redirect(url_for("auth.handle_login_form"))
        else:
            # Registrasi gagal — tampilkan pesan error dan kembali ke form
            flash(registration_result["message"], "error")
            return render_template("auth/register.html")

    # GET request — tampilkan form kosong
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def handle_login_form():
    """
    Tampilkan dan proses form login.

    GET  → Render halaman form login.
    POST → Ambil kredensial, delegasikan ke authenticate_user(),
           redirect ke dashboard jika sukses atau kembali ke form jika gagal.

    Rate limiting diterapkan di __init__.py via Flask-Limiter
    untuk mencegah brute-force attack pada endpoint ini.
    """
    # Cegah user yang sudah login mengakses halaman login
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        # Ambil kredensial dari form — email di-lowercase untuk konsistensi
        submitted_email = request.form.get("email", "").strip().lower()
        submitted_password = request.form.get("password", "")
        # Checkbox "Remember Me" — True jika dicentang, False jika tidak
        should_remember_session = bool(request.form.get("remember_me"))

        # Validasi dasar: field tidak boleh kosong
        if not submitted_email or not submitted_password:
            flash("Email dan password wajib diisi.", "error")
            return render_template("auth/login.html")

        # Delegasikan autentikasi ke service layer
        authentication_result = authenticate_user(
            email_address=submitted_email,
            plain_password=submitted_password,
            remember_session=should_remember_session,
        )

        if authentication_result["success"]:
            # Login berhasil — redirect ke halaman yang diminta sebelumnya,
            # atau ke dashboard jika tidak ada halaman sebelumnya
            flash(authentication_result["message"], "success")
            next_page_url = request.args.get("next")
            return redirect(next_page_url or url_for("main.dashboard"))
        else:
            # Login gagal — tampilkan pesan error generik (tidak membocorkan detail)
            flash(authentication_result["message"], "error")
            return render_template("auth/login.html")

    # GET request — tampilkan form kosong
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def handle_logout_request():
    """
    Proses logout: hapus session aktif dan redirect ke homepage.

    Tidak memerlukan POST karena tidak ada data sensitif yang dikirim.
    Flask-Login menangani penghapusan session cookie secara otomatis.
    """
    logout_result = logout_current_user()
    flash(logout_result["message"], "success")
    return redirect(url_for("main.dashboard"))


@auth_bp.route("/verify/<string:verification_token>")
def verify_email_token(verification_token: str):
    """
    Verifikasi email via token unik yang dikirim ke email user.

    Placeholder untuk implementasi penuh di fase berikutnya.
    Saat ini menampilkan pesan informasi dan redirect ke dashboard.

    Args:
        verification_token: Token unik dari URL verifikasi email.
    """
    # TODO: Implementasi penuh — cek token di database, set is_verified=True
    flash("Fitur verifikasi email akan segera tersedia.", "info")
    return redirect(url_for("main.dashboard"))
