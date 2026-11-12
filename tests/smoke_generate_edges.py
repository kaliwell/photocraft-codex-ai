"""Verify native Generate adds an unfeathered layer without calling image services."""
import io
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageChops
from photocraft_ai.__main__ import RUNTIME
from photocraft_ai.bridge import ControlClient, PhotoCraftBridge
from photocraft_ai.native import NativeWorker
from photocraft_ai.service import Service


class FixtureBackend:
    def generate(self, job, prompt, mode, cancel, progress, source, guide, size):
        result = job / 'generated.png'
        Image.new('RGBA', tuple(map(int, size.split('x'))), (240, 40, 80, 255)).save(result)
        return result


def main():
    client = ControlClient(17924, RUNTIME / 'control.token')
    bridge = PhotoCraftBridge(client, RUNTIME / 'exchange', RUNTIME)
    previous = bridge.active_image()
    raw = io.BytesIO()
    Image.new('RGBA', (320, 240), (40, 90, 130, 255)).save(raw, format='PNG')
    bridge.new_image_from_pngs([raw.getvalue()], 'Generate edge smoke fixture', None)
    target = bridge.active_image()
    try:
        client.run('select.rect', x=60, y=50, width=200, height=140)
        original, mask = bridge._snapshot(target)
        worker = NativeWorker(Service(bridge, RUNTIME / 'generate-edge-smoke/jobs', FixtureBackend()))
        worker._run({'mode': 'generate', 'prompt': 'edge test', 'document':
                     {'index': target.index, 'name': target.name, 'revision': bridge._revision(target)}})
        state = worker.snapshot()
        assert not state['error'], state
        result, selection = bridge._snapshot(target)
        assert result.getpixel((60, 120)) == (240, 40, 80, 255)
        assert result.getpixel((259, 120)) == (240, 40, 80, 255)
        diff = ImageChops.difference(original.convert('RGB'), result.convert('RGB'))
        assert all(ImageChops.multiply(channel, ImageChops.invert(mask)).getbbox() is None for channel in diff.split())
        assert selection.tobytes() == mask.tobytes()
        metadata = json.loads((Path(state['job']) / 'job.json').read_text(encoding='utf-8'))
        assert metadata['feather_px'] == 0
        client.run('edit.undo')
        undone, _ = bridge._snapshot(target)
        assert ImageChops.difference(original.convert('RGB'), undone.convert('RGB')).getbbox() is None
        report = {'passed': True, 'feather_px': 0, 'edges_opaque': True,
                  'outside_unchanged': True, 'selection_preserved': True, 'one_step_undo': True}
        (RUNTIME / 'generate-edge-smoke/report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps(report))
    finally:
        bridge.activate(target)
        client.run('file.close', document=target.index)
        if previous:
            bridge.activate(previous)


if __name__ == '__main__':
    main()
