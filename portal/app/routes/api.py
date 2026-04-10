"""
Modul routes/api.py — Blueprint API Unified IT Knowledge Portal.

Menyediakan endpoint JSON yang dikonsumsi oleh JavaScript frontend:
- GET  /api/search        : Live search lintas pilar ERP dan Cloud
- POST /api/set-language  : Simpan preferensi bahasa ke session Flask

Prinsip Clean Code yang diterapkan:
- Thin Controller: route hanya menangani HTTP request/response
- Semua logika bisnis didelegasikan ke service layer (search_service)
- Nama fungsi deskriptif: handle_live_search_request, handle_language_change
- Validasi input dilakukan di awal fungsi sebelum memanggil service
"""

from flask import Blueprint, request, jsonify, session
from flask_wtf.csrf import CSRFProtect

from app.services.search_service import execute_full_text_search


# Buat blueprint API — semua route diawali /api (via url_prefix di __init__.py)
api_bp = Blueprint("api", __name__)

# Kode bahasa yang didukung portal — digunakan untuk validasi input
SUPPORTED_LANGUAGE_CODES = frozenset({"en", "id"})

# Bahasa default jika tidak ada preferensi tersimpan di session
DEFAULT_LANGUAGE_CODE = "en"


@api_bp.route("/search", methods=["GET"])
def handle_live_search_request():
    """
    Endpoint live search — mencari konten di seluruh pilar portal.

    Menerima parameter via query string:
    - q    : Kata kunci pencarian (minimal 2 karakter)
    - lang : Kode bahasa untuk konten bilingual ('en' atau 'id')

    Mendelegasikan logika pencarian ke execute_full_text_search()
    di search_service.py — route ini hanya menangani HTTP.

    Aturan akses yang diterapkan oleh service:
    - KnowledgeArticle: tampil penuh untuk semua user
    - BestPractice: body hanya untuk user terautentikasi

    Returns:
        JSON response dengan key 'results' (list) dan 'count' (int).
        HTTP 200 untuk semua kasus termasuk hasil kosong.
    """
    # Ambil dan bersihkan parameter dari query string URL
    raw_search_query = request.args.get("q", "").strip()

    # Baca bahasa aktif: prioritas dari parameter URL, fallback ke session
    requested_language_code = request.args.get(
        "lang",
        session.get("lang", DEFAULT_LANGUAGE_CODE)
    )

    # Validasi kode bahasa — gunakan default jika tidak valid
    active_language_code = (
        requested_language_code
        if requested_language_code in SUPPORTED_LANGUAGE_CODES
        else DEFAULT_LANGUAGE_CODE
    )

    # Delegasikan ke service layer — route tidak mengandung logika pencarian
    search_results = execute_full_text_search(
        search_query=raw_search_query,
        active_language_code=active_language_code,
    )

    return jsonify(search_results)


@api_bp.route("/set-language", methods=["POST"])
def handle_language_change():
    """
    Endpoint untuk menyimpan preferensi bahasa ke session Flask.

    Dipanggil oleh i18n.js saat user mengklik tombol language toggle.
    Menyimpan pilihan bahasa ke server-side session agar sinkron dengan
    konten yang di-render server-side (Jinja2 templates).

    Menerima JSON body:
    - lang: Kode bahasa ('en' atau 'id')

    Returns:
        JSON response dengan status 'ok' dan kode bahasa yang disimpan.
        HTTP 400 jika kode bahasa tidak valid.
    """
    # Ambil JSON body dari request — kembalikan None jika bukan JSON valid
    request_body = request.get_json(silent=True)

    # Ekstrak kode bahasa dari body, fallback ke default jika tidak ada
    submitted_language_code = (
        request_body.get("lang", DEFAULT_LANGUAGE_CODE)
        if request_body
        else DEFAULT_LANGUAGE_CODE
    )

    # Validasi: tolak kode bahasa yang tidak didukung
    if submitted_language_code not in SUPPORTED_LANGUAGE_CODES:
        return jsonify({
            "error": f"Kode bahasa tidak valid. Gunakan: {list(SUPPORTED_LANGUAGE_CODES)}"
        }), 400

    # Simpan ke session Flask — digunakan saat render template server-side
    session["lang"] = submitted_language_code

    return jsonify({
        "status": "ok",
        "lang": submitted_language_code,
        "message": f"Bahasa berhasil diubah ke '{submitted_language_code}'.",
    })
