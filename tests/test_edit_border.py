import unittest,tempfile
from pathlib import Path
from unittest.mock import Mock
from PIL import Image,ImageChops
from photocraft_ai.edit_border import refine_border_mask,alignment_mask


class BorderTests(unittest.TestCase):
    def fixture(self):
        photo=Image.new('RGBA',(400,500),'white')
        photo.paste((120,190,230,255),(60,0,340,500))
        mask=Image.new('L',photo.size);mask.paste(255,(0,150,400,500));mask.putpixel((2,200),0)
        return photo,mask

    def test_explicit_border_request_preserves_center_and_selection_exterior(self):
        photo,mask=self.fixture();result,info=refine_border_mask(photo,mask,'移除左右两侧的白色边框，补全内容')
        self.assertEqual((info['left'],info['right']),(60,60))
        self.assertEqual(result.getpixel((20,200)),255)
        self.assertEqual(result.getpixel((380,200)),255)
        self.assertEqual(result.getpixel((200,200)),0)
        self.assertEqual(result.getpixel((20,100)),0)
        self.assertEqual(result.getpixel((2,200)),0)
        self.assertIsNone(ImageChops.subtract(result,mask).getbbox())

    def test_other_edits_keep_exact_user_selection(self):
        photo,mask=self.fixture()
        for prompt in ['移除充电宝','把左右的产品改成白色','remove the white product','fill the sky']:
            result,info=refine_border_mask(photo,mask,prompt)
            self.assertIs(result,mask);self.assertIsNone(info)

    def test_uncertain_or_one_sided_margins_are_not_inferred(self):
        photo,mask=self.fixture()
        for image in [Image.new('RGBA',photo.size,'white'),Image.new('RGBA',photo.size,(255,255,255,0))]:
            result,info=refine_border_mask(image,mask,'fill white side borders')
            self.assertIs(result,mask);self.assertIsNone(info)
        photo.paste('blue',(0,0,5,500))
        self.assertIsNone(refine_border_mask(photo,mask,'fill white side borders')[1])

    def test_feather_coverage_and_holes_are_retained(self):
        photo,mask=self.fixture();mask.putpixel((5,200),100)
        result,info=refine_border_mask(photo,mask,'fill white side borders')
        self.assertIsNotNone(info)
        self.assertEqual(result.getpixel((5,200)),100)
        self.assertEqual(result.getpixel((200,200)),0)

    def test_registration_excludes_blank_margins_without_expanding_edit_mask(self):
        photo,mask=self.fixture();edit,border=refine_border_mask(photo,mask,'fill white side borders')
        registration=alignment_mask(edit,border)
        self.assertEqual(registration.getpixel((20,100)),255)
        self.assertEqual(edit.getpixel((20,100)),0)
        self.assertEqual(edit.getpixel((2,200)),0)
        self.assertEqual(registration.getpixel((200,200)),0)

    def test_invalid_alignment_metadata_cannot_exclude_central_photo(self):
        photo,mask=self.fixture()
        with self.assertRaises(ValueError):alignment_mask(mask,{'method':'white-side-borders','left':200,'right':200,'seam':16})

    def test_border_fill_bakes_seam_but_keeps_native_mask_hard(self):
        from photocraft_ai.service import Service
        photo,mask=self.fixture()
        with tempfile.TemporaryDirectory() as folder:
            bridge=Mock();target=bridge.active_image.return_value
            target.index=0;target.name='test';target._inspect.return_value={'hasSelection':True}
            bridge._snapshot.return_value=(photo,mask);bridge._revision.return_value=2
            bridge.documents.return_value=[{'index':0,'name':'test','revision':2}]
            service=Service(bridge,Path(folder));prepared=service.prepare('fill','fill white side borders',feather_px=12)
            service.apply(prepared,prepared.source)
            self.assertTrue((prepared.job/'selection-user.png').exists())
            self.assertEqual(bridge.insert_results.call_args.kwargs['feather'],0)
            with Image.open(prepared.job/'layer.png') as layer:
                alpha=layer.getchannel('A')
                self.assertEqual(alpha.getpixel((200,200)),0)
                self.assertEqual(alpha.getpixel((20,100)),0)
                self.assertEqual(alpha.getpixel((2,200)),0)
                self.assertTrue(any(0<value<255 for value in alpha.getdata()))
