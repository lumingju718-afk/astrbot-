import os
import httpx
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("agent_dev_tools", "YourName", "为子Agent提供代码生成与热重载能力的工具箱", "1.0.0")
class AgentDevTools(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 限制文件写入的根目录：只允许在 plugins 下创建
        self.plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # WebUI 地址，请根据你的实际配置修改
        self.webui_url = "http://127.0.0.1:6185"
        # 管理员 token，建议通过环境变量获取
        self.admin_token = os.environ.get("ASTRBOT_ADMIN_TOKEN", "")

    # ────────── 工具一：安全地写入插件文件 ──────────
    async def write_plugin_file(self, plugin_name: str, code: str) -> str:
        """
        将 LLM 生成的 Python 代码保存为一个 AstrBot 插件文件。
        Args:
            plugin_name: 插件名称，英文小写，单词间用下划线分隔，例如 hello_world
            code: 完整的 Python 插件代码，将被写入 main.py
        """
        try:
            # 安全检查：防止路径穿越
            if ".." in plugin_name or "/" in plugin_name or "\\" in plugin_name:
                return "❌ 非法插件名，请使用纯粹的英文和下划线。"

            plugin_dir = os.path.join(self.plugins_dir, plugin_name)
            os.makedirs(plugin_dir, exist_ok=True)

            # 自动生成 metadata.yaml
            metadata_content = (
                f"name: {plugin_name}\n"
                f"description: 由 AI 自动生成的插件\n"
                f"version: 1.0.0\n"
                f"author: AI_Agent\n"
            )
            with open(os.path.join(plugin_dir, "metadata.yaml"), "w", encoding="utf-8") as f:
                f.write(metadata_content)

            # 写入核心代码
            with open(os.path.join(plugin_dir, "main.py"), "w", encoding="utf-8") as f:
                f.write(code)

            logger.info(f"✅ 插件 {plugin_name} 已写入到 {plugin_dir}")
            return f"✅ 插件 `{plugin_name}` 已成功创建。"
        except Exception as e:
            logger.error(f"❌ 写入插件文件失败: {e}")
            return f"❌ 写入失败: {str(e)}"

    # ────────── 工具二：热重载指定插件 ──────────
    async def hot_reload_plugin(self, plugin_name: str) -> str:
        """
        热重载一个已安装的插件，使其立即生效。
        Args:
            plugin_name: 要重载的插件名字，即 plugins/ 下的文件夹名
        """
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{self.webui_url}/api/plugin/reload",
                    json={"plugin_name": plugin_name},
                    headers={"Authorization": f"Bearer {self.admin_token}"},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    logger.info(f"✅ 插件 {plugin_name} 已热重载成功")
                    return f"✅ 插件 `{plugin_name}` 加载成功，现在可以使用了。"
                else:
                    return f"❌ 重载失败，HTTP {resp.status_code}: {resp.text}"
        except Exception as e:
            logger.error(f"❌ 热重载失败: {e}")
            return f"❌ 热重载失败: {str(e)}"

    # ────────── 关键！通过覆盖此方法注册工具 ──────────
    async def get_llm_tools(self):
        """AstrBot 会自动调用此方法来获取此插件提供的所有 LLM 工具"""
        return [
            {
                "name": "write_plugin_file",
                "description": "将 LLM 生成的 Python 代码保存为一个 AstrBot 插件文件。需要提供插件名字（英文，不含空格）和完整的 Python 代码内容。",
                "handler": self.write_plugin_file,
                "parameters": {
                    "plugin_name": {"type": "string", "description": "插件名，英文小写+下划线"},
                    "code": {"type": "string", "description": "完整的 Python 插件代码"}
                }
            },
            {
                "name": "hot_reload_plugin",
                "description": "热重载一个已安装的插件，使其立即生效。提供插件名称即可。",
                "handler": self.hot_reload_plugin,
                "parameters": {
                    "plugin_name": {"type": "string", "description": "要重载的插件文件夹名"}
                }
            }
        ]