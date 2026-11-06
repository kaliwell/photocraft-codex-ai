"""Local prompt/reference snapshots. No canvas commands and no remote requests."""
import base64
import hashlib
from io import BytesIO
from PIL import Image, ImageOps
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import threading
import uuid

from .references import save_references, validate_references, MAX_BYTES, MAX_TOTAL


class History:
    @staticmethod
    def _fingerprint(prompt, mode, references, options=None):
        digest=hashlib.sha256(json.dumps([prompt,mode],ensure_ascii=False).encode('utf-8'))
        if options is not None:digest.update(json.dumps(options,sort_keys=True,ensure_ascii=False).encode('utf-8'))
        for item in references:
            data=base64.b64decode(item['data'],validate=True)
            with Image.open(BytesIO(data)) as image:
                if image.width*image.height>100_000_000:
                    raise ValueError('History reference exceeds the pixel guard')
                upright=ImageOps.exif_transpose(image).convert('RGBA')
                digest.update(json.dumps([item['name'],upright.size],ensure_ascii=False).encode('utf-8'))
                digest.update(hashlib.sha256(upright.tobytes()).digest())
        return digest.hexdigest()

    def __init__(self, root, max_entries=50, max_bytes=512*1024*1024):
        self.root = Path(root)
        self.max_entries, self.max_bytes = max_entries, max_bytes
        self.lock = threading.RLock()

    def _folder(self, identifier):
        if not isinstance(identifier, str) or not re.fullmatch('[a-f0-9]{32}', identifier):
            raise ValueError('Invalid history identifier')
        folder = self.root / identifier
        if folder.is_symlink() or folder.resolve().parent != self.root.resolve():
            raise ValueError('Invalid history directory')
        return folder

    def _records(self):
        if not self.root.exists():
            return []
        records = []
        for folder in self.root.iterdir():
            if not re.fullmatch('[a-f0-9]{32}', folder.name) or not folder.is_dir() or folder.is_symlink():
                continue
            if folder.resolve().parent != self.root.resolve():
                continue
            try:
                path = folder / 'snapshot.json'
                if path.is_symlink() or path.stat().st_size > 32768:
                    continue
                meta = json.loads(path.read_text(encoding='utf-8'))
                if (meta['id'] != folder.name or not isinstance(meta['created'], str)
                    or not isinstance(meta['prompt'],str) or not isinstance(meta['names'],list)
                    or not isinstance(meta['bytes'],int) or meta['bytes']<0
                    or meta['mode'] not in ('fill','remove','generate','layout')):
                    continue
                datetime.fromisoformat(meta['created']).astimezone()
                records.append(meta)
            except (OSError, ValueError, KeyError, TypeError, OverflowError):
                continue
        return sorted(records, key=lambda r: r['created'], reverse=True)

    def list(self):
        with self.lock:
            return [{'id':r['id'], 'created':r['created'], 'mode':r['mode'],
                     'display_time':datetime.fromisoformat(r['created']).astimezone().strftime('%Y-%m-%d %H:%M:%S %z'),
                     'prompt':r['prompt'][:120], 'references':len(r['names'])}
                    for r in self._records()[:self.max_entries]]

    def save(self, request):
        with self.lock:
            prompt, mode = request.get('prompt', ''), request.get('mode', 'generate')
            if not isinstance(prompt, str) or len(prompt)>4000 or mode not in ('fill','remove','generate','layout'):
                raise ValueError('Invalid history draft')
            references = validate_references(request.get('references', []))
            options=None
            if request.get('layout_options') is not None:
                from .layout import validate_options
                options=validate_options(request['layout_options'])
            fingerprint=self._fingerprint(prompt,mode,references,options)
            for previous in self._records():
                if (previous['prompt']!=prompt or previous['mode']!=mode
                    or previous['names']!=[item['name'] for item in references]):
                    continue
                try:
                    old=previous.get('fingerprint')
                    if old is None:
                        restored=self.restore(previous['id'])
                        old=self._fingerprint(restored['prompt'],restored['mode'],restored['references'],restored.get('layout_options'))
                    if old==fingerprint:
                        return previous['id']
                except (OSError,ValueError,KeyError,TypeError):
                    continue
            self.root.mkdir(parents=True, exist_ok=True)
            identifier = uuid.uuid4().hex
            folder = self._folder(identifier)
            folder.mkdir()
            try:
                paths, names = save_references(references, folder)
                size = sum(p.stat().st_size for p in paths)
                if size>MAX_TOTAL or any(p.stat().st_size>MAX_BYTES for p in paths):
                    raise ValueError('History references exceed local resource limits')
                meta = {'id':identifier,'created':datetime.now(timezone.utc).isoformat(timespec='microseconds'),
                        'prompt':prompt,'mode':mode,'names':names,'bytes':size,'fingerprint':fingerprint}
                if options is not None:meta['layout_options']=options
                temporary = folder/'snapshot.tmp'
                encoded=json.dumps(meta,ensure_ascii=False).encode('utf-8')
                if len(encoded)>32768:
                    raise ValueError('History metadata exceeds the local size guard')
                temporary.write_bytes(encoded)
                temporary.replace(folder/'snapshot.json')
            except Exception:
                shutil.rmtree(self._folder(identifier))
                raise
            kept, total = 0, 0
            for record in self._records():
                total += record['bytes'] + (self._folder(record['id'])/'snapshot.json').stat().st_size; kept += 1
                if kept>self.max_entries or total>self.max_bytes:
                    shutil.rmtree(self._folder(record['id']))
            return identifier

    def restore(self, identifier):
        with self.lock:
            folder=self._folder(identifier)
            if (folder/'snapshot.json').is_symlink() or (folder/'snapshot.json').stat().st_size>32768:
                raise ValueError('History metadata is too large')
            meta=json.loads((folder/'snapshot.json').read_text(encoding='utf-8'))
            if (meta['id'] != identifier or not isinstance(meta['prompt'],str) or len(meta['prompt'])>4000
                or meta['mode'] not in ('fill','remove','generate','layout') or not isinstance(meta['names'],list)):
                raise ValueError('Invalid history metadata')
            refs=[]; total=0
            if ((folder/'references').is_symlink()
                or ((folder/'references').exists() and (folder/'references').resolve().parent != folder.resolve())):
                raise ValueError('Invalid history reference directory')
            for index,name in enumerate(meta['names'],1):
                path=folder/'references'/f'reference-{index:02}.png'
                if path.is_symlink() or path.resolve().parent != (folder/'references').resolve():
                    raise ValueError('Invalid history reference')
                size=path.stat().st_size; total+=size
                if size>MAX_BYTES or total>MAX_TOTAL:
                    raise ValueError('History references exceed local resource limits')
                refs.append({'name':name,'data':base64.b64encode(path.read_bytes()).decode('ascii')})
            validate_references(refs)
            result={'prompt':meta['prompt'],'mode':meta['mode'],'references':refs}
            if meta.get('layout_options') is not None:
                from .layout import validate_options
                result['layout_options']=validate_options(meta['layout_options'])
            return result
