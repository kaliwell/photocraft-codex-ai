import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from PIL import Image
from photocraft_ai.backend import CodexBackend, receive_generated_image

THREAD = '01a19761-30db-70d0-a4a7-33ce000ae6a6'


class ReceiveImageTests(unittest.TestCase):
    def test_receives_only_current_thread_complete_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            job = root / 'job'; job.mkdir()
            images = root / 'generated_images' / THREAD; images.mkdir(parents=True)
            (images / 'partial.png').write_bytes(b'not a complete PNG')
            self.assertFalse(receive_generated_image(job, THREAD, root))
            Image.new('RGB', (8, 8), 'red').save(images / 'partial.png')
            self.assertFalse(receive_generated_image(job, '../' + THREAD, root))
            self.assertTrue(receive_generated_image(job, THREAD, root))
            self.assertEqual((job / 'generated.png').read_bytes(), (images / 'partial.png').read_bytes())
            Image.new('RGB', (8, 8), 'blue').save(images / 'second.png')
            self.assertFalse(receive_generated_image(job, THREAD, root))

    def test_shell_copy_failure_does_not_lose_finished_image(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            job = root / 'job'; job.mkdir()
            images = root / 'generated_images' / THREAD; images.mkdir(parents=True)
            script = job / 'fake_cli.py'
            script.write_text('import sys,json\nfrom PIL import Image\nsys.stdin.read()\n'
                              f'print(json.dumps({{"type":"thread.started","thread_id":{THREAD!r}}}),flush=True)\n'
                              f'Image.new("RGB",(8,8),"red").save({str(images / "output.png")!r})\n'
                              'print("CreateProcessAsUserW failed: 5",flush=True)\nsys.exit(1)\n')
            with patch('photocraft_ai.backend.codex_command', return_value=[sys.executable, str(script)]), \
                    patch('photocraft_ai.backend.codex_environment', return_value=({**os.environ, 'CODEX_HOME': str(root)}, False)):
                result = CodexBackend().generate(job, 'a rabbit', 'create', threading.Event(), lambda _: None)
            self.assertTrue(result.is_file())
            self.assertTrue(json.loads((job / 'timing.json').read_text())['received_directly'])
