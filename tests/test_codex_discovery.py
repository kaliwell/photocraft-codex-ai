import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from photocraft_ai.backend import codex_command


class CodexDiscoveryTests(unittest.TestCase):
    def test_local_node_and_custom_npm_prefix_are_used(self):
        with tempfile.TemporaryDirectory() as folder:
            prefix = Path(folder)
            script = prefix / 'node_modules/@openai/codex/bin/codex.js'
            script.parent.mkdir(parents=True)
            script.write_text('test')
            mapping = {'node': str(prefix / 'node.exe'), 'codex.cmd': str(prefix / 'codex.cmd')}
            with patch.dict(os.environ, {'APPDATA': str(prefix / 'unused')}), \
                    patch('photocraft_ai.backend.shutil.which', side_effect=mapping.get):
                self.assertEqual(codex_command(), [mapping['node'], str(script)])

    def test_missing_codex_provides_install_command(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.dict(os.environ, {'APPDATA': folder}), \
                    patch('photocraft_ai.backend.shutil.which', return_value=None):
                with self.assertRaisesRegex(RuntimeError, 'npm.cmd install'):
                    codex_command()
