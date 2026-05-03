import os
import httpx
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.provider import llm_tool  # 修改点 1：导入 llm_tool 装饰器

@register("agent_dev_tools", "YourName", "为子Agent提供代码生成与热重载能力的工具箱", "1.0.0")
class AgentDevTools(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.webui_url = "http://127.0.0.1:6185"
        self.admin_token = os.environ.get("ASTRBOT_ADMIN_TOKEN", "")

    # ⚙️ 工具一：安全地写入插件文件
    @llm_tool(name="write_plugin_file")  # 修改点 2：用装饰器命名
    async def write_plugin_file(self, plugin_name: str, code: str) -> str:
        """将 LLM 生成的 Python 代码保存为一个 AstrBot 插件文件。需要提供插件名字（英文，不含空格）和完整的 Python 代码内容。"""
        try:
            if ".." in plugin_name or "/" in plugin_name or "\\" in plugin_name:
                return "❌ 非法插件名，请使用纯粹的英文和下划线。"
            plugin_dir = os.path.join(self.plugins_dir, plugin_name)
            os.makedirs(plugin_dir, exist_ok=True)
            metadata_content = f"name: {plugin_name}\ndescription: 自动生成的插件\nversion: 1.0.0\nauthor: AI_Agent\n"
            with open(os.path.join(plugin_dir, "metadata.yaml"), "w", encoding="utf-8") as f:
                f.write(metadata_content)
            with open(os.path.join(plugin_dir, "main.py"), "w", encoding="utf-8") as f:
                f.write(code)
            logger.info(f"✅ 插件 {plugin_name} 已写入到 {plugin_dir}")
            return f"✅ 插件 `{plugin_name}` 已成功创建并写入到 `{plugin_dir}`。"
        except Exception as e:
            logger.error(f"❌ 写入插件文件失败: {e}")
            return f"❌ 写入失败: {str(e)}"

    # ⚙️ 工具二：热重载指定插件
    @llm_tool(name="hot_reload_plugin")  # 修改点 3：用装饰器命名
    async def hot_reload_plugin(self, plugin_name: str) -> str:
        """热重载一个已安装的插件，使其立即生效。提供插件名称（plugins/下的文件夹名）即可。"""
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
    # ⚠️ 注意：使用 @llm_tool 装饰后，通常不再需要显式调 add_llm_tools，Agent 会自动发现
