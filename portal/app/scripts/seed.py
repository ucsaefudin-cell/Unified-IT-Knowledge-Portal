"""
Script seeder untuk mengisi database dengan data awal (placeholder).
Mendukung dua pilar konten: SAP Business One dan GCP Cloud Infrastructure.

Cara menjalankan dari folder portal/:
    python -m app.scripts.seed

Script ini bersifat IDEMPOTENT — aman dijalankan berkali-kali.
Jika data sudah ada (berdasarkan judul), record tidak akan diduplikasi.
"""

import sys
import os

# Tambahkan path root portal ke sys.path agar import app bisa berjalan
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app import create_app, db
from app.models.article import KnowledgeArticle
from app.models.best_practice import BestPractice


# ==============================================================
# DATA PILAR SAP — KnowledgeArticle (Konten Publik)
# Berisi artikel pengetahuan dasar SAP Business One v10
# Dapat diakses oleh semua pengunjung tanpa login
# ==============================================================
SAP_ARTICLES = [
    {
        # --- Kategori: Master Data ---
        "title": "SAP B1: Master Data Management",
        "topic_category": "Master Data",
        "pillar": "SAP",
        "summary": "Fondasi data utama dalam SAP Business One: Business Partner, Item Master, dan Chart of Accounts.",
        "body_en": (
            "Master Data in SAP Business One v10 is the foundation of all transactions. "
            "It includes three core entities:\n\n"
            "1. **Business Partner (BP):** Covers Customers, Vendors, and Leads. "
            "Each BP has a unique code, payment terms, currency, and contact details.\n\n"
            "2. **Item Master Data:** Defines products and services with attributes like "
            "Item Group, Unit of Measure, valuation method (Moving Average / Standard Cost), "
            "and warehouse bin locations.\n\n"
            "3. **Chart of Accounts (CoA):** The backbone of financial reporting. "
            "SAP B1 uses a 4-level account hierarchy: Drawer → Title → Active → Detail.\n\n"
            "Best Practice: Always define BP and Item Master before creating any transaction document."
        ),
        "body_id": (
            "Master Data di SAP Business One v10 adalah fondasi dari semua transaksi. "
            "Terdiri dari tiga entitas utama:\n\n"
            "1. **Business Partner (BP):** Mencakup Pelanggan, Vendor, dan Prospek. "
            "Setiap BP memiliki kode unik, syarat pembayaran, mata uang, dan detail kontak.\n\n"
            "2. **Item Master Data:** Mendefinisikan produk dan layanan dengan atribut seperti "
            "Grup Item, Satuan Ukur, metode penilaian (Moving Average / Standard Cost), "
            "dan lokasi bin gudang.\n\n"
            "3. **Chart of Accounts (CoA):** Tulang punggung pelaporan keuangan. "
            "SAP B1 menggunakan hierarki akun 4 level: Laci → Judul → Aktif → Detail.\n\n"
            "Best Practice: Selalu definisikan BP dan Item Master sebelum membuat dokumen transaksi apapun."
        ),
    },
    {
        # --- Kategori: Purchasing (A/P) ---
        "title": "SAP B1: Purchasing & Accounts Payable (A/P)",
        "topic_category": "Purchasing (A/P)",
        "pillar": "SAP",
        "summary": "Alur proses pembelian di SAP B1: dari Purchase Order hingga pembayaran vendor.",
        "body_en": (
            "The Purchasing (A/P) module in SAP Business One v10 manages the full procure-to-pay cycle:\n\n"
            "**Document Flow:**\n"
            "Purchase Request → Purchase Quotation → Purchase Order (PO) → "
            "Goods Receipt PO (GRPO) → A/P Invoice → Outgoing Payment\n\n"
            "**Key Points:**\n"
            "- A PO commits inventory and budget but does not post a journal entry.\n"
            "- GRPO posts the inventory receipt and creates a Goods Received Not Invoiced (GRNI) liability.\n"
            "- A/P Invoice matches the GRPO and creates the vendor payable.\n"
            "- Three-way matching: PO ↔ GRPO ↔ A/P Invoice ensures accuracy.\n\n"
            "**CSL02 Reference:** Procurement best practices include mandatory PO approval workflow "
            "and tolerance checks between PO price and invoice price."
        ),
        "body_id": (
            "Modul Purchasing (A/P) di SAP Business One v10 mengelola siklus procure-to-pay secara penuh:\n\n"
            "**Alur Dokumen:**\n"
            "Permintaan Pembelian → Penawaran Pembelian → Purchase Order (PO) → "
            "Goods Receipt PO (GRPO) → Faktur A/P → Pembayaran Keluar\n\n"
            "**Poin Utama:**\n"
            "- PO mengkomit inventaris dan anggaran tetapi tidak memposting jurnal.\n"
            "- GRPO memposting penerimaan inventaris dan membuat kewajiban GRNI.\n"
            "- Faktur A/P mencocokkan GRPO dan membuat hutang vendor.\n"
            "- Three-way matching: PO ↔ GRPO ↔ Faktur A/P memastikan akurasi.\n\n"
            "**Referensi CSL02:** Best practice pengadaan mencakup alur persetujuan PO wajib "
            "dan pemeriksaan toleransi antara harga PO dan harga faktur."
        ),
    },
    {
        # --- Kategori: Sales (A/R) ---
        "title": "SAP B1: Sales & Accounts Receivable (A/R)",
        "topic_category": "Sales (A/R)",
        "pillar": "SAP",
        "summary": "Alur proses penjualan di SAP B1: dari Sales Quotation hingga penerimaan pembayaran.",
        "body_en": (
            "The Sales (A/R) module in SAP Business One v10 covers the order-to-cash cycle:\n\n"
            "**Document Flow:**\n"
            "Sales Opportunity → Sales Quotation → Sales Order (SO) → "
            "Delivery → A/R Invoice → Incoming Payment\n\n"
            "**Key Points:**\n"
            "- Sales Order reserves stock and triggers MRP if configured.\n"
            "- Delivery reduces inventory and posts COGS (Cost of Goods Sold).\n"
            "- A/R Invoice creates the customer receivable and posts revenue.\n"
            "- Credit limit checks can be enforced at SO or Delivery stage.\n\n"
            "**CSL06 Reference (CRM):** Sales Opportunity tracking with win/loss analysis "
            "and activity management integrates directly with the A/R flow."
        ),
        "body_id": (
            "Modul Sales (A/R) di SAP Business One v10 mencakup siklus order-to-cash:\n\n"
            "**Alur Dokumen:**\n"
            "Peluang Penjualan → Penawaran Penjualan → Sales Order (SO) → "
            "Pengiriman → Faktur A/R → Pembayaran Masuk\n\n"
            "**Poin Utama:**\n"
            "- Sales Order mereservasi stok dan memicu MRP jika dikonfigurasi.\n"
            "- Pengiriman mengurangi inventaris dan memposting HPP (Harga Pokok Penjualan).\n"
            "- Faktur A/R membuat piutang pelanggan dan memposting pendapatan.\n"
            "- Pemeriksaan batas kredit dapat diterapkan di tahap SO atau Pengiriman.\n\n"
            "**Referensi CSL06 (CRM):** Pelacakan Peluang Penjualan dengan analisis menang/kalah "
            "dan manajemen aktivitas terintegrasi langsung dengan alur A/R."
        ),
    },
    {
        # --- Kategori: Inventory ---
        "title": "SAP B1: Inventory Management",
        "topic_category": "Inventory",
        "pillar": "SAP",
        "summary": "Manajemen gudang dan stok di SAP B1: bin location, transfer, dan stock counting.",
        "body_en": (
            "Inventory Management in SAP Business One v10 provides real-time stock visibility:\n\n"
            "**Core Features:**\n"
            "- **Multi-Warehouse:** Manage multiple physical locations with separate stock levels.\n"
            "- **Bin Location:** Sub-divide warehouses into rows, shelves, and bins for precise tracking.\n"
            "- **Inventory Transfer:** Move stock between warehouses with full audit trail.\n"
            "- **Stock Counting:** Periodic physical count with variance posting.\n"
            "- **Valuation Methods:** Moving Average Price (MAP) or Standard Cost per item.\n\n"
            "**CSL05 Reference (Warehouse):** Advanced warehouse scenarios include "
            "pick-and-pack workflows, batch/serial number tracking, and FIFO bin allocation."
        ),
        "body_id": (
            "Manajemen Inventaris di SAP Business One v10 memberikan visibilitas stok secara real-time:\n\n"
            "**Fitur Utama:**\n"
            "- **Multi-Gudang:** Kelola beberapa lokasi fisik dengan level stok terpisah.\n"
            "- **Bin Location:** Bagi gudang menjadi baris, rak, dan bin untuk pelacakan presisi.\n"
            "- **Transfer Inventaris:** Pindahkan stok antar gudang dengan jejak audit lengkap.\n"
            "- **Stock Counting:** Penghitungan fisik berkala dengan posting selisih.\n"
            "- **Metode Penilaian:** Moving Average Price (MAP) atau Standard Cost per item.\n\n"
            "**Referensi CSL05 (Gudang):** Skenario gudang lanjutan mencakup "
            "alur pick-and-pack, pelacakan nomor batch/serial, dan alokasi bin FIFO."
        ),
    },
]


