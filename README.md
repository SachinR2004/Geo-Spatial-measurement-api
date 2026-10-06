The inner triple backticks in the architecture diagram and code blocks prematurely closed the code window.

To write the complete README directly to your project without any copy-paste or formatting issues, run this single command in your terminal from your project root:

```bash
cat << 'EOF' > README.md
# Geospatial File Measurement API

A production-ready FastAPI backend service designed to ingest geospatial vector files (ESRI Shapefile .zip and KML), dynamically reproject coordinates to local projected coordinate reference systems (UTM), calculate accurate metric measurements (polygon area, line length), and persist results in PostgreSQL.

---

## Architecture Overview

Upload (POST /api/files/)
       │
       ▼
File Parser Service (GeoPandas + Fiona)
       │ Reads vector layers, handles temporary archives, validates CRS
       ▼
CRS Reprojection Engine (PyProj)
       │ Computes centroid in WGS84 and maps to local UTM Zone (EPSG:326XX / 327XX)
       ▼
Measurement Engine (Shapely)
       │ Calculates Polygon Area (m², ha, km²) & LineString Length (m, km)
       ▼
PostgreSQL Database Record (Status: COMPLETED)

---

## Technical Decisions & Alternatives Considered

### 1. Coordinate Systems: Dynamic UTM Selection vs Alternatives
* **Geographic Coordinates (EPSG:4326):** Coordinates are expressed in angular degrees (latitude/longitude). Direct planar distance and area calculations on angular coordinates yield meaningless numbers (degrees²) and do not account for Earth's ellipsoidal curvature.
* **Web Mercator (EPSG:3857):** While Web Mercator is projected in linear meters, it introduces massive scale and area distortion away from the equator (up to 100%+ distortion at higher latitudes). It is suited for web tile display, not engineering or land survey measurements.
* **Selected Solution (Dynamic UTM Projection via PyProj):** Universal Transverse Mercator (UTM) divides the world into 60 longitudinal zones of 6° width. The service determines the geometric centroid of each feature in WGS84 and projects it into its specific local UTM zone (e.g., EPSG:32643 for Bengaluru). This provides conformal, metric measurements with minimal local distortion (< 0.1%).

### 2. File Format Handling & Memory Management
* **ESRI Shapefiles:** Because shapefiles are multi-file collections (.shp, .shx, .dbf, .prj), the parser safely handles .zip archives using temporary filesystem directories and context-managed cleanup, preventing disk bloat.
* **Layer Isolation:** In compliance with the ESRI Shapefile specification (single geometry type per layer), the parser gracefully extracts valid features while marking unsupported types (such as Point geometries) as NOT_APPLICABLE rather than crashing the pipeline.

### 3. Application Lifecycle & Database Management
* Utilizes FastAPI's modern lifespan context manager to initialize database schemas on startup.
* Implements a decoupled SQLAlchemy repository layer, facilitating clean migrations and isolated testing.

---

## Tech Stack

* **Framework:** FastAPI (Python 3.10+)
* **Database:** PostgreSQL (Production / Docker), SQLite (Local Testing)
* **ORM:** SQLAlchemy 2.0
* **GIS / Spatial Libraries:** GeoPandas, Shapely, PyProj, Fiona
* **Testing:** Pytest, HTTPX
* **Containerization:** Docker & Docker Compose

---

## Project Structure


```

.
├── Dockerfile
├── README.md
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── app
│   ├── **init**.py
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

## Getting Started

### Prerequisites
* Docker and Docker Compose installed and running.
* Alternatively, Python 3.10+ with system GDAL/GEOS libraries installed.

### Running with Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone [https://github.com/SachinR2004/Geo-Spatial-measurement-api.git](https://github.com/SachinR2004/Geo-Spatial-measurement-api.git)
   cd Geo-Spatial-measurement-api

```

2. Start the API and PostgreSQL database:
```bash
docker compose up --build -d

```


3. Check service health:
```bash
curl http://localhost:8000/health
# Returns: {"status":"ok"}

```


4. Interactive Swagger documentation will be available at:
```
http://localhost:8000/docs

```



---

## API Reference

### 1. Upload Geospatial File

`POST /api/files/`

Accepts `multipart/form-data` with a single file parameter. Supports `.zip` (ESRI Shapefile archives) and `.kml`.

**cURL Example:**

```bash
curl -X POST "http://localhost:8000/api/files/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/sample_shapefile.zip"

```

**Response (`200 OK`):**

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

### 2. Get File Processing Details

`GET /api/files/{id}`

**cURL Example:**

```bash
curl http://localhost:8000/api/files/c509d540-1f46-4425-b69b-bdc2c74f1d30

```

**Response (`200 OK`):**

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

### 3. Get Calculated Measurements

`GET /api/files/{id}/measurements`

**cURL Example:**

```bash
curl http://localhost:8000/api/files/c509d540-1f46-4425-b69b-bdc2c74f1d30/measurements

```

**Response (`200 OK`):**

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

## Running Automated Tests

The test suite covers file parsing, UTM reprojection accuracy, geometry measurements, and HTTP endpoint workflows.

To run tests locally:

```bash
pytest -v

```

Expected output:

```text
tests/test_crs.py::test_geographic_crs_is_projected PASSED
tests/test_files.py::test_upload_kml PASSED
tests/test_files.py::test_upload_shapefile_zip PASSED
tests/test_files.py::test_reject_unsupported_file PASSED
tests/test_files.py::test_get_file PASSED
tests/test_files.py::test_get_measurements PASSED
tests/test_measurements.py::test_polygon_measurement PASSED
tests/test_measurements.py::test_linestring_measurement PASSED
tests/test_measurements.py::test_point_has_no_measurement PASSED
tests/test_parser.py::test_parse_kml PASSED

========================= 10 passed in 1.57s =========================

```

---

## Learnings & Future Scope

### Learnings

* **Geospatial Projections & Geodesy:** Handling datum distortions when converting unprojected ellipsoidal coordinates (WGS84) to local conformal cartesian planes.
* **Format-Specific Constraints:** Managing the strict single-geometry limitations of the ESRI Shapefile format versus open multi-geometry KML schemas.
* **Docker Multi-Stage Spatial Runtimes:** Balancing lightweight image footprints against necessary C/C++ dependencies (libgdal-dev, libpq-dev).

### Future Scope

* **Distributed Task Execution:** Integrate Celery and Redis to process multi-gigabyte spatial rasters and large vector archives asynchronously.
* **Spatial Database (PostGIS):** Migrate from standard relational columns to native PostGIS geometry columns via GeoAlchemy2 to unlock spatial indexing (R-Tree/GiST), bounding box queries, and spatial joins directly at the database layer.
* **Cloud Native Storage:** Decouple file ingestion from disk using AWS S3 / Cloudflare R2 presigned URLs.
EOF

```

After pasting and executing that command, update GitHub:

```bash
git add README.md
git commit -m "docs: finalize assessment documentation and architecture guide"
git push origin main

```
