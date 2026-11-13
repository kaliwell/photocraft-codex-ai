import unittest
from photocraft_ai.reflow import content_units,validate_plan


class ReflowTests(unittest.TestCase):
    def test_six_clipping_panels_bind_captions_from_a_different_folder(self):
        panels=[];labels=[]
        for y in (20,170,320):
            for x in (20,280):
                panels += [{'kind':'Pixel','name':'Photo','clipped':True,'bounds':[x-20,y-20,180,200]},
                           {'kind':'Shape','name':'Card','bounds':[x,y,120,130]}]
                labels += [{'kind':'Type','name':'Caption','bounds':[x+10,y+10,100,20],'text':{'text':'feature'}}]
        info={'width':500,'height':600,'split_reflow_groups':True,'layers':[
            {'kind':'Group','name':'Titles','children':labels}, {'kind':'Group','name':'Panels','children':panels}]}
        units,_=content_units(info)
        self.assertEqual(len(units),6)
        self.assertTrue(all(len(u['paths'])==3 and u['peer_panel']==[120,130] for u in units))
        paths=[p for u in units for p in u['paths']]
        self.assertEqual(len(paths),len(set(paths)))
        info['layers'][1]['hasMask']=True
        units,_=content_units(info)
        self.assertTrue(any(u['path']==(1,) and not u.get('paths') for u in units))

    def test_product_callouts_and_shadow_share_one_transform(self):
        product={'kind':'Group','name':'Product','children':[{'kind':'Smart Object','name':'Pen','bounds':[100,20,20,400]}]}
        arrows=[{'kind':'Pixel','name':'Arrow','bounds':[125,y,30,8]} for y in (40,240)]
        text=[{'kind':'Type','name':'Label','bounds':[160,y,90,20],'text':{'text':'feature'}} for y in (35,235)]
        labels={'kind':'Group','name':'Callouts','children':arrows+text}
        shadow={'kind':'Smart Object','name':'Shadow','bounds':[105,400,300,20],'hasMask':True,'smartFilters':[{'command':'filter.blur.motionBlur'}]}
        info={'width':500,'height':600,'split_reflow_groups':True,'layers':[product,labels,shadow]}
        units,_=content_units(info)
        self.assertEqual(len(units),1)
        self.assertEqual(units[0]['paths'],[(0,),(1,),(2,)])
        self.assertEqual(units[0]['rasterize_support_paths'],[(2,)])
        self.assertEqual(units[0]['bounds'],[100,20,150,400])
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
        self.assertEqual(len(backgrounds),0)
        self.assertEqual(units[0]['path'],(0,))
        # Independent panels may split only after the photo is unlinked.
        info['layers'][0]['children'][1]['clipped']=False
        units,backgrounds=content_units(info)
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
