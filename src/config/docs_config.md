# Config & Dependencies Documentation

> Dokumen ini berisi ringkasan *dependencies* (paket dan sistem) yang digunakan dalam proyek ini, spesifikasi versinya, dan alasan pemilihan versi tersebut.

## 1. Docker Base Images

| Komponen | Image & Tag | Alasan Pemilihan |
| :--- | :--- | :--- |
| **Object Storage (MinIO)** | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | Menggunakan tag rilis stabil terbaru pasca-pemeriksaan di Docker Hub karena tag lawas tahun 2024 sudah dihapus oleh *maintainer*. |
| **MinIO Client** | `minio/mc:RELEASE.2025-08-13T08-35-41Z` | Sinkron dengan versi MinIO Server untuk menjalankan skrip inisiasi *bucket* (bronze, silver, gold, rejected). |
| **Processing (PySpark)** | `jupyter/pyspark-notebook:spark-3.5.0` | Menyediakan lingkungan Spark engine versi 3.5.0 berbasis Python 3.11. Digunakan sebagai *sandbox* interaktif sekaligus runtime dependensi untuk *host*. |
| **Orchestrator (Dagster)** | Custom build via `python:3.11-slim` | Image resmi Dagster tidak *standalone*. Dibuat *Dockerfile.dagster* khusus berbasis OS yang sangat ringan (slim) untuk menjaga ukuran infrastruktur efisien. |

## 2. Python Dependencies (Pipeline & Orchestration)

Tercatat di `requirements.txt` dan diinstal di dalam environment eksekusi.

| Package | Version | Alasan / Catatan Kritis |
| :--- | :--- | :--- |
| `pyspark` | `==3.5.0` | **KRITIS:** Versi ini **wajib** sama dengan versi `APACHE_SPARK_VERSION` di dalam container. Menggunakan versi terbaru (mis. 4.x) akan menyebabkan *TypeError (JavaPackage)* dan men-*crash*-kan pipeline. |
| `dagster` | `==1.7.5` | Versi stabil dari rilis minor 1.7. Dagster digunakan sebagai pengganti Airflow yang lebih *Pythonic* dan ringan untuk mesin lokal. |
| `dagster-webserver`| `==1.7.5` | Modul wajib penyedia UI untuk memantau DAG Dagster di port 3000. Harus sinkron dengan versi core Dagster. |
| `pandas` | `*` | Digunakan untuk profiling tahap awal dan eksplorasi ukuran file CSV secara cepat tanpa perlu membangkitkan JVM Spark. |

## 3. Spark Session Configurations (Resource Limits)

Diatur di dalam `src/config/engine_session.py` untuk mengamankan OS *host* (RAM 16GB) dari ancaman OOM:

- **Resource Limits:**
  - `master("local[4]")`: Membatasi paralelisme JVM maksimal 4 core.
  - `spark.driver.memory = 4g` & `spark.executor.memory = 4g`: Mengunci alokasi memori Spark agar tidak melebihi 4GB. Sisa memori akan di-*spill* secara otomatis ke *disk*.
- **S3 / MinIO Integration:**
  - `spark.jars.packages = org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262`: Paket Java wajib agar Spark bisa membaca URL S3 (`s3a://`).
  - *Path Style Access*: Diaktifkan `true` untuk kompatibilitas protokol MinIO lokal.