from pyspark.sql import SparkSession
import time
import logging

def get_spark_session(app_name="SpatialTemporalPipeline"):
    """
    Inisialisasi Spark Session untuk pipeline.
    Dengan batasan memory 4GB dan 4 Cores untuk mencegah OOM di laptop 16GB.
    Juga memuat dependensi AWS untuk MinIO.
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .master("local[4]") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.memory.offHeap.enabled", "true") \
        .config("spark.memory.offHeap.size", "1g") \
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin123") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.ui.port", "4040") \
        .getOrCreate()
    return spark

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("EngineSession")
    
    logger.info("Memulai Spark Session untuk mengaktifkan UI di port 4040...")
    spark = get_spark_session("SparkUI_Test")
    
    logger.info("Spark Session AKTIF! Silahkan buka http://localhost:4040 di browser Anda.")
    logger.info("Script ini akan menahan session selama 1 jam agar Anda bisa melakukan inspeksi.")
    
    # Menahan agar session tidak mati dan UI tetap bisa diakses
    try:
        time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Dihentikan oleh pengguna.")
    finally:
        spark.stop()
        logger.info("Spark Session dimatikan.")