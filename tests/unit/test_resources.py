from importlib.resources import files
import shutil
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory


def test_installed_revision_history_and_template(tmp_path):
    root = files("gis_kpi_metric_db")
    migrations = tmp_path / "migrations"
    shutil.copytree(
        str(root / "migrations"),
        migrations,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    config = Config()
    config.set_main_option("script_location", str(migrations))
    scripts = ScriptDirectory.from_config(config)
    assert scripts.get_current_head() == "0001"
    revision = command.revision(config, message="test source revision", rev_id="0002")
    assert revision.down_revision == "0001"
