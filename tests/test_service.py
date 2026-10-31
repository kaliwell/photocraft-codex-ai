import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from PIL import Image
from photocraft_ai.service import Service, Prepared, clipped_layer
from photocraft_ai.backend import CodexBackend, Cancelled


class ServiceTests(unittest.TestCase):
    def test_selection_outside_pixels_are_transparent(self):
        mask = Image.new('L', (4, 3), 0)
        mask.putpixel((1, 1), 255)
        mask.putpixel((2, 1), 128)
        layer = clipped_layer(Image.new('RGBA', (4, 3), 'red'), mask)
        self.assertEqual(layer.getpixel((0, 0))[3], 0)
        self.assertEqual(layer.getpixel((1, 1))[3], 255)
        self.assertEqual(layer.getpixel((2, 1))[3], 128)

    def test_rejects_different_output_dimensions(self):
        with self.assertRaisesRegex(RuntimeError, '尺寸'):
            clipped_layer(Image.new('RGB', (5, 3)), Image.new('L', (4, 3)))

    def test_model_resolution_is_mapped_without_distortion(self):
        mask = Image.new('L', (400, 300), 0)
        mask.putpixel((100, 100), 255)
        layer = clipped_layer(Image.new('RGB', (800, 600), 'red'), mask)
        self.assertEqual(layer.size, mask.size)
        self.assertEqual(layer.getpixel((100, 100)), (255, 0, 0, 255))
        self.assertEqual(layer.getpixel((0, 0))[3], 0)

    def test_stale_document_never_receives_layer(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = root / 'generated.png'
            Image.new('RGB', (4, 3)).save(result)
            bridge = Mock()
            bridge.documents.return_value = [{'index': 0, 'name': 'test', 'revision': 9}]
            target = Mock(index=0)
            target.name = 'test'
            prepared = Prepared(root, 'fill', 'red', target, 8, (4, 3), Image.new('L', (4, 3), 255), None, None)
            with self.assertRaisesRegex(RuntimeError, '原文档已改变'):
                Service(bridge, root).apply(prepared, result)
            bridge.insert_results.assert_not_called()

    def test_empty_selection_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            bridge = Mock()
            bridge.active_image.return_value._inspect.return_value = {'hasSelection': False}
            with self.assertRaisesRegex(RuntimeError, '选择'):
                Service(bridge, Path(folder)).prepare('fill', 'test')

    def test_backend_failure_never_applies(self):
        with tempfile.TemporaryDirectory() as folder:
            bridge = Mock()
            backend = Mock()
            backend.generate.side_effect = RuntimeError('image tool unavailable')
            service = Service(bridge, Path(folder), backend)
            prepared = service.prepare('create', 'a cup')
            with self.assertRaisesRegex(RuntimeError, 'unavailable'):
                service.generate(prepared, threading.Event(), lambda _: None)
            bridge.commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
