# Decision Log

> Dokumen ini mencatat setiap keputusan teknis/arsitektural yang berdampak signifikan pada pipeline, beserta justifikasi (berbasis bukti empiris) di balik keputusan tersebut.

## 1. Pemilihan Processing Engine Utama
- **Date:** June 12, 2026
- **Status:** **DIPUTUSKAN**
- **Decision:** Menggunakan **Apache Spark (PySpark)** sebagai engine pemrosesan utama untuk transformasi Bronze → Silver → Gold.
- **Context/Evidence:** Merujuk pada komitmen "*Evidence-based Engineering*" di MVP, pemilihan engine ditentukan setelah data ditarik dan diprofiling. Berdasarkan `benchmarks/PROFILING_REPORT.md` yang dieksekusi pada data lokal `data/bronze/`:
  - Ukuran dataset Kualitas Air mencapai **23.29 GB**.
  - Total baris: 62.9 Juta.
- **Justification:** Ambang batas *threshold* pada Blueprint menetapkan bahwa data di atas 20 GB membutuhkan/membenarkan penggunaan ekosistem distributed/PySpark. Karena data aktual melebihi threshold tersebut, penggunaan PySpark dianggap valid secara fungsional dan operasional, alih-alih menggunakan Pandas (yang rentan OOM pada mesin lokal tunggal) atau sekadar memilih Spark tanpa bukti dataset besar.

---

*(Catatan: Keputusan mengenai komponen infrastruktur lainnya akan ditambahkan pada entri berikutnya).*

## 2. Pemilihan Orkestrator
- **Date:** June 12, 2026
- **Status:** **DIPUTUSKAN**
- **Decision:** Menggunakan **Dagster** sebagai orkestrator pipeline.
- **Justification:** Dagster dipilih dibandingkan Mage.ai karena pendekatannya yang lebih *Pythonic*, deklarasi aset/alur (software-defined assets) yang sangat cocok dengan skrip Data Engineering murni, serta kemudahan integrasi dan visualisasi log secara lokal melalui Docker.

## 3. Infrastruktur Docker (Base Images)
- **Date:** June 12, 2026
- **Status:** **DIPUTUSKAN**
- **Decision:** Menggunakan *stable tags* spesifik untuk setiap image Docker, bukan `latest`.
  - MinIO: `minio/minio:RELEASE.2024-03-30T09-41-56Z`
  - PySpark: `jupyter/pyspark-notebook:spark-3.5.0`
  - Dagster: `dagster/dagster:1.7.5`
- **Justification:** Mencegah isu *breaking changes* tak terduga dan menjamin *reproducibility* secara absolut sesuai dengan best practices engineering.