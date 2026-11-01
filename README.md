# PhotoCraft · Codex AI 0.2.6 — 原生选区工具栏

**免安装整合包：** [下载 Windows x64 便携版](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.6)，
选择 `photocraft-codex-ai-0.2.6-windows-x64-portable.zip`，完整解压后双击 `start.cmd`。
已包含 PhotoCraft、Python、Pillow 和 Codex CLI，无需另装 Python、Node.js 或运行 pip。
首次按提示在浏览器登录自己的 Codex/ChatGPT 账号；之后直接启动即可。
仍需网络和支持内置生图的账号。整合包不包含任何账号凭据、任务记录或本机代理设置。
需要代理时按包内 `使用说明.txt` 配置；重新登录可运行 `login.cmd`。

以下是旧版源码/需自行安装依赖的包说明；使用 0.2.6 便携版可跳过环境安装步骤。

[下载 Windows 集成版](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.5)：
选择 `photocraft-codex-ai-0.2.5.zip`，完整解压后运行 `start.cmd`。
GitHub 自动生成的 Source code 压缩包仅含源码，不包含编辑器二进制。

0.2.5 的“生成图片”不再额外羽化边缘，保留原始选区遮罩；局部修改和移除物体继续使用
默认 12 像素向内羽化。生成结果仍作为新图层导入，支持撤销。

0.2.4 支持为插件启动的 Codex 单独设置 HTTP 代理，配置见下方 `codex-proxy.json` 说明。
本机代理地址不会写入发布包，也不会修改系统或全局 Codex 设置。

0.2.3 修复连接反复超时和失败原因不清楚的问题。每次任务通过已有 Codex 登录使用 HTTPS，
限制网络重试；遇到服务端安全拦截、额度不足或网络错误时显示具体原因，最多等待 3 分钟。
纯色空白画布省去参考图上传。一次 HTTPS 实测约 73 秒成功返回，耗时仍取决于网络和服务端。
不修改全局 Codex 配置，不自动重试安全拦截，也不切换付费 API。

0.2.2 为局部编辑加入默认 12 像素边缘羽化，在选区内逐渐过渡到原图，内部保持清晰。
支持不规则选区和原有软选区，选区外保持不变。这是本地合成步骤，不额外调用生图。

0.2.1 默认只生成一版，精简每次任务的准备步骤，使用低推理强度；完整 PNG 返回后即可导入，
不等待助手的收尾说明。一次真实编辑测试约 46 秒，服务端排队及画面复杂度仍会影响耗时。
每次任务新增 `timing.json`，用于记录图像返回和总耗时。无需重新登录或设置 API Key。

在 **PhotoCraft 软件内部、选区下方**直接输入描述并使用：

- **局部修改**：按描述修改选中的区域。
- **移除物体**：移除选区中的物体并自然补全，不需要填写描述。
- **生成图片**：按描述在选区内生成新画面。

“生成图片”保留原始选区边缘，不附加羽化；局部修改和移除物体默认羽化 12 像素。

生成完成后自动添加为新图层，原图保持，支持一次 Ctrl+Z 撤销。
这是实际的 Rust/egui 原生界面。

## 原生版使用

双击 **`start.cmd`**（或 `start-native.cmd`），会打开项目内的原生集成版 PhotoCraft。
在新窗口中打开图片，用框选或套索建立选区，下方即出现工具栏。
输入描述后点击“局部修改”或“生成图片”；移除物体可直接点击。

工具栏跟随选区、缩放、平移和旋转，靠近底部时自动放到选区上方。
运行时显示进度和取消按钮；错误就地显示，可悬停查看完整信息。

**原版 `D:/PhotoCraft` 未被覆盖。** 原生版位于 `native/photocraft.exe`，配置独立保存在
`runtime/native-profile/`。应从启动脚本打开，以便同时启动本地生成后台。
原生任务保存在 `runtime/native-jobs/`。

如需为插件的 Codex 命令行显式指定 HTTP 代理，创建 `runtime/codex-proxy.json`：

```json
{"url":"http://127.0.0.1:10808"}
```

