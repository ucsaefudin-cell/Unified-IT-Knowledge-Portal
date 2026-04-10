# Implementation Plan: Unified IT Knowledge Portal

## Overview

Implementasi Flask full-stack web application dengan dua pilar konten:
- **ERP Systems** (SAP Business One v10+)
- **Cloud Computing Infrastructure** (GCP — Multi-Cloud GCP & Azure)

Arsitektur telah dimigrasikan dari AWS ke **Google Cloud Platform (GCP)**:
- Web Server: GCP Compute Engine
- Database: GCP Cloud SQL (PostgreSQL 18.3)
- Static Storage: GCP Cloud Storage
- Automation: GCP Cloud Functions + Cloud Scheduler

Database menggunakan GCP Cloud SQL PostgreSQL untuk production, SQLite lokal untuk development (via `DATABASE_URL` env var). Semua komentar dan docstring ditulis dalam Bahasa Indonesia. Semua kode Python mengikuti standar **PEP 8**, prinsip **DRY**, dan penamaan variabel/fungsi yang deskriptif.

## Tasks

- [x] 0. Clean Code & Standards (Task baru — standar wajib untuk semua kode)
  - Semua kode Python WAJIB mengikuti PEP 8 (indentasi 4 spasi, max 79 karakter per baris)
  - Prinsip DRY: tidak ada duplikasi logika — ekstrak ke fungsi/service terpisah
  - Nama variabel dan fungsi harus deskriptif (hindari `x`, `tmp`, `data` tanpa konteks)
  - Semua fungsi WAJIB memiliki docstring dalam Bahasa Indonesia
  - Semua inline comment dalam Bahasa Indonesia
  - _Berlaku untuk semua task berikutnya_

- [x] 1. Buat struktur folder Flask dan konfigurasi dasar
  - Buat direktori `portal/` dengan struktur modular sesuai desain
  - Buat `portal/app/__init__.py` (app factory)
  - Buat `portal/app/config.py` (kelas Dev/Prod dari env vars, DATABASE_URL default ke SQLite)
  - Buat `portal/requirements.txt` dengan semua dependensi Python (versi pinned)
  - Buat `portal/.env.example` sebagai template variabel lingkungan
  - Buat `portal/run.py` sebagai entry point aplikasi
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 2. Implementasi model database (SQLAlchemy)
  - [x] 2.1 Buat `portal/app/models/user.py` — model User
    - Implementasi kolom: id, email, password_hash, is_verified, verification_token, token_expires_at, created_at
    - _Requirements: 9.5_
  - [x] 2.2 Buat `portal/app/models/article.py` — model KnowledgeArticle
    - Implementasi kolom: id, title, topic_category, pillar (SAP/AWS), summary, body_en, body_id, created_at
    - _Requirements: 9.3_
  - [x] 2.3 Buat `portal/app/models/best_practice.py` — model BestPractice
    - Implementasi kolom: id, title, pillar, teaser, body_en, body_id, case_study_ref, created_at
    - _Requirements: 9.4_
  - [x] 2.4 Buat `portal/app/models/__init__.py` — ekspor semua model
  - [ ]* 2.5 Tulis property test untuk model KnowledgeArticle
    - **Property 1: Pillar page renders all articles from database**
    - **Validates: Requirements 1.5, 2.2, 3.2**
  - [ ]* 2.6 Tulis unit test untuk validasi model User
    - Test kolom wajib, default value, dan constraint unik pada email
    - _Requirements: 9.5_

- [ ] 3. Checkpoint — Pastikan semua model dapat di-migrate ke SQLite
  - Jalankan `flask db init && flask db migrate && flask db upgrade`, pastikan tidak ada error.

