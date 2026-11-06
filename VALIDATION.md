# 本机验证记录

## 跟随选中图层与 PSD 底稿（2026-11-06）

- 普通生成记录发起时的活动选中图层，通过已有 copyToDocument 路径在该层上方插入；未选中时保留置顶。未增加单独移动图层的撤销步骤。
- 增加参考图转 PSD 底稿：独立 CLI 只读分析请求禁用生图，以受限 JSON 重建文字和几何形状；不执行模型返回的命令，不导入参考照片。输出新 PSD 文档，不修改源工程。
- Python 67 项通过，覆盖布局白名单、非法数据拒绝、受限曲线及选中层/置顶选择。真实编辑器验证中间图层上方插入，PSD 关闭并重开后文字仍为 Type、边框和底色仍为 Shape。
- 使用本项目制作的 SUMMER SALE 几何参考图执行一次真实 Codex 分析，得到 4 个布局元素，构建并重开 PSD 验证成功；未使用用户照片，未调用远端生图。该样例不代表任意设计都能精确还原。
- Native/UI all-targets Clippy、wasm 和分层检查通过，保留上游既有 wasm 警告。
- 对用户指定的 5 张本地营销主图分别执行真实版式分析并导出到指定目录；1500×2000 尺寸保持，PSD 重开验证文字层数量为 13/6/3/4/3，总层数为 24/12/9/8/7，产品和人物照片不导入。用户原图、生成的 PSD 和预览只留本机，不发布到仓库。

## 完整长图与分语言页面（2026-11-05）

- 切图默认按可用宽高等比完整显示并居中，保留可关闭的 Fit full image 选项，放大细节时仍可按宽度滚动查看。
- 中文首页 README.md 与英文 README.en.md 独立，使用图、说明和工程路径页分别链接各自语言；不再在一个首页折叠混排两套图片。
- 中英文真实界面截图显示完整 640×1280 长图、三条切割线和四段；自动检查图像边界在截图可视区域内。示例为本项目制作的几何图案。

## 工程隔离保存（2026-11-04）

- 历史按编辑器实际保存路径选择 `<完整文件名>.photocraft-data/history/`，HTTP 请求不能指定任意历史目录；校验当前工程上下文，切换/另存为时清理列表并丢弃过期异步结果。
- 切图自动方案改为相邻 `cutting/plan.json`；导出方案写入 `cutting/longpiccutter.json`。切换文档关闭旧切图窗口，打开中的方案在另存为后改写新工程目录。
- Python 63 项通过，新增工程隔离、未保存拒绝、过期路径拒绝。真实编辑器验证两份相同画布的工程历史和切图隔离、重开方案恢复、另存为切图路径跟随；未调用远端生图。

## 历史恢复逻辑修正（2026-11-04）

- 打开历史时保留提示词/参考图修改工具栏，历史窗口默认位于右侧，可同时查看和编辑。
- 恢复接口不再保存当前草稿，不再因反复回滚新增记录。需要保留未提交内容时手动保存草稿。
- 保存时按提示词、操作类型、参考图顺序/名称和实际 RGBA 像素去重；相同组合复用已有记录，兼容旧记录，无需再次复制图片。
- Python 62 项测试通过，覆盖重复保存及跨实例去重、反复恢复条数不变和认证要求。中英文实际界面检查保留两个窗口、恢复提示词/参考图且条数不变。

## 提示词与参考图历史（2026-11-04，统一开发版）

- 生成任务准备成功后自动保存提示词、操作类型与参考图；增加保存草稿、历史列表和恢复。恢复先保存当前草稿，不修改画布、不自动生成；历史保存在 `runtime/native-history/`，跨重启保留，最多 50 条及 512 MiB，超限清理旧记录。
- Python 61 项通过，新增覆盖跨实例恢复、图片顺序与像素、纯文字记录、数量/空间保留限制、无效记录清理、路径限制、生成自动保存及带认证 HTTP 恢复与当前草稿备份。
- 中英文真实编辑器验证保存草稿、修改提示词/删除参考图、恢复原提示词和两张参考图、当前草稿备份及文档完全不变。英文实例复用前一实例记录，确认重启持久化；截图只使用合成测试图片，未调用远端生图。
- Native/UI all-targets Clippy、wasm 及 31 crates 分层检查通过；历史窗口打开时隐藏浮动工具栏并暂停画布快捷键，避免操作冲突。保留既有 wasm 警告，不声称全量历史回归通过。
- AI 工具栏 10 项和语言辅助 2 项专项回归通过，保留剪贴板参考图和原有拖放、路径限制行为。

