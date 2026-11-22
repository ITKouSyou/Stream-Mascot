import os
import importlib.util

class PluginManager:
    def __init__(self, plugins_dir="plugins"):
        self.plugins_dir = plugins_dir
        self.plugins = []
        self.context = {}
        
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)

    def set_context(self, context):
        """设置给插件使用的 API 上下文"""
        self.context = context

    def load_plugins(self):
        """扫描并加载 plugins 目录下的所有 py 文件"""
        for filename in os.listdir(self.plugins_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                filepath = os.path.join(self.plugins_dir, filename)
                module_name = filename[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    
                    # 如果插件有 on_load 钩子，初始化时调用
                    if hasattr(mod, "on_load"):
                        mod.on_load(self.context)
                        
                    self.plugins.append(mod)
                    print(f"[插件系统] 成功加载插件: {filename}")
                except Exception as e:
                    print(f"[插件系统] 插件 {filename} 加载失败: {e}")

    def trigger_event(self, event_type, data=None):
        """向所有插件广播事件"""
        for plugin in self.plugins:
            if hasattr(plugin, "on_event"):
                try:
                    plugin.on_event(event_type, data, self.context)
                except Exception as e:
                    print(f"[插件系统] 插件处理事件 {event_type} 出错: {e}")