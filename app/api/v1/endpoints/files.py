import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.measurement import Measurement
from app.models.uploaded_file import UploadedFile
from app.services.crs_service import prepare_for_measurement
from app.services.measurement_service import calculate_measurement
from app.services.parser_service import parse_geospatial_file


router = APIRouter()


@router.post("/")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    extension = Path(file.filename or "").suffix.lower()

    if extension not in {".zip", ".kml"}:
        raise HTTPException(
            status_code=400,
            detail="Only .zip and .kml files are supported.",
        )

    file_type = "shapefile" if extension == ".zip" else "kml"

    uploaded_file = UploadedFile(
        filename=file.filename,
        file_type=file_type,
        status="PROCESSING",
    )

    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=extension,
            delete=False,
        ) as temp_file:
            temp_file.write(file.file.read())
            temp_path = temp_file.name

        gdf = parse_geospatial_file(temp_path)
        measured_gdf = prepare_for_measurement(gdf)

        uploaded_file.feature_count = len(measured_gdf)
        uploaded_file.crs = str(gdf.crs)

        for index, row in measured_gdf.iterrows():
            measurement, unit, status = calculate_measurement(row)

            record = Measurement(
                file_id=uploaded_file.id,
                feature_index=int(index),
                geometry_type=row.geometry.geom_type,
                measurement=measurement,
                measurement_unit=unit,
                status=status,
            )

            db.add(record)

        uploaded_file.status = "COMPLETED"
        db.commit()

        return {
            "id": uploaded_file.id,
            "filename": uploaded_file.filename,
            "feature_count": uploaded_file.feature_count,
            "crs": uploaded_file.crs,
            "status": uploaded_file.status,
        }

    except Exception as exc:
        db.rollback()

        uploaded_file.status = "FAILED"
        db.commit()

        raise HTTPException(
            status_code=400,
            detail=f"File processing failed: {str(exc)}",
        )

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            
@router.get("/{file_id}")
def get_file(
    file_id: str,
    db: Session = Depends(get_db),
):
    uploaded_file = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id)
        .first()
    )

    if uploaded_file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    return {
        "id": uploaded_file.id,
        "filename": uploaded_file.filename,
        "feature_count": uploaded_file.feature_count,
        "crs": uploaded_file.crs,
        "status": uploaded_file.status,
        "created_at": uploaded_file.created_at,
    }


@router.get("/{file_id}/measurements")
def get_measurements(
    file_id: str,
    db: Session = Depends(get_db),
):
    uploaded_file = (
        db.query(UploadedFile)
        .filter(UploadedFile.id == file_id)
        .first()
    )

    if uploaded_file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found.",
        )

    measurements = (
        db.query(Measurement)
        .filter(Measurement.file_id == file_id)
        .order_by(Measurement.feature_index)
        .all()
    )

    return {
        "file_id": file_id,
        "measurements": [
            {
                "feature_index": item.feature_index,
                "geometry_type": item.geometry_type,
                "measurement": item.measurement,
                "unit": item.measurement_unit,
                "status": item.status,
                "error_message": item.error_message,
            }
            for item in measurements
        ],
    }