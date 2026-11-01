"""Export only the native integration changes, preserving UTF-8 patch bytes."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
source = root / 'research/photocraft'
subprocess.run(['git', 'add', '-N', 'crates/ui-egui/src/codex_ai.rs'], cwd=source, check=True)
patch = subprocess.check_output(['git', 'diff', '--binary', 'HEAD', '--',
    'crates/ui-egui/src/codex_ai.rs', 'crates/ui-egui/src/canvas.rs',
    'crates/ui-egui/src/control/inspect.rs', 'crates/ui-egui/src/lib.rs',
    'crates/ui-egui/src/state.rs', 'crates/ui-egui/src/panels/layer_menu_ui.rs',
    'crates/ui-egui/src/panels/layer_menu_ui/tests.rs',
    'crates/engine/src/cmd/layer_mask_props_cmds.rs',
    'crates/engine/src/cmd/layer_mask_props_cmds/tests.rs'], cwd=source)
destination = root / 'native-source/photocraft-codex.patch'
destination.write_bytes(patch)
print(destination)
