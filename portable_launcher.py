"""First-run sign-in and launch for the self-contained Windows distribution."""
from pathlib import Path
import json
import os
import subprocess
import sys

from photocraft_ai.backend import codex_command, codex_environment

ROOT = Path(__file__).resolve().parent


def main():
    os.chdir(ROOT)
    if '--cache-status' in sys.argv or '--clean-cache' in sys.argv:
        from photocraft_ai.cache import maintain
        # Status is read-only; cleaning only handles completed tracked jobs.
        print(json.dumps(maintain(ROOT/'runtime',force='--clean-cache' in sys.argv,dry_run='--clean-cache' not in sys.argv)))
        return
    env, _ = codex_environment()
    flags = subprocess.CREATE_NO_WINDOW
    status = subprocess.run(codex_command() + ['login', 'status'], env=env, capture_output=True,
                            creationflags=flags)
    if '--check' in sys.argv:
        from PIL import Image
        from photocraft_ai.native import NativeWorker
        print(json.dumps({'python': sys.version.split()[0], 'pillow': Image.__version__,
                          'codex': subprocess.check_output(codex_command() + ['--version'], env=env,
                                                          creationflags=flags, text=True).strip(),
                          'logged_in': status.returncode == 0}))
        return
    if '--login' in sys.argv or status.returncode:
        print('请在浏览器中登录你自己的 Codex / ChatGPT 账号。', flush=True)
        result = subprocess.run(codex_command() + ['login'], env=env)
        if result.returncode:
            raise RuntimeError('登录未完成。请检查网络；需要代理时先编辑 runtime/codex-proxy.json。')
        if '--login' in sys.argv:
            return
    (ROOT / 'runtime').mkdir(exist_ok=True)
    with (ROOT / 'runtime/launcher.log').open('ab') as log:
        subprocess.Popen([str(ROOT / 'python/pythonw.exe'), '-m', 'photocraft_ai.native'], cwd=ROOT,
                         env=env, stdout=log, stderr=log, creationflags=flags)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error), file=sys.stderr)
        if '--check' not in sys.argv:
            input('按回车关闭…')
        sys.exit(1)
