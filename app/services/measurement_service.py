import geopandas as gpd


def calculate_measurement(row) -> tuple[float | None, str | None, str]:
    geometry = row.geometry

    if geometry is None or geometry.is_empty:
        return None, None, "FAILED"

    geometry_type = geometry.geom_type

    if geometry_type in {"Polygon", "MultiPolygon"}:
        return float(geometry.area), "m²", "COMPLETED"

    if geometry_type in {"LineString", "MultiLineString"}:
        return float(geometry.length), "m", "COMPLETED"

    if geometry_type == "Point":
        return None, None, "NOT_APPLICABLE"

    return None, None, "FAILED"