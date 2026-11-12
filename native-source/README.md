# PhotoCraft 0.23.0 隔离集成源码

固定上游：`storytold/photocraft` v0.23.0，提交 `9963efcb2f04867b56c564f876befd412b6c3c4e`。
固定翻译：`storytold/craft-i18n` 提交 `e02939ef009218e81c44e8ec001fbb7603461de4`。

本分支独立于旧版 Unified。原生补丁适用于 0.23.0，保留 AI 工具栏、参考图/历史、PSD 底稿、切图、剪贴板及可选格式的批量图片导出。蒙版内向羽化保留工程兼容字段，已适配新版自动化读取和剪贴板结构。

```powershell
git clone --depth 1 --branch v0.23.0 https://github.com/storytold/photocraft.git research/photocraft-0.23
git -C research/photocraft-0.23 apply ../../native-source/photocraft-codex.patch
python prepare_i18n.py
python build_native.py
```

构建脚本强制嵌入固定翻译目录；`i18n-overlay.json` 保存自定义中文词条，不修改远程仓库。需要 Python 3.11+ 与 Rust/MSVC 工具链。源码位于 `research/photocraft-0.23`，独立编译缓存位于 `target-native-023`，输出 `native-0.23`。

本机独立安装为 `PhotoCraft-0.23.0-Codex-Isolated`，使用 17923 / 17924 端口及 `.photocraft-023-data` 工程旁文件夹。详见 [隔离说明](../ISOLATION.md)。首次使用独立 Codex 登录目录，不复制旧版凭据。

保留上游许可证、NOTICE 和作者信息。翻译库许可证位于安装目录 `licenses/craft-i18n`；自定义词条沿用 MIT OR Apache-2.0 许可。
