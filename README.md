# GIS KPI database deployment

This is a database deployment/configuration repository, **not** a Python package or Airflow provider. Do not run `pip install .` or build a wheel here.

The separate [gis-kpi-metric-data-service](https://github.com/sljelic/gis-kpi-metric-data-service) library owns models, schemas and services. Run the application migrations from the root of [gis-kpi-metric-jobs](https://github.com/sljelic/gis-kpi-metric-jobs), using its `alembic.ini` and `migrations/`.

Configure the internal Python index and read credentials as documented in [REGISTRY.md](REGISTRY.md). Database credentials stay in the deployment environment. The application database is separate from Airflow's metadata database.

Revision `0001` and existing database revision state are preserved. This repository's CI validates dependency installation and documentation.


## Unified Python registry

Use ordinary pip package versions through the configured single internal index. This deployment repository is not built or uploaded as a package. See [REGISTRY.md](REGISTRY.md) for endpoint configuration, read credentials and container netrc secrets.
