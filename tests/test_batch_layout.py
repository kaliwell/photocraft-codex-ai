from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PIL import Image
import json,tempfile,threading,unittest
from photocraft_ai.batch_layout import run_batch
from photocraft_ai.backend import Cancelled


class BatchTests(unittest.TestCase):
    def setup_batch(self,root):
        job=root/'job';job.mkdir();exchange=root/'exchange';exchange.mkdir()
        (job/'job.json').write_text(json.dumps({'references':['same.jpg','same.jpg']}))
        refs=[]
        for i in range(2):
            p=root/f'{i}.png';Image.new('RGB',(10,20),'white').save(p);refs.append(p)
        prepared=SimpleNamespace(job=job,references=refs,prompt='',layout_options={'reference_size':True})
        service=SimpleNamespace(bridge=SimpleNamespace(exchange=exchange,client=None),lock=threading.Lock())
        return service,prepared

    def test_failure_does_not_stop_other_items_and_references_stay_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            service,prepared=self.setup_batch(Path(directory));seen=[]
            def generate(job,refs,*args,**kwargs):
                seen.append(refs)
                if len(seen)==1:raise ValueError('Bad first item')
                return job/'layout.json'
            def build(bridge,path,job):
                p=bridge.exchange/(job.name+'.psd');p.write_bytes(b'PSD');return p
            with patch('photocraft_ai.batch_layout.generate_layout',side_effect=generate),patch('photocraft_ai.batch_layout.build_layout',side_effect=build):
                report=run_batch(service,prepared,threading.Event(),lambda _:None)
            self.assertEqual([item['status'] for item in report['items']],['failed','success'])
            self.assertEqual(seen,[[prepared.references[0]],[prepared.references[1]]])
            self.assertTrue(Path(report['items'][1]['psd']).exists())
            self.assertEqual(json.loads((Path(report['output'])/'batch-report.json').read_text()),report)

    def test_cancel_retains_completed_file_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            service,prepared=self.setup_batch(Path(directory));cancel=threading.Event()
            def build(bridge,path,job):
                p=bridge.exchange/(job.name+'.psd');p.write_bytes(b'PSD');cancel.set();return p
            with patch('photocraft_ai.batch_layout.generate_layout',return_value=Path('unused')),patch('photocraft_ai.batch_layout.build_layout',side_effect=build):
                with self.assertRaises(Cancelled):run_batch(service,prepared,cancel,lambda _:None)
            report=json.loads((prepared.job/'batch-report.json').read_text())
            self.assertEqual([item['status'] for item in report['items']],['success','pending'])
            self.assertTrue(Path(report['items'][0]['psd']).exists())