# ==============================================================
# DATA PILAR GCP — KnowledgeArticle (Konten Publik)
# Berisi artikel pengetahuan dasar Google Cloud Platform
# Menggantikan pilar AWS sesuai perubahan arsitektur ke GCP
# ==============================================================
GCP_ARTICLES = [
    {
        # --- Kategori: Compute Engine (pengganti EC2) ---
        "title": "GCP: Compute Engine Fundamentals",
        "topic_category": "Compute Engine",
        "pillar": "GCP",
        "summary": "Dasar-dasar VM di Google Cloud: instance types, machine families, dan persistent disk.",
        "body_en": (
            "Google Cloud Compute Engine provides scalable virtual machines (VMs) on Google's infrastructure.\n\n"
            "**Machine Families:**\n"
            "- **General Purpose (E2, N2, N2D):** Balanced CPU/memory for web servers and databases.\n"
            "- **Compute Optimized (C2, C2D):** High-performance for compute-intensive workloads.\n"
            "- **Memory Optimized (M1, M2, M3):** Large in-memory workloads like SAP HANA.\n\n"
            "**Key Concepts:**\n"
            "- **Persistent Disk:** Network-attached block storage (Standard HDD, Balanced SSD, Extreme SSD).\n"
            "- **Preemptible / Spot VMs:** Up to 91% cheaper, suitable for fault-tolerant batch jobs.\n"
            "- **Instance Groups:** Managed (MIG) for auto-scaling; Unmanaged for heterogeneous VMs.\n\n"
            "Best Practice: Use Committed Use Discounts (CUDs) for predictable workloads to save up to 57%."
        ),
        "body_id": (
            "Google Cloud Compute Engine menyediakan mesin virtual (VM) yang skalabel di infrastruktur Google.\n\n"
            "**Keluarga Mesin:**\n"
            "- **General Purpose (E2, N2, N2D):** CPU/memori seimbang untuk web server dan database.\n"
            "- **Compute Optimized (C2, C2D):** Performa tinggi untuk beban kerja intensif komputasi.\n"
            "- **Memory Optimized (M1, M2, M3):** Beban kerja in-memory besar seperti SAP HANA.\n\n"
            "**Konsep Utama:**\n"
            "- **Persistent Disk:** Block storage berbasis jaringan (HDD Standar, SSD Seimbang, SSD Ekstrem).\n"
            "- **Preemptible / Spot VM:** Hingga 91% lebih murah, cocok untuk batch job toleran kesalahan.\n"
            "- **Instance Groups:** Managed (MIG) untuk auto-scaling; Unmanaged untuk VM heterogen.\n\n"
            "Best Practice: Gunakan Committed Use Discounts (CUD) untuk beban kerja yang dapat diprediksi, hemat hingga 57%."
        ),
    },
    {
        # --- Kategori: Cloud Storage (pengganti S3) ---
        "title": "GCP: Cloud Storage Fundamentals",
        "topic_category": "Cloud Storage",
        "pillar": "GCP",
        "summary": "Object storage GCP: storage classes, bucket policies, dan lifecycle management.",
        "body_en": (
            "Google Cloud Storage (GCS) is a globally unified object storage service.\n\n"
            "**Storage Classes:**\n"
            "- **Standard:** Frequently accessed data (hot data). No minimum storage duration.\n"
            "- **Nearline:** Access less than once per month. 30-day minimum.\n"
            "- **Coldline:** Access less than once per quarter. 90-day minimum.\n"
            "- **Archive:** Long-term archival. 365-day minimum, lowest cost.\n\n"
            "**Key Features:**\n"
            "- **Uniform Bucket-Level Access:** Disables ACLs, enforces IAM-only access control.\n"
            "- **Object Versioning:** Retains previous versions of objects for recovery.\n"
            "- **Lifecycle Rules:** Automatically transition or delete objects based on age or condition.\n"
            "- **Signed URLs:** Grant time-limited access to private objects without requiring Google accounts.\n\n"
            "Best Practice: Enable Uniform Bucket-Level Access and use lifecycle rules to auto-transition to cheaper storage classes."
        ),
        "body_id": (
            "Google Cloud Storage (GCS) adalah layanan object storage terpadu secara global.\n\n"
            "**Kelas Penyimpanan:**\n"
            "- **Standard:** Data yang sering diakses (hot data). Tidak ada durasi penyimpanan minimum.\n"
            "- **Nearline:** Akses kurang dari sekali per bulan. Minimum 30 hari.\n"
            "- **Coldline:** Akses kurang dari sekali per kuartal. Minimum 90 hari.\n"
            "- **Archive:** Pengarsipan jangka panjang. Minimum 365 hari, biaya terendah.\n\n"
            "**Fitur Utama:**\n"
            "- **Uniform Bucket-Level Access:** Menonaktifkan ACL, menerapkan kontrol akses IAM saja.\n"
            "- **Object Versioning:** Menyimpan versi sebelumnya dari objek untuk pemulihan.\n"
            "- **Lifecycle Rules:** Otomatis transisi atau hapus objek berdasarkan usia atau kondisi.\n"
            "- **Signed URLs:** Berikan akses terbatas waktu ke objek privat tanpa memerlukan akun Google.\n\n"
            "Best Practice: Aktifkan Uniform Bucket-Level Access dan gunakan lifecycle rules untuk transisi otomatis ke kelas penyimpanan lebih murah."
        ),
    },
    {
        # --- Kategori: Cloud SQL (pengganti RDS) ---
        "title": "GCP: Cloud SQL Fundamentals",
        "topic_category": "Cloud SQL",
        "pillar": "GCP",
        "summary": "Database terkelola di GCP: PostgreSQL, MySQL, SQL Server — HA, backup, dan koneksi.",
        "body_en": (
            "Google Cloud SQL is a fully managed relational database service supporting PostgreSQL, MySQL, and SQL Server.\n\n"
            "**Key Features:**\n"
            "- **High Availability (HA):** Synchronous replication to a standby instance in another zone. "
            "Automatic failover in ~60 seconds.\n"
            "- **Read Replicas:** Offload read traffic; supports cross-region replicas for disaster recovery.\n"
            "- **Automated Backups:** Daily backups with point-in-time recovery (PITR) up to 7 days.\n"
            "- **Cloud SQL Auth Proxy:** Secure, IAM-authenticated connection without exposing public IPs.\n\n"
            "**Connection Options:**\n"
            "- Public IP with authorized networks (SSL required)\n"
            "- Private IP via VPC peering (recommended for production)\n"
            "- Cloud SQL Auth Proxy (recommended for applications)\n\n"
            "Best Practice: Use Private IP + Cloud SQL Auth Proxy for production. Never expose Cloud SQL directly to the public internet."
        ),
        "body_id": (
            "Google Cloud SQL adalah layanan database relasional terkelola penuh yang mendukung PostgreSQL, MySQL, dan SQL Server.\n\n"
            "**Fitur Utama:**\n"
            "- **High Availability (HA):** Replikasi sinkron ke instance standby di zona lain. "
            "Failover otomatis dalam ~60 detik.\n"
            "- **Read Replicas:** Membagi beban baca; mendukung replika lintas region untuk disaster recovery.\n"
            "- **Automated Backups:** Backup harian dengan point-in-time recovery (PITR) hingga 7 hari.\n"
            "- **Cloud SQL Auth Proxy:** Koneksi aman berbasis IAM tanpa mengekspos IP publik.\n\n"
            "**Opsi Koneksi:**\n"
            "- IP Publik dengan jaringan yang diotorisasi (SSL wajib)\n"
            "- IP Privat via VPC peering (direkomendasikan untuk production)\n"
            "- Cloud SQL Auth Proxy (direkomendasikan untuk aplikasi)\n\n"
            "Best Practice: Gunakan IP Privat + Cloud SQL Auth Proxy untuk production. Jangan pernah mengekspos Cloud SQL langsung ke internet publik."
        ),
    },
    {
        # --- Kategori: Cloud CDN (pengganti CloudFront) ---
        "title": "GCP: Cloud CDN Fundamentals",
        "topic_category": "Cloud CDN",
        "pillar": "GCP",
        "summary": "Content Delivery Network GCP: cache modes, origin, dan integrasi dengan Cloud Load Balancing.",
        "body_en": (
            "Google Cloud CDN accelerates content delivery by caching responses at Google's global edge network.\n\n"
            "**How It Works:**\n"
            "Cloud CDN sits in front of a Cloud Load Balancer (HTTP(S) LB). "
            "When a user requests content, Cloud CDN serves it from the nearest edge Point of Presence (PoP) "
            "if cached, otherwise fetches from the origin backend.\n\n"
            "**Cache Modes:**\n"
            "- **CACHE_ALL_STATIC:** Automatically caches static content based on content type.\n"
            "- **USE_ORIGIN_HEADERS:** Respects Cache-Control headers from the origin.\n"
            "- **FORCE_CACHE_ALL:** Caches all responses regardless of headers (use with caution).\n\n"
            "**Key Features:**\n"
            "- **Cache Invalidation:** Purge specific URLs or path patterns instantly.\n"
            "- **Signed URLs / Cookies:** Restrict access to cached content.\n"
            "- **Anycast IP:** Single global IP routes to the nearest PoP automatically.\n\n"
            "Best Practice: Use CACHE_ALL_STATIC mode and set long max-age headers for versioned static assets."
        ),
        "body_id": (
            "Google Cloud CDN mempercepat pengiriman konten dengan menyimpan cache respons di jaringan edge global Google.\n\n"
            "**Cara Kerja:**\n"
            "Cloud CDN berada di depan Cloud Load Balancer (HTTP(S) LB). "
            "Saat pengguna meminta konten, Cloud CDN menyajikannya dari edge Point of Presence (PoP) terdekat "
            "jika sudah di-cache, jika tidak akan mengambil dari backend origin.\n\n"
            "**Mode Cache:**\n"
            "- **CACHE_ALL_STATIC:** Otomatis menyimpan cache konten statis berdasarkan tipe konten.\n"
            "- **USE_ORIGIN_HEADERS:** Menghormati header Cache-Control dari origin.\n"
            "- **FORCE_CACHE_ALL:** Menyimpan cache semua respons tanpa memperhatikan header (gunakan dengan hati-hati).\n\n"
            "**Fitur Utama:**\n"
            "- **Cache Invalidation:** Hapus URL atau pola path tertentu secara instan.\n"
            "- **Signed URLs / Cookies:** Batasi akses ke konten yang di-cache.\n"
            "- **Anycast IP:** Satu IP global merutekan ke PoP terdekat secara otomatis.\n\n"
            "Best Practice: Gunakan mode CACHE_ALL_STATIC dan set header max-age panjang untuk static asset yang sudah di-versioning."
        ),
    },
]
# ==============================================================
# DATA BEST PRACTICES SAP � Konten Gated (Hanya untuk User Login)
# Referensi studi kasus: CSL02, CSL06, CSL08
# Guest hanya melihat title + teaser; body penuh hanya untuk member
# ==============================================================
SAP_BEST_PRACTICES = [
    {
        "title": "CSL02: Optimizing the Procurement Approval Workflow",
        "pillar": "SAP",
        "case_study_ref": "CSL02",
        "teaser": "Discover how to configure multi-level PO approval in SAP B1 to enforce budget controls and eliminate unauthorized purchases.",
        "body_en": (
            "## CSL02: Procurement Best Practice � Multi-Level PO Approval\n\n"
            "**Problem:** Unauthorized purchases and budget overruns due to missing approval controls.\n\n"
            "**Solution Steps:**\n"
            "1. Navigate to Administration > Approval Procedures > Approval Stages.\n"
            "2. Define approval stages (e.g., Dept Head > Finance Manager > CFO) with user assignments.\n"
            "3. Create Approval Templates: set document type = Purchase Order, define conditions (e.g., Total > 10,000,000 IDR).\n"
            "4. Activate the template and assign to relevant users/departments.\n"
            "5. Test: create a PO exceeding the threshold � it should enter 'Pending' status.\n\n"
            "**Key Configuration:**\n"
            "- Enable 'Active' flag on the approval template.\n"
            "- Set 'No Approval Required' for petty cash POs below threshold.\n"
            "- Configure email notifications via Administration > System Initialization > General Settings > Email.\n\n"
            "**Result:** 100% of POs above threshold require documented approval before GRPO can be created."
        ),
        "body_id": (
            "## CSL02: Best Practice Pengadaan � Persetujuan PO Multi-Level\n\n"
            "**Masalah:** Pembelian tidak sah dan pembengkakan anggaran akibat tidak adanya kontrol persetujuan.\n\n"
            "**Langkah Solusi:**\n"
            "1. Navigasi ke Administrasi > Prosedur Persetujuan > Tahap Persetujuan.\n"
            "2. Definisikan tahap persetujuan (mis. Kepala Dept > Manajer Keuangan > CFO) dengan penugasan pengguna.\n"
            "3. Buat Template Persetujuan: set tipe dokumen = Purchase Order, definisikan kondisi (mis. Total > 10.000.000 IDR).\n"
            "4. Aktifkan template dan tetapkan ke pengguna/departemen terkait.\n"
            "5. Uji: buat PO melebihi ambang batas � harus masuk status 'Pending'.\n\n"
            "**Konfigurasi Utama:**\n"
            "- Aktifkan flag 'Aktif' pada template persetujuan.\n"
            "- Set 'Tidak Perlu Persetujuan' untuk PO kas kecil di bawah ambang batas.\n"
            "- Konfigurasi notifikasi email via Administrasi > Inisialisasi Sistem > Pengaturan Umum > Email.\n\n"
            "**Hasil:** 100% PO di atas ambang batas memerlukan persetujuan terdokumentasi sebelum GRPO dapat dibuat."
        ),
    },
    {
        "title": "CSL06: CRM Sales Pipeline & Activity Management",
        "pillar": "SAP",
        "case_study_ref": "CSL06",
        "teaser": "Learn how to build a structured sales pipeline in SAP B1 CRM � from lead capture to closed deal � with activity tracking and win/loss analysis.",
        "body_en": (
            "## CSL06: CRM Best Practice � Sales Pipeline Management\n\n"
            "**Problem:** Sales team lacks visibility into pipeline stages, leading to missed follow-ups and inaccurate forecasts.\n\n"
            "**Solution Steps:**\n"
            "1. Define Sales Stages: Administration > Setup > Sales Opportunities > Sales Stages.\n"
            "   Recommended stages: Lead > Qualified > Proposal > Negotiation > Closed Won/Lost.\n"
            "2. Configure Closing Percentages per stage for weighted pipeline forecasting.\n"
            "3. Create Sales Opportunities linked to Business Partners with expected revenue and close date.\n"
            "4. Log Activities (calls, meetings, tasks) directly on each opportunity.\n"
            "5. Use the Sales Opportunity Report for pipeline analysis and win/loss ratio tracking.\n\n"
            "**Integration Point:** Closed Won opportunities can be converted directly to Sales Quotations, "
            "maintaining document linkage for full audit trail.\n\n"
            "**Result:** Sales forecast accuracy improves by linking pipeline stages to weighted revenue projections."
        ),
        "body_id": (
            "## CSL06: Best Practice CRM � Manajemen Pipeline Penjualan\n\n"
            "**Masalah:** Tim penjualan kurang visibilitas ke tahap pipeline, menyebabkan tindak lanjut terlewat dan perkiraan tidak akurat.\n\n"
            "**Langkah Solusi:**\n"
            "1. Definisikan Tahap Penjualan: Administrasi > Setup > Peluang Penjualan > Tahap Penjualan.\n"
            "   Tahap yang direkomendasikan: Prospek > Kualifikasi > Proposal > Negosiasi > Menang/Kalah.\n"
            "2. Konfigurasi Persentase Penutupan per tahap untuk perkiraan pipeline berbobot.\n"
            "3. Buat Peluang Penjualan yang terhubung ke Business Partner dengan pendapatan yang diharapkan dan tanggal penutupan.\n"
            "4. Catat Aktivitas (panggilan, pertemuan, tugas) langsung pada setiap peluang.\n"
            "5. Gunakan Laporan Peluang Penjualan untuk analisis pipeline dan pelacakan rasio menang/kalah.\n\n"
            "**Titik Integrasi:** Peluang yang Menang dapat dikonversi langsung ke Penawaran Penjualan, "
            "mempertahankan tautan dokumen untuk jejak audit lengkap.\n\n"
            "**Hasil:** Akurasi perkiraan penjualan meningkat dengan menghubungkan tahap pipeline ke proyeksi pendapatan berbobot."
        ),
    },
    {
        "title": "CSL08: Service Call Management & SLA Tracking",
        "pillar": "SAP",
        "case_study_ref": "CSL08",
        "teaser": "Master SAP B1 Service module to manage customer service calls, assign technicians, track resolution time, and enforce SLA compliance.",
        "body_en": (
            "## CSL08: Service Best Practice � Service Call & SLA Management\n\n"
            "**Problem:** Customer complaints are untracked, technician assignments are manual, and SLA breaches go unnoticed.\n\n"
            "**Solution Steps:**\n"
            "1. Configure Service Contract Templates: Service > Service Contracts > Contract Templates.\n"
            "   Define response time SLAs (e.g., Critical: 4h, High: 8h, Normal: 24h).\n"
            "2. Assign Service Contracts to Customer Business Partners.\n"
            "3. Create Service Calls: Service > Service Calls. Link to customer, item (serial number), and contract.\n"
            "4. Assign to technician queue; set Priority and Expected Resolution Date.\n"
            "5. Monitor via Service > Service Call Reports � filter by status (Open, Pending, Closed) and SLA breach.\n\n"
            "**Escalation Rule:** Configure alerts (Administration > Alerts Management) to notify service manager "
            "when a service call approaches SLA deadline without resolution.\n\n"
            "**Result:** SLA compliance visibility increases; average resolution time decreases through structured assignment."
        ),
        "body_id": (
            "## CSL08: Best Practice Layanan � Manajemen Service Call & SLA\n\n"
            "**Masalah:** Keluhan pelanggan tidak terlacak, penugasan teknisi manual, dan pelanggaran SLA tidak terdeteksi.\n\n"
            "**Langkah Solusi:**\n"
            "1. Konfigurasi Template Kontrak Layanan: Layanan > Kontrak Layanan > Template Kontrak.\n"
            "   Definisikan SLA waktu respons (mis. Kritis: 4j, Tinggi: 8j, Normal: 24j).\n"
            "2. Tetapkan Kontrak Layanan ke Business Partner pelanggan.\n"
            "3. Buat Service Call: Layanan > Service Call. Hubungkan ke pelanggan, item (nomor seri), dan kontrak.\n"
            "4. Tetapkan ke antrian teknisi; set Prioritas dan Tanggal Resolusi yang Diharapkan.\n"
            "5. Pantau via Layanan > Laporan Service Call � filter berdasarkan status (Terbuka, Tertunda, Ditutup) dan pelanggaran SLA.\n\n"
            "**Aturan Eskalasi:** Konfigurasi alert (Administrasi > Manajemen Alert) untuk memberi tahu manajer layanan "
            "saat service call mendekati batas waktu SLA tanpa resolusi.\n\n"
            "**Hasil:** Visibilitas kepatuhan SLA meningkat; rata-rata waktu resolusi berkurang melalui penugasan terstruktur."
        ),
    },
]

