"""Verify feathered layer import and one-step undo against the real native editor."""
import io
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageChops
from photocraft_ai.__main__ import RUNTIME
from photocraft_ai.bridge import ControlClient, PhotoCraftBridge
from photocraft_ai.service import Service


def main():
    c = ControlClient(17924, RUNTIME / 'control.token')
    bridge = PhotoCraftBridge(c, RUNTIME / 'exchange', RUNTIME)
    previous = bridge.active_image()
    directory = RUNTIME / 'feather-smoke'
    directory.mkdir(exist_ok=True)
    raw = io.BytesIO()
    Image.new('RGBA', (320, 240), (40, 90, 130, 255)).save(raw, format='PNG')
    bridge.new_image_from_pngs([raw.getvalue()], 'Feather smoke fixture', None)
    target = bridge.active_image()
    try:
        c.run('select.rect', x=60, y=50, width=200, height=140)
        service = Service(bridge, directory / 'jobs')
        prepared = service.prepare('fill', 'feather test')
        original = Image.open(prepared.source).convert('RGBA')
        path = prepared.job / 'generated.png'
        Image.new('RGBA', prepared.size, (240, 40, 80, 255)).save(path)
        started = time.perf_counter()
        service.apply(prepared, path)
        applied_seconds = time.perf_counter() - started
        result, selection = bridge._snapshot(target)
        result.save(directory / 'result.png')
        assert result.getpixel((59, 120)) == original.getpixel((59, 120))
        edge = result.getpixel((60, 120))
        assert original.getpixel((60, 120))[0] < edge[0] < 240
        assert result.getpixel((160, 120)) == (240, 40, 80, 255)
        diff = ImageChops.difference(original.convert('RGB'), result.convert('RGB'))
        outside = ImageChops.invert(prepared.mask)
        assert all(ImageChops.multiply(channel, outside).getbbox() is None for channel in diff.split())
        assert selection.tobytes() == prepared.mask.tobytes()
        c.run('edit.undo')
        undone, _ = bridge._snapshot(target)
        assert ImageChops.difference(original.convert('RGB'), undone.convert('RGB')).getbbox() is None
        report = {'passed': True, 'feather_px': prepared.feather_px, 'edge_blended': True,
                  'outside_unchanged': True, 'center_opaque': True, 'selection_preserved': True,
                  'one_step_undo': True, 'apply_seconds': round(applied_seconds, 3)}
        (directory / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report))
    finally:
        bridge.activate(target)
        c.run('file.close', document=target.index)
        if previous:
            bridge.activate(previous)


if __name__ == '__main__':
    main()
