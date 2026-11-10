# Python package registry

Packages and Airflow providers are published as immutable versioned wheels/sdists. Consumers declare normal package versions in pyproject.toml or requirements.txt; they do not clone source repositories. Deployment repositories remain DAG/configuration bundles and are not uploaded to PyPI.

## Registry endpoints and credentials

Configure the following repository/organization **variables** on Gitea (and on the GitHub validation mirror):

| Variable | Value |
| --- | --- |
| `PIP_INDEX_URL` | Credential-free **single aggregate index** serving private packages and public PyPI, e.g. `https://packages.example.com/simple/` |
| `PYPI_UPLOAD_URL` | Gitea upload endpoint: `https://git.example.com/api/packages/OWNER/pypi` |
| `PYPI_READ_USERNAME` | Account used for registry reads |
| `PYPI_PUBLISH_USERNAME` | Account used for Gitea package uploads |

Configure **secrets** `PYPI_READ_TOKEN` (read-package permission), `PYPI_PUBLISH_TOKEN` (write-package permission), and the existing `RELEASE_TOKEN` (source commit/tag/release permission). Keep these purposes separate. Do not put tokens in URLs, requirements, source files or image build arguments. Do not send secret values in chat.

The Gitea read index is `https://git.example.com/api/packages/OWNER/pypi/simple/`. Gitea hosts private packages but does **not** automatically proxy public PyPI. For one endpoint, expose it together with public PyPI through your devpi/Nexus/Artifactory aggregate, with routing that reserves the internal project names for the private source. Point `PIP_INDEX_URL` at that aggregate. If using Gitea directly, its index must also contain/mirror all required public dependencies; otherwise use an aggregate. No public `--extra-index-url` fallback is configured.

Registry ownership is independent of the source repository. Packages are uploaded to the selected Gitea owner/organization and may be linked to their source repositories in Gitea. This repository does not create a registry server, change access permissions or store tokens.

## Normal installation

Provision a secret-managed `~/.netrc` (mode 0600) for the **index host**, or use an equivalent keyring/credential mechanism:

```text
machine packages.example.com
login reader-account
password READ_TOKEN_FROM_SECRET_STORE
```

Set the credential-free `PIP_INDEX_URL` once in the environment or pip configuration. Then use ordinary pip commands:

```sh
pip install -r requirements.txt
# Inside an installable package source checkout:
pip install -e '.[dev]'
```

Do not install a deployment repository itself. In Airflow environments retain the environment's pinned Airflow version and constraints when installing requirements. Install matching requirements in the DAG processor, scheduler and all workers.

CI uses `scripts/registry.py install ...` or `scripts/registry.py run COMMAND ...`. The helper creates an ephemeral 0600 netrc, disables additional indexes/config-file fallback, and retains proxy and CA environment settings. It requires the read credentials above. Public/untrusted fork workflows do not receive repository secrets and need a trusted maintainer validation path.

## Publishing and Git flow

Flow: feature -> integration -> release -> production. Integration and PRs validate tests, distributions and docs. Only the **Gitea production** workflow can publish packages. The GitHub mirror validates and never uploads a package.

The production job waits for validation, checks publishing configuration, uses Conventional Commits to calculate the semantic version, updates package metadata, builds the wheel/sdist, and validates artifact names, versions and version-only dependencies. Semantic-release creates the release commit/tag; its publish hook uploads the distributions with Twine using the write token. Documentation remains attached to the Gitea release where configured.

Versions are immutable: publishing an existing version fails rather than overwriting or silently skipping it. If upload fails after tagging, repair the credentials/registry and republish the **same reviewed artifacts**; do not rebuild different content under that version. Use a new semantic version for changed code.

Initial bootstrap uses semantic-release's first release, `1.0.0`, when no earlier semantic tags exist. Deployments pin those first versions; library metadata permits the compatible 1.x line (and the existing 0.x development baseline where specified). If a package already has release tags, use the actual next version and update deployment pins before promotion.

Publish in dependency order:

1. datetime-interval-calculator, http-auth, http-paginators, data-process, and independent providers/libraries.
2. Shared database library, then issue-metric-calculator.
3. HTTP provider, after its three standalone strategy dependencies exist.
4. Deploy Airflow jobs after every pinned package is available.

Read credentials alone cannot make a missing first package release installable. Bootstrap leaf packages before validating/releasing their consumers. No Git-based fallback is used.

## Containers

Pass the index URL as configuration and provide a secret-mounted netrc during builds. Example:

```sh
docker build --build-arg PIP_INDEX_URL="$PIP_INDEX_URL" \
  --secret id=pip_netrc,src="$PYPI_NETRC_FILE" -t gis-kpi-jobs .
```

The netrc is not copied into an image layer. Runtime credentials are needed only if packages are installed at runtime; prefer prebuilt deployment images.
