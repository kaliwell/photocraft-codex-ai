"""Build the modified native editor without replacing the installed PhotoCraft."""
from pathlib import Path
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
print(output / 'photocraft.exe')
