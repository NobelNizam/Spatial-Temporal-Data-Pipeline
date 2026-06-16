import os
import sys

# Menambahkan path src ke sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.config.engine_session import get_spark_session

def show_silver_data():
    spark = get_spark_session("ViewSilverData")
    
    print("\n" + "="*60)
    print("1. fact_england_water_quality (Top 5 Rows)")
    print("="*60)
    try:
        df_eng = spark.read.parquet("s3a://silver/fact_england_water_quality")
        df_eng.show(5, truncate=False)
    except Exception as e:
        print(f"Failed to read: {e}")
        
    print("\n" + "="*60)
    print("2. fact_wims_water_quality (Top 5 Rows)")
    print("="*60)
    try:
        df_wims = spark.read.parquet("s3a://silver/fact_wims_water_quality")
        df_wims.show(5, truncate=False)
    except Exception as e:
        print(f"Failed to read: {e}")
        
    print("\n" + "="*60)
    print("3. dim_station_population (All 14 Rows)")
    print("="*60)
    try:
        df_dim = spark.read.parquet("s3a://silver/dim_station_population")
        df_dim.show(15, truncate=False)
    except Exception as e:
        print(f"Failed to read: {e}")
        
    spark.stop()

if __name__ == "__main__":
    show_silver_data()
