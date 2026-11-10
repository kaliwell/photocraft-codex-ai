import unittest,tempfile,json
from pathlib import Path
from unittest.mock import Mock
import cv2,numpy as np
from PIL import Image
from photocraft_ai.edit_alignment import estimate,render,AlignmentError
from photocraft_ai.service import Service


class AlignmentTests(unittest.TestCase):
    def fixture(self):
        rng=np.random.default_rng(42)
        pixels=cv2.GaussianBlur(rng.integers(0,256,(512,512,3),dtype=np.uint8),(11,11),0)
        cv2.rectangle(pixels,(40,50),(460,460),(220,240,180),4)
        cv2.circle(pixels,(70,150),30,(20,50,250),6)
        return Image.fromarray(pixels),Image.fromarray(np.pad(np.full((212,212),255,dtype=np.uint8),((150,150),(150,150))))

    def test_translated_scene_is_registered_using_unchanged_context(self):
        original,mask=self.fixture()
        pixels=cv2.warpAffine(np.array(original),np.float32([[1,0,6],[0,1,-4]]),(512,512),borderMode=cv2.BORDER_REFLECT)
        pixels[175:325,175:325]=(255,0,0)
        matrix,report=estimate(original,Image.fromarray(pixels),mask)
        self.assertAlmostEqual(float(matrix[0,2]),6,delta=.5)
        self.assertAlmostEqual(float(matrix[1,2]),-4,delta=.5)
        self.assertLess(report['after_error'],report['before_error'])
        mapping={'source_size':[512,512],'content_box':[0,0,512,512]}
        result=render(Image.fromarray(pixels),mapping,(512,512),matrix)
        self.assertEqual(result.getpixel((240,240)),(255,0,0,255))

    def test_excessive_scaling_is_rejected(self):
        original,mask=self.fixture()
        pixels=cv2.warpAffine(np.array(original),np.float32([[1.2,0,0],[0,1.2,0]]),(512,512))
        with self.assertRaises(AlignmentError):estimate(original,Image.fromarray(pixels),mask)

    def test_flat_context_color_change_is_rejected(self):
        mask=Image.new('L',(128,128));mask.paste(255,(40,40,80,80))
        with self.assertRaises(AlignmentError):estimate(Image.new('RGB',mask.size,'white'),Image.new('RGB',mask.size,'black'),mask)

    def test_unchanged_context_does_not_introduce_transform(self):
        original,mask=self.fixture();matrix,report=estimate(original,original,mask)
        self.assertEqual(report['status'],'context_matches')
        self.assertTrue(np.array_equal(matrix,np.eye(2,3,dtype=np.float32)))

    def test_rejected_result_never_imports_a_layer(self):
        from photocraft_ai.edit_region import prepare_region
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);original=Image.new('RGBA',(256,256),'white');mask=Image.new('L',original.size);mask.paste(255,(80,80,160,160))
            bridge=Mock();target=bridge.active_image.return_value;target.index=0;target.name='test';target._inspect.return_value={'hasSelection':True}
            bridge._snapshot.return_value=(original,mask);bridge._revision.return_value=2
            service=Service(bridge,root);p=service.prepare('fill','edit')
            bridge.documents.return_value=[{'index':0,'name':'test','revision':2}]
            result=root/'generated.png';Image.new('RGB',Image.open(p.source).size,'black').save(result)
            with self.assertRaises(AlignmentError):service.apply(p,result)
            bridge.insert_results.assert_not_called()
            self.assertTrue(result.exists())
            self.assertEqual(json.loads((p.job/'edit-alignment.json').read_text(encoding='utf8'))['status'],'rejected')
