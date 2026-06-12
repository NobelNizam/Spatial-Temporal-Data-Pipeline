# Project_Blueprint_v0.2

> **Catatan Revisi:** Versi ini merevisi v0.1 berdasarkan dua review teknis. Fokus revisi: menghilangkan _buzzword_ yang tidak didukung implementasi (Data Contracts, Great Expectations, Retry Mechanism, "Spatial Big Data", "Local Distributed Processing" tanpa justifikasi), menambah komponen yang sebelumnya hilang (Decision Threshold, Data Dictionary, Partition Justification, Lineage sederhana, Orkestrator ringan), dan membuat narasi benchmark menjadi pengujian hipotesis yang objektif (bukan pembenaran teknologi yang sudah dipilih).

## 1. Executive Summary

**Nama Proyek:** Spatial-Temporal Data Pipeline dengan Justifikasi Engineering Berbasis Bukti

**Elevator Pitch:** Repositori ini membangun _pipeline_ Bronze-Silver-Gold skala lokal yang menggabungkan data _time-series_ kualitas air berukuran besar (puluhan GB) dengan data kepadatan penduduk (raster WorldPop) untuk 14 stasiun air. Berbeda dari proyek serupa, tujuan utama proyek ini bukan sekadar "membangun pipeline", melainkan **menjawab dengan data**: kapan PySpark benar-benar dibutuhkan dibanding alternatif yang lebih ringan (Pandas/Polars/DuckDB), dan komponen arsitektur mana yang benar-benar memberi nilai versus yang hanya menambah kompleksitas.

**Masalah yang Diselesaikan:**
- **Engineering Decision-Making:** Menentukan, berdasarkan ukuran data aktual (baris, kolom, kardinalitas), _engine_ pemrosesan mana yang tepat — alih-alih memilih teknologi terlebih dahulu lalu mencari pembenarannya.
- **Data Reliability:** Mencegah kegagalan _pipeline_ akibat anomali data (skema berubah, _null_ tidak wajar, duplikasi) melalui validasi ringan yang berjalan _native_ di dalam _engine_ pemrosesan, tanpa menambah _overhead_ tooling eksternal.
- **Spatial Enrichment yang Efisien:** Memperkaya tabel fakta (data kualitas air) dengan tabel dimensi populasi (14 stasiun) tanpa memuat seluruh raster Inggris Raya ke memori.

**Target Pengguna:**
**Data Scientists / ML Engineers:** Membutuhkan dataset gabungan kualitas air + kepadatan penduduk dengan skema yang terdokumentasi jelas (_Data Dictionary_) dan konsisten (_Schema Enforcement_), siap untuk eksplorasi statistik dan pemodelan.

---

## 2. Scope

**In Scope:**

- **Decision Framework (Baru):** Profiling awal dataset (jumlah baris, kolom, kardinalitas, ukuran per partisi) untuk menentukan _engine_ pemrosesan yang sesuai berdasarkan threshold yang telah ditentukan (lihat Bagian 5.1).
- **Bronze Layer (Raw Data):** Ingesti data mentah (CSV kualitas air & GeoTIFF WorldPop) ke dalam _object storage_ lokal (MinIO) untuk menjaga jejak data asli.
- **Silver Layer (Data Quality & Enrichment):**
    - Pembersihan & validasi data kualitas air menggunakan validasi _native_ pada _engine_ terpilih (bukan _tooling_ eksternal).
    - Ekstraksi tabel dimensi populasi (14 baris: `station_id`, `population_density`) dari raster via `rasterio`, dilakukan sekali sebagai _pre-processing_ ringan — **bukan** klaim "Spatial Big Data".
    - Penggabungan tabel fakta (kualitas air, puluhan juta baris) dengan tabel dimensi (14 baris) melalui **Broadcast Join**.
- **Gold Layer (ML-Ready Serving):** Penyimpanan Parquet terpartisi dengan **Schema Enforcement** eksplisit (`StructType`) dan **Data Dictionary** yang terdokumentasi.
- **Observability Dasar:** _Structured logging_ di setiap transisi _layer_, ditangani oleh orkestrator ringan (lihat Bagian 5.3) — bukan _retry mechanism_ manual untuk I/O lokal.
- **Benchmarking sebagai Pengujian Hipotesis:** Perbandingan objektif Pandas/Polars/DuckDB vs PySpark pada dataset aktual, dengan hasil yang **bisa saja menunjukkan Spark tidak diperlukan** — dan itu dianggap valid.

