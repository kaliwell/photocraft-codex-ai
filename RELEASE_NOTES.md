# Unreleased / 统一开发版新增

- 参考图、缩略图、粘贴、历史和草稿回归生图主栏。PSD 侧栏紧贴主栏并跟随位置变化，空间不足时换边，不再固定到画布右端。
- Keep references, thumbnails, paste, history and drafts with generation in the main composer. The PSD drawer attaches beside the composer and follows its position, changing sides when space is limited.

- 浮动栏精简为提示词与常用 AI 操作，PSD、参考图和历史移至可展开的右侧工具栏，支持关闭、滚动、拖入和粘贴参考图。
- Compact composer with prompt and common AI actions; PSD, references and history move to a collapsible right-side tools drawer with scrolling, image drops and clipboard paste.

- PSD 底稿来源支持参考图或选中图层（可多选），独立于当前/新建文件选项。图层快照通过透明临时文档读取，不修改源图层；历史保留当时快照。
- PSD source switch supports attached references or selected layers, independently of destination. Layer snapshots use a transparent scratch document without altering source layers; history retains the captured snapshot.

- AI 工具栏按 AI 编辑、PSD 底稿、参考图与历史分区，PSD 设置与制作按钮同行；按钮支持换行。长图参考缩略图显示顶部裁切预览，保存成功提示简化，悬停可查看完整路径。
- Group the composer into AI editing, PSD base layouts, and References and history. PSD settings stays with layout actions, with wrapping controls. Long references show a readable top crop; saved-layout status is concise with the complete path on hover.

- 新增“详情页优化底稿”：分段读取完整长图，重建可编辑文案、底色、形状与边框，排除产品与背景照片；支持最长 30000 像素及当前/新建文件模式。
- Add Detail page base: read full long pages through numbered crops and reconstruct editable text, colors, shapes and borders without product/background photos. Supports height up to 30000 pixels and current/new destinations.

- PSD 制作位置支持“当前文件 / 新建文件”切换。当前文件沿用画布尺寸和 DPI，在顶部添加底稿，保留原图层与工程路径，由用户保存；生成期间工程改变则停止导入。
- PSD destination switch: current or new document. Current mode preserves canvas dimensions, DPI, existing layers and project path, adding the base layout on top without automatic saving. Changed targets are rejected before import.

- 修复 PSD 底稿因模型返回 `font_style` 而被拒绝：兼容转换为引擎使用的 `fontStyle`，不改变用户选定样式。未知字段仍拒绝，并显示具体字段；相关错误补充中文翻译。
- Fix PSD layouts rejected when model text uses `font_style`: normalize it to engine `fontStyle` while preserving the chosen style. Unknown fields remain rejected with specific diagnostics; Chinese error translations added.

- PSD 字体改用文字工具的字体家族与样式选择器，支持搜索、预览、最近使用和收藏；生成时强制使用选定字体和样式，首次沿用文字工具当前设置。
- PSD fonts now use the Type tool's family/style picker with search, previews, recents and favorites. Generated text uses the selected family and style; initial values follow the current Type tool settings.

- 参考图转 PSD 新增参数设置：像素宽高、宽高比快捷键、DPI 与字体名称；不同比例按目标尺寸重新排版，历史/草稿包含参数。默认保持参考图尺寸与 72 DPI。
- Reference-to-PSD settings: target pixel dimensions, ratio shortcuts, DPI and font family, with recomposition for the target canvas and parameters saved in history/drafts. Defaults retain the reference dimensions at 72 DPI.

- Generated layers follow the selected layer; no selection falls back to the top.
- Reference-to-PSD reconstructs editable text and vector base layouts without product or background photos.

- Project-scoped storage: history and cutter JSON live beside each saved project under `<filename>.photocraft-data/`. See [path rules](docs/project-data.md).

- 提示词与参考图历史：自动记录生成输入、保存草稿、恢复不新增记录，相同内容去重；仅恢复输入区，跨重启保留，最近 50 条且合计最多 512 MiB。
- 剪贴板参考图：按钮或提示词中 Ctrl+V 追加图片，兼容 Windows DIB/DIBV5，保留文字与画布粘贴。
- Prompt/reference history with draft saving and restore, read-only rollback and duplicate snapshot reuse; local persistence with 50-entry / 512 MiB retention. Clipboard references support Windows DIB/DIBV5 while preserving text/canvas paste.

These features are newer than the published v0.4.0 ZIP. / 这些功能尚不在已发布的 v0.4.0 ZIP 中。

# PhotoCraft Codex AI v0.4.0 · PhotoCraft 0.20.1

## 中文

- 在原 Codex AI 插件中加入多图参考：多选或拖入图片，显示编号缩略图并支持逐张移除，随本次生成请求传递实际图片附件。使用原来的 `start.cmd` 启动。

- 修复局部修改羽化边缘仍有硬截断的问题：向选区内部平滑渐隐，最外沿完全透明。支持原选区、居中圆形和正方形蒙版，保留 0–1000 px 滑条、撤销/重做和 `.pcraft` 保存。已有图层重新调整羽化滑条即可应用。
- 生成成功后显示本次总耗时，包含读取选区、生图和导入新图层。
- 改进 Windows 运行中更新的二进制暂存与安装包构建，保证包内使用最新编辑器。

下载 `photocraft-codex-ai-0.4.0-windows-x64-local-node.zip`，完整解压后运行 `start.cmd`。更新前保存文档并关闭旧版，建议解压到新文件夹；需要代理时复制自己的 `runtime/codex-proxy.json`。

包内包含 PhotoCraft 0.20.1、Python 3.13.5 和 Pillow 11.3.0；沿用电脑已有 Node.js、npm 安装的 Codex CLI 和自己的登录，不额外打包 Node.js/Codex，也不包含账号凭据。

专项、实机、静态、wasm 和异常输入检查通过。全套回归并非全部通过：开发配置下现有深嵌套小栈问题、Windows 基准构建执行权限和外部测试素材下载限制详见 `VALIDATION.md`。仍为预览开发构建，需要网络和支持内置生图的 Codex 账号。

## English

- Adds multi-image references to the original Codex AI plugin: select or drop images, inspect numbered thumbnails, remove individual references and send actual image attachments with generation requests. Launch with the original `start.cmd`.

Upgrades the matching editor to upstream PhotoCraft 0.20.1, retaining the AI toolbar, inward feathering and generation timing.

- Fixes sharp feather boundaries on clipped AI results: masks now fade inward to full transparency at the outer edge. Original selection, centered circle and square masks retain their 0–1000 px controls, undo/redo and `.pcraft` persistence. Adjust an existing layer's feather slider to apply the new mode.
- Shows total elapsed time after successful generation, including selection export, generation and import.
- Updates Windows executable staging and packaging so the current editor build is included.

Download `photocraft-codex-ai-0.4.0-windows-x64-local-node.zip`, extract completely, and run `start.cmd`. Save documents and close the old version first. Extract into a new folder and copy your own `runtime/codex-proxy.json` if needed.

Includes PhotoCraft 0.20.1, Python 3.13.5 and Pillow 11.3.0. Uses local Node.js, npm-installed Codex CLI and your own sign-in; no Node.js, Codex CLI or account credentials are bundled.

Focused, live-editor, static, wasm and adversarial-input checks passed. Full regression is not entirely green; existing small-stack failures in the development configuration and environment limits are documented in `VALIDATION.md`. This remains a preview development build requiring internet access and a Codex account with working built-in image generation.
