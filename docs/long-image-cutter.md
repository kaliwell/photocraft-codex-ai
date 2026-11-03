# 长图切割 / Long image cutter

工具版 0.3.3 新增原生长图切割窗口。功能参考 kaliwell/LongPicCutter，采用独立 Rust/egui 实现，不包含该项目的源码，也不打开网页或上传图片。

1. 在 PhotoCraft 中打开长图，点击顶部 **长图切割**，或 **文件 → 导出 → 长图切割**。
2. 工具读取当前完整可见画布的快照，忽略选区；打开后对原文档的编辑不会自动刷新快照。需要刷新时关闭工具并重新打开。
3. 左侧点击或将鼠标放在图片上按 **S**，在原图像素行添加切割线；拖动红线调整。**Delete** 删除鼠标附近的线，**Ctrl+Z** 撤销。快捷键在鼠标位于左侧图片且不在文本输入时生效。
4. 从 0.3.5 起使用单栏大图，移除右侧切图预览。窗口默认随编辑器尺寸放大，可拖边缩放或点击 **最大化 / 还原**，图像操作区高度随窗口变化。点击 **导出 PNG ZIP**，选择保存位置。各段保持原图宽度，连续覆盖每一行，保留 8-bit RGBA 透明度。
5. 切割线自动保存在本机配置目录，按完整画布像素内容和尺寸识别；同一张图重新打开可以恢复。编辑画布后内容不同，视为新图。
6. **导出方案** 保存兼容 LongPicCutter v1 的 JSON；**导入方案** 仅接受相同宽高的方案，确认后替换。清空也需要确认。

边界：最多 6400 万像素、1024 条线，ZIP 最多 512 MiB。图片和方案均在本机处理。自动保存不是备份，重要方案请导出 JSON。工具使用打开时的可见画布合成图，不会把隐藏层或原始分层写入 ZIP。关闭工具不改变文档、剪贴板或撤销记录。

## English

Open **Long image cutter** from the title bar or File → Export. The native window snapshots the full visible canvas without altering the selection, clipboard, or history. Click or press S over the source to mark a row; drag a red line to move it, Delete to remove a nearby line, and Ctrl+Z to undo. Since 0.3.5, the cutter has one full-width source view with no slice preview. Its default size follows the editor window, with Maximize/Restore, manual resizing and a dynamically sized image area.

Export a ZIP of lossless RGBA8 PNG slices at original width, or exchange a version-1 JSON plan with LongPicCutter. Import requires identical dimensions and confirmation. Cuts are saved locally by canvas content and dimensions. Reopen the tool to refresh a snapshot after editing the document. Limits: 64 million pixels, 1,024 cuts, 512 MiB ZIP. No image is uploaded. This is an independent implementation inspired by LongPicCutter, with no source copied from that project.

# 默认 1:1 生图 / Square generation

顶部选区工具栏的 **生成图片** 默认请求 1024×1024（1:1）。结果等比居中放入选区的外接矩形，并按选区透明度裁切，不拉伸、不裁掉主体。选区不是方形时会留下透明余量。模型返回其他比例时同样等比放入，避免与整张画布比例不同而导入失败。

从 0.3.4 起，**局部修改** 和 **移除物体** 将完整画布等比补边为 1024×1024 参考图，选区指引同步映射；模型返回后归一化为方图、移除补边，再映射回原画布，只应用原选区。模型不遵守输入构图或输出比例时仍可能有几何误差；原始生成结果保留，文档名及修订号检查、单次新图层导入和撤销机制保持有效。旧任务无坐标映射时，按原画布尺寸归一化结果。

**Generate image** requests 1024×1024 by default. New artwork is proportionally centered inside the selection bounds and clipped by selection alpha, without stretching. Non-square selections leave transparent margins. Since 0.3.4, Fill/Remove use square letterboxed references and invert that mapping on import. Outputs with incorrect aspect ratios are normalized and may have geometric error; original files are retained. Legacy tasks are normalized directly to their original canvas size. Stale-document protection remains active. Model output dimensions are a request rather than a guarantee.