**Out of Scope:**
- Pembangunan model _Machine Learning_ dan _Forecasting_ (repositori terpisah).
- Implementasi _Dashboard Visual_.
- Migrasi _pipeline_ ke _Cloud_ (AWS/EMR) — fokus pada arsitektur _local-reproducible_.
- _Data Contract_ formal dengan _schema registry_ antar-tim (tidak relevan untuk proyek satu repositori/satu pengembang).
- Orkestrasi skala produksi penuh (Airflow) — digantikan orkestrator ringan.

---

## 3. Functional Requirements

**MVP (Minimum Viable Product):**

- **Dataset Profiling (Baru):** Sebelum implementasi, jalankan profiling pada sampel data kualitas air untuk mencatat jumlah baris, jumlah kolom, kardinalitas kolom kunci, dan estimasi ukuran per partisi `station_id`/`year`. Hasil ini dijadikan dasar keputusan _engine_ (Bagian 5.1).
- **Dimension Table Extraction (Spatial):** Menggunakan `rasterio` untuk mengekstrak nilai kepadatan penduduk dalam radius _n_ km dari koordinat 14 stasiun air, menghasilkan tabel dimensi kecil (14 baris). Proses ini **tidak** memuat seluruh raster Inggris Raya — hanya piksel dalam radius yang ditentukan.
- **Native Data Validation (Silver Layer):** Validasi ringan menggunakan API _native_ _engine_ terpilih (misalnya `df.filter()`, `df.describe()`, pengecekan `null_rate`, duplikasi, dan tipe kolom) untuk menyaring anomali sebelum _join_. Baris yang gagal validasi dicatat ke log dan/atau dipindahkan ke folder `rejected/` (DLQ sederhana) — bukan dihentikan total.
- **Broadcast Join & Schema Enforcement (Gold Layer):** Penggabungan tabel fakta kualitas air (hasil validasi) dengan tabel dimensi populasi melalui _broadcast join_ (menghindari _shuffle_ pada data besar). Hasil disimpan sebagai Parquet dengan skema eksplisit (`StructType`) yang didokumentasikan dalam **Data Dictionary** (lihat lampiran `docs/DATA_DICTIONARY.md`).

**Observability & Error Handling:**

- **Structured Logging:** Logging operasional pada setiap _task_ (Bronze → Silver → Gold), mencatat waktu eksekusi, jumlah baris masuk/lolos/ditolak per tahap.
- **Validation & Fail-Fast (pengganti Retry Mechanism):** Untuk kegagalan baca berkas lokal (kasus yang sangat jarang), _pipeline_ menghentikan eksekusi dengan log error yang jelas (_fail-fast_) alih-alih melakukan _retry_ otomatis — karena _retry_ tidak relevan untuk I/O filesystem lokal yang deterministik. _Retry_ hanya diterapkan jika di masa depan ada sumber data via API/jaringan.
- **Lineage Sederhana (Baru):** Setiap _output_ Silver dan Gold menyertakan metadata minimal (`source_file`, `processed_at`, `pipeline_run_id`) sebagai bentuk _lineage_ dasar tanpa memerlukan _tooling_ lineage khusus.

---

## 4. Non-Functional Requirements

**Scalability & Memory Efficiency:** Sistem harus mampu memproses dataset kualitas air berskala puluhan GB tanpa OOM pada perangkat keras lokal. _Engine_ pemrosesan dipilih berdasarkan hasil profiling (Bagian 5.1), bukan diasumsikan sejak awal. Ekstraksi raster menggunakan `rasterio` hanya memuat piksel dalam radius stasiun ke memori.

**Reliability (Data & Operational):** Dijamin melalui validasi _native_ pada Silver Layer (skema, _null rate_, duplikasi) dan strategi _fail-fast_ pada kegagalan I/O, dengan _logging_ yang cukup untuk _debugging_ tanpa orkestrator berat.

**Reproducibility & Maintainability:** Seluruh _environment_ (object storage, _processing engine_) dibungkus Docker. Kode modular, dieksekusi melalui orkestrator ringan (Dagster/Mage.ai) yang menangani urutan _task_, _logging_, dan visualisasi DAG — menggantikan rangkaian skrip `spark-submit` manual.

