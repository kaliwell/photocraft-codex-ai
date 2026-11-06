from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import threading
import uuid
from datetime import datetime

from PIL import Image, ImageChops, ImageFilter, ImageOps

from .backend import CodexBackend, Cancelled
from .bridge import PhotoCraftBridge, Rect
from .references import save_references


@dataclass
class Prepared:
    job: Path
    mode: str
    prompt: str
    target: object
    revision: int | None
    size: tuple[int, int]
    mask: Image.Image | None
    source: Path | None
    guide: Path | None
    feather_px: int = 12
    references: tuple[Path, ...] = ()
    active_layer: int | None = None
    layout_options: dict | None = None


def fit_dimensions(generated: Image.Image, size: tuple[int, int], *, adapt=False) -> Image.Image:
    rgba = generated.convert('RGBA')
    if rgba.size != size:
        # Equal aspect ratio: map model pixels to document pixels uniformly.
        ratio_error = abs((rgba.width / rgba.height) / (size[0] / size[1]) - 1)
        if ratio_error > .005 and not adapt:
            raise RuntimeError(f'返回图片尺寸 {rgba.size} 与目标 {size} 宽高比不同，已保留结果，未拉伸或导入。')
        rgba = rgba.resize(size, Image.Resampling.LANCZOS)
    return rgba


def edit_reference(full: Image.Image, mask: Image.Image):
    """Letterbox the complete canvas into a bounded square, retaining its coordinate map."""
    fitted = ImageOps.contain(full.convert('RGBA'), (1024, 1024), Image.Resampling.LANCZOS)
    x, y = (1024-fitted.width)//2, (1024-fitted.height)//2
    square = Image.new('RGBA', (1024,1024))
    square.paste(fitted,(x,y))
    selection = Image.new('L',(1024,1024))
    selection.paste(mask.resize(fitted.size,Image.Resampling.LANCZOS),(x,y))
    return square, selection, (x,y,x+fitted.width,y+fitted.height)


def edited_layer(image: Image.Image, mask: Image.Image, job: Path) -> Image.Image:
    transform = job/'edit-transform.json'
    if transform.is_file():
        mapping=json.loads(transform.read_text(encoding='utf-8'))
        box=tuple(mapping['content_box'])
        if len(box)!=4 or not (0<=box[0]<box[2]<=1024 and 0<=box[1]<box[3]<=1024):
            raise RuntimeError('编辑坐标映射无效。')
        aligned=fit_dimensions(image,(1024,1024),adapt=True).crop(box).resize(mask.size,Image.Resampling.LANCZOS)
    else:
        # Retained jobs from older versions used the full canvas directly.
        aligned=fit_dimensions(image,mask.size,adapt=True)
    return clipped_layer(aligned,mask)


def inward_feather(mask: Image.Image, radius: int) -> Image.Image:
    """Smooth alpha falloff inside the selection, including holes and canvas edges.

    A bounded erosion distance avoids Gaussian tails outside the original selection.
    Normalize very small selections to their actual depth so they do not disappear.
    """
    mask = mask.convert('L')
    radius = max(0, min(64, int(radius)))
    bounds = mask.getbbox()
    if not radius or bounds is None:
        return mask.copy()
    support = mask.crop(bounds).point([0] + [255] * 255)
    support = ImageOps.expand(support, border=1, fill=0)
    distance = Image.new('L', support.size, 0)
    count = 0
    for count in range(1, radius + 1):
        distance = ImageChops.add(distance, support.point([0] + [1] * 255))
        support = support.filter(ImageFilter.MinFilter(3))
        if support.getbbox() is None:
            break
    # Smoothstep gives a gradual join and a fully opaque interior. Original feathered
    # coverage remains an upper bound: no pixel outside the selection is introduced.
    def coverage(value):
        t = min(1.0, value / count)
        return round(255 * t * t * (3 - 2 * t))
    ramp = distance.point([coverage(value) for value in range(256)])
    ramp = ramp.crop((1, 1, ramp.width - 1, ramp.height - 1))
    result = Image.new('L', mask.size, 0)
    result.paste(ramp, bounds[:2])
    return ImageChops.multiply(mask, result)


def clipped_layer(generated: Image.Image, mask: Image.Image, feather_px: int = 0) -> Image.Image:
    rgba = fit_dimensions(generated, mask.size)
    rgba.putalpha(ImageChops.multiply(rgba.getchannel('A'), inward_feather(mask, feather_px)))
    return rgba