## Windows 剪贴板兼容修复（2026-11-04）

- 复现主读取器对当前 Windows DIB/DIBV5 剪贴板图片的转换错误；新增有尺寸/长度上限的 24/32-bit 非压缩 DIB 兼容读取，通过已锁定的 clipboard-win 5.4.1 安全接口访问系统剪贴板，无新增 unsafe 代码。主读取器成功时仍保留原格式处理。
- 修复新增翻译条目缺失首列导致中文按钮仍为英文的问题。针对中文粘贴按钮及空图片提示增加翻译断言。
- 新增 DIB 方向、行补齐、显式透明度、无 alpha 位图、不完整数据及超大尺寸测试，并只读验证当前实际剪贴板。真实编辑器中对当前剪贴板验证按钮、Ctrl+V 和画布粘贴；未上传、发布用户图片，未调用远端生图。
- 补上 Windows 原生图片粘贴只转发 V 松开事件时的参考图路由，并防止同一次按键重复追加。

## 剪贴板参考图（2026-11-04，统一开发版）

- 新增“粘贴参考图 / Paste reference image”按钮；提示词输入框聚焦或鼠标位于 AI 工具栏时，Ctrl+V 图片追加为参考图。文字粘贴及工具栏外的画布粘贴保留原行为。支持连续追加、缩略图移除、忙碌保护和原参考图资源校验。
- AI 工具栏专项 10 项通过，包括剪贴板路由不改变文档、普通文本保留及非法/超大尺寸拒绝；UI all-targets Clippy（警告视为错误）、wasm 检查和 31 crates 分层检查通过。wasm 保留上游现有警告。
- 独立真实编辑器中验证按钮追加、Ctrl+V 追加、无重复添加、参考图粘贴不改变文档，以及画布 Ctrl+V 仍新增图层。测试后恢复原剪贴板内容，未请求远端生图。
- 中英文使用截图同步更新。当前仍为开发版，不表示已发布的 v0.4.0 ZIP 包含该功能，也不声称全量回归通过。

## 统一开发版：一个 PhotoCraft 同时承载两个工具集

- 将 Userfull Tools 的长图切割、整幅画布复制、语言辅助与尺寸适配合入现有 0.20.1 Codex AI 编辑器，保留多图参考、羽化和耗时显示。正常启动和本机旧 Userfull 入口均指向同一程序，本轮不打包。
- 适配 0.20.1 新增的 `Clip.svg`；保留原来的 SVG 剪贴板导入逻辑，显式导出位图时清除旧 SVG 状态。
- Python 54 项、AI 工具栏 8 项、剪贴板 UI 2 项、切图 5 项、语言 2 项、剪贴板引擎 3 项通过；all-targets Clippy、分层、wasm 和 panic_hunt（132.55 秒）通过。
- 临时编辑器中同时验证参考图加载/移除和长图切割，文档像素及选区状态不变，界面截图确认长图切割和复制图片位于同一编辑器。本轮未请求远端生图，未替换用户剪贴板内容。

## 0.4.0 开发版：原插件多图参考

