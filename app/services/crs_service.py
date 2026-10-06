import geopandas as gpd


def prepare_for_measurement(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        raise ValueError("Input file has no CRS information.")

    if not gdf.crs.is_geographic:
        return gdf

    projected_crs = gdf.estimate_utm_crs()

    if projected_crs is None:
        raise ValueError("Could not determine a suitable projected CRS.")

    return gdf.to_crs(projected_crs)