# Unreleased / 统一开发版新增

- PSD 比例适配达到三轮审查上限、审查超时或返回无效审查结果时，保存最近有效方案为原工程同级的“自适应_宽x高_待审查.psd”，重名自动编号；新草稿保留分层和保存路径，明确标记审查未通过。取消任务和首次渲染失败不额外导出。
- Preserve a layered, review-required PSD beside the source when bounded layout review fails, times out or returns invalid results. Use collision-safe pending filenames, retain the latest valid correction, and keep review failure visible instead of reporting success.

- 修复竖版 PSB 适配方图时的功能卡片和标注脱离：多卡片剪贴组按卡片拆分，并绑定其他分组内的标题；细长产品、箭头、说明与关联投影共用变换。
- 背景扩图不再收集独立装饰笔迹、局部投影与空组；原生渐变叠加均匀底色时直接适配背景，不调用生图。运动模糊投影先保留源智能对象备份，再转换副本，避免缩放后出现硬边。
- 审查增加跨不同卡片高度的宽度一致性检查，并明确只审查布局，避免要求坐标计划修复源图片噪点。

- 隔离版改为复用系统 Codex 的现有登录、配置与会话，不再强制覆盖 `CODEX_HOME`；PhotoCraft 本身仍独立运行。

- 新增独立 PhotoCraft 0.23.0 分支与隔离安装：独立源码、编译缓存、编辑器配置、Python/插件副本、后台端口、Codex 会话目录及工程旁历史/切图命名空间。沿用原有 Unified 的功能，旧版保持独立。
- 迁移至新版自动化读取结果和剪贴板结构；按固定提交嵌入外部翻译库，并叠加 191 条自定义中文翻译（简体/繁体分别保存）。

- 快速导出支持格式选择：动态读取当前构建可写的图片格式（PNG、JPG、WebP、TIFF、BMP、GIF 等），当前/批量及指定文件夹共用格式、JPEG 质量和 WebP 无损/有损设置，输出扩展名匹配实际编码。
- Quick export now selects writable image formats from the native codec registry, with JPEG quality, WebP lossless/lossy settings and matching filename extensions for current/batch exports.

- 标题栏新增「导出图片」及下拉菜单：当前工程一键导出完整画布 PNG 到同级 `导出图片` 文件夹；批量导出所有已打开工程；当前/全部导出到指定文件夹。后台逐张处理、进度与失败列表、取消保留已完成图片；重名自动编号，不覆盖工程及已有图片。
- Added title-bar PNG export for the current or all open projects, sibling or chosen folders, background progress, cancellation and collision-safe filenames. Exports preserve the source projects and selection.

- PSD 比例适配增加实际预览视觉审查与有界自动修正；修复剪贴图片完整尺寸误当卡片可见尺寸，支持混合文件夹内标注与卡片分别布局。
- Visually review native reflow drafts with bounded corrections; respect clipped visible bounds and separate independent callouts from cards in mixed folders.

- PSD 比例自适应结果保存到原工程同级目录，重名自动编号，关联新文档保存路径；未保存工程使用临时输出。
- Save ratio-adapted PSDs beside their source project with collision-safe names and the correct document save identity. Unsaved projects keep temporary output.

- 修复局部修改返回图的小幅构图偏移：基于未修改上下文校正位置/缩放，保持一次采样；新增可靠性检查，失败保留结果并拒绝自动导入。Windows 开发版包含 NumPy 与 OpenCV headless 对齐依赖。
- Register selection-edit returns against unchanged context, preserving single-pass sampling; reject unreliable alignment and retain raw results. Bundle NumPy/OpenCV headless dependencies.

- 修复局部修改/移除物体的细节损失：选区加上下文取样，最长 1536 像素；返回原图直接裁切，一次适配；兼容旧任务，保留选区外像素。
- Preserve detail in fill/remove with selection-local references and single-pass mapping from raw returned pixels; legacy edit maps remain supported.

