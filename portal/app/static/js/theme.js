/**
 * theme.js — Modul Dark/Light Mode untuk Unified IT Knowledge Portal
 *
 * PENJELASAN LOGIKA localStorage UNTUK TEMA (BAHASA INDONESIA):
 * ============================================================
 * localStorage adalah penyimpanan data di browser yang bersifat PERSISTEN.
 * Artinya, data yang disimpan di sini TIDAK akan hilang meskipun:
 * - Tab browser ditutup
 * - Browser di-restart
 * - Halaman di-refresh
 *
 * Data baru hilang jika user menghapus cache/data browser secara manual.
 *
 * ALUR KERJA TEMA:
 * 1. Saat halaman pertama kali dibuka:
 *    → Script di <head> (base.html) membaca localStorage['portal_theme']
 *    → Jika nilainya 'dark', class 'dark' ditambahkan ke <html> SEBELUM render
 *    → Ini mencegah "flash of white" — halaman tidak berkedip putih sebelum gelap
 *
 * 2. Saat user mengklik tombol toggle (bulan/matahari):
 *    → Fungsi toggleTheme() dipanggil
 *    → Class 'dark' ditambah/dihapus dari <html>
 *    → Nilai baru ('dark' atau 'light') disimpan ke localStorage
 *    → Ikon tombol berganti antara matahari dan bulan
 *
 * 3. Saat user membuka halaman lain di portal:
 *    → Script di <head> kembali membaca localStorage
 *    → Tema yang sama diterapkan secara konsisten di semua halaman
 *
 * MENGAPA MENGGUNAKAN CLASS DI <html> BUKAN <body>?
 * → Karena Tailwind CSS dark mode menggunakan selector 'html.dark ...'
 * → Menempatkan class di <html> memastikan semua elemen di bawahnya
 *   (termasuk <body>, <nav>, dll) bisa di-style dengan selector dark mode
 */

/**
 * Terapkan tema ke UI: update ikon dan class <html>.
 * @param {string} theme - 'dark' atau 'light'
 */
function applyTheme(theme) {
  const html = document.documentElement;
  const iconMoon = document.getElementById('icon-moon');
  const iconSun = document.getElementById('icon-sun');

  if (theme === 'dark') {
    // Tambahkan class 'dark' ke <html> untuk mengaktifkan dark mode CSS
    html.classList.add('dark');
    // Tampilkan ikon matahari (klik untuk kembali ke light)
    if (iconMoon) iconMoon.classList.add('hidden');
    if (iconSun) iconSun.classList.remove('hidden');
  } else {
    // Hapus class 'dark' dari <html> untuk kembali ke light mode
    html.classList.remove('dark');
    // Tampilkan ikon bulan (klik untuk ke dark mode)
    if (iconMoon) iconMoon.classList.remove('hidden');
    if (iconSun) iconSun.classList.add('hidden');
  }
}

/**
 * Toggle tema: jika dark → ganti ke light, jika light → ganti ke dark.
 * Simpan pilihan ke localStorage agar persisten antar sesi browser.
 */
function toggleTheme() {
  // Cek tema saat ini berdasarkan class di <html>
  const isDark = document.documentElement.classList.contains('dark');
  const newTheme = isDark ? 'light' : 'dark';

  // Terapkan tema baru ke UI
  applyTheme(newTheme);

  // Simpan preferensi ke localStorage dengan key 'portal_theme'
  // Nilai ini akan dibaca kembali saat halaman berikutnya dibuka
  localStorage.setItem('portal_theme', newTheme);
}

// ============================================================
// INISIALISASI — Jalankan saat DOM selesai dimuat
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  // Baca tema yang tersimpan dari localStorage
  const savedTheme = localStorage.getItem('portal_theme') || 'light';

  // Terapkan tema (sinkronkan ikon dengan state yang sudah diterapkan di <head>)
  applyTheme(savedTheme);

  // Pasang event listener ke tombol theme toggle
  const themeToggleBtn = document.getElementById('theme-toggle');
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', toggleTheme);
  }
});
