# Project Status & Configuration Log

> **Dokumen Referensi:** Log ini merekam seluruh proses inisialisasi, konfigurasi infrastruktur, resolusi masalah, dan status perkembangan proyek. Berfungsi sebagai acuan (*playbook*) untuk mereplikasi proyek serupa atau dokumentasi *open-source*.

## 1. Status Perkembangan Proyek (Minggu 1)
**Fase Saat Ini:** Minggu 1 - Profiling & Setup Infrastruktur
**Status:** **SELESAI**

**Pencapaian:**
1. **Verifikasi Dataset:** Berhasil memindai dan memverifikasi keberadaan data raw di `data/bronze/` (302 file CSV kualitas air, 21 file raster GeoTIFF WorldPop).
2. **Profiling Empiris:** Membuat dan menjalankan skrip `benchmarks/profiling_script.py`. Ditemukan bahwa dataset kualitas air memiliki ukuran **23.29 GB**, 62.9 juta baris, dan kardinalitas tinggi.
3. **Penentuan Engine (Evidence-Based):** Mengacu pada *Decision Threshold* di Blueprint, ukuran data > 20 GB memvalidasi penggunaan **PySpark** alih-alih Pandas/Polars (dicatat resmi di `DECISION_LOG.md`).
4. **Setup Infrastruktur Docker:** Menyelesaikan konfigurasi `docker-compose.yml` yang mencakup MinIO (Object Storage), PySpark Jupyter (Processing Environment), dan Dagster (Orchestrator).

---

## 2. Jurnal Permasalahan & Resolusi (Troubleshooting Log)

Selama proses konfigurasi infrastruktur Docker dan engine, ditemukan beberapa kendala yang diselesaikan secara definitif:

### Isu 1: Docker Image Tag "Not Found" (MinIO)
- **Gejala:** Eksekusi `docker-compose up -d` gagal karena tag `minio/mc:RELEASE.2024-03-30T11-45-12Z` tidak tersedia di Docker Hub.
- **Analisis:** Tim MinIO secara rutin membersihkan tag lama atau memindahkannya, sehingga bergantung pada tag lampau yang spesifik berisiko rusak seiring waktu.
- **Resolusi:** Menggunakan perintah API `curl` ke Docker Hub untuk memetakan tag terbaru yang valid, lalu memperbarui `docker-compose.yml` menggunakan tag rilis September/Agustus 2025 (`RELEASE.2025-09-07T16-13-09Z`).
- **Pelajaran:** Validasi eksistensi *image tag* sebelum mengunci *environment*.

### Isu 2: Dagster Official Image Absen
- **Gejala:** Image `dagster/dagster:1.7.5` tidak bisa ditarik (*pull access denied*).
- **Analisis:** Dagster tidak menyediakan *monolithic pre-built image* siap pakai untuk instance webserver + daemon lokal dengan nama tersebut. Praktik resminya adalah mem-*build* image dari `python-slim`.
- **Resolusi:** Membuat `Dockerfile.dagster` kustom berbasis `python:3.11-slim` yang secara eksplisit menginstal dependensi inti (`dagster==1.7.5` dan `dagster-webserver==1.7.5`), lalu mengubah konfigurasi compose menjadi `build: context: .`.

### Isu 3: Otentikasi Jupyter Notebook
- **Gejala:** Container PySpark hidup, tetapi UI Jupyter meminta token akses yang dihasilkan secara dinamis di dalam log.
- **Resolusi:** Memperbarui `docker-compose.yml` dengan menambahkan environment variable `JUPYTER_TOKEN=spatial` agar login dari *host* konsisten dan praktis.

### Isu 4: Spark UI (Port 4040) Tidak Terbuka & Engine Crash
- **Gejala:** Port 4040 memberi error `NS_ERROR_NET_EMPTY_RESPONSE`.
- **Analisis:** Spark UI bersifat *ephemeral* (hanya hidup saat `SparkSession` aktif). Ketika skrip penahan sesi dieksekusi, skrip *crash* dan mati secara diam-diam.
- **Root Cause Crash:** Terjadi ketidakcocokan (*mismatch*) versi. Container memiliki Java Spark Engine versi `3.5.0`, namun `pip install pyspark` secara default mengunduh versi `4.1.2`. Ini memicu *TypeError* pada `JavaPackage`.
- **Resolusi:** Melakukan *uninstall* PySpark v4.1.2 dan melakukan `pip install pyspark==3.5.0` agar sinkron dengan mesin Spark internal container.

