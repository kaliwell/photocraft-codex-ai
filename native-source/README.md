# PhotoCraft 原生集成源码

基线：`storytold/photocraft`，版本 0.20.1，提交
`327c4cc82e737a3e0af7c147a477126d77525495`。

修改涉及 `crates/ui-egui` 和 `crates/engine`：选区下方的 egui 工具栏、可序列化的提示词状态、
后台本地请求、图层右键羽化控制，以及 `layer.layerMask.edit` 的居中圆形/正方形蒙版参数。
`ui.inspect.codexAI.maskFeatherMenu` 提供菜单与控件坐标，供界面测试使用。
图像导出、选区、图层和撤销仍通过已有引擎命令完成。

边缘羽化使用独立蒙版的向内渐隐：原始覆盖边界为完全透明，内部平滑过渡到不透明。
`layer.layerMask.edit` 的 `inward: true` 开启此模式；标准蒙版的默认高斯羽化保持原有行为。
该标志随 `.pcraft` 保存，旧文档默认为标准羽化；右键调整羽化即可应用向内模式。
算法、缓存和原生格式的扩展位于 `crates/doc`、`crates/compose` 与 `crates/format`。

原生 AI 工具栏支持多图参考的多选、拖放、缩略图及逐张移除；`ui.codexAI.references`
提供受现有自动化读取策略约束的测试入口。参考图通过本地认证请求发送实际图片字节，后台校验并保存到当前任务目录，再作为 CLI 图片附件传入；不从 HTTP 请求读取任意文件路径。

当前开发版同时集成 Userfull Tools 的 `long_cut`、标题栏“长图切割/复制图片”、`file.export.clipboard` 命令及语言辅助模块；所有功能运行于同一个 PhotoCraft。0.20.1 原有 SVG 剪贴板导入与新整幅画布导出同时保留。

标题栏「导出图片」直接导出当前完整可见画布，菜单支持全部已打开工程及指定文件夹。格式列表取自 `photocraft_codecs::Format::ALL` 中 `caps().write` 为真的格式，PNG 默认，JPEG 质量及 WebP 无损/有损设置由同一原生编码器处理；扩展名取自格式注册表。原生 `image_export` 模块使用不可变工程快照在后台编码，逐张报告进度，重名排他创建并自动编号；保留原工程、活动标签和选区。

在项目根目录准备源码（本机已经完成）：

```powershell
git clone https://github.com/storytold/photocraft.git research/photocraft-0.20
git -C research/photocraft-0.20 checkout 327c4cc82e737a3e0af7c147a477126d77525495
git -C research/photocraft-0.20 apply ../../native-source/photocraft-codex.patch
python build_native.py
```

依赖 Python 3.11+、Rust/MSVC 构建工具及网络下载 Cargo 依赖。构建输出 `native-0.20/photocraft.exe`，
不修改已安装的原版编辑器。`native-build.toml` 是便于本机迭代的开发配置。

原生界面只在启动脚本设置 `PHOTOCRAFT_CODEX_PORT` 和 `PHOTOCRAFT_CODEX_TOKEN_FILE`
时启用。生成后台是 `photocraft_ai/native.py`，只接收经认证的 localhost 请求。
在 WebAssembly 中禁用本机后台能力，保持原有网页版本构建兼容。

上游许可证和通知随二进制保存于 `native/`。源码补丁遵循上游 MIT OR Apache-2.0。
