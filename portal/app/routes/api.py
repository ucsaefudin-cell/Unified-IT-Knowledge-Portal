"""
Blueprint routes API: live search dan language toggle.
Menyediakan endpoint JSON yang dikonsumsi oleh JavaScript frontend.
"""

from flask import Blueprint, request, jsonify, session
from flask_login import current_user
from app import db
from app.models.article import KnowledgeArticle
from app.models.best_practice import BestPractice

# Buat blueprint untuk routes API — semua response berformat JSON
api_bp = Blueprint("api", __name__)


@api_bp.route("/search")
def search():
    """
    Endpoint live search lintas pilar SAP dan GCP.
    Menerima parameter query 'q' dan 'lang' via GET request.
    Mengembalikan JSON berisi daftar hasil pencarian.
    Akses konten best practice dikontrol berdasarkan status autentikasi.
    """
    # Ambil parameter query dari URL, bersihkan whitespace
    query = request.args.get("q", "").strip()
    lang = request.args.get("lang", session.get("lang", "en"))

    # Validasi: query minimal 2 karakter sesuai requirement
    if len(query) < 2:
        return jsonify({"results": [], "count": 0})

    results = []

    # --- Cari di tabel KnowledgeArticle (konten publik) ---
    # Gunakan ILIKE untuk pencarian case-insensitive di PostgreSQL
    articles = KnowledgeArticle.query.filter(
        db.or_(
            KnowledgeArticle.title.ilike(f"%{query}%"),
            KnowledgeArticle.body_en.ilike(f"%{query}%"),
            KnowledgeArticle.summary.ilike(f"%{query}%"),
        )
    ).limit(5).all()

    for article in articles:
        results.append({
            "id": article.id,
            "title": article.title,
            "pillar": article.pillar,
            "content_type": "knowledge_article",
            "summary": article.summary or article.body_en[:100],
            "teaser": None,
            "is_gated": False,  # Artikel publik — tidak dikunci
        })

    # --- Cari di tabel BestPractice (konten gated) ---
    best_practices = BestPractice.query.filter(
        db.or_(
            BestPractice.title.ilike(f"%{query}%"),
            BestPractice.teaser.ilike(f"%{query}%"),
        )
    ).limit(5).all()

    for bp in best_practices:
        # Gunakan method to_search_result() dari model untuk kontrol akses
        # Body konten hanya disertakan jika user sudah terautentikasi
        results.append(bp.to_search_result(
            is_authenticated=current_user.is_authenticated
        ))

    return jsonify({"results": results, "count": len(results)})


@api_bp.route("/set-language", methods=["POST"])
def set_language():
    """
    Endpoint untuk menyimpan preferensi bahasa ke session Flask.
    Dipanggil oleh i18n.js saat user mengklik tombol language toggle.
    Memastikan bahasa yang dipilih sinkron antara client dan server.
    """
    data = request.get_json()
    lang = data.get("lang", "en") if data else "en"

    # Validasi: hanya terima nilai 'en' atau 'id'
    if lang not in ("en", "id"):
        return jsonify({"error": "Invalid language code"}), 400

    # Simpan ke session Flask — akan digunakan saat render template server-side
    session["lang"] = lang
    return jsonify({"status": "ok", "lang": lang})