**Security:** Kredensial _object storage_ diisolasi dari kode menggunakan _environment variables_ (`.env`).

**Honesty of Claims (Baru):** Setiap istilah arsitektur yang digunakan harus sesuai dengan implementasi aktual. Jika suatu komponen (misalnya PySpark) dipilih bukan karena efisiensi tertinggi tetapi untuk demonstrasi kompetensi ekosistem, hal ini dinyatakan secara eksplisit dalam dokumentasi (lihat Bagian 5.2).

---

## 5. Tech Stack

### 5.1 Decision Threshold — Pemilihan Processing Engine

Keputusan _engine_ didasarkan pada hasil _profiling_ data aktual, dengan threshold berikut:

| Ukuran Data (per partisi relevan) | Engine yang Dipertimbangkan |
|---|---|
| < 5 GB | Pandas |
| 5–20 GB, baris sangat banyak / kolom sedang | Polars / DuckDB |
| > 20 GB, atau dibutuhkan demonstrasi ekosistem _distributed_ | PySpark |

**Hasil Profiling Dataset (diisi setelah profiling aktual dijalankan):**
- Jumlah baris: _[diisi]_
- Jumlah kolom: _[diisi]_
- Kardinalitas `station_id`: 14
- Estimasi ukuran per partisi `station_id`/`year`: _[diisi]_

Profiling ini menjadi lampiran wajib (`benchmarks/PROFILING_REPORT.md`) sebelum keputusan _engine_ final ditetapkan.

### 5.2 Justifikasi Komponen (Direvisi)

- **Data Processing Engine (PySpark, dengan justifikasi eksplisit):** PySpark dipertahankan dalam proyek ini bukan diklaim sebagai "paling efisien di lokal" — pada data tunggal 25GB di satu mesin, Polars/DuckDB kemungkinan lebih cepat dan hemat memori (lihat hasil benchmark di Bagian 9). PySpark digunakan secara sadar untuk **mendemonstrasikan kompetensi pada ekosistem _distributed processing_** (`StructType`, _broadcast join_, _partitioned write_) yang relevan untuk peran Data Engineer, dengan _local single-node cluster_ sebagai simulasi terbatas — bukan klaim "Local Distributed Processing" yang setara klaster produksi.
- **Spatial Processor (`rasterio`):** Digunakan untuk ekstraksi **tabel dimensi populasi** (14 baris) dari GeoTIFF WorldPop, dengan _clip_ langsung pada radius koordinat stasiun. Proses ini diposisikan sebagai _pre-processing_ ringan, **bukan** komponen "Spatial Big Data" — beban data besar ada pada _time-series_ kualitas air, bukan pada data spasial.
- **Object Storage (MinIO):** Digunakan untuk mendemonstrasikan **interoperabilitas Spark dengan S3 API** (membaca/menulis Parquet via `s3a://`), bukan sebagai klaim _governance_ atau _auditability_ tingkat enterprise. Jika kompleksitas operasional MinIO dirasa tidak proporsional dengan skala proyek (satu pengguna, satu repositori), alternatif `data/bronze | silver | gold` di filesystem lokal dapat digunakan sebagai _fallback_ yang didokumentasikan.
- **Validasi Data (Native PySpark/Engine, pengganti Great Expectations):** Validasi skema dan kualitas data (_null rate_, duplikasi, tipe kolom) diimplementasikan menggunakan API _native_ _engine_ terpilih (`df.filter()`, `df.describe()`, pengecekan eksplisit). Pilihan ini dibuat secara sadar untuk menghindari _overhead_ dan risiko OOM dari Great Expectations pada data berskala besar di Spark (validasi GE memicu _multiple lazy evaluation calls_ yang berat).
- **Data Serving Format (Apache Parquet) dengan Schema Enforcement (pengganti "Data Contracts"):** Skema Gold Layer didefinisikan eksplisit via `StructType` dan didokumentasikan dalam `docs/DATA_DICTIONARY.md`. Istilah "Data Contracts" tidak digunakan karena tidak ada _producer-consumer_ terpisah antar tim dalam proyek ini; istilah yang akurat adalah **Strict Schema Enforcement**.
- **Infrastructure & Containerization (Docker):** Membungkus _object storage_ dan _processing engine_ untuk reproduktibilitas lintas mesin.

### 5.3 Orkestrasi Ringan (Baru)

