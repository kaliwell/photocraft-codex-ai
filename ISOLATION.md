# PhotoCraft 0.23.0 Codex 隔离版

独立运行目录：`D:\photocraftinstallandplugin\PhotoCraft-0.23.0-Codex-Isolated`。
独立开发目录：`D:\photocraftinstallandplugin\plugin-023`。

这个版本迁移了 Unified 的 AI 编辑、多图参考、历史、PSD 底稿、比例适配、切图及图片导出功能。现有 Unified 安装、源码和快捷方式保持独立，不通过其启动器运行。

| 数据/服务 | 隔离方式 |
|---|---|
| 编辑器 | 本目录 `native-0.23/photocraft.exe`，PhotoCraft 0.23.0 |
| Python 和插件 | 本目录副本，不引用旧版插件目录 |
| 配置、日志、缓存、临时文件 | 本目录 `runtime` |
| Codex 会话与配置 | 本目录 `runtime/codex-home`；首次需要单独登录，不复制旧版账号凭据 |
| AI 后台 / 编辑器控制端口 | 17923 / 17924，与旧版 17879 / 17880 分开 |
| 工程历史 / 切图方案 | 工程旁 `<工程名>.photocraft-023-data`，不使用旧版 `.photocraft-data` |
| 窗口标识 | `ai.storyteller.photocraft.codex023`；使用独立进程 |

桌面快捷方式：`PhotoCraft 0.23 隔离版.lnk`。首次启动按浏览器提示登录，或先运行本目录 `login.cmd`。关闭隔离版不会关闭 Unified。

两版均可以手动打开同一个工程；编辑保存仍会作用于用户选择的文件，因此比较版本时请打开工程副本。生成输出沿用重名保护规则，不迁移或清理旧版历史、缓存。

基线固定为上游正式版提交 `9963efcb2f04867b56c564f876befd412b6c3c4e`；翻译库固定为 `e02939ef009218e81c44e8ec001fbb7603461de4`，叠加本插件自定义中文词条。
