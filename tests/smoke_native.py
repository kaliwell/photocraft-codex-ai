"""Drive the real embedded toolbar. --live consumes a Codex image generation."""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageChops
from photocraft_ai.__main__ import ROOT, RUNTIME
from photocraft_ai.bridge import ControlClient, PhotoCraftBridge


def center(rect):
    x, y, w, h = rect
    return {'x': x + w / 2, 'y': y + h / 2}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    args = parser.parse_args()
    client = ControlClient(17880, RUNTIME / 'control.token', timeout=60)
    bridge = PhotoCraftBridge(client, RUNTIME / 'exchange', RUNTIME)
    bridge.new_image_from_pngs([(ROOT / 'examples/text-to-image.png').read_bytes()], 'Codex AI native demo', None)
    client.run('select.rect', x=60, y=850, width=300, height=240)
    client.call('ui.set', zoom=.5, center=[627, 627])
    state = client.call('ui.inspect')
    toolbar = state['codexAI']
    assert len(toolbar['buttons']) == 3
    before_revision = state['document']['revision']
    client.call('ui.click', **center(toolbar['input']))
    client.call('ui.type', text='在选区内添加一颗小草莓，完整放在区域中央，保持其他画面不变')
    state = client.call('ui.inspect')
    assert state['document']['revision'] == before_revision, 'Toolbar input changed the canvas'
    client.call('ui.screenshot', path='native-toolbar.png')
    report = {'toolbar': state['codexAI'], 'text_input_preserves_document': True, 'live': args.live}
    if args.live:
        source = bridge.active_image()
        original, selection = bridge._snapshot(source)
        original_layers = len(source._inspect()['layers'])
        toolbar = client.call('ui.inspect')['codexAI']
        button = next(b for b in toolbar['buttons'] if b['label'] == '生成图片')
        client.call('ui.click', **center(button['rect']))
        started = time.monotonic()
        busy_seen = False
        while time.monotonic() - started < 1000:
            state = client.call('ui.inspect')
            ai = state['codexAI']
            busy_seen |= ai['busy']
            if ai['error']:
                raise RuntimeError(ai['message'])
            if busy_seen and not ai['busy']:
                break
            time.sleep(1)
        else:
            raise RuntimeError('native generation timeout')
        result, current_selection = bridge._snapshot(source)
        assert len(source._inspect()['layers']) == original_layers + 1
        difference = ImageChops.difference(original.convert('RGB'), result.convert('RGB'))
        outside = ImageChops.invert(selection)
        assert all(ImageChops.multiply(c, outside).getbbox() is None for c in difference.split())
        assert any(ImageChops.multiply(c, selection).getbbox() for c in difference.split())
        assert current_selection.tobytes() == selection.tobytes()
        client.call('app.save', path='codex-ai-native-demo.pcraft')
        source = bridge.active_image()  # Save As changes the document name.
        result.save(RUNTIME / 'native-result.png')
        client.call('ui.screenshot', path='native-toolbar-result.png')
        client.run('edit.undo')
        undone, _ = bridge._snapshot(source)
        assert ImageChops.difference(original.convert('RGB'), undone.convert('RGB')).getbbox() is None
        client.run('edit.redo')
        report.update(live_passed=True, outside_unchanged=True, selection_preserved=True,
                      one_undo_restores_original=True, elapsed=round(time.monotonic() - started, 1))
    filename = 'native-live-report.json' if args.live else 'native-smoke-report.json'
    (RUNTIME / filename).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main()
