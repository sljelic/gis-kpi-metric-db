from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from gis_kpi_metric_db import models as m, schemas as s
from gis_kpi_metric_db.services import CalendarService, IssueService, MetricService


@pytest.fixture
def session():
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def attach(conn, _):
        conn.execute("ATTACH DATABASE ':memory:' AS accelo")
        conn.execute("ATTACH DATABASE ':memory:' AS adms")

    m.Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def test_ingest_calculate_persist_retry(session):
    service = IssueService(session)
    service.create(
        {
            "id": 1,
            "title": "One",
            "class": {"title": "Data maintenance"},
            "issue_type": {"title": "GIS As-built"},
            "date_modified": 10,
            "date_submitted": 1777885200,
            "date_resolved": 1777914000,
        }
    )
    service.create(
        {"id": 2, "title": "Two", "class": {"title": "Reactive"}, "date_modified": 20}
    )
    session.add_all(
        [
            m.IssueProgression(
                id=1,
                to_id=1,
                to_title="Pending WEGIS QA",
                against_type="issues",
                against_id=1,
                date_modified=1777888800,
            ),
            m.IssueProgression(
                id=2,
                to_id=2,
                to_title="Open",
                against_type="issues",
                against_id=1,
                date_modified=1777892400,
            ),
            m.IssueProgression(
                id=3,
                to_id=1,
                to_title="Bad join",
                against_type="projects",
                against_id=1,
                date_modified=1,
            ),
            m.ExtensionValue(
                id=1,
                field_type="text",
                file_name="Contractor",
                value="Omexom",
                field_name="Contractor",
                link_id=1,
                link_type="issues",
            ),
        ]
    )
    session.flush()
    obj = service.get(
        type="GIS As-built",
        class_="Data maintenance",
        modified_after=0,
        modified_before=15,
    )[0]
    assert len(obj.progressions) == 2 and len(obj.extensions) == 1
    assert service.getById(1, progressions=[], extensions=[]).progressions == []
    assert len(service.getById(1, progressions=["Open"]).progressions) == 1
    assert len(service.get()) == 2
    metric = s.Metric(issue_id=obj.issue_id, title="OP2", value=7 * 3600)
    assert metric.value == 7 * 3600
    metrics = MetricService(session)
    first = metrics.create(metric)
    assert metrics.create(metric).id == first.id
    assert len(metrics.get(issue_id=1, title="OP2")) == 1
    assert metrics.getById(first.id).value == 7 * 3600
    session.commit()
    assert service.delete(2) and service.getById(2) is None


def test_calendar_crud_filters_and_local_day(session):
    service = CalendarService(session, "Pacific/Auckland")
    from zoneinfo import ZoneInfo

    zone = ZoneInfo("Pacific/Auckland")
    holiday = s.Holiday(
        id=1,
        title="Test",
        datetime_from=datetime(2026, 4, 5, tzinfo=zone),
        datetime_to=datetime(2026, 4, 6, tzinfo=zone),
    )
    service.create(holiday)
    obj = service.get(year=2026, titles=["Test"])[0]
    assert obj.datetime_to.timestamp() - obj.datetime_from.timestamp() == 25 * 3600
    assert service.get(year=2025) == []
    service.update(1, holiday.model_copy(update={"title": "Changed"}))
    assert service.getById(1).title == "Changed"
    assert service.delete(1)
