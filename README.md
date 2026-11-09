# GIS KPI Metric Database

Shared SQLAlchemy models, Pydantic schemas, data services and Alembic migrations. This is the sole persistence owner for the GIS KPI project; it is a normal Python library, not an Airflow provider.

```sh
pip install -e '.[dev]'
export GIS_KPI_DATABASE_URL='postgresql+psycopg://user:password@host:5432/gis_kpi'
gis-kpi-metric-db upgrade head
gis-kpi-metric-db current
```

Imports are `gis_kpi_metric_db.models`, `.schemas` and `.services`. Runtime code and migration resources live in `src/gis_kpi_metric_db`; PostgreSQL deployments install the `postgres` extra. No Airflow or calculator dependency is required.

**Existing databases:** revision `0001` moved unchanged from the jobs repository. Keep the existing `alembic_version` state and data. Run `upgrade head`; do not recreate or stamp the database solely because the migration files moved. The CLI works from any directory using resources shipped in the wheel.

For new revisions, use the source checkout: update models, then run `alembic revision --autogenerate -m 'description'` and review the result. The revision template and root source configuration are included. Rollback of the initial revision drops application tables; review/back up before downgrading.

Documentation follows the providers' structure: `docs/guides`, `docs/references`, `docs/changelog`, one `docs/conf.py`, and root `Makefile`. See [migrations](docs/guides/migrations.rst), [services](docs/guides/services.rst) and [releases](docs/guides/releases.rst).

```sh
pytest
python -m build
python -m twine check dist/*
make html
make pdf
```

Set `TEST_POSTGRES_URL` to an empty disposable PostgreSQL database for migration integration tests. Git flow is feature → integration → release → production; Gitea production releases require `RELEASE_TOKEN`. GitHub validates only. Database dependencies are public; this package does not need private calculator access.
