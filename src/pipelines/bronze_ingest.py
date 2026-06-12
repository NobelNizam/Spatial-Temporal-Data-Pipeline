import os
import boto3
from botocore.client import Config
import logging

# Konfigurasi logging standar
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BronzeIngest")

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv('AWS_ENDPOINT_URL', 'http://minio:9000'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin123'),
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

def ingest_to_minio(source_dir: str = 'data/bronze', bucket_name: str = 'bronze') -> dict:
    """
    Meng-ingest file raw lokal ke MinIO object storage.
    Sesuai constraint: fail-fast untuk error I/O, tanpa mekanisme retry otomatis.
    """
    s3 = get_s3_client()
    
    # Memastikan bucket ada
    try:
        s3.head_bucket(Bucket=bucket_name)
    except Exception:
        logger.info(f"Bucket '{bucket_name}' belum ada. Membuat bucket...")
        try:
            s3.create_bucket(Bucket=bucket_name)
        except Exception as e:
            logger.error(f"Gagal membuat bucket '{bucket_name}': {e}")
            raise RuntimeError(f"Fail-fast: Tidak dapat membuat bucket {bucket_name}")

    ingested_files = []
    
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file == '.gitkeep':
                continue
            
            local_path = os.path.join(root, file)
            # Kunci objek mengabaikan base path 'data/bronze/'
            relative_path = os.path.relpath(local_path, source_dir)
            # Pastikan format path menggunakan forward slash untuk S3
            s3_key = relative_path.replace(os.sep, '/')
            
            try:
                # Cek apakah file sudah ada dengan ukuran yang sama (Idempotency sederhana)
                try:
                    head = s3.head_object(Bucket=bucket_name, Key=s3_key)
                    local_size = os.path.getsize(local_path)
                    if head['ContentLength'] == local_size:
                        logger.debug(f"Lewati {s3_key}, file sudah ada dengan ukuran sama.")
                        ingested_files.append(s3_key)
                        continue
                except Exception:
                    pass # Objek belum ada atau ukuran beda, lanjut upload

                logger.info(f"Uploading {local_path} ke s3://{bucket_name}/{s3_key}...")
                s3.upload_file(local_path, bucket_name, s3_key)
                ingested_files.append(s3_key)
            except Exception as e:
                # Fail-fast: Hentikan seketika dan lempar error
                logger.error(f"Gagal upload file lokal {local_path} ke MinIO: {str(e)}")
                raise RuntimeError(f"Fail-fast terpicu akibat I/O error pada {local_path}: {str(e)}")
                
    logger.info(f"Bronze Ingest Selesai. Total {len(ingested_files)} file berhasil diproses ke bucket '{bucket_name}'.")
    return {
        "status": "success",
        "ingested_count": len(ingested_files),
        "bucket": bucket_name
    }

if __name__ == "__main__":
    ingest_to_minio()