- [-] 4. Implementasi Auth Service dan routes autentikasi
  - [x] 4.1 Buat `portal/app/services/auth_service.py`
    - Fungsi: register_new_user, authenticate_user, logout_current_user
    - Validasi panjang password (≥ 8 karakter), email unik
    - MVP: simpan user langsung tanpa email verification (bypass SES)
    - _Requirements: 5.1, 5.5, 5.6, 6.1, 6.3_
  - [ ] 4.2 Buat `portal/app/services/email_service.py`
    - Fungsi pengiriman email verifikasi via Gmail SMTP (implementasi penuh nanti)
    - _Requirements: 5.2_
  - [x] 4.3 Buat `portal/app/routes/auth.py`
    - Route: POST /auth/register, POST /auth/login, GET /auth/logout
    - Flash messages untuk feedback user
    - _Requirements: 5.1, 6.1, 6.3_
  - [x] 4.5 Security Hardening (Task baru)
    - CSRF Protection via Flask-WTF (CSRFProtect)
    - Security Headers via Flask-Talisman
    - Rate Limiting via Flask-Limiter pada route login
    - _Requirements: keamanan aplikasi production_
  - [ ]* 4.4 Tulis property test untuk registrasi user
    - **Property 3: Registration creates an unverified user**
    - **Validates: Requirements 5.1**
  - [ ]* 4.5 Tulis property test untuk validasi token verifikasi
    - **Property 4: Email verification token validity gate**
    - **Validates: Requirements 5.3, 5.7**
  - [ ]* 4.6 Tulis property test untuk gating login berdasarkan status verifikasi
    - **Property 5: Verification status gates login**
    - **Validates: Requirements 5.4, 6.1**
  - [ ]* 4.7 Tulis property test untuk penolakan registrasi duplikat
    - **Property 6: Duplicate registration is rejected**
    - **Validates: Requirements 5.5**
  - [ ]* 4.8 Tulis property test untuk validasi panjang password
    - **Property 7: Password length validation**
    - **Validates: Requirements 5.6**
  - [ ]* 4.9 Tulis property test untuk pesan error login yang tidak diskriminatif
    - **Property 8: Login error message is non-discriminating**
    - **Validates: Requirements 6.2**
  - [ ]* 4.10 Tulis property test untuk invalidasi session saat logout
    - **Property 9: Logout invalidates session**
    - **Validates: Requirements 6.3**
  - [ ]* 4.11 Tulis property test untuk expiry session
    - **Property 10: Session expiry enforced**
    - **Validates: Requirements 6.5**

- [ ] 5. Checkpoint — Pastikan semua test autentikasi lulus
  - Jalankan `pytest portal/tests/test_auth*.py`, pastikan tidak ada kegagalan.

- [-] 6. Implementasi Search Service dan API endpoint
  - [x] 6.1 Buat `portal/app/services/search_service.py`
    - Fungsi pencarian lintas KnowledgeArticle dan BestPractice
    - Filter akses: body_en/body_id disembunyikan untuk guest pada BestPractice
    - _Requirements: 7.2, 7.3, 7.4, 7.5_
  - [x] 6.2 Buat `portal/app/routes/api.py`
    - Route: GET /api/search?q=<query>&lang=<en|id>
    - Route: POST /api/set-language
    - _Requirements: 7.1, 7.2, 8.2, 8.4_
  - [ ]* 6.3 Tulis property test untuk kelengkapan dan format hasil pencarian
    - **Property 11: Search results are complete and correctly formatted**
    - **Validates: Requirements 7.2, 7.3, 7.4**

- [-] 7. Implementasi routes utama dan template Jinja2
  - [x] 7.1 Buat `portal/app/routes/main.py`
    - Route: GET / (dashboard), GET /sap, GET /gcp, GET /best-practices
    - _Requirements: 1.1, 1.2, 2.1, 3.1, 4.1_
  - [x] 7.2 Buat `portal/app/templates/base.html`
    - Layout dasar dengan navbar, footer, language toggle, dark/light mode toggle
    - Footer: "© 2026 Ucu Saefudin. All rights reserved."
    - _Requirements: 1.4, 8.1_
  - [x] 7.3 Buat `portal/app/templates/dashboard.html`
    - Bento Box/Grid layout — ERP (biru) dan Cloud Infrastructure (oranye)
    - Placeholder konten: Best Practices + Troubleshooting & Solutions
    - _Requirements: 1.1, 1.2, 1.3_
  - [x] 7.4 Buat `portal/app/templates/sap/index.html` dan `portal/app/templates/gcp/index.html`
    - Render kartu artikel dari database, tampilkan placeholder jika kosong
    - _Requirements: 2.2, 2.4, 3.2, 3.4_
  - [x] 7.5 Buat `portal/app/templates/best_practices/index.html`
    - Tampilkan teaser + blur + lock icon untuk guest; full content untuk user terautentikasi
    - _Requirements: 4.1, 4.2, 4.3, 4.6_
  - [x] 7.6 Buat `portal/app/templates/auth/register.html` dan `login.html`
    - Form registrasi dan login dengan validasi sisi klien dasar
    - _Requirements: 5.1, 6.1_
  - [ ]* 7.7 Tulis property test untuk rendering pillar page
    - **Property 1: Pillar page renders all articles from database**
    - **Validates: Requirements 1.5, 2.2, 3.2**
  - [ ]* 7.8 Tulis property test untuk kontrol akses Best Practice
    - **Property 2: Best Practice teaser visibility is access-controlled**
    - **Validates: Requirements 4.1, 4.2, 4.6**