# ==============================================================
# DATA BEST PRACTICES GCP � Konten Gated (Hanya untuk User Login)
# Panduan praktis: Cloud SQL Backup, Compute Engine Troubleshooting, FinOps
# ==============================================================
GCP_BEST_PRACTICES = [
    {
        "title": "GCP: Automated Cloud SQL Backup to Cloud Storage",
        "pillar": "GCP",
        "case_study_ref": "GCP-BP-01",
        "teaser": "Step-by-step guide to configure automated Cloud SQL backups, export to Cloud Storage buckets, and set up retention policies for disaster recovery.",
        "body_en": (
            "## GCP Best Practice: Cloud SQL Backup & Export to Cloud Storage\n\n"
            "**Scenario:** Ensure PostgreSQL data on Cloud SQL is protected with automated backups and exportable to GCS for long-term retention.\n\n"
            "**Part 1: Enable Automated Backups**\n"
            "1. GCP Console > SQL > Select your instance > Edit.\n"
            "2. Under 'Backups', enable Automated Backups.\n"
            "3. Set backup window (e.g., 02:00�04:00 local time to minimize impact).\n"
            "4. Enable Point-in-Time Recovery (PITR) � requires binary logging.\n"
            "5. Set retention: 7 days (default) up to 365 days.\n\n"
            "**Part 2: Export to Cloud Storage (for long-term archival)**\n"
            "```bash\n"
            "# Ekspor database ke GCS bucket menggunakan gcloud CLI\n"
            "gcloud sql export sql INSTANCE_NAME gs://BUCKET_NAME/backup-$(date +%Y%m%d).sql \\\n"
            "  --database=DATABASE_NAME \\\n"
            "  --offload\n"
            "```\n"
            "Schedule this via Cloud Scheduler + Cloud Functions for full automation.\n\n"
            "**Part 3: Restore Test (Critical)**\n"
            "Regularly test restores to a separate Cloud SQL instance to validate backup integrity.\n\n"
            "**Result:** RPO < 1 hour with PITR; long-term exports stored cost-effectively in GCS Coldline."
        ),
        "body_id": (
            "## Best Practice GCP: Backup Cloud SQL & Ekspor ke Cloud Storage\n\n"
            "**Skenario:** Pastikan data PostgreSQL di Cloud SQL terlindungi dengan backup otomatis dan dapat diekspor ke GCS untuk retensi jangka panjang.\n\n"
            "**Bagian 1: Aktifkan Backup Otomatis**\n"
            "1. GCP Console > SQL > Pilih instance Anda > Edit.\n"
            "2. Di bawah 'Backup', aktifkan Backup Otomatis.\n"
            "3. Set jendela backup (mis. 02:00�04:00 waktu lokal untuk meminimalkan dampak).\n"
            "4. Aktifkan Point-in-Time Recovery (PITR) � memerlukan binary logging.\n"
            "5. Set retensi: 7 hari (default) hingga 365 hari.\n\n"
            "**Bagian 2: Ekspor ke Cloud Storage (untuk pengarsipan jangka panjang)**\n"
            "```bash\n"
            "# Ekspor database ke GCS bucket menggunakan gcloud CLI\n"
            "gcloud sql export sql INSTANCE_NAME gs://BUCKET_NAME/backup-$(date +%Y%m%d).sql \\\n"
            "  --database=DATABASE_NAME \\\n"
            "  --offload\n"
            "```\n"
            "Jadwalkan ini via Cloud Scheduler + Cloud Functions untuk otomasi penuh.\n\n"
            "**Bagian 3: Uji Restore (Kritis)**\n"
            "Uji restore secara berkala ke instance Cloud SQL terpisah untuk memvalidasi integritas backup.\n\n"
            "**Hasil:** RPO < 1 jam dengan PITR; ekspor jangka panjang disimpan hemat biaya di GCS Coldline."
        ),
    },
    {
        "title": "GCP: Compute Engine Troubleshooting Playbook",
        "pillar": "GCP",
        "case_study_ref": "GCP-BP-02",
        "teaser": "A practical troubleshooting guide for common Compute Engine issues: SSH failures, disk full errors, high CPU, and network connectivity problems.",
        "body_en": (
            "## GCP Best Practice: Compute Engine Troubleshooting\n\n"
            "**Issue 1: Cannot SSH into VM**\n"
            "- Check firewall rules: VPC Network > Firewall � ensure port 22 is open for your IP.\n"
            "- Use Serial Console: Compute Engine > VM > Connect to Serial Console for boot-level access.\n"
            "- Try browser-based SSH from GCP Console as a fallback.\n"
            "- Check VM status: ensure it is RUNNING, not TERMINATED or SUSPENDED.\n\n"
            "**Issue 2: Disk Full (100% usage)**\n"
            "```bash\n"
            "# Cek penggunaan disk\n"
            "df -h\n"
            "# Temukan folder terbesar\n"
            "du -sh /* 2>/dev/null | sort -rh | head -10\n"
            "# Bersihkan log lama\n"
            "sudo journalctl --vacuum-time=3d\n"
            "```\n"
            "To resize: GCP Console > Disks > Edit > increase size (no downtime for online resize).\n\n"
            "**Issue 3: High CPU**\n"
            "```bash\n"
            "# Identifikasi proses penyebab CPU tinggi\n"
            "top -b -n 1 | head -20\n"
            "```\n"
            "Consider upgrading machine type or enabling autoscaling with Managed Instance Groups.\n\n"
            "**Issue 4: Network Connectivity**\n"
            "- Verify VPC firewall rules allow the required ports.\n"
            "- Check Cloud NAT configuration for outbound internet access from private VMs.\n"
            "- Use `gcloud compute ssh --troubleshoot` for automated diagnosis."
        ),
        "body_id": (
            "## Best Practice GCP: Panduan Troubleshooting Compute Engine\n\n"
            "**Masalah 1: Tidak Bisa SSH ke VM**\n"
            "- Periksa aturan firewall: VPC Network > Firewall � pastikan port 22 terbuka untuk IP Anda.\n"
            "- Gunakan Serial Console: Compute Engine > VM > Connect to Serial Console untuk akses level boot.\n"
            "- Coba SSH berbasis browser dari GCP Console sebagai fallback.\n"
            "- Periksa status VM: pastikan RUNNING, bukan TERMINATED atau SUSPENDED.\n\n"
            "**Masalah 2: Disk Penuh (penggunaan 100%)**\n"
            "```bash\n"
            "# Cek penggunaan disk\n"
            "df -h\n"
            "# Temukan folder terbesar\n"
            "du -sh /* 2>/dev/null | sort -rh | head -10\n"
            "# Bersihkan log lama\n"
            "sudo journalctl --vacuum-time=3d\n"
            "```\n"
            "Untuk resize: GCP Console > Disk > Edit > tambah ukuran (tidak perlu downtime untuk resize online).\n\n"
            "**Masalah 3: CPU Tinggi**\n"
            "```bash\n"
            "# Identifikasi proses penyebab CPU tinggi\n"
            "top -b -n 1 | head -20\n"
            "```\n"
            "Pertimbangkan upgrade tipe mesin atau aktifkan autoscaling dengan Managed Instance Groups.\n\n"
            "**Masalah 4: Konektivitas Jaringan**\n"
            "- Verifikasi aturan firewall VPC mengizinkan port yang diperlukan.\n"
            "- Periksa konfigurasi Cloud NAT untuk akses internet keluar dari VM privat.\n"
            "- Gunakan `gcloud compute ssh --troubleshoot` untuk diagnosis otomatis."
        ),
    },
    {
        "title": "GCP FinOps: Cost Optimization Strategies for Compute & Storage",
        "pillar": "GCP",
        "case_study_ref": "GCP-BP-03",
        "teaser": "Practical FinOps guide to reduce GCP bills: rightsizing VMs, Committed Use Discounts, Spot VMs, storage lifecycle policies, and budget alerts.",
        "body_en": (
            "## GCP FinOps Best Practice: Cost Optimization\n\n"
            "**Strategy 1: Rightsizing Compute Engine VMs**\n"
            "- Use GCP Recommender: Compute Engine > VM Instances > Recommendations tab.\n"
            "- Identify underutilized VMs (CPU < 10% average) and downsize machine type.\n"
            "- Schedule non-production VMs to stop during off-hours using Cloud Scheduler + Cloud Functions.\n\n"
            "**Strategy 2: Committed Use Discounts (CUDs)**\n"
            "- 1-year CUD: up to 37% discount on N2/E2 machines.\n"
            "- 3-year CUD: up to 57% discount.\n"
            "- Purchase via: Billing > Commitments. Applies automatically to matching usage.\n\n"
            "**Strategy 3: Spot VMs for Batch Workloads**\n"
            "- Up to 91% cheaper than on-demand pricing.\n"
            "- Suitable for: data processing, CI/CD runners, ML training jobs.\n"
            "- Implement checkpointing to handle preemption gracefully.\n\n"
            "**Strategy 4: Cloud Storage Lifecycle Policies**\n"
            "- Auto-transition objects: Standard ? Nearline (30d) ? Coldline (90d) ? Archive (365d).\n"
            "- Delete incomplete multipart uploads after 7 days.\n\n"
            "**Strategy 5: Budget Alerts**\n"
            "- Billing > Budgets & Alerts > Create Budget.\n"
            "- Set thresholds at 50%, 90%, 100% of monthly budget.\n"
            "- Connect to Pub/Sub for automated cost control actions.\n\n"
            "**Result:** Typical savings of 30�60% on GCP bills with disciplined FinOps practices."
        ),
        "body_id": (
            "## Best Practice GCP FinOps: Optimasi Biaya\n\n"
            "**Strategi 1: Rightsizing VM Compute Engine**\n"
            "- Gunakan GCP Recommender: Compute Engine > VM Instances > tab Rekomendasi.\n"
            "- Identifikasi VM yang kurang dimanfaatkan (CPU rata-rata < 10%) dan turunkan tipe mesin.\n"
            "- Jadwalkan VM non-produksi untuk berhenti di luar jam kerja menggunakan Cloud Scheduler + Cloud Functions.\n\n"
            "**Strategi 2: Committed Use Discounts (CUD)**\n"
            "- CUD 1 tahun: diskon hingga 37% untuk mesin N2/E2.\n"
            "- CUD 3 tahun: diskon hingga 57%.\n"
            "- Beli via: Billing > Commitments. Berlaku otomatis untuk penggunaan yang cocok.\n\n"
            "**Strategi 3: Spot VM untuk Beban Kerja Batch**\n"
            "- Hingga 91% lebih murah dari harga on-demand.\n"
            "- Cocok untuk: pemrosesan data, runner CI/CD, pekerjaan pelatihan ML.\n"
            "- Implementasikan checkpointing untuk menangani preemption dengan baik.\n\n"
            "**Strategi 4: Kebijakan Lifecycle Cloud Storage**\n"
            "- Transisi otomatis objek: Standard ? Nearline (30h) ? Coldline (90h) ? Archive (365h).\n"
            "- Hapus upload multipart yang tidak lengkap setelah 7 hari.\n\n"
            "**Strategi 5: Budget Alerts**\n"
            "- Billing > Budgets & Alerts > Buat Budget.\n"
            "- Set ambang batas di 50%, 90%, 100% dari anggaran bulanan.\n"
            "- Hubungkan ke Pub/Sub untuk tindakan kontrol biaya otomatis.\n\n"
            "**Hasil:** Penghematan tipikal 30�60% pada tagihan GCP dengan praktik FinOps yang disiplin."
        ),
    },
]


