"""Build a portable source bundle; never include tokens, logs or runtime jobs."""
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent
destination = root / 'dist/photocraft-codex-ai-0.4.0.zip'
destination.parent.mkdir(exist_ok=True)
files = [root / name for name in ('README.md', 'README.en.md', 'VALIDATION.md', 'THIRD_PARTY.md', 'RELEASE_NOTES.md',
                                 'requirements.txt', 'start.cmd', 'start-native.cmd', 'start-panel.cmd',
                                 'native-build.toml', 'build_native.py', 'export_native_patch.py', 'build_release.py')]
for folder in ('photocraft_ai', 'vendor', 'tests', 'examples', 'native-source'):
    files.extend(p for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files.extend(p for p in (root / 'native-0.20').rglob('*') if p.is_file())
with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(files):
        archive.write(path, path.relative_to(root).as_posix().replace('native-0.20/', 'native/', 1))
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
    assert all(not name.startswith(('runtime/', 'research/')) for name in archive.namelist())
print(destination)
