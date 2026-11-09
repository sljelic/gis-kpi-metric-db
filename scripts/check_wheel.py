from pathlib import Path
from importlib import metadata
from importlib.resources import files
import os
import gis_kpi_metric_db
from alembic.config import Config
from alembic.script import ScriptDirectory

assert Path(gis_kpi_metric_db.__file__).is_relative_to(Path(os.environ["VIRTUAL_ENV"]))
root = files("gis_kpi_metric_db")
assert (root / "alembic.ini").is_file()
assert (root / "migrations/script.py.mako").is_file()
config = Config(str(root / "alembic.ini"))
assert ScriptDirectory.from_config(config).get_current_head() == "0001"
dist = metadata.distribution("gis-kpi-metric-db")
assert not any(e.group == "apache_airflow_provider" for e in dist.entry_points)
assert not any("issue-metric-calculator" in req for req in dist.requires or [])
print(
    "Installed DB wheel, packaged migration history/template and dependency direction verified"
)
