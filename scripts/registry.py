"""Install and publish versioned packages using one authenticated Python index.

URLs contain no credentials. Read credentials live in an ephemeral 0600 netrc;
write credentials are passed to Twine through its standard environment variables.
"""
from contextlib import contextmanager
from email.parser import BytesParser
import json
import netrc
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import tomllib
from urllib.parse import urlsplit
import zipfile



def endpoint(value, label):
    parsed = urlsplit(value or '')
    if not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(f'{label} must be a credential-free registry URL')
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1','localhost','::1')):
        raise ValueError(f'{label} must use HTTPS (HTTP is permitted only on loopback)')
    return parsed


def setting(env, key):
    value = env.get(key, '')
    if not value:
        raise ValueError(f'Missing {key}; see REGISTRY.md')
    return value


@contextmanager
def installation_environment(environment=None):
    env = dict(os.environ if environment is None else environment)
    url = setting(env, 'PIP_INDEX_URL')
    host = endpoint(url, 'PIP_INDEX_URL').hostname
    username = setting(env, 'PYPI_READ_USERNAME')
    token = setting(env, 'PYPI_READ_TOKEN')
    if any(c.isspace() for c in username + token):
        raise ValueError('Registry credentials must not contain whitespace')
    with tempfile.TemporaryDirectory(prefix='pip-registry-') as directory:
        path = Path(directory) / 'netrc'
        path.write_text(f'machine {host}\nlogin {username}\npassword {token}\n')
        path.chmod(0o600)
        env['NETRC'] = str(path)
        env['PIP_CONFIG_FILE'] = os.devnull
        env['PIP_INDEX_URL'] = url
        # A single aggregate index controls private/public project routing.
        for key in ('PIP_EXTRA_INDEX_URL','PIP_FIND_LINKS','PIP_NO_INDEX'):
            env.pop(key, None)
        yield env


def project(root):
    return tomllib.loads((root / 'pyproject.toml').read_text())['project']


def package_artifacts(root):
    return sorted((root/'dist').glob('*.whl')) + sorted((root/'dist').glob('*.tar.gz'))


def validate_artifacts(root, artifact_directory=None):
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name, parse_sdist_filename, parse_wheel_filename
    from packaging.version import Version
    metadata = project(root)
    expected_name, expected_version = canonicalize_name(metadata['name']), Version(metadata['version'])
    for group in [metadata.get('dependencies', []), *metadata.get('optional-dependencies', {}).values()]:
        for value in group:
            if Requirement(value).url:
                raise ValueError('Publish dependencies must use package versions, not direct URLs')
    artifacts = package_artifacts(root if artifact_directory is None else artifact_directory)
    if len(artifacts) != 2 or not any(p.suffix == '.whl' for p in artifacts):
        raise ValueError('Build exactly one wheel and one sdist into a clean dist directory')
    for path in artifacts:
        if path.suffix == '.whl':
            name, version, _, _ = parse_wheel_filename(path.name)
            with zipfile.ZipFile(path) as archive:
                candidates = [n for n in archive.namelist() if n.endswith('.dist-info/METADATA')]
                if len(candidates) != 1:
                    raise ValueError('Wheel must contain exactly one METADATA file')
                raw = archive.read(candidates[0])
        else:
            name, version = parse_sdist_filename(path.name)
            with tarfile.open(path) as archive:
                candidates = [m for m in archive.getmembers() if len(Path(m.name).parts) == 2 and m.name.endswith('/PKG-INFO')]
                if len(candidates) != 1:
                    raise ValueError('Sdist must contain exactly one top-level PKG-INFO file')
                raw = archive.extractfile(candidates[0]).read()
        if canonicalize_name(name) != expected_name or version != expected_version:
            raise ValueError('Artifact name/version does not match pyproject.toml; clean dist and rebuild')
        headers = BytesParser().parsebytes(raw)
        for dependency in headers.get_all('Requires-Dist', []):
            if Requirement(dependency).url:
                raise ValueError('Artifact still declares a direct-URL dependency')
    return artifacts


def publishing_environment(environment=None):
    env = dict(os.environ if environment is None else environment)
    url = setting(env, 'PYPI_UPLOAD_URL')
    endpoint(url, 'PYPI_UPLOAD_URL')
    env['TWINE_REPOSITORY_URL'] = url
    env['TWINE_USERNAME'] = setting(env, 'PYPI_PUBLISH_USERNAME')
    env['TWINE_PASSWORD'] = setting(env, 'PYPI_PUBLISH_TOKEN')
    env['TWINE_NON_INTERACTIVE'] = '1'
    return env


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        raise SystemExit('Usage: registry.py install [pip arguments] | verify-publish | validate | publish')
    repository = Path(__file__).resolve().parents[1]
    root = repository / os.environ.get('PYTHON_PROJECT_DIR', '.')
    try:
        if args[0] == 'install':
            with installation_environment() as env:
                subprocess.run([sys.executable,'-m','pip','install',*args[1:]],env=env,check=True)
        elif args[0] == 'run':
            with installation_environment() as env:
                subprocess.run(args[1:], env=env, check=True)
        elif args[0] == 'verify-publish':
            publishing_environment()
        elif args[0] == 'validate':
            validate_artifacts(root, repository)
            print('Distribution metadata and version-only dependencies verified')
        elif args[0] == 'publish':
            artifacts = validate_artifacts(root, repository)
            env = publishing_environment()
            subprocess.run([sys.executable,'-m','twine','check','--strict',*[str(p) for p in artifacts]],check=True,stdout=sys.stderr)
            # Never overwrite or silently skip an existing release version.
            subprocess.run([sys.executable,'-m','twine','upload',*[str(p) for p in artifacts]],env=env,check=True,stdout=sys.stderr)
        else:
            raise ValueError('Unknown registry command')
    except ValueError as error:
        raise SystemExit(str(error)) from None


if __name__ == '__main__':
    main()