地址应与本机代理软件的 HTTP/混合端口一致，并保持代理软件运行。配置仅传给插件启动的
Codex 子进程，不修改系统环境或全局 Codex 设置；本地编辑器连接绕过代理。
删除该文件即可恢复继承原有网络设置。该本机配置不会打包到发布压缩包。
显式代理可避免不可靠的直连，不能保证缩短服务端生成耗时。

无选区时工具栏隐藏。需要整张文生图时，可选中整张画布，或用 `start-panel.cmd` 打开备用面板。
当前原生程序为开发构建，尚未制作 MSI。原生源码补丁与重建说明见
[native-source/README.md](native-source/README.md)。

[原生工具栏截图](examples/native-toolbar.png) · [点击原生按钮后的结果](examples/native-toolbar-result.png) · [分层演示](examples/codex-ai-native-demo.pcraft)

## 备用面板（0.1）

中文桌面伴随面板：文生图、选区局部修改、选区移除物体。
使用本机 Codex CLI 的内置生图工具及已有登录，不读取登录凭据，不自动转付费 API。

本机已验证真实生图与局部修改。[验证记录](VALIDATION.md) · [生图样例](examples/text-to-image.png) · [局部修改样例](examples/local-edit.png) · [分层演示文档](examples/codex-ai-demo.pcraft)

## 启动

本机：双击 `start-panel.cmd`。会打开独立的 PhotoCraft 配套窗口，已有窗口和文档保留。
请在**新打开的窗口**中编辑图片。
面板运行时，可以从 PhotoCraft 的 `Filter → Plug-ins → Codex AI` 唤回面板（需要激活像素图层）。

其他机器需要 Python 3.10+（含 Tk）、`pip install -r requirements.txt`、PhotoCraft 桌面版、
Codex CLI，并先完成 `codex login`。自定义位置：

```powershell
python -m photocraft_ai --photocraft "D:/PhotoCraft/photocraft.exe"
```

1. 文生图：选择模式、填写描述、开始生成，预览后点击“在 PhotoCraft 新建文档”。
2. 局部修改：在配套 PhotoCraft 打开图片，框选或套索区域；在面板填写描述并生成。
3. 移除物体：选择区域，选择移除模式后生成。
4. 预览后采用：以新图层导入，原图保持，可用 Ctrl+Z 撤销。

生成期间可以修改文档，但文档有变化时会拒绝自动导入，防止结果错位。
图片、原始选区、提示词、Codex 日志在 `runtime/jobs/`，生成服务会接收图片与描述。
取消会终止本次 Codex 子进程；服务端已开始的任务可能仍消耗额度。

## 实现与限制

- 备用面板通过认证的 localhost 控制接口连接原版编辑器；0.2 原生版在独立程序中渲染选区工具栏。
- 菜单入口是临时安装的无操作 WASM 滤镜，借鉴 OpenFill 的方式；面板识别并移除它产生的空历史步骤。仅在本次配套编辑器进程中有效。
- Codex CLI `exec` 启用 `image_generation`，使用 workspace-write 沙箱，禁用多代理。
- 编辑时提交原图和带标记的区域参考图，模型返回完整图；本地使用原始选区裁切结果图层，选区外完全透明。
- 若生成图分辨率不同但宽高比相同，会等比例适配；宽高比不匹配时保留图片并拒绝导入。初版暂不做自动扩图或候选切换。
- 导出和生成图层为 8-bit PNG；高位深、特殊颜色空间的专业保真暂未验证。
- Codex 不同安装、账户、模型或沙箱可能不开放内置生图。失败时显示错误并保留日志，不承诺所有订阅均可用。
- 本地 `image_generation=true` 只能证明功能开启，实际可用性以生成结果为准。
- 关闭面板不会关闭编辑器，未保存文档可继续编辑。

桥接代码源于 OpenFill（Apache-2.0），详见 [THIRD_PARTY.md](THIRD_PARTY.md)。

## 验证

```powershell
python -m unittest discover -s tests -v
python -m photocraft_ai --connect-only
python tests/smoke_photocraft.py
```

实机测试会在配套实例中新建测试文档，保留导出样本于 `runtime/smoke/`。
