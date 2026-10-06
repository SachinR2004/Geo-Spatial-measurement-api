from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    file_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("uploaded_files.id"),
        nullable=False,
    )

    feature_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    geometry_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    measurement: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    measurement_unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )