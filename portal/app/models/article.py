"""
Model KnowledgeArticle untuk konten publik portal.
Menyimpan artikel pengetahuan untuk pilar SAP Business One dan AWS Cloud Infrastructure.
Artikel ini dapat diakses oleh semua pengunjung tanpa autentikasi.
"""

from datetime import datetime
from app import db


class KnowledgeArticle(db.Model):
    """
    Model database untuk tabel 'knowledge_articles'.
    Mendukung konten bilingual (English dan Bahasa Indonesia).
    """

    __tablename__ = "knowledge_articles"

    # Kolom primary key — auto-increment integer
    id = db.Column(db.Integer, primary_key=True)

    # Judul artikel — wajib diisi
    title = db.Column(db.String(255), nullable=False)

    # Kategori topik dalam pillar, contoh: "Master Data", "EC2", "S3"
    topic_category = db.Column(db.String(100), nullable=False, index=True)

    # Pillar konten: SAP atau AWS
    # Menggunakan String dengan constraint check untuk kompatibilitas SQLite dan PostgreSQL
    pillar = db.Column(db.String(3), nullable=False, index=True)

    # Ringkasan singkat artikel untuk tampilan kartu di dashboard
    summary = db.Column(db.Text, nullable=True)

    # Konten lengkap dalam Bahasa Inggris — wajib diisi
    body_en = db.Column(db.Text, nullable=False)

    # Konten lengkap dalam Bahasa Indonesia — opsional, fallback ke body_en jika null
    body_id = db.Column(db.Text, nullable=True)

    # Waktu pembuatan artikel — otomatis diisi saat record dibuat
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def get_body(self, lang="en"):
        """
        Ambil konten artikel sesuai bahasa yang dipilih.
        Jika terjemahan Bahasa Indonesia tidak tersedia, fallback ke Bahasa Inggris.
        """
        if lang == "id" and self.body_id:
            return self.body_id
        # Fallback ke Bahasa Inggris jika body_id kosong atau bahasa bukan 'id'
        return self.body_en

    def __repr__(self):
        """Representasi string untuk debugging."""
        return f"<KnowledgeArticle id={self.id} pillar={self.pillar} title={self.title!r}>"
