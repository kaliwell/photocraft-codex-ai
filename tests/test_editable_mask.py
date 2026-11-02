from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch, create_autospec

from PIL import Image
from photocraft_ai.bridge import PhotoCraftBridge
from photocraft_ai.service import Prepared, Service


class EditableMaskTests(unittest.TestCase):
    def test_generated_pixels_keep_original_alpha_and_feather_is_native(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = root / 'generated.png'
            Image.new('RGBA', (8, 8), 'red').save(result)
            bridge = create_autospec(PhotoCraftBridge, instance=True)
            target = Mock(index=0)
            target.name = 'test'
            bridge.documents.return_value = [{'index': 0, 'name': 'test', 'revision': 2}]
            mask = Image.new('L', (8, 8), 0)
            mask.putpixel((3, 3), 128)
            prepared = Prepared(root, 'fill', 'test', target, 2, mask.size, mask, None, None, 24)
            Service(bridge, root).apply(prepared, result)
            with Image.open(root / 'layer.png') as layer:
                self.assertEqual(layer.getpixel((3, 3))[3], 128)
                self.assertEqual(layer.getpixel((0, 0))[3], 0)
            options = bridge.insert_results.call_args.kwargs
            self.assertTrue(options['use_selection_mask'])
            self.assertEqual(options['feather'], 24)
            self.assertEqual(options['mask_pixels'][3 * 8 + 3], 255)

    def test_bridge_attaches_feather_in_scratch_document_before_commit(self):
        bridge = object.__new__(PhotoCraftBridge)
        bridge.client = Mock()
        with patch('openfill_photocraft.bridge.PhotoCraftBridge._add_mask') as original:
            bridge._add_mask(1, 9, 'pixels', 0, 24, 3, 4)
        original.assert_called_once_with(1, 9, 'pixels', 0, 0, 3, 4)
        bridge.client.run.assert_called_once_with('layer.layerMask.edit', layer=9, feather=24, inward=True)
