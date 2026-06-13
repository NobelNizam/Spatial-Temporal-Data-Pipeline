# Update Status

**Date:** June 12, 2026
**Location of Update:** `/home/bishamon/proyek/Spatial-Temporal-Data-Pipeline/UPDATE_STATUS.md`

## 1. Reason for Update
Sejalan dengan penyelesaian *Milestone* Minggu 1 (Profiling & Setup Infrastruktur Docker), keputusan-keputusan krusial mengenai *processing engine* dan *orchestrator* telah difinalisasi berbasis bukti (*evidence-based*). Oleh karena itu, dokumen rujukan awal (`Project_Blueprint` dan `PROJECT_CONTEXT`) harus diperbarui agar mencerminkan kondisi aktual proyek, tidak lagi berada pada fase "Belum mulai implementasi".

## 2. Status Perkembangan Proyek
- **Fase:** Telah menyelesaikan Minggu 1. Akan memasuki Minggu 2 (Bronze & Silver Layer Implementation).
- **Engine Terpilih:** PySpark (Berdasarkan ukuran dataset > 23GB).
- **Orkestrator Terpilih:** Dagster (Berdasarkan keputusan untuk menggunakan arsitektur *Software-Defined Assets* yang *Pythonic*).
- **Infrastruktur:** Seluruh Docker Container (MinIO, Jupyter/PySpark, Dagster Daemon/Webserver) telah aktif, terhubung via *bind-mount*, dan diatur dengan limitasi OOM (4 Cores, 4GB RAM).

## 3. Komparasi Pembaruan File Rujukan

### A. PROJECT_CONTEXT_v0.1.md (Ditingkatkan dari versi awal)
- **Bagian 1 (Status):** Diubah dari "belum mulai implementasi" menjadi "Minggu 1 Selesai. Masuk ke implementasi Bronze Ingest."
- **Bagian 4 & 10 (Scope & Tasks):** Menandai selesai (`[x]`) pada tugas Profiling dan penentuan Engine, serta setup Docker. Menghapus opsi Mage.ai dan mengunci "Dagster".
- **Bagian 5 (Tech Stack):** Mengganti "PySpark sebagai default eksplorasi" menjadi "PySpark sebagai engine utama" berdasarkan bukti ukuran 23.29 GB.
- **Bagian 11 (Known Issues):** Menghapus poin-poin ketidakpastian (engine sementara, Dagster vs Mage, MinIO vs lokal) karena semua sudah terjawab di `DECISION_LOG.md`.

### B. Project_Blueprint_v0.3.md (Ditingkatkan dari v0.2)
- **Bagian 5.1 (Decision Threshold):** Memasukkan hasil empiris profiling (23.29 GB, 62.9 Juta baris, 34 kolom) untuk membuktikan validitas pemilihan PySpark.
- **Bagian 5.3 (Orkestrasi Ringan):** Secara eksplisit menghapus referensi Mage.ai dan menetapkan Dagster sebagai orkestrator tunggal.
- **Bagian 7 (Development Roadmap):** Menandai bahwa Minggu 1 (Profiling & Infrastructure) telah diselesaikan secara penuh.
- **Bagian 8 (Risks):** Menambahkan Risiko 4 terkait *Out of Memory* (OOM) pada mesin lokal dan mitigasinya via pembatasan eksekutor Spark di `engine_session.py` (4 Cores, 4GB RAM).

---

**Date:** June 13, 2026
**Location of Update:** `/home/bishamon/proyek/Spatial-Temporal-Data-Pipeline/UPDATE_STATUS.md`

## 1. Reason for Update
Tahap **Ingestion Layer (Bronze)** telah berhasil diimplementasikan dan dieksekusi. Skrip `bronze_ingest.py` berhasil memindahkan 326 file *raw* (CSV kualitas air dan GeoTIFF kepadatan penduduk) dari direktori lokal ke dalam MinIO Object Storage (bucket `bronze`). Integrasi *asset* dengan Dagster Orchestrator juga telah berhasil diverifikasi. Dokumen rujukan proyek perlu diperbarui untuk mencatat perpindahan status dari "Memasuki implementasi Bronze" menjadi "Bronze Layer Selesai, berlanjut ke Silver Layer".

