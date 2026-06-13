## **Analisis Teknis Skema Data Water Quality Archive Inggris Raya** 

Arsip Kualitas Air (Water Quality Archive) yang dikelola oleh Environment Agency (EA) Inggris Raya merupakan salah satu repositori data lingkungan hidup terbesar yang mencakup hasil pemantauan kualitas air permukaan, air tanah, dan limbah di seluruh wilayah Inggris.[1] Secara historis, infrastruktur penyimpanan data ini bersumber dari Water Information Management System (WIMS), sebuah sistem manajemen informasi internal yang digunakan oleh EA untuk mengelola sampel lingkungan dan data kepatuhan izin pembuangan limbah.[3] Sistem ini telah mengalami evolusi teknologi yang signifikan, di mana catatan katalog data lama telah dipensiunkan dan digantikan secara resmi oleh Water Quality Explorer 

(https://environment.data.gov.uk/dataset/8034d47a-ba8a-4978-aca0-bd5d6e870536).[2] Selain itu, transisi teknologi penting terjadi pada akhir tahun 2025, di mana API lama resmi dihentikan fungsinya pada Desember 2025 dan digantikan oleh arsitektur API baru yang aktif penuh per Februari 2026 di bawah pengelolaan Defra Data Services Platform.[1] Arsip ini melacak lebih dari 72 juta observasi analitik yang diekstrak dari sekitar 5 juta sampel pada lebih dari 58.000 titik pemantauan sejak tahun 2000.[1] Data disajikan dalam format Linked Open Data menggunakan representasi terstruktur seperti RDF, JSON, dan CSV untuk memfasilitasi integrasi lintas sistem pemerintahan dan publik.[1] 

## **Spesifikasi Kamus Data dan Definisi Kolom CSV** 

Struktur berkas .csv yang dihasilkan oleh sistem Water Quality Archive mengadopsi model data berorientasi objek yang meratakan (flattening) struktur hierarki Linked Data ke dalam bentuk tabel dua dimensi.[1] Setiap baris dalam berkas tersebut mewakili satu hasil observasi atau pengukuran analitik spesifik dari suatu sampel air.[2] 

Tabel berikut menyajikan definisi teknis komprehensif, tipe data, serta nilai contoh dari ketujuh belas kolom yang terdapat dalam berkas data tersebut: 

|**Nama Kolom di**<br>**CSV**|**Tipe Data**|**Deskripsi Teknis**<br>**dan Penafsiran**<br>**Konseptual**|**Contoh Nilai**<br>**Lapangan**|
|---|---|---|---|
|id|String|URI (_Uniform_<br>_Resource Identifier_)<br>unik yang bertindak<br>sebagai<br>pengidentifikasi<br>global dalam<br>arsitektur_Linked_|https://<br>environment.data.g<br>ov.uk/water-<br>quality/sampling-<br>point/AN-131660/<br>sample/2127272/<br>observation/01118|



|||_Open Data_. Kolom<br>ini menunjuk secara<br>langsung ke entitas<br>observasi spesifik di<br>peladen web EA.3||
|---|---|---|---|
|samplingPoint.notat<br>ion|String|Kode identifikasi<br>alfanumerik pendek<br>dan unik yang<br>digunakan oleh EA<br>untuk merujuk pada<br>titik pengambilan<br>sampel tertentu<br>tanpa ambiguitas.7|AN-1316608|
|samplingPoint.prefL<br>abel|String|Nama lokasi atau<br>label tekstual yang<br>disukai untuk<br>mempermudah<br>identifikasi manusia<br>terhadap posisi<br>geografis titik<br>sampel.7|"THE PRIORY,<br>LITTLE<br>WYMONDLEY"8|
|samplingPoint.longit<br>ude|String|Koordinat bujur<br>geografis titik<br>sampel<br>berdasarkan datum<br>geodesi standar<br>global WGS84.8|-0.22748|
|samplingPoint.latitu<br>de|String|Koordinat lintang<br>geografis titik<br>sampel<br>berdasarkan datum<br>geodesi standar<br>global WGS84.8|51.93598|
|samplingPoint.regio<br>n|String|Wilayah<br>administratif<br>lingkungan tingkat<br>makro di Inggris<br>tempat lokasi titik<br>pemantauan<br>berada.7|Anglian8|
|samplingPoint.area|String|Pembagian wilayah<br>operasional tingkat<br>menengah di<br>bawah struktur<br>organisasi EA,<br>biasanya mencakup<br>daerah aliran<br>sungai utama.8|ANGLIAN - CAMBS<br>AND<br>BEDFORDSHIRE8|
|samplingPoint.subA<br>rea|String|Sub-divisi<br>operasional terkecil<br>yang merujuk pada<br>unit kerja atau tim<br>lapangan lokal yang<br>bertanggung jawab<br>langsung atas<br>pemeliharaan<br>situs.8|BRAMPTON TEAM<br>SUB AREA8|
|samplingPoint.sam<br>plingPointStatus|String|Status administratif<br>operasional titik<br>sampel, yang<br>menunjukkan<br>apakah titik tersebut<br>aktif digunakan atau<br>telah ditutup.8|OPEN8|
|samplingPoint.sam<br>plingPointType|String|Klasifikasi<br>fungsional dari<br>badan air atau jenis<br>outlet limpasan<br>tempat sampel<br>tersebut diambil.3|SEWAGE<br>DISCHARGES -<br>FINAL/TREATED<br>EFFLUENT - NOT<br>WATER COMPANY<br>8|
|phenomenonTime|String|Cap waktu<br>(_timestamp_) standar<br>ISO 8601 yang<br>merekam kapan<br>sampel fisik<br>tersebut diambil<br>dari lingkungan <br>alamiahnya.7|2026-03-18<br>13:32:008|
|samplingPurpose|String|Mandat kebijakan<br>atau dasar hukum<br>pengambilan<br>sampel, yang<br>membedakan<br>pengawasan<br>regulasi dari<br>pemantauan<br>ekologis rutin.8|COMPLIANCE<br>AUDIT (PERMIT)8|
|sampleMaterialTyp<br>e|String|Karakteristik fisik<br>dan jenis matriks<br>bahan kimia dari<br>medium yang<br>dijadikan sampel<br>analitik.8|FINAL SEWAGE<br>EFFLUENT8|
|determinand.notatio<br>n|String|Kode numerik<br>internal (biasanya<br>empat digit) yang<br>ditetapkan oleh EA<br>untuk<br>mengidentifikasi zat<br>atau parameter fisik<br>yang diukur.11|1118|
|determinand.prefLa<br>bel|String|Nama deskriptif<br>standar dari zat,<br>senyawa kimia,<br>atau properti fisik<br>lingkungan yang<br>dianalisis dalam<br>sampel.7|Ammoniacal<br>Nitrogen as N8|
|result|String|Hasil kuantitatif<br>atau kualitatif dari<br>proses pengujian<br>analitik laboratorium<br>atau pengukuran<br>langsung di<br>lapangan.7|6.98|
|unit|String|Satuan metrik<br>standar yang<br>digunakan untuk<br>mengukur dan<br>mengekspresikan<br>nilai dari parameter<br>terkait.7|MILLIGRAM PER<br>LITRE8||



## **Analisis Hubungan Spasial dan Hierarki Administratif** 

Pengelolaan data lingkungan di Inggris sangat bergantung pada struktur administratif regional untuk menyalurkan tanggung jawab pengawasan dari tingkat pusat ke unit operasional lapangan.[4] Pada data titik sampel (samplingPoint), relasi logis di antara kolom geografis membentuk suatu rantai dependensi hirarkis yang kaku: 

**Region → Area → Sub-Area → Sampling Point**

Sebagai contoh, wilayah administratif makro Anglian membawahi wilayah operasional tingkat menengah ANGLIAN - CAMBS AND BEDFORDSHIRE.[8] Wilayah tingkat menengah ini kemudian dibagi lagi ke dalam unit taktis terkecil seperti BRAMPTON TEAM SUB AREA yang bertanggung jawab atas titik fisik riil seperti AN-131660 dengan deskripsi lokasi "THE PRIORY, LITTLE WYMONDLEY".[8] Koordinat spasial yang tersimpan pada longitude dan latitude mengunci lokasi tersebut dalam ruang geografis global menggunakan proyeksi WGS84, yang memungkinkan integrasi langsung ke dalam sistem informasi geografis (GIS) korporat maupun publik.[8] 

Status operasional yang dinyatakan dalam samplingPointStatus (misalnya OPEN) memastikan keandalan data historis, di mana pengguna data dapat segera mengetahui apakah titik pemantauan tersebut masih aktif mengirimkan data terkini atau merupakan situs warisan yang sudah tidak dipantau lagi.[8] Hal ini sangat penting untuk pemodelan tren jangka panjang guna menghindari bias spasial akibat penghentian pemantauan secara mendadak.[2] 

## **Keterkaitan Prosedural dan Klasifikasi Sampel** 

Skema data ini menunjukkan pola kausalitas yang kuat antara jenis titik sampel, tujuan pengambilan sampel, dan material yang diuji.[8] Hubungan ini mencerminkan protokol operasional yang diterapkan oleh para inspektur lapangan Environment Agency.[13] Tabel di bawah memetakan bagaimana tujuan pemantauan berkorelasi secara langsung dengan tipe material sampel dan titik pengambilan sampel: 

|**Tipe Titik Sampel**<br>**(samplingPointTyp**<br>**e)**|**Tujuan**<br>**Pengambilan**<br>**(samplingPurpose**<br>**)**|**Jenis Material**<br>**Sampel**<br>**(sampleMaterialTy**<br>**pe)**|**Paradigma**<br>**Pemantauan**<br>**Lingkungan**|
|---|---|---|---|
|SEWAGE<br>DISCHARGES -<br>FINAL/TREATED<br>EFFLUENT...8|COMPLIANCE<br>AUDIT (PERMIT)8|FINAL SEWAGE<br>EFFLUENT8|Pengawasan<br>kepatuhan hukum<br>industri dan<br>instalasi<br>pembuangan<br>limbah swasta.4|
|TRADE<br>DISCHARGES -<br>SITE DRAINAGE...<br>8|COMPLIANCE<br>AUDIT (PERMIT)8|ANY TRADE<br>EFFLUENT8|Pemantauan<br>limpasan air<br>permukaan<br>terkontaminasi dari<br>area pabrik.8|
|FRESHWATER -<br>RIVERS3|MONITORING<br>(NATIONAL<br>AGENCY POLICY)<br>8|RIVER / RUNNING<br>SURFACE WATER<br>8|Evaluasi kualitas air<br>sungai alami untuk<br>kebijakan<br>lingkungan<br>nasional.15|



Dalam kasus audit kepatuhan (COMPLIANCE AUDIT (PERMIT)), pengambilan sampel difokuskan pada pembuangan limbah aktif, baik berupa limbah domestik terolah (FINAL SEWAGE EFFLUENT) maupun limbah industri perdagangan (ANY TRADE EFFLUENT).[4] Pemantauan ini bertujuan untuk membuktikan secara hukum apakah pemegang izin pembuangan (consent/permit) mematuhi batasan konsentrasi zat pencemar yang ditetapkan dalam regulasi.[4] 

Sebaliknya, pemantauan kebijakan nasional (MONITORING (NATIONAL AGENCY POLICY)) berfokus pada kesehatan sungai secara ekologis.[13] Sampel yang diambil adalah air sungai alami (RIVER / RUNNING SURFACE WATER) dengan tipe titik pemantauan air tawar (FRESHWATER - RIVERS).[8] Analisis ini menunjukkan bahwa data WIMS mengintegrasikan pengawasan sumber polusi titik ( _point source pollution_ ) dan pemantauan kualitas air ambien lingkungan secara simultan dalam satu platform data tunggal.[17] 

## **Signifikansi Teori Observasi dalam Arsitektur Data** 

Kolom id dan phenomenonTime merepresentasikan penerapan prinsip Linked Data dan standar ISO 19156 (Observations and Measurements).[4] Kolom id tidak sekadar berfungsi sebagai kunci primer acak dalam basis data relasional biasa, melainkan sebuah URI HTTP yang jika diakses akan mengembalikan representasi metadata kaya dari observasi tersebut dalam berbagai format pertukaran data.[1] 

Sementara itu, penggunaan istilah phenomenonTime (bukan sekadar "tanggal_sampling") memiliki landasan teoretis yang kuat dalam metrologi lingkungan[12] : 

1. **Waktu Kejadian Riil (** _**Phenomenon Time**_ **)** : Kolom ini mencatat waktu fisik yang sesungguhnya terjadi di alam saat sampel diambil dari ekosistem.[7] Waktu ini krusial karena keadaan fisik air (seperti suhu atau kadar oksigen terlarut) mengalami fluktuasi cepat tergantung pada siklus harian matahari.[8] 

2. **Waktu Pelaporan (** _**Result Time**_ **)** : Waktu yang merekam penyelesaian analisis sampel di laboratorium.[12] Rentang waktu antara phenomenonTime dan resultTime sering kali memiliki jeda beberapa hari akibat proses logistik pengiriman sampel ke laboratorium pusat milik EA serta antrean pengujian analitik.[2] 

Dengan memisahkan kedua dimensi waktu ini secara eksplisit, para peneliti lingkungan dapat memodelkan dinamika kualitas air secara tepat tanpa terdistorsi oleh penundaan administratif di laboratorium penguji.[2] 

## **Analisis Kimia, Metrologi, dan Penanganan Sensor Terkiri** 

Representasi parameter kimia dalam skema data ini dikelola melalui sistem klasifikasi terstandar.[13] Di dalam basis data Water Quality Archive, terdapat lebih dari 7.600 jenis parameter pengujian yang disebut sebagai "determinand".[3] Kolom determinand.notation menyimpan kode identifikasi numerik unik dari determinand tersebut, sedangkan determinand.prefLabel menyimpan deskripsi tekstual standarnya.[7] 

Tabel berikut menunjukkan pola pemetaan metrologi dari beberapa determinand utama yang umum ditemui dalam pemantauan kualitas air permukaan dan limbah: 

|**Kode Analit**<br>**(determinand.nota**<br>**tion)**|**Deskripsi Teknis**<br>**(determinand.pref**<br>**Label)**|**Satuan Metrik**<br>**(unit)**|**Relevansi**<br>**Lingkungan**|
|---|---|---|---|
|0061|pH8|PH UNITS8|Mengukur tingkat<br>keasaman atau<br>kebasaan air<br>permukaan.8|
|0076|Temperature of<br>Water8|CELSIUS8|Mengukur suhu air<br>yang memengaruhi<br>kelarutan oksigen.8|
|0077|Conductivity at 25 C<br>8|MICROSIEMENS<br>PER CENTIMETRE<br>8|Proksi untuk total<br>padatan terlarut dan<br>salinitas air.8|
|0111|Ammoniacal<br>Nitrogen as N8|MILLIGRAM PER<br>LITRE8|Indikator utama<br>pencemaran limbah<br>domestik dan<br>pertanian.8|
|0180|Orthophosphate,<br>reactive as P8|MILLIGRAM PER<br>LITRE8|Nutrisi pembatas<br>yang dapat memicu<br>eutrofikasi badan<br>air.8|
|2921|Perfluoro-3-<br>methoxypropanoic<br>acid8|MICROGRAM PER<br>LITRE8|Pengukuran<br>kontaminan<br>mikroorganik baru<br>(senyawa PFAS).8|



Salah satu tantangan terbesar dalam pemrosesan data kualitas air adalah penafsiran kolom result yang bertipe data String.[8] Penatapan tipe data tekstual ini sangat penting untuk menangani kompleksitas batas deteksi analitik instrumen laboratorium, yang secara teoretis dikenal sebagai penyensoran data terkiri ( _left-censored data_ ).[8] 

Ketika konsentrasi analit sangat rendah (seperti senyawa PFAS atau mikro-polutan organik), instrumen laboratorium tidak mampu mengukur nilai numerik pastinya melainkan hanya dapat memastikan bahwa konsentrasi zat tersebut berada di bawah batas pelaporan metodologi (Limit of Quantitation/LOQ).[8] Kondisi ini dilaporkan dalam bentuk string seperti <0.0005.[8] 

Selain itu, jika terjadi hambatan fisik di lapangan yang menyebabkan pengukuran tidak dapat dilakukan (misalnya tidak ada aliran air di saluran keluar industri), kolom result akan merekam pesan kegagalan operasional secara kualitatif seperti No flow/discharge at sampling point dengan kolom unit yang ditandai khusus sebagai Coded Result.[8] Para ilmuwan data lingkungan harus melakukan pembersihan data ( _data cleansing_ ) yang hati-hati sebelum menggunakan kolom result dalam kalkulasi numerik guna menghindari kesalahan konversi tipe data ( _typecasting errors_ ) dalam alur pipa data ( _ETL pipelines_ ) mereka.[24] 

## **Aksesibilitas Data dan Implementasi Praktis Arsitektur** 

## **API** 

Untuk mengonsumsi data dari sistem Water Quality Archive yang diperbarui ini, para analis data profesional disarankan menggunakan mekanisme permintaan HTTP secara langsung melalui endpoint observasi terstandar.[7] 

Langkah operasional pengunduhan data secara programmatic menggunakan pustaka pengolahan data ataupun fungsionalitas impor eksternal (seperti Power Query pada Microsoft Excel) dirumuskan melalui pembentukan URL terstruktur sebagai berikut[7] : 

`https://environment.data.gov.uk/water-quality/sampling-point/<KODE-TITIK-SAMPEL>/ observation?dateFrom=<TANGGAL-MULAI>&dateTo=<TANGGAL-SELESAI>&limit=250` 

Sebagai contoh spesifik, untuk mengunduh riwayat observasi dari stasiun pemantauan di wilayah Anglian, pemanggilan URL harus menggunakan kode notasi stasiun yang valid.[7] Salah satu aspek teknis paling krusial yang wajib disertakan dalam header permintaan HTTP ( _HTTP Request Header_ ) untuk berinteraksi dengan API versi 2026 adalah[7] : 

Accept: text/csv 

Konfigurasi header ini memaksa peladen Linked Data EA untuk melakukan serialisasi instan dari format grafik internal mereka menjadi dokumen tabel terstruktur.[1] Tanpa adanya penyertaan header ini secara eksplisit, peladen secara default akan mengembalikan dokumen berbasis JSON-LD atau RDF yang memerlukan pemrosesan parsing tambahan yang jauh lebih kompleks.[1] Pembaruan arsitektur API 2026 ini memberikan kontrol penuh bagi para profesional lingkungan untuk menarik data deret waktu berkualitas tinggi guna mendukung analisis ekologis, audit kepatuhan industri, serta pemodelan beban pencemaran pada skala daerah aliran sungai secara akurat dan real-time.[7] 

## **Works cited** 

1. Water Quality - API Catalogue, accessed June 14, 2026, - 

https://www.api.gov.uk/ea/water quality/ 

2. Water Quality Explorer - Defra Data Services Platform, accessed June 14, 2026, https://environment.data.gov.uk/dataset/8034d47a-ba8a-4978-aca0bd5d6e870536 

3. EXERCISE: INTRODUCTION TO ACCESSING AND USING THE ENVIRONMENT AGENCY'S WATER QUALITY ARCHIVE, accessed June 14, 2026, 

   - 

   - https://catchmentbasedapproach.org/wp content/uploads/2021/04/WQ_tc_Exercis e_OpenWIMS_Participants_V1_Rev1.pdf 

4. CLEAR Info: Populating INSPIRE spatial objects from WIMS Data - GOV.UK, accessed June 14, 2026, https://assets.publishing.service.gov.uk/media/5a7cfd1c40f0b60a7f1a997d/ Action_2.2_Annex_1_Consultant_Study.pdf 

5. Restoring Intertidal Habitats at Chyngton Brooks Ground Investigation - Interpretative Report - East Sussex County Council, accessed June 14, 2026, https://apps.eastsussex.gov.uk/environment/planning/applications/register/ documents/datawright%20saved%20documents/scannedinfo/planning/escc-2025001-cb/8.%20gi%20interpretative%20report_redacted.pdf 

6. Water Quality Archive - Defra Data Services Platform, accessed June 14, 2026, https://environment.data.gov.uk/dataset/2499766e-b15a-4f85-a7585702de693723 

7. Getting EA Water Quality Data - UPDATED for New API (2026 ..., accessed June 14, 2026, https://camvalleyforum.uk/wp-content/uploads/2026/02/How-todownload-data-from-new-EA-WQ-API-into-Excel-Feb2026.pdf 

8. sampel-station.csv 

9. API Documentation - Defra Data Services Platform, accessed June 14, 2026, 

## https://environment.data.gov.uk/hydrology/doc/reference 

10. Water quality - Collection - National Data Library, accessed June 14, 2026, - 

https://www.data.gov.uk/collections/environment/water quality 

11. EXERCISE: INTRODUCTION TO ACCESSING AND USING THE ENVIRONMENT AGENCY'S WATER QUALITY ARCHIVE, accessed June 14, - - 

2026, https://catchmentbasedapproach.org/wp content/uploads/2018/08/Water Quality-OpenWIMS-Exercise-Answers.pdf 

12. Applying OGC Sensor Web Enablement Standards to Develop a TDR MultiFunctional Measurement Model - PMC, accessed June 14, 2026, https://pmc.ncbi.nlm.nih.gov/articles/PMC6806113/ 

13. Water Quality Dashboard - ArcGIS StoryMaps, accessed June 14, 2026, https://storymaps.arcgis.com/stories/d92224d0cf1944a6826f770915cf2f9b 

14. How do I use the Water Quality Explorer (WQE)? - Defra Data Services Platform, accessed June 14, 2026, https://environment.data.gov.uk/support/faqs/275879249/1082097669 

15. Getting the full picture: Assessing the complementarity of citizen science and agency monitoring data | PLOS One - Research journals, accessed June 14, 2026, https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0188507 

16. Water Quality Planning Definitions | DEQ - ADEQ, accessed June 14, 2026, https://adeq.state.ar.us/water/resources/definitions.aspx 

17. Understanding Geochemical Fluxes Between Groundwater and Surface Water: Scoping Report - GOV.UK, accessed June 14, 2026, - 

https://assets.publishing.service.gov.uk/media/5a7c2763e5274a1f5cc76208/sp2 260-5-tr-e-e.pdf 

18. 6.3.2 - SDG indicator metadata, accessed June 14, 2026, https://unstats.un.org/sdgs/metadata/files/Metadata-06-03-02.pdf 

19. rnrfa: An R package to Retrieve, Filter and Visualize Data from the UK National River Flow Archive, accessed June 14, 2026, https://journal.r-project.org/articles/RJ-2016-036/RJ-2016-036.pdf 

20. Development of a Methodology for Selection of Determinand Suites and Sampling Frequency for Groundwater Quality Monitoring - GOV.UK, accessed June 14, 2026, https://assets.publishing.service.gov.uk/media/5a7c75e4ed915d6969f45060/ scho0303bitu-e-e.pdf 

21. STEP-BY-STEP MONITORING METHODOLOGY FOR INDICATOR 6.3.2, accessed June 14, 2026, https://wesr.unep.org/media/docs/projects/step_by_step_methodology_632_revisi on_final.pdf 

22. Nutrient Monitoring on the Rivers Test, Itchen and Meon - Chilbolton Parish - 

Council, accessed June 14, 2026, https://www.chilboltonparish.gov.uk/wp content/uploads/sites/115/2026/02/202425-WQMN-Report-Test-Itchen-Meon.pdf 

23. STOCKTAKE OF DATA QUALITY CODE AND METADATA USAGE IN REGIONAL COUNCIL WATER QUALITY DATASETS - Ministry for the Environment, accessed June 14, 2026, 

https://environment.govt.nz/assets/publications/Freshwater/stocktake-of-dataquality-code-and-metadata-usage-in-regional-council-water-quality-datasets.pdf 

24. Water Quality Performance Commitment Review | Ofwat, accessed June 14, - - - 2026, https://www.ofwat.gov.uk/wp content/uploads/2023/06/Water Quality Performance-Commitment-Review-Jacobs-Rev3.05.pdf 

