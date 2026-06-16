# Data Dictionary (Gold Layer)

Dokumen ini mendefinisikan skema secara eksplisit (*Schema Enforcement*) yang diterapkan pada format penyimpanan data `Parquet` di *Gold Layer* proyek "Spatial-Temporal Data Pipeline". 
Proyek ini menghasilkan dua dataset utama di *Gold Layer*:
1. **Gold England (Pivot Table):** `gold_england_water_quality`
2. **Gold WIMS (Transactional Table):** `gold_wims_water_quality`

---

## 1. Skema Dimension Table (Spasial)
*Tabel ini diintegrasikan ke dalam tabel-tabel fakta di atas melalui metode Broadcast Join.*

| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `station_id` | String | Kode identifikasi stasiun (WIMS `samplingPoint.notation`). |
| `area_name` | String | Nama area (WIMS `prefLabel` / Figshare `Area`). |
| `latitude` | Float | Koordinat Lat (WGS84). |
| `longitude` | Float | Koordinat Lon (WGS84). |
| `population_density` | Float | Kepadatan penduduk (radius dinamis) berdasarkan ekstraksi *raster* WorldPop. |

---

## 2. Skema Fact Table: Gold England (Pivot)
**Lokasi Penyimpanan:** `s3a://gold/england_water_quality`
**Partisi:** `station_id`, `year`

Tabel ini mewakili data kualitas air yang telah di-*pivot* (satu baris merepresentasikan berbagai parameter dalam satu tanggal), diperkaya dengan atribut geospasial dari stasiun.

| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `station_id` | String | **[Partition Key]** Kode stasiun WIMS EA yang berhasil dipetakan ke area bersangkutan. |
| `year` | Integer | **[Partition Key]** Tahun observasi (diekstrak dari `Date`). |
| `Country` | String | Nama negara asal observasi. |
| `Area` | String | Nama area atau stasiun yang digunakan sebagai Join Key. |
| `Waterbody_Type` | String | Klasifikasi sumber badan air permukaan. |
| `Date` | String | Tanggal koleksi data (`DD-MM-YYYY`). |
| `Ammonia_mg_l` | Float | Konsentrasi kadar amonia bebas terlarut (mg/L). |
| `Biochemical_Oxygen_Demand_mg_l`| Float | Konsentrasi kebutuhan oksigen biokimia (mg/L). |
| `Dissolved_Oxygen_mg_l` | Float | Kadar Oksigen Terlarut bebas di dalam air (mg/L). |
| `Orthophosphate_mg_l` | Float | Konsentrasi senyawa ortofosfat (mg/L). |
| `pH_ph_units` | Float | Tingkat keasaman (unit pH). |
| `Temperature_cel` | Float | Suhu air saat pengukuran (Celsius). |
| `Nitrogen_mg_l` | Float | Kadar Nitrogen Total (mg/L). |
| `Nitrate_mg_l` | Float | Kadar senyawa nitrat terlarut (mg/L). |
| `CCME_Values` | Float | Nilai indeks kualitas air CCME (skala 0-100). |
| `CCME_WQI` | String | Klasifikasi kualitas air deskriptif CCME (e.g. Excellent, Poor). |
| `population_density` | Float | Kepadatan populasi dalam radius *n-km* sekitar stasiun. |

---

## 3. Skema Fact Table: Gold WIMS (Transactional)
**Lokasi Penyimpanan:** `s3a://gold/wims_water_quality`
**Partisi:** `station_id`, `year`

Tabel log transaksional WIMS (>60 Juta observasi mentah sebelum difilter). Setiap baris mengukur satu jenis `determinand` secara spesifik, diperkaya dengan dimensi spasial.

| Kolom | Tipe Data | Deskripsi |
| :--- | :--- | :--- |
| `station_id` | String | **[Partition Key]** Kode identifikasi alfanumerik spesifik titik sampel. |
| `year` | Integer | **[Partition Key]** Tahun observasi (diekstrak dari `phenomenonTime`). |
| `id` | String | URI URI *Linked Open Data* (Primary Key WIMS). |
| `area_name` | String | Nama wilayah preferensi (*prefLabel*). |
| `samplingPoint_samplingPointStatus`| String | Status administratif titik sampel (e.g., OPEN). |
| `samplingPoint_samplingPointType` | String | Klasifikasi fungsional dari badan air. |
| `phenomenonTime` | String | Timestamp aktual observasi/koleksi di lapangan. |
| `samplingPurpose` | String | Tujuan atau mandat pengambilan sampel air (e.g., COMPLIANCE). |
| `sampleMaterialType` | String | Tipe material sampel (e.g., FRESHWATER, EFFLUENT). |
| `determinand_notation` | String | Kode *determinand* EA. |
| `determinand_prefLabel` | String | Label tekstual untuk parameter yang sedang diukur. |
| `result_clean` | Float | Hasil kuantitatif bersih dari *left-censored data* (sudah di-strip karakter `<`/`>`). |
| `unit` | String | Satuan metrik parameter. |
| `population_density` | Float | Kepadatan populasi spasial yang disesuaikan melalui konfigurasi radius dinamis. |

---

> **Schema Enforcement Note:**
> PySpark memaksakan skema tersebut menggunakan `StructType` yang dikonfigurasi saat pembuatan `DataFrame`. Baris yang menyimpang dari struktur ini dalam eksekusi akan tertolak, menjamin konsistensi yang sangat tinggi pada lapisan ML/Serving.
