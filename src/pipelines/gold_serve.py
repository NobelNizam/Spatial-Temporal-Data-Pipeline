import os
import sys
import logging
import time
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, FloatType, IntegerType
)

# Konfigurasi logging standar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GoldServe")

# Menambahkan path ke sys.path untuk absolute import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.config.engine_session import get_spark_session
from src.utils.spatial_helpers import extract_population_density

def run_gold_serving(radius_km: float = 5.0):
    """
    Eksekusi Gold Layer:
    - Regenerasi tabel dimensi dengan dynamic radius_km.
    - Explicit Schema Enforcement via StructType.
    - Broadcast Join tabel fakta dan tabel dimensi.
    - Parquet terpartisi berdasarkan station_id dan year.
    """
    start_time = time.time()
    logger.info(f"Membangun Spark Session untuk Gold Layer (Radius Kepadatan: {radius_km} km)...")
    spark = get_spark_session("GoldLayer")
    
    # ==============================================================================
    # 1. Regenerasi Dimension Table (Dynamic Radius n-km)
    # ==============================================================================
    logger.info("Membaca Dimension Table dari Silver (s3a://silver/dim_station_population)...")
    dim_df = spark.read.parquet("s3a://silver/dim_station_population")
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    raster_path = os.path.join(base_dir, "data/bronze/popdensity/gbr_pd_2020_1km_UNadj.tif")
    
    dim_records = dim_df.collect()
    updated_dim_records = []
    
    logger.info(f"Menghitung ulang populasi untuk 14 stasiun dengan radius {radius_km} km...")
    for row in dim_records:
        pop_density = extract_population_density(raster_path, row["latitude"], row["longitude"], radius_km=radius_km)
        updated_dim_records.append({
            "station_id": row["station_id"],
            "area_name": row["area_name"],
            "population_density": float(pop_density)
        })
        
    dim_schema = StructType([
        StructField("station_id", StringType(), False),
        StructField("area_name", StringType(), False),
        StructField("population_density", FloatType(), True)
    ])
    
    updated_dim_df = spark.createDataFrame(updated_dim_records, schema=dim_schema)
    
    # Broadcast Dimension Table
    broadcast_dim_df = F.broadcast(updated_dim_df)
    
    # ==============================================================================
    # 2. Schema Enforcement Definition (DATA_DICTIONARY)
    # ==============================================================================
    # Skema untuk Gold England (Pivot Table)
    gold_england_schema = StructType([
        StructField("station_id", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("Country", StringType(), True),
        StructField("Area", StringType(), True),
        StructField("Waterbody_Type", StringType(), True),
        StructField("Date", StringType(), True),
        StructField("Ammonia_mg_l", FloatType(), True),
        StructField("Biochemical_Oxygen_Demand_mg_l", FloatType(), True),
        StructField("Dissolved_Oxygen_mg_l", FloatType(), True),
        StructField("Orthophosphate_mg_l", FloatType(), True),
        StructField("pH_ph_units", FloatType(), True),
        StructField("Temperature_cel", FloatType(), True),
        StructField("Nitrogen_mg_l", FloatType(), True),
        StructField("Nitrate_mg_l", FloatType(), True),
        StructField("CCME_Values", FloatType(), True),
        StructField("CCME_WQI", StringType(), True),
        StructField("population_density", FloatType(), True)
    ])
    
    # Skema untuk Gold WIMS (Transactional Table)
    gold_wims_schema = StructType([
        StructField("station_id", StringType(), True),
        StructField("year", IntegerType(), True),
        StructField("id", StringType(), True),
        StructField("area_name", StringType(), True),
        StructField("samplingPoint_samplingPointStatus", StringType(), True),
        StructField("samplingPoint_samplingPointType", StringType(), True),
        StructField("phenomenonTime", StringType(), True),
        StructField("samplingPurpose", StringType(), True),
        StructField("sampleMaterialType", StringType(), True),
        StructField("determinand_notation", StringType(), True),
        StructField("determinand_prefLabel", StringType(), True),
        StructField("result_clean", FloatType(), True),
        StructField("unit", StringType(), True),
        StructField("population_density", FloatType(), True)
    ])
    
    # ==============================================================================
    # 3. Proses Gold England (Country-Wise Data)
    # ==============================================================================
    logger.info("Membaca Fact Table England dari s3a://silver/fact_england_water_quality...")
    eng_df = spark.read.parquet("s3a://silver/fact_england_water_quality")
    
    logger.info("Broadcast Join England Fact Table dengan Dimension Table...")
    # Extract year from Date (format: DD-MM-YYYY)
    eng_df = eng_df.withColumn("year", F.substring(F.col("Date"), 7, 4).cast(IntegerType()))
    
    # Cast tipe data numerik
    numeric_cols = [
        "Ammonia_mg_l", "Biochemical_Oxygen_Demand_mg_l", "Dissolved_Oxygen_mg_l",
        "Orthophosphate_mg_l", "pH_ph_units", "Temperature_cel", "Nitrogen_mg_l",
        "Nitrate_mg_l", "CCME_Values"
    ]
    for c in numeric_cols:
        if c in eng_df.columns:
            eng_df = eng_df.withColumn(c, F.col(c).cast(FloatType()))
    
    eng_joined_df = eng_df.join(
        broadcast_dim_df.select("station_id", "area_name", "population_density"), 
        eng_df.Area == broadcast_dim_df.area_name, 
        how="inner"
    )
    
    # Urutkan kolom sesuai skema eksplisit
    eng_final_df = eng_joined_df.select([f.name for f in gold_england_schema.fields])
    
    # Terapkan schema eksplisit (Schema Enforcement)
    eng_final_df = spark.createDataFrame(eng_final_df.rdd, schema=gold_england_schema)
    
    logger.info("Menyimpan Gold England Table (Partitioned by station_id, year) ke s3a://gold/england_water_quality...")
    spark.conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")
    eng_final_df.write.mode("overwrite") \
        .partitionBy("station_id", "year") \
        .parquet("s3a://gold/england_water_quality")
        
    logger.info("Menyimpan versi Single Parquet untuk Gold England Table ke s3a://gold/england_water_quality_single...")
    eng_final_df.coalesce(1).write.mode("overwrite") \
        .parquet("s3a://gold/england_water_quality_single")
        
    eng_gold_count = eng_final_df.count()
    logger.info(f"Berhasil menyimpan {eng_gold_count} baris Gold England.")
    
    # ==============================================================================
    # 4. Proses Gold WIMS (Transactional Data)
    # ==============================================================================
    logger.info("Membaca Fact Table WIMS dari s3a://silver/fact_wims_water_quality...")
    wims_df = spark.read.parquet("s3a://silver/fact_wims_water_quality")
    
    logger.info("Broadcast Join WIMS Fact Table dengan Dimension Table...")
    # Extract year from phenomenonTime (format: YYYY-MM-DD HH:MM:SS)
    wims_df = wims_df.withColumn("year", F.substring(F.col("phenomenonTime"), 1, 4).cast(IntegerType()))
    
    # Rename kolom agar match dengan schema target
    wims_df = wims_df.withColumnRenamed("samplingPoint_notation", "station_id") \
                     .withColumnRenamed("samplingPoint_prefLabel", "area_name")
                     
    wims_joined_df = wims_df.join(
        broadcast_dim_df.select("station_id", "population_density"), 
        on="station_id", 
        how="left"
    )
    
    # Urutkan kolom sesuai skema eksplisit
    wims_final_df = wims_joined_df.select([f.name for f in gold_wims_schema.fields])
    
    # Terapkan schema eksplisit (Schema Enforcement)
    # Catatan: createDataFrame(rdd, schema) sangat direkomendasikan untuk enforcement mutlak
    wims_final_df = spark.createDataFrame(wims_final_df.rdd, schema=gold_wims_schema)
    
    logger.info("Menyimpan Gold WIMS Table (Partitioned by station_id, year) ke s3a://gold/wims_water_quality...")
    # Memaksa repartitioning agar terhindar dari OOM saat menulis partisi >60jt baris
    spark.conf.set("spark.sql.shuffle.partitions", "200")
    wims_final_df.repartition("station_id", "year").write.mode("overwrite") \
        .partitionBy("station_id", "year") \
        .parquet("s3a://gold/wims_water_quality")
        
    wims_gold_count = wims_final_df.count()
    logger.info(f"Berhasil menyimpan {wims_gold_count} baris Gold WIMS.")
    
    end_time = time.time()
    duration = end_time - start_time
    logger.info(f"Gold Serving Selesai dalam {duration:.2f} detik.")
    
    spark.stop()
    
    return {
        "status": "success",
        "radius_km": radius_km,
        "england_gold_count": eng_gold_count,
        "wims_gold_count": wims_gold_count,
        "duration_seconds": duration
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Gold Layer")
    parser.add_argument("--radius", type=float, default=5.0, help="Radius (km) untuk populasi")
    args = parser.parse_args()
    run_gold_serving(radius_km=args.radius)
