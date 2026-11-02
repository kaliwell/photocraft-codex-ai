# PhotoCraft · Codex AI

**原生选区 AI 工具栏 / Native selection AI toolbar**

[中文](#中文说明) · [English](#english) · [下载 / Download v0.2.9](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.9)

![PhotoCraft 原生 AI 工具栏 / Native AI toolbar](examples/native-toolbar-final.png)

## 中文说明

在 PhotoCraft 编辑器内部，通过选区下方的原生工具栏进行**局部修改、移除物体和生成图片**。使用本机 Codex CLI 的内置生图能力及已有登录，生成结果自动添加为新图层，支持撤销。

### 下载与启动

1. 在 [v0.2.9 发布页](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.9) 下载 **`photocraft-codex-ai-0.2.9-windows-x64-local-node.zip`**。
2. 完整解压到可写目录。压缩包已包含配套 PhotoCraft、Python 3.13.5 和 Pillow 11.3.0；**不包含 Node.js 或 Codex CLI**。
3. 使用电脑现有的 Node.js 和通过 npm 安装的 Codex CLI。尚未安装 Codex 时，执行 `npm.cmd install -g @openai/codex`。
4. 双击 **`start.cmd`**。已有 Codex 登录可直接使用；尚未登录时按提示登录自己的账号。
5. 在新打开的配套编辑器中打开图片，用框选或套索建立选区，在选区工具栏中输入描述并选择操作。

需要网络，以及实际支持内置生图的 Codex 安装与账号。GitHub 自动生成的 **Source code** 压缩包不含配套编辑器二进制。当前 Windows x64 发布包为试用开发构建；原生编辑器基于 PhotoCraft 0.18.0，插件版本为 0.2.9。

### 使用方式

| 操作 | 行为 |
| --- | --- |
| 局部修改 | 根据输入的描述修改选区，默认羽化 12 px |
| 移除物体 | 移除选区中的物体并自然补全，无需输入描述，默认羽化 12 px |
| 生成图片 | 根据描述在选区内生成画面，默认羽化 0 px |

结果以新图层导入，原图保留，可按 **Ctrl+Z** 撤销。无选区时工具栏隐藏；整张文生图可先选中整张画布。工具栏跟随选区、缩放、平移和旋转，靠近底部时移到选区上方。生成期间可取消；错误显示在工具栏内。

**v0.2.9：可编辑蒙版羽化。** 右键 AI 结果图层 → **边缘羽化**，选择原选区、居中圆形或正方形，拖动 **0–1000 px** 滑条或输入数值。形状中心依据图层的原始像素覆盖范围计算，透明结果按实际像素范围计算。新结果使用独立蒙版，无需重新生图即可调整，支持撤销/重做，保存 `.pcraft` 后保留。旧版本已烘焙到像素中的软边无法反向还原。

[右键操作示意](examples/editable-mask-menu.png) · [可编辑蒙版示例](examples/editable-mask-demo.pcraft) · [分层演示](examples/codex-ai-native-demo.pcraft)

### 代理与本地文件

如需显式指定 HTTP/混合代理，在安装目录创建 `runtime/codex-proxy.json`：

```json
{"url":"http://127.0.0.1:10808"}
```

`10808` 为示例端口，请改为自己的代理端口，并保持代理软件运行。配置只传给插件启动的 Codex 子进程，不修改系统或全局 Codex 设置；本地编辑器通信绕过代理。删除该文件可恢复继承原有网络设置。

- 通过 `start.cmd` 启动，以便同时启动编辑器和后台；不要只打开 `native/photocraft.exe`。
- 原生版配置在 `runtime/native-profile/`，任务图片、提示词、结果和日志在 `runtime/native-jobs/`。
- 已安装的其他 PhotoCraft 副本保持独立。更新插件前先保存文档、关闭旧版，再完整解压新版；插件配套编辑器应随插件更新，避免被上游原版覆盖。

### 数据与限制

- 局部编辑会向 Codex 生图服务提交**整张合成原图及带选区标记的参考图**；选区限制本地导入范围，不限制上传范围。
- 插件通过 Codex CLI 使用已有登录，不自行读取登录凭据，不自动切换到付费 API。取消会终止本次子进程，服务端已开始的任务可能仍消耗额度。
- 本地后台只接收经令牌认证的 localhost 请求，并拒绝浏览器 Origin 请求。Codex 使用 `workspace-write` 沙箱，启用 `image_generation`，禁用多代理。
- 生成完成后，若文档已改变或关闭，会拒绝自动导入，避免错位。图片宽高比不匹配时保留结果并拒绝导入；相同比例的不同分辨率会等比例适配。
- 导出和生成图层为 8-bit PNG；高位深和特殊色彩空间的专业保真尚未验证。
- 不同 Codex 安装、账号、模型或沙箱可能不提供内置生图。启用功能不代表服务一定可用；失败时显示错误并保留日志。

### 源码、备用面板与验证

原生 Rust/egui 集成的补丁及重建说明见 [native-source/README.md](native-source/README.md)。桥接代码来自 OpenFill（Apache-2.0），第三方组件与许可证见 [THIRD_PARTY.md](THIRD_PARTY.md)。

备用 Tk 面板主要用于源码环境，需要 Python 3.10+（含 Tk）、Pillow、PhotoCraft 桌面版和已登录的 Codex CLI；源码入口为 `start-panel.cmd`：

```powershell
pip install -r requirements.txt
python -m photocraft_ai --photocraft "D:/PhotoCraft/photocraft.exe"
```

备用面板支持文生图、选区局部修改和移除物体；预览后采用结果。任务保存在 `runtime/jobs/`。Windows 原生发布包优先使用 `start.cmd`。

```powershell
python -m unittest discover -s tests -v
python -m photocraft_ai --connect-only
python tests/smoke_photocraft.py
```

验证记录及已知测试边界见 [VALIDATION.md](VALIDATION.md)。这些源码环境命令需要相应依赖和配套编辑器；实机测试会创建测试文档。真实生图依赖账号和服务，会消耗额度。

### 版本历史

| 版本 | 主要变化 |
| --- | --- |
| [0.2.9](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.9) | 可编辑图层蒙版，原选区/圆形/正方形，0–1000 px 羽化 |
| [0.2.8](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.8) | 直接接收本次会话的完整 PNG，修复 Windows 复制命令失败导致无法导回 |
| [0.2.7](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.7) | 改用本机 Node.js 和 npm 安装的 Codex，不再打包这两个组件 |
| [0.2.6](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.6) | 旧版自带 Python、Pillow、PhotoCraft 和 Codex CLI 的便携包 |
| [0.2.5](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.5) | 生成图片取消额外羽化，保留原始选区遮罩 |
| 0.2.4–0.2.1 | 独立代理、HTTPS 错误分类与超时、局部编辑羽化、单次生成和延迟优化 |

## English

Use **Edit selection, Remove object, and Generate image** directly inside PhotoCraft, from a native toolbar next to your selection. The integration uses your locally installed Codex CLI, its built-in image generation tool, and your existing sign-in. Results are imported as new layers with undo support.

### Download and start

1. Download **`photocraft-codex-ai-0.2.9-windows-x64-local-node.zip`** from the [v0.2.9 release](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.9).
2. Extract the entire archive into a writable folder. It includes the matching PhotoCraft editor, Python 3.13.5, and Pillow 11.3.0. **Node.js and Codex CLI are not bundled.**
3. Use your existing Node.js and npm-installed Codex CLI. If Codex is missing, run `npm.cmd install -g @openai/codex`.
4. Double-click **`start.cmd`**. Your existing Codex sign-in is reused; otherwise, follow the sign-in prompt for your own account.
5. Open an image in the newly launched editor, make a rectangular or lasso selection, enter a description, and choose an operation from the selection toolbar.

An internet connection and a Codex installation/account with working built-in image generation are required. GitHub's automatically generated **Source code** archives do not include the editor binary. The Windows x64 package is a preview development build: plugin 0.2.9 with a modified PhotoCraft 0.18.0 editor.

### Usage

| Operation | Behavior |
| --- | --- |
| Edit selection / 局部修改 | Edit the selected area using your description; default feather: 12 px |
| Remove object / 移除物体 | Remove the selected object and fill the background; no description required; default feather: 12 px |
| Generate image / 生成图片 | Generate content inside the selection; default feather: 0 px |

Results are added as new layers, preserving the original. Press **Ctrl+Z** to undo. The toolbar is hidden when there is no selection; select the whole canvas for a full-image prompt. It follows the selection, zoom, pan, and rotation, moving above the selection near the bottom edge. Progress, cancellation, and errors appear in the toolbar.

**New in v0.2.9: editable mask feathering.** Right-click an AI result layer → **边缘羽化 (Edge feathering)**. Choose the original selection, a centered circle, or a square, then adjust the **0–1000 px** slider or enter a value. The center comes from the layer's original pixel coverage; transparent results use their actual pixel bounds. New results have separate masks that can be adjusted without generating another image, support undo/redo, and persist in `.pcraft` files. Soft edges already baked into pixels by older versions cannot be reversed.

[Context menu example](examples/editable-mask-menu.png) · [Editable mask document](examples/editable-mask-demo.pcraft) · [Layered demo](examples/codex-ai-native-demo.pcraft)

### Proxy and local files

To use an explicit HTTP/mixed proxy, create `runtime/codex-proxy.json` inside the installation folder:

```json
{"url":"http://127.0.0.1:10808"}
```

`10808` is an example: replace it with your own proxy port and keep your proxy running. This setting applies only to Codex child processes launched by the plugin. It does not change system settings or global Codex configuration; local editor traffic bypasses the proxy. Delete the file to resume inheriting the existing network environment.

- Launch with `start.cmd` so both the editor and worker start. Do not launch only `native/photocraft.exe`.
- Editor settings are stored in `runtime/native-profile/`. Task images, prompts, results, and logs are stored in `runtime/native-jobs/`.
- Other PhotoCraft installations remain separate. Save your documents and close the old version before extracting an update. Update the matching editor through the plugin package to avoid replacing it with the upstream editor.

### Data handling and limitations

- Selection edits send **the full flattened source image and a reference image marking the selection** to Codex image generation. The selection limits local result compositing, not what is uploaded.
- The plugin uses the existing CLI sign-in without extracting login credentials and does not automatically fall back to a paid API. Cancellation stops the child process; a server-side job already in progress may still consume quota.
- The worker accepts token-authenticated localhost requests and rejects browser Origin requests. Codex runs with the `workspace-write` sandbox, `image_generation` enabled, and multi-agent mode disabled.
- Automatic import is refused if the document has changed or closed. A mismatched aspect ratio also prevents import while preserving the output; a different resolution with the same aspect ratio is scaled proportionally.
- Exported images and generated layers use 8-bit PNG. Professional fidelity for high-bit-depth documents and special color spaces has not been verified.
- Image generation availability depends on the Codex installation, account, model, and sandbox. Enabling the feature does not guarantee service access; failures are displayed and logs are retained.

### Source, fallback panel, and validation

See [native-source/README.md](native-source/README.md) for the Rust/egui patch and rebuild instructions. The bridge derives from OpenFill (Apache-2.0); component and license details are in [THIRD_PARTY.md](THIRD_PARTY.md).

The fallback Tk panel is mainly for source installations. It requires Python 3.10+ with Tk, Pillow, a desktop PhotoCraft installation, and a signed-in Codex CLI. Its source launcher is `start-panel.cmd`:

```powershell
pip install -r requirements.txt
python -m photocraft_ai --photocraft "D:/PhotoCraft/photocraft.exe"
```

The panel supports text-to-image, selection editing, and object removal, with a preview before applying results. Tasks are stored in `runtime/jobs/`. For the native Windows release, use `start.cmd`.

```powershell
python -m unittest discover -s tests -v
python -m photocraft_ai --connect-only
python tests/smoke_photocraft.py
```

See [VALIDATION.md](VALIDATION.md) for recorded results and known testing boundaries. These source-install commands require their dependencies and the matching editor; integration tests create test documents. Live image generation requires service access and consumes quota.

### Version history

| Version | Main change |
| --- | --- |
| [0.2.9](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.9) | Editable layer masks; original selection/circle/square; 0–1000 px feathering |
| [0.2.8](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.8) | Receive complete PNGs directly from the current session; fix failed Windows copy commands preventing import |
| [0.2.7](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.7) | Use local Node.js and npm-installed Codex instead of bundling them |
| [0.2.6](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.6) | Legacy portable bundle including Python, Pillow, PhotoCraft, and Codex CLI |
| [0.2.5](https://github.com/kaliwell/photocraft-codex-ai/releases/tag/v0.2.5) | Remove extra feathering for image generation; preserve the original selection mask |
| 0.2.4–0.2.1 | Per-plugin proxy, HTTPS error classification and timeout, local edit feathering, single-generation and latency improvements |
