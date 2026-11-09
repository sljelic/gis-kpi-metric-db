from sqlalchemy import BigInteger, Boolean, JSON, String
from sqlalchemy.orm import mapped_column
from ..base import Base


class ExtensionValue(Base):
    __tablename__ = "extension_values"
    __table_args__ = {"schema": "accelo"}
    id = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    field_type = mapped_column(String, nullable=False)
    file_name = mapped_column(String, nullable=False)
    value = mapped_column(JSON(), nullable=False)
    values = mapped_column(JSON(none_as_null=True), nullable=True)
    field_id = mapped_column(BigInteger, nullable=True)
    link_id = mapped_column(BigInteger, nullable=True)
    link_type = mapped_column(String, nullable=True)
    link_type_id = mapped_column(BigInteger, nullable=True)
    date_modified = mapped_column(BigInteger, nullable=True)
    modified_by = mapped_column(JSON(none_as_null=True), nullable=True)
    default_value = mapped_column(JSON(none_as_null=True), nullable=True)
    is_sensitive = mapped_column(Boolean, nullable=True)
    is_important = mapped_column(Boolean, nullable=True)
    is_exported = mapped_column(Boolean, nullable=True)
    value_id = mapped_column(BigInteger, nullable=True)
    value_type = mapped_column(String, nullable=True)
    field_description = mapped_column(String, nullable=True)
    field_name = mapped_column(String, nullable=True)
