"""Alembic CLI using migration resources from the installed DB distribution."""

from importlib.resources import files
from alembic.config import CommandLine


def main(argv=None):
    cli = CommandLine(prog="gis-kpi-metric-db")
    cli.parser.set_defaults(config=[str(files("gis_kpi_metric_db") / "alembic.ini")])
    cli.main(argv)


if __name__ == "__main__":
    main()
