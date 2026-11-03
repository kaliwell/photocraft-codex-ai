"""Attach local test pictures to an isolated QA editor; never requests AI generation."""
from pathlib import Path
import argparse
import json
import shutil
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from photocraft_ai.bridge import ControlClient,PhotoCraftBridge


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--folder',type=Path,required=True)
    p.add_argument('--port',type=int,default=17980)
    args=p.parse_args();r=args.runtime.resolve();folder=args.folder.resolve()
    c=ControlClient(args.port,r/'control.token',timeout=30)
    for _ in range(60):
        if c.alive():break
        time.sleep(.25)
    bridge=PhotoCraftBridge(c,r/'exchange',r)
    assert not bridge.documents(),'Use a fresh isolated QA editor'
    c.run('file.new',width=512,height=512)
    c.run('select.rect',x=100,y=80,width=280,height=280)
    before=c.run('document.inspect')
    c.call('ui.set',fit=True)
    files=[]
    for path in sorted(folder.iterdir()):
        if path.is_file() and path.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.bmp','.gif','.tif','.tiff'):
            dest=r/'exchange'/path.name
            if path!=dest:shutil.copy2(path,dest)
            files.append(dest)
    assert files,'No test pictures'
    c.call('ui.codexAI.references',paths=[str(p) for p in files])
    for _ in range(200):
        state=c.call('ui.inspect')['codexAI']
        if not state['referenceLoading']:break
        time.sleep(.1)
    assert not state['error'],state
    assert [f['name'] for f in state['references']]==[p.name for p in files],state
    assert state['rect'],'Launch QA editor with a local test receiver enabled'
    if len(files)>1:
        button=next(b for b in state['buttons'] if b['label']=='移除参考图2')
        x,y,w,h=button['rect'];c.call('ui.move',x=x+w/2,y=y+h/2);c.call('ui.click',x=x+w/2,y=y+h/2)
        assert len(c.call('ui.inspect')['codexAI']['references'])==len(files)-1
    assert c.run('document.inspect')==before
    c.call('ui.screenshot',path='reference-gallery.png')
    report={'loaded':[p.name for p in files],'removal_verified':len(files)>1,'document_preserved':True,'live_generation':False}
    (r/'reference-gallery-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__=='__main__':main()
