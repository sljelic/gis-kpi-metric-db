# GIS KPI database deployment

This is a database deployment/configuration repository, **not** a Python package or Airflow provider. Do not run `pip install .` or build a wheel here.

The separate [gis-kpi-metric-data-service](https://github.com/sljelic/gis-kpi-metric-data-service) library owns models, schemas, services and Alembic resources. This repository installs its published version and invokes migrations:

```sh
pip install -r requirements.txt
export GIS_KPI_DATABASE_URL='postgresql+psycopg://user:password@host:5432/gis_kpi'
python scripts/migrate.py upgrade head
python scripts/migrate.py current
```

Configure the single internal Python index and read credentials as documented in [REGISTRY.md](REGISTRY.md). Database credentials stay in the deployment environment. The application database is separate from Airflow's metadata database.

Revision `0001` is unchanged. Existing databases retain their revision state and data; no tables need recreation. Create new revisions in the persistence library source repository, release that library, then update this deployment's requirements pin. The root Alembic configuration references installed library resources and is for deployment commands only.

Documentation retains the guides/reference/changelog structure. This repository's CI validates dependency installation, migration resources and documentation; it does not publish a Python package. No migration is executed against production by CI.


## Unified Python registry

Use ordinary pip package versions through the configured single internal index. This deployment repository is not built or uploaded as a package. See [REGISTRY.md](REGISTRY.md) for endpoint configuration, read credentials and container netrc secrets.