- 从 Userfull Tools 的参考图功能提交 `c05124b` 单独迁移原生工具栏、拖放、自动化入口和 Python 附件链路；保留 0.20.1 基线、原来的 `start.cmd`、羽化和耗时显示，不迁移切图或剪贴板功能。
- Python 46 项测试及 UI 的 8 项 Codex AI 专项通过，覆盖参考图顺序、多个附件、数量不固定、资源保护、非法图片拒绝、路径受限、拖放命中工具栏及原画布不变。
- 原 Codex AI 的真实 0.20.1 编辑器中，参考图加载、缩略图按钮及单张移除验证通过，截图确认入口可见。本轮未请求远端生图。
- UI all-targets Clippy（警告视为错误）、分层和 wasm 检查通过；补丁反向检查通过。最新编辑器已编译，沿用原插件启动入口。

## 0.4.0 开发版：同步 PhotoCraft 0.20.1

- 上游正式标签 v0.20.1，提交 `327c4cc82e737a3e0af7c147a477126d77525495`；在独立源码目录迁移集成补丁，无冲突，保留旧版源码和二进制。
- 新编辑器输出到 `native-0.20`，启动脚本优先选择此版本。保留原生 AI 工具栏、向内羽化和生成耗时显示；构建与打包脚本同步使用 0.20.1。
- Python 37 项测试通过；向内羽化、可撤销参数和原生格式往返专项通过；蒙版引擎 6 项、图层菜单 22 项、AI 工具栏 4 项通过。
- all-targets Clippy（警告视为错误）、分层、wasm（24 crates + heif）及 panic_hunt 通过，异常参数检查耗时 181.95 秒。补丁反向检查通过。
- 实机验证 AI 工具栏、最外沿透明、内部渐变、撤销/重做、保存/重开通过；原选区/圆形/正方形及 0 px 恢复通过。
- 0.19 测试项目在 0.20.1 打开、另存、重新打开后逐像素一致。本轮未调用远端生图，不声称完整回归或素材/性能测试全部通过。

## 0.3.1：向内羽化与生成耗时

- 修复图片 alpha 已裁到选区、普通高斯蒙版在边界仍有透明度导致的硬截断。新增独立蒙版的向内渐隐模式，最外沿覆盖为 0，向内部平滑过渡；原选区、圆形和正方形均支持，0 px 恢复硬边。
- 向内羽化参数随 `.pcraft` 保存；标准蒙版默认保留原有高斯行为。已有图层重新调整右键羽化滑条即可应用新模式。
- 完成提示显示从读取选区到导入新图层的总耗时，精确到 0.1 秒。
- Windows 运行中的编辑器锁定二进制时，构建器暂存新程序，启动器在下次启动时根据构建信息加载；整合包只包含当前构建对应的编辑器。
- Python 37 项、合成模块 413 项、蒙版引擎专项 6 项、图层菜单 18 项通过；U8/U16/F32 边界透明、渐变、大半径和原始数据保留检查通过。
- 真实编辑器的三种蒙版、0 px 恢复、撤销/重做、保存/重开均通过。12 px 羽化实测覆盖：0、5、19、40、66、96、128、159、189、215、236、250、255。
- 新参数的原生格式往返、all-targets Clippy、分层、wasm（24 crates + heif）及 panic_hunt 通过；补丁反向检查、二进制及补丁哈希核对通过。
- 不声称全量回归通过：高并发引擎测试中的插件超时项单独复跑通过；原生格式及 IO 的小栈测试溢出在未修改的 0.19.0、相同开发配置下也能复现。性能基准因 Windows 拒绝执行构建脚本（os error 5）失败；素材测试的外部下载及耗时较长的完整 UI 测试已停止。

## 0.3.0 升级 PhotoCraft 0.19.0

