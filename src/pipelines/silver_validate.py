import os
import sys
import logging
import time
from pyspark.sql import functions as F
from pyspark.sql.types import FloatType, StructType, StructField, StringType

# Konfigurasi logging standar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SilverValidate")

# Menambahkan path ke sys.path untuk absolute import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.engine_session import get_spark_session
from src.utils.spatial_helpers import extract_population_density

def run_silver_validation():
    start_time = time.time()
    logger.info("Membangun Spark Session...")
    spark = get_spark_session("SilverLayer")
    
    total_rejected = 0
    total_valid = 0
    
    # ==============================================================================
    # 1. Jalur Fact Table A: Baca data Kualitas Air (Country-Wise Data / England)
    # ==============================================================================
    logger.info("Membaca raw data England (Country-Wise Data) dari s3a://bronze/Country-Wise Data/England_dataset.csv...")
    england_df = spark.read.option("header", "true").csv("s3a://bronze/Country-Wise Data/England_dataset.csv")
    eng_raw_count = england_df.count()
    logger.info(f"Jumlah baris raw England data masuk: {eng_raw_count}")
    
    # Rename kolom agar tidak ada spasi atau karakter ilegal (., (), dsb)
    # Misal: "Ammonia (mg/l)" -> "Ammonia_mg_l"
    for c in england_df.columns:
        clean_col = c.replace(' ', '_').replace('(', '').replace(')', '').replace('.', '_').replace('/', '_')
        england_df = england_df.withColumnRenamed(c, clean_col)
        
    logger.info("Memvalidasi anomali England Dataset (Typo, Suhu ekstrim, CCME_WQI, Date)...")
    
    # Cast temperatur ke float
    england_df = england_df.withColumn("Temp_Float", F.col("Temperature_cel").cast(FloatType()))
    
    valid_ccme = ["Excellent", "Good", "Fair", "Marginal", "Poor"]
    
    eng_valid_condition = (
        ~(F.col("Waterbody_Type").isin([" THROCKMORTON", " FE"])) &
        (F.col("Date").rlike(r"^\d{2}-\d{2}-\d{4}$")) &
        (F.col("Temp_Float").isNotNull() & (F.col("Temp_Float") >= -10.0) & (F.col("Temp_Float") <= 60.0)) &
        (F.col("CCME_WQI").isin(valid_ccme))
    )
    
    eng_valid_df = england_df.filter(eng_valid_condition).dropDuplicates()
    eng_rejected_df = england_df.filter(~eng_valid_condition)
    
    eng_valid_count = eng_valid_df.count()
    eng_rejected_count = eng_rejected_df.count()
    total_valid += eng_valid_count
    total_rejected += eng_rejected_count
    
    logger.info(f"England Dataset - Lolos: {eng_valid_count}, Ditolak: {eng_rejected_count}")
    
    logger.info("Menyimpan valid England Fact Table ke s3a://silver/fact_england_water_quality...")
    eng_valid_df.drop("Temp_Float").write.mode("overwrite").parquet("s3a://silver/fact_england_water_quality")
    
    logger.info("Menyimpan rejected England records ke s3a://rejected/england_water_quality...")
    eng_rejected_df.drop("Temp_Float").write.mode("overwrite").parquet("s3a://rejected/england_water_quality")
    
    # ==============================================================================
    # 2. Jalur Fact Table B: Baca data Observasi WIMS (station/*/*.csv)
    # ==============================================================================
    logger.info("Membaca raw fact data WIMS dari MinIO (s3a://bronze/station/*/*.csv)...")
    raw_df = spark.read.option("header", "true").csv("s3a://bronze/station/*/*.csv")
    wims_raw_count = raw_df.count()
    logger.info(f"Jumlah baris raw WIMS data masuk: {wims_raw_count}")
    
    # RENAME KOLOM WIMS di awal agar titik tidak diinterpretasikan sebagai struct
    for c in raw_df.columns:
        raw_df = raw_df.withColumnRenamed(c, c.replace('.', '_'))
        
    logger.info("Melakukan data cleansing & regex stripping (Left-Censored Data) pada WIMS...")
    
    cleaned_df = raw_df.withColumn(
        "result_clean", 
        F.regexp_replace(F.trim(F.col("result")), r"[<>]", "").cast(FloatType())
    )
    
    cleaned_df = cleaned_df.withColumn("lat_float", F.col("samplingPoint_latitude").cast(FloatType())) \
                           .withColumn("lon_float", F.col("samplingPoint_longitude").cast(FloatType()))
    
    wims_valid_condition = (
        F.col("id").startswith("http") &
        F.col("lat_float").isNotNull() &
        F.col("lon_float").isNotNull() &
        ~(
            (F.col("determinand_notation") == '0061') & ((F.col("result_clean") < 0) | (F.col("result_clean") > 14))
        ) &
        ~(
            (F.col("determinand_notation") == '0076') & ((F.col("result_clean") < -10) | (F.col("result_clean") > 50))
        )
    )
    
    valid_df = cleaned_df.filter(wims_valid_condition)
    rejected_df = cleaned_df.filter(~wims_valid_condition)
    
    valid_df = valid_df.dropDuplicates(["id"])
    
    wims_valid_count = valid_df.count()
    wims_rejected_count = rejected_df.count()
    total_valid += wims_valid_count
    total_rejected += wims_rejected_count
    
    logger.info(f"WIMS Dataset - Lolos: {wims_valid_count}, Ditolak: {wims_rejected_count}")
    
    logger.info("Menyimpan valid WIMS Fact Table ke s3a://silver/fact_wims_water_quality...")
    # Repartition untuk menghindari OOM saat saving karena default shuffle partitions terlalu kecil (8)
    spark.conf.set("spark.sql.shuffle.partitions", "200")
    valid_df.drop("lat_float", "lon_float").repartition(64).write.mode("overwrite").parquet("s3a://silver/fact_wims_water_quality")
    
    logger.info("Menyimpan rejected WIMS records ke s3a://rejected/wims_water_quality...")
    rejected_df.drop("lat_float", "lon_float").repartition(16).write.mode("overwrite").parquet("s3a://rejected/wims_water_quality")
    
    # ==============================================================================
    # 3. Jalur Dimension Table: Ekstraksi 14 stasiun via rasterio
    # ==============================================================================
    logger.info("Mengekstrak unique stations untuk Dimension Table (Join Key: Area -> prefLabel)...")
    
    eng_areas_df = eng_valid_df.select(F.col("Area")).dropDuplicates()
    
    wims_stations_df = valid_df.select(
        F.col("samplingPoint_prefLabel").alias("Area"),
        F.col("samplingPoint_notation").alias("station_id"),
        F.col("samplingPoint_latitude").cast(FloatType()).alias("latitude"),
        F.col("samplingPoint_longitude").cast(FloatType()).alias("longitude")
    ).dropDuplicates(["Area"])
    
    # Inner join untuk memetakan stasiun yang ada di kedua dataset
    joined_stations_df = eng_areas_df.join(wims_stations_df, on="Area", how="inner")
    
    uk_stations_df = joined_stations_df.filter(
        (F.col("latitude") >= 49) & (F.col("latitude") <= 61) &
        (F.col("longitude") >= -9) & (F.col("longitude") <= 2)
    )
    
    fourteen_stations = uk_stations_df.limit(14).collect()
    logger.info("Mengekstrak kepadatan populasi (rasterio) untuk 14 stasiun...")
    
    dim_records = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    raster_path = os.path.join(base_dir, "data/bronze/popdensity/gbr_pd_2020_1km_UNadj.tif")
    
    for row in fourteen_stations:
        # Radius 1.0 km sebagai baseline di Silver. Gold akan mengimplementasikan dynamic/scalable radius.
        pop_density = extract_population_density(raster_path, row["latitude"], row["longitude"], radius_km=1.0)
        dim_records.append({
            "station_id": row["station_id"],
            "area_name": row["Area"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "population_density": float(pop_density)
        })
        
    dim_schema = StructType([
        StructField("station_id", StringType(), False),
        StructField("area_name", StringType(), False),
        StructField("latitude", FloatType(), False),
        StructField("longitude", FloatType(), False),
        StructField("population_density", FloatType(), True)
    ])
    dim_df = spark.createDataFrame(dim_records, schema=dim_schema)
    
    logger.info("Menyimpan Dimension Table ke s3a://silver/dim_station_population...")
    dim_df.write.mode("overwrite").parquet("s3a://silver/dim_station_population")
    
    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Silver Validation & Enrichment Selesai dalam {duration:.2f} detik.")
    
    spark.stop()
    
    return {
        "status": "success", 
        "wims_raw_count": wims_raw_count,
        "eng_raw_count": eng_raw_count,
        "total_valid_count": total_valid, 
        "total_rejected_count": total_rejected,
        "dim_count": len(dim_records),
        "duration_seconds": duration
    }

if __name__ == "__main__":
    run_silver_validation()