### Isu 5: Mencegah OOM pada Host (Laptop 16GB RAM)
- **Gejala (Potensial):** Memproses 23 GB data berisiko tinggi menyebabkan *Out of Memory* pada OS host yang hanya memiliki 16 GB RAM.
- **Resolusi:** Pembatasan memori tidak dilakukan di level Docker Container (agar tidak terjadi *OOMKilled* secara brutal), melainkan di level **Aplikasi PySpark** melalui `engine_session.py`.
- **Konfigurasi yang Diterapkan:**
  - `spark.master("local[4]")` -> Maksimal 4 thread/core.
  - `spark.driver.memory("4g")` & `spark.executor.memory("4g")` -> Membatasi pemakaian RAM JVM hanya 4GB.
  - Opsi *Off-Heap* dihidupkan untuk *spill* ekstra, dan partisi *shuffle* disesuaikan.

---

## 3. Klarifikasi Arsitektur

- **Peran Jupyter (`spark_workspace`):** Bertindak sebagai lingkungan eksperimentasi interaktif (*sandbox*). Kode tidak ditulis menggunakan metode kuno `spark-submit`.
## 4. Pembaruan File Rujukan (Context Versioning)
Sesuai dengan instruksi `GEMINI.md`, setelah selesainya Milestone Minggu 1 dan pengambilan keputusan final terkait engine dan infrastruktur:
- Dibuat file **`UPDATE_STATUS.md`** sebagai rangkuman status terkini proyek.
- File `PROJECT_CONTEXT.md` ditingkatkan versinya menjadi **`PROJECT_CONTEXT_v0.1.md`**.
- File `Project_Blueprint_v0.2.md` ditingkatkan versinya menjadi **`Project_Blueprint_v0.3.md`**.
- Semua *checkbox* pada "Pending Tasks" untuk fase setup telah ditandai selesai (`[x]`), dan ketidakpastian (*Known Issues*) terkait infrastruktur telah dihapus.

---

## 5. Status Perkembangan Proyek (Minggu 2 - Ingestion Layer)
**Fase Saat Ini:** Minggu 2 - Bronze Ingest
**Status:** **SELESAI**

**Pencapaian:**
1. **Pemutakhiran Dependensi:** Telah ditambahkan dependensi *library* sistem (`gdal-bin`, `libgdal-dev`, `gcc`, `default-jre`) dan Python (`boto3`, `minio`, `rasterio`, `pyspark`) ke dalam `Dockerfile.dagster` agar lingkungan eksekusi memiliki semua *tools* yang dibutuhkan.
2. **Implementasi Ingest (Fail-Fast):** Menulis fungsi `ingest_to_minio` di `src/pipelines/bronze_ingest.py` yang menggunakan `boto3`. Menerapkan prinsip *idempotency* berdasarkan *content length* file dan *fail-fast error handling* untuk kegagalan lokal.
3. **Eksekusi Dagster Asset:** Mengintegrasikan `bronze_ingest.py` ke dalam Dagster lewat `@asset` di `orchestration/pipeline_dag.py`. Saat dieksekusi, sistem sukses mengunggah 326 file (data stasiun, density map) ke S3-API lokal (`myminio/bronze`).

## 6. Jurnal Permasalahan & Resolusi (Minggu 2)

### Isu 1: ModuleNotFoundError 'boto3' dalam Dagster Container
- **Gejala:** Skrip eksekusi gagal diimpor oleh Dagster code server karena modul `boto3` tidak dikenali. `docker exec dagster_ui pip list` membuktikan paket tersebut nihil.
- **Analisis:** Image Dagster secara default dibangun hanya dengan fungsionalitas inti, tanpa dependensi *data engineering*. 
- **Resolusi:** Memutakhirkan `Dockerfile.dagster` agar menjalankan `pip install boto3 minio rasterio pyspark pandas` serta menyertakan paket *system-level* untuk C++ kompilasi (`libgdal-dev` dll). Me-*restart* dan me-*rebuild* layanan `dagster-webserver` dan `dagster-daemon`.

### Isu 2: Error "Executable file not found in $PATH" untuk Java
- **Gejala:** Memeriksa keberadaan Java pada `dagster_daemon` memberikan kode gagal. Hal ini dikarenakan *base image* Python-slim tidak menyertakan JRE secara *default*.
- **Resolusi:** Mengintegrasikan `apt-get install -y default-jre` ke dalam `Dockerfile.dagster` agar *container* mampu menjembatani eksekusi PySpark ke depannya jika *engine* digunakan di *asset* Silver.

## 7. Pembaruan File Rujukan (Minggu 2)
Sesuai prosedur pelaporan:
- Progres log Minggu 2 ditambahkan di **`UPDATE_STATUS.md`**.
- File `PROJECT_CONTEXT_v0.1.md` diperbarui menjadi **`PROJECT_CONTEXT_v0.2.md`**.
- File `Project_Blueprint_v0.3.md` diperbarui menjadi **`Project_Blueprint_v0.4.md`**.