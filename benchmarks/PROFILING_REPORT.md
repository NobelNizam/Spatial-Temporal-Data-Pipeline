# Profiling Report

**Date:** June 12, 2026
**Dataset:** Water Quality Time-Series (CSV)
**Location:** `data/bronze/` (Various subdirectories including `Country-Wise Data` and `station/`)

## 1. Objective
Sesuai dengan Bagian 5.1 dari `Project_Blueprint_v0.2.md`, dokumen ini mencatat hasil profiling empiris pada data mentah (Bronze Layer) untuk menentukan *processing engine* yang paling tepat, mencegah *resume-driven development*, dan memastikan spesifikasi teknologi sebanding dengan skala data aktual.

## 2. Methodology
Profiling dilakukan dengan memindai seluruh file CSV pada direktori `data/bronze/` secara rekursif, menghitung total ukuran file (bytes), jumlah baris, mendeteksi header kolom, serta menghitung kardinalitas khusus untuk kolom representasi stasiun (`Area`). Skrip eksekusi dapat dilihat pada `benchmarks/profiling_script.py`.

## 3. Results
- **Total Files Analyzed:** 302 CSV files
- **Total Storage Size:** 23.29 GB (23,854.25 MB)
- **Total Rows:** 62,900,930
- **Total Unique Columns:** 34
- **Cardinality ('Area'):** 61,689 unique areas

**Sample Columns:** `Ammonia (mg/l)`, `id`, `Temperature (cel)`, `Nitrogen (mg/l)`, `Date`, `samplingPoint.region`, `Biochemical Oxygen Demand (mg/l)`, etc.

## 4. Conclusion & Next Steps
Berdasarkan *Decision Threshold* di Blueprint:
- `< 5 GB`: Pandas
- `5–20 GB`: Polars / DuckDB
- `> 20 GB`: PySpark

Karena ukuran data menembus **23.29 GB**, maka persyaratan sistem telah memenuhi ambang batas penggunaan pemrosesan terdistribusi lokal. **PySpark** akan digunakan sebagai engine pemrosesan utama untuk tahap Silver dan Gold. Keputusan ini akan dilampirkan secara resmi di `docs/DECISION_LOG.md`.