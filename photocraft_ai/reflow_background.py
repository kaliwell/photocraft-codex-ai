"""Outpaint isolated raster scenes, retaining original PSD layers as hidden backups."""
import json
import uuid
from PIL import Image, ImageOps, ImageDraw, ImageFilter, ImageChops


def imported_layer(before,after):
    def ids(rows):
        return {row['id'] for row in rows}|{value for row in rows for value in ids(row.get('children',[]))}
    added=ids(after)-ids(before)
    if len(added)!=1:raise ValueError('Background import did not create exactly one layer')
    return added.pop()


def scene_roots(info):
    def editable(row):
        return row['kind'] in ('Type','Shape') or any(editable(c) for c in row.get('children',[]))
    rows=info['layers']
    candidates=[];full=False
    def walk(rows,path=()):
        nonlocal full
        for i,r in enumerate(rows):
            if not r.get('visible',True):continue
            key=path+(i,)
            if r.get('children'):walk(r['children'],key)
            elif not editable(r) and (not path or r['kind'] in ('Fill','Adjustment') or (r.get('bounds') and r['bounds'][2]>=info['width']*.9 and r['bounds'][3]>=info['height']*.9)) and (r['kind']!='Smart Object' or (r.get('bounds') and r['bounds'][2]>=info['width']*.9 and r['bounds'][3]>=info['height']*.9)):
                candidates.append(key)
                b=r.get('bounds')
                full=full or bool(b and b[2]>=info['width']*.9 and b[3]>=info['height']*.9)
    walk(rows)
    return candidates if full else []


def capture_scene(bridge,target,info,job,width,height):
    if info['width']*height==info['height']*width:return
    roots=scene_roots(info)
    if not roots:return
    c=bridge.client;bridge.activate(target);scratch=None
    path=bridge.exchange/('reflow-scene-'+uuid.uuid4().hex+'.png')
    try:
        c.run('image.duplicate',name='Background outpaint source',mergedOnly=False)
        scratch=c.run('session.inspect')['active'];copy=c.run('document.inspect')
        # info may deliberately suppress a stamped cover in this scratch copy.
        for i,row in enumerate(info['layers']):
            if not row.get('visible',True) and copy['layers'][i].get('visible',True):c.run('layer.setProps',layer=copy['layers'][i]['id'],visible=False)
        def hide(rows,path=()):
            for i,row in enumerate(rows):
                key=path+(i,)
                if key in roots:continue
                if any(p[:len(key)]==key for p in roots):hide(row.get('children',[]),key)
                elif row.get('visible',True):c.run('layer.setProps',layer=row['id'],visible=False)
        hide(copy['layers'])
        c.call('app.save',path=str(path))
        with Image.open(path) as image:
            rgba=image.convert('RGBA')
            if all(high-low<=2 for low,high in rgba.getextrema()[:3]) and rgba.getchannel('A').getextrema()==(255,255):return
            rgba.save(job/'reflow-scene.png')
        (job/'reflow-scene-layers.json').write_text(json.dumps(roots),encoding='utf8')
    finally:
        if scratch is not None:c.run('file.close',document=scratch)
        bridge.activate(target);path.unlink(missing_ok=True)


def scene_placement(source_size,size):
    scale=min(size[0]/source_size[0],size[1]/source_size[1])
    fitted=(round(source_size[0]*scale),round(source_size[1]*scale))
    return fitted,((size[0]-fitted[0])//2,(size[1]-fitted[1])//2)


def compose_scene(original,generated,size):
    fitted,xy=scene_placement(original.size,size)
    result=ImageOps.fit(generated.convert('RGBA'),size,method=Image.Resampling.LANCZOS)
    source=original.convert('RGBA').resize(fitted,Image.Resampling.LANCZOS)
    # Blend only the edge, preserving the original product pixels in the interior.
    mask=Image.new('L',fitted,0);d=ImageDraw.Draw(mask)
    margin=min(24,min(fitted)//8)
    d.rectangle((margin,margin,fitted[0]-margin-1,fitted[1]-margin-1),fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(max(1,margin/3)))
    source.putalpha(ImageChops.multiply(source.getchannel('A'),mask))
    result.alpha_composite(source,xy)
    return result


def generate_scene(prepared,backend,cancel,progress):
    job=prepared.job;source=job/'reflow-scene.png'
    if not source.exists():return
    width=prepared.layout_options['width'];height=prepared.layout_options['height']
    task=job/'outpaint';task.mkdir(exist_ok=True)
    with Image.open(source) as original:
        fitted,xy=scene_placement(original.size,(width,height))
        canvas=Image.new('RGBA',(width,height));canvas.paste(original.resize(fitted,Image.Resampling.LANCZOS),xy)
        canvas.save(task/'canvas.png')
    prompt=f'Outpaint the attached product scene to {width}:{height} aspect ratio. Reference 1 is the original clean scene. Reference 2 positions it in the larger canvas: keep the known rectangle x={xy[0]}, y={xy[1]}, width={fitted[0]}, height={fitted[1]} unchanged. Seamlessly extend ONLY the empty surrounding areas with matching background texture, lighting and perspective. No duplicated products, no repeated strips, no seams, no text, no logos, no new objects. Keep every existing product unchanged. Return the entire opaque target canvas.'
    progress('Outpainting PSD background')
    generated=backend.generate(task,prompt,'create',cancel,progress,size=f'{width}x{height}',reference_images=(source,task/'canvas.png'))
    if cancel.is_set():
        from .backend import Cancelled
        raise Cancelled('Cancelled')
    with Image.open(source) as original,Image.open(generated) as image:
        compose_scene(original,image,(width,height)).save(job/'reflow-outpaint.png')
