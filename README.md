# 🛒 Stuffsus Recommendation System

Sistem Rekomendasi Produk Retail berbasis **Content-Based Filtering**, **TF-IDF**, dan **Cosine Similarity** menggunakan **Dataset Retail New York**. Model rekomendasi telah diintegrasikan ke dalam aplikasi web **Stuffsus** untuk membantu pengguna menemukan produk yang relevan berdasarkan tingkat kemiripan antarproduk.

---

# 📖 Deskripsi Proyek

Stuffsus merupakan aplikasi e-commerce retail berbasis web yang dilengkapi dengan sistem rekomendasi produk. Sistem ini menggunakan pendekatan **Content-Based Filtering** dengan metode **TF-IDF (Term Frequency–Inverse Document Frequency)** dan **Cosine Similarity** untuk menghitung tingkat kemiripan antarproduk sehingga mampu memberikan rekomendasi produk yang relevan kepada pengguna.

Proyek ini dikembangkan sebagai **Proyek Kolaborasi Program Studi Sains Data dan Informatika** di Universitas Teknologi Yogyakarta.

---

# ✨ Fitur Utama

- Pencarian Produk
- Sistem Rekomendasi Produk
- Content-Based Filtering
- TF-IDF Vectorization
- Cosine Similarity
- Keranjang Belanja
- Checkout
- Riwayat Pesanan
- Dashboard Seller
- Dashboard Admin

---

# 📊 Dataset

Dataset yang digunakan adalah **Retail New York Dataset** dengan karakteristik sebagai berikut:

| Informasi | Keterangan |
|-----------|------------|
| Jumlah Transaksi | 9.744 |
| Jumlah Atribut | 34 |
| Jumlah Produk Unik | 81 |

Tahapan preprocessing meliputi:

- Menghapus missing value
- Menghapus data duplikat
- Menyeragamkan nama produk
- Membentuk atribut *transaction_text*
- Menyiapkan data untuk proses vektorisasi

---

# 🧠 Metode yang Digunakan

Metode utama yang digunakan adalah **Content-Based Filtering**, yaitu sistem rekomendasi yang memberikan rekomendasi berdasarkan tingkat kemiripan antarproduk.

Tahapan pengembangan model meliputi:

1. Pengumpulan Data
2. Preprocessing Data
3. Feature Engineering
4. TF-IDF Vectorization
5. Perhitungan Cosine Similarity
6. Content-Based Filtering
7. Top-N Recommendation
8. Evaluasi Model
9. Integrasi ke Aplikasi Web Flask

---

# 🤖 Model Machine Learning

Seluruh proses pembangunan model machine learning dilakukan pada notebook:

```
uas_model_rekomen.ipynb
```

Notebook tersebut mencakup seluruh tahapan pembangunan model, yaitu:

- Memuat dataset
- Data preprocessing
- Feature engineering
- TF-IDF Vectorization
- Perhitungan Cosine Similarity
- Pembentukan Top-N Recommendation
- Evaluasi model
- Menyimpan model hasil pelatihan

Model yang telah dilatih kemudian disimpan dalam file:

```
model/content_based_model_ads_versi7.joblib
```

Model tersebut selanjutnya dipanggil oleh file:

```
recommender.py
```

Kemudian diintegrasikan ke dalam aplikasi Flask melalui:

```
app.py
```

sehingga sistem dapat memberikan rekomendasi produk secara **real-time** kepada pengguna.

---

# 🔄 Alur Sistem

```
Dataset Retail New York
          │
          ▼
Preprocessing Data
          │
          ▼
Feature Engineering
(Transaction Text)
          │
          ▼
TF-IDF Vectorization
          │
          ▼
Cosine Similarity
          │
          ▼
Content-Based Filtering
          │
          ▼
Top-N Recommendation
          │
          ▼
Evaluasi Model
          │
          ▼
Menyimpan Model (.joblib)
          │
          ▼
recommender.py
          │
          ▼
app.py
          │
          ▼
Aplikasi Web Stuffsus
```

---

# 📈 Hasil Evaluasi

| Metrik | Nilai |
|---------|-------:|
| Precision@K | 1.000 |
| Recall@K | 0.266 |
| F1-Score | 0.391 |
| Average Similarity | 0.028 |
| Category Match Ratio | 100% |
| Subcategory Match Ratio | 64.20% |

Hasil evaluasi menunjukkan bahwa sistem mampu menghasilkan rekomendasi produk yang relevan dengan tingkat akurasi yang tinggi berdasarkan kemiripan karakteristik produk.

---

# 💻 Teknologi yang Digunakan

### Bahasa Pemrograman

- Python

### Framework

- Flask

### Machine Learning

- Scikit-Learn
- Pandas
- NumPy

### Basis Data

- MySQL

### Front-End

- HTML
- CSS
- JavaScript

---

# 📂 Struktur Proyek

```
stuffsus-recommendation-system
│
├── data/
│   └── Dataset Retail New York
│
├── model/
│   └── content_based_model_ads_versi7.joblib
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│   ├── base.html
│   ├── shop.html
│   ├── login.html
│   ├── admin.html
│   └── ...
│
├── app.py
├── recommender.py
├── fix_image_url.py
├── requirements.txt
├── uas_model_rekomen.ipynb
└── README.md
```

---

# ⚙️ Cara Menjalankan Aplikasi

### 1. Clone Repository

```bash
git clone https://github.com/undeadarya69/stuffsus-recommendation-system.git
```

### 2. Masuk ke Folder Proyek

```bash
cd stuffsus-recommendation-system
```

### 3. Install Seluruh Library

```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi Flask

```bash
python app.py
```

### 5. Buka Browser

```
http://127.0.0.1:5000
```

---

# 📷 Tampilan Aplikasi

Aplikasi Stuffsus menyediakan beberapa fitur utama, antara lain:

- Halaman Beranda
- Katalog Produk
- Pencarian Produk
- Rekomendasi Produk
- Keranjang Belanja
- Checkout
- Dashboard Seller
- Dashboard Admin

> Screenshot aplikasi dapat ditambahkan pada bagian ini sebagai dokumentasi.

---

# 👨‍💻 Pengembang

**Nyoman Arya Kristian Penny Karna Jaya**

Program Studi Sains Data

Fakultas Sains dan Teknologi

Universitas Teknologi Yogyakarta

---

# 📄 Lisensi

Proyek ini dikembangkan untuk keperluan akademik sebagai bagian dari **Proyek Kolaborasi Program Studi Sains Data dan Informatika Universitas Teknologi Yogyakarta**.
