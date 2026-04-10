"""
Script verifikasi koneksi database — Unified IT Knowledge Portal.
Tujuan: memastikan aplikasi dapat membaca data dari GCP Cloud SQL
menggunakan config.py dan models.py yang sudah ada.

Cara menjalankan: lihat instruksi di bagian bawah file ini.
"""

import sys
import os

# Tambahkan path root portal/ ke sys.path
# agar Python bisa menemukan package 'app' saat dijalankan dari folder portal/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# Import app factory dan model yang sudah dibuat sebelumnya
from app import create_app, db
from app.models.article import KnowledgeArticle
from app.models.best_practice import BestPractice


def test_koneksi_database():
    """
    Fungsi utama untuk memverifikasi koneksi dan membaca data dari database.
    Menggunakan Flask app context agar SQLAlchemy bisa terhubung ke database
    sesuai konfigurasi di config.py (DATABASE_URL dari .env).
    """

    print("=" * 55)
    print("  TEST KONEKSI DATABASE — GCP Cloud SQL")
    print("=" * 55)

    # Buat instance aplikasi Flask menggunakan factory function
    # create_app() akan membaca DATABASE_URL dari file .env secara otomatis
    app = create_app()

    # Semua operasi database harus dijalankan di dalam app context
    with app.app_context():

        # --- Langkah 1: Cek versi database ---
        print("\n[1/3] Mengecek koneksi ke database...")
        try:
            from sqlalchemy import text
            result = db.session.execute(text("SELECT version()"))
            versi = result.fetchone()[0]
            # Tampilkan 70 karakter pertama dari string versi PostgreSQL
            print(f"  ✓ Terhubung! Versi: {versi[:70]}")
        except Exception as e:
            # Jika koneksi gagal, tampilkan pesan error dan hentikan script
            print(f"  ✗ Koneksi GAGAL: {e}")
            print("\n  Pastikan:")
            print("  - IP kantor sudah ditambahkan di GCP Cloud SQL Authorized Networks")
            print("  - DATABASE_URL di file .env sudah benar")
            sys.exit(1)

        # --- Langkah 2: Query KnowledgeArticle — ambil 3 record pertama ---
        print("\n[2/3] Membaca 3 artikel pertama dari tabel knowledge_articles...")
        try:
            # Query ke database: ambil 3 record pertama, urutkan berdasarkan id
            artikel = KnowledgeArticle.query.order_by(KnowledgeArticle.id).limit(3).all()

            if not artikel:
                # Jika tabel kosong, berarti seeder belum dijalankan
                print("  ⚠ Tabel kosong! Jalankan seed.py terlebih dahulu.")
            else:
                print(f"  ✓ Berhasil membaca {len(artikel)} artikel:\n")
                # Tampilkan detail setiap artikel yang ditemukan
                for i, a in enumerate(artikel, 1):
                    print(f"  [{i}] Judul  : {a.title}")
                    print(f"       Pillar : {a.pillar}")
                    print(f"       Topik  : {a.topic_category}")
                    print()

        except Exception as e:
            print(f"  ✗ Gagal membaca KnowledgeArticle: {e}")
            sys.exit(1)

        # --- Langkah 3: Hitung total semua record di kedua tabel ---
        print("[3/3] Menghitung total record di database...")
        try:
            total_artikel = KnowledgeArticle.query.count()
            total_bp = BestPractice.query.count()

            print(f"  ✓ Total KnowledgeArticle : {total_artikel} record")
            print(f"  ✓ Total BestPractice     : {total_bp} record")

            # Breakdown per pillar untuk verifikasi data seeder
            sap_artikel = KnowledgeArticle.query.filter_by(pillar="SAP").count()
            gcp_artikel = KnowledgeArticle.query.filter_by(pillar="GCP").count()
            sap_bp = BestPractice.query.filter_by(pillar="SAP").count()
            gcp_bp = BestPractice.query.filter_by(pillar="GCP").count()

            print(f"\n  Breakdown per Pillar:")
            print(f"  ┌─────────────────────┬────────────┬──────────────┐")
            print(f"  │ Pillar              │ Articles   │ Best Practice│")
            print(f"  ├─────────────────────┼────────────┼──────────────┤")
            print(f"  │ SAP Business One    │ {sap_artikel:<10} │ {sap_bp:<12} │")
            print(f"  │ GCP Cloud           │ {gcp_artikel:<10} │ {gcp_bp:<12} │")
            print(f"  └─────────────────────┴────────────┴──────────────┘")

        except Exception as e:
            print(f"  ✗ Gagal menghitung record: {e}")
            sys.exit(1)

    # Semua test berhasil
    print("\n" + "=" * 55)
    print("  ✓ SEMUA TEST BERHASIL — Database siap digunakan!")
    print("=" * 55)


# Entry point: jalankan hanya jika script dieksekusi langsung
if __name__ == "__main__":
    test_koneksi_database()
