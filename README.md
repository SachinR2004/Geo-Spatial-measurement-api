# Geospatial File Measurement API

A production-ready FastAPI backend service designed to ingest geospatial vector files (ESRI Shapefile `.zip` archives and KML documents), dynamically reproject geometries into local metric UTM coordinate systems, and calculate precise measurements (polygon area, line length) persisted in PostgreSQL.

---

## Technical Decisions & Coordinate Reference Systems

### 1. Dynamic UTM Projection vs Alternatives
* **Geographic WGS84 (EPSG:4326):** Stores data in angular degrees (latitude/longitude). Calculating planar distances and areas directly on degrees yields invalid numbers that do not account for Earth's curvature.
* **Web Mercator (EPSG:3857):** While measured in meters, Web Mercator introduces severe scale and area distortion away from the equator (exceeding 100% distortion at higher latitudes). It is suitable for interactive web mapping, not geometric calculations.
* **Chosen Approach (Dynamic UTM via PyProj):** The engine calculates the geometric centroid of each feature in WGS84 and maps it directly to its local Universal Transverse Mercator (UTM) zone (e.g., `EPSG:32643` for Bengaluru). This ensures conformal, high-precision metric calculations with less than 0.1% local scale distortion.

### 2. File Format Handling & Memory Management
* **ESRI Shapefiles:** Because Shapefiles consist of mandatory sidecar files (`.shp`, `.shx`, `.dbf`, `.prj`), uploaded `.zip` archives are extracted into isolated temporary directories and automatically purged after extraction.
* **Layer Constraints:** In line with the ESRI Shapefile specification (one geometry type per layer), non-measurable entities (like `Point` features) are flagged with status `NOT_APPLICABLE` rather than raising uncaught exceptions.

### 3. Application Lifecycle
* Database table schemas are created on application startup via FastAPI's `lifespan` context manager, allowing zero-setup local deployment with Docker Compose.

---

## Tech Stack

* **Framework:** FastAPI (Python 3.10+)
* **Database:** PostgreSQL (Containerized), SQLite (Local Testing)
* **ORM:** SQLAlchemy 2.0
* **GIS Stack:** GeoPandas, Shapely, PyProj, Fiona / GDAL
* **Testing:** Pytest, HTTPX
* **Containerization:** Docker & Docker Compose

---

## Project Structure

```text
.
├── Dockerfile
├── README.md
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── app
│   ├── __init__.py
│   ├── main.py
│   ├── api
│   │   ├── deps.py
│   │   └── v1
│   │       ├── router.py
│   │       └── endpoints
│   │           └── files.py
│   ├── core
│   │   └── config.py
│   ├── db
│   │   ├── base.py
│   │   └── session.py
│   ├── models
│   │   ├── measurement.py
│   │   └── uploaded_file.py
│   ├── schemas
│   │   ├── file.py
│   │   └── measurement.py
│   └── services
│       ├── crs_service.py
│       ├── measurement_service.py
│       └── parser_service.py
├── sample_data
│   ├── sample_shapefile.zip
│   └── test_geospatial.kml
└── tests
    ├── conftest.py
    ├── test_crs.py
    ├── test_files.py
    ├── test_measurements.py
    └── test_parser.py
```

---

## Quickstart (Docker Compose)

1. Start PostgreSQL and the API service:
```bash
docker compose up --build -d
```

2. Verify system health:
```bash
curl http://localhost:8000/health
# Returns: {"status":"ok"}
```

3. Interactive Swagger documentation is available at:
```text
http://localhost:8000/docs
```

---

## API Endpoints

### 1. Upload Geospatial Archive
* **Method:** `POST`
* **Path:** `/api/files/`
* **Body:** `multipart/form-data` with `file` (`.zip` or `.kml`)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/files/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/sample_shapefile.zip"
```

**Example Response (`200 OK`):**
```json
{
  "id": "c509d540-1f46-4425-b69b-bdc2c74f1d30",
  "filename": "sample_shapefile.zip",
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "COMPLETED"
}
```

---

### 2. Fetch File Processing Metadata
* **Method:** `GET`
* **Path:** `/api/files/{id}`

**Example Request:**
```bash
curl http://localhost:8000/api/files/c509d540-1f46-4425-b69b-bdc2c74f1d30
```

**Example Response (`200 OK`):**
```json
{
  "id": "c509d540-1f46-4425-b69b-bdc2c74f1d30",
  "filename": "sample_shapefile.zip",
  "feature_count": 3,
  "crs": "EPSG:4326",
  "status": "COMPLETED",
  "created_at": "2026-10-06T19:01:33.370395"
}
```

---

### 3. Fetch Geometric Measurements
* **Method:** `GET`
* **Path:** `/api/files/{id}/measurements`

**Example Request:**
```bash
curl http://localhost:8000/api/files/c509d540-1f46-4425-b69b-bdc2c74f1d30/measurements
```

**Example Response (`200 OK`):**
```json
{
  "file_id": "c509d540-1f46-4425-b69b-bdc2c74f1d30",
  "measurements": [
    {
      "feature_index": 0,
      "geometry_type": "Polygon",
      "measurement": 300422.8,
      "unit": "m²",
      "status": "COMPLETED",
      "error_message": null
    },
    {
      "feature_index": 1,
      "geometry_type": "Polygon",
      "measurement": 300425.5,
      "unit": "m²",
      "status": "COMPLETED",
      "error_message": null
    },
    {
      "feature_index": 2,
      "geometry_type": "Polygon",
      "measurement": 300415.7,
      "unit": "m²",
      "status": "COMPLETED",
      "error_message": null
    }
  ]
}
```

---

## Testing

Run the automated test suite locally:
```bash
pytest -v
```

Coverage includes CRS transformation, KML parsing, Shapefile extraction, unsupported file rejection, and measurement endpoint verification (10 passing tests).

---
