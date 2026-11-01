"""Build the modified native editor without replacing the installed PhotoCraft."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
source = ROOT / 'research/photocraft'
if not (source / 'Cargo.toml').is_file():
    raise SystemExit('请先按 native-source/README.md 准备 PhotoCraft 源码。')
subprocess.run(['cargo', 'build', '--locked', '-p', 'photocraft', '-j', '4',
                '--config', str(ROOT / 'native-build.toml')], cwd=source, check=True)
output = ROOT / 'native'
output.mkdir(exist_ok=True)
shutil.copy2(source / 'target/debug/photocraft.exe', output / 'photocraft.exe')
for name in ('LICENSE-MIT', 'LICENSE-APACHE', 'NOTICE', 'ATTRIBUTION.md'):
    shutil.copy2(source / name, output / name)
info = {'version': 'development', 'photocraft_version': '0.18.0',
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip(),
        'profile': 'development',
        'exe_sha256': hashlib.sha256((output / 'photocraft.exe').read_bytes()).hexdigest(),
        'patch_sha256': hashlib.sha256((ROOT / 'native-source/photocraft-codex.patch').read_bytes()).hexdigest()}
(output / 'BUILD_INFO.json').write_text(json.dumps(info, indent=2), encoding='utf-8')
print(output / 'photocraft.exe')
