import unittest
from PIL import Image
from photocraft_ai.reflow_merged import candidates,similarity
from photocraft_ai.reflow import content_units
from photocraft_ai.reflow_background import scene_roots


class MergedCoverTests(unittest.TestCase):
    def test_hidden_versions_are_skipped_and_visible_stamp_is_candidate(self):
        info={'width':100,'height':100,'layers':[{'kind':'Pixel','visible':False,'bounds':[0,0,100,100]},{'kind':'Pixel','bounds':[0,0,100,100]},{'kind':'Group','children':[{'kind':'Type'}]}]}
        self.assertEqual(candidates(info),[1])
        info['layers'][1]['hasMask']=True
        self.assertEqual(candidates(info),[])

    def test_real_foreground_photo_or_partial_overlay_is_not_a_stamp(self):
        info={'width':100,'height':100,'layers':[{'kind':'Pixel','bounds':[0,0,100,80]},{'kind':'Type'}]}
        self.assertEqual(candidates(info),[])
        info['layers'][0]['bounds']=[0,0,100,100]
        info['layers'][0]['opacity']=.5
        self.assertEqual(candidates(info),[])

    def test_visual_comparison_accepts_duplicate_but_rejects_different_content(self):
        a=Image.new('RGBA',(100,100),(0,30,100,255))
        self.assertEqual(similarity(a,a),(0,1))
        mean,close=similarity(a,Image.new('RGBA',(100,100),'white'))
        self.assertGreater(mean,16)
        self.assertLess(close,.8)

    def test_card_clipping_and_color_labels_remain_foreground_group(self):
        info={'width':100,'height':100,'layers':[{'kind':'Group','name':'Cards','children':[{'kind':'Type','name':'Label','bounds':[0,0,10,10]},{'kind':'Smart Object','name':'Model','clipped':True,'bounds':[0,0,50,50]},{'kind':'Pixel','name':'Card','bounds':[0,0,50,50]}]},{'kind':'Pixel','name':'Background','bounds':[0,0,100,100]}]}
        self.assertEqual(scene_roots(info),[(1,)])
        units,_=content_units(info)
        self.assertEqual(units[0]['path'],(0,))
