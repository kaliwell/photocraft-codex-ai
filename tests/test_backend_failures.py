from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw
from photocraft_ai.backend import CodexBackend, GenerationFailure, failure_from_log, is_blank_selection


class FailureTests(unittest.TestCase):
    def test_moderation_failure_has_priority_over_earlier_timeouts(self):
        error = failure_from_log('Reconnecting: request timed out\ncode: moderation_blocked')
        self.assertEqual(error.code, 'moderation_blocked')
        self.assertIn('安全系统', str(error))

    def test_network_timeout_is_explained(self):
        self.assertEqual(failure_from_log('request timed out').code, 'network')

    def test_distinguishes_quota_authentication_and_unknown_errors(self):
        self.assertEqual(failure_from_log('insufficient_quota').code, 'quota')
        self.assertEqual(failure_from_log('401 Unauthorized').code, 'authentication')
        self.assertEqual(str(failure_from_log('', 'Image tool unavailable')), 'Image tool unavailable')

    def test_moderation_stops_without_waiting_for_agent_wrap_up(self):
        with tempfile.TemporaryDirectory() as directory:
            job = Path(directory)
            script = job / 'fake_cli.py'
            script.write_text('import sys,time\nsys.stdin.read()\nprint("moderation_blocked",flush=True)\ntime.sleep(30)\n')
            started = time.monotonic()
            with patch('photocraft_ai.backend.codex_command', return_value=[sys.executable, str(script)]):
                with self.assertRaises(GenerationFailure) as error:
                    CodexBackend().generate(job, 'test', 'create', threading.Event(), lambda _: None)
            self.assertEqual(error.exception.code, 'moderation_blocked')
            self.assertLess(time.monotonic() - started, 10)
            self.assertFalse((job / 'generated.png').exists())

    def test_blank_canvas_uses_text_only_but_keeps_real_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, selected = root / 'source.png', root / 'selection.png'
            image = Image.new('RGBA', (100, 100), 'white')
            image.save(source)
            mask = Image.new('L', image.size, 0)
            ImageDraw.Draw(mask).rectangle((20, 20, 80, 80), fill=255)
            mask.save(selected)
            self.assertTrue(is_blank_selection(source, selected))
            image.putpixel((0, 0), (0, 0, 0, 255))
            image.save(source)
            self.assertFalse(is_blank_selection(source, selected))


if __name__ == '__main__':
    unittest.main()