def generated_layer(generated: Image.Image, mask: Image.Image) -> Image.Image:
    """Place new artwork proportionally inside the selection, without cropping or stretching."""
    bounds = mask.getbbox()
    if bounds is None:
        raise RuntimeError('选区为空。')
    left, top, right, bottom = bounds
    fitted = ImageOps.contain(generated.convert('RGBA'), (right-left, bottom-top), Image.Resampling.LANCZOS)
    layer = Image.new('RGBA', mask.size)
    layer.paste(fitted, (left+(right-left-fitted.width)//2, top+(bottom-top-fitted.height)//2))
    layer.putalpha(ImageChops.multiply(layer.getchannel('A'), mask))
    return layer


class Service:
    def __init__(self, bridge: PhotoCraftBridge, root: Path, backend=None):
        self.bridge, self.root = bridge, root
        self.backend = backend or CodexBackend()
        self.lock = threading.Lock()

    def prepare(self, mode: str, prompt: str, size='1024x1024', *, feather_px=12, references=None, layout_options=None) -> Prepared:
        if mode in ('layout','detail','batch','reflow'):
            from .layout import validate_options
            layout_options=validate_options(layout_options)
            if mode=='reflow':layout_options={**layout_options,'destination':'new','source':'references','reference_size':False}
            if mode=='batch':layout_options={**layout_options,'source':'references','destination':'new'}
            if mode=='detail':layout_options['reference_size']=True
        if mode not in ('create', 'fill', 'remove', 'generate', 'layout', 'detail', 'batch', 'reflow'):
            raise ValueError('未知模式')
        if mode not in ('remove','layout','detail','batch','reflow') and not prompt.strip():
            raise ValueError('请输入画面描述。')
        if not isinstance(feather_px, int) or not 0 <= feather_px <= 64:
            raise ValueError('边缘羽化应为 0–64 像素。')
        job = self.root / (datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8])
        job.mkdir(parents=True)
        if mode in ('layout','detail','batch','reflow') and layout_options['source']=='layers':
            from .layout_source import selected_layer_reference
            references=selected_layer_reference(self.bridge)
        reference_paths,reference_names=save_references([] if references is None else references,job)
        if mode in ('layout','detail','batch') and not reference_paths:raise ValueError('Add a reference image first')
        target, revision, mask, source, guide = None, None, None, None, None
        active_layer = None
        dims = tuple(map(int, size.split('x')))
        if mode=='reflow':
            target=self.bridge.active_image()
            if target is None:raise ValueError('Open a PSD before adapting its ratio')
            info=target._inspect()
            from .reflow import content_units,validate_workspace
            validate_workspace(info,layout_options['width'],layout_options['height'])
            content_units(info)
            revision=self.bridge._revision(target)
            full,_=self.bridge._snapshot(target)
            source=job/'reflow-source.png';full.save(source)
            (job/'reflow-source.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf8')
        if mode in ('layout','detail','batch','reflow') and layout_options['destination']=='current':
            target=self.bridge.active_image()
            if not target:raise ValueError('Open a document before creating the layout')
            info=target._inspect()
            revision=self.bridge._revision(target)
            dims=(info['width'],info['height'])
            layout_options=validate_options({**layout_options,'reference_size':False,'width':dims[0],'height':dims[1],'dpi':round(info.get('resolution',72))})
        if mode not in ('create','layout','detail','batch','reflow'):
            target = self.bridge.active_image()
            if not target:
                raise RuntimeError('请先在配套 PhotoCraft 窗口打开图片。')
            info = target._inspect()
            if info.get('selectedLayers'):
                active_layer = info.get('activeLayer')
            if not info.get('hasSelection'):
                raise RuntimeError('请先使用框选或套索选择要修改的区域。')
            full, mask = self.bridge._snapshot(target)
            if mask is None or not mask.getbbox():
                raise RuntimeError('选区为空。')
            dims = full.size
            source, guide = job / 'source.png', job / 'guide.png'
            full.save(source)
            mask.save(job / 'selection.png')
            overlay = Image.new('RGBA', dims, (255, 0, 180, 0))
            overlay.putalpha(mask.point(lambda p: round(p * .55)))
            Image.alpha_composite(full, overlay).save(guide)
            revision = self.bridge._revision(target)
            if mode == 'generate':
                source, guide = None, None
            elif mode in ('fill', 'remove'):
                square, selection, box = edit_reference(full,mask)
                square.save(source)
                selection.save(job/'selection-guide.png')
                overlay=Image.new('RGBA',square.size,(255,0,180,0))
                overlay.putalpha(selection.point(lambda p:round(p*.55)))
                Image.alpha_composite(square,overlay).save(guide)
                (job/'edit-transform.json').write_text(json.dumps({'content_box':box,'canvas_size':dims}),encoding='utf-8')
        if mode == 'remove':
            prompt = 'Remove the marked object and fill the area naturally, preserving surrounding light, texture and perspective.'
        meta = {'mode': mode, 'prompt': prompt, 'size': dims,
                'document': target.name if target else None, 'revision': revision,
                'feather_px': feather_px if mode != 'create' else 0,
                'generation_size': '1024x1024' if mode in ('generate','fill','remove') else dims,
                'references':reference_names}
        (job / 'job.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
        return Prepared(job, mode, prompt, target, revision, dims, mask, source, guide, feather_px,reference_paths,active_layer,layout_options)

    def generate(self, prepared: Prepared, cancel: threading.Event, progress) -> Path:
        if prepared.mode=='reflow':
            from .reflow import analyze_reflow
            return analyze_reflow(prepared,cancel,progress)
        if prepared.mode in ('layout','detail','batch','reflow'):
            from .layout import generate_layout
            return generate_layout(prepared.job,prepared.references,prepared.prompt,cancel,progress,prepared.layout_options,**({'long_page':True} if prepared.mode=='detail' else {}))
        return self.backend.generate(prepared.job, prepared.prompt, prepared.mode, cancel, progress,
                                     prepared.source, prepared.guide,
                                     '1024x1024' if prepared.mode in ('generate','fill','remove') else 'x'.join(map(str, prepared.size)),
                                     **({'reference_images':prepared.references} if prepared.references else {}))

    def apply(self, prepared: Prepared, path: Path):
        b = self.bridge
        with self.lock:
            if prepared.mode=='reflow':
                from .reflow import apply_reflow
                return apply_reflow(b,prepared,path)
            if prepared.mode in ('layout','detail','batch','reflow'):
                from .layout import build_layout
                current=(prepared.layout_options or {}).get('destination')=='current'
                if current:
                    docs=b.documents()
                    match=next((d for d in docs if d['index']==prepared.target.index and d['name']==prepared.target.name),None)
                    if not match or int(match.get('revision',0))!=prepared.revision:
                        raise RuntimeError('Current document changed; layout result retained')
                    b.activate(prepared.target)
                return build_layout(b,path,prepared.job,current=current)
            with Image.open(path) as image:
                image.load()
                if prepared.mode == 'create':
                    output = prepared.job / 'document.png'
                    fit_dimensions(image, prepared.size).save(output)
                    return b.new_image_from_pngs([output.read_bytes()], 'Codex AI ' + prepared.job.name, None)
                # Refuse stale targets: tab index AND name, revision and dimensions must match.
                docs = b.documents()
                match = next((d for d in docs if d['index'] == prepared.target.index and
                              d['name'] == prepared.target.name), None)
                if not match or int(match.get('revision', 0)) != prepared.revision:
                    raise RuntimeError('原文档已改变或关闭。结果已保存，未导入；请撤销改动后重试，或手动导入。')
                # Original coverage stays in alpha; a separate native mask provides editable
                # feather. Hard support guarantees the selection's exterior stays untouched.
                support = prepared.mask.point([0] + [255] * 255)
                prepared.mask.save(prepared.job / 'blend-mask.png')
                layer = generated_layer(image, prepared.mask) if prepared.mode == 'generate' else edited_layer(image, prepared.mask,prepared.job)
            output = prepared.job / 'layer.png'
            layer.save(output)
            b.insert_results(prepared.target, [output.read_bytes()], Rect(0, 0, *prepared.size),
                             'Codex AI · ' + prepared.prompt[:40], feather=prepared.feather_px,
                             temp_dir=None, use_selection_mask=True, mask_pixels=support.tobytes())
            # No automatic mutation retry: a lost acknowledgement must not insert twice.
            b.commit_above(prepared.target, prepared.active_layer)
            return prepared.target
