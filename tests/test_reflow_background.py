import unittest
from PIL import Image
from photocraft_ai.reflow_background import scene_roots,scene_placement,compose_scene,imported_layer


class BackgroundTests(unittest.TestCase):
    def test_foreground_ink_shadow_and_empty_folders_are_not_background_scenes(self):
        info={'width':1500,'height':2000,'layers':[
            {'kind':'Group','children':[]},
            {'kind':'Pixel','bounds':[300,1440,1100,520]},
            {'kind':'Smart Object','bounds':[610,1410,980,76],'hasMask':True},
            {'kind':'Fill'}, {'kind':'Pixel','bounds':[0,0,1500,2000]}]}
        self.assertEqual(scene_roots(info),[(3,),(4,)])

    def test_canvas_edge_repairs_stay_with_full_photo(self):
        info={'width':1500,'height':1500,'layers':[{'kind':'Pixel','bounds':[-131,0,209,1500]},{'kind':'Pixel','bounds':[60,0,1500,1500]},{'kind':'Pixel','bounds':[300,1000,1000,300]}]}
        self.assertEqual(scene_roots(info),[(0,),(1,)])

    def test_native_gradient_resize_never_calls_image_generation(self):
        import tempfile,json,threading
        from pathlib import Path
        from types import SimpleNamespace
        from unittest.mock import Mock
        from photocraft_ai.reflow_background import generate_scene
        with tempfile.TemporaryDirectory() as directory:
            job=Path(directory);image=Image.new('RGB',(100,200))
            for y in range(200):
                for x in range(100):image.putpixel((x,y),(y,20,40))
            image.save(job/'reflow-scene.png');(job/'reflow-native-backdrop.json').write_text(json.dumps({'method':'resize-native-backdrop'}))
            backend=Mock();generate_scene(SimpleNamespace(job=job,layout_options={'width':100,'height':100}),backend,threading.Event(),lambda _:None)
            backend.generate.assert_not_called()
            with Image.open(job/'reflow-outpaint.png') as result:
                self.assertEqual(result.size,(100,100));self.assertGreaterEqual(result.getpixel((50,99))[0],197)
    def test_import_inside_existing_group_does_not_move_original_foreground(self):
        before=[{'id':1,'children':[{'id':2}]},{'id':3}]
        after=[{'id':1,'children':[{'id':2},{'id':4}]},{'id':3}]
        self.assertEqual(imported_layer(before,after),4)
        with self.assertRaises(ValueError):imported_layer(before,before)
    def test_nested_gradients_bake_with_scene_but_logo_and_text_do_not(self):
        info={'width':100,'height':100,'layers':[{'kind':'Group','children':[{'kind':'Type'},{'kind':'Smart Object','bounds':[0,0,20,10]},{'kind':'Fill'}]},{'kind':'Pixel','bounds':[0,0,100,100]},{'kind':'Pixel','visible':False,'bounds':[0,0,100,100]}]}
        self.assertEqual(scene_roots(info),[(0,2),(1,)])

    def test_extension_keeps_original_product_pixels_and_fills_surroundings(self):
        source=Image.new('RGBA',(100,100),(10,20,30,255))
        generated=Image.new('RGBA',(75,100),(70,80,90,255))
        result=compose_scene(source,generated,(100,150))
        self.assertEqual(result.size,(100,150))
        self.assertEqual(result.getpixel((50,75)),(10,20,30,255))
        self.assertEqual(result.getpixel((50,0)),(70,80,90,255))
        self.assertEqual(result.getchannel('A').getextrema(),(255,255))
        self.assertEqual(scene_placement((100,100),(100,150)),((100,100),(0,25)))

    def test_internal_transparency_uses_generated_background(self):
        source=Image.new('RGBA',(100,100),(0,0,0,0))
        generated=Image.new('RGBA',(100,150),(70,80,90,255))
        self.assertEqual(compose_scene(source,generated,(100,150)).getpixel((50,75)),(70,80,90,255))
