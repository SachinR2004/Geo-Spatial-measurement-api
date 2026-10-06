from pathlib import Path

import geopandas as gpd


SUPPORTED_EXTENSIONS = {".kml", ".zip"}


def parse_geospatial_file(file_path: str) -> gpd.GeoDataFrame:
    path = Path(file_path)

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file format.")

    if path.suffix.lower() == ".kml":
        gdf = gpd.read_file(path, driver="KML")
    else:
        gdf = gpd.read_file(path)

    return gdf