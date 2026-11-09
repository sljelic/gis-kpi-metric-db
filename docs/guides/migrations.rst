Alembic migrations
==================

The installed distribution contains the complete migration history. Set the
application database URL, pointing to the same database as the Airflow
GIS_KPI_POSTGRESS_CONNECTION::

    export GIS_KPI_DATABASE_URL='postgresql+psycopg://user:password@host:5432/gis_kpi'
    gis-kpi-metric-data-service heads
    gis-kpi-metric-data-service history --verbose
    gis-kpi-metric-data-service upgrade head
    gis-kpi-metric-data-service current

The CLI works from any working directory. It reads packaged alembic.ini and
migration resources; it does not read Airflow connections. PostgreSQL must
already contain the gis_kpi database. The migration role needs CREATE/ALTER
permission for accelo, adms and the default schema. Supply credentials through
your environment/secret manager and URL-encode special characters in passwords.

Existing deployments
--------------------

Revision ``0001`` was moved unchanged from gis-kpi-metric-jobs. The revision ID,
parent, schema names, constraints and alembic_version table are preserved.
An existing database already at 0001 needs no schema recreation: install this
package and run upgrade head normally. Do not drop/recreate tables or stamp a
new revision just because migration ownership moved.

Run migrations once per deployment, before enabling DAGs that require the
schema. They migrate the KPI database, not the Airflow metadata database.
Running upgrade head again applies only pending revisions.

Review SQL without applying it::

    gis-kpi-metric-data-service upgrade head --sql > migration.sql

That renders the path from base; for a database at 0001 use
``gis-kpi-metric-data-service upgrade 0001:head --sql``.

Adding migrations
-----------------

Create new revisions in the separate gis-kpi-metric-data-service source repository,
release a new package version, then update requirements.txt here. Do not
write revisions into installed site-packages.

Rollback and adoption
---------------------

Inspect history/current and back up data before rollback::

    gis-kpi-metric-data-service downgrade -1
    gis-kpi-metric-data-service upgrade head

Downgrading the initial revision drops the application tables and data.
``stamp`` only changes revision bookkeeping; use it only after confirming that
an existing unmanaged schema exactly matches the selected revision.
