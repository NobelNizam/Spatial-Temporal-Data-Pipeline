from dagster import asset, Definitions, DefaultScheduleStatus, AssetExecutionContext
import sys
import os

# Menambahkan path src ke sys.path agar bisa mengimpor module dari src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipelines.bronze_ingest import ingest_to_minio
from src.pipelines.silver_validate import run_silver_validation

@asset(description="Ingest raw data dari CSV dan GeoTIFF lokal ke MinIO bucket 'bronze'")
def bronze_layer_asset(context: AssetExecutionContext) -> dict:
    """
    Eksekusi Ingestion Layer (Bronze).
    Mengunggah dataset lokal (data/bronze/) ke object storage MinIO.
    """
    context.log.info("Memulai proses ingest dari lokal ke MinIO...")
    
    # Fail-fast sudah diimplementasikan di fungsi ingest_to_minio
    result = ingest_to_minio(source_dir='data/bronze', bucket_name='bronze')
    
    context.log.info(f"Proses ingest selesai: {result['ingested_count']} file terunggah.")
    return result

@asset(deps=[bronze_layer_asset], description="Validasi data Bronze dan ekstraksi dimensi spasial ke Silver layer")
def silver_layer_asset(context: AssetExecutionContext) -> dict:
    """
    Eksekusi Validation & Enrichment Layer (Silver).
    Membaca dari s3a://bronze/, memfilter anomali, mengekstrak dimensi stasiun,
    dan menyimpan hasilnya di s3a://silver/ (dan data gagal ke s3a://rejected/).
    """
    context.log.info("Memulai proses validasi Silver Layer...")
    
    result = run_silver_validation()
    
    context.log.info(f"Validasi selesai. {result['valid_count']} record lolos, {result['rejected_count']} ditolak. {result['dim_count']} dimensi diekstrak.")
    return result

# Definisi Dagster Workspace
defs = Definitions(
    assets=[bronze_layer_asset, silver_layer_asset],
)
