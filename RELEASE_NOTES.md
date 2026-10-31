# PhotoCraft Codex AI v0.2.5

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
