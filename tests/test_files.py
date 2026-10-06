from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_kml():
    with open("sample_data/test_geospatial.kml", "rb") as file:
        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "test_geospatial.kml",
                    file,
                    "application/vnd.google-earth.kml+xml",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test_geospatial.kml"
    assert data["feature_count"] == 3
    assert data["crs"] == "EPSG:4326"
    assert data["status"] == "COMPLETED"


def test_upload_shapefile_zip():
    with open("sample_data/sample_shapefile.zip", "rb") as file:
        response = client.post(
            "/api/files/",
            files={
                "file": (
                    "sample_shapefile.zip",
                    file,
                    "application/zip",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "sample_shapefile.zip"
    assert data["feature_count"] == 3
    assert data["status"] == "COMPLETED"


def test_reject_unsupported_file():
    response = client.post(
        "/api/files/",
        files={
            "file": (
                "test.txt",
                b"this is not a geospatial file",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "Only .zip and .kml files are supported." in response.json()["detail"]


def test_get_file():
    with open("sample_data/test_geospatial.kml", "rb") as file:
        upload_response = client.post(
            "/api/files/",
            files={
                "file": (
                    "test_geospatial.kml",
                    file,
                    "application/vnd.google-earth.kml+xml",
                )
            },
        )

    file_id = upload_response.json()["id"]

    response = client.get(f"/api/files/{file_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == file_id
    assert data["filename"] == "test_geospatial.kml"
    assert data["feature_count"] == 3
    assert data["status"] == "COMPLETED"


def test_get_measurements():
    with open("sample_data/test_geospatial.kml", "rb") as file:
        upload_response = client.post(
            "/api/files/",
            files={
                "file": (
                    "test_geospatial.kml",
                    file,
                    "application/vnd.google-earth.kml+xml",
                )
            },
        )

    file_id = upload_response.json()["id"]

    response = client.get(
        f"/api/files/{file_id}/measurements"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["measurements"]) == 3

    assert data["measurements"][0]["geometry_type"] == "Polygon"
    assert data["measurements"][0]["status"] == "COMPLETED"

    assert data["measurements"][1]["geometry_type"] == "LineString"
    assert data["measurements"][1]["status"] == "COMPLETED"

    assert data["measurements"][2]["geometry_type"] == "Point"
    assert data["measurements"][2]["status"] == "NOT_APPLICABLE"