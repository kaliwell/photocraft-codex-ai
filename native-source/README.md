# PhotoCraft 原生集成源码

基线：`storytold/photocraft`，版本 0.18.0，提交
`422ca7beda90d927643bcd074646ebbd37706d75`。

修改仅涉及 `crates/ui-egui`：选区下方的 egui 工具栏、可序列化的提示词状态、
后台本地请求及 `ui.inspect.codexAI` 的状态和按钮坐标。
图像导出、选区、图层和撤销仍通过已有引擎命令完成。

在项目根目录准备源码（本机已经完成）：

```powershell
git clone https://github.com/storytold/photocraft.git research/photocraft
git -C research/photocraft checkout 422ca7beda90d927643bcd074646ebbd37706d75
git -C research/photocraft apply ../../native-source/photocraft-codex.patch
python build_native.py
```

依赖 Rust/MSVC 构建工具及网络下载 Cargo 依赖。构建输出 `native/photocraft.exe`，
不修改已安装的原版编辑器。`native-build.toml` 是便于本机迭代的开发配置。

原生界面只在启动脚本设置 `PHOTOCRAFT_CODEX_PORT` 和 `PHOTOCRAFT_CODEX_TOKEN_FILE`
时启用。生成后台是 `photocraft_ai/native.py`，只接收经认证的 localhost 请求。
在 WebAssembly 中禁用本机后台能力，保持原有网页版本构建兼容。

上游许可证和通知随二进制保存于 `native/`。源码补丁遵循上游 MIT OR Apache-2.0。
