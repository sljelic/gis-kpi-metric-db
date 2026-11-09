import os
from alembic import context
from sqlalchemy import create_engine
from gis_kpi_metric_db.models import Base

if context.is_offline_mode():
    context.configure(
        url=os.environ["GIS_KPI_DATABASE_URL"],
        target_metadata=Base.metadata,
        literal_binds=True,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(os.environ["GIS_KPI_DATABASE_URL"])
    with engine.connect() as connection:
        context.configure(
            connection=connection, target_metadata=Base.metadata, include_schemas=True
        )
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()
