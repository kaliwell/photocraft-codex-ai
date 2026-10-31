from __future__ import annotations
import argparse
from pathlib import Path
import json
import os
import socket
import subprocess
import time

from .bridge import ControlClient, PhotoCraftBridge

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'runtime'
PORT = 17878


def panel_lock(name='panel.lock'):
    """OS lock is released even after a crash; do not launch two job panels."""
    RUNTIME.mkdir(exist_ok=True)
    handle = (RUNTIME / name).open('a+b')
    handle.seek(0, 2)
    if not handle.tell():
        handle.write(b'0')
        handle.flush()
    handle.seek(0)
    try:
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        (RUNTIME / ('show.request' if name == 'panel.lock' else 'native.show.request')).touch()
        return None
    return handle


def connect(executable: str, port=PORT):
    RUNTIME.mkdir(exist_ok=True)
    exchange = RUNTIME / 'exchange'
    exchange.mkdir(exist_ok=True)
    token = RUNTIME / 'control.token'
    client = ControlClient(port, token, timeout=20)
    with socket.socket() as sock:
        occupied = sock.connect_ex(('127.0.0.1', port)) == 0
    if occupied:
        if not client.alive():
            raise RuntimeError(f'端口 {port} 被其他程序占用，或令牌不匹配。')
    else:
        exe = Path(executable).resolve()
        if not exe.is_file():
            raise RuntimeError(f'未找到 PhotoCraft：{exe}')
        env = {k: v for k, v in os.environ.items() if not k.startswith('PHOTOCRAFT_CONTROL_')
               and not k.startswith('PHOTOCRAFT_AUTOMATION_')}
        args = [str(exe), '--new-instance', '--control', str(port), '--control-token-file', str(token),
                '--automation-read-root', str(exchange), '--automation-write-root', str(exchange)]
        with (RUNTIME / 'photocraft.log').open('ab') as log:
            # The editor window is interactive; only console windows are hidden.
            subprocess.Popen(args, cwd=str(exe.parent), env=env, stdout=log, stderr=log,
                             creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        for _ in range(60):
            time.sleep(.25)
            if client.alive():
                break
        else:
            raise RuntimeError('PhotoCraft 启动失败，请查看 runtime/photocraft.log。')
    bridge = PhotoCraftBridge(client, exchange, RUNTIME)
    (RUNTIME / 'connection.json').write_text(json.dumps({'port': port, 'exchange': str(exchange)}))
    return bridge


def main():
    parser = argparse.ArgumentParser(description='PhotoCraft Codex AI 中文面板')
    parser.add_argument('--photocraft', default=os.environ.get('PHOTOCRAFT_BIN', 'D:/PhotoCraft/photocraft.exe'))
    parser.add_argument('--port', type=int, default=PORT)
    parser.add_argument('--connect-only', action='store_true')
    parser.add_argument('--check-layout', action='store_true')
    args = parser.parse_args()
    singleton = None
    if not args.connect_only and not args.check_layout:
        singleton = panel_lock()
        if singleton is None:
            return
    try:
        bridge = connect(args.photocraft, args.port)
        if args.connect_only:
            print(json.dumps(bridge.session(), ensure_ascii=False))
            return
        from .ui import run
        run(bridge, RUNTIME, check_layout=args.check_layout)
    except Exception as error:
        if args.connect_only or args.check_layout:
            raise
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror('PhotoCraft Codex AI', str(error))
        root.destroy()
    finally:
        if singleton:
            singleton.close()


if __name__ == '__main__':
    main()
