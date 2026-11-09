"""Credential isolation and immutable release validation, without external services."""
import importlib.util
from pathlib import Path
import netrc
import os
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('registry',Path(__file__).with_name('registry.py'))
registry=importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)


class RegistryTests(unittest.TestCase):
    def test_read_credentials_are_scoped_and_temporary(self):
        source={'PIP_INDEX_URL':'https://packages.example.test/simple','PYPI_READ_USERNAME':'reader','PYPI_READ_TOKEN':'test-token',
                'PIP_EXTRA_INDEX_URL':'https://unwanted.example/simple','HTTPS_PROXY':'http://proxy.example:8080','PIP_CERT':'/trust/ca.pem'}
        with registry.installation_environment(source) as env:
            path=Path(env['NETRC'])
            self.assertEqual(path.stat().st_mode & 0o777,0o600)
            self.assertEqual(netrc.netrc(path).authenticators('packages.example.test'),('reader','','test-token'))
            self.assertNotIn('PIP_EXTRA_INDEX_URL',env)
            self.assertNotIn('test-token',env['PIP_INDEX_URL'])
            self.assertEqual(env['HTTPS_PROXY'],source['HTTPS_PROXY'])
            self.assertEqual(env['PIP_CERT'],source['PIP_CERT'])
        self.assertFalse(path.exists())

    def test_credentials_in_urls_and_remote_http_are_rejected(self):
        for url in ['https://user:password@example.test/simple','http://example.test/simple','https://example.test/simple?token=test']:
            with self.assertRaises(ValueError):registry.endpoint(url,'index')

    def test_missing_read_token_fails_before_installation(self):
        with self.assertRaises(ValueError):
            with registry.installation_environment({'PIP_INDEX_URL':'https://example.test/simple','PYPI_READ_USERNAME':'reader'}):pass

    def test_publish_uses_a_separate_write_token(self):
        env=registry.publishing_environment({'PYPI_UPLOAD_URL':'https://git.example.test/api/packages/team/pypi',
            'PYPI_PUBLISH_USERNAME':'publisher','PYPI_PUBLISH_TOKEN':'write-test','PYPI_READ_TOKEN':'read-test'})
        self.assertEqual(env['TWINE_PASSWORD'],'write-test')
        self.assertEqual(env['TWINE_NON_INTERACTIVE'],'1')


if __name__=='__main__':unittest.main()
