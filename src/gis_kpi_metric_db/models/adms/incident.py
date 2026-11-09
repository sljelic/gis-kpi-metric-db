from sqlalchemy import BigInteger, Boolean, JSON, String, UniqueConstraint
from sqlalchemy.orm import mapped_column
from ..base import Base


class Incident(Base):
    __tablename__ = "incident"
    __table_args__ = (UniqueConstraint("title"), {"schema": "adms"})
    incident_id = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    title = mapped_column(String, nullable=False)
    type_id = mapped_column(BigInteger, nullable=False)
    against_type = mapped_column(String, nullable=False)
    against_id = mapped_column(BigInteger, nullable=False)
    standing = mapped_column(String, nullable=True)
    status_id = mapped_column(BigInteger, nullable=True)
    affiliation_id = mapped_column(BigInteger, nullable=True)
    date_started = mapped_column(BigInteger, nullable=True)
    date_due = mapped_column(BigInteger, nullable=True)
    description = mapped_column(String, nullable=True)
    class_id = mapped_column(BigInteger, nullable=True)
    assignee = mapped_column(BigInteger, nullable=True)
    priority_id = mapped_column(BigInteger, nullable=True)
    date_created_in_accelo = mapped_column(BigInteger, nullable=True)
