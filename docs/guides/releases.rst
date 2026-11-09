Git flow and releases
=====================

Use feature branches -> integration -> release branches -> production.
GitHub and Gitea validate tests, PostgreSQL migration lifecycle, wheel resources
and full HTML/PDF documentation. Only Gitea production releases after all checks.
Conventional Commit fix/feat/breaking messages select patch/minor/major versions.

The release pipeline synchronizes pyproject.toml and VERSION, updates
CHANGELOG.md, builds distributions and versioned HTML/PDF assets, commits release
metadata and creates vX.Y.Z on Gitea. Configure RELEASE_TOKEN with commit/tag/
release write permissions and allow the release bot on production. GitHub is a
validation mirror. Maintainers configure branch protection and promotion branches.

This is a database library, not an Airflow provider: there is no provider.yaml
or apache_airflow_provider entry point. No Airflow provider metadata is generated.