- 使用正式 v0.19.0 标签，基线提交 `2df9f807702a935184041355a86405380bda8274`；在独立 worktree 迁移集成补丁，保留旧版源码和二进制。
- 补丁仅有一处默认工具状态冲突，保留上游 Tool::Move 并加入空 AI 提示词。新增默认状态回归测试。
- Python 37 项测试、蒙版引擎 5 项、图层菜单 22 项、AI 工具栏 4 项测试通过；分层及 wasm（24 crates + heif）检查通过。
- 新版引擎/UI 的 all-targets Clippy、格式检查及命令注册表恶意参数 panic_hunt 检查通过（125.87 秒）。整合包内 Python 运行 37 项测试通过，二进制、补丁和依赖文件哈希已核对。
- 实机点击原生 AI 工具栏生成图片，直接接收 PNG 约 45.14 秒，新图层、选区外不变、选区保留、0 羽化、撤销/重做均通过。
- 0.18 生成的可编辑蒙版项目在 0.19 中打开后，另存并重新打开，逐像素结果一致。圆形/正方形菜单、滑条调整、一次撤销/重做和保存参数保留通过。
- 仍为未优化开发构建，不将上游正式优化构建的性能数据视为本整合包性能承诺；不声称全量 UI 测试通过。

## 0.2.9 图层右键可调羽化

- 新 AI 结果保留原始选区像素透明度，并在临时文档中创建独立原生蒙版、设置默认羽化后再作为一个新图层导入，目标文档单步撤销。
- 图层及蒙版缩略图的右键“边缘羽化”菜单：原选区、居中圆形、居中正方形，0–1000 px 滑条及数值输入；矩形选区内按短边生成内接圆/正方形。
- 实机右键点击和滑条验证通过：12 px 调至约 40 px，单次撤销恢复 12，重做恢复新值；选区保留、选区外不变，保存并重新打开后蒙版外观和羽化参数一致。已查看菜单与圆形/正方形截图。
- 子菜单在修改形状、滑条和数字时保持打开；数值框手动输入 24 px 的实机检查通过。
- 37 项 Python 测试、5 项蒙版引擎测试（8/16/32 位）、22 项图层菜单 UI 测试通过；命令注册表恶意参数 panic_hunt 检查通过。
- 引擎和 UI 的 all-targets Clippy、格式、分层和 wasm（24 crates + heif）检查通过。
- 旧图层的烘焙软边不具备原始未羽化像素，不能反向消除；新图层使用可编辑蒙版。当前仍为未优化开发构建。

## 0.2.8 直接接收生成结果

- 用户失败任务实际已生成 PNG，失败发生在 Windows `CreateProcessAsUserW` 启动复制命令阶段（错误 5）。
- 已找回该任务生成文件，核对原文档名称和 revision 后按原始选区及羽化参数导入新图层，未重新请求生图。
- 后台直接从当前 thread.started 对应的 generated_images 会话目录接收完整 PNG；UUID 校验、目录边界检查，多个有效候选时不猜测，不接受不完整 PNG，原有沙箱不变。
- 35 项测试通过，覆盖 CLI 复制命令失败退出时的结果接收、目录范围、PNG 完整性和歧义结果拒绝。

## 0.2.7 使用本地 Node.js/Codex

- 删除构建流程中的 Codex 程序和资源复制步骤，发布包不含 Node.js、Codex CLI 或 tools 目录。
- 优先通过本机 node.exe 执行 npm 安装的 codex.js，同时识别 PATH 上 Codex 命令所在的自定义 npm 前缀。
- 保留内置 Python 3.13.5/Pillow 11.3.0 和 PhotoCraft；缺少本机 Codex 时显示明确的安装命令。
- 33 项测试通过，新增本地 Node.js/自定义 npm 前缀识别以及缺失 Codex 的错误提示覆盖。

## 0.2.6 Windows x64 免安装整合包

- 内置官方 CPython 3.13.5 embeddable、Pillow 11.3.0 wheel、Codex CLI 0.166.0 原生程序及沙箱/命令辅助程序，不依赖系统 Python 或 Node.js。
- PATH 仅保留 Windows System32，设置空白 CODEX_HOME，使用包内 Python 进行自检：组件正常，登录状态正确为未登录；包内 Python 执行 31 项测试全部通过。
- 整合包不包含 auth.json、任务目录或本机代理设置，首次通过 Codex 自身的浏览器登录流程登录；账号凭据由 Codex 管理。
- Codex、Python、Pillow 及附带二进制依赖的许可证随包提供；语音资源不包含在整合包中。
- 尚未在另一台全新 Windows 设备进行完整登录、生图与原生窗口实机验收。

