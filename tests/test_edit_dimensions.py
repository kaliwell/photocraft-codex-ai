import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
from PIL import Image
from photocraft_ai.service import Service,edit_reference,edited_layer


class EditDimensionsTests(unittest.TestCase):
    def test_square_letterbox_preserves_canvas_aspect_and_mask_coordinates(self):
        full=Image.new('RGBA',(1920,1080),'red')
        mask=Image.new('L',full.size,255)
        square,selection,box=edit_reference(full,mask)
        self.assertEqual(square.size,(1024,1024))
        self.assertEqual(box,(0,224,1024,800))
        self.assertEqual(selection.getbbox(),box)
        self.assertEqual(square.getpixel((500,100))[3],0)

    def test_mismatched_result_maps_back_and_clips_to_original_selection(self):
        with tempfile.TemporaryDirectory() as d:
            job=Path(d);mask=Image.new('L',(192,108));mask.paste(128,(30,20,80,70))
            (job/'edit-transform.json').write_text(json.dumps({'content_box':[0,224,1024,800]}))
            result=edited_layer(Image.new('RGBA',(1717,916),'green'),mask,job)
            self.assertEqual(result.size,mask.size)
            self.assertEqual(result.getpixel((50,50)),(0,128,0,128))
            self.assertEqual(result.getpixel((0,0))[3],0)

    def test_legacy_retained_result_is_adapted_and_prepare_keeps_original_mask(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);mask=Image.new('L',(192,108),255)
            self.assertEqual(edited_layer(Image.new('RGBA',(1717,916),'red'),mask,root).size,mask.size)
            bridge=Mock();bridge.active_image.return_value._inspect.return_value={'hasSelection':True}
            bridge.active_image.return_value.name='doc'
            bridge._snapshot.return_value=(Image.new('RGBA',mask.size,'red'),mask)
            bridge._revision.return_value=3
            p=Service(bridge,root).prepare('fill','necklace')
            self.assertEqual(p.mask.size,(192,108))
            self.assertEqual(Image.open(p.source).size,(1024,1024))
            self.assertEqual(Image.open(p.job/'selection.png').size,(192,108))
            self.assertEqual(Image.open(p.job/'selection-guide.png').size,(1024,1024))
