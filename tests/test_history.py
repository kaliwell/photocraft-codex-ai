import base64
from io import BytesIO
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from http.server import ThreadingHTTPServer
from urllib.request import Request, build_opener, ProxyHandler
from PIL import Image
from photocraft_ai.history import History
from photocraft_ai.native import NativeWorker, handler


def picture(name='reference.png', color='red'):
    data=BytesIO();Image.new('RGBA',(8,6),color).save(data,format='PNG')
    return {'name':name,'data':base64.b64encode(data.getvalue()).decode('ascii')}


class HistoryTests(unittest.TestCase):
    def test_reopen_restores_prompt_reference_order_names_and_pixels(self):
        with tempfile.TemporaryDirectory() as directory:
            h=History(directory)
            request={'prompt':'first prompt','mode':'fill','references':[picture('../one.png'),picture('two.png','blue')]}
            identifier=h.save(request)
            restored=History(directory).restore(identifier)
            self.assertEqual(restored['prompt'],request['prompt']);self.assertEqual(restored['mode'],'fill')
            self.assertEqual([r['name'] for r in restored['references']],['../one.png','two.png'])
            with Image.open(BytesIO(base64.b64decode(restored['references'][1]['data']))) as image:
                self.assertEqual(image.getpixel((0,0)),(0,0,255,255))
            self.assertEqual(h.list()[0]['references'],2)

    def test_text_only_drafts_and_empty_reference_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            h=History(directory);identifier=h.save({'prompt':'text only'})
            self.assertEqual(h.restore(identifier)['references'],[])

    def test_retention_removes_only_older_snapshots(self):
        with tempfile.TemporaryDirectory() as directory:
            h=History(directory,max_entries=2)
            first=h.save({'prompt':'one'});h.save({'prompt':'two'});h.save({'prompt':'three'})
            self.assertEqual([r['prompt'] for r in h.list()],['three','two'])
            self.assertFalse((Path(directory)/first).exists())

    def test_byte_retention_and_invalid_payload_cleanup(self):
        with tempfile.TemporaryDirectory() as directory:
            h=History(directory,max_bytes=100)
            h.save({'prompt':'image','references':[picture()]})
            self.assertEqual(h.list(),[])
            with self.assertRaises(OSError):h.save({'references':[{'name':'bad','data':base64.b64encode(b'bad image').decode()}]})
            self.assertEqual(list(Path(directory).iterdir()),[])

    def test_path_escape_corruption_and_missing_reference_are_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            h=History(directory)
            for identifier in ['../outside','x','',None]:
                with self.assertRaises(ValueError):h.restore(identifier)
            identifier=h.save({'prompt':'test','references':[picture()]})
            (Path(directory)/identifier/'references/reference-01.png').unlink()
            with self.assertRaises(OSError):h.restore(identifier)
            (Path(directory)/identifier/'snapshot.json').write_text('broken')
            self.assertEqual(h.list(),[])

    def test_generation_preparation_saves_history_without_remote_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            service=Mock();service.lock=threading.Lock()
            service.bridge.active_image.return_value=SimpleNamespace(index=0,name='Demo')
            service.bridge._revision.return_value=1
            service.prepare.return_value=SimpleNamespace(job=Path(directory)/'job')
            worker=NativeWorker(service);worker.history=History(Path(directory)/'history')
            worker.history_for=Mock(return_value=worker.history)
            request={'mode':'fill','prompt':'edit prompt','document':{'index':0,'name':'Demo','revision':1},'references':[picture()]}
            worker._run(request)
            self.assertFalse(worker.snapshot()['error']);self.assertEqual(worker.history.list()[0]['prompt'],'edit prompt')
            service.apply.assert_called_once()

    def test_http_restore_does_not_save_drafts_and_keeps_authentication(self):
        with tempfile.TemporaryDirectory() as directory:
            worker=NativeWorker(None);worker.history=History(directory)
            identifier=worker.history.save({'prompt':'original','references':[picture()]})
            server=ThreadingHTTPServer(('127.0.0.1',0),handler(worker,'token'))
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                url=f'http://127.0.0.1:{server.server_port}'
                opener=build_opener(ProxyHandler({}))
                data=json.dumps({'id':identifier,'draft':{'prompt':'current draft','references':[]}}).encode()
                request=Request(url+'/history/restore',data=data,headers={'Authorization':'Bearer token','Content-Type':'application/json'})
                with opener.open(request) as response:restored=json.load(response)
                self.assertEqual(restored['prompt'],'original')
                self.assertEqual(worker.history.list()[0]['prompt'],'original')
                self.assertEqual(len(worker.history.list()),1)
                with opener.open(request) as response:json.load(response)
                self.assertEqual(len(worker.history.list()),1)
                self.assertEqual(len(restored['references']),1)
                with self.assertRaises(Exception) as raised:opener.open(Request(url+'/history/list',data=b'{}'))
                self.assertEqual(raised.exception.code,401)
            finally:server.shutdown();server.server_close();thread.join()


    def test_identical_snapshots_are_reused_without_extra_files(self):
        with tempfile.TemporaryDirectory() as directory:
            h=History(directory)
            request={'prompt':'same','mode':'generate','references':[picture()]}
            first=h.save(request)
            self.assertEqual(h.save(request),first)
            meta_path=Path(directory)/first/'snapshot.json'
            meta=json.loads(meta_path.read_text(encoding='utf-8'));meta.pop('fingerprint')
            meta_path.write_text(json.dumps(meta),encoding='utf-8')
            self.assertEqual(History(directory).save(request),first)
            self.assertEqual(len(h.list()),1)
            self.assertEqual(len(list(Path(directory).iterdir())),1)
            changed={**request,'prompt':'changed'}
            self.assertNotEqual(h.save(changed),first)

    def test_project_history_uses_editor_paths_and_isolates_projects(self):
        with tempfile.TemporaryDirectory() as directory:
            service=Mock();worker=NativeWorker(service)
            first=str(Path(directory)/'one.pcraft');second=str(Path(directory)/'two.pcraft')
            def active(path):
                service.bridge.client.run.return_value={'active':0,'documents':[{'index':0,'name':'Demo','path':path}]}
            request={'document':{'index':0,'name':'Demo'}}
            active(first);a=worker.history_for(request);a.save({'prompt':'project one'})
            self.assertEqual(a.root,Path(first+'.photocraft-data')/'history')
            active(second);self.assertEqual(worker.history_for(request).list(),[])
            active(first);self.assertEqual(worker.history_for(request).list()[0]['prompt'],'project one')
            active(None)
            with self.assertRaises(ValueError):worker.history_for(request)
            active(second)
            with self.assertRaises(ValueError):worker.history_for({'document':{'index':0,'name':'Demo','path':first}})

if __name__=='__main__':unittest.main()
