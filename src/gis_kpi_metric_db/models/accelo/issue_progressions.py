from sqlalchemy import BigInteger, Boolean, JSON, String
from sqlalchemy.orm import mapped_column
from ..base import Base


class IssueProgression(Base):
    __tablename__ = "issue_progressions"
    __table_args__ = {"schema": "accelo"}
    id = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    to_id = mapped_column(BigInteger, nullable=False)
    to_title = mapped_column(String, nullable=False)
    against_type = mapped_column(String, nullable=True)
    against_id = mapped_column(BigInteger, nullable=True)
    modified_by = mapped_column(BigInteger, nullable=True)
    date_modified = mapped_column(BigInteger, nullable=True)
