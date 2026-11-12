"""Capture every theme and check embedded controls at two window sizes."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from photocraft_ai.__main__ import RUNTIME
from photocraft_ai.bridge import ControlClient

THEMES = ['pro', 'proMedium', 'proLightGray', 'proLight', 'studio', 'studioLight', 'classic',
          'solarizedDark', 'adwaita', 'adwaitaDark', 'breezeLight', 'breezeDark', 'softDark', 'softLight']


def main():
    c = ControlClient(17924, RUNTIME / 'control.token', timeout=60)
    reports = []
    for width, height in [(1440, 900), (960, 720)]:
        c.call('ui.resize', width=width, height=height)
        for theme in THEMES:
            c.call('ui.set', theme=theme)
            name = f'native-{theme}-{width}.png'
            c.call('ui.screenshot', path=name)
            state = c.call('ui.inspect')
            ai = state['codexAI']
            assert ai['rect'], (theme, width, 'toolbar missing')
            x, y, w, h = ai['rect']
            assert x >= 0 and y >= 0 and x + w <= state['window']['width'] and y + h <= state['window']['height'], (theme, ai)
            for button in ai['buttons']:
                bx, by, bw, bh = button['rect']
                assert x <= bx and y <= by and bx + bw <= x + w + 1 and by + bh <= y + h + 1
            reports.append({'theme': theme, 'size': [width, height], 'rect': ai['rect'], 'screenshot': name})
    c.call('ui.resize', width=1440, height=900)
    c.call('ui.set', theme='proMedium')
    (RUNTIME / 'native-theme-report.json').write_text(json.dumps(reports, indent=2), encoding='utf-8')
    print(f'Passed: {len(reports)} theme/size combinations')


if __name__ == '__main__':
    main()
