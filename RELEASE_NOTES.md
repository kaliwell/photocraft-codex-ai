# PhotoCraft Codex AI v0.2.6 · Windows x64 免安装整合包

下载 `photocraft-codex-ai-0.2.6-windows-x64-portable.zip`，完整解压后双击 `start.cmd`。
包含 PhotoCraft、Python 3.13.5、Pillow 11.3.0 和 Codex CLI 0.166.0，无需另装 Python、Node.js 或 Codex。
首次使用按提示登录自己的 Codex/ChatGPT 账号；仍需网络和支持内置生图的账号。
不包含账号凭据、代理配置或任务记录。需要代理时参照包内 `使用说明.txt`。

模拟移除 PATH 中的 Python/Node.js、使用空白 Codex 配置目录验证组件自检及 31 项测试通过。
未在另一台全新 Windows 设备完成实机验收。此版本为试用开发构建。

下面保留 v0.2.5 功能说明；其中手动安装依赖仅适用于旧版源码包。

在 PhotoCraft 软件内、选区下方直接使用 Codex AI：局部修改、移除物体和生成图片。

- “生成图片”取消额外边缘羽化，保留原始选区遮罩。
- 局部修改和移除物体继续使用默认 12 像素向内羽化。
- 支持为插件启动的 Codex 配置独立 HTTP 代理；使用 HTTPS 并限制连接重试。
- 生成结果添加为新图层，支持 Ctrl+Z 撤销。
- 31 项 Python 测试通过；完整原生测试边界见 VALIDATION.md。

下载 `photocraft-codex-ai-0.2.5.zip`，完整解压后运行 `start.cmd`。
需要 Windows、Python 3.10+、Pillow（`pip install -r requirements.txt`）、已安装并登录的 Codex CLI，
且账号与当前 CLI 需实际支持内置生图。不需要 API Key，不自动切换付费 API。

这是 Windows 试用开发构建，压缩包包含集成版 PhotoCraft；GitHub 自动生成的 Source code 压缩包仅含源码，
不含编辑器二进制。运行时任务、代理配置及登录凭据均不包含在发布包中。
