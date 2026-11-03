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
