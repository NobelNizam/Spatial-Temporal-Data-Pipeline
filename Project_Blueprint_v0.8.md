# Project_Blueprint_v0.6

> **Catatan Revisi:** Versi ini merevisi v0.5 dengan menambahkan strategi pemetaan stasiun yang valid antara dataset Figshare dan WIMS EA, serta mengonfirmasi parameter radius kepadatan penduduk yang bersifat *scalable*.

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

- **Decision Framework:** Profiling awal dataset (jumlah baris, kolom, kardinalitas, ukuran per partisi) untuk menentukan _engine_ pemrosesan yang sesuai berdasarkan threshold yang telah ditentukan (lihat Bagian 5.1).
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

- **Dataset Profiling:** Sebelum implementasi, jalankan profiling pada sampel data kualitas air untuk mencatat jumlah baris, jumlah kolom, kardinalitas kolom kolom kunci, dan estimasi ukuran per partisi `station_id`/`year`. Hasil ini dijadikan dasar keputusan _engine_ (Bagian 5.1).
- **Dimension Table Extraction (Spatial):** Menggunakan `rasterio` untuk mengekstrak nilai kepadatan penduduk dalam radius _n_ km dari koordinat 14 stasiun air, menghasilkan tabel dimensi kecil (14 baris). Proses ini **tidak** memuat seluruh raster Inggris Raya — hanya piksel dalam radius yang ditentukan.
- **Native Data Validation (Silver Layer):** Validasi ringan menggunakan API _native_ _engine_ terpilih (misalnya `df.filter()`, `df.describe()`, pengecekan `null_rate`, duplikasi, dan tipe kolom) untuk menyaring anomali sebelum _join_. Baris yang gagal validasi dicatat ke log dan/atau dipindahkan ke folder `rejected/` (DLQ sederhana) — bukan dihentikan total.
- **Broadcast Join & Schema Enforcement (Gold Layer):** Penggabungan tabel fakta kualitas air (hasil validasi) dengan tabel dimensi populasi melalui _broadcast join_ (menghindari _shuffle_ pada data besar). Hasil disimpan sebagai Parquet dengan skema eksplisit (`StructType`) yang didokumentasikan dalam **Data Dictionary** (lihat lampiran `docs/DATA_DICTIONARY.md`).

**Observability & Error Handling:**

- **Structured Logging:** Logging operasional pada setiap _task_ (Bronze → Silver → Gold), mencatat waktu eksekusi, jumlah baris masuk/lolos/ditolak per tahap.
- **Validation & Fail-Fast (pengganti Retry Mechanism):** Untuk kegagalan baca berkas lokal (kasus yang sangat jarang), _pipeline_ menghentikan eksekusi dengan log error yang jelas (_fail-fast_) alih-alih melakukan _retry_ otomatis — karena _retry_ tidak relevan untuk I/O filesystem lokal yang deterministik. _Retry_ hanya diterapkan jika di masa depan ada sumber data via API/jaringan.
- **Lineage Sederhana:** Setiap _output_ Silver dan Gold menyertakan metadata minimal (`source_file`, `processed_at`, `pipeline_run_id`) sebagai bentuk _lineage_ dasar tanpa memerlukan _tooling_ lineage khusus.

---

## 4. Non-Functional Requirements

**Scalability & Memory Efficiency:** Sistem harus mampu memproses dataset kualitas air berskala puluhan GB tanpa OOM pada perangkat keras lokal. _Engine_ pemrosesan (PySpark) diatur dengan pembatasan eksekutor (maks 4 Cores, 4GB RAM) agar aman pada mesin *host* (lihat Bagian 8). Ekstraksi raster menggunakan `rasterio` hanya memuat piksel dalam radius stasiun ke memori.

**Reliability (Data & Operational):** Dijamin melalui validasi _native_ pada Silver Layer (skema, _null rate_, duplikasi) dan strategi _fail-fast_ pada kegagalan I/O, dengan _logging_ yang cukup untuk _debugging_ tanpa orkestrator berat.

**Reproducibility & Maintainability:** Seluruh _environment_ (object storage, _processing engine_) dibungkus Docker. Kode modular, dieksekusi melalui orkestrator ringan (Dagster) yang menangani urutan _task_, _logging_, dan visualisasi DAG — menggantikan rangkaian skrip `spark-submit` manual.

**Security:** Kredensial _object storage_ diisolasi dari kode menggunakan _environment variables_ (`.env`).