## 0.2.5 生成图片保留边缘

- 原生“生成图片”使用 0 像素附加羽化，仍保留原选区自身的透明度与软边；局部修改和移除物体继续使用 12 像素向内羽化。
- 31 项 Python 测试通过，新增覆盖三个原生操作的羽化参数，原有合成测试覆盖原始遮罩保留、边缘过渡及选区外透明。
- 本次仅改变 Python 后台的合成参数，不重建原生二进制，也不额外请求生图。
- 实际原生编辑器验证：通过原生后台“生成图片”操作导入固定测试图，选区两侧边缘完全不透明，选区外逐像素不变，选区保留，单步撤销恢复原图；另行验证局部修改仍保留 12 像素羽化。
- 实机脚本 `tests/smoke_generate_edges.py`、`tests/smoke_feather.py` 均通过；使用独立临时文档并恢复原有活动文档。

## 显式命令行代理

- 0.2.4 实际生图：使用与之前 HTTPS 测试相同的兔子照片描述，完整图片返回 48.84 秒，总计 50.38 秒，`explicit_proxy=true`，日志无重连。此前相同描述总计 72.95 秒；样本各一次，不能排除服务端负载等影响，也不能据此保证固定提速。
- 发布包 `dist/photocraft-codex-ai-0.2.4.zip` 包含代理功能，不包含本机 runtime 配置、任务或令牌。
- 本机 `runtime/codex-proxy.json` 指向 HTTP 代理 `127.0.0.1:10808`，只注入 Codex 子进程；HTTP/HTTPS/ALL_PROXY 一致，本地地址加入 NO_PROXY。
- 当前 CLI 的 `respect_system_proxy` 为 false、`system_proxy_fallback` 为 true，原有系统代理回退可能已经生效，不能将显式设置等同于新增提速。
- 相同 HTTPS provider、相同登录的无工具文本请求，在显式代理下 14.62 秒返回 OK；不代表生图耗时。
- 30 项 Python 测试通过，覆盖子进程代理覆盖、父环境不变、本地地址绕过、缺省继承和错误配置提示。
- 已备份完整文档。组合重启命令被自动审批拦截后，核实后台空闲及进程身份，仅停止该明确 PID 并分别启动后台成功；编辑器保留，原文档名称与 revision 一致。

## 0.2.3 连接与错误反馈

- 用户失败任务先经历多次连接超时，随后服务端报告 `moderation_blocked`，阶段为输出检查；未生成图片。没有自动重试该任务或改写描述。
- 改为单次任务的 HTTPS provider 配置，继续使用现有 Codex 登录及默认服务地址；关闭 WebSocket，网络和流重试各限制一次，不修改用户全局配置。
- 中性兔子照片真实生图成功：图片完整返回 71.58 秒，总计 72.95 秒，日志无反复重连。记录在本机 `runtime/http-check-2/timing.json`，不构成固定耗时保证。
- 识别安全拦截、额度不足、登录失效、限流和网络失败；检测拦截后直接结束等待。总等待上限改为 3 分钟。
- 纯色不透明空白画布可省去参考图；存在画面内容时保留完整参考图。
- 27 项 Python 测试通过，包括失败分类、拦截后终止、空白画布与已有内容区分。
- 更新时先备份完整文档副本，仅重启 Python 后台；原生编辑器、文档名称和 revision 保留。

## 0.2.2 边缘羽化

- 局部编辑默认 12 像素向内羽化，原选区保留，选区外不增加像素；生成画面内部保持清晰。
- 不规则选区、孔洞、原有软选区、单像素小选区均有覆盖；小选区自动归一化，避免完全消失。
- 22 项 Python 测试通过。实机验证边缘混合、中心不透明、选区外逐像素不变及单步撤销。
- 1254×1254 图像、约 1042×1028 选区的本地羽化耗时约 0.256 秒；不增加模型调用。
- 新任务记录 `feather_px`，保存实际混合蒙版 `blend-mask.png`。原生二进制无需重建。

