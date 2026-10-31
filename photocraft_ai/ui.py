from pathlib import Path
import os
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageTk
from .backend import Cancelled
from .service import Service


def run(bridge, runtime: Path, check_layout=False):
    root = tk.Tk()
    root.title('PhotoCraft · Codex AI')
    root.geometry('430x760')
    root.minsize(390, 680)
    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TFrame', background='#202228')
    style.configure('TLabel', background='#202228', foreground='#eceef4', font=('Microsoft YaHei UI', 10))
    style.configure('Title.TLabel', font=('Microsoft YaHei UI', 19, 'bold'))
    style.configure('TButton', font=('Microsoft YaHei UI', 10), padding=8)
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='Codex AI', style='Title.TLabel').pack(anchor='w')
    ttk.Label(frame, text='生成画面，或修改你选中的区域').pack(anchor='w', pady=(3, 16))
    modes = {'文生图 · 新文档': 'create', '局部修改 · 选区': 'fill', '移除物体 · 选区': 'remove'}
    mode = ttk.Combobox(frame, values=list(modes), state='readonly')
    mode.current(0)
    mode.pack(fill='x')
    ttk.Label(frame, text='画面描述').pack(anchor='w', pady=(16, 6))
    prompt = tk.Text(frame, height=5, bg='#2c2f37', fg='#f4f5f8', insertbackground='white',
                     relief='flat', wrap='word', font=('Microsoft YaHei UI', 11), padx=10, pady=10)
    prompt.pack(fill='x')
    row = ttk.Frame(frame)
    row.pack(fill='x', pady=12)
    ttk.Label(row, text='生图尺寸').pack(side='left')
    size = ttk.Combobox(row, width=14, values=['1024x1024', '1536x1024', '1024x1536'], state='readonly')
    size.current(0)
    size.pack(side='right')
    ttk.Label(frame, text='局部修改请先在配套编辑器中框选或套索选区。\n沿用本机 Codex 登录；图片会发送至生成服务。',
              wraplength=380).pack(anchor='w', pady=(0, 12))
    buttons = ttk.Frame(frame)
    buttons.pack(fill='x')
    generate = ttk.Button(buttons, text='开始生成')
    generate.pack(side='left', fill='x', expand=True)
    cancel_button = ttk.Button(buttons, text='取消', state='disabled')
    cancel_button.pack(side='left', padx=(8, 0))
    status = tk.StringVar(value='就绪 · 使用新打开的配套 PhotoCraft 窗口')
    ttk.Label(frame, textvariable=status, wraplength=380).pack(anchor='w', pady=12)
    preview = ttk.Label(frame, text='生成后在这里预览', anchor='center')
    preview.pack(fill='both', expand=True, pady=8)
    apply_button = ttk.Button(frame, text='采用结果', state='disabled')
    apply_button.pack(fill='x')
    ttk.Button(frame, text='打开任务与图片目录', command=lambda: os.startfile(str(runtime / 'jobs'))).pack(fill='x', pady=(8, 0))
    (runtime / 'jobs').mkdir(exist_ok=True)
    service = Service(bridge, runtime / 'jobs')
    events = queue.Queue()
    cancel = threading.Event()
    state = {'prepared': None, 'result': None, 'busy': False}
    stopped = threading.Event()

    def watch_menu():
        from openfill_photocraft.menu import install, Watcher
        try:
            with service.lock:
                installed = install(bridge.client)
            watcher = Watcher(bridge.client, lambda _: events.put(('raise', None)))
            while not stopped.wait(1):
                request = runtime / 'show.request'
                if request.exists():
                    request.unlink(missing_ok=True)
                    events.put(('raise', None))
                if installed and not state['busy']:
                    with service.lock:
                        watcher.poll()
        except Exception:
            # Older PhotoCraft builds may not have the filter ABI; the panel still works.
            return

    def worker(mode_value, text, dimensions):
        try:
            events.put(('status', '正在读取文档与选区…'))
            with service.lock:
                prepared = service.prepare(mode_value, text, dimensions)
            # Throttle UI status events to once per second.
            previous = [None]
            def progress(text):
                if text != previous[0]:
                    previous[0] = text
                    events.put(('status', text))
            result = service.generate(prepared, cancel, progress)
            events.put(('ready', (prepared, result)))
        except Cancelled as error:
            events.put(('cancelled', str(error)))
        except Exception as error:
            events.put(('error', str(error)))

    def start():
        if state['busy']:
            return
        state.update(prepared=None, result=None, busy=True)
        cancel.clear()
        generate.configure(state='disabled')
        apply_button.configure(state='disabled')
        cancel_button.configure(state='normal')
        threading.Thread(target=worker, args=(modes[mode.get()], prompt.get('1.0', 'end').strip(), size.get()), daemon=True).start()

    def apply_worker():
        try:
            service.apply(state['prepared'], state['result'])
            events.put(('applied', '结果已导入 PhotoCraft；局部修改可用 Ctrl+Z 撤销。'))
        except Exception as error:
            events.put(('error', str(error)))

    def apply():
        if not state['result'] or state['busy']:
            return
        state['busy'] = True
        generate.configure(state='disabled')
        apply_button.configure(state='disabled')
        status.set('正在导入 PhotoCraft…')
        threading.Thread(target=apply_worker, daemon=True).start()

    def poll():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == 'raise':
                    root.deiconify()
                    root.lift()
                    root.focus_force()
                    continue
                if kind == 'status':
                    status.set(value)
                    continue
                state['busy'] = False
                generate.configure(state='normal')
                cancel_button.configure(state='disabled')
                if kind == 'ready':
                    state['prepared'], state['result'] = value
                    with Image.open(state['result']) as image:
                        image.thumbnail((370, 250))
                        photo = ImageTk.PhotoImage(image.copy())
                    preview.configure(image=photo, text='')
                    preview.image = photo
                    apply_button.configure(text='在 PhotoCraft 新建文档' if value[0].mode == 'create' else '作为新图层导入', state='normal')
                    status.set('生成完成 · 采用后导入 PhotoCraft')
                elif kind == 'error':
                    status.set(value)
                    messagebox.showerror('操作未完成', value)
                else:
                    status.set(value)
        except queue.Empty:
            pass
        root.after(100, poll)

    def close():
        if state['busy']:
            messagebox.showinfo('任务运行中', '请先取消生成，等待任务停止后关闭。')
            return
        stopped.set()
        bridge.client.close()
        root.destroy()

    generate.configure(command=start)
    cancel_button.configure(command=cancel.set)
    apply_button.configure(command=apply)
    root.protocol('WM_DELETE_WINDOW', close)
    if check_layout:
        import json
        root.update()
        root.update_idletasks()
        widgets = [mode, prompt, size, generate, cancel_button, preview, apply_button]
        report = {'window': [root.winfo_width(), root.winfo_height()], 'widgets': []}
        for widget in widgets:
            x = widget.winfo_rootx() - root.winfo_rootx()
            y = widget.winfo_rooty() - root.winfo_rooty()
            w, h = widget.winfo_width(), widget.winfo_height()
            report['widgets'].append({'kind': widget.winfo_class(), 'bounds': [x, y, w, h]})
        (runtime / 'ui-layout-report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        root.destroy()
        for item in report['widgets']:
            x, y, w, h = item['bounds']
            assert x >= 0 and y >= 0 and w > 1 and h > 1, item
            assert x + w <= report['window'][0] and y + h <= report['window'][1], item
        return
    poll()
    threading.Thread(target=watch_menu, daemon=True).start()
    root.mainloop()
