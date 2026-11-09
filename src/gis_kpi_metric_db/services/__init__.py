"""Session-scoped services. The caller owns commit/rollback and connection lifetime."""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import select
from .. import models as m
from .. import schemas as s


class CRUDService:
    def __init__(self, session):
        self.session = session

    def delete(self, id):
        obj = self.session.get(self.model, id)
        if obj is None:
            return False
        self.session.delete(obj)
        self.session.flush()
        return True

    def _save(self, id, values):
        obj = self.session.get(self.model, id) if id is not None else None
        if obj is None:
            obj = self.model(**values)
            self.session.add(obj)
        else:
            for key, value in values.items():
                setattr(obj, key, value)
        self.session.flush()
        return obj


class CalendarService(CRUDService):
    model = m.Holiday

    def __init__(self, session, timezone="Pacific/Auckland"):
        super().__init__(session)
        self.zone = ZoneInfo(timezone)

    def _schema(self, obj):
        day = datetime.fromtimestamp(obj.date, self.zone).date()
        return s.Holiday(
            id=obj.id,
            title=obj.title,
            datetime_from=datetime.combine(day, time(), self.zone),
            datetime_to=datetime.combine(day + timedelta(days=1), time(), self.zone),
        )

    def getById(self, id):
        obj = self.session.get(self.model, id)
        return self._schema(obj) if obj is not None else None

    def get(self, year=None, after=None, before=None, titles=None):
        stmt = select(self.model)
        if year is not None:
            stmt = stmt.where(
                self.model.date
                >= int(datetime(year, 1, 1, tzinfo=self.zone).timestamp()),
                self.model.date
                < int(datetime(year + 1, 1, 1, tzinfo=self.zone).timestamp()),
            )
        if after is not None:
            stmt = stmt.where(
                self.model.date >= int(after.timestamp())
                if isinstance(after, datetime)
                else self.model.date >= after
            )
        if before is not None:
            stmt = stmt.where(
                self.model.date < int(before.timestamp())
                if isinstance(before, datetime)
                else self.model.date < before
            )
        if titles is not None:
            stmt = stmt.where(self.model.title.in_(titles))
        return [
            self._schema(o)
            for o in self.session.scalars(stmt.order_by(self.model.date, self.model.id))
        ]

    def create(self, holiday):
        return self.update(holiday.id, holiday)

    def update(self, id, holiday):
        obj = self._save(
            id,
            dict(
                id=id, title=holiday.title, date=int(holiday.datetime_from.timestamp())
            ),
        )
        return self._schema(obj)