Eksekusi _pipeline_ tiga lapis (Bronze → Silver → Gold) dikelola oleh orkestrator ringan (**Dagster** atau **Mage.ai**, dipilih berdasarkan kemudahan setup lokal) yang menyediakan:
- Definisi _dependency_ antar-_task_ secara eksplisit.
- Visualisasi DAG eksekusi.
- _Structured logging_ terintegrasi per _task_.

Airflow secara sengaja tidak digunakan karena _overhead_ operasionalnya tidak proporsional untuk skala proyek ini.

---

## 6. System Architecture

- **Decision Layer (Baru):** Sebelum implementasi _layer_ Bronze, dilakukan _profiling_ dataset untuk menetapkan _engine_ pemrosesan sesuai Bagian 5.1. Keputusan ini didokumentasikan dan dapat diuji ulang jika asumsi berubah.

- **Bronze Layer (Raw Data):** Data CSV kualitas air dan GeoTIFF WorldPop disimpan dalam format asli di _object storage_ (MinIO) atau folder `data/bronze/` (lihat 5.2 untuk kondisi _fallback_). Tujuan: menjaga jejak data asli untuk keperluan _debugging_ dan reproduksi ulang.

- **Silver Layer (Validation & Dimension Extraction):**
    - **Jalur Fact Table:** Data kualitas air divalidasi menggunakan fungsi _native_ _engine_ (cek _null rate_, duplikasi, tipe kolom, konsistensi skema). Baris yang gagal dicatat ke log dan dipindahkan ke `data/rejected/`.
    - **Jalur Dimension Table:** `rasterio` mengekstrak kepadatan populasi untuk 14 stasiun, menghasilkan tabel kecil `station_id, population_density`.
    - **Join:** Tabel fakta (tervalidasi) digabung dengan tabel dimensi (14 baris) via **Broadcast Join**, menghindari _shuffle_ pada dataset besar.

- **Gold Layer (Schema-Enforced Serving):** Hasil _join_ disimpan sebagai Parquet terpartisi berdasarkan `station_id` dan `year`, dengan skema eksplisit (`StructType`). Skema didokumentasikan di `docs/DATA_DICTIONARY.md` yang menjelaskan setiap kolom, tipe, satuan, dan sumber data.

- **Observability Backbone:** Orkestrator ringan (Dagster/Mage.ai) menjalankan setiap _task_ Bronze → Silver → Gold, mencatat _structured log_ (waktu eksekusi, jumlah baris masuk/lolos/ditolak) dan menampilkan DAG eksekusi.

### Struktur Repositori (Direvisi)

```
spatial-temporal-pipeline/
|-- .env                          # Isolasi kredensial object storage
|-- docker-compose.yml            # Containerization object storage & engine
|-- requirements.txt              # Dependensi Python
|-- docs/
|   |-- DATA_DICTIONARY.md         # (Baru) Definisi skema Gold Layer
|   |-- DECISION_LOG.md            # (Baru) Catatan keputusan engine & alasannya
|-- src/
|   |-- config/
|   |   |-- engine_session.py      # Inisialisasi processing engine (sesuai hasil profiling)
|   |-- pipelines/
|   |   |-- bronze_ingest.py       # Ingesti raw CSV & GeoTIFF
|   |   |-- silver_validate.py     # Validasi native + ekstraksi dimensi populasi
|   |   |-- gold_serve.py          # Broadcast join, schema enforcement, partitioning
|   |-- utils/
|   |   |-- spatial_helpers.py     # Fungsi clip/mask koordinat via rasterio
|   |   |-- logger.py              # Structured logging
|-- orchestration/
|   |-- pipeline_dag.py            # Definisi DAG Dagster/Mage.ai
|-- benchmarks/
|   |-- PROFILING_REPORT.md        # (Baru) Hasil profiling awal (rows, cols, cardinality)
|   |-- engine_comparison.py       # Skrip komparasi Pandas/Polars/DuckDB vs PySpark
|   |-- BENCHMARK_REPORT.md        # Laporan hasil benchmark (hipotesis, bukan justifikasi)
```

---

## 7. Development Roadmap

**Minggu 1 — Profiling & Infrastructure:** Jalankan _profiling_ dataset kualitas air (baris, kolom, kardinalitas, estimasi ukuran partisi) dan tetapkan _engine_ awal berdasarkan threshold (Bagian 5.1). Setup Docker untuk _object storage_ dan _engine_ terpilih. Susun `DECISION_LOG.md`.

