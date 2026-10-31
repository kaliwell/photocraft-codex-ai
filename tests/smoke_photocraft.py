"""Actual editor test; synthetic pixels test transport, not AI quality."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageChops
from photocraft_ai.__main__ import connect, RUNTIME
from photocraft_ai.service import Service


def main():
    b = connect('D:/PhotoCraft/photocraft.exe')
    folder = RUNTIME / 'smoke'
    folder.mkdir(exist_ok=True)
    b.new_image_from_pngs([fixture()], 'Codex AI transport test', None)
    original = b.active_image()
    info = original._inspect()
    b.client.run('select.rect', x=80, y=60, width=100, height=90)
    service = Service(b, folder / 'jobs')
    prepared = service.prepare('fill', 'test selection clipping')
    source = Image.open(prepared.source).convert('RGBA')
    candidate = prepared.job / 'generated.png'
    Image.new('RGBA', prepared.size, (240, 40, 80, 255)).save(candidate)
    before = original._inspect()
    service.apply(prepared, candidate)
    after = original._inspect()
    output, selection = b._snapshot(original)
    output.save(folder / 'after.png')
    source.save(folder / 'before.png')
    assert output.getpixel((10, 10)) == source.getpixel((10, 10)), 'outside selection changed'
    assert output.getpixel((100, 80))[:3] == (240, 40, 80), 'inside selection not updated'
    assert selection is not None and selection.tobytes() == prepared.mask.tobytes(), 'selection changed'
    b.client.run('edit.undo')
    undone, _ = b._snapshot(original)
    undone.save(folder / 'undone.png')
    assert ImageChops.difference(undone.convert('RGB'), source.convert('RGB')).getbbox() is None, 'undo failed'
    report = {'passed': True, 'size': list(prepared.size), 'before': before, 'after': after,
              'checks': ['snapshot + selection', 'new layer', 'outside pixels preserved', 'selection preserved', 'single undo']}
    (folder / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


def fixture():
    import io
    image = Image.new('RGBA', (320, 240), (40, 90, 130, 255))
    data = io.BytesIO()
    image.save(data, format='PNG')
    return data.getvalue()


if __name__ == '__main__':
    main()