**Honesty of Claims:** Setiap istilah arsitektur yang digunakan harus sesuai dengan implementasi aktual. Jika suatu komponen (misalnya PySpark) dipilih bukan karena efisiensi tertinggi tetapi untuk demonstrasi kompetensi ekosistem, hal ini dinyatakan secara eksplisit dalam dokumentasi (lihat Bagian 5.2).

---

## 5. Tech Stack

### 5.1 Decision Threshold — Pemilihan Processing Engine

Keputusan _engine_ didasarkan pada hasil _profiling_ data aktual, dengan threshold berikut:

| Ukuran Data (per partisi relevan) | Engine yang Dipertimbangkan |
|---|---|
| < 5 GB | Pandas |
| 5–20 GB, baris sangat banyak / kolom sedang | Polars / DuckDB |
| > 20 GB, atau dibutuhkan demonstrasi ekosistem _distributed_ | **PySpark** |

**Hasil Profiling Dataset (Telah Dijalankan):**
- Jumlah baris: **62,900,930**
- Jumlah kolom: **34**
- Kardinalitas `Area`: **61,689**
- Total Ukuran Data: **23.29 GB**

Berdasarkan bukti empiris (>20 GB), **PySpark ditetapkan sebagai engine utama** (Lampiran lengkap di `benchmarks/PROFILING_REPORT.md`).

### 5.2 Justifikasi Komponen

- **Data Processing Engine (PySpark, dengan justifikasi eksplisit):** PySpark dipertahankan dalam proyek ini bukan diklaim sebagai "paling efisien di lokal" — pada data tunggal 25GB di satu mesin, Polars/DuckDB kemungkinan lebih cepat dan hemat memori. PySpark digunakan secara sadar untuk **mendemonstrasikan kompetensi pada ekosistem _distributed processing_** (`StructType`, _broadcast join_, _partitioned write_) yang relevan untuk peran Data Engineer, dengan _local single-node cluster_ sebagai simulasi terbatas. Keputusan ini didukung oleh ukuran data yang melebihi batas bawah (20 GB).
- **Spatial Processor (`rasterio`):** Digunakan untuk ekstraksi **tabel dimensi populasi** (14 baris) dari GeoTIFF WorldPop, dengan _clip_ langsung pada radius koordinat stasiun. Proses ini diposisikan sebagai _pre-processing_ ringan, **bukan** komponen "Spatial Big Data" — beban data besar ada pada _time-series_ kualitas air, bukan pada data spasial.
- **Object Storage (MinIO):** Digunakan untuk mendemonstrasikan **interoperabilitas Spark dengan S3 API** (membaca/menulis Parquet via `s3a://`), bukan sebagai klaim _governance_ atau _auditability_ tingkat enterprise.
- **Validasi Data (Native PySpark/Engine, pengganti Great Expectations):** Validasi skema dan kualitas data (_null rate_, duplikasi, tipe kolom) diimplementasikan menggunakan API _native_ _engine_ terpilih (`df.filter()`, `df.describe()`, pengecekan eksplisit). Pilihan ini dibuat secara sadar untuk menghindari _overhead_ dan risiko OOM dari Great Expectations pada data berskala besar di Spark.
- **Data Serving Format (Apache Parquet) dengan Schema Enforcement (pengganti "Data Contracts"):** Skema Gold Layer didefinisikan eksplisit via `StructType` dan didokumentasikan dalam `docs/DATA_DICTIONARY.md`. Istilah "Data Contracts" tidak digunakan karena tidak ada _producer-consumer_ terpisah antar tim dalam proyek ini.
- **Infrastructure & Containerization (Docker):** Membungkus _object storage_ dan _processing engine_ untuk reproduktibilitas lintas mesin.

### 5.3 Orkestrasi Ringan

Eksekusi _pipeline_ tiga lapis (Bronze → Silver → Gold) dikelola oleh orkestrator ringan **Dagster** yang menyediakan:
- Definisi _dependency_ antar-_task_ (Assets) secara eksplisit dengan pendekatan *Pythonic*.
- Visualisasi DAG eksekusi.
- _Structured logging_ terintegrasi per _task_.

Mage.ai dan Airflow secara sengaja tidak digunakan karena _overhead_ operasionalnya atau kecocokan arsitekturnya kurang proporsional untuk skala proyek ini.

---

## 6. System Architecture

- **Decision Layer:** Sebelum implementasi _layer_ Bronze, dilakukan _profiling_ dataset untuk menetapkan _engine_ pemrosesan sesuai Bagian 5.1. Keputusan ini telah didokumentasikan dan PySpark resmi dipakai.

