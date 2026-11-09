Models, DTOs and services
=========================

Models use the accelo and adms schemas plus the metrics table. JSON columns
retain object-or-ID and dynamic extension values; Unix timestamps use BIGINT.
Python ``class_`` maps to API/database class.

CalendarService, IssueService and MetricService accept a caller-owned
SQLAlchemy Session. They flush but never commit. The caller owns transaction
and connection lifetime. CRUD and AND-combined filters are supported.

IssueService child selectors use None for all, [] for none, and nonempty lists
for matching progression titles/extension field names. Child filtering does
not remove parent issues; link types are constrained to issues. Calculators
need all status transitions to preserve exclusion end timestamps.

Metric snapshots are unique by issue_id, title and datetime_calculated.
MetricService.create reuses that snapshot on retry. Supply the same UTC
calculation timestamp for retries; later runs retain history. CalendarService
uses full local holiday dates, including DST days.
