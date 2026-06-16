import nbformat as nbf

nb = nbf.v4.new_notebook()

code_cells = [
    """
# Setup Spark Session
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '..')))
from src.config.engine_session import get_spark_session
from pyspark.sql import functions as F
import matplotlib.pyplot as plt
import seaborn as sns

spark = get_spark_session("GoldEnglandEDA")
df = spark.read.parquet("s3a://gold/england_water_quality")
    """,
    """
# 1. Data Overview
print(f"Total baris observasi: {df.count():,}")
print("\\n--- Schema ---")
df.printSchema()
print("\\n--- Sampel Data ---")
df.show(5, truncate=False)
    """,
    """
# 2. Data Quality Assessment (Missing Values & Duplicates)
print("--- Missing Values Check ---")
df.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df.columns]).show()

print("--- Duplicate Check ---")
print(f"Jumlah baris duplikat (exact match): {df.count() - df.dropDuplicates().count()}")
    """,
    """
# 3. Anomaly & String Cleansing (Khusus Data Kotor/Tersensor)
# Di Gold Layer, data sudah berbentuk float (hasil Silver cleansing), 
# namun kita validasi apakah ada nilai non-numerik tersisa jika CCME_WQI aneh.
print("Check anomali tipe WQI:")
df.groupBy("CCME_WQI").count().show()
    """,
    """
# 4. Categorical Analysis
top_cats = df.groupBy("Waterbody_Type").count().orderBy(F.desc("count")).limit(10).toPandas()

plt.figure(figsize=(10, 5))
sns.barplot(data=top_cats, x="count", y="Waterbody_Type")
plt.title("Distribusi Waterbody Type")
plt.tight_layout()
plt.show()
    """,
    """
# 5. Descriptive Statistic
# Select numeric columns
num_cols = ["Ammonia_mg_l", "Biochemical_Oxygen_Demand_mg_l", "Dissolved_Oxygen_mg_l", 
            "Orthophosphate_mg_l", "pH_ph_units", "Temperature_cel", "Nitrogen_mg_l", 
            "Nitrate_mg_l", "population_density"]
df.select(num_cols).summary("count", "mean", "min", "max", "stddev").show()
    """,
    """
# 6. Distribution Analysis / Outlier Detection
sample_pd = df.select("Temperature_cel", "pH_ph_units", "population_density").sample(fraction=0.5).toPandas()

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
sns.boxplot(data=sample_pd, y="Temperature_cel", ax=axes[0]).set_title("Temperature")
sns.boxplot(data=sample_pd, y="pH_ph_units", ax=axes[1]).set_title("pH")
sns.boxplot(data=sample_pd, y="population_density", ax=axes[2]).set_title("Population Density")
plt.tight_layout()
plt.show()
    """,
    """
# 7. Relationship / Spatial Analysis
# Hubungan kepadatan populasi dengan Nitrate
sample_pd = df.select("population_density", "Nitrate_mg_l", "CCME_WQI").sample(fraction=0.5).toPandas()

plt.figure(figsize=(10, 6))
sns.scatterplot(data=sample_pd, x="population_density", y="Nitrate_mg_l", hue="CCME_WQI", alpha=0.6)
plt.title("Hubungan Kepadatan Populasi dan Nitrat")
plt.tight_layout()
plt.show()
    """,
    """
# 8. Time-Based Analysis
monthly_counts = df.groupBy("year").count().orderBy("year").toPandas()

plt.figure(figsize=(10, 5))
sns.lineplot(data=monthly_counts, x="year", y="count", marker="o")
plt.title("Trend Observasi per Tahun")
plt.tight_layout()
plt.show()
    """,
    """
# 9. Data Consistency Check
invalid_dates = df.filter(F.col("year") > 2026).count()
print(f"Baris dengan tahun di masa depan: {invalid_dates}")
    """,
    """
# 10. Business/Domain Validation
invalid_temp = df.filter((F.col("Temperature_cel") < -10) | (F.col("Temperature_cel") > 60))
print(f"Anomali suhu ekstrem (di luar -10 s/d 60): {invalid_temp.count():,} baris")

poor_wqi = df.filter(F.col("CCME_WQI") == "Poor").count()
print(f"Total observasi WQI 'Poor': {poor_wqi:,} baris")
    """
]

for cell in code_cells:
    nb.cells.append(nbf.v4.new_code_cell(cell))

with open("/home/jovyan/work/benchmarks/Gold_England_EDA.ipynb", "w") as f:
    nbf.write(nb, f)
print("Notebook Gold_England_EDA.ipynb generated.")
