# 工程数据路径 / Project data paths

已保存的工程使用同目录的专属文件夹。保留工程完整文件名和扩展名，再追加 `.photocraft-data`，避免同名 PSD、PNG、PCraft 混用记录。

```text
设计目录/
├─ 海报.pcraft
└─ 海报.pcraft.photocraft-data/
   ├─ history/
   │  └─ <记录ID>/
   │     ├─ snapshot.json
   │     └─ references/reference-01.png …
   └─ cutting/
      ├─ plan.json
      └─ longpiccutter.json
```

- `history/`：提示词、操作类型、参考图快照。每个工程独立保留最多 50 条和 512 MiB；恢复不新增记录，重复保存去重。
- `cutting/plan.json`：切割线自动保存和恢复。根据工程路径归属，不再按画布像素放入全局目录；相同图片的两个工程也互不影响。尺寸不兼容的方案不会自动应用。
- `cutting/longpiccutter.json`：点击“导出方案”时保存的互通 JSON，不再要求另选目录。PNG ZIP 仍可选择输出位置。
- 未保存工程：提示先保存工程再保留历史；切割线只在本次窗口内存在，仍可手动导出 JSON。
- 切换工程：历史列表跟随当前工程，过期异步结果不会覆盖新工程；切图窗口关闭，重新打开读取该工程方案。
- 另存为：新路径使用新数据目录，旧历史仍属于旧工程，不自动复制。若切图窗口保持打开，当前切割线会随另存为写入新工程目录。
- 移动整个工程：将工程文件与旁边的数据文件夹一起复制。手动改工程文件名时，也将数据文件夹改为相同的新完整文件名加 `.photocraft-data`。
- 旧版 `runtime/native-history/` 和配置目录 `long-cut/` 保留原处，不自动混入工程目录，避免把来源不明的记录归给错误工程。

## English

Saved projects use `<full-project-filename>.photocraft-data/` beside the project file. Keeping the extension separates similarly named PSD, PNG and PCraft projects.

- `history/<id>/snapshot.json` and `references/` hold prompt/reference snapshots. Retention is **per project**: 50 entries / 512 MiB. Restore is read-only and identical snapshots are reused.
- `cutting/plan.json` automatically persists cut lines. Identical canvases in different projects remain isolated; incompatible canvas sizes do not reuse a plan.
- **Export plan** writes `cutting/longpiccutter.json`. PNG ZIP export still asks for its destination.
- Save an untitled project before storing history. Unsaved cutting plans remain in the current window; manual JSON export is available.
- Switching documents changes history scope and discards stale asynchronous history responses. Reopen the cutter to load that project's plan.
- Save As starts a new history scope, retaining the old project's history. An open cutter carries its current lines into the new project's data directory.
- Move the project file and its adjacent data directory together. When renaming the project manually, rename its data directory to match.
- Legacy global history and cutter caches remain untouched; they are not automatically assigned to a project.
