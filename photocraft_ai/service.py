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


def fit_dimensions(generated: Image.Image, size: tuple[int, int]) -> Image.Image:
    rgba = generated.convert('RGBA')
    if rgba.size != size:
        # Equal aspect ratio: map model pixels to document pixels uniformly.
        ratio_error = abs((rgba.width / rgba.height) / (size[0] / size[1]) - 1)
        if ratio_error > .005:
            raise RuntimeError(f'返回图片尺寸 {rgba.size} 与目标 {size} 宽高比不同，已保留结果，未拉伸或导入。')
        rgba = rgba.resize(size, Image.Resampling.LANCZOS)
    return rgba


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


class Service:
    def __init__(self, bridge: PhotoCraftBridge, root: Path, backend=None):
        self.bridge, self.root = bridge, root
        self.backend = backend or CodexBackend()
        self.lock = threading.Lock()

    def prepare(self, mode: str, prompt: str, size='1024x1024', *, feather_px=12) -> Prepared:
        if mode not in ('create', 'fill', 'remove'):
            raise ValueError('未知模式')
        if mode != 'remove' and not prompt.strip():
            raise ValueError('请输入画面描述。')
        if not isinstance(feather_px, int) or not 0 <= feather_px <= 64:
            raise ValueError('边缘羽化应为 0–64 像素。')
        job = self.root / (datetime.now().strftime('%Y%m%d-%H%M%S-') + uuid.uuid4().hex[:8])
        job.mkdir(parents=True)
        target, revision, mask, source, guide = None, None, None, None, None
        dims = tuple(map(int, size.split('x')))
        if mode != 'create':
            target = self.bridge.active_image()
            if not target:
                raise RuntimeError('请先在配套 PhotoCraft 窗口打开图片。')
            info = target._inspect()
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
        if mode == 'remove':
            prompt = '移除标记区域中的物体，根据周围环境自然补全，保持光照、纹理和透视一致。'
        meta = {'mode': mode, 'prompt': prompt, 'size': dims,
                'document': target.name if target else None, 'revision': revision,
                'feather_px': feather_px if mode != 'create' else 0}
        (job / 'job.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
        return Prepared(job, mode, prompt, target, revision, dims, mask, source, guide, feather_px)

    def generate(self, prepared: Prepared, cancel: threading.Event, progress) -> Path:
        return self.backend.generate(prepared.job, prepared.prompt, prepared.mode, cancel, progress,
                                     prepared.source, prepared.guide, 'x'.join(map(str, prepared.size)))

    def apply(self, prepared: Prepared, path: Path):
        b = self.bridge
        with self.lock:
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
                layer = clipped_layer(image, prepared.mask)
            output = prepared.job / 'layer.png'
            layer.save(output)
            b.insert_results(prepared.target, [output.read_bytes()], Rect(0, 0, *prepared.size),
                             'Codex AI · ' + prepared.prompt[:40], feather=prepared.feather_px,
                             temp_dir=None, use_selection_mask=True, mask_pixels=support.tobytes())
            # No automatic mutation retry: a lost acknowledgement must not insert twice.
            b.commit(prepared.target)
            return prepared.target
