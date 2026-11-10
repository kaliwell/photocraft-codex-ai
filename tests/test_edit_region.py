import tempfile,json,unittest
from pathlib import Path
from PIL import Image,ImageChops
from photocraft_ai.edit_region import prepare_region,map_result
from photocraft_ai.service import edited_layer


class EditRegionTests(unittest.TestCase):
    def test_actual_portrait_selection_keeps_native_pixels(self):
        full=Image.new('RGBA',(790,1688),'red');mask=Image.new('L',full.size);mask.paste(255,(0,598,790,1390))
        reference,selection,mapping=prepare_region(full,mask)
        self.assertEqual(reference.size,(1120,1120))
        self.assertEqual(mapping['crop_box'],[0,440,790,1548])
        self.assertEqual(mapping['content_box'],[165,6,955,1114])
        self.assertEqual(selection.getbbox(),(165,164,955,956))

    def test_small_selection_does_not_send_full_large_canvas(self):
        full=Image.new('RGBA',(4000,3000),'red');mask=Image.new('L',full.size);mask.paste(255,(1900,1400,2100,1600))
        _,_,m=prepare_region(full,mask)
        self.assertEqual(m['crop_box'],[1836,1336,2164,1664])
        self.assertEqual(m['source_size'],[336,336])

    def test_edge_irregular_selection_maps_back_without_outside_changes(self):
        full=Image.new('RGBA',(120,180),'red');mask=Image.new('L',full.size)
        mask.paste(128,(0,0,20,40));mask.putpixel((3,4),0)
        source,_,mapping=prepare_region(full,mask)
        with tempfile.TemporaryDirectory() as folder:
            job=Path(folder);(job/'edit-transform.json').write_text(json.dumps(mapping))
            layer=edited_layer(source.resize((1254,1254)),mask,job)
            self.assertEqual(layer.getpixel((5,5)),(255,0,0,128))
            self.assertEqual(layer.getpixel((3,4))[3],0)
            self.assertEqual(layer.getpixel((100,100))[3],0)

    def test_legacy_higher_resolution_return_is_not_downsampled_first(self):
        image=Image.effect_noise((1536,1536),100).convert('RGBA')
        mapping={'content_box':[0,0,1024,1024]}
        result=map_result(image,Image.new('L',image.size,255),mapping)
        self.assertEqual(result.tobytes(),image.tobytes())

    def test_large_input_is_bounded_and_invalid_map_is_rejected(self):
        full=Image.new('RGBA',(2000,3000),'red');mask=Image.new('L',full.size,255)
        reference,_,mapping=prepare_region(full,mask)
        self.assertEqual(reference.size,(1536,1536))
        mapping['crop_box']=[0,0,10,10]
        with self.assertRaises(ValueError):map_result(reference,mask,mapping)