- 审计修复：保护剪贴/蒙版组，收紧盖印比对，支持单层 PSD，新增中间缓存保留规则及查看/清理命令；保留生成图片、成品和旧任务。修复扩图背景无法放在原生 Background 图层下方的导入错误。
- Audit fixes: preserve dependent groups, compare stamped previews at full resolution, support flattened PSDs, manage completed intermediate caches, and import outpainted scenes above hidden native Background backups.

- 修复置顶合并预览遮挡比例自适应：对比重复盖印与原分层，仅在新副本隐藏重复盖印；保留剪贴分组，纯色背景跳过扩图。
- Detect redundant leading stamped previews before PSD reflow, retaining them hidden in the copy; preserve clipped card groups and skip outpainting flat backgrounds.

- PSD 比例自适应支持背景自动扩图：隔离场景，生成扩展区域，保留可编辑文字与 Logo，原背景在新副本中隐藏备份。
- Automatic background outpainting during PSD ratio adaptation, retaining editable foreground layers and hidden original scene layers.

- 修复方图转竖图时，未命名场景图与补边层分别移动导致的透明空洞和接缝；相连场景使用同一等比覆盖变换，文案区块单独排版。位图场景铺满不同宽高比时可能裁切背景。
- Fix transparent gaps when resizing square PSDs to portrait: canvas scene rasters and edge repairs share a uniform cover transform, while copy is rearranged separately. Raster scenes may be cropped to fill the target aspect ratio.

- 新增现有 PSD 比例自适应：分析当前文档内容，在新副本中重排区块并等比缩放，保留原文字、智能对象、分组与 DPI。纯色背景分栏和分隔线单独适配画布。
- Adapt existing PSD ratios by analyzing current content, repositioning/uniformly scaling groups in a new copy, retaining text, smart objects, groups and DPI. Named background panels and dividers adapt separately.

- PSD 文字样式支持标题、副标题、正文/小字分别设置字体、字重和像素字号（0 为自动），支持历史与批量制作。优化宽高、DPI 预设和设置分区；未保存工程的历史提示不再误报为 PSD 错误。
- Independent title/subtitle/body families, styles and pixel sizes (0 for automatic), including history/batch support. Cleaner canvas/DPI sections and a non-error notice for unsaved-project history.

- 新增多参考图批量转 PSD：逐张分析、独立新建、按源文件命名并保留大组。支持逐张进度、失败继续、取消保留已完成文件及 JSON 清单。
- Add Batch references to PSD: independent analysis and new files per reference, source-based names, major groups, per-item progress, failure continuation and durable cancellation reports.

- 中英文主页优先展示三项主要功能：基本生图、局部修改和移除物体，各有独立 GIF。自制场景实际经过插件 Codex 生图/编辑；英文版重放相同结果，动图压缩等待过程。
- Lead both showcases with separate Generate, Edit selection and Remove object GIFs. Original examples were generated/edited through the actual plugin; English replays the same outputs and waiting is condensed.

- GitHub 中英文主页和指南更新：分语言动态 GIF、当前单抽屉设置截图、命名大组示例与功能表；演示使用预先分析的自制示例，不代表远程生成速度。
- Refresh separate Chinese/English GitHub showcases with animated GIFs, unified settings screenshots, named-group examples and feature tables. Demonstrations use a pre-analyzed original sample rather than measuring remote generation speed.

- 主栏与 PSD 工具合并为单抽屉：一次展开即可设置来源、位置、字体、尺寸、DPI 并制作，取消分类页跳转。
- PSD 自动按命名大区块分组：一个总组、最多 8 个区块组，默认折叠，保留原始叠放顺序和可编辑元素。
- Merge composer and PSD tools into one expandable drawer with all settings and actions together. Generated PSDs use a named root and at most eight major groups, collapsed by default, preserving paint order and editable elements.

- 工具抽屉采用左侧分类导航、右侧功能内容布局，包含全部工具、PSD 底稿、详情页底稿、参数设置；参数直接在抽屉中调整，主栏仍保留参考图与历史。
- Tools drawer now has left navigation and right content for All tools, PSD base layouts, Detail page base and settings. Edit parameters inline while references/history remain in the main composer.

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
