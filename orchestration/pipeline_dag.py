from dagster import asset, Definitions, DefaultScheduleStatus, AssetExecutionContext
import sys
import os

# Menambahkan path src ke sys.path agar bisa mengimpor module dari src/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.pipelines.bronze_ingest import ingest_to_minio

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

# Definisi Dagster Workspace
defs = Definitions(
    assets=[bronze_layer_asset],
)
