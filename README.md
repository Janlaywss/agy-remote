# agy-remote

在 Mac 的项目目录运行 `agy-mac`，即可打开 VPS 上的 Antigravity CLI（`agy`）。CLI 的模型会话和历史记录保存在 VPS，文件读写和 shell 命令由 Mac 上的 zsh 执行。每个会话以启动时的 Mac 当前目录作为工作目录。

```sh
cd ~/agy-remote
agy-mac
```

- **操作项目。** 在 TUI 中说「运行 `pwd` 并列出当前目录」，就能确认这次会话操作的是哪个 Mac 目录。
- **查看长任务。** 命令运行超过 5 秒会返回 `job-…` 编号。可以继续下达其他命令，再问「查看刚才任务的进度」。Mac 终端也支持 `agy-mac-job list` 和 `agy-mac-job status <任务编号>`。
- **粘贴截图。** 在 Mac 复制图片，在 TUI 中按 **Control + V**。出现 `media attached` 后即可继续输入提示词。
- **结束与恢复。** 输入 `/exit` 结束 CLI。要从某个 Mac 项目继续已有对话，在该目录运行 `agy-mac --conversation <会话 ID>`。`caffeinate -i` 在 SSH 会话期间防止空闲睡眠，随会话退出释放。

## 目录

| 位置 | 实现 |
| --- | --- |
| [mac/bin](mac/bin/) | 本地启动命令和后台任务管理器 |
| [mac/service](mac/service/) | Mac shell 服务、反向 SSH 隧道、从剪贴板读取 PNG 的 Swift 源码 |
| [mac/launchd](mac/launchd/) | shell、隧道及剪贴板三个用户级 LaunchAgent 的构建模板 |
| [vps](vps/) | `agy` 使用的 stdio MCP 代理、工具定义缓存和读取图片的 `xclip` 适配器 |
| [vps/config](vps/config/) | 默认在 Mac 上操作的全局规则；安装时由 agy 注册 MCP |

普通命令通过 VPS 的 `tools.sock` 进入 Mac 主动建立的 SSH 隧道。VPS 代理把启动目录和命令交给 Mac 的任务管理器，再把输出或任务编号返回 TUI。图片走每次启动单独分配的剪贴板 socket，由 Mac 上的 Swift 程序按需输出 PNG。

首次部署时，将 [.env.example](.env.example) 复制为本地 `.env.local` 并填入 SSH 主机、用户、密钥路径和 VPS 用户目录。Mac 构建从导出的环境变量生成私有连接配置与 LaunchAgent，并用 Swift 编译剪贴板程序。首次安装、更新和故障排查见[部署与验证](docs/部署与验证.md)。维护约定见 [AGENT.md](AGENT.md)，历次行为变化见[开发记录](docs/开发记录.md)。
