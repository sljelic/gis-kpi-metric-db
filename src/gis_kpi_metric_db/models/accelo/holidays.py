from sqlalchemy import BigInteger, Boolean, JSON, String
from sqlalchemy.orm import mapped_column
from ..base import Base


class Holiday(Base):
    __tablename__ = "holidays"
    __table_args__ = {"schema": "accelo"}
    id = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    title = mapped_column(String, nullable=False)
    date = mapped_column(BigInteger, nullable=False)
