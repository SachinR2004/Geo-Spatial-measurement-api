from app.services.parser_service import parse_geospatial_file


def test_parse_kml():
    gdf = parse_geospatial_file("sample_data/test_geospatial.kml")

    assert len(gdf) == 3
    assert gdf.crs.to_epsg() == 4326
    assert list(gdf.geometry.geom_type) == [
        "Polygon",
        "LineString",
        "Point",
    ]