# plugins/demo_chat.py
def on_load(context):
    print("[Demo插件] 加载成功！等待事件...")

def on_event(event_type, data, context):
    if event_type == "voice_trigger":
        text = data.get("text", "")
        emotion = data.get("emotion", "")
        print(f"[Demo插件] 听到语音：'{text}'，触发了 {emotion} 表情！")
        
    elif event_type == "sing_start":
        print("[Demo插件] 用户开始唱歌了！准备蹦迪！")
        
    elif event_type == "key_press":
        key = data.get("key", "")
        if key == "f2":
            print("[Demo插件] 用户按下了 F2，手动触发比心！")
            context["trigger_expression"]("heart")