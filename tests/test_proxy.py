import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from photocraft_ai.backend import codex_environment


class ProxyTests(unittest.TestCase):
    def test_explicit_proxy_reaches_child_without_changing_parent(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / 'proxy.json'
            config.write_text(json.dumps({'url': 'http://127.0.0.1:10808'}))
            original = {'HTTPS_PROXY': 'http://old:8080', 'NO_PROXY': 'internal', 'CODEX_THREAD_ID': 'old'}
            with patch.dict(os.environ, original, clear=True):
                env, enabled = codex_environment(config)
                self.assertTrue(enabled)
                self.assertEqual(env['HTTPS_PROXY'], 'http://127.0.0.1:10808')
                self.assertEqual(env['https_proxy'], env['HTTPS_PROXY'])
                self.assertIn('127.0.0.1', env['NO_PROXY'])
                self.assertIn('internal', env['NO_PROXY'])
                self.assertNotIn('CODEX_THREAD_ID', env)
                self.assertEqual(dict(os.environ), original)

    def test_missing_config_preserves_inherited_proxy(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(os.environ, {'HTTPS_PROXY': 'http://inherited:8080'}, clear=True):
                env, enabled = codex_environment(Path(folder) / 'missing.json')
                self.assertFalse(enabled)
                self.assertEqual(env['HTTPS_PROXY'], 'http://inherited:8080')

    def test_invalid_config_is_reported(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / 'proxy.json'
            config.write_text('{"url":"not a proxy"}')
            with self.assertRaisesRegex(RuntimeError, '代理配置无效'):
                codex_environment(config)
