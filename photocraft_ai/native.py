"""Authenticated local worker for the native PhotoCraft selection toolbar."""
from __future__ import annotations
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import base64
import hmac
import json
import os
from pathlib import Path
import secrets
import threading
import time

from .__main__ import ROOT, RUNTIME, connect, panel_lock
from .backend import Cancelled
from .service import Service
from .references import validate_references
from .localization import english
from .history import History

API_PORT = 17923
EDITOR_PORT = 17924


class NativeWorker:
    def __init__(self, service):
        self.service = service
        self.lock = threading.Lock()
        self.cancel = threading.Event()
        self.state = {'busy': False, 'message': '就绪', 'error': False, 'job': None}
        self.history = History(RUNTIME / 'native-history')
        self.project_histories = {}

    def history_for(self, request):
        if self.service is None:
            return self.history
        session=self.service.bridge.client.run('session.inspect')
        expected=request.get('document', {})
        active=session.get('active')
        document=next((d for d in session.get('documents',[]) if d.get('index')==active),None)
        if not document or (document.get('index'),document.get('name')) != (expected.get('index'),expected.get('name')):
            raise ValueError('The active project changed; reopen history')
        if 'path' in expected and expected['path'] != document.get('path'):
            raise ValueError('The active project changed; reopen history')
        path=document.get('path')
        if not path:
            raise ValueError('Save the project first to store history beside the project file')
        project=Path(path)
        if not project.is_absolute():
            raise ValueError('The project path must be absolute')
        folder=project.with_name(project.name+'.photocraft-023-data')/'history'
        key=str(folder)
        with self.lock:
            if key not in self.project_histories:
                self.project_histories[key]=History(folder)
            return self.project_histories[key]

    def snapshot(self):
        with self.lock:
            result = dict(self.state)
            result['message'] = english(result['message'])
            return result

    def update(self, **fields):
        with self.lock:
            self.state.update(fields)

    def submit(self, request):
        mode = request.get('mode')
        prompt = request.get('prompt', '')
        if mode not in ('fill', 'remove', 'generate','layout','detail','batch','reflow') or not isinstance(prompt, str) or len(prompt) > 4000:
            raise ValueError('请求参数无效。')
        if mode not in ('remove','layout','detail','batch','reflow') and not prompt.strip():
            raise ValueError('请先输入画面描述。')
        validate_references(request.get('references',[]))
        if mode in ('layout','detail','batch','reflow'):
            from .layout import validate_options
            validate_options(request.get('layout_options'))
        document=request.get('document',{})
        if not isinstance(document,dict):raise ValueError('Invalid document context')
        anchor=document.get('insertionLayer')
        if anchor is not None and (type(anchor) is not int or not 0<anchor<2**64):raise ValueError('Invalid insertion layer')
        with self.lock:
            if self.state['busy']:
                raise ValueError('已有生成任务正在运行。')
            self.state = {'busy': True, 'message': '正在读取选区…', 'error': False, 'job': None}
            self.cancel.clear()
        threading.Thread(target=self._run, args=(request,), daemon=True).start()

    def _run(self, request):
        started = time.monotonic()
        prepared=None
        try:
            service = self.service
            if service is None:
                raise RuntimeError('编辑器尚未连接。')
            with service.lock:
                current = service.bridge.active_image()
                expected = request.get('document', {})
                if not current or (current.index, current.name, service.bridge._revision(current)) != (
                    expected.get('index'), expected.get('name'), expected.get('revision')
                ):
                    raise RuntimeError('选区或文档已经改变，请重新点击生成。')
                mode = request['mode']
                prompt = request.get('prompt', '').strip()
                prepared = service.prepare(mode, prompt,
                                           feather_px=0 if mode == 'generate' else 12,
                                           references=request.get('references', []),
                                           **({'layout_options':request.get('layout_options')} if mode in ('layout','detail','batch','reflow') else {}))
                if 'insertionLayer' in expected:
                    prepared.active_layer=expected['insertionLayer']
            try:
                history_request=request
                if mode in ('layout','detail','batch','reflow') and prepared.layout_options.get('source')=='layers':
                    history_request={**request,'references':[{'name':'Selected layers.png','data':base64.b64encode(prepared.references[0].read_bytes()).decode('ascii')}],
                                     'layout_options':{**prepared.layout_options,'source':'references'}}
                self.history_for(request).save(history_request)
            except Exception as error:
                self.update(history_warning=str(error))
            self.update(job=str(prepared.job))
            if mode=='batch':
                from .batch_layout import run_batch
                report=run_batch(service,prepared,self.cancel,lambda text:self.update(message=text))
                failed=sum(item['status']=='failed' for item in report['items'])
                self.update(busy=False,error=bool(failed),message=f'Batch PSD complete: {len(report["items"])-failed}/{len(report["items"])}; {report["output"]}')
                return
            result = service.generate(prepared, self.cancel, lambda text: self.update(message=text))
            if self.cancel.is_set():
                raise Cancelled('已取消')
            self.update(message='正在添加新图层…')
            applied=service.apply(prepared, result)
            elapsed = time.monotonic() - started
            self.update(busy=False,
                        message=('Layout added to current document; save the project when ready' if applied is None else f'PSD base layout saved: {applied}') if mode in ('layout','detail','batch','reflow') else f'已生成到新图层 · 本次耗时 {elapsed:.1f} 秒 · Ctrl+Z 撤销',
                        error=False)
        except Cancelled:
            self.update(busy=False, message='已取消', error=False)
        except Exception as error:
            self.update(busy=False, message=str(error), error=True)
        finally:
            if prepared is not None:
                try:
                    from .cache import complete,maintain
                    complete(prepared.job)
                    maintain(prepared.job.parent.parent)
                except (OSError,TypeError,ValueError):pass


