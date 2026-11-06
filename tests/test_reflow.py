import unittest
from photocraft_ai.reflow import content_units,validate_plan


class ReflowTests(unittest.TestCase):
    def test_unnamed_full_canvas_photo_and_edge_repair_stay_aligned(self):
        info={'width':1500,'height':1500,'layers':[{'kind':'Group','name':'Copy','children':[{'kind':'Type','name':'Title','bounds':[0,0,500,100]}]},{'kind':'Pixel','name':'Layer 2','bounds':[-131,0,209,1500]},{'kind':'Pixel','name':'Layer 1','bounds':[60,0,1500,1500]},{'kind':'Pixel','name':'Hidden scene','visible':False,'bounds':[0,0,1500,1500]}]}
        units,backgrounds=content_units(info)
        self.assertEqual(len(units),1)
        self.assertEqual([b['path'] for b in backgrounds],[(1,),(2,)])
        self.assertTrue(all(b['scene'] for b in backgrounds))
    def test_combined_workspace_guard_prevents_crossed_large_canvases(self):
        from photocraft_ai.reflow import validate_workspace
        validate_workspace({'width':1500,'height':2000},1500,1500)
        with self.assertRaises(ValueError):validate_workspace({'width':30000,'height':1000},1000,30000)
    def test_split_background_panels_and_divider_are_not_scaled_with_photos(self):
        info={'width':1500,'height':2000,'layers':[{'kind':'Group','name':'Split scene','children':[{'kind':'Pixel','name':'分隔线','bounds':[749,0,2,2000]},{'kind':'Smart Object','name':'Photo','bounds':[750,0,750,1800],'clipped':True},{'kind':'Pixel','name':'浅灰右栏','bounds':[750,0,750,2000]},{'kind':'Pixel','name':'深灰左栏','bounds':[0,0,750,2000]}]}]}
        units,backgrounds=content_units(info)
        self.assertEqual(len(units),1)
        self.assertEqual(len(backgrounds),3)
        self.assertEqual(units[0]['path'],(0,1))
    def test_extracts_content_groups_separately_from_flat_background(self):
        info={'width':1500,'height':2000,'layers':[{'kind':'Group','name':'Headline','children':[{'kind':'Type','name':'Title','bounds':[100,100,600,100]}]},{'kind':'Group','name':'Scene','children':[{'kind':'Smart Object','name':'Product','bounds':[-100,400,1700,1500]},{'kind':'Pixel','name':'整页底色','bounds':[0,0,1500,2000]}]},{'kind':'Type','name':'Hidden','visible':False,'bounds':[0,0,20,20]}]}
        units,backgrounds=content_units(info)
        self.assertEqual([u['path'] for u in units],[(0,),(1,0)])
        self.assertEqual(units[1]['bounds'],[0,400,1500,1500])
        self.assertEqual(backgrounds[0]['path'],(1,1))

    def test_plan_requires_all_units_uniform_scale_and_in_bounds(self):
        units=[{'key':'u1','bounds':[0,0,500,500]}]
        self.assertEqual(validate_plan({'placements':[{'key':'u1','x':10,'y':10,'scale':1}]},units,1000,1000)['placements'][0]['scale'],1)
        invalid=[[],[{'key':'other','x':0,'y':0,'scale':1}],[{'key':'u1','x':900,'y':0,'scale':1}],[{'key':'u1','x':0,'y':0,'scale':float('nan')}],[{'key':'u1','x':0,'y':0,'scale':1,'command':'run'}]]
        for placements in invalid:
            with self.assertRaises(ValueError):validate_plan({'placements':placements},units,1000,1000)
