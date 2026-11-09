"""Validated application objects, independent of Airflow."""

from datetime import datetime, timezone
from typing import Any
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    AliasChoices,
    model_validator,
    field_validator,
)


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class Holiday(Schema):
    id: int = Field(ge=0)
    title: str
    datetime_from: datetime
    datetime_to: datetime

    @model_validator(mode="after")
    def check_interval(self):
        if self.datetime_from.tzinfo is None or self.datetime_to.tzinfo is None:
            raise ValueError("Holiday endpoints must be timezone-aware")
        if self.datetime_to <= self.datetime_from:
            raise ValueError("Holiday end must follow start")
        return self


class Progression(Schema):
    against_id: int | None = None
    to_title: str
    date_modified: int


class Extension(Schema):
    link_id: int | None = None
    field_name: str
    value: Any = None


class Issue(Schema):
    issue_id: int = Field(ge=0, validation_alias=AliasChoices("issue_id", "id"))
    title: str
    type: str | None = None
    class_: str | None = Field(default=None, alias="class")
    date_submitted: int | None = None
    date_resolved: int | None = None
    progressions: list[Progression] = Field(default_factory=list)
    extensions: list[Extension] = Field(default_factory=list)

    @field_validator("type", "class_", mode="before")
    @classmethod
    def object_title(cls, value):
        return (
            value.get("title")
            if isinstance(value, dict)
            else (None if isinstance(value, int) else value)
        )


class Metric(Schema):
    id: int | None = None
    issue_id: int = Field(ge=0)
    title: str
    value: float | None = Field(default=None, allow_inf_nan=False)
    datetime_calculated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @field_validator("datetime_calculated")
    @classmethod
    def aware(cls, value):
        if value.tzinfo is None:
            raise ValueError("Calculation timestamp must be timezone-aware")
        return value
