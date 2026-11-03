"""Canonical English worker messages; the editor translates them using its live UI language."""
import json
from pathlib import Path
import re

MESSAGES=json.loads(Path(__file__).with_name('messages.json').read_text(encoding='utf-8'))


def english(message):
    if message in MESSAGES:return MESSAGES[message]
    for original,translated in MESSAGES.items():
        if '{' not in original:continue
        parts=re.split(r'\{[^{}]*\}',original)
        match=re.fullmatch('(.*?)'.join(map(re.escape,parts)),message,flags=re.S)
        if match:
            for value in match.groups():translated=translated.replace('{}',english(value),1)
            return translated
    return message
