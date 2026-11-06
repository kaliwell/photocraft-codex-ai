import unittest
from PIL import Image
from photocraft_ai.reflow_background import scene_roots,scene_placement,compose_scene,imported_layer


class BackgroundTests(unittest.TestCase):
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