class IssueService(CRUDService):
    model = m.Issue

    def get(
        self,
        modified_after=None,
        modified_before=None,
        class_=None,
        type=None,
        progressions=None,
        extensions=None,
        **filters,
    ):
        class_ = filters.pop("class", class_)
        if filters:
            raise TypeError(f"Unknown filters: {list(filters)}")
        stmt = select(self.model)
        if modified_after is not None:
            stmt = stmt.where(self.model.date_modified > modified_after)
        if modified_before is not None:
            stmt = stmt.where(self.model.date_modified < modified_before)
        if class_ is not None:
            stmt = stmt.where(self.model.class_["title"].as_string() == class_)
        if type is not None:
            # issue_type supersedes deprecated type; fall back only when absent.
            from sqlalchemy import func

            stmt = stmt.where(
                func.coalesce(
                    self.model.issue_type["title"].as_string(),
                    self.model.type["title"].as_string(),
                )
                == type
            )
        return self._schemas(
            list(self.session.scalars(stmt.order_by(self.model.id))),
            progressions,
            extensions,
        )

    def _schemas(self, objects, progressions=None, extensions=None):
        ids = [o.id for o in objects]
        ps, es = {}, {}
        if ids and progressions != []:
            stmt = select(m.IssueProgression).where(
                m.IssueProgression.against_id.in_(ids),
                m.IssueProgression.against_type == "issues",
            )
            if progressions is not None:
                stmt = stmt.where(m.IssueProgression.to_title.in_(progressions))
            for p in self.session.scalars(
                stmt.order_by(m.IssueProgression.date_modified, m.IssueProgression.id)
            ):
                if p.date_modified is not None:
                    ps.setdefault(p.against_id, []).append(
                        s.Progression.model_validate(p)
                    )
        if ids and extensions != []:
            stmt = select(m.ExtensionValue).where(
                m.ExtensionValue.link_id.in_(ids),
                m.ExtensionValue.link_type == "issues",
            )
            if extensions is not None:
                stmt = stmt.where(m.ExtensionValue.field_name.in_(extensions))
            for e in self.session.scalars(stmt.order_by(m.ExtensionValue.id)):
                if e.field_name is not None:
                    es.setdefault(e.link_id, []).append(s.Extension.model_validate(e))
        return [
            s.Issue(
                issue_id=o.id,
                title=o.title,
                type=o.issue_type if o.issue_type is not None else o.type,
                class_=o.class_,
                date_submitted=o.date_submitted,
                date_resolved=o.date_resolved,
                progressions=ps.get(o.id, []),
                extensions=es.get(o.id, []),
            )
            for o in objects
        ]

    def getById(self, id, progressions=None, extensions=None):
        obj = self.session.get(self.model, id)
        return (
            self._schemas([obj], progressions, extensions)[0]
            if obj is not None
            else None
        )

    def create(self, issue):
        return self.update(
            issue.get("id") if isinstance(issue, dict) else issue.issue_id, issue
        )

    def update(self, id, issue):
        if isinstance(issue, s.Issue):
            values = dict(
                id=id,
                title=issue.title,
                issue_type={"title": issue.type} if issue.type else None,
                class_={"title": issue.class_} if issue.class_ else None,
                date_submitted=issue.date_submitted,
                date_resolved=issue.date_resolved,
            )
        else:
            values = dict(issue)
            if "class" in values:
                values["class_"] = values.pop("class")
            values["id"] = id
        obj = self._save(id, values)
        return self._schemas([obj])[0]


class MetricService(CRUDService):
    model = m.Metric

    @staticmethod
    def _schema(obj):
        # SQLite drops timezone information; persisted instants are UTC.
        from datetime import timezone

        values = {
            k: getattr(obj, k)
            for k in ("id", "issue_id", "title", "value", "datetime_calculated")
        }
        if values["datetime_calculated"].tzinfo is None:
            values["datetime_calculated"] = values["datetime_calculated"].replace(
                tzinfo=timezone.utc
            )
        return s.Metric(**values)

    def get(self, id=None, issue_id=None, title=None, from_=None, to=None):
        stmt = select(self.model)
        for key, value in [("id", id), ("issue_id", issue_id), ("title", title)]:
            if value is not None:
                stmt = stmt.where(getattr(self.model, key) == value)
        if from_ is not None:
            stmt = stmt.where(self.model.datetime_calculated >= from_)
        if to is not None:
            stmt = stmt.where(self.model.datetime_calculated < to)
        return [
            self._schema(o) for o in self.session.scalars(stmt.order_by(self.model.id))
        ]

    def getById(self, id):
        obj = self.session.get(self.model, id)
        return self._schema(obj) if obj is not None else None

    def create(self, metric):
        # A stable DAG logical timestamp makes retries idempotent.
        obj = self.session.scalar(
            select(self.model).where(
                self.model.issue_id == metric.issue_id,
                self.model.title == metric.title,
                self.model.datetime_calculated == metric.datetime_calculated,
            )
        )
        return self.update(obj.id if obj is not None else metric.id, metric)

    def update(self, id, metric):
        values = metric.model_dump(exclude={"id"})
        from datetime import timezone

        values["datetime_calculated"] = metric.datetime_calculated.astimezone(
            timezone.utc
        )
        if id is not None:
            values["id"] = id
        return self._schema(self._save(id, values))