## 0.2.1 延迟优化

- 本次用户任务从创建到生成图层约 110 秒；日志显示每次任务启动完整 Codex 会话并读取长技能说明。
- 任务改为低推理、单次生成，按调用禁用长篇资产设计技能；不改用户全局配置，也不改所用模型。
- 原生生图工具和现有账号登录保持；未引入额外收费服务或 API 后备。
- PNG 文件完整返回后提前结束助手收尾，增加 JSON 事件日志及 `timing.json`。
- 使用既有演示图及选区完成一次真实编辑，约 45.6 秒。与用户上一任务不是严格同请求 A/B，不能据此保证固定提速比例。
- 16 项 Python 测试通过，包括完整 PNG 提前返回、半截 PNG 不导入、取消不返回结果。
- 仅重启了本地 Python 后台，原生编辑器进程及两个打开文档保持；重启前后文档名称和 revision 相同，并已另存完整副本备份。

## 0.2 原生选区工具栏

2026-10-31，基于 PhotoCraft 0.18.0 源码提交 `422ca7beda90d927643bcd074646ebbd37706d75`。

- 在实际 Rust/egui 编辑器内渲染选区工具栏，已查看截图确认中文输入框及三个按钮均显示。
- 实际点击工具栏输入和“生成图片”按钮，调用已登录 Codex 生图，并自动导入新图层。
- 逐像素确认选区外 RGB 不变、选区保留，单次 Undo 恢复原图，Redo 恢复生成图层。
- 14 种主题 × 1440×900、960×720 共 28 个组合完成截图和控件边界检查，并查看 QA 总览。
- 13 项 Python 测试通过，包括本地后台认证、浏览器跨源拒绝、参数检查及取消。
- 新增 Rust 测试 3 项通过：选区下方定位、边缘避让、选区修订/缩放缓存更新。
- 分层检查通过（31 crates）；原生界面 crate 的 all-targets Clippy 检查通过。
- WebAssembly 兼容检查通过：24 个 crate，以及 codecs 的 heif 可选特性。
- 最终原生二进制已重建，源码补丁通过反向应用检查，格式检查通过。

**全量测试边界：** 运行 `cargo test -p photocraft-ui-egui --lib --tests`，测试进程在输入相关
用例阶段以 `0xc0000005 / STATUS_ACCESS_VIOLATION` 退出，未完成全量测试，不能视为全量通过。
新工具栏在未配置本地后台时不启用；尚未对该全量测试退出做基线归因。当前交付为试用开发构建。

原生输出：`runtime/native-live-report.json`、`runtime/native-smoke-report.json`、`runtime/native-theme-report.json`，
可查看样例 `examples/native-toolbar-result.png` 和 `examples/codex-ai-native-demo.pcraft`。

## 0.1 备用面板

2026-10-31，Windows，本机 PhotoCraft 0.18.0 / Codex CLI 0.166.0 / Python + Pillow 11.3.0。

- Codex 使用已有 ChatGPT 登录，内置生图实际生成蓝色陶瓷杯照片，无 API Key。
- 实际通过 PhotoCraft 控制接口读取原图和选区，调用 Codex 图像编辑，将结果导回新图层。
- 对合成结果逐像素比较，选区外 RGB 与原图完全一致，选区内有修改。
- 桥接测试验证原选区保留，导入多一层，单次撤销恢复原图。
- 原生 `Filter → Plug-ins → Codex AI` WASM 菜单注册成功。
- 8 项单元测试通过：选区透明度、比例适配、异常尺寸拒绝、文档过期拒绝、空选区拒绝、后端失败不导入、写命令不重放、读命令可重试。
- 运行真实 Tk 窗口布局检查：主要控件均有有效尺寸且在窗口内。
- Computer Use 原生连接不可用，因此没有完成截图和鼠标点击验收；真实生成和编辑链路通过代码调用验证。

本机输出（不包含在源码压缩包中）：