- **Bronze Layer (Raw Data):** Data CSV kualitas air dan GeoTIFF WorldPop disalin ke format asli di _object storage_ (MinIO). Tujuan: menjaga jejak data asli untuk keperluan _debugging_ dan reproduksi ulang.

- **Silver Layer (Validation & Dimension Extraction):**
    - **Jalur Fact Table:** Data kualitas air divalidasi menggunakan fungsi _native_ PySpark (cek _null rate_, duplikasi, tipe kolom, konsistensi skema, regex stripping untuk data tersensor). Baris yang gagal dicatat ke log dan dipindahkan ke `data/rejected/`.
    - **Jalur Dimension Table:** `rasterio` mengekstrak kepadatan populasi untuk 14 stasiun, menghasilkan tabel kecil `station_id, population_density`.
    - **Join Key Investigation:** Ditemukan bahwa kolom `Area` (Figshare) memiliki kesesuaian dengan `samplingPoint.prefLabel` (WIMS EA), yang memungkinkan penarikan koordinat Lat/Lon secara akurat.
    - **Join:** Tabel fakta (tervalidasi) digabung dengan tabel dimensi (14 baris) via **Broadcast Join**, menghindari _shuffle_ pada dataset besar.

- **Gold Layer (Schema-Enforced Serving):** Hasil _join_ disimpan sebagai Parquet terpartisi berdasarkan `station_id` dan `year`, dengan skema eksplisit (`StructType`). Skema didokumentasikan di `docs/DATA_DICTIONARY.md`. Penambahan parameter radius kepadatan penduduk bersifat *scalable* (n-km).

- **Observability Backbone:** Orkestrator Dagster menjalankan setiap aset Bronze → Silver → Gold, mencatat _structured log_ (waktu eksekusi, jumlah baris masuk/lolos/ditolak) dan menampilkan DAG eksekusi.

### Struktur Repositori

```
spatial-temporal-pipeline/
|-- .env                          # Isolasi kredensial object storage
|-- docker-compose.yml            # Containerization object storage & engine
|-- requirements.txt              # Dependensi Python
|-- docs/
|   |-- DATA_DICTIONARY.md         # Definisi skema Gold Layer
|   |-- DECISION_LOG.md            # Catatan keputusan engine & alasannya
|   |-- STATUS_LOG.md              # Log progres & troubleshooting proyek
|-- src/
|   |-- config/
|   |   |-- engine_session.py      # Inisialisasi PySpark dengan resource limit (4 Cores/4GB)
|   |   |-- docs_config.md         # Log versi dependensi
|   |-- pipelines/
|   |   |-- bronze_ingest.py       # Ingesti raw CSV & GeoTIFF ke MinIO
|   |   |-- silver_validate.py     # Validasi native + ekstraksi dimensi populasi
|   |   |-- gold_serve.py          # Broadcast join, schema enforcement, partitioning
|   |-- utils/
|   |   |-- spatial_helpers.py     # Fungsi clip/mask koordinat via rasterio
|   |   |-- logger.py              # Structured logging
|-- orchestration/
|   |-- pipeline_dag.py            # Definisi Dagster Assets
|-- benchmarks/
|   |-- PROFILING_REPORT.md        # Laporan empiris ukuran & skema data raw
|   |-- profiling_script.py        # Eksekusi kalkulasi ukuran file
|   |-- BENCHMARK_REPORT.md        # Laporan komparasi runtime
|   |-- engine_comparison.py       # Skrip komparasi Pandas/Polars/DuckDB vs PySpark
```

---

## 7. Development Roadmap

**Minggu 1 — Profiling & Infrastructure (SELESAI):** Menjalankan _profiling_ dataset kualitas air (23.29GB) dan menetapkan **PySpark**. Setup Docker untuk MinIO, Dagster, dan PySpark Jupyter dengan limitasi RAM. Menyusun dokumentasi awal.

**Minggu 2 — Silver Layer (Validation & Spatial Dimension):** Implementasi ingesti data (Bronze) selesai, EDA selesai. Investigasi pemetaan stasiun (Area Figshare ↔ prefLabel WIMS) selesai. Dilanjutkan dengan koding validasi _native_ untuk data kualitas air (Regex cleansing untuk left-censored data, DropMalformed untuk column-shifting) (skema, _null rate_, duplikasi) dengan output ke `data/rejected/` untuk baris gagal. Ekstraksi tabel dimensi populasi (14 stasiun) via `rasterio`.

