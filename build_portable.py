"""Assemble the offline Windows x64 runtime without copying user configuration."""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
VERSION = '0.23.0-isolated'
output = ROOT / f'dist/photocraft-codex-ai-{VERSION}-windows-x64-local-node'
output.mkdir(parents=True, exist_ok=False)
python = output / 'python'
python.mkdir()
with zipfile.ZipFile(ROOT / 'runtime/python-3.13.5-embed-amd64.zip') as archive:
    archive.extractall(python)
for pattern in ('pillow-11.3.0-cp313-cp313-win_amd64.whl','numpy-2.2.6-cp313-cp313-win_amd64.whl','opencv_python_headless-4.12.0.88-cp37-abi3-win_amd64.whl'):
    wheel = next((ROOT / 'runtime/portable-downloads').glob(pattern))
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(python / 'Lib/site-packages')
(python / 'python313._pth').write_text('python313.zip\n.\n..\nLib/site-packages\nimport site\n', encoding='utf-8')
for folder in ('photocraft_ai', 'vendor', 'native-source', 'docs'):
    shutil.copytree(ROOT / folder, output / folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
shutil.copytree(ROOT / 'native-0.23', output / 'native-0.23',
                ignore=shutil.ignore_patterns('photocraft.exe', 'photocraft-next.exe'))
build_info = json.loads((output / 'native-0.23/BUILD_INFO.json').read_text())
build_info['version'] = VERSION
staged_executable = build_info.get('executable', 'photocraft.exe')
assert staged_executable in ('photocraft.exe', 'photocraft-next.exe')
shutil.copy2(ROOT / 'native-0.23' / staged_executable, output / 'native-0.23/photocraft.exe')
build_info['executable'] = 'photocraft.exe'
assert build_info['exe_sha256'] == hashlib.sha256((output / 'native-0.23/photocraft.exe').read_bytes()).hexdigest()
assert build_info['photocraft_version'] == '0.23.0'
(output / 'native-0.23/BUILD_INFO.json').write_text(json.dumps(build_info, indent=2), encoding='utf-8')
for name in ('portable_launcher.py', 'cache-status.cmd', 'clean-cache.cmd', 'README.md', 'README.en.md', 'THIRD_PARTY.md', 'VALIDATION.md', 'RELEASE_NOTES.md'):
    shutil.copy2(ROOT / name, output / name)
command = '@echo off\r\nchcp 65001 >nul\r\ncd /d "%~dp0"\r\n"%~dp0python\\python.exe" "%~dp0portable_launcher.py" %*\r\n'
(output / 'start.cmd').write_bytes(command.encode('utf-8'))
(output / 'login.cmd').write_bytes((command.replace('%*', '--login')).encode('utf-8'))
(output / 'proxy-example.json').write_text('{"url":"http://127.0.0.1:10808"}\n', encoding='utf-8')
(output / '使用说明.txt').write_text(
    'Windows x64 本地 Node.js 版\n\n1. 完整解压到可写目录。\n2. 使用电脑现有 Node.js 和 npm 安装的 Codex CLI。\n'
    '如果尚未安装 Codex，运行：npm.cmd install -g @openai/codex\n'
    '3. 双击 start.cmd，首次按提示登录自己的 Codex 账号。\n'
    '4. 打开图片并框选，选区下方即可使用 AI。包内已提供 Python，无需另外安装。\n\n'
    '需要网络及支持内置生图的 Codex 账号。包内不含任何账号登录信息。\n'
    '需要代理时：创建 runtime 文件夹，将 proxy-example.json 复制为 runtime/codex-proxy.json，修改为自己的 HTTP/混合端口。\n'
    '账号登录可随时运行 login.cmd。错误日志在 runtime/launcher.log。\n'
    '生成图片默认 0 羽化；局部修改和移除物体默认 12 像素。\n'
    '右键 AI 结果图层 -> 边缘羽化：选择原选区/圆形/正方形，拖动羽化滑条（0-1000 px）。\n'
    '羽化向选区内部渐变，最外沿完全透明；已有图层重新调整滑条即可应用。\n'
    '生成完成后显示本次总耗时，包含读取选区、生图和导入。\n'
    '新图层使用可编辑蒙版，保存 .pcraft 后保留参数。旧图层已烘焙的软边不能反向恢复。\n', encoding='utf-8-sig')
manifest = {str(p.relative_to(output).as_posix()): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in output.rglob('*') if p.is_file()}
(output / 'FILES-SHA256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
archive_path = ROOT / f'dist/photocraft-codex-ai-{VERSION}-windows-x64-local-node.zip'
with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in output.rglob('*'):
        if path.is_file():
            archive.write(path, path.relative_to(output).as_posix())
with zipfile.ZipFile(archive_path) as archive:
    assert archive.testzip() is None
    assert not any(name.startswith('runtime/') or name.endswith('auth.json') for name in archive.namelist())
    assert not any(name.startswith('tools/') or name.endswith(('codex.exe', 'node.exe')) for name in archive.namelist())
print(archive_path, flush=True)
