"""
Modul search_service.py — Layanan pencarian Unified IT Knowledge Portal.

Tanggung jawab modul ini:
- Menjalankan query pencarian lintas tabel KnowledgeArticle dan BestPractice
- Menerapkan aturan akses: konten gated hanya menampilkan teaser untuk guest
- Memformat hasil pencarian ke struktur dict yang konsisten untuk API response

Prinsip Clean Code yang diterapkan:
- Single Responsibility: setiap fungsi hanya melakukan satu hal
- DRY: format hasil artikel dan best practice diekstrak ke fungsi terpisah
- Nama deskriptif: tidak ada variabel ambigu seperti 'data' atau 'res'
- Konstanta untuk nilai tetap (batas hasil, panjang minimum query)
"""

from flask_login import current_user

from app import db
from app.models.article import KnowledgeArticle
from app.models.best_practice import BestPractice


# ============================================================
# KONSTANTA — Nilai tetap untuk konfigurasi pencarian
# ============================================================

MINIMUM_QUERY_CHARACTER_LENGTH = 2   # Sesuai requirement 7.2
MAXIMUM_ARTICLE_RESULTS_PER_QUERY = 5  # Batas hasil per tipe konten
MAXIMUM_BEST_PRACTICE_RESULTS_PER_QUERY = 5
BODY_PREVIEW_CHARACTER_LIMIT = 120    # Panjang preview body untuk summary


# ============================================================
# FUNGSI PRIVAT — Pembangun query dan formatter hasil
# ============================================================

def _build_article_search_query(search_term: str):
    """
    Bangun query SQLAlchemy untuk mencari di tabel KnowledgeArticle.

    Mencari di tiga kolom sekaligus menggunakan OR:
    - title: judul artikel
    - body_en: konten Bahasa Inggris
    - summary: ringkasan artikel

    Menggunakan ilike() untuk pencarian case-insensitive di PostgreSQL.
    Fallback ke like() untuk SQLite (development).

    Args:
        search_term: Kata kunci pencarian dari user.

    Returns:
        Query SQLAlchemy yang belum dieksekusi (lazy evaluation).
    """
    # Bungkus search_term dengan wildcard % untuk pencarian substring
    wildcard_pattern = f"%{search_term}%"

    return KnowledgeArticle.query.filter(
        db.or_(
            KnowledgeArticle.title.ilike(wildcard_pattern),
            KnowledgeArticle.body_en.ilike(wildcard_pattern),
            KnowledgeArticle.summary.ilike(wildcard_pattern),
        )
    )


def _build_best_practice_search_query(search_term: str):
    """
    Bangun query SQLAlchemy untuk mencari di tabel BestPractice.

    Hanya mencari di title dan teaser — TIDAK di body_en/body_id
    karena konten body bersifat gated dan tidak boleh terekspos
    melalui pencarian untuk guest.

    Args:
        search_term: Kata kunci pencarian dari user.

    Returns:
        Query SQLAlchemy yang belum dieksekusi.
    """
    wildcard_pattern = f"%{search_term}%"

    return BestPractice.query.filter(
        db.or_(
            BestPractice.title.ilike(wildcard_pattern),
            BestPractice.teaser.ilike(wildcard_pattern),
        )
    )


def _format_article_as_search_result(article: KnowledgeArticle) -> dict:
    """
    Format satu record KnowledgeArticle menjadi dict untuk API response.

    KnowledgeArticle adalah konten publik — tidak ada pembatasan akses.
    Summary diambil dari kolom summary jika ada, fallback ke 120 karakter
    pertama dari body_en.

    Args:
        article: Instance model KnowledgeArticle dari database.

    Returns:
        Dict dengan struktur standar hasil pencarian.
    """
    # Gunakan summary jika tersedia, fallback ke preview body_en
    article_summary = (
        article.summary
        if article.summary
        else article.body_en[:BODY_PREVIEW_CHARACTER_LIMIT]
    )

    return {
        "id": article.id,
        "title": article.title,
        "pillar": article.pillar,
        "content_type": "knowledge_article",
        "summary": article_summary,
        "teaser": None,       # Artikel publik tidak memiliki teaser
        "is_gated": False,    # Konten publik — tidak dikunci
    }


