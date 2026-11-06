import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock
from PIL import Image
from photocraft_ai.service import Prepared, Service, generated_layer


class SquareGenerationTests(unittest.TestCase):
    def test_square_request_ignores_widescreen_canvas(self):
        backend = Mock()
        p = Prepared(Path('.'), 'generate', 'cat', None, 1, (1920,1080), None, None, None, 0)
        Service(None, Path('.'), backend).generate(p, threading.Event(), lambda _: None)
        self.assertEqual(backend.generate.call_args.args[-1], '1024x1024')

    def test_non_square_result_is_contained_without_distortion(self):
        mask = Image.new('L', (192,108))
        mask.paste(255,(20,10,100,90))
        layer = generated_layer(Image.new('RGBA',(1717,916),(255,0,0,128)),mask)
        self.assertEqual(layer.size, mask.size)
        bounds = layer.getbbox()
        self.assertEqual(bounds, (20,28,100,71))
        self.assertEqual(layer.getpixel((40,40)),(255,0,0,128))
        self.assertEqual(layer.getpixel((0,0))[3],0)

    def test_generate_applies_with_revision_check(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);path=root/'result.png';Image.new('RGBA',(16,16),'red').save(path)
            target=Mock(index=0);target.name='doc'
            bridge=Mock();bridge.documents.return_value=[{'index':0,'name':'doc','revision':3}]
            p=Prepared(root,'generate','cat',target,3,(40,20),Image.new('L',(40,20),255),None,None,0)
            Service(bridge,root).apply(p,path)
            bridge.insert_results.assert_called_once()
            bridge.commit_above.assert_called_once_with(target,None)
