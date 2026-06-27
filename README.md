# Stuffsus E-commerce (Flask) — Versi 3
Terintegrasi dengan dataset transaksi New York + model rekomendasi content-based.

## Cara Menjalankan
```bash
pip install -r requirements.txt
python app.py
```
Buka http://127.0.0.1:5000

> **Tidak perlu hapus database manual lagi.** Saat start, aplikasi otomatis
> mendeteksi skema database lama dan membangun ulang + mengisi data contoh.
> (Inilah penyebab halaman/link error sebelumnya: file `stuffsus_shop.db`
> lama masih terpakai sehingga query gagal.)

## Akun Demo
| Role   | Username | Password  |
|--------|----------|-----------|
| Admin  | admin    | admin123  |
| Seller | seller   | seller123 |
| User   | user     | user123   |

## Struktur Sesuai ERD
Kategori (1) → (N) Subkategori (1) → (N) Produk.
81 produk di-seed dari `data/seed_products.json` (dihasilkan dari
`data_kategorikal_newyork.xlsx` + `subcategory_map` di model joblib).
Label **Best Seller** dihitung dari frekuensi penjualan asli di dataset.

## Model Rekomendasi (Content-Based)
- File: `model/content_based_model.joblib` (TF-IDF + cosine similarity, 81 produk)
- Wrapper: `recommender.py` — `recommend(slug)` dan `recommend_for_many([slug,...])`
- Dipakai di: **Beranda** (section "Rekomendasi Untukmu" jika keranjang berisi)
  dan **Keranjang** (section "Produk Serupa Untukmu").
- Jika scikit-learn tidak terinstal, aplikasi tetap jalan tanpa rekomendasi.

> **Siap untuk diganti dengan model dari Data Scientist**
> 
> Untuk mengganti model + dataset:
> 1. Ganti file `model/content_based_model.joblib` dengan file baru
> 2. Update / ganti `data/seed_products.json` (struktur sama: `kategori_map` + list `products`)
> 3. Jalankan ulang `python app.py` → otomatis rebuild database + seed data baru
> 4. Model wrapper di `recommender.py` sudah siap (hanya butuh `product_index`, `similarity`, `product_names`)

## Perubahan di v3.1 (Fixes & Improvements)
- ✅ Product card styling diperbaiki (layout sekarang sesuai CSS)
- ✅ Stock management lengkap (stok berkurang saat checkout + validasi saat tambah keranjang)
- ✅ Quantity bisa diubah di halaman Keranjang
- ✅ Pagination + filter yang lebih pintar di halaman Shop (12 produk per halaman)
- ✅ Filter kategori & special tetap preserve saat berpindah halaman
- ✅ Siap production untuk model & dataset dari tim Data Science

## Halaman
- **Beranda (/)**: New Arrival, Best Seller, On Discount (+ Rekomendasi).
- **Shop (/shop)**: SEMUA produk + sidebar kategori dinamis (dengan jumlah produk)
  + filter spesial New Arrival / Best Seller / On Discount yang bisa diklik.
- Checkout dengan 6 metode pembayaran, riwayat pesanan, profil yang bisa diedit,
  Dashboard Seller, Dashboard Admin.