# ==============================================================
# FUNGSI UTAMA SEEDER
# Logika inti: cek duplikat berdasarkan title sebelum insert
# Bersifat idempotent � aman dijalankan berkali-kali
# ==============================================================

def seed_articles(app):
    """
    Seed semua KnowledgeArticle (SAP + GCP) ke database.
    Menggunakan pengecekan title untuk menghindari duplikasi.
    """
    with app.app_context():
        # Gabungkan data SAP dan GCP menjadi satu list untuk diproses bersama
        all_articles = SAP_ARTICLES + GCP_ARTICLES
        inserted = 0
        skipped = 0

        for data in all_articles:
            # Cek apakah artikel dengan judul yang sama sudah ada di database
            existing = KnowledgeArticle.query.filter_by(title=data["title"]).first()

            if existing:
                # Lewati jika sudah ada � jaga idempotency
                print(f"  [SKIP] Artikel sudah ada: '{data['title']}'")
                skipped += 1
                continue

            # Buat objek model baru dari data dict
            article = KnowledgeArticle(
                title=data["title"],
                topic_category=data["topic_category"],
                pillar=data["pillar"],
                summary=data.get("summary"),
                body_en=data["body_en"],
                body_id=data.get("body_id"),
            )
            # Tambahkan ke session SQLAlchemy (belum commit ke database)
            db.session.add(article)
            print(f"  [ADD]  Artikel baru: '{data['title']}' [{data['pillar']}]")
            inserted += 1

        # Commit semua perubahan sekaligus ke database
        db.session.commit()
        print(f"\n  Artikel: {inserted} ditambahkan, {skipped} dilewati.")
        return inserted, skipped


