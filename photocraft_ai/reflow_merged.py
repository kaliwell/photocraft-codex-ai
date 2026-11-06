"""Recognize leading stamped copies by comparing with the editable stack below."""
import copy,json,uuid
from PIL import Image,ImageChops,ImageStat


def candidates(info):
    def editable(row):
        return row.get('visible',True) and (row['kind'] in ('Type','Shape') or any(editable(r) for r in row.get('children',[])))
    rows=info['layers'];first=next((i for i,r in enumerate(rows) if editable(r)),None)
    if first is None:return []
    result=[]
    for i,row in enumerate(rows[:first]):
        if not row.get('visible',True):continue
        b=row.get('bounds')
        if row['kind']!='Pixel' or not b or row.get('hasMask') or row.get('clipped') or row.get('blend','Normal')!='Normal' or row.get('opacity',1)<.999:return []
        x,y,w,h=b
        if x>0 or y>0 or x+w<info['width'] or y+h<info['height']:return []
        result.append(i)
    return result


def similarity(first,second):
    a=first.convert('RGB').resize((192,192),Image.Resampling.LANCZOS)
    b=second.convert('RGB').resize((192,192),Image.Resampling.LANCZOS)
    diff=ImageChops.difference(a,b)
    mean=sum(ImageStat.Stat(diff).mean)/3
    close=sum(max(pixel)<=24 for pixel in diff.getdata())/(192*192)
    return mean,close


def duplicate_cover(first,second):
    # Full-resolution RGBA comparison: a small changed price or logo must not
    # disappear through thumbnail averaging or a global similarity threshold.
    if first.size!=second.size:return False
    diff=ImageChops.difference(first.convert('RGBA'),second.convert('RGBA'))
    return all(high<=2 for low,high in diff.getextrema())


def isolate_editable(bridge,target,info,full,job):
    indices=candidates(info)
    if not indices:return info,full
    c=bridge.client;bridge.activate(target);scratch=None
    path=bridge.exchange/('editable-source-'+uuid.uuid4().hex+'.png')
    try:
        c.run('image.duplicate',name='Inspect merged cover',mergedOnly=False)
        scratch=c.run('session.inspect')['active'];rows=c.run('document.inspect')['layers']
        for index in indices:c.run('layer.setProps',layer=rows[index]['id'],visible=False)
        c.call('app.save',path=str(path))
        with Image.open(path) as image:underlying=image.convert('RGBA')
        mean,close=similarity(full,underlying)
        accepted=duplicate_cover(full,underlying)
        (job/'reflow-cover-check.json').write_text(json.dumps({'indices':indices,'mean_difference':mean,'matching_fraction':close,'accepted':accepted}),encoding='utf8')
        if not accepted:return info,full
        filtered=copy.deepcopy(info)
        for index in indices:filtered['layers'][index]['visible']=False
        (job/'reflow-merged-covers.json').write_text(json.dumps(indices),encoding='utf8')
        return filtered,underlying
    finally:
        if scratch is not None:c.run('file.close',document=scratch)
        bridge.activate(target);path.unlink(missing_ok=True)
