"""Export only the native integration changes, preserving UTF-8 patch bytes."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
source = root / 'research/photocraft-0.23'
subprocess.run(['git', 'add', '-N', '--', 'crates', 'docs', 'apps', 'Cargo.lock'], cwd=source, check=True)
patch = subprocess.check_output(['git', 'diff', '--binary', 'HEAD', '--', 'crates', 'docs', 'apps', 'Cargo.lock'], cwd=source)

destination = root / 'native-source/photocraft-codex.patch'
destination.write_bytes(patch)
print(destination)