- `runtime/live-generation/generated.png`：真实生图原始输出。
- `runtime/live-edit-report.json`：真实局部编辑验证报告。
- `runtime/smoke/report.json`：选区、图层与撤销验证报告。
- `runtime/ui-layout-report.json`：窗口布局报告。
- `runtime/exchange/codex-ai-live-demo.pcraft`：可继续编辑的演示文档。

移除物体使用相同选区编辑链路，尚未单独进行生成质量验收。高位深文档及特殊色彩空间未验证。
# PSD 参数设置验证（2026-11-06）

- 70 项 Python 测试通过，包含参数边界、DPI 与文字点数换算、历史去重与参数恢复。
- 原生设置窗口实测编辑宽高、1:2 比例、300 DPI 和 Arial；经认证的本地 worker 收到全部参数，生成 600×1200、300 DPI 的可编辑文档。
- 真实 Codex 视觉分析将自制 600×600 参考图重新排版为 600×1200；导出 PSD 并重新打开，尺寸、300 DPI、Arial 字体与文字点数一致，文字/形状仍可编辑。
- UI all-targets Clippy（警告视为错误）、桌面编译、wasm 检查及分层检查通过。本轮没有重跑全部原生历史测试，也没有新建 GitHub Release 安装包。
# PSD 字体选择器验证（2026-11-06）

- 字体家族和样式复用文字工具的选择器，菜单预览使用独立标识，不触发原图文字层的悬停预览或格式命令。
- 实际点击选择 Arial 与 Bold 后，经本地 worker 接收参数并导出 PSD；文件包含 Arial-BoldMT 字体信息，重新打开后文字仍为可编辑 Arial 图层。宽高与 300 DPI 同时保留。
- 71 项 Python 测试通过，包含字体样式参数校验，以及禁止模型字重覆盖用户选定样式；桌面构建、UI all-targets Clippy、wasm 和分层检查通过。
# PSD 返回字体字段兼容修复（2026-11-06）

- 实际失败响应使用 `font_style`，旧版误报为不支持元素；现将该字段规范为 `fontStyle`，冲突字段和未知字段仍拒绝，校验不修改原始响应。
- 73 项 Python 测试通过，新增字段别名、冲突及未知字段诊断回归测试；桌面编译、Clippy、wasm 与分层检查通过。
- 使用本机保留的失败响应恢复 1500×2000、72 DPI 的 PSD，重新打开后 9 个文字层可编辑、字体正确。恢复过程未再次调用模型，用户素材与恢复结果均未提交仓库。

## PSD destination switch (2026-11-06)

75 Python tests pass; desktop, Clippy, wasm and layers checks pass. Live native verification adds editable text/shapes to the current document without a new tab or project-path change, then verifies editable PSD roundtrip. Existing new-document behavior remains the default.

## Long detail page base (2026-11-06)

76 Python tests, desktop build, all-targets Clippy, wasm and layers passed. Authenticated native detail-button flow verified. Actual user page (790x26977) analyzed using 12 readable crops into 125 elements including 99 text elements. Native PSD export/reopen verified dimensions, DPI, editable Type/Shape layers and selected fonts; middle and bottom UI previews reviewed. Sample PSD saved beside the original locally; user artwork and model responses are excluded from GitHub. New document keeps reference dimensions; current document uses its existing canvas.

## Composer grouping (2026-11-06)

Desktop, Clippy, wasm and layers checks pass. Native UI screenshot reviewed with the actual long reference: three action groups and readable top-crop thumbnail. Verified PSD settings shares the layout-action row, reference/history row is separate, and the Detail page button still completes the authenticated worker flow. Original reference payload is retained. No remote generation requested for this UI change.

## Selected layer layout source (2026-11-06)

78 Python tests and desktop/clippy/wasm/layers passed. Live native snapshot verifies selected red shape is captured while another blue layer is excluded, preserving source revision and tab count. Layer-source prepare persists one reference. Actual UI with zero attachments switches to Selected layers and completes authenticated worker -> editable PSD flow without a new remote model request. UI screenshot reviewed. History saves the frozen layer image as a reference for restoration.

