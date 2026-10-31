"""Explicit, live Codex image editing test. Consumes the account's image quota."""
import json
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageChops
from photocraft_ai.__main__ import connect, RUNTIME
from photocraft_ai.service import Service, Prepared


def main():
    b = connect('D:/PhotoCraft/photocraft.exe')
    service = Service(b, RUNTIME / 'live-edit')
    create = service.prepare('create', 'blue ceramic cup')
    b_image = service.apply(create, RUNTIME / 'live-generation/generated.png')
    # A small blank tabletop area, away from the cup, tests a localized insertion.
    b.client.run('select.rect', x=25, y=750, width=230, height=220)
    prepared = service.prepare('fill', '在标记的桌面区域放一颗小草莓，真实摄影，保持杯子和其他画面不变。')
    result = service.generate(prepared, threading.Event(), lambda _: None)
    service.apply(prepared, result)
    output, mask = b._snapshot(prepared.target)
    source = Image.open(prepared.source).convert('RGBA')
    output.save(prepared.job / 'applied.png')
    # Compare RGB channels outside the captured selection; all must remain identical.
    difference = ImageChops.difference(source.convert('RGB'), output.convert('RGB'))
    outside = ImageChops.invert(prepared.mask)
    assert all(ImageChops.multiply(channel, outside).getbbox() is None for channel in difference.split())
    inside = [ImageChops.multiply(channel, prepared.mask).getbbox() for channel in difference.split()]
    assert any(inside), 'The generated selection did not change'
    b.client.call('app.save', path='codex-ai-live-demo.pcraft')
    report = {'passed': True, 'job': str(prepared.job), 'dimensions': list(output.size),
              'outside_unchanged': True, 'inside_changed': True, 'document': prepared.target.name}
    (RUNTIME / 'live-edit-report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