def seed_best_practices(app):
    """
    Seed semua BestPractice (SAP + GCP) ke database.
    Menggunakan pengecekan title untuk menghindari duplikasi.
    """
    with app.app_context():
        # Gabungkan data Best Practice SAP dan GCP
        all_bp = SAP_BEST_PRACTICES + GCP_BEST_PRACTICES
        inserted = 0
        skipped = 0

        for data in all_bp:
            # Cek apakah best practice dengan judul yang sama sudah ada
            existing = BestPractice.query.filter_by(title=data["title"]).first()

            if existing:
                # Lewati jika sudah ada � jaga idempotency
                print(f"  [SKIP] Best Practice sudah ada: '{data['title']}'")
                skipped += 1
                continue

            # Buat objek model baru dari data dict
            bp = BestPractice(
                title=data["title"],
                pillar=data["pillar"],
                teaser=data["teaser"],
                body_en=data["body_en"],
                body_id=data.get("body_id"),
                case_study_ref=data.get("case_study_ref"),
            )
            # Tambahkan ke session SQLAlchemy
            db.session.add(bp)
            print(f"  [ADD]  Best Practice baru: '{data['title']}' [{data['pillar']}]")
            inserted += 1

        # Commit semua perubahan ke database
        db.session.commit()
        print(f"\n  Best Practices: {inserted} ditambahkan, {skipped} dilewati.")
        return inserted, skipped


def run_seed():
    """
    Fungsi utama yang mengorkestrasi seluruh proses seeding.
    Membuat app context, memastikan tabel ada, lalu menjalankan seeder.
    """
    print("=" * 60)
    print("  UNIFIED IT KNOWLEDGE PORTAL � DATABASE SEEDER")
    print("=" * 60)

    # Buat instance aplikasi Flask menggunakan factory function
    app = create_app()

    # Pastikan semua tabel sudah dibuat sebelum insert data
    # Ini aman dijalankan meski tabel sudah ada (tidak menghapus data)
    with app.app_context():
        db.create_all()
        print("\n[OK] Tabel database siap.\n")

    # Jalankan seeder untuk KnowledgeArticle
    print("[1/2] Seeding Knowledge Articles...")
    seed_articles(app)

    # Jalankan seeder untuk BestPractice
    print("\n[2/2] Seeding Best Practices...")
    seed_best_practices(app)

    print("\n" + "=" * 60)
    print("  SEEDING SELESAI!")
    print("=" * 60)


# Entry point: jalankan hanya jika script dieksekusi langsung
# Bukan saat diimpor sebagai modul
if __name__ == "__main__":
    run_seed()
