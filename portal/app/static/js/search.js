/**
 * search.js — Modul Live Search untuk Unified IT Knowledge Portal
 * Menangani pencarian real-time lintas pilar SAP dan GCP tanpa reload halaman.
 *
 * Cara kerja:
 * 1. User mengetik di input search (minimal 2 karakter)
 * 2. Setelah jeda 300ms (debounce), kirim request ke /api/search
 * 3. Tampilkan hasil di dropdown bawah navbar
 * 4. Klik hasil → navigasi ke halaman terkait
 * 5. Input dikosongkan → sembunyikan dropdown
 */

// Referensi elemen DOM yang digunakan
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
const searchResultsInner = document.getElementById('search-results-inner');

// Timer untuk debounce — mencegah request terlalu sering saat user mengetik
let debounceTimer = null;

// Jumlah minimum karakter sebelum search dijalankan
const MIN_QUERY_LENGTH = 2;

// Delay debounce dalam milidetik — sesuai requirement: hasil dalam 500ms
const DEBOUNCE_DELAY = 300;

/**
 * Jalankan pencarian ke API endpoint /api/search.
 * Dipanggil setelah debounce timer selesai.
 * @param {string} query - Kata kunci pencarian dari input user
 */
async function performSearch(query) {
  // Validasi panjang query — jangan kirim request jika terlalu pendek
  if (query.length < MIN_QUERY_LENGTH) {
    hideSearchResults();
    return;
  }

  try {
    // Kirim request GET ke API search dengan parameter query dan bahasa aktif
    const lang = localStorage.getItem('portal_lang') || 'en';
    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&lang=${lang}`);

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const data = await response.json();
    // Render hasil pencarian ke dropdown
    renderSearchResults(data.results, query);

  } catch (error) {
    // Tampilkan pesan error jika request gagal
    console.error('Search error:', error);
    showSearchError();
  }
}

/**
 * Render hasil pencarian ke dalam dropdown.
 * Menerapkan aturan akses: Best Practice hanya tampilkan teaser untuk guest.
 * @param {Array} results - Array hasil pencarian dari API
 * @param {string} query - Query asli untuk highlight teks
 */
function renderSearchResults(results, query) {
  // Kosongkan hasil sebelumnya
  searchResultsInner.innerHTML = '';

  if (!results || results.length === 0) {
    // Tampilkan pesan "tidak ditemukan"
    const lang = localStorage.getItem('portal_lang') || 'en';
    searchResultsInner.innerHTML = `
      <p class="text-sm text-gray-400 py-2 text-center">
        ${lang === 'id' ? 'Tidak ada hasil untuk' : 'No results for'} "<strong>${escapeHtml(query)}</strong>"
      </p>`;
    showSearchResults();
    return;
  }

  // Buat header ringkasan jumlah hasil
  const lang = localStorage.getItem('portal_lang') || 'en';
  const summaryText = lang === 'id'
    ? `${results.length} hasil ditemukan`
    : `${results.length} result${results.length > 1 ? 's' : ''} found`;

  searchResultsInner.innerHTML = `
    <p class="text-xs text-gray-400 mb-2 font-medium">${summaryText}</p>`;

  // Render setiap item hasil pencarian
  results.forEach(item => {
    const div = document.createElement('div');
    div.className = 'search-result-item';

    // Tentukan URL tujuan berdasarkan tipe konten dan pillar
    let targetUrl = '#';
    if (item.content_type === 'knowledge_article') {
      targetUrl = item.pillar === 'SAP' ? '/sap' : '/gcp';
    } else if (item.content_type === 'best_practice') {
      targetUrl = '/best-practices';
    }

    // Badge pillar dengan warna sesuai (SAP = biru, GCP = merah)
    const pillarClass = item.pillar === 'SAP' ? 'sap' : 'gcp';
    const pillarLabel = item.pillar;

    // Teks deskripsi: teaser untuk best practice, summary untuk artikel
    const descText = item.teaser || item.summary || '';
    const truncatedDesc = descText.length > 80 ? descText.substring(0, 80) + '...' : descText;

    // Ikon kunci untuk konten gated (best practice yang belum login)
    const lockIcon = item.is_gated ? ' 🔒' : '';

    div.innerHTML = `
      <span class="search-pillar-badge ${pillarClass}">${pillarLabel}</span>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-semibold text-gray-800 truncate">${escapeHtml(item.title)}${lockIcon}</p>
        ${truncatedDesc ? `<p class="text-xs text-gray-500 mt-0.5 line-clamp-1">${escapeHtml(truncatedDesc)}</p>` : ''}
      </div>`;

    // Navigasi ke halaman terkait saat item diklik
    div.addEventListener('click', () => {
      window.location.href = targetUrl;
      hideSearchResults();
      searchInput.value = '';
    });

    searchResultsInner.appendChild(div);
  });

  showSearchResults();
}

/**
 * Tampilkan pesan error jika search API tidak tersedia.
 */
function showSearchError() {
  const lang = localStorage.getItem('portal_lang') || 'en';
  searchResultsInner.innerHTML = `
    <p class="text-sm text-red-400 py-2 text-center">
      ${lang === 'id' ? 'Pencarian tidak tersedia saat ini.' : 'Search is temporarily unavailable.'}
    </p>`;
  showSearchResults();
}

/**
 * Tampilkan dropdown hasil search.
 */
function showSearchResults() {
  searchResults.classList.remove('hidden');
}

/**
 * Sembunyikan dropdown hasil search.
 */
function hideSearchResults() {
  searchResults.classList.add('hidden');
  searchResultsInner.innerHTML = '';
}

/**
 * Escape karakter HTML untuk mencegah XSS injection.
 * Selalu gunakan fungsi ini sebelum memasukkan teks user ke innerHTML.
 * @param {string} text - Teks yang akan di-escape
 * @returns {string} Teks yang sudah aman untuk dimasukkan ke HTML
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(text));
  return div.innerHTML;
}

// ============================================================
// EVENT LISTENERS — Pasang setelah DOM siap
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  if (!searchInput) return; // Keluar jika elemen search tidak ada di halaman ini

  // Event: user mengetik di input search
  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();

    // Bersihkan timer debounce sebelumnya agar tidak tumpang tindih
    clearTimeout(debounceTimer);

    if (query.length < MIN_QUERY_LENGTH) {
      // Sembunyikan dropdown jika query terlalu pendek
      hideSearchResults();
      return;
    }

    // Set timer debounce — tunggu 300ms setelah user berhenti mengetik
    debounceTimer = setTimeout(() => {
      performSearch(query);
    }, DEBOUNCE_DELAY);
  });

  // Event: klik di luar area search → sembunyikan dropdown
  document.addEventListener('click', (e) => {
    if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
      hideSearchResults();
    }
  });

  // Event: tekan Escape → sembunyikan dropdown dan kosongkan input
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      hideSearchResults();
      searchInput.value = '';
      searchInput.blur();
    }
  });
});
