from app.services.measurement_service import calculate_measurement


def test_polygon_measurement():
    from shapely.geometry import Polygon

    polygon = Polygon([
        (0, 0),
        (10, 0),
        (10, 10),
        (0, 10),
    ])

    class Row:
        geometry = polygon

    measurement, unit, status = calculate_measurement(Row())

    assert measurement == 100.0
    assert unit == "m²"
    assert status == "COMPLETED"


def test_linestring_measurement():
    from shapely.geometry import LineString

    line = LineString([
        (0, 0),
        (3, 4),
    ])

    class Row:
        geometry = line

    measurement, unit, status = calculate_measurement(Row())

    assert measurement == 5.0
    assert unit == "m"
    assert status == "COMPLETED"


def test_point_has_no_measurement():
    from shapely.geometry import Point

    class Row:
        geometry = Point(0, 0)

    measurement, unit, status = calculate_measurement(Row())

    assert measurement is None
    assert unit is None
    assert status == "NOT_APPLICABLE"