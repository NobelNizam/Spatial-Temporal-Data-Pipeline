import rasterio
import logging

logger = logging.getLogger("SpatialHelpers")

def extract_population_density(raster_path: str, lat: float, lon: float, radius_km: float = 1.0) -> float:
    """
    Ekstrak rata-rata kepadatan penduduk dari raster GeoTIFF dalam radius tertentu dari koordinat.
    Parameter radius_km bersifat scalable (dinamis).
    Menggunakan rasterio untuk hanya memuat piksel di sekitar stasiun (Anti-OOM).
    """
    try:
        with rasterio.open(raster_path) as src:
            # Lon=x, Lat=y
            py, px = src.index(lon, lat)
            
            # Asumsi resolusi raster adalah ~1km. 
            # Jika radius 1km, offset = 1 (window 3x3). Jika 2km, offset = 2 (window 5x5).
            offset = max(1, int(radius_km))
            window_size = offset * 2 + 1
            
            window = rasterio.windows.Window(px - offset, py - offset, window_size, window_size)
            data = src.read(1, window=window)
            
            # Filter no-data
            valid_pixels = [float(p) for p in data.flatten() if p != src.nodata and p >= 0]
            
            if valid_pixels:
                return sum(valid_pixels) / len(valid_pixels)
            return 0.0
    except Exception as e:
        logger.warning(f"Gagal ekstrak raster untuk koordinat ({lat}, {lon}) di {raster_path}: {e}")
        return 0.0
