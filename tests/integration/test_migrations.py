"""Installed migration resources must preserve existing revision state and data."""

import os
import subprocess
import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine, inspect, text
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from gis_kpi_metric_db.models import Base

pytestmark = pytest.mark.skipif(
    not os.environ.get("TEST_POSTGRES_URL"),
    reason="Set TEST_POSTGRES_URL to an empty disposable PostgreSQL database",
)


def test_migration_upgrade_replay_metadata_and_downgrade(tmp_path):
    engine = create_engine(os.environ["TEST_POSTGRES_URL"])
    env = {**os.environ, "GIS_KPI_DATABASE_URL": os.environ["TEST_POSTGRES_URL"]}

    def run(*args):
        return subprocess.run(
            [sys.executable, "-m", "gis_kpi_metric_db.cli", *args],
            cwd=tmp_path,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )

    try:
        run("upgrade", "head")
        with engine.begin() as conn:
            assert (
                conn.scalar(text("SELECT version_num FROM alembic_version")) == "0001"
            )
            conn.execute(
                text("INSERT INTO accelo.issues (id,title) VALUES (1,'preserved')")
            )
        run("upgrade", "head")
        assert "0001" in run("current").stdout
        with engine.connect() as conn:
            assert (
                conn.scalar(text("SELECT title FROM accelo.issues WHERE id=1"))
                == "preserved"
            )
            context = MigrationContext.configure(
                conn,
                opts={
                    "include_schemas": True,
                    "include_object": lambda obj, name, type_, reflected, compare_to: (
                        name != "alembic_version"
                    ),
                },
            )
            assert compare_metadata(context, Base.metadata) == []
        run("downgrade", "base")
        with engine.connect() as conn:
            assert not inspect(conn).has_table("issues", schema="accelo")
        run("upgrade", "head")
    finally:
        run("downgrade", "base")
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS alembic_version"))
        engine.dispose()