## Compact composer and tools sidebar (2026-11-06)

Desktop build, all-targets Clippy, wasm and layers passed. Native UI verifies default collapsed sidebar hides secondary actions, opens with Tools sidebar, exposes PSD controls, completes the authenticated worker flow, and closes successfully. Compact and expanded screenshots reviewed. Composer and sidebar both participate in reference-drop and clipboard routing. No new remote generation requested.

## Attached PSD drawer and primary references (2026-11-06)

Desktop/clippy/wasm/layers pass. Native UI verifies paste/history remain available with the drawer closed. Drawer-to-composer gap stays within 10 screen points before and after moving the selection; screenshots reviewed for both right and left placement. PSD worker flow still completes. No remote generation requested.

## Drawer navigation (2026-11-06)

Native UI navigated All tools, PSD, Detail page and inline settings; assertions verify each category only exposes its matching actions. Screenshots reviewed for content layout and inline font/dimension controls. Composer adjacency before/after selection movement and authenticated PSD worker flow passed. Desktop/clippy/wasm/layers pass.

## Unified drawer and major PSD groups (2026-11-06)

79 Python tests passed, including bounded grouping and stable element order. Native PSD export/reopen verifies named root with at most eight section folders, editable text/shapes, dimensions and fonts. Full 790x26977 rendered RGBA pixels are byte-identical before/after grouping. Zero new remote model calls. Actual single-drawer UI screenshot reviewed; all settings and actions visible together, no category navigation or second panel. Authenticated worker flow passed. Desktop/clippy/wasm/layers passed. Grouped sample delivered locally without overwriting the previous sample.
# Bilingual animated showcase (2026-11-06)

- Recorded Chinese and English native UI sessions separately using original project example artwork. No user product references or private history included.
- Both GIFs contain five stages at 1152×720 with positive frame durations and infinite looping; file sizes are under 450 KiB each. Verified 20 Markdown image references resolve locally.
- Full-resolution unified settings and editable named-group screenshots reviewed in both languages. Source generation uses a pre-analyzed example; README and guides disclose this and distinguish animation playback from model latency.
- Documentation/media only; application code and release installation packages are unchanged.
# Core AI feature demos (2026-11-06)

- Actual plugin/Codex generation produces a mug/cube scene; fill changes the mug to blue; removal clears the cube and shadow. A second removal run extends the selection to include the complete shadow; only the final result is showcased.
- Visual output reviewed. Exact image-difference bounds for both edits stay inside their selections, verifying unchanged pixels outside those regions.
- Chinese native UI captures actual remote runs. English UI replays recorded outputs through the same local apply pipeline; this is disclosed on each page. Waiting is condensed rather than presented as generation latency.
- Separate GIFs for all three primary features in both languages; no personal artwork included. Documentation/media only.

## Batch reference PSD conversion (2026-11-06)

81 Python tests pass, including per-file isolation, failure continuation, cancellation retaining files and durable reports. Native batch button with two references creates two separate grouped PSDs. Actual five user JPGs processed sequentially into five named PSDs; all reopen at 1500x2000 with editable Type/Shape layers and bounded major groups. Original JPG hashes unchanged. Results remain in a new subfolder of the user-specified source folder; no user assets published. Desktop/clippy/wasm/layers pass. Batch polling scales with reference count and progress controls remain visible while processing new documents.

## Text hierarchy styling and settings layout (2026-11-06)

83 Python tests pass: role-specific fonts/styles/pixel sizes, validation, legacy size-based role inference. Native UI edits Title Arial/72px, Subtitle Georgia/36px, Body Calibri/18px independently and forwards all settings to the authenticated worker. Native PSD export/reopen at 300 DPI verifies independent family and pixel-size conversion; PSD font faces include Arial-BoldMT, Georgia-Italic and Calibri. Unified UI screenshot reviewed with visible creation buttons. Canvas controls compacted, DPI presets use native combo, unsaved history notice no longer reports a PSD error. Updated bilingual settings screenshots/GIFs; desktop/clippy/wasm/layers pass.
