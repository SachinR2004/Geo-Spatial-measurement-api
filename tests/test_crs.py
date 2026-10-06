from app.services.parser_service import parse_geospatial_file
from app.services.crs_service import prepare_for_measurement


def test_geographic_crs_is_projected():
    gdf = parse_geospatial_file("sample_data/test_geospatial.kml")

    measured_gdf = prepare_for_measurement(gdf)

    assert gdf.crs.is_geographic
    assert measured_gdf.crs.is_projected
    assert measured_gdf.crs.to_epsg() == 32643