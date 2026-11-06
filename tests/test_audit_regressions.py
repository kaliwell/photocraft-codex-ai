import json,tempfile,unittest,time,os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image,ImageDraw
from photocraft_ai.reflow import content_units,analyze_reflow
from photocraft_ai.reflow_merged import duplicate_cover
from photocraft_ai.reflow_background import scene_roots
from photocraft_ai.cache import maintain,complete


class AuditRegressionTests(unittest.TestCase):
    def test_outpaint_keeps_clipped_and_masked_groups_atomic(self):
        for props in ({},{'hasMask':True}):
            card={'kind':'Group','name':'Card','children':[{'kind':'Smart Object','name':'Photo','clipped':not props,'bounds':[0,0,40,40]},{'kind':'Shape','name':'Base','bounds':[0,0,40,40]}],**props}
            info={'width':100,'height':100,'split_reflow_groups':True,'layers':[card,{'kind':'Pixel','name':'Scene','bounds':[0,0,100,100]}]}
            self.assertEqual(content_units(info)[0][0]['path'],(0,))
            self.assertEqual(scene_roots(info),[(1,)])

    def test_local_stamp_changes_are_never_hidden(self):
        a=Image.new('RGBA',(400,400),'white');b=a.copy()
        ImageDraw.Draw(b).rectangle((40,320,359,339),fill='black')
        self.assertFalse(duplicate_cover(a,b))
        b=a.copy();b.putpixel((200,200),(0,0,0,255))
        self.assertFalse(duplicate_cover(a,b))
        self.assertTrue(duplicate_cover(a,a))

    def test_flattened_psd_skips_layout_model_and_keeps_empty_plan(self):
        info={'width':100,'height':100,'layers':[{'kind':'Pixel','name':'Flattened','bounds':[0,0,100,100]}]}
        self.assertEqual(content_units(info)[0],[])
        with tempfile.TemporaryDirectory() as folder,patch('photocraft_ai.reflow.analyze_json') as model:
            job=Path(folder);(job/'reflow-source.json').write_text(json.dumps(info))
            prepared=SimpleNamespace(job=job,source=job/'reflow-source.png',layout_options={'width':100,'height':150},prompt='')
            path=analyze_reflow(prepared,None,None)
            self.assertEqual(json.loads(path.read_text()),{'placements':[]});model.assert_not_called()

    def test_cache_pruning_preserves_results_history_and_active_jobs(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime=Path(folder);job=runtime/'native-jobs'/'done';job.mkdir(parents=True);complete(job)
            for name in ('source.png','generated.png','art.psd'):(job/name).write_bytes(b'0123456789')
            active=runtime/'native-jobs'/'active';active.mkdir();(active/'source.png').write_bytes(b'active')
            exchange=runtime/'exchange';exchange.mkdir();(exchange/'result.psd').write_bytes(b'psd')
            self.assertEqual(maintain(runtime,dry_run=True)['removed_bytes'],0)
            self.assertEqual(maintain(runtime,force=True)['removed_bytes'],10)
            for p in [job/'generated.png',job/'art.psd',active/'source.png',exchange/'result.psd']:self.assertTrue(p.exists())

    def test_cache_capacity_evicts_oldest_intermediates_only(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime=Path(folder);job=runtime/'native-jobs'/'done';job.mkdir(parents=True);complete(job)
            for i,name in enumerate(('source.png','guide.png')):
                p=job/name;p.write_bytes(b'0123456789');os.utime(p,(100+i,100+i))
            result=maintain(runtime,now=105,limit=10,age=1000)
            self.assertEqual(result['removed_bytes'],10);self.assertFalse((job/'source.png').exists());self.assertTrue((job/'guide.png').exists())

    def test_expired_cache_and_dry_run(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime=Path(folder);job=runtime/'native-jobs'/'done';job.mkdir(parents=True);complete(job)
            p=job/'source.png';p.write_bytes(b'cache');os.utime(p,(100,100))
            self.assertEqual(maintain(runtime,now=100+15*86400,dry_run=True)['removed_bytes'],0)
            self.assertEqual(maintain(runtime,now=100+15*86400)['removed_bytes'],5)