## 2. Status Perkembangan Proyek
- **Fase:** Implementasi **Bronze Layer telah SELESAI**. Selanjutnya akan masuk ke tahap Silver Layer (Validation & Dimension Extraction).
- **Infrastruktur & Dependensi:** Container Dagster (`dagster_daemon` dan `dagster_ui`) telah diperbarui (`Dockerfile.dagster`) untuk mencakup paket-paket Python krusial untuk keseluruhan *pipeline* seperti `boto3`, `minio`, `pyspark` (dengan Java Runtime), dan `rasterio` (dengan libgdal C++ backend).
- **Ingestion Log:** Total 326 file sukses tertampung di MinIO S3 API *endpoint* yang direpresentasikan dalam `myminio/bronze/`.

## 3. Komparasi Pembaruan File Rujukan

### A. PROJECT_CONTEXT_v0.2.md (Ditingkatkan dari v0.1.md)
- **Bagian 1 (Status):** Diubah dari "Masuk ke implementasi Bronze Ingest." menjadi "Bronze Layer selesai. Masuk ke implementasi Silver Validation & Spatial Enrichment."
- **Bagian 4 (Current Scope):** *Checkbox* fitur Bronze Layer ("Bronze Layer: ingest raw CSV kualitas air + GeoTIFF WorldPop ke object storage") telah ditandai selesai `[x]`.
- **Bagian 10 (Pending Tasks):** Poin "Setup Docker untuk object storage" dan "Implementasi Bronze ingest" telah ditandai selesai. Tugas prioritas selanjutnya bergeser ke poin 5 (Implementasi Silver: validasi native + ekstraksi dimensi).
- **Bagian 11 (Known Issues):** Dihapus masalah "Menunggu implementasi Bronze Layer." karena sudah selesai. Menambahkan informasi bahwa dependensi kontainer telah dimutakhirkan.

### B. Project_Blueprint_v0.4.md (Ditingkatkan dari v0.3.md)
- **Bagian 7 (Development Roadmap):** Menandai target implementasi Bronze di "Minggu 2" sebagai selesai, mengunci fokus selanjutnya pada *Validation* dan pembentukan *Dimension Table* `rasterio`.
- **Bagian 8 (Risks):** Mencatat berhasilnya mitigasi atas ketidakhadiran *environment dependencies* (seperti *module not found `boto3`*) dengan otomatisasi melalui *custom* `Dockerfile.dagster`.

---

**Date:** June 13, 2026
**Location of Update:** `/home/bishamon/proyek/Spatial-Temporal-Data-Pipeline/UPDATE_STATUS.md`

## 1. Reason for Update
Tahap **Exploratory Data Analysis (EDA)** untuk transisi Bronze-to-Silver Layer telah berhasil diselesaikan secara komprehensif pada Jupyter Notebook dan diekstrak laporannya. Keputusan krusial mengenai struktur tabel dimensi vs fakta serta logika pembersihan data (Regex untuk left-censored data, filter threshold, drop malformed CSV) telah didefinisikan. Dokumen rujukan proyek perlu diperbarui untuk mencatat perpindahan ke tahap implementasi skrip `silver_validate.py`.

## 2. Status Perkembangan Proyek
- **Fase:** EDA Transisi Bronze-Silver **SELESAI**. Selanjutnya akan masuk ke koding validasi Silver Layer.
- **Data Anomalies Discovered:** 
  - Data stasiun bukanlah tabel dimensi statis, melainkan data observasi transaksional (>60 juta baris).
  - Ditemukan >16 juta baris data tersensor (misal `<0.5`) yang harus dibersihkan dengan regex agar tidak merusak typecasting float.
  - Ditemukan column-shifting akibat escaped quotes CSV yang rusak.
- **Documentation:** Pembuatan `docs/EDA.md`.

## 3. Komparasi Pembaruan File Rujukan

### A. PROJECT_CONTEXT_v0.3.md (Ditingkatkan dari v0.2.md)
- **Bagian 1 (Status):** Diubah menjadi "EDA selesai. Masuk ke implementasi script silver_validate.py."
- **Bagian 11 (Known Issues):** Mencatat temuan anomali data (Left-censored & Column shifting) dari data stasiun.

### B. Project_Blueprint_v0.5.md (Ditingkatkan dari v0.4.md)
- **Bagian 3 (Functional Requirements):** Menambahkan detail validasi Silver Layer berupa regex stripping dan DROPMALFORMED.
- **Bagian 6 (System Architecture):** Menjelaskan pemisahan Dimension Extraction dari Fact Table WIMS EA di dalam Silver Layer.
