# E-Commerce Data Analysis Dashboard

## Deskripsi
Dashboard ini dibuat untuk menganalisis data e-commerce dengan fokus pada:
- Segmentasi pelanggan menggunakan RFM Analysis
- Kategori produk dengan penjualan tertinggi
- Pengaruh keterlambatan pengiriman terhadap rating pelanggan

Dashboard ini bersifat interaktif dengan fitur filter berdasarkan rentang tanggal untuk mengeksplorasi perubahan data dari waktu ke waktu.

## Setup Environment
### 1. Clone Repository
```bash
git clone https://github.com/aeiprsty/dashboard-streamlit-e-commerce.git
cd dashboard-streamlit-e-commerce
```
### 2. Install Dependencies
Pastikan Python sudah terinstall, lalu jalankan:
```bash
pip install -r requirements.txt
```

## Menjalankan Dashboard Secara Lokal
Jalankan perintah berikut di terminal:
```bash
streamlit run dashboard/dashboard.py
```

Setelah itu, dashboard akan terbuka otomatis di browser pada alamat:
```
http://localhost:8501
```

## Deployment
Dashboard dapat diakses melalui link berikut:
https://aeiprsty-dashboard-e-commerce.streamlit.app/