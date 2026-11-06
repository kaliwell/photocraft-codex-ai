"""Bounded intermediate-file cache; exported and generated artwork is never pruned."""
import json,time,re
from pathlib import Path

LIMIT=2*1024**3
AGE=14*86400
NAMES={'source.png','guide.png','selection.png','selection-guide.png','blend-mask.png','canvas.png','reflow-source.png','reflow-scene.png'}


def safe(path,root):
    return not path.is_symlink() and not path.is_junction() and path.resolve().is_relative_to(root.resolve())


def intermediates(job):
    # Never traverse links or remove directories, PSDs, generated images or history.
    def walk(folder):
        for p in folder.iterdir():
            if not safe(p,job):continue
            if p.is_dir():yield from walk(p)
            elif p.is_file() and (p.name in NAMES or (p.parent.name=='references' and re.fullmatch(r'reference-\d+\.png',p.name))):yield p
    yield from walk(job)


def directory_bytes(folder):
    if not folder.exists() or folder.is_symlink() or folder.is_junction():return 0
    total=0
    for p in folder.iterdir():
        if not safe(p,folder):continue
        if p.is_dir():total+=directory_bytes(p)
        elif p.is_file():total+=p.stat().st_size
    return total


def maintain(runtime,*,force=False,now=None,limit=LIMIT,age=AGE,active=None,dry_run=False):
    runtime=Path(runtime);root=runtime/'native-jobs';now=time.time() if now is None else now
    files=[]
    if root.exists() and safe(root,runtime):
        for job in root.iterdir():
            if not safe(job,root) or not job.is_dir() or (active and job.resolve()==Path(active).resolve()):continue
            marker=job/'.cache-complete.json'
            if not marker.is_file() or not safe(marker,job):continue
            for p in intermediates(job):
                stat=p.stat();files.append((stat.st_mtime,p,stat.st_size))
    total=sum(x[2] for x in files);removed=0
    for modified,p,size in sorted(files):
        if not dry_run and (force or now-modified>age or total>limit):
            try:p.unlink()
            except OSError:continue
            total-=size;removed+=size
    return {'eligible_cache_bytes':total,'removed_bytes':removed,'job_bytes':directory_bytes(root),'exchange_bytes':directory_bytes(runtime/'exchange'),'limit_bytes':limit,'retention_days':age//86400,'preserves':'PSDs, generated artwork, active/unmarked jobs, history and exchange outputs'}


def complete(job):
    (Path(job)/'.cache-complete.json').write_text(json.dumps({'completed':time.time()}),encoding='utf8')
