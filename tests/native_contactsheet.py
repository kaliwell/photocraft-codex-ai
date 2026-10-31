"""QA contact sheet of native UI screenshots; not a generated-image asset."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageDraw
from photocraft_ai.__main__ import RUNTIME

rows = json.loads((RUNTIME / 'native-theme-report.json').read_text())
for width in (1440, 960):
    subset = [row for row in rows if row['size'][0] == width]
    sheet = Image.new('RGB', (1440, 1020), 'white')
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(subset):
        x, y = (index % 4) * 360, (index // 4) * 255
        draw.text((x + 5, y + 4), row['theme'], fill='black')
        with Image.open(RUNTIME / 'exchange' / row['screenshot']) as shot:
            shot.thumbnail((356, 229))
            sheet.paste(shot, (x + 2, y + 22))
    output = RUNTIME / f'native-themes-{width}.jpg'
    sheet.save(output, quality=90)
    print(output)
