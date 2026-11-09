from sqlalchemy import (
    BigInteger,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import mapped_column
from .base import Base


class Metric(Base):
    __tablename__ = "metrics"
    __table_args__ = (UniqueConstraint("issue_id", "title", "datetime_calculated"),)
    id = mapped_column(Integer, primary_key=True)
    issue_id = mapped_column(BigInteger, ForeignKey("accelo.issues.id"), nullable=False)
    title = mapped_column(String, nullable=False)
    value = mapped_column(Float, nullable=True)
    datetime_calculated = mapped_column(DateTime(timezone=True), nullable=False)
