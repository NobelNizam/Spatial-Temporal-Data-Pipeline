# PROJECT_CONTEXT.md

> Dokumen ini adalah memori permanen untuk AI assistant. Baca seluruh dokumen ini sebelum memberikan bantuan apapun pada proyek ini.

---

## 1. Project Identity

- **Nama:** Spatial-Temporal Data Pipeline dengan Justifikasi Engineering Berbasis Bukti
- **Tujuan:** Membangun pipeline data Bronze-Silver-Gold skala lokal yang menggabungkan data time-series kualitas air (puluhan GB) dengan data kepadatan penduduk (raster WorldPop, 14 stasiun), sambil membuktikan secara empiris (lewat profiling & benchmark) bahwa setiap pilihan teknologi memang dibutuhkan — bukan sekadar mengikuti tren arsitektur enterprise.
- **Status:** Blueprint v0.3 — Minggu 1 Selesai. Masuk ke implementasi Bronze Ingest.

---

## 2. Project Vision

Menghasilkan portofolio Data Engineering yang **defensible** di wawancara teknis: setiap istilah arsitektur (broadcast join, schema enforcement, dimension/fact table) harus bisa ditelusuri ke kode nyata. Proyek ini ingin menunjukkan kemampuan *engineering judgment* — memilih alat berdasarkan bukti (profiling/benchmark), bukan berdasarkan buzzword.

---

## 3. Problem Statement

- **Engineering Decision-Making:** Banyak proyek memilih tool berat (Spark, MinIO, Great Expectations) tanpa justifikasi data nyata. Proyek ini menentukan engine pemrosesan berdasarkan hasil profiling aktual (baris, kolom, kardinalitas).
- **Data Reliability:** Mencegah pipeline rusak akibat anomali data (null tidak wajar, duplikasi, skema berubah) lewat validasi native ringan.
- **Spatial Enrichment Efisien:** Memperkaya tabel fakta kualitas air dengan tabel dimensi populasi (14 stasiun) tanpa memuat seluruh raster Inggris Raya ke memori.

---

## 4. Current Scope

Fitur yang sudah disepakati (sesuai Blueprint v0.2):

- [x] Dataset profiling awal (rows, cols, cardinality, ukuran per partisi) → dasar pemilihan engine
- [ ] Bronze Layer: ingest raw CSV kualitas air + GeoTIFF WorldPop ke object storage / `data/bronze/`
- [ ] Silver Layer — jalur fact table: validasi native (null rate, duplikasi, tipe kolom, skema), baris gagal → `data/rejected/`
- [ ] Silver Layer — jalur dimension table: ekstraksi populasi 14 stasiun via `rasterio` (clip radius, bukan full raster)
- [ ] Gold Layer: broadcast join fact table + dimension table, schema enforcement via `StructType`, simpan Parquet terpartisi (`station_id`, `year`)
- [ ] Data Dictionary (`docs/DATA_DICTIONARY.md`)
- [ ] Decision Log (`docs/DECISION_LOG.md`)
- [ ] Lineage minimal: metadata `source_file`, `processed_at`, `pipeline_run_id` pada setiap output Silver/Gold
- [ ] Structured logging di setiap task, dikelola orkestrator ringan
- [ ] Benchmark: Pandas/Polars/DuckDB vs PySpark sebagai pengujian hipotesis (`benchmarks/BENCHMARK_REPORT.md`)

**Out of Scope (jangan dikerjakan kecuali diminta ulang):**
- Model ML / forecasting (repo terpisah)
- Dashboard visual
- Migrasi ke cloud (AWS/EMR)
- Data Contract formal dengan schema registry antar-tim
- Orkestrasi skala produksi penuh (Airflow)

---

## 5. Tech Stack

- **Frontend:** Tidak ada (proyek ini murni data pipeline, tidak ada UI).
- **Backend / Processing Engine:** Engine final ditentukan oleh hasil profiling (Bagian 5.1 Blueprint v0.2), dengan threshold >20GB. Berdasarkan profiling aktual (23.29 GB), **PySpark telah ditetapkan sebagai engine utama**.
- **Spatial Processing:** `rasterio` (untuk clip raster WorldPop, hanya 14 titik koordinat stasiun).
- **Database / Storage Format:** Apache Parquet (Gold Layer), partisi `station_id` + `year`.
- **Object Storage:** MinIO (S3-compatible) — fallback ke folder lokal `data/bronze|silver|gold/` jika kompleksitas operasional tidak proporsional.
- **Orchestration:** Dagster (ringan; Airflow secara sengaja TIDAK dipakai).
- **Infrastructure:** Docker / docker-compose untuk membungkus object storage + processing engine.
- **Deployment:** Lokal-reproducible saja, tidak ada deployment cloud dalam scope ini.

---

## 6. Architecture Decisions

- **Decision:** Engine pemrosesan ditentukan berdasarkan hasil profiling data aktual (rows/cols/cardinality), bukan ditetapkan sejak awal.
  **Reason:** Menghindari resume-driven development; memastikan tool yang dipilih proporsional dengan ukuran data sebenarnya.

- **Decision:** Validasi data menggunakan API native engine (`df.filter()`, `df.describe()`, cek null rate/duplikasi/tipe) — TIDAK menggunakan Great Expectations.
  **Reason:** GE pada PySpark memicu multiple lazy-evaluation calls yang berat dan berisiko menyebabkan OOM justru pada skala data besar yang ingin dihindari.

- **Decision:** Istilah "Data Contracts" diganti "Strict Schema Enforcement" (via `StructType`), didokumentasikan di Data Dictionary.
  **Reason:** Data Contract formal mengandaikan producer-consumer terpisah antar tim; proyek ini satu repo, satu pipeline — istilah Schema Enforcement lebih akurat.

- **Decision:** Spatial extraction (14 stasiun) diposisikan sebagai *dimension table*, digabung ke fact table via *broadcast join*.
  **Reason:** 14 baris bukan "spatial big data"; beban data besar ada di time-series kualitas air. Broadcast join menghindari shuffle pada dataset besar.

- **Decision:** Jika PySpark dipakai meski data bisa ditangani Polars/DuckDB, hal ini dinyatakan eksplisit sebagai "demonstrasi kompetensi ekosistem distributed", bukan klaim performa terbaik.
  **Reason:** Konsistensi dengan klaim "pragmatisme engineering" — kejujuran trade-off lebih kredibel daripada overclaiming.

- **Decision:** Retry mechanism untuk I/O lokal dihapus, diganti strategi fail-fast + log error jelas.
  **Reason:** Retry relevan untuk API/network/DB, bukan untuk pembacaan file lokal yang deterministik.

- **Decision:** MinIO diposisikan sebagai demonstrasi interoperabilitas Spark ↔ S3 API, dengan fallback filesystem lokal jika overhead operasional tidak proporsional.
  **Reason:** Skala proyek (single user, single repo) tidak otomatis membutuhkan object storage; harus ada justifikasi jelas jika tetap dipakai.

- **Decision:** Orkestrator ringan (Dagster/Mage.ai) menggantikan rangkaian `spark-submit` manual; Airflow tidak dipakai.
  **Reason:** Airflow terlalu berat untuk skala proyek ini; orkestrator ringan tetap memberi DAG, logging, dependency management.

---

## 7. Coding Standards

- **Naming Convention:** `snake_case` untuk file Python, variabel, dan kolom dataset. Nama task pipeline deskriptif (`bronze_ingest.py`, `silver_validate.py`, `gold_serve.py`) — hindari penamaan generik seperti `script1.py`.
- **Folder Convention:** Ikuti struktur repo di Blueprint v0.2:
  ```
  src/config/      -> inisialisasi engine
  src/pipelines/   -> bronze_ingest, silver_validate, gold_serve
  src/utils/       -> spatial_helpers, logger
  orchestration/   -> DAG definitions
  docs/            -> DATA_DICTIONARY.md, DECISION_LOG.md
  benchmarks/      -> PROFILING_REPORT.md, BENCHMARK_REPORT.md, engine_comparison.py
  data/bronze|silver|gold|rejected/
  ```
- **API Convention:** Tidak ada API publik dalam scope ini (pipeline batch, bukan service). Jika ditambah di masa depan, gunakan REST + JSON, versi di path (`/v1/...`).
- **Error Handling:** Fail-fast untuk error I/O lokal — log error lengkap lalu hentikan task, jangan retry diam-diam. Baris data yang gagal validasi tidak menghentikan pipeline, tapi dipindahkan ke `data/rejected/` dengan alasan kegagalan dicatat di log.
- **Logging:** Structured logging (format konsisten: timestamp, task name, row counts in/pass/reject, durasi eksekusi) di setiap transisi Bronze→Silver→Gold, terintegrasi dengan orkestrator.

---

## 8. Constraints

Hal-hal yang TIDAK BOLEH dilakukan tanpa diskusi ulang:

1. Jangan menambahkan Great Expectations atau tooling Data Contract formal (schema registry, dsb.) — sudah diputuskan diganti validasi native + schema enforcement.
2. Jangan mengklaim ekstraksi spasial 14 stasiun sebagai "Spatial Big Data" — selalu posisikan sebagai dimension table kecil.
3. Jangan menambahkan retry mechanism untuk I/O filesystem lokal.
4. Jangan menambahkan Airflow atau orkestrator berat lainnya.
5. Jangan menetapkan/mengganti processing engine (Spark/Polars/DuckDB/Pandas) tanpa merujuk pada hasil profiling di `benchmarks/PROFILING_REPORT.md`.
6. Jangan menambahkan fitur ML/forecasting, dashboard visual, atau migrasi cloud — semua di luar scope.
7. Jangan membuat klaim arsitektur (di README/dokumentasi) yang tidak punya implementasi pendukung langsung di kode.