**Minggu 3 — Gold Layer & Schema Enforcement (SELESAI):** Implementasi _broadcast join_ tabel fakta dengan tabel dimensi, definisikan skema eksplisit (`StructType`), simpan ke Parquet terpartisi (`station_id`, `year`), dan susun `DATA_DICTIONARY.md`. Jalankan seluruh _pipeline_ melalui Dagster. Implementasi radius kepadatan penduduk yang *scalable*.

**Minggu 4 — Benchmarking & Finalization:** Jalankan `engine_comparison.py` membandingkan Pandas/Polars/DuckDB vs PySpark pada dataset aktual (sebagai pengujian hipotesis, hasil apapun valid). Susun `BENCHMARK_REPORT.md` dengan kesimpulan objektif mengenai _engine_ yang tepat untuk skala data ini.

---

## 8. Risks

**Risiko Teknis 1: OOM pada Eksekusi Spasial.** Membaca seluruh raster GeoTIFF Inggris Raya dapat menyebabkan _crash_ memori.
**Mitigasi 1:** Menggunakan `rasterio` untuk hanya memotong (_clip_) piksel dalam radius koordinat 14 stasiun — total output tabel dimensi hanya 14 baris.

**Risiko Teknis 2: Mismatch antara Engine dan Ukuran Data.** Memilih PySpark tanpa profiling dapat menghasilkan _overhead_ JVM yang tidak proporsional, atau sebaliknya memilih _engine_ ringan yang ternyata OOM pada data sebenarnya.
**Mitigasi 2:** Profiling telah dilaksanakan di Minggu 1 (membuktikan ukuran data 23.29GB), sehingga _engine_ PySpark valid digunakan secara bukti faktual.

**Risiko Teknis 3: Validasi Native Tidak Menangkap Anomali Kompleks.** Validasi ringan (`df.filter()`, _null rate_) mungkin tidak menangkap anomali skema yang lebih halus dibanding _tooling_ khusus seperti Great Expectations.
**Mitigasi 3:** Daftar aturan validasi didokumentasikan secara eksplisit dan dapat diperluas inkremental; trade-off ini diterima secara sadar demi menghindari _overhead_ GE pada Spark skala besar.

**Risiko Teknis 4 (Baru): OOM pada Host System.** Memproses 23GB data menggunakan PySpark pada laptop dengan RAM 16GB berisiko tinggi mematikan kontainer OS secara tiba-tiba (*OOMKilled*).
**Mitigasi 4:** Konfigurasi ketat di `engine_session.py` untuk mengunci Spark di maksimal 4 CPU Cores dan 4GB JVM Memory, memicu sistem *spill* Spark tanpa membahayakan RAM sisa dari OS *host*.

**Risiko Operasional: Ketergantungan pada Orkestrator & Dependensi Lingkungan.** Menambahkan Dagster menambah satu komponen _setup_ baru. Eksekusi skrip membutuhkan banyak paket sistem (seperti libgdal) yang tidak selalu ada secara default.
**Mitigasi:** Telah disediakan *custom Dockerfile* dan *docker-compose.yml* agar Dagster berdiri secara otomatis dengan *bind-mount* volume agar modifikasi aset bisa real-time tanpa *rebuild*. Semua dependensi krusial telah dibungkus ke dalam *image* via Dockerfile.dagster.

---

## 9. Success Criteria

**Kriteria 1 (Operational):** _Pipeline_ Bronze → Silver → Gold berjalan otomatis dan berurutan melalui Dagster tanpa menyebabkan OS Host OOM.

**Kriteria 2 (Data Quality):** Dataset Gold Layer mematuhi **Schema Enforcement** (`StructType`) yang terdokumentasi di `DATA_DICTIONARY.md`, hasil _broadcast join_ akurat antara data kualitas air dan kepadatan penduduk, dan terpartisi logis berdasarkan `station_id`/`year`.

**Kriteria 3 (Engineering Defense):** `BENCHMARK_REPORT.md` menyajikan hasil komparasi Pandas/Polars/DuckDB vs PySpark sebagai **pengujian hipotesis objektif**, lengkap dengan kesimpulan jujur.

**Kriteria 4 (Honesty of Claims):** Setiap istilah arsitektur dalam dokumentasi (Schema Enforcement, Broadcast Join, Dimension/Fact Table, dsb.) dapat ditelusuri langsung ke implementasi kode yang sesuai — tidak ada istilah yang digunakan tanpa dukungan implementasi nyata.mentasi nyata.