import base64
from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import Mock,patch
from PIL import Image
from photocraft_ai.references import validate_references,save_references
from photocraft_ai.service import Service
from photocraft_ai.native import NativeWorker
from photocraft_ai.backend import CodexBackend,failure_from_log


def attachment(name='one.png',color='red'):
    b=BytesIO();Image.new('RGBA',(8,6),color).save(b,format='PNG')
    return {'name':name,'data':base64.b64encode(b.getvalue()).decode('ascii')}


class ReferenceTests(unittest.TestCase):
    def test_codex_input_limit_message_is_preserved(self):
        error=failure_from_log(json.dumps({'type':'error','message':'Too many images for the selected model'}))
        self.assertEqual(error.code,'input_limit')
        self.assertEqual(str(error),'Too many images for the selected model')
    def test_multiple_images_keep_order_and_are_saved_only_under_job(self):
        with tempfile.TemporaryDirectory() as d:
            paths,names=save_references([attachment('../../one.png'),attachment('two.png','blue')],Path(d))
            self.assertEqual(names,['../../one.png','two.png'])
            self.assertEqual([p.name for p in paths],['reference-01.png','reference-02.png'])
            self.assertTrue(all(p.parent==Path(d)/'references' for p in paths))
            with Image.open(paths[1]) as i:self.assertEqual(i.getpixel((0,0)),(0,0,255,255))

    def test_invalid_shapes_counts_paths_and_base64_are_rejected(self):
        for value in [None,{},[{'path':'private.png'}]]:
            with self.subTest(value=type(value)),self.assertRaises(ValueError):validate_references(value)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):save_references([{'name':'bad','data':'%%%'}],Path(d))
            with self.assertRaises(OSError):save_references([{'name':'bad','data':base64.b64encode(b'not image').decode()}],Path(d))

    def test_more_than_five_references_are_forwarded(self):
        with tempfile.TemporaryDirectory() as d:
            paths,_=save_references([attachment(str(i)+".png") for i in range(7)],Path(d))
            self.assertEqual(len(paths),7)

    def test_pixel_and_payload_limits(self):
        with tempfile.TemporaryDirectory() as d,patch('photocraft_ai.references.MAX_PIXELS',10):
            with self.assertRaises(ValueError):save_references([attachment()],Path(d))
        with patch('photocraft_ai.references.MAX_BYTES',3):
            with self.assertRaises(ValueError):validate_references([attachment()])
        with patch('photocraft_ai.references.MAX_TOTAL',3):
            with self.assertRaises(ValueError):validate_references([attachment()])

    def test_exif_orientation_preserves_full_resolution(self):
        b=BytesIO();image=Image.new('RGB',(3000,1000),'red');exif=Image.Exif();exif[274]=6
        image.save(b,format='JPEG',exif=exif)
        with tempfile.TemporaryDirectory() as d:
            paths,_=save_references([{'name':'photo.jpg','data':base64.b64encode(b.getvalue()).decode()}],Path(d))
            with Image.open(paths[0]) as result:
                self.assertEqual(result.size,(1000,3000));self.assertLess(result.width,result.height)

    def test_service_forwards_actual_reference_files_to_backend(self):
        with tempfile.TemporaryDirectory() as d:
            backend=Mock();service=Service(None,Path(d),backend)
            prepared=service.prepare('create','two photos',references=[attachment(),attachment('two.png','blue')])
            service.generate(prepared,threading.Event(),lambda _:None)
            paths=backend.generate.call_args.kwargs['reference_images']
            self.assertEqual(len(paths),2);self.assertTrue(all(p.is_file() for p in paths))
            self.assertEqual(json.loads((prepared.job/'job.json').read_text(encoding='utf-8'))['references'],['one.png','two.png'])

    def test_worker_forwards_references_and_rejects_bad_request_before_busy(self):
        worker=NativeWorker(None)
        with self.assertRaises(ValueError):worker.submit({'mode':'generate','prompt':'test','references':[{'path':'secret'}]})
        self.assertFalse(worker.snapshot()['busy'])
        service=Mock();service.lock=threading.Lock();target=Mock(index=0);target.name='test'
        service.bridge.active_image.return_value=target;service.bridge._revision.return_value=7
        worker=NativeWorker(service);refs=[attachment(),attachment('two.png')]
        worker._run({'mode':'generate','prompt':'test','document':{'index':0,'name':'test','revision':7},'references':refs})
        self.assertFalse(worker.snapshot()['error']);self.assertEqual(service.prepare.call_args.kwargs['references'],refs)

    def test_cli_receives_each_image_attachment_and_role_instructions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.png';guide=root/'guide.png'
            image=Image.new('RGBA',(8,8),'red');image.putpixel((0,0),(0,255,0,255));image.save(source)
            Image.new('RGBA',(8,8),'blue').save(guide)
            Image.new('L',(8,8),255).save(root/'selection.png')
            refs,_=save_references([attachment(),attachment('two.png')],root)
            script=root/'fake_cli.py';script.write_text(
                'import sys,json\nfrom pathlib import Path\nfrom PIL import Image\nsys.stdin.read()\n'
                'Path("argv.json").write_text(json.dumps(sys.argv[1:]))\nImage.new("RGB",(8,8),"red").save("generated.png")\n',encoding='utf-8')
            with patch('photocraft_ai.backend.codex_command',return_value=[sys.executable,str(script)]):
                CodexBackend().generate(root,'combine references','fill',threading.Event(),lambda _:None,source,guide,reference_images=refs)
            args=json.loads((root/'argv.json').read_text());images=[args[i+1] for i,a in enumerate(args) if a=='--image']
            self.assertEqual(images,[str(source),str(guide),*map(str,refs)])
            self.assertIn('Reference 1 is attachment Image 3',(root/'request.txt').read_text(encoding='utf-8'))
