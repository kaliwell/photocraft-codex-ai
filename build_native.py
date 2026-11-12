"""Build the modified native editor without replacing the installed PhotoCraft."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tomllib
import os

ROOT = Path(__file__).resolve().parent
source = ROOT / 'research/photocraft-0.23'
target = ROOT / 'target-native-023'
if not (source / 'Cargo.toml').is_file():
    raise SystemExit('请先按 native-source/README.md 准备 PhotoCraft 源码。')
env = {**os.environ, 'CRAFT_I18N_DIR': str(ROOT/'research/craft-i18n'), 'CRAFT_I18N_REQUIRED': '1'}
subprocess.run(['cargo', 'build', '--locked', '-p', 'photocraft', '-j', '4',
                '--config', str(ROOT / 'native-build.toml'), '--target-dir', str(target)], cwd=source, env=env, check=True)
output = ROOT / 'native-0.23'
output.mkdir(exist_ok=True)
binary = output / 'photocraft.exe'
try:
    shutil.copy2(target / 'debug/photocraft.exe', binary)
except PermissionError:
    # Windows locks a running executable. Stage the update for the next launch.
    binary = output / 'photocraft-next.exe'
    shutil.copy2(target / 'debug/photocraft.exe', binary)
for name in ('LICENSE-MIT', 'LICENSE-APACHE', 'NOTICE', 'ATTRIBUTION.md'):
    shutil.copy2(source / name, output / name)
info = {'version': 'development', 'photocraft_version': tomllib.loads((source / 'Cargo.toml').read_text(encoding='utf-8'))['workspace']['package']['version'],
        'source_commit': '9963efcb2f04867b56c564f876befd412b6c3c4e',
        'source_checkout_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=source, text=True).strip(),
        'profile': 'development',
        'executable': binary.name,
        'exe_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
        'patch_sha256': hashlib.sha256((ROOT / 'native-source/photocraft-codex.patch').read_bytes()).hexdigest()}
(output / 'BUILD_INFO.json').write_text(json.dumps(info, indent=2), encoding='utf-8')
print(binary)