---

## 9. Current Progress

- [x] Blueprint v0.1 selesai
- [x] Review teknis (2 reviewer) selesai
- [x] Blueprint v0.2 selesai (revisi berdasarkan review)
- [x] PROJECT_CONTEXT.md dibuat
- [x] Profiling dataset kualitas air selesai (23.29 GB)
- [x] Infrastruktur Docker (MinIO, Dagster, PySpark) aktif. Belum ada kode pipeline.

---

## 10. Pending Tasks

1. Jalankan profiling dataset kualitas air (rows, cols, cardinality, ukuran per partisi `station_id`/`year`) → tulis ke `benchmarks/PROFILING_REPORT.md`.
2. Tetapkan engine final berdasarkan threshold (Bagian 5.1 Blueprint v0.2) → catat di `docs/DECISION_LOG.md`.
3. Setup Docker untuk object storage (atau fallback filesystem) + engine terpilih.
4. Implementasi Bronze ingest (CSV kualitas air + GeoTIFF WorldPop).
5. Implementasi Silver: validasi native (fact table) + ekstraksi dimensi populasi via `rasterio` (14 stasiun).
6. Implementasi Gold: broadcast join + schema enforcement (`StructType`) + partisi Parquet.
7. Tulis `docs/DATA_DICTIONARY.md`.
8. Setup orkestrator ringan (Dagster/Mage.ai) untuk menjalankan DAG Bronze→Silver→Gold.
9. Implementasi `engine_comparison.py` (Pandas/Polars/DuckDB vs PySpark) → `BENCHMARK_REPORT.md`.

---

## 11. Known Issues

- Infrastruktur Docker sudah berdiri dan dependensi kontainer telah dimutakhirkan (Dockerfile.dagster dengan boto3, minio, rasterio).
- Fase Ingestion Layer (Bronze) telah selesai. 326 file raw berhasil diunggah ke MinIO.
- Hasil profiling sudah selesai (23.29GB, 62.9Jt baris). PySpark resmi dipilih.
- Dagster secara resmi terpilih dan sudah running dalam container.
- MinIO S3 resmi digunakan.

---

## 12. Future Roadmap

Mengikuti roadmap 4 minggu di Blueprint v0.2:

- **Minggu 1:** Profiling & Infrastructure → tetapkan engine, setup Docker, susun `DECISION_LOG.md`.
- **Minggu 2:** Silver Layer — validasi native (fact table) + ekstraksi dimensi populasi (rasterio).
- **Minggu 3:** Gold Layer — broadcast join, schema enforcement, partisi Parquet, `DATA_DICTIONARY.md`, integrasi orkestrator.
- **Minggu 4:** Benchmarking (Pandas/Polars/DuckDB vs PySpark) sebagai pengujian hipotesis → `BENCHMARK_REPORT.md`, finalisasi dokumentasi.

Setelah 4 minggu selesai, evaluasi apakah perlu iterasi tambahan (misalnya menambah stasiun, memperluas radius zonal statistics, atau memperdalam lineage).

---

## 13. Context For AI

Saat membantu proyek ini, AI HARUS:

1. **Jangan mengubah arsitektur tanpa alasan kuat.** Semua keputusan di Bagian 6 (Architecture Decisions) sudah melalui proses review — jangan disarankan diubah kecuali ada data/bukti baru yang kuat (misalnya hasil profiling/benchmark yang bertentangan dengan asumsi).
2. **Hormati keputusan teknis yang telah dibuat.** Termasuk: tidak memakai Great Expectations, tidak memakai retry mechanism untuk I/O lokal, tidak memakai Airflow, tidak overclaim soal "Spatial Big Data" atau "Data Contracts".
3. **Prioritaskan maintainability.** Pilih solusi yang mudah dipahami dan diaudit oleh satu pengembang, sesuai struktur folder di Bagian 7.
4. **Prioritaskan clean architecture.** Pisahkan jelas antara: profiling/decision, ingestion (Bronze), validation & enrichment (Silver), serving (Gold), dan orchestration — jangan campur tanggung jawab antar layer.
5. **Jelaskan trade-off setiap rekomendasi.** Setiap kali menyarankan tool/pendekatan baru, jelaskan trade-off-nya secara eksplisit dan kaitkan dengan threshold/keputusan di Bagian 6 — terutama jika rekomendasi tersebut berpotensi menambah "buzzword" yang sudah dihindari dalam revisi v0.2.
