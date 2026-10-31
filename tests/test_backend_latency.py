import json
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from photocraft_ai.backend import CodexBackend, Cancelled, valid_result


class LatencyTests(unittest.TestCase):
    def test_complete_image_returns_without_waiting_for_agent_summary(self):
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder)
            script = job / 'fake_cli.py'
            script.write_text(
                'import sys,time,json\nfrom PIL import Image\n'
                'sys.stdin.read()\n'
                'print(json.dumps({"type":"thread.started"}),flush=True)\n'
                'Image.new("RGB",(8,8),"red").save("generated.png")\n'
                'time.sleep(30)\n', encoding='utf-8')
            started = time.monotonic()
            with patch('photocraft_ai.backend.codex_command', return_value=[sys.executable, str(script)]):
                result = CodexBackend().generate(job, 'test', 'create', threading.Event(), lambda _: None)
            self.assertTrue(valid_result(result))
            self.assertLess(time.monotonic() - started, 10)
            timing = json.loads((job / 'timing.json').read_text())
            self.assertTrue(timing['returned_before_cli_exit'])

    def test_cancellation_never_returns_a_result(self):
        with tempfile.TemporaryDirectory() as folder:
            job = Path(folder)
            script = job / 'fake_cli.py'
            script.write_text('import sys,time\nsys.stdin.read()\ntime.sleep(30)\n', encoding='utf-8')
            cancel = threading.Event()
            cancel.set()
            with patch('photocraft_ai.backend.codex_command', return_value=[sys.executable, str(script)]):
                with self.assertRaises(Cancelled):
                    CodexBackend().generate(job, 'test', 'create', cancel, lambda _: None)

    def test_incomplete_png_is_not_treated_as_finished(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'partial.png'
            path.write_bytes(b'\x89PNG\r\n\x1a\n')
            self.assertFalse(valid_result(path))


if __name__ == '__main__':
    unittest.main()
