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