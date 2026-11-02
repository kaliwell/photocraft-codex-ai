# PhotoCraft 原生集成源码

基线：`storytold/photocraft`，版本 0.19.0，提交
`2df9f807702a935184041355a86405380bda8274`。

修改涉及 `crates/ui-egui` 和 `crates/engine`：选区下方的 egui 工具栏、可序列化的提示词状态、
后台本地请求、图层右键羽化控制，以及 `layer.layerMask.edit` 的居中圆形/正方形蒙版参数。
`ui.inspect.codexAI.maskFeatherMenu` 提供菜单与控件坐标，供界面测试使用。
图像导出、选区、图层和撤销仍通过已有引擎命令完成。

边缘羽化使用独立蒙版的向内渐隐：原始覆盖边界为完全透明，内部平滑过渡到不透明。
`layer.layerMask.edit` 的 `inward: true` 开启此模式；标准蒙版的默认高斯羽化保持原有行为。
该标志随 `.pcraft` 保存，旧文档默认为标准羽化；右键调整羽化即可应用向内模式。
算法、缓存和原生格式的扩展位于 `crates/doc`、`crates/compose` 与 `crates/format`。

在项目根目录准备源码（本机已经完成）：

```powershell
git clone https://github.com/storytold/photocraft.git research/photocraft-0.19
git -C research/photocraft-0.19 checkout 2df9f807702a935184041355a86405380bda8274
git -C research/photocraft-0.19 apply ../../native-source/photocraft-codex.patch
python build_native.py
```

依赖 Python 3.11+、Rust/MSVC 构建工具及网络下载 Cargo 依赖。构建输出 `native-0.19/photocraft.exe`，
不修改已安装的原版编辑器。`native-build.toml` 是便于本机迭代的开发配置。

原生界面只在启动脚本设置 `PHOTOCRAFT_CODEX_PORT` 和 `PHOTOCRAFT_CODEX_TOKEN_FILE`
时启用。生成后台是 `photocraft_ai/native.py`，只接收经认证的 localhost 请求。
在 WebAssembly 中禁用本机后台能力，保持原有网页版本构建兼容。

上游许可证和通知随二进制保存于 `native/`。源码补丁遵循上游 MIT OR Apache-2.0。
