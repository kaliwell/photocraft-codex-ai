# 多图参考 / Reference images

原 Codex AI 插件现已在 PhotoCraft 0.20.1 的选区 AI 工具栏中集成参考图片。通过项目根目录的 `start.cmd` 启动，无需使用独立 Userfull Tools 整合版。

1. 选择画布区域，提示词栏出现后，将图片文件直接拖到这块工具栏上。可一次拖入多张，也可点击 **参考图 ＋** 多选。
2. 图片以缩略图显示，编号从 1 开始；点击编号旁的 **×** 移除单张。较多图片可横向滚动查看。
3. 提示词可以写“参考图1的场景，参考图2的产品结构”。编号按当前缩略图顺序解释，区别于插件内部的画布和选区指引图。
4. 点击 **生成图片 / 局部修改 / 移除物体**，参考图会作为图片附件传给 Codex，不是仅把文件名写进提示词。
5. 正在读取参考图或生成时，不能修改本次参考图。生成结束后保留所选参考图，方便继续使用。关闭应用后需重新选择，图片不会写入文档或偏好设置。

仅拖到 AI 工具栏上的图片会成为参考图；拖到其他位置继续按 PhotoCraft 原来的方式打开图片。支持 PNG、JPEG、WebP、BMP、GIF、TIFF（动画/多页文件使用第一帧/页）。参考图会按 EXIF 方向转正，保留完整像素尺寸，转换为 PNG 后传给生图工具，不自动缩至 2048。

**数量由 Codex 的实际能力校验，不设置固定 5 张等数量上限。** Codex 返回图片/上下文限制时显示其实际错误。所用模型、工具和账号的限制不能从其他 OpenAI API 的张数限制推断；参考 [Codex 官方文档](https://learn.chatgpt.com/docs/codex/cli)。

本地仍保留资源保护，这不是 Codex 额度：单文件 64 MiB、参考图原文件合计 256 MiB、单图解码最多 1 亿像素；大于这些阈值会提示分批或缩小图片。图片会在点击生成后发送到 Codex 生图服务，并在对应的本机任务目录保留，便于排查和恢复。

## English

Drop one or more image files onto the selection AI composer, or use **Reference images ＋** to select several. Thumbnails are numbered and individually removable, with horizontal scrolling for larger batches. Refer to them as “reference 1”, “reference 2”, etc. They are passed as actual image attachments to Codex in that order. References stay selected for subsequent requests and are disabled while loading/generating.

Drops outside the composer retain normal PhotoCraft file-opening behavior. EXIF orientation is applied and original pixel dimensions are retained. Supported raster formats are normalized to PNG, without an automatic 2048-pixel reduction. Generation sends these pictures to the Codex image service; local job files retain copies.

No fixed image-count cap is imposed by this plugin. Codex/model/tool restrictions are surfaced from actual errors rather than inferred from unrelated API limits. Local resource guards remain: 64 MiB per source file, 256 MiB total source files and 100 million decoded pixels per image. These guards are not a statement of Codex quotas.

## 自动化 / Automation

`ui.inspect.codexAI` exposes reference names, byte counts, loading state and composer/button rectangles, without image contents. The authenticated `ui.codexAI.references` method appends image attachments:

- `{"references":[{"name":"sample.png","data":"<base64>"}]}` for small inline payloads.
- `{"paths":["/approved/read/root/sample.png"]}` for larger images; every path is read through the existing `automation_read` service and must satisfy the configured automation read roots. It does not grant arbitrary filesystem access.

The editor control transport's existing request-size limit is unchanged. The private generation worker receives image bytes rather than arbitrary user-provided filesystem paths.
