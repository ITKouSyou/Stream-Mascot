# plugins/bilibili_danmaku.py
# 修复说明：
# 1. blivedm 官方包没有发布到 PyPI，pip install blivedm 装到的是同名错误包，
#    必须从 GitHub 安装：pip install git+https://github.com/xfgryujk/blivedm.git --no-deps
# 2. 官方新版中 DanmakuMessage 在 blivedm.models.web 子模块，不在 blivedm 顶层
# 3. client 注册 handler 用 set_handler()，而不是 add_handler()
# 4. 新版 BLiveClient 构造参数已没有 ssl=True（默认走 wss），删掉该参数
# 5. 原代码在 on_load 里直接 asyncio.run() 会阻塞 plugin_manager 的加载循环，
#    这里改为后台线程运行
# 6. 官方 BaseHandler 的 _on_* 回调是【同步】方法（handle() 里同步调用，不 await），
#    因此 _on_danmaku 必须是 def 而不是 async def；
#    否则回调返回协程却没人 await，弹幕处理不生效并报
#    "coroutine 'MyHandler._on_danmaku' was never awaited"
import asyncio
import threading

import config
import blivedm
import blivedm.models.web as web_models


class MyHandler(blivedm.BaseHandler):
    def __init__(self, context):
        super().__init__()
        self.context = context

    def _on_danmaku(self, client, message: web_models.DanmakuMessage):
        text = message.msg
        username = message.uname
        print(f"[B站弹幕] {username}: {text}")

        if "谢谢" in text or "比心" in text:
            self.context["trigger_expression"]("heart")
            self.context["emit_text"](f"感谢 {username} 的弹幕！")
        elif "生气" in text or "靠" in text:
            self.context["trigger_expression"]("angry")
        elif "哭" in text or "呜呜" in text:
            self.context["trigger_expression"]("cry")
        elif "震惊" in text or "卧槽" in text:
            self.context["trigger_expression"]("surprised")


def on_load(context):
    room_id = config.CFG["global"].get("bilibili_room_id", "").strip()
    if not room_id:
        print("[B站插件] 未配置房间号，插件处于休眠状态。")
        return

    async def run():
        client = blivedm.BLiveClient(int(room_id))
        handler = MyHandler(context)
        client.set_handler(handler)

        # start() 是同步方法，内部会创建后台协程，不需要 await
        client.start()
        print(f"[B站插件] 正在连接直播间: {room_id}")

        try:
            # 保持连接，直到程序关闭
            await client.join()
        finally:
            await client.stop_and_close()

    # 放到后台线程运行，避免阻塞 plugin_manager 的 load_plugins() 循环
    threading.Thread(target=lambda: asyncio.run(run()), daemon=True).start()
    print(f"[B站插件] 弹幕监听已启动（房间 {room_id}）")