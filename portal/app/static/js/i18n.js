/**
 * i18n.js — Modul Language Toggle untuk Unified IT Knowledge Portal
 * Menangani pergantian bahasa antara English (EN) dan Bahasa Indonesia (ID)
 * tanpa reload halaman penuh (client-side i18n).
 *
 * Cara kerja:
 * 1. Setiap elemen teks yang bisa diterjemahkan memiliki atribut data-en dan data-id
 * 2. Saat toggle diklik, semua elemen tersebut diperbarui sesuai bahasa yang dipilih
 * 3. Preferensi bahasa disimpan di localStorage agar persisten antar halaman
 */

// Bahasa aktif saat ini — dibaca dari localStorage, default ke 'en'
let currentLang = localStorage.getItem('portal_lang') || 'en';

/**
 * Terapkan bahasa ke semua elemen yang memiliki atribut data-en / data-id.
 * Fungsi ini dipanggil saat halaman dimuat dan saat toggle diklik.
 * @param {string} lang - Kode bahasa: 'en' atau 'id'
 */
function applyLanguage(lang) {
  // Perbarui semua elemen yang memiliki atribut data-en (teks statis)
  document.querySelectorAll('[data-en]').forEach(el => {
    // Ambil teks sesuai bahasa yang dipilih
    const text = lang === 'id' ? el.getAttribute('data-id') : el.getAttribute('data-en');
    if (text) el.textContent = text;
  });

  // Perbarui placeholder input search jika ada
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    const placeholder = lang === 'id'
      ? searchInput.getAttribute('data-placeholder-id')
      : searchInput.getAttribute('data-placeholder-en');
    if (placeholder) searchInput.placeholder = placeholder;
  }

  // Perbarui label tombol toggle bahasa di navbar
  const langLabel = document.getElementById('lang-label');
  if (langLabel) langLabel.textContent = lang.toUpperCase();

  // Perbarui atribut lang pada tag <html> untuk aksesibilitas
  document.getElementById('html-root').setAttribute('lang', lang);

  // Perbarui konten artikel yang memiliki data-body-en / data-body-id
  // Ini untuk halaman pillar SAP dan GCP yang menampilkan body artikel
  document.querySelectorAll('.article-body, .bp-body').forEach(el => {
    const body = lang === 'id'
      ? el.getAttribute('data-body-id')
      : el.getAttribute('data-body-en');
    if (body) el.textContent = body;
  });

  // Simpan preferensi bahasa ke localStorage agar persisten
  localStorage.setItem('portal_lang', lang);
  currentLang = lang;
}

/**
 * Toggle bahasa: jika aktif EN → ganti ke ID, dan sebaliknya.
 * Dipanggil saat tombol language toggle di navbar diklik.
 */
function toggleLanguage() {
  const newLang = currentLang === 'en' ? 'id' : 'en';
  applyLanguage(newLang);

  // Kirim preferensi bahasa ke server via API agar sinkron dengan session Flask
  // Ini penting agar konten yang di-render server-side juga menggunakan bahasa yang benar
  fetch('/api/set-language', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lang: newLang })
  }).catch(() => {
    // Jika request gagal (offline), tetap lanjutkan — client-side sudah diperbarui
    console.warn('Gagal sinkronisasi bahasa ke server, menggunakan client-side saja.');
  });
}

// ============================================================
// INISIALISASI — Jalankan saat DOM selesai dimuat
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  // Terapkan bahasa yang tersimpan saat halaman pertama kali dimuat
  applyLanguage(currentLang);

  // Pasang event listener ke tombol language toggle di navbar
  const langToggleBtn = document.getElementById('lang-toggle');
  if (langToggleBtn) {
    langToggleBtn.addEventListener('click', toggleLanguage);
  }
});
