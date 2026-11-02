# PhotoCraft Codex AI v0.2.9 · 可编辑蒙版羽化 / Editable mask feathering

## 中文

下载 **`photocraft-codex-ai-0.2.9-windows-x64-local-node.zip`**，完整解压到可写目录后双击 **`start.cmd`**。更新前请先保存文档并关闭旧版窗口。

- 右键 AI 结果图层 → **边缘羽化**，选择原选区、居中圆形或正方形。
- 羽化范围 **0–1000 px**，支持滑条和数值输入；中心依据图层原始像素覆盖范围计算。
- 新 AI 图层使用独立蒙版，调整无需重新生图，支持撤销/重做，保存 `.pcraft` 后保留。
- 生成图片默认 0 px 羽化；局部修改和移除物体默认 12 px。旧版已烘焙到像素的软边无法反向还原。
- 使用本机 Node.js 与 npm 安装的 Codex CLI；包内包含配套 PhotoCraft、Python 和 Pillow。

这是 Windows x64 试用开发构建。需要网络和实际支持内置生图的 Codex 账号；GitHub 自动生成的 Source code 压缩包不含配套编辑器二进制。验证记录与已知边界见 [VALIDATION.md](https://github.com/kaliwell/photocraft-codex-ai/blob/v0.2.9/VALIDATION.md)。

## English

Download **`photocraft-codex-ai-0.2.9-windows-x64-local-node.zip`**, extract the entire archive into a writable folder, and double-click **`start.cmd`**. Save your documents and close the previous version before updating.

- Right-click an AI result layer → **边缘羽化 (Edge feathering)** and choose the original selection, a centered circle, or a square.
- Adjust feathering from **0–1000 px** using the slider or numeric input; the center follows the layer's original pixel coverage.
- New AI layers use separate masks. Adjustments require no new generation, support undo/redo, and persist in `.pcraft` files.
- Image generation defaults to 0 px feathering; selection edits and object removal default to 12 px. Soft edges baked into pixels by older versions cannot be reversed.
- Uses local Node.js and npm-installed Codex CLI; includes the matching PhotoCraft editor, Python, and Pillow.

This is a Windows x64 preview development build. Internet access and a Codex account with working built-in image generation are required. GitHub's automatically generated Source code archives do not include the matching editor binary. See [VALIDATION.md](https://github.com/kaliwell/photocraft-codex-ai/blob/v0.2.9/VALIDATION.md) for recorded results and known boundaries.

## SHA-256

`7e0c5ff97ece01fcc24a06a2e370769a8e8f848f15b22cc2090185070e163554`