**Minggu 2 — Silver Layer (Validation & Spatial Dimension):** Implementasi validasi _native_ untuk data kualitas air (skema, _null rate_, duplikasi) dengan output ke `data/rejected/` untuk baris gagal. Ekstraksi tabel dimensi populasi (14 stasiun) via `rasterio`.

**Minggu 3 — Gold Layer & Schema Enforcement:** Implementasi _broadcast join_ tabel fakta dengan tabel dimensi, definisikan skema eksplisit (`StructType`), simpan ke Parquet terpartisi (`station_id`, `year`), dan susun `DATA_DICTIONARY.md`. Jalankan seluruh _pipeline_ melalui orkestrator ringan.

**Minggu 4 — Benchmarking & Finalization:** Jalankan `engine_comparison.py` membandingkan Pandas/Polars/DuckDB vs PySpark pada dataset aktual (sebagai pengujian hipotesis, hasil apapun valid). Susun `BENCHMARK_REPORT.md` dengan kesimpulan objektif mengenai _engine_ yang tepat untuk skala data ini.

---

## 8. Risks

**Risiko Teknis 1: OOM pada Eksekusi Spasial.** Membaca seluruh raster GeoTIFF Inggris Raya dapat menyebabkan _crash_ memori.
**Mitigasi 1:** Menggunakan `rasterio` untuk hanya memotong (_clip_) piksel dalam radius koordinat 14 stasiun — total output tabel dimensi hanya 14 baris.

**Risiko Teknis 2 (Direvisi): Mismatch antara Engine dan Ukuran Data.** Memilih PySpark tanpa profiling dapat menghasilkan _overhead_ JVM yang tidak proporsional, atau sebaliknya memilih _engine_ ringan yang ternyata OOM pada data sebenarnya.
**Mitigasi 2:** Profiling wajib di Minggu 1 sebelum keputusan _engine_ final; keputusan didokumentasikan di `DECISION_LOG.md` dan dapat direvisi jika asumsi awal salah.

**Risiko Teknis 3 (Baru): Validasi Native Tidak Menangkap Anomali Kompleks.** Validasi ringan (`df.filter()`, _null rate_) mungkin tidak menangkap anomali skema yang lebih halus dibanding _tooling_ khusus seperti Great Expectations.
**Mitigasi 3:** Daftar aturan validasi didokumentasikan secara eksplisit dan dapat diperluas inkremental; trade-off ini diterima secara sadar demi menghindari _overhead_ GE pada Spark skala besar.

**Risiko Operasional (Baru): Ketergantungan pada Orkestrator.** Menambahkan Dagster/Mage.ai menambah satu komponen _setup_ baru.
**Mitigasi:** Pilih orkestrator dengan _setup_ Docker minimal dan dokumentasikan langkah _onboarding_ singkat di README.

---

## 9. Success Criteria

**Kriteria 1 (Operational):** _Pipeline_ Bronze → Silver → Gold berjalan otomatis dan berurutan melalui orkestrator ringan tanpa OOM, dengan _engine_ yang dipilih berdasarkan hasil profiling terdokumentasi.

**Kriteria 2 (Data Quality):** Dataset Gold Layer mematuhi **Schema Enforcement** (`StructType`) yang terdokumentasi di `DATA_DICTIONARY.md`, hasil _broadcast join_ akurat antara data kualitas air dan kepadatan penduduk, dan terpartisi logis berdasarkan `station_id`/`year` dengan justifikasi partisi tercantum.

**Kriteria 3 (Engineering Defense — Direvisi):** `BENCHMARK_REPORT.md` menyajikan hasil komparasi Pandas/Polars/DuckDB vs PySpark sebagai **pengujian hipotesis objektif**, lengkap dengan kesimpulan jujur — termasuk jika hasilnya menunjukkan bahwa _engine_ yang lebih ringan sebenarnya cukup, dan PySpark dipilih untuk alasan demonstrasi kompetensi ekosistem (bukan klaim performa absolut).

**Kriteria 4 (Baru — Honesty of Claims):** Setiap istilah arsitektur dalam dokumentasi (Schema Enforcement, Broadcast Join, Dimension/Fact Table, dsb.) dapat ditelusuri langsung ke implementasi kode yang sesuai — tidak ada istilah yang digunakan tanpa dukungan implementasi nyata.
