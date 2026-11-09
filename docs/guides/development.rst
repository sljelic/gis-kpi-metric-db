Development and validation
==========================

The layout follows the provider documentation structure: src for runtime code,
tests/unit and tests/integration, and docs/guides, docs/references,
docs/changelog with one Sphinx configuration.

Run::

    pytest
    python -m build
    python -m twine check dist/*
    make html
    make pdf

Set TEST_POSTGRES_URL to an empty disposable PostgreSQL database to run the
migration lifecycle test. It upgrades from base, verifies metadata parity,
retains existing rows across a repeated 0001 upgrade, tests downgrade and
re-upgrade, and cleans up its tables. SQLite tests exercise service behavior.
The migration-resource test also generates a new revision in a temporary copy.

PDF uses SimplePDF/WeasyPrint and needs Pango plus fonts on the host (Debian:
libpango-1.0-0, libpangoft2-1.0-0, fonts-dejavu-core). Outputs are not tracked.
