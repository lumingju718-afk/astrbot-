# Agent 自开发工具箱

让 AstrBot 的智能体（Agent）能够自己生成和加载新的插件，实现能力自我扩展。

## 功能

- 📝 `write_plugin_file`：将 AI 生成的代码保存为一个完整的 AstrBot 插件。
- 🔄 `hot_reload_plugin`：调用 WebUI API 热重载指定插件，使其立即生效。

## 安装

1. 将整个 `agent_dev_tools` 文件夹放入 AstrBot 的 `data/plugins/` 目录。
2. 重启 AstrBot，或在 WebUI 插件管理页面点击“重载插件”。

## 使用方法

该插件提供的工具供智能体（Agent）调用，无需手动通过指令触发。

当你在聊天中向主 Agent 提出类似以下需求时，它会自动调用本插件工具：
- “帮我写一个插件，当有人发送 `/time` 时回复当前时间。”
- “给我开发一个能查询天气的工具插件。”

## 配置

确保 `main.py` 中的 `webui_url` 和 `admin_token` 已正确设置（推荐通过环境变量 `ASTRBOT_ADMIN_TOKEN` 传递）。

## 依赖

- `httpx`（已内置在 AstrBot 环境中）

## 许可

MIT