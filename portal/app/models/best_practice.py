"""
Model BestPractice untuk konten eksklusif yang memerlukan autentikasi.
Menyimpan skenario lanjutan dan studi kasus untuk pilar SAP dan AWS.
Guest hanya dapat melihat judul dan teaser; konten penuh hanya untuk user terverifikasi.
"""

from datetime import datetime
from app import db


class BestPractice(db.Model):
    """
    Model database untuk tabel 'best_practices'.
    Mendukung konten bilingual dan referensi studi kasus.
    """

    __tablename__ = "best_practices"

    # Kolom primary key — auto-increment integer
    id = db.Column(db.Integer, primary_key=True)

    # Judul best practice — wajib diisi dan ditampilkan ke semua pengunjung
    title = db.Column(db.String(255), nullable=False)

    # Pillar konten: SAP atau AWS
    pillar = db.Column(db.String(3), nullable=False, index=True)

    # Teaser singkat yang ditampilkan ke guest sebagai preview konten
    # Wajib diisi agar guest termotivasi untuk mendaftar
    teaser = db.Column(db.Text, nullable=False)

    # Konten lengkap dalam Bahasa Inggris — hanya untuk user terautentikasi
    body_en = db.Column(db.Text, nullable=False)

    # Konten lengkap dalam Bahasa Indonesia — opsional, fallback ke body_en jika null
    body_id = db.Column(db.Text, nullable=True)

    # Referensi kode studi kasus, contoh: "CSL02", "CSL06"
    case_study_ref = db.Column(db.String(100), nullable=True)

    # Waktu pembuatan record — otomatis diisi saat record dibuat
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def get_body(self, lang="en"):
        """
        Ambil konten lengkap sesuai bahasa yang dipilih.
        Jika terjemahan Bahasa Indonesia tidak tersedia, fallback ke Bahasa Inggris.
        Metode ini hanya boleh dipanggil untuk user yang sudah terautentikasi.
        """
        if lang == "id" and self.body_id:
            return self.body_id
        # Fallback ke Bahasa Inggris jika body_id kosong
        return self.body_en

    def to_search_result(self, is_authenticated=False):
        """
        Konversi record ke format dict untuk respons API search.
        Jika tidak terautentikasi, body_en dan body_id tidak disertakan.
        """
        result = {
            "id": self.id,
            "title": self.title,
            "pillar": self.pillar,
            "content_type": "best_practice",
            "teaser": self.teaser,
            "is_gated": not is_authenticated,
        }
        # Hanya sertakan konten penuh jika user sudah login
        if is_authenticated:
            result["body_en"] = self.body_en
            result["body_id"] = self.body_id
        return result

    def __repr__(self):
        """Representasi string untuk debugging."""
        return f"<BestPractice id={self.id} pillar={self.pillar} title={self.title!r}>"
