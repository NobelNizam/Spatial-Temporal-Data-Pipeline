import nbformat as nbf

nb = nbf.v4.new_notebook()

cells = []

# Setup Cell
cells.append(nbf.v4.new_markdown_cell("# Silver Layer EDA - 10 Step PySpark EDA Analyzer"))
cells.append(nbf.v4.new_code_cell("""
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from pyspark.sql import functions as F
from pyspark.sql.types import *

sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '..')))
from src.config.engine_session import get_spark_session

spark = get_spark_session("SilverLayerEDA")

print("Membaca Tabel Silver...")
df_eng = spark.read.parquet("s3a://silver/fact_england_water_quality")
df_wims = spark.read.parquet("s3a://silver/fact_wims_water_quality")
df_dim = spark.read.parquet("s3a://silver/dim_station_population")
"""))

# 1. Data Overview
cells.append(nbf.v4.new_markdown_cell("## 1. Data Overview"))
cells.append(nbf.v4.new_code_cell("""
print("--- Data Overview ---")
print(f"Total baris England Data: {df_eng.count():,}")
print(f"Total baris WIMS Data: {df_wims.count():,}")
print(f"Total baris Dim Station: {df_dim.count():,}")

print("\\n--- Schema England Data ---")
df_eng.printSchema()
print("\\n--- Schema Dim Station ---")
df_dim.printSchema()
"""))

# 2. Data Quality Assessment (Missing Values & Duplicates)
cells.append(nbf.v4.new_markdown_cell("## 2. Data Quality Assessment (Missing Values & Duplicates)"))
cells.append(nbf.v4.new_code_cell("""
print("--- Missing Values Check (Dim Station) ---")
df_dim.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df_dim.columns]).show()

print("--- Missing Values Check (England Data) ---")
df_eng.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in ["CCME_WQI", "Temperature_cel", "pH_ph_units"]]).show()

# Duplicates
print(f"Duplicate di England: {df_eng.count() - df_eng.dropDuplicates().count():,}")
print(f"Duplicate di Dim Station: {df_dim.count() - df_dim.dropDuplicates().count():,}")
"""))

# 3. Anomaly & String Cleansing (Cek Ulang Hasil Cleansing)
cells.append(nbf.v4.new_markdown_cell("## 3. Anomaly & String Cleansing Check"))
cells.append(nbf.v4.new_code_cell("""
print("Memverifikasi apakah masih ada sisa < atau > di WIMS result_clean...")
# Cek null rate di result_clean
null_results = df_wims.filter(F.col("result_clean").isNull()).count()
print(f"WIMS Result Nulls: {null_results:,}")
"""))

# 4. Categorical Analysis
cells.append(nbf.v4.new_markdown_cell("## 4. Categorical Analysis"))
cells.append(nbf.v4.new_code_cell("""
print("--- Top Waterbody Types di England Data ---")
top_wb = df_eng.groupBy("Waterbody_Type").count().orderBy(F.desc("count")).limit(10).toPandas()
print(top_wb)

plt.figure(figsize=(10,5))
sns.barplot(data=top_wb, x='count', y='Waterbody_Type')
plt.title("Top Waterbody Types (England)")
plt.tight_layout()
plt.show()

print("\\n--- WQI Categories ---")
wqi_counts = df_eng.groupBy("CCME_WQI").count().orderBy(F.desc("count")).toPandas()
print(wqi_counts)
"""))

# 5. Descriptive Statistic
cells.append(nbf.v4.new_markdown_cell("## 5. Descriptive Statistic"))
cells.append(nbf.v4.new_code_cell("""
print("--- Statistik WIMS Data ---")
df_wims = df_wims.withColumn("lat_float", F.col("samplingPoint_latitude").cast("float")).withColumn("lon_float", F.col("samplingPoint_longitude").cast("float"))
df_wims.select("result_clean", "lat_float", "lon_float").summary("count", "mean", "min", "max", "stddev").show()

print("--- Statistik Dim Station ---")
df_dim.select("population_density").summary("count", "mean", "min", "max", "stddev").show()
"""))