def handler(worker: NativeWorker, token: str):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, data):
            payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Connection', 'close')
            self.end_headers()
            self.wfile.write(payload)

        def authorized(self):
            if not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + token):
                self.respond(401, {'message': '拒绝未认证请求', 'error': True})
                return False
            # No cross-origin web requests, even if a browser learned the token.
            if self.headers.get('Origin'):
                self.respond(403, {'message': '不接受网页请求', 'error': True})
                return False
            return True

        def do_GET(self):
            if not self.authorized():
                return
            if self.path != '/state':
                self.respond(404, {'message': '未知操作', 'error': True})
                return
            self.respond(200, worker.snapshot())

        def do_POST(self):
            if not self.authorized():
                return
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if length < 0 or length > 350*1024*1024:
                    raise ValueError('请求过大')
                request = json.loads(self.rfile.read(length) or b'{}')
                if not isinstance(request, dict):
                    raise ValueError('请求必须是对象')
                if self.path == '/history/list':
                    self.respond(200, {'entries':worker.history_for(request).list()})
                    return
                elif self.path == '/history/save':
                    history=worker.history_for(request)
                    history.save(request)
                    self.respond(200, {'entries':history.list()})
                    return
                elif self.path == '/history/restore':
                    history=worker.history_for(request)
                    restored=history.restore(request.get('id'))
                    self.respond(200, {**restored, 'entries':history.list()})
                    return
                elif self.path == '/generate':
                    worker.submit(request)
                elif self.path == '/cancel':
                    worker.cancel.set()
                else:
                    self.respond(404, {'message': '未知操作', 'error': True})
                    return
                self.respond(202, worker.snapshot())
            except (ValueError, TypeError, OSError, KeyError) as error:
                self.respond(400, {'message': str(error), 'error': True})
    return Handler


def main():
    parser = argparse.ArgumentParser(description='PhotoCraft Codex AI 原生选区工具栏')
    upgraded = ROOT / 'native-0.23/photocraft.exe'
    build_info = upgraded.parent / 'BUILD_INFO.json'
    if build_info.is_file():
        executable = json.loads(build_info.read_text(encoding='utf-8')).get('executable', 'photocraft.exe')
        if executable in ('photocraft.exe', 'photocraft-next.exe'):
            upgraded = upgraded.with_name(executable)
    parser.add_argument('--photocraft', default=str(upgraded))
    args = parser.parse_args()
    # Separate from the fallback Tk panel.
    singleton = panel_lock('native.lock')
    if singleton is None:
        return
    worker = NativeWorker(None)
    token_file = RUNTIME / 'native-api.token'
    token = secrets.token_hex(32)
    token_file.write_text(token, encoding='utf-8')
    os.environ['PHOTOCRAFT_CODEX_PORT'] = str(API_PORT)
    os.environ['PHOTOCRAFT_CODEX_TOKEN_FILE'] = str(token_file)
    os.environ['PHOTOCRAFT_CONFIG_DIR'] = str(RUNTIME / 'native-profile')
    server = ThreadingHTTPServer(('127.0.0.1', API_PORT), handler(worker, token))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        bridge = connect(args.photocraft, EDITOR_PORT)
        worker.service = Service(bridge, RUNTIME / 'native-jobs')
        print('PhotoCraft 原生选区工具栏已启动。', flush=True)
        # Keep the service alive while the editor exists; do not close user documents.
        while True:
            threading.Event().wait(3)
            show = RUNTIME / 'native.show.request'
            if show.exists():
                show.unlink(missing_ok=True)
                bridge.client.call('ui.focus')
            if not bridge.client.alive():
                break
    finally:
        worker.cancel.set()
        server.shutdown()
        singleton.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        RUNTIME.mkdir(exist_ok=True)
        import traceback
        (RUNTIME / 'native-worker-error.log').write_text(traceback.format_exc(), encoding='utf-8')
        if os.name == 'nt':
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, str(error), 'PhotoCraft Codex AI', 0x10)
        else:
            raise