- [x] 8. Implementasi static assets (CSS, JS)
  - [x] 8.1 Buat `portal/app/static/css/main.css` dengan Tailwind CSS (CDN atau build)
    - Styling grid dashboard, kartu artikel, blur effect, dark/light mode
    - _Requirements: 1.1, 1.3, 4.2_
  - [x] 8.2 Buat `portal/app/static/js/search.js`
    - Debounced AJAX live search (debounce 300ms, min 2 karakter)
    - _Requirements: 7.1, 7.2, 7.5, 7.6, 7.7_
  - [x] 8.3 Buat `portal/app/static/js/i18n.js`
    - Language toggle: kirim POST /api/set-language, reload konten tanpa full page reload
    - _Requirements: 8.2, 8.3, 8.4_
  - [x] 8.4 Buat `portal/app/static/js/theme.js`
    - Dark/Light mode toggle dengan localStorage persistence
    - Sun/Moon icon swap, transisi smooth antar tema

- [x] 9. Implementasi bilingual i18n (Flask-Babel)
  - Buat `portal/app/translations/en/messages.json` dan `portal/app/translations/id/messages.json`
  - Integrasikan Flask-Babel ke app factory untuk resolusi bahasa dari session
  - _Requirements: 8.1, 8.2, 8.3, 8.5, 8.6_
  - [ ]* 9.1 Tulis property test untuk rendering bahasa dengan fallback
    - **Property 12: Language rendering with fallback**
    - **Validates: Requirements 8.5, 8.6**

- [x] 10. Implementasi Database Seeder
  - Buat `portal/app/scripts/seed.py`
  - Seed KnowledgeArticle untuk SAP (Master Data, Purchasing A/P, Sales A/R, Inventory)
  - Seed KnowledgeArticle untuk AWS (EC2, S3, RDS, CloudFront)
  - Seed BestPractice untuk SAP (CSL02, CSL06, CSL08) dan AWS (RDS Backup, EC2 Troubleshooting, FinOps)
  - Implementasi logika skip-duplicate (idempotent)
  - _Requirements: 4.4, 4.5, 9.6, 9.7_
  - [ ]* 10.1 Tulis property test untuk idempotency seeder
    - **Property 13: Seeder is idempotent**
    - **Validates: Requirements 9.7**

- [x] 11. Implementasi GCP Cloud Scheduler Script (FinOps)
  - Buat `portal/app/scripts/scheduler.py`
  - GCP Cloud Functions handler yang membaca GCP_INSTANCE_ID dan ACTION dari env/event
  - Logika start/stop Compute Engine VM dengan pengecekan state saat ini (idempotent)
  - Logging dengan action, instance ID, dan timestamp
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_
  - [ ]* 11.1 Tulis property test untuk idempotency scheduler
    - **Property 14: Scheduler is idempotent**
    - **Validates: Requirements 11.5**
  - [ ]* 11.2 Tulis property test untuk field log scheduler
    - **Property 15: Scheduler logs contain required fields**
    - **Validates: Requirements 11.6**

- [ ] 12. Buat `portal/tests/conftest.py` dan integrasi test akhir
  - Setup pytest fixture dengan SQLite in-memory database
  - Tulis integration test: registrasi → verifikasi email → login → akses best practice
  - _Requirements: semua_

- [ ] 13. Checkpoint akhir — Pastikan semua test lulus
  - Jalankan `pytest portal/tests/ --tb=short`, pastikan tidak ada kegagalan.
  - Verifikasi `requirements.txt` lengkap dan semua komentar kode dalam Bahasa Indonesia.

## Notes

- Task bertanda `*` bersifat opsional dan dapat dilewati untuk MVP yang lebih cepat
- Setiap task mereferensikan requirement spesifik untuk keterlacakan
- Checkpoint memastikan validasi inkremental di setiap fase
- Property test memvalidasi properti kebenaran universal (menggunakan pytest-hypothesis)
- Unit test memvalidasi contoh spesifik dan edge case
- Database: SQLite lokal untuk development, **GCP Cloud SQL PostgreSQL** untuk production (via `DATABASE_URL`)
- Arsitektur: **GCP** (Compute Engine + Cloud SQL + Cloud Storage + Cloud Functions)
- Taksonomi pilar: **ERP Systems** (SAP B1) dan **Cloud Computing Infrastructure** (Multi-Cloud GCP & Azure)
- Standar kode: **PEP 8 + DRY + nama deskriptif + docstring Bahasa Indonesia**