# 6. Distribution Analysis / Outlier Detection
cells.append(nbf.v4.new_markdown_cell("## 6. Distribution Analysis / Outlier Detection"))
cells.append(nbf.v4.new_code_cell("""
print("Distribusi pH pada England Data")
sample_ph = df_eng.select("pH_ph_units").sample(fraction=0.05, seed=42).toPandas()
sample_ph['pH_ph_units'] = sample_ph['pH_ph_units'].astype(float)

plt.figure(figsize=(10,5))
sns.histplot(sample_ph['pH_ph_units'].dropna(), bins=50, kde=True)
plt.title("Distribusi pH (Sample 5%)")
plt.show()
"""))

# 7. Relationship / Spatial Analysis
cells.append(nbf.v4.new_markdown_cell("## 7. Relationship / Spatial Analysis"))
cells.append(nbf.v4.new_code_cell("""
print("Melihat Spatial Distribution dari 14 Station di UK")
stations_pd = df_wims.select("samplingPoint_prefLabel", "lat_float", "lon_float").dropDuplicates(["samplingPoint_prefLabel"]).join(
    df_dim, df_wims["samplingPoint_prefLabel"] == df_dim["area_name"], "inner"
).toPandas()

plt.figure(figsize=(8,8))
sns.scatterplot(data=stations_pd, x='lon_float', y='lat_float', size='population_density', sizes=(50, 500), hue='population_density', palette='viridis')
plt.title("Spatial Analysis: 14 Stations (Silver Layer)")
plt.show()
"""))

# 8. Time-Based Analysis
cells.append(nbf.v4.new_markdown_cell("## 8. Time-Based Analysis"))
cells.append(nbf.v4.new_code_cell("""
print("Tren Pengambilan Sampel per Tahun di WIMS")
# Ambil tahun dari phenomenonTime
df_wims_time = df_wims.withColumn("Year", F.substring("phenomenonTime", 1, 4))
yearly_counts = df_wims_time.groupBy("Year").count().orderBy("Year").toPandas()

# Hapus outlier tahun (jika ada error entry)
yearly_counts['Year'] = yearly_counts['Year'].astype(int)
yearly_counts = yearly_counts[(yearly_counts['Year'] >= 2000) & (yearly_counts['Year'] <= 2026)]

plt.figure(figsize=(12,5))
sns.lineplot(data=yearly_counts, x='Year', y='count', marker='o')
plt.title("WIMS Observations per Year")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()
"""))

# 9. Data Consistency Check
cells.append(nbf.v4.new_markdown_cell("## 9. Data Consistency Check"))
cells.append(nbf.v4.new_code_cell("""
print("Verifikasi apakah ada pH > 14 atau < 0 (Harusnya 0 di Silver)")
invalid_ph = df_eng.withColumn("pH", F.col("pH_ph_units").cast("float")).filter((F.col("pH") < 0) | (F.col("pH") > 14)).count()
print(f"Invalid pH (England): {invalid_ph}")

invalid_temp_wims = df_wims.filter((F.col("determinand_notation") == '0076') & ((F.col("result_clean") < -10) | (F.col("result_clean") > 50))).count()
print(f"Invalid Temp (WIMS): {invalid_temp_wims}")
"""))

# 10. Business/Domain Validation
cells.append(nbf.v4.new_markdown_cell("## 10. Business/Domain Validation"))
cells.append(nbf.v4.new_code_cell("""
print("Memastikan Dimensi Stasiun sesuai Business Logic (UK Region, >0 Pop Density)")
valid_dims = df_dim.filter(F.col("population_density") >= 0).count()
print(f"Stasiun dengan populasi valid: {valid_dims} dari {df_dim.count()}")
print("Menutup Spark Session.")
spark.stop()
"""))

nb['cells'] = cells

with open('benchmarks/Silver_Layer_EDA.ipynb', 'w') as f:
    nbf.write(nb, f)
print("Berhasil membuat benchmarks/Silver_Layer_EDA.ipynb")