def _format_best_practice_as_search_result(
    best_practice: BestPractice,
    requester_is_authenticated: bool,
) -> dict:
    """
    Format satu record BestPractice menjadi dict untuk API response.

    Menerapkan aturan akses gated content:
    - Guest (tidak login): hanya title dan teaser, is_gated=True
    - User terautentikasi: title, teaser, dan body tersedia, is_gated=False

    Menggunakan method to_search_result() dari model untuk konsistensi
    (DRY — logika akses tidak diduplikasi di sini).

    Args:
        best_practice: Instance model BestPractice dari database.
        requester_is_authenticated: Status autentikasi user yang melakukan pencarian.

    Returns:
        Dict dengan struktur standar hasil pencarian, dengan atau tanpa body
        tergantung status autentikasi.
    """
    # Delegasikan ke method model — logika akses sudah ada di sana
    return best_practice.to_search_result(
        is_authenticated=requester_is_authenticated
    )


# ============================================================
# FUNGSI PUBLIK — Dipanggil dari routes/api.py
# ============================================================

def execute_full_text_search(
    search_query: str,
    active_language_code: str = "en",
) -> dict:
    """
    Jalankan pencarian teks penuh lintas semua konten portal.

    Alur eksekusi:
    1. Validasi panjang query (minimal 2 karakter)
    2. Query KnowledgeArticle (konten publik)
    3. Query BestPractice (konten gated — hanya title & teaser)
    4. Gabungkan dan format semua hasil
    5. Kembalikan dict dengan results dan count

    Aturan akses yang diterapkan:
    - KnowledgeArticle: selalu tampil penuh untuk semua user
    - BestPractice: body hanya untuk user terautentikasi

    Args:
        search_query: Kata kunci pencarian dari input user.
        active_language_code: Kode bahasa aktif ('en' atau 'id'),
                              digunakan untuk memilih konten bilingual.

    Returns:
        Dict dengan key:
        - 'results' (list): Daftar dict hasil pencarian
        - 'count' (int): Jumlah total hasil
        - 'query' (str): Query yang digunakan (untuk debugging)
    """
    # Bersihkan query dari whitespace berlebih
    cleaned_query = search_query.strip()

    # Validasi panjang minimum — kembalikan kosong jika terlalu pendek
    if len(cleaned_query) < MINIMUM_QUERY_CHARACTER_LENGTH:
        return {"results": [], "count": 0, "query": cleaned_query}

    # Tentukan status autentikasi user yang melakukan pencarian
    # Diambil sekali di sini untuk efisiensi — tidak perlu cek berulang
    requester_is_authenticated = current_user.is_authenticated

    combined_search_results = []

    # --- Bagian 1: Cari di KnowledgeArticle (konten publik ERP & Cloud) ---
    matching_articles = (
        _build_article_search_query(cleaned_query)
        .limit(MAXIMUM_ARTICLE_RESULTS_PER_QUERY)
        .all()
    )

    for article in matching_articles:
        formatted_article = _format_article_as_search_result(article)
        combined_search_results.append(formatted_article)

    # --- Bagian 2: Cari di BestPractice (konten gated) ---
    matching_best_practices = (
        _build_best_practice_search_query(cleaned_query)
        .limit(MAXIMUM_BEST_PRACTICE_RESULTS_PER_QUERY)
        .all()
    )

    for best_practice in matching_best_practices:
        formatted_best_practice = _format_best_practice_as_search_result(
            best_practice=best_practice,
            requester_is_authenticated=requester_is_authenticated,
        )
        combined_search_results.append(formatted_best_practice)

    return {
        "results": combined_search_results,
        "count": len(combined_search_results),
        "query": cleaned_query,
    }
