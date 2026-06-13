# Exploratory Data Analysis (EDA) Report
**Date:** June 13, 2026
**Layer:** Bronze-to-Silver Transition

## Bagian A: Analisis Data Kualitas Air (Figshare / Country-Wise Data)
Dataset: `England_dataset.csv` (Pivot Table, 2.1 Juta Baris)

**1. Data Overview & Missing Values**
- **Skala Data:** Terdapat total 2,129,198 baris dan 14 kolom numerik/kategorikal.
- **Duplikasi:** Terdapat 1,301 baris duplikat yang harus di-drop di Silver Layer.
- **Missing Values:** Fungsi `count` untuk nilai Null/NaN adalah 0. Namun, ada kemungkinan kekosongan diisi string kosong `""` atau `"null"`.

**2. Descriptive Statistic & Outliers**
- **Karakteristik:** Rata-rata pH adalah 7.72. Terdapat anomali dengan nilai minimal pH 0.0 dan maksimal 14.0. Temperatur memiliki nilai maksimal ekstrem (97.5 °C) yang mengindikasikan error sensor.
- **Metode Deteksi Outlier:** Metode IQR mendeteksi outlier sangat banyak (BOD: 337,547 baris) dibanding Z-Score (29,799 baris), menunjukkan distribusi right-skewed. Pendekatan domain threshold (logika bisnis) lebih esensial untuk validasi Silver dibanding sekadar IQR statistik.

**3. Data Consistency**
Ditemukan data kotor yang wajib di-filter ke layer `rejected/`:
- **Waterbody Type Typo:** ` THROCKMORTON"` dan ` FE"`.
- **Invalid Date:** 7 baris tidak sesuai format `DD-MM-YYYY`.
- **Invalid Temperature:** 38 baris (< -10°C atau > 60°C).
- **Invalid CCME_WQI:** 7 baris di luar klasifikasi standar.

---

## Bagian B: Analisis Data Stasiun (WIMS EA / Transactional Data)
Dataset: `station/*/*.csv` (Log Transaksional, > 60 Juta Baris)

**1. Struktur Data Transaksional**
Dataset stasiun ini BUKAN sekadar tabel dimensi spasial, melainkan log observasi (Linked Open Data) raksasa. Satu baris mewakili satu pengukuran spesifik (`determinand`) pada waktu tertentu (`phenomenonTime`).

**2. Volume & Corrupt Records**
- **Skala Data:** 60,076,180 baris observasi.
- **Corrupted Lines:** Terdapat *column shifting* (pergeseran kolom) akibat *escaped quotes* kotor di CSV, ditandai dengan ID bernilai `0` atau notasi berisi teks seperti ` BEDS."`. Baris ini harus dibuang menggunakan mode `DROPMALFORMED` atau regex ketat.

**3. Left-Censored Data Analysis**
- Terdapat **16,055,132 baris** dengan kolom `result` berformat string tersensor (misal: `<0.5` atau `>100`). Data ini harus dibersihkan (regex stripping) dan di-cast ke Float sebelum diagregasi, agar tidak menyebabkan typecasting error di Silver Layer.

**4. Statistik & Domain Anomali**
- **Ammoniacal Nitrogen:** Nilai Max mencapai 124,000 mg/L (rata-rata 4.3 mg/L).
- **Temperature:** Nilai Max mencapai 1310 °C. Terdapat 111 baris observasi suhu air yang tidak wajar (< -10 atau > 50 °C).

**5. Ekstraksi Dimensi Spasial**
Dari 60 juta baris fakta, dapat diekstrak 57,845 baris dimensi stasiun unik (`dropDuplicates` pada kolom notasi). Karena adanya *column shifting*, proses ekstraksi ini harus disertai pembersihan format notasi stasiun (alfanumerik) dan validasi batas geografis Inggris Raya (Lat 49-61, Lon -9-2).

---

## Kesimpulan untuk Implementasi Silver Layer (`silver_validate.py`):
1. **Pemisahan Pipeline:** Harus memisahkan aliran proses antara pembersihan Fact Table (Observasi Kualitas Air) dengan penarikan Dimension Table (Data Geospasial Stasiun).
2. **Regex Cleansing:** Menerapkan regex stripping untuk nilai *result* tersensor di log transaksional WIMS.
3. **Filter Anomali Ekstrim:** Memfilter baris yang mengalami *column-shifting* dan menerapkan *domain threshold* (seperti Suhu -10 s/d 50 °C, pH 0 s/d 14). Baris gagal validasi akan disalurkan ke direktori `rejected/`.
4. **Agregasi Aman (Anti-OOM):** Menggunakan operasi agregasi native PySpark secara terdistribusi pada keseluruhan tahap validasi untuk mencegah Host OS *Out of Memory*.
